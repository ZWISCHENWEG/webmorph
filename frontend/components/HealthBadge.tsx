import React from 'react';

type HealthState = 'HEALTHY' | 'DEGRADED' | 'DRIFT_DETECTED' | 'DIAGNOSING' | 'HEAL_PROPOSED' | 'AWAITING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'HEALING' | 'VERIFYING' | 'RECOVERED' | 'MANUAL_INTERVENTION';

interface HealthBadgeProps {
  state: HealthState;
  score: number | null;
}

export function HealthBadge({ state, score }: HealthBadgeProps) {
  const getBadgeStyle = (s: HealthState) => {
    switch (s) {
      case 'HEALTHY':
      case 'APPROVED':
      case 'RECOVERED':
        return { color: 'var(--accent-cyan)', borderColor: 'var(--border-cyan)', bg: 'rgba(0, 229, 255, 0.05)' };
      case 'DEGRADED':
      case 'DIAGNOSING':
      case 'AWAITING_APPROVAL':
      case 'HEALING':
      case 'VERIFYING':
        return { color: 'var(--accent-warning)', borderColor: 'var(--border-tech)', bg: 'rgba(255, 170, 0, 0.05)' };
      case 'DRIFT_DETECTED':
      case 'REJECTED':
      case 'HEAL_PROPOSED':
      case 'MANUAL_INTERVENTION':
        return { color: 'var(--accent-red)', borderColor: 'var(--border-red)', bg: 'rgba(255, 42, 42, 0.05)' };
      default:
        return { color: 'var(--text-secondary)', borderColor: 'var(--border-tech)', bg: 'transparent' };
    }
  };

  const style = getBadgeStyle(state);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <span 
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          padding: '4px 8px',
          fontSize: '0.75rem',
          fontWeight: 600,
          fontFamily: 'var(--font-mono)',
          letterSpacing: '0.05em',
          color: style.color,
          backgroundColor: style.bg,
          border: `1px solid ${style.borderColor}`,
          textTransform: 'uppercase'
        }}
      >
        {state}
      </span>
      {score !== null && (
        <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
          {score.toFixed(1)}
        </span>
      )}
    </div>
  );
}
