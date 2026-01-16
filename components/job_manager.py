"""
Redis-based job persistence for async enrichment processing.

Provides job state management with GZIP-compressed result storage
and automatic 7-day TTL on all keys.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import gzip
import json
import os
import uuid

import redis


@dataclass
class Job:
    """Represents an enrichment job with its current state."""
    id: str
    status: str  # "pending", "processing", "completed", "failed"
    filename: str
    total_records: int
    processed_records: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class JobManager:
    """
    Manages job persistence in Redis with GZIP compression for results.
    
    Redis Schema:
        job:{uuid}:meta      -> JSON: {id, status, filename, total, processed, created_at, completed_at, error}
        job:{uuid}:results   -> GZIP-compressed JSON array of result dicts
        job:{uuid}:progress  -> JSON: {current, total, message}
        user:{session_id}:jobs -> List of job IDs (max 10, newest first)
    
    All keys have 7-day TTL.
    """
    
    TTL_SECONDS = 604800  # 7 days
    MAX_JOBS_PER_USER = 10
    
    def __init__(self):
        """Initialize Redis connection. Set self.redis to None if unavailable."""
        self.redis: Optional[redis.Redis] = None
        try:
            redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
            self.redis = redis.from_url(redis_url, decode_responses=False)
            # Test connection
            self.redis.ping()
        except (redis.ConnectionError, redis.RedisError) as e:
            self.redis = None
    
    def is_available(self) -> bool:
        """Check if Redis is available."""
        if self.redis is None:
            return False
        try:
            self.redis.ping()
            return True
        except (redis.ConnectionError, redis.RedisError):
            return False
    
    def create_job(self, session_id: str, filename: str, total_records: int) -> Optional[str]:
        """Create a new job, return job_id or None if Redis unavailable."""
        if not self.is_available():
            return None
        
        try:
            job_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            meta = {
                "id": job_id,
                "status": "pending",
                "filename": filename,
                "total": total_records,
                "processed": 0,
                "created_at": now.isoformat(),
                "completed_at": None,
                "error": None
            }
            
            meta_key = f"job:{job_id}:meta"
            progress_key = f"job:{job_id}:progress"
            user_jobs_key = f"user:{session_id}:jobs"
            
            # Store job metadata
            self.redis.set(
                meta_key,
                json.dumps(meta).encode(),
                ex=self.TTL_SECONDS
            )
            
            # Initialize progress
            progress = {"current": 0, "total": total_records, "message": ""}
            self.redis.set(
                progress_key,
                json.dumps(progress).encode(),
                ex=self.TTL_SECONDS
            )
            
            # Add to user's job list (newest first)
            self.redis.lpush(user_jobs_key, job_id.encode())
            self.redis.ltrim(user_jobs_key, 0, self.MAX_JOBS_PER_USER - 1)
            self.redis.expire(user_jobs_key, self.TTL_SECONDS)
            
            return job_id
        except (redis.ConnectionError, redis.RedisError):
            return None
    
    def update_progress(self, job_id: str, current: int, total: int, message: str = "") -> bool:
        """Update job progress. Returns True on success."""
        if not self.is_available():
            return False
        
        try:
            progress_key = f"job:{job_id}:progress"
            meta_key = f"job:{job_id}:meta"
            
            # Update progress
            progress = {"current": current, "total": total, "message": message}
            self.redis.set(
                progress_key,
                json.dumps(progress).encode(),
                ex=self.TTL_SECONDS
            )
            
            # Update processed count in metadata
            meta_raw = self.redis.get(meta_key)
            if meta_raw:
                meta = json.loads(meta_raw.decode())
                meta["processed"] = current
                meta["status"] = "processing"
                self.redis.set(
                    meta_key,
                    json.dumps(meta).encode(),
                    ex=self.TTL_SECONDS
                )
            
            return True
        except (redis.ConnectionError, redis.RedisError, json.JSONDecodeError):
            return False
    
    def mark_completed(self, job_id: str) -> bool:
        """Mark job as completed with timestamp."""
        if not self.is_available():
            return False
        
        try:
            meta_key = f"job:{job_id}:meta"
            meta_raw = self.redis.get(meta_key)
            
            if not meta_raw:
                return False
            
            meta = json.loads(meta_raw.decode())
            meta["status"] = "completed"
            meta["completed_at"] = datetime.utcnow().isoformat()
            
            self.redis.set(
                meta_key,
                json.dumps(meta).encode(),
                ex=self.TTL_SECONDS
            )
            
            return True
        except (redis.ConnectionError, redis.RedisError, json.JSONDecodeError):
            return False
    
    def mark_failed(self, job_id: str, error: str) -> bool:
        """Mark job as failed with error message."""
        if not self.is_available():
            return False
        
        try:
            meta_key = f"job:{job_id}:meta"
            meta_raw = self.redis.get(meta_key)
            
            if not meta_raw:
                return False
            
            meta = json.loads(meta_raw.decode())
            meta["status"] = "failed"
            meta["error"] = error
            meta["completed_at"] = datetime.utcnow().isoformat()
            
            self.redis.set(
                meta_key,
                json.dumps(meta).encode(),
                ex=self.TTL_SECONDS
            )
            
            return True
        except (redis.ConnectionError, redis.RedisError, json.JSONDecodeError):
            return False
    
    def save_results(self, job_id: str, results: list[dict]) -> bool:
        """Save results (GZIP compressed). Returns True on success."""
        if not self.is_available():
            return False
        
        try:
            results_key = f"job:{job_id}:results"
            
            # GZIP compress the results
            json_bytes = json.dumps(results).encode()
            compressed = gzip.compress(json_bytes)
            
            self.redis.set(
                results_key,
                compressed,
                ex=self.TTL_SECONDS
            )
            
            return True
        except (redis.ConnectionError, redis.RedisError, json.JSONDecodeError):
            return False
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job metadata."""
        if not self.is_available():
            return None
        
        try:
            meta_key = f"job:{job_id}:meta"
            meta_raw = self.redis.get(meta_key)
            
            if not meta_raw:
                return None
            
            meta = json.loads(meta_raw.decode())
            
            return Job(
                id=meta["id"],
                status=meta["status"],
                filename=meta["filename"],
                total_records=meta["total"],
                processed_records=meta["processed"],
                created_at=datetime.fromisoformat(meta["created_at"]),
                completed_at=datetime.fromisoformat(meta["completed_at"]) if meta.get("completed_at") else None,
                error_message=meta.get("error")
            )
        except (redis.ConnectionError, redis.RedisError, json.JSONDecodeError, KeyError, ValueError):
            return None
    
    def get_job_results(self, job_id: str) -> Optional[list[dict]]:
        """Get job results (decompressed)."""
        if not self.is_available():
            return None
        
        try:
            results_key = f"job:{job_id}:results"
            compressed = self.redis.get(results_key)
            
            if not compressed:
                return None
            
            # Decompress and parse
            json_bytes = gzip.decompress(compressed)
            results = json.loads(json_bytes.decode())
            
            return results
        except (redis.ConnectionError, redis.RedisError, gzip.BadGzipFile, json.JSONDecodeError):
            return None
    
    def get_user_jobs(self, session_id: str) -> list[Job]:
        """Get list of jobs for a user (newest first, max 10)."""
        if not self.is_available():
            return []
        
        try:
            user_jobs_key = f"user:{session_id}:jobs"
            job_ids = self.redis.lrange(user_jobs_key, 0, self.MAX_JOBS_PER_USER - 1)
            
            jobs = []
            for job_id_bytes in job_ids:
                job_id = job_id_bytes.decode() if isinstance(job_id_bytes, bytes) else job_id_bytes
                job = self.get_job(job_id)
                if job:
                    jobs.append(job)
            
            return jobs
        except (redis.ConnectionError, redis.RedisError):
            return []
    
    def get_progress(self, job_id: str) -> Optional[dict]:
        """Get current progress for a job."""
        if not self.is_available():
            return None
        
        try:
            progress_key = f"job:{job_id}:progress"
            progress_raw = self.redis.get(progress_key)
            
            if not progress_raw:
                return None
            
            return json.loads(progress_raw.decode())
        except (redis.ConnectionError, redis.RedisError, json.JSONDecodeError):
            return None
