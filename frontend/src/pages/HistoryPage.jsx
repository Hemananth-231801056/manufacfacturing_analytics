import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getDocuments } from '../services/api';

function StatusBadge({ status }) {
  const m = { success: 'success', ready: 'info', warning: 'warning', failed: 'error', pending: 'pending' };
  return <span className={`badge badge-${m[status] || 'pending'}`}>{status}</span>;
}

export default function HistoryPage() {
  const [docs, setDocs]       = useState([]);

  // Convert backend naive UTC string "YYYY-MM-DD HH:MM:SS" to Local Time
  const formatLocalTime = (utcString) => {
    if (!utcString) return '—';
    const d = new Date(utcString.replace(' ', 'T') + 'Z');
    return isNaN(d) ? utcString : d.toLocaleString();
  };
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    getDocuments()
      .then(setDocs)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <main className="page-content" style={{ display: 'flex', justifyContent: 'center', paddingTop: 80 }}>
      <div style={{ textAlign: 'center' }}>
        <div className="spinner spinner-lg" style={{ margin: '0 auto 16px' }} />
        <p style={{ color: 'var(--text-secondary)' }}>Loading history…</p>
      </div>
    </main>
  );

  return (
    <main className="page-content fade-up">
      <div className="page-header">
        <div className="page-header-left">
          <h1>Processing History</h1>
          <p>All previously uploaded batch files and their evaluation status.</p>
        </div>
        <Link to="/" className="btn btn-primary">↑ New Upload</Link>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 20 }}><span>✕</span> {error}</div>}

      {docs.length === 0 && !error ? (
        <div className="empty-state card">
          <div className="empty-icon">📂</div>
          <h3>No files uploaded yet</h3>
          <p>Upload your first pharmaceutical batch file to begin evaluation.</p>
          <Link to="/" className="btn btn-primary" style={{ marginTop: 8 }}>Upload Now</Link>
        </div>
      ) : (
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>File Name</th>
                <th>Format</th>
                <th>Status</th>
                <th>Total Batches</th>
                <th>Approved</th>
                <th>Rework/Rejected</th>
                <th>Uploaded At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {docs.map((doc, i) => (
                <tr key={doc.id} style={{ animationDelay: `${i * 0.04}s` }}>
                  <td style={{ color: 'var(--text-muted)', fontFamily: 'var(--mono)' }}>{doc.id}</td>
                  <td style={{ color: 'var(--text-primary)', fontWeight: 500, maxWidth: 240, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    📄 {doc.filename}
                  </td>
                  <td>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: '0.78rem', color: 'var(--accent-2)' }}>
                      {doc.file_format?.toUpperCase() || '—'}
                    </span>
                  </td>
                  <td><StatusBadge status={doc.status} /></td>
                  <td style={{ color: 'var(--accent-2)', fontWeight: 600 }}>{doc.total_batches}</td>
                  <td style={{ color: 'var(--success)', fontWeight: 600 }}>
                    {doc.valid_batches}
                  </td>
                  <td style={{ color: doc.failed_batches > 0 ? 'var(--warning)' : 'var(--text-muted)', fontWeight: 600 }}>
                    {doc.failed_batches}
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontFamily: 'var(--mono)' }}>
                    {formatLocalTime(doc.uploaded_at)}
                  </td>
                  <td>
                    <Link
                      to={`/results/${doc.id}`}
                      className="btn btn-outline btn-sm"
                    >
                      View Results →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
