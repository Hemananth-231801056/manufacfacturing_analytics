import { useState } from 'react';
import BatchForm from '../components/BatchForm';
import PredictionResult from '../components/PredictionResult';
import { submitPrediction } from '../services/api';

function BatchPrediction() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handlePredict = async (formData) => {
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const data = await submitPrediction(formData);
      setResult(data);
    } catch (err) {
      setError(err.message || 'An error occurred during prediction.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
  };

  return (
    <div className="batch-prediction fade-in">
      <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <h1 style={{ color: 'var(--accent-teal)' }}>Batch Quality Evaluation</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Enter process and material parameters to evaluate batch quality.</p>
      </div>

      {error && (
        <div className="glass-card" style={{ borderColor: 'var(--accent-rose)', padding: '1rem', marginBottom: '2rem', color: 'var(--accent-rose)' }}>
          {error}
        </div>
      )}

      {!result && (
        <BatchForm onSubmit={handlePredict} isLoading={loading} />
      )}

      {result && (
        <PredictionResult result={result} onReset={handleReset} />
      )}
    </div>
  );
}

export default BatchPrediction;
