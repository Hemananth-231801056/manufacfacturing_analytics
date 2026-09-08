import { useEffect, useState } from 'react';
import { getPredictions, downloadReport } from '../services/api';
import { FileText, Download, Loader } from 'lucide-react';
import './Reports.css';

function Reports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  const mockData = [
    { id: 1, batch_id: 'BATCH-8321', predicted_class: 'Approved', created_at: '2023-10-12T10:30:00Z' },
    { id: 2, batch_id: 'BATCH-4912', predicted_class: 'Rework', created_at: '2023-10-11T14:15:00Z' }
  ];

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const data = await getPredictions(1, 20);
        setReports(data.items || data);
      } catch (err) {
        setReports(mockData);
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  }, []);

  const handleDownload = async (id, batchId) => {
    try {
      await downloadReport(id);
    } catch (err) {
      alert(`Backend unavailable. Cannot download report for ${batchId}.`);
    }
  };

  if (loading) return <div className="loading-state"><Loader className="spinner" size={32} /></div>;

  return (
    <div className="reports-page fade-in">
      <div className="reports-header">
        <h1>QA/QC Reports</h1>
        <p>Download official PDF evaluation reports for batch release documentation.</p>
      </div>

      <div className="reports-grid">
        {reports.length === 0 ? (
          <div className="glass-card empty-state">No reports available.</div>
        ) : (
          reports.map(report => (
            <div key={report.id || report.batch_id} className="report-card glass-card">
              <div className="report-icon">
                <FileText size={32} />
              </div>
              <div className="report-info">
                <h3>{report.batch_id}</h3>
                <p>{new Date(report.created_at).toLocaleDateString()}</p>
                <span className={`badge status-${report.predicted_class.toLowerCase()}`}>
                  {report.predicted_class}
                </span>
              </div>
              <button 
                className="btn btn-outline download-btn"
                onClick={() => handleDownload(report.id || 1, report.batch_id)}
              >
                <Download size={18} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Reports;
