function JobStatus({ job, onDownload }) {
  if (!job) return null;

  // Handle both API field names (processed_records/total_records) and legacy names (progress/total)
  const processed = job.processed_records ?? job.progress ?? 0;
  const total = job.total_records ?? job.total ?? 0;
  const jobId = job.id ?? job.job_id;

  const progressPercent = total > 0
    ? Math.round((processed / total) * 100)
    : 0;

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'processing':
        return 'job-status-badge processing';
      case 'completed':
        return 'job-status-badge completed';
      case 'failed':
        return 'job-status-badge failed';
      default:
        return 'job-status-badge pending';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'processing':
        return 'Finding restaurant owners...';
      case 'completed':
        return 'All done!';
      case 'failed':
        return 'Oops! Something went wrong';
      case 'pending':
        return 'Getting ready...';
      default:
        return status;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return (
          <svg className="status-icon status-icon-success" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        );
      case 'failed':
        return (
          <svg className="status-icon status-icon-error" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      case 'processing':
        return <span className="status-icon-spinner"></span>;
      case 'pending':
        return (
          <svg className="status-icon status-icon-pending" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="job-status">
      <div className="job-status-header">
        <h3 className="job-status-title">{job.filename}</h3>
        <span className={getStatusBadgeClass(job.status)}>
          {getStatusIcon(job.status)}
          {getStatusText(job.status)}
        </span>
      </div>

      {job.status === 'processing' && (
        <div className="job-progress">
          <div className="job-progress-bar">
            <div
              className="job-progress-fill"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <p className="job-progress-text">
            {processed} of {total} records processed ({progressPercent}%)
          </p>
        </div>
      )}

      {job.status === 'completed' && (
        <button
          className="job-download-btn"
          onClick={() => onDownload(jobId, job.filename)}
        >
          <svg className="download-icon" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
          Download Enriched Data
        </button>
      )}

      {job.errors && job.errors.length > 0 && (
        <div className="job-errors">
          <h4 className="job-errors-title">Errors ({job.errors.length})</h4>
          <ul className="job-errors-list">
            {job.errors.slice(0, 5).map((error, index) => (
              <li key={index}>{error}</li>
            ))}
            {job.errors.length > 5 && (
              <li>...and {job.errors.length - 5} more errors</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

export default JobStatus;
