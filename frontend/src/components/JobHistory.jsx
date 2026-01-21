function JobHistory({ jobs, isLoading, onJobSelect, onDownload, onRefresh, onDelete }) {
  const getRelativeTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

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
        return 'Processing';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'pending':
        return 'Pending';
      default:
        return status;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return (
          <svg className="status-icon status-icon-success" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        );
      case 'failed':
        return (
          <svg className="status-icon status-icon-error" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        );
      case 'processing':
        return <span className="status-icon-spinner-small"></span>;
      case 'pending':
        return (
          <svg className="status-icon status-icon-pending" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="job-history">
      <div className="job-history-header">
        <h3 className="job-history-title">Job History</h3>
        <button
          className="job-history-refresh"
          onClick={onRefresh}
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {isLoading && jobs.length === 0 ? (
        <div className="loading">
          <div className="loading-spinner" />
          <p>Loading jobs...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="job-history-empty">
          <svg className="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="48" height="48">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
          <p className="empty-state-title">No enrichments yet</p>
          <p className="empty-state-subtitle">Upload a file to get started!</p>
        </div>
      ) : (
        <div className="job-history-list">
          {jobs.map((job) => {
            const jobId = job.id ?? job.job_id;
            return (
              <div
                key={jobId}
                className="job-history-item"
                onClick={() => onJobSelect(job)}
              >
                <div className="job-history-item-info">
                  <p className="job-history-item-filename">{job.filename}</p>
                  <p className="job-history-item-date">
                    {getRelativeTime(job.created_at)}
                  </p>
                </div>
                <div className="job-history-item-actions">
                  <span className={getStatusBadgeClass(job.status)}>
                    {getStatusIcon(job.status)}
                    {getStatusText(job.status)}
                  </span>
                  {job.status === 'completed' && (
                    <button
                      className="job-history-download-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDownload(jobId, job.filename);
                      }}
                    >
                      <svg className="download-icon-small" viewBox="0 0 20 20" fill="currentColor" width="12" height="12">
                        <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                      Download
                    </button>
                  )}
                  <button
                    className="job-history-delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(jobId);
                    }}
                    title="Delete job"
                  >
                    <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                      <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default JobHistory;
