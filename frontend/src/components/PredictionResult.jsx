import { CheckCircle, AlertTriangle, XCircle, Download, ArrowLeft } from 'lucide-react';
import ShapChart from './ShapChart';
import ConfidenceGauge from './ConfidenceGauge';
import MetricsCard from './MetricsCard';
import './PredictionResult.css';
import { downloadReport } from '../services/api';

function PredictionResult({ result, onReset }) {
  const handleDownload = async () => {
    try {
      await downloadReport(result.prediction_id);
    } catch (err) {
      alert('Failed to download report. Please ensure the backend is running.');
    }
  };

  const getStatusConfig = (status) => {
    switch (status) {
      case 'Approved': return { icon: <CheckCircle />, colorClass: 'status-approved', color: 'var(--accent-teal)' };
      case 'Rework': return { icon: <AlertTriangle />, colorClass: 'status-rework', color: 'var(--accent-amber)' };
      case 'Rejected': return { icon: <XCircle />, colorClass: 'status-rejected', color: 'var(--accent-rose)' };
      default: return { icon: <CheckCircle />, colorClass: 'status-approved', color: 'var(--accent-teal)' };
    }
  };

  const config = getStatusConfig(result.predicted_class);

  return (
    <div className="prediction-result fade-in">
      <div className="result-header">
        <button onClick={onReset} className="btn btn-outline btn-sm">
          <ArrowLeft size={16} /> Back
        </button>
        <h2>Evaluation Result for {result.batch_id}</h2>
        <button onClick={handleDownload} className="btn btn-outline">
          <Download size={18} /> Download Report
        </button>
      </div>

      <div className="result-main-grid">
        <div className={`status-card glass-card ${config.colorClass}-border`}>
          <div className="status-badge-large" style={{ color: config.color }}>
            {config.icon}
            <span>{result.predicted_class}</span>
          </div>
          <p className="decision-text">{result.decision_details}</p>
        </div>

        <div className="confidence-card glass-card">
          <h3>Confidence Score</h3>
          <ConfidenceGauge score={result.confidence} />
        </div>
      </div>

      <div className="recommendations-grid">
        <div className="rec-card glass-card">
          <h4>Recommendation</h4>
          <p>{result.recommendation}</p>
        </div>
        {(result.predicted_class === 'Rework' || result.predicted_class === 'Rejected') && (
          <div className="rec-card glass-card warning">
            <h4>Corrective Action</h4>
            <p>{result.corrective_action || 'Review process parameters and out-of-spec limits.'}</p>
          </div>
        )}
      </div>

      {result.shap_values && (
        <div className="shap-section glass-card">
          <h3>Feature Importance (SHAP)</h3>
          <p className="shap-desc">These variables had the most impact on the final decision.</p>
          <ShapChart data={result.shap_values} />
        </div>
      )}
    </div>
  );
}

export default PredictionResult;
