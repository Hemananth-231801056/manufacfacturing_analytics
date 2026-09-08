import React from 'react';

function MetricsCard({ title, value, icon, subtitle }) {
  return (
    <div className="metrics-card glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
      <div style={{ color: 'var(--accent-teal)', background: 'rgba(6, 214, 160, 0.1)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
        {icon}
      </div>
      <div>
        <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{title}</p>
        <h4 style={{ margin: '0.25rem 0', fontSize: '1.5rem', fontFamily: 'var(--font-mono)' }}>{value}</h4>
        {subtitle && <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>{subtitle}</p>}
      </div>
    </div>
  );
}

export default MetricsCard;
