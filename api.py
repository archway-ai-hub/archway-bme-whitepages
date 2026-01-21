"""
FastAPI REST API for Restaurant Lead Enrichment

Provides endpoints for file upload, job management, and results download.
Designed to be consumed by a React frontend on Vercel.
"""

import asyncio
import os
import re
import tempfile
import uuid
from contextlib import asynccontextmanager
from pathlib import Path, PurePath
from typing import Optional
from urllib.parse import quote

import pandas as pd
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Import from existing codebase
from components.job_manager import Job, JobManager
from main import Config, format_output_row, parse_csv_row, process_batch

# Constants
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for Content-Disposition header."""
    # Remove control characters and path separators
    sanitized = re.sub(r'[\r\n\x00-\x1f/\\]', '_', filename)
    return sanitized[:255]


# Global job manager instance
job_manager: Optional[JobManager] = None

# Temporary file storage for uploads (maps job_id -> file_path)
upload_files: dict[str, str] = {}

# In-memory job storage for local dev (when Redis unavailable)
in_memory_jobs: dict[str, dict] = {}
in_memory_results: dict[str, str] = {}  # job_id -> results file path


class InMemoryJob:
    """Simple in-memory job for local development without Redis."""
    def __init__(self, job_id: str, session_id: str, filename: str, total_records: int):
        self.job_id = job_id
        self.session_id = session_id
        self.filename = filename
        self.total_records = total_records
        self.status = "pending"
        self.processed_records = 0
        self.error_message = None
        from datetime import datetime
        self.created_at = datetime.now()


def redis_available() -> bool:
    """Check if Redis is available."""
    return job_manager is not None and job_manager.is_available()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    global job_manager
    job_manager = JobManager()
    yield
    # Cleanup temp files on shutdown
    for path in upload_files.values():
        try:
            os.unlink(path)
        except OSError:
            pass


app = FastAPI(
    title="Restaurant Lead Enrichment API",
    description="API for enriching restaurant lead data with owner information",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS - in production, set CORS_ORIGINS env var to your frontend URL
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
# Strip whitespace from origins
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS]
print(f"CORS allowed origins: {CORS_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Pydantic Models
# ==============================================================================


class UploadResponse(BaseModel):
    """Response from file upload endpoint."""
    job_id: str
    filename: str
    total_records: int
    message: str


class JobStatus(BaseModel):
    """Job status response."""
    id: str
    status: str
    filename: str
    total_records: int
    processed_records: int
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class JobStartResponse(BaseModel):
    """Response from job start endpoint."""
    job_id: str
    message: str


class JobListResponse(BaseModel):
    """Response listing all jobs."""
    jobs: list[JobStatus]


# ==============================================================================
# Helper Functions
# ==============================================================================


def job_to_status(job: Job) -> JobStatus:
    """Convert Job dataclass to JobStatus response model."""
    return JobStatus(
        id=job.id,
        status=job.status,
        filename=job.filename,
        total_records=job.total_records,
        processed_records=job.processed_records,
        created_at=job.created_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        error_message=job.error_message,
    )


async def run_enrichment(job_id: str, file_path: str, config: Config) -> None:
    """Background task to run the enrichment pipeline."""
    use_redis = redis_available()

    # Mark job as processing
    if use_redis:
        job_manager.update_progress(job_id, 0, 1, "Starting...")
    elif job_id in in_memory_jobs:
        in_memory_jobs[job_id].status = "processing"

    try:
        # Read file
        path = Path(file_path)
        if path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)

        # Filter out empty rows (rows where 'name' column is empty/null)
        if "name" in df.columns:
            df = df[df["name"].notna() & (df["name"].astype(str).str.strip() != "")]
        else:
            # Fallback: drop rows where all values are empty
            df = df.dropna(how="all")

        # Parse records
        records = []
        for _, row in df.iterrows():
            try:
                record = parse_csv_row(row)
                records.append(record)
            except Exception:
                continue

        if not records:
            if use_redis:
                job_manager.mark_failed(job_id, "No valid records found in file")
            elif job_id in in_memory_jobs:
                in_memory_jobs[job_id].status = "failed"
                in_memory_jobs[job_id].error_message = "No valid records found in file"
            return

        # Progress callback for job updates
        def progress_callback(current: int, total: int, message: str) -> None:
            if use_redis:
                job_manager.update_progress(job_id, current, total, message)
            elif job_id in in_memory_jobs:
                in_memory_jobs[job_id].processed_records = current

        # Run processing
        results = await process_batch(
            records=records,
            config=config,
            batch_size=10,
            progress_callback=progress_callback,
        )

        # Convert results to dicts and save
        result_dicts = [format_output_row(r) for r in results]
        if use_redis:
            job_manager.save_results(job_id, result_dicts)
            job_manager.mark_completed(job_id)
        else:
            # Save results to temp file for in-memory mode
            results_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w")
            pd.DataFrame(result_dicts).to_csv(results_file.name, index=False)
            in_memory_results[job_id] = results_file.name
            if job_id in in_memory_jobs:
                in_memory_jobs[job_id].status = "completed"
                in_memory_jobs[job_id].processed_records = len(results)

    except Exception as e:
        if use_redis:
            job_manager.mark_failed(job_id, str(e))
        elif job_id in in_memory_jobs:
            in_memory_jobs[job_id].status = "failed"
            in_memory_jobs[job_id].error_message = str(e)

    finally:
        # Clean up temp file
        try:
            os.unlink(file_path)
        except OSError:
            pass
        upload_files.pop(job_id, None)


# ==============================================================================
# API Endpoints
# ==============================================================================


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), session_id: Optional[str] = None):
    """
    Upload a CSV or Excel file for processing.

    Returns a job_id that can be used to start processing and check status.
    """
    # Sanitize filename - remove path components
    raw_filename = file.filename or "unknown"
    filename = PurePath(raw_filename).name  # Remove path components
    if not filename or filename in ('.', '..'):
        filename = "upload.csv"

    # Validate file type
    suffix = Path(filename).suffix.lower()
    if suffix not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a CSV or Excel file.",
        )

    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = await file.read()

        # Validate file size
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE // (1024*1024)}MB."
            )

        temp_file.write(content)
        temp_file.close()

        # Read to get record count
        path = Path(temp_file.name)
        if suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)

        # Filter out empty rows (rows where 'name' column is empty/null)
        if "name" in df.columns:
            df = df[df["name"].notna() & (df["name"].astype(str).str.strip() != "")]
        else:
            # Fallback: drop rows where all values are empty
            df = df.dropna(how="all")

        total_records = len(df)

        if total_records == 0:
            os.unlink(temp_file.name)
            raise HTTPException(status_code=400, detail="File contains no records.")

        # Use provided session_id or generate one
        if not session_id:
            session_id = "api-" + str(uuid.uuid4())[:8]

        # Try Redis first, fall back to in-memory
        if redis_available():
            job_id = job_manager.create_job(session_id, filename, total_records)
            if not job_id:
                os.unlink(temp_file.name)
                raise HTTPException(status_code=500, detail="Failed to create job.")
        else:
            # In-memory fallback for local development
            job_id = str(uuid.uuid4())
            in_memory_jobs[job_id] = InMemoryJob(job_id, session_id, filename, total_records)

        # Store temp file path for later processing
        upload_files[job_id] = temp_file.name

        return UploadResponse(
            job_id=job_id,
            filename=filename,
            total_records=total_records,
            message=f"File uploaded successfully. {total_records} records ready for processing.",
        )

    except HTTPException:
        raise
    except Exception as e:
        try:
            os.unlink(temp_file.name)
        except OSError:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@app.post("/api/jobs/{job_id}/start", response_model=JobStartResponse)
async def start_job(job_id: str, background_tasks: BackgroundTasks):
    """
    Start processing a previously uploaded job.

    The processing runs in the background. Use GET /api/jobs/{job_id} to check status.
    """
    # Verify job exists (check both Redis and in-memory)
    if redis_available():
        job = job_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")
        if job.status != "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Job cannot be started. Current status: {job.status}",
            )
    else:
        job = in_memory_jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")
        if job.status != "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Job cannot be started. Current status: {job.status}",
            )

    # Verify we have the file
    if job_id not in upload_files:
        raise HTTPException(
            status_code=400,
            detail="Upload file not found. Please upload the file again.",
        )

    # Validate API keys
    config = Config()
    if not config.google_places_api_key or not config.openrouter_api_key:
        raise HTTPException(
            status_code=500,
            detail="Required API keys (GOOGLE_PLACES_API_KEY, OPENROUTER_API_KEY) not configured.",
        )

    # Start background processing
    file_path = upload_files[job_id]
    background_tasks.add_task(run_enrichment, job_id, file_path, config)

    return JobStartResponse(
        job_id=job_id,
        message="Processing started. Check status with GET /api/jobs/{job_id}",
    )


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get the current status of a job.

    Status can be: pending, processing, completed, failed
    """
    if redis_available():
        job = job_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")
        return job_to_status(job)
    else:
        # In-memory fallback
        job = in_memory_jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")
        return JobStatus(
            id=job.job_id,
            status=job.status,
            filename=job.filename,
            total_records=job.total_records,
            processed_records=job.processed_records,
            error_message=job.error_message,
            created_at=job.created_at.isoformat(),
        )


