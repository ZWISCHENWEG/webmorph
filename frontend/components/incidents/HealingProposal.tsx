import React from 'react';
import { HealingEvent } from '../../types';

export function HealingProposal({ event, incidentStatus }: { event: HealingEvent, incidentStatus: string }) {
  if (!event.proposal) {
    return null;
  }

  const { proposal } = event;
  const isRejected = event.approval_status === 'REJECTED' || incidentStatus === 'REJECTED';

  let borderColor = 'var(--accent-cyan)';
  let bgColor = 'rgba(0, 240, 255, 0.05)';
  
  if (isRejected) {
    borderColor = 'var(--accent-magenta)';
    bgColor = 'rgba(255, 0, 85, 0.05)';
  } else if (incidentStatus === 'AWAITING_APPROVAL') {
    borderColor = 'var(--accent-amber)';
    bgColor = 'rgba(255, 170, 0, 0.05)';
  }

  return (
    <div style={{ padding: '24px', backgroundColor: bgColor, border: `1px solid ${borderColor}`, borderRadius: '4px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)' }}>Heal Proposal</h3>
        <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', padding: '4px 8px', backgroundColor: 'var(--bg-secondary)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
          {event.approval_status}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
        <div>
          <h4 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>PROPOSED CHANGES</h4>
          {proposal.changes && proposal.changes.length > 0 ? (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {proposal.changes.map((change: string, idx: number) => (
                <li key={idx} style={{ padding: '8px 12px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', marginBottom: '8px', fontSize: '0.875rem' }}>
                  {change}
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No specific changes listed.</p>
          )}
        </div>

        <div>
          <h4 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>IMPACT & RISK</h4>
          <div style={{ padding: '16px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
              <strong>Risk Level:</strong> <span style={{ color: proposal.risk_level === 'HIGH' ? 'var(--accent-magenta)' : proposal.risk_level === 'MEDIUM' ? 'var(--accent-amber)' : 'var(--accent-cyan)' }}>{proposal.risk_level || 'UNKNOWN'}</span>
            </p>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              {proposal.impact_assessment || 'No impact assessment provided.'}
            </p>
          </div>
        </div>
      </div>

      <div>
        <details>
          <summary style={{ cursor: 'pointer', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>View Raw Proposal JSON</summary>
          <pre style={{ marginTop: '12px', padding: '16px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', overflowX: 'auto', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {JSON.stringify(proposal, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}
