import { useEffect, useState } from 'react';

function ConfidenceGauge({ score }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedScore(score);
    }, 300);
    return () => clearTimeout(timer);
  }, [score]);

  // Convert probability to percentage
  const percentage = Math.round(animatedScore * 100);
  
  let color = 'var(--accent-rose)';
  if (percentage >= 80) color = 'var(--accent-teal)';
  else if (percentage >= 60) color = 'var(--accent-amber)';

  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div style={{ position: 'relative', width: '150px', height: '150px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <svg width="150" height="150" style={{ transform: 'rotate(-90deg)' }}>
        <circle
          cx="75" cy="75" r={radius}
          stroke="rgba(255,255,255,0.1)"
          strokeWidth="12"
          fill="none"
        />
        <circle
          cx="75" cy="75" r={radius}
          stroke={color}
          strokeWidth="12"
          fill="none"
          strokeLinecap="round"
          style={{
            strokeDasharray: circumference,
            strokeDashoffset: strokeDashoffset,
            transition: 'stroke-dashoffset 1s ease-out, stroke 1s ease'
          }}
        />
      </svg>
      <div style={{ position: 'absolute', fontSize: '1.5rem', fontWeight: 'bold', fontFamily: 'var(--font-mono)' }}>
        {percentage}%
      </div>
    </div>
  );
}

export default ConfidenceGauge;