@app.get("/api/jobs/{job_id}/results")
async def get_job_results(job_id: str):
    """
    Download the results of a completed job as CSV.

    Returns 400 if the job is not yet completed.
    """
    if redis_available():
        job = job_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")

        if job.status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Results not available. Job status: {job.status}",
            )

        results = job_manager.get_job_results(job_id)
        if not results:
            raise HTTPException(status_code=404, detail="Results not found.")

        # Convert to CSV
        df = pd.DataFrame(results)
        csv_content = df.to_csv(index=False)
        output_filename = f"enriched_{job.filename}"
    else:
        # In-memory fallback
        job = in_memory_jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")

        if job.status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Results not available. Job status: {job.status}",
            )

        results_path = in_memory_results.get(job_id)
        if not results_path or not os.path.exists(results_path):
            raise HTTPException(status_code=404, detail="Results not found.")

        df = pd.read_csv(results_path)
        csv_content = df.to_csv(index=False)
        output_filename = f"enriched_{job.filename}"

    if not output_filename.endswith(".csv"):
        output_filename = output_filename.rsplit(".", 1)[0] + ".csv"

    safe_filename = sanitize_filename(output_filename)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'},
    )


@app.get("/api/jobs", response_model=JobListResponse)
async def list_jobs(session_id: Optional[str] = None):
    """
    List all jobs, optionally filtered by session_id.

    If no session_id is provided, returns an empty list (for privacy).
    Pass the session_id returned during upload to see your jobs.
    """
    if not session_id:
        return JobListResponse(jobs=[])

    if redis_available():
        jobs = job_manager.get_user_jobs(session_id)
        return JobListResponse(jobs=[job_to_status(job) for job in jobs])
    else:
        # In-memory fallback
        jobs = [
            JobStatus(
                id=job.job_id,
                status=job.status,
                filename=job.filename,
                total_records=job.total_records,
                processed_records=job.processed_records,
                error_message=job.error_message,
                created_at=job.created_at.isoformat(),
            )
            for job in in_memory_jobs.values()
            if job.session_id == session_id
        ]
        return JobListResponse(jobs=sorted(jobs, key=lambda j: j.created_at, reverse=True))


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str, session_id: Optional[str] = None):
    """Delete a specific job."""
    if redis_available():
        success = job_manager.delete_job(job_id, session_id)
        if success:
            return {"message": f"Job {job_id} deleted"}
        raise HTTPException(status_code=500, detail="Failed to delete job")
    else:
        # In-memory fallback
        if job_id in in_memory_jobs:
            del in_memory_jobs[job_id]
            if job_id in in_memory_results:
                del in_memory_results[job_id]
            return {"message": f"Job {job_id} deleted"}
        raise HTTPException(status_code=404, detail="Job not found")


@app.delete("/api/jobs")
async def delete_all_jobs(session_id: str):
    """Delete all jobs for a session."""
    if redis_available():
        deleted = job_manager.delete_all_jobs(session_id)
        return {"message": f"Deleted {deleted} jobs"}
    else:
        # In-memory fallback
        to_delete = [jid for jid, job in in_memory_jobs.items() if job.session_id == session_id]
        for jid in to_delete:
            del in_memory_jobs[jid]
            if jid in in_memory_results:
                del in_memory_results[jid]
        return {"message": f"Deleted {len(to_delete)} jobs"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "cors_origins": CORS_ORIGINS,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
