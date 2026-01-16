import { useState, useEffect, useCallback } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import JobStatus from './components/JobStatus';
import JobHistory from './components/JobHistory';
import { uploadFile, startJob, getJobStatus, getJobResults, getJobs } from './api';

function App() {
  // Current file/job state
  const [currentFile, setCurrentFile] = useState(null);
  const [currentJob, setCurrentJob] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  // Job history
  const [jobs, setJobs] = useState([]);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);

  // Load job history on mount
  useEffect(() => {
    loadJobs();
  }, []);

  // Poll for job status when there's an active job
  useEffect(() => {
    if (!currentJob || currentJob.status === 'completed' || currentJob.status === 'failed') {
      return;
    }

    const jobId = currentJob.id ?? currentJob.job_id;
    if (!jobId) return;

    const interval = setInterval(async () => {
      try {
        const status = await getJobStatus(jobId);
        setCurrentJob(prev => ({ ...prev, ...status, job_id: jobId }));

        if (status.status === 'completed' || status.status === 'failed') {
          loadJobs(); // Refresh job history
        }
      } catch (err) {
        console.error('Failed to poll job status:', err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [currentJob?.id, currentJob?.job_id, currentJob?.status]);

  const loadJobs = async () => {
    try {
      setIsLoadingJobs(true);
      const jobList = await getJobs();
      setJobs(jobList);
    } catch (err) {
      console.error('Failed to load jobs:', err);
    } finally {
      setIsLoadingJobs(false);
    }
  };

  const handleFileSelect = useCallback((file) => {
    setCurrentFile(file);
    setError(null);
  }, []);

  const handleUpload = async () => {
    if (!currentFile) return;

    setIsUploading(true);
    setError(null);

    try {
      // Upload the file
      const uploadResult = await uploadFile(currentFile);

      // Start processing
      await startJob(uploadResult.job_id);

      // Set current job and start polling
      setCurrentJob({
        job_id: uploadResult.job_id,
        filename: uploadResult.filename,
        status: 'processing',
        processed_records: 0,
        total_records: uploadResult.total_records,
      });

      setCurrentFile(null);
      loadJobs();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownload = async (jobId, filename) => {
    try {
      const blob = await getJobResults(jobId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `enriched_${filename}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleJobSelect = (job) => {
    setCurrentJob(job);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🍽️ Restaurant Lead Enrichment</h1>
        <p className="subtitle">Discover restaurant owners in seconds — transform your leads with powerful insights</p>
      </header>

      <main className="main">
        <section className="upload-section">
          <FileUpload
            onFileSelect={handleFileSelect}
            currentFile={currentFile}
            disabled={isUploading}
          />

          {currentFile && (
            <button
              className="upload-btn"
              onClick={handleUpload}
              disabled={isUploading}
            >
              {isUploading ? 'Uploading...' : 'Start Processing'}
            </button>
          )}

          {error && <p className="error">{error}</p>}
        </section>

        {currentJob && (
          <section className="status-section">
            <JobStatus
              job={currentJob}
              onDownload={handleDownload}
            />
          </section>
        )}

        <section className="history-section">
          <JobHistory
            jobs={jobs}
            isLoading={isLoadingJobs}
            onJobSelect={handleJobSelect}
            onDownload={handleDownload}
            onRefresh={loadJobs}
          />
        </section>
      </main>

      <footer className="footer">
        <p>Made with care for restaurant industry professionals</p>
      </footer>
    </div>
  );
}

export default App;
