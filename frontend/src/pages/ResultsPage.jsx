import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getDocumentPredictions, downloadReport, downloadAllReports } from '../services/api';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts';

const DECISION_COLORS = { Approved: '#10b981', Rework: '#f59e0b', Rejected: '#ef4444', Error: '#6b7280' };

function getBadgeClass(d) {
  const m = { Approved: 'approved', Rework: 'rework', Rejected: 'rejected' };
  return `badge badge-${m[d] || 'error'}`;
}

function ConfidenceBar({ confidence, decision }) {
  const color = DECISION_COLORS[decision] || '#6b7280';
  return (
    <div className="confidence-bar-wrap">
      <label>
        <span>Confidence Score</span>
        <span style={{ color, fontWeight: 700 }}>{(confidence * 100).toFixed(1)}%</span>
      </label>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${confidence * 100}%`, background: color }} />
      </div>
    </div>
  );
}

function ShapChart({ shapValues }) {
  const entries = Object.entries(shapValues || {})
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 12);
  if (!entries.length) return null;
  const maxAbs = Math.max(...entries.map(([, v]) => Math.abs(v)));
  return (
    <div className="shap-container">
      <h4>SHAP Feature Impact</h4>
      {entries.map(([feat, val]) => (
        <div key={feat} className="shap-bar-row">
          <div className="shap-feature" title={feat}>{feat}</div>
          <div className="shap-bar-track">
            <div
              className="shap-bar-fill"
              style={{
                width: `${(Math.abs(val) / maxAbs) * 100}%`,
                background: val >= 0 ? '#10b981' : '#ef4444',
                marginLeft: val >= 0 ? 0 : 'auto'
              }}
            />
          </div>
          <div className="shap-val">{val >= 0 ? '+' : ''}{val.toFixed(4)}</div>
        </div>
      ))}
    </div>
  );
}

function BatchCard({ result, idx }) {
  const [expanded, setExpanded] = useState(false);
  const cls = (result.decision || '').toLowerCase();

  return (
    <div className={`result-card ${cls} fade-up`} style={{ animationDelay: `${idx * 0.05}s` }}>
      <div className="result-header">
        <div className="result-header-left">
          <span style={{ fontSize: '1.1rem' }}>
            {cls === 'approved' ? '✅' : cls === 'rework' ? '🔶' : cls === 'rejected' ? '🚫' : '⚠️'}
          </span>
          <div>
            <div className="batch-id">{result.batch_id}</div>
            <span className={getBadgeClass(result.decision)}>{result.decision}</span>
          </div>
        </div>
        <div className="result-header-right">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Model: <strong style={{ color: 'var(--text-primary)' }}>{result.prediction}</strong>
          </span>
          {result.report_url && (
            <button
              className="btn btn-outline btn-sm"
              onClick={() => downloadReport(result.id, result.batch_id)}
            >
              ⬇ PDF Report
            </button>
          )}
        </div>
      </div>

      <div className="result-body">
        <ConfidenceBar confidence={result.confidence} decision={result.decision} />

        {/* Class probabilities */}
        <div className="result-grid">
          {Object.entries(result.confidence_scores || {}).map(([cls, prob]) => (
            <div key={cls} className="result-field">
              <label>{cls}</label>
              <div className="value" style={{ color: DECISION_COLORS[cls] || 'var(--text-primary)' }}>
                {(prob * 100).toFixed(2)}%
              </div>
            </div>
          ))}
        </div>

        {/* Decision details */}
        {result.decision_details && (
          <div className="alert alert-info" style={{ marginBottom: 16 }}>
            <span>ℹ</span>
            <div>{result.decision_details}</div>
          </div>
        )}

        {/* Recommendation */}
        {result.recommendation && (
          <div className="recommendation-box">
            <h4>Recommendation</h4>
            <p>{result.recommendation}</p>
          </div>
        )}

        {/* Expand for CAPA & SHAP */}
        <button className="accordion-toggle" onClick={() => setExpanded(e => !e)}>
          {expanded ? '▲ Hide' : '▼ Show'} Corrective Action & SHAP Analysis
        </button>

        {expanded && (
          <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 16 }}>
            {result.corrective_action && (
              <div className="recommendation-box" style={{ borderColor: 'rgba(245,158,11,0.2)' }}>
                <h4 style={{ color: 'var(--warning)' }}>Corrective Action (CAPA)</h4>
                <p>{result.corrective_action}</p>
              </div>
            )}
            {result.investigation && (
              <div className="recommendation-box" style={{ borderColor: 'rgba(239,68,68,0.2)' }}>
                <h4 style={{ color: 'var(--danger)' }}>Investigation Plan</h4>
                <p>{result.investigation}</p>
              </div>
            )}
            {result.shap_values && Object.keys(result.shap_values).length > 0 && (
              <ShapChart shapValues={result.shap_values} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ResultsPage() {
  const { id } = useParams();
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);
  const [filter, setFilter] = useState('All');

  useEffect(() => {
    getDocumentPredictions(id)
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <main className="page-content" style={{ display: 'flex', justifyContent: 'center', paddingTop: 80 }}>
      <div style={{ textAlign: 'center' }}>
        <div className="spinner spinner-lg" style={{ margin: '0 auto 16px' }} />
        <p style={{ color: 'var(--text-secondary)' }}>Loading batch prediction results…</p>
      </div>
    </main>
  );

  if (error) return (
    <main className="page-content">
      <div className="alert alert-error"><span>✕</span> {error}</div>
    </main>
  );

  const results = data?.results || [];
  const counts = results.reduce((acc, r) => {
    acc[r.decision] = (acc[r.decision] || 0) + 1;
    return acc;
  }, {});

  const chartData = Object.entries(DECISION_COLORS)
    .filter(([d]) => counts[d])
    .map(([d, color]) => ({ name: d, count: counts[d] || 0, color }));

  const filtered = filter === 'All' ? results : results.filter(r => r.decision === filter);

  return (
    <main className="page-content fade-up">
      <div className="page-header">
        <div className="page-header-left">
          <h1>Batch Results</h1>
          <p>Document #{id} — {results.length} batch(es) evaluated</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          {results.length > 1 && (
            <button 
              className="btn btn-primary"
              onClick={() => downloadAllReports(id)}
            >
              ⬇ Download All (.zip)
            </button>
          )}
          <Link to="/" className="btn btn-outline">↑ New Upload</Link>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="stats-row">
        {[
          { label: 'Total Batches',    value: results.length,              cls: 'stat-total' },
          { label: 'Approved',         value: counts.Approved || 0,        cls: 'stat-approved' },
          { label: 'Rework',           value: counts.Rework || 0,          cls: 'stat-rework' },
          { label: 'Rejected',         value: counts.Rejected || 0,        cls: 'stat-rejected' },
        ].map(s => (
          <div key={s.label} className="stat-card">
            <div className="stat-label">{s.label}</div>
            <div className={`stat-value ${s.cls}`}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Bar Chart */}
      {chartData.length > 0 && (
        <div className="card" style={{ marginBottom: 24, height: 200 }}>
          <h3 style={{ marginBottom: 16, fontSize: '0.9rem', fontWeight: 600 }}>Decision Distribution</h3>
          <ResponsiveContainer width="100%" height={140}>
            <BarChart data={chartData} barSize={48}>
              <XAxis dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip
                contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)' }}
                cursor={{ fill: 'rgba(255,255,255,0.04)' }}
              />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {chartData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="tab-bar">
        {['All', 'Approved', 'Rework', 'Rejected'].map(f => (
          <button key={f} className={`tab${filter === f ? ' active' : ''}`} onClick={() => setFilter(f)}>
            {f} {counts[f] !== undefined ? `(${counts[f]})` : f === 'All' ? `(${results.length})` : ''}
          </button>
        ))}
      </div>

      {/* Batch Cards */}
      {filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h3>No batches match this filter</h3>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {filtered.map((r, i) => (
            <BatchCard key={r.id || r.batch_id} result={r} idx={i} />
          ))}
        </div>
      )}
    </main>
  );
}
