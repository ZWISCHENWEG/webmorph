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
        return { color: 'var(--accent-cyan)', borderColor: 'rgba(0, 240, 255, 0.2)', bg: 'rgba(0, 240, 255, 0.05)' };
      case 'DEGRADED':
      case 'DIAGNOSING':
      case 'AWAITING_APPROVAL':
      case 'HEALING':
      case 'VERIFYING':
        return { color: 'var(--accent-amber)', borderColor: 'rgba(255, 170, 0, 0.2)', bg: 'rgba(255, 170, 0, 0.05)' };
      case 'DRIFT_DETECTED':
      case 'REJECTED':
      case 'HEAL_PROPOSED':
      case 'MANUAL_INTERVENTION':
        return { color: 'var(--accent-magenta)', borderColor: 'rgba(255, 0, 85, 0.2)', bg: 'rgba(255, 0, 85, 0.05)' };
      default:
        return { color: 'var(--text-secondary)', borderColor: 'var(--border-subtle)', bg: 'transparent' };
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
          borderRadius: '4px',
          fontSize: '0.75rem',
          fontWeight: 600,
          fontFamily: 'var(--font-mono)',
          letterSpacing: '0.05em',
          color: style.color,
          backgroundColor: style.bg,
          border: `1px solid ${style.borderColor}`,
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
