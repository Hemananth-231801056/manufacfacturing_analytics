import { useEffect, useState } from 'react';
import { getPredictions } from '../services/api';
import { Loader, ChevronLeft, ChevronRight, Search } from 'lucide-react';
import './PredictionHistory.css';

function PredictionHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('All');

  // Hardcoded mockup data in case API fails
  const mockData = [
    { id: 1, batch_id: 'BATCH-8321', predicted_class: 'Approved', confidence: 0.92, decision: 'Proceed to release.', created_at: '2023-10-12T10:30:00Z' },
    { id: 2, batch_id: 'BATCH-4912', predicted_class: 'Rework', confidence: 0.74, decision: 'Rework required.', created_at: '2023-10-11T14:15:00Z' },
    { id: 3, batch_id: 'BATCH-7742', predicted_class: 'Rejected', confidence: 0.88, decision: 'Batch rejected due to impurities.', created_at: '2023-10-10T09:45:00Z' }
  ];

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getPredictions(1, 50);
        setHistory(data.items || data);
      } catch (err) {
        // Fallback to mock data for demo purposes if backend isn't up
        console.warn('Backend unavailable, using mock data.');
        setHistory(mockData);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const filteredHistory = filter === 'All' 
    ? history 
    : history.filter(item => item.predicted_class === filter);

  if (loading) return <div className="loading-state"><Loader className="spinner" size={32} /></div>;

  return (
    <div className="prediction-history fade-in">
      <div className="history-header">
        <div>
          <h1>Batch History</h1>
          <p>Review past batch evaluations and decisions.</p>
        </div>
        <div className="filter-controls glass-card">
          {['All', 'Approved', 'Rework', 'Rejected'].map(status => (
            <button 
              key={status}
              className={`filter-btn ${filter === status ? 'active' : ''}`}
              onClick={() => setFilter(status)}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      <div className="table-container glass-card">
        {filteredHistory.length === 0 ? (
          <div className="empty-state">No predictions found for this filter.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Batch ID</th>
                <th>Date</th>
                <th>Prediction</th>
                <th>Confidence</th>
                <th>Decision</th>
              </tr>
            </thead>
            <tbody>
              {filteredHistory.map((item) => (
                <tr key={item.id || item.batch_id}>
                  <td className="mono">{item.batch_id}</td>
                  <td>{new Date(item.created_at).toLocaleString()}</td>
                  <td>
                    <span className={`badge status-${item.predicted_class.toLowerCase()}`}>
                      {item.predicted_class}
                    </span>
                  </td>
                  <td>{Math.round(item.confidence * 100)}%</td>
                  <td className="truncate-text" title={item.decision}>{item.decision || item.decision_details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default PredictionHistory;
