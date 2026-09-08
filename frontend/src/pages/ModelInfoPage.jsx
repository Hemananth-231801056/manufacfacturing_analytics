import { useState, useEffect } from 'react';
import { getModelInfo } from '../services/api';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, Tooltip,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Cell
} from 'recharts';

export default function ModelInfoPage() {
  const [info, setInfo]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    getModelInfo().then(setInfo).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <main className="page-content" style={{ display: 'flex', justifyContent: 'center', paddingTop: 80 }}>
      <div style={{ textAlign: 'center' }}>
        <div className="spinner spinner-lg" style={{ margin: '0 auto 16px' }} />
        <p style={{ color: 'var(--text-secondary)' }}>Loading model info…</p>
      </div>
    </main>
  );

  if (error) return (
    <main className="page-content">
      <div className="alert alert-error"><span>✕</span> {error} — Train the model first using <code>python scripts/train_model.py</code></div>
    </main>
  );

  const metrics = [
    { name: 'Accuracy',    value: +(info.accuracy * 100).toFixed(1) },
    { name: 'F1 Weighted', value: +(info.f1_weighted * 100).toFixed(1) },
    { name: 'F1 Macro',    value: +(info.f1_macro * 100).toFixed(1) },
  ];

  const classDist = Object.entries(info.class_distribution || {}).map(([cls, cnt]) => ({
    name: cls, count: cnt,
    color: cls === 'Approved' ? '#10b981' : cls === 'Rework' ? '#f59e0b' : '#ef4444'
  }));

  const radarData = metrics.map(m => ({ metric: m.name, value: m.value }));

  return (
    <main className="page-content fade-up">
      <div className="page-header">
        <div className="page-header-left">
          <h1>Model Information</h1>
          <p>Trained ML model evaluation metrics and feature details.</p>
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="stats-row" style={{ marginBottom: 28 }}>
        {[
          { label: 'Model Type',       value: info.model_type,                  cls: 'stat-total' },
          { label: 'Accuracy',         value: `${(info.accuracy*100).toFixed(2)}%`, cls: 'stat-approved' },
          { label: 'F1 Score (Wt.)',   value: info.f1_weighted.toFixed(4),      cls: 'stat-approved' },
          { label: 'Training Samples', value: info.training_samples,            cls: 'stat-total' },
          { label: 'Test Samples',     value: info.test_samples,                cls: 'stat-rework' },
          { label: 'Features',         value: info.feature_count,               cls: 'stat-total' },
        ].map(s => (
          <div key={s.label} className="stat-card">
            <div className="stat-label">{s.label}</div>
            <div className={`stat-value ${s.cls}`} style={{ fontSize: typeof s.value === 'string' && s.value.length > 8 ? '1.1rem' : '1.6rem' }}>
              {s.value}
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>
        {/* Radar Chart */}
        <div className="card">
          <h3 style={{ marginBottom: 16, fontSize: '0.95rem', fontWeight: 600 }}>Performance Metrics</h3>
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.08)" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} />
              <Radar dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.25} dot />
              <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text-primary)' }} formatter={(v) => [`${v}%`]} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Class Distribution */}
        <div className="card">
          <h3 style={{ marginBottom: 16, fontSize: '0.95rem', fontWeight: 600 }}>Training Class Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={classDist} barSize={52}>
              <XAxis dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text-primary)' }} cursor={false} />
              <Bar dataKey="count" radius={[6,6,0,0]}>
                {classDist.map(e => <Cell key={e.name} fill={e.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Feature List */}
      <div className="card">
        <h3 style={{ marginBottom: 16, fontSize: '0.95rem', fontWeight: 600 }}>
          Model Feature Set ({info.feature_count} features)
        </h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {(info.feature_names || []).map(feat => (
            <span
              key={feat}
              style={{
                padding: '4px 10px',
                background: 'rgba(59,130,246,0.08)',
                border: '1px solid rgba(59,130,246,0.2)',
                borderRadius: 6,
                fontSize: '0.75rem',
                fontFamily: 'var(--mono)',
                color: 'var(--accent-2)'
              }}
            >
              {feat}
            </span>
          ))}
        </div>
      </div>
    </main>
  );
}
