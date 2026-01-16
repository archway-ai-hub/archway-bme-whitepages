const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = `${API_BASE}/api`;

// Generate or retrieve a persistent session ID
function getSessionId() {
  let sessionId = localStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem('session_id', sessionId);
  }
  return sessionId;
}

/**
 * Upload a CSV/Excel file for processing
 * @param {File} file - The file to upload
 * @returns {Promise<{job_id: string, filename: string}>}
 */
export async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/upload?session_id=${getSessionId()}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }

  return response.json();
}

/**
 * Start processing a job
 * @param {string} jobId - The job ID to start
 * @param {Object} options - Processing options
 * @returns {Promise<{status: string, message: string}>}
 */
export async function startJob(jobId, options = {}) {
  const response = await fetch(`${API_URL}/jobs/${jobId}/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(options),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to start job');
  }

  return response.json();
}

/**
 * Get the status of a job
 * @param {string} jobId - The job ID to check
 * @returns {Promise<{status: string, progress: number, total: number, errors: string[]}>}
 */
export async function getJobStatus(jobId) {
  const response = await fetch(`${API_URL}/jobs/${jobId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get job status');
  }

  return response.json();
}

/**
 * Download the results of a completed job
 * @param {string} jobId - The job ID to download
 * @returns {Promise<Blob>}
 */
export async function getJobResults(jobId) {
  const response = await fetch(`${API_URL}/jobs/${jobId}/results`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get results');
  }

  return response.blob();
}

/**
 * Get list of all jobs (history)
 * @returns {Promise<Array<{job_id: string, status: string, filename: string, created_at: string}>>}
 */
export async function getJobs() {
  const response = await fetch(`${API_URL}/jobs?session_id=${getSessionId()}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get jobs');
  }

  const data = await response.json();
  return data.jobs || [];
}

/**
 * Delete a job
 * @param {string} jobId - The job ID to delete
 * @returns {Promise<{message: string}>}
 */
export async function deleteJob(jobId) {
  const response = await fetch(`${API_URL}/jobs/${jobId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete job');
  }

  return response.json();
}
