import React from 'react';
import { HealingEvent } from '../../types';

export function HealingProposal({ event, incidentStatus }: { event: HealingEvent, incidentStatus: string }) {
  if (!event.proposal) {
    return null;
  }

  const { proposal } = event;
  const isRejected = event.approval_status === 'REJECTED' || incidentStatus === 'REJECTED';

  let borderColor = 'var(--border-cyan)';
  let bgColor = 'rgba(0, 229, 255, 0.05)';

  if (isRejected) {
    borderColor = 'var(--border-red)';
    bgColor = 'rgba(255, 42, 42, 0.05)';
  } else if (incidentStatus === 'AWAITING_APPROVAL') {
    borderColor = 'rgba(255, 170, 0, 0.4)';
    bgColor = 'rgba(255, 170, 0, 0.05)';
  }

  return (
    <div className="angular-panel glass-panel stat-card" style={{ backgroundColor: bgColor, border: `1px solid ${borderColor}` }}>
      <div className="flex-row" style={{ justifyContent: 'space-between', marginBottom: '24px', borderBottom: `1px dashed ${borderColor}`, paddingBottom: '16px' }}>
        <h3 className="section-header">Heal Proposal Review</h3>
        <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', padding: '6px 12px', backgroundColor: 'var(--bg-panel-secondary)', border: `1px solid ${borderColor}`, color: 'var(--text-primary)' }}>
          STATUS: {event.approval_status}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        <div>
          <h4 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '12px', fontFamily: 'var(--font-mono)' }}>PROPOSED CHANGES</h4>
          {proposal.changes && proposal.changes.length > 0 ? (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {proposal.changes.map((change: string, idx: number) => (
                <li key={idx} style={{ padding: '12px', backgroundColor: 'var(--bg-panel-secondary)', borderLeft: `2px solid ${borderColor}`, marginBottom: '8px', fontSize: '0.875rem', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
                  {change}
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>[ NO SPECIFIC CHANGES LISTED ]</p>
          )}
        </div>

        <div>
          <h4 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '12px', fontFamily: 'var(--font-mono)' }}>IMPACT & RISK</h4>
          <div style={{ padding: '16px', backgroundColor: 'var(--bg-panel-secondary)', border: '1px solid var(--border-tech)' }}>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '12px', fontFamily: 'var(--font-mono)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>RISK LEVEL: </span>
              <span style={{
                color: proposal.risk_level === 'HIGH' ? 'var(--accent-red)' : proposal.risk_level === 'MEDIUM' ? 'var(--accent-warning)' : 'var(--accent-cyan)',
                fontWeight: 600
              }}>
                {proposal.risk_level || 'UNKNOWN'}
              </span>
            </p>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {proposal.impact_assessment || 'No impact assessment provided.'}
            </p>
          </div>
        </div>
      </div>

      <div style={{ borderTop: `1px solid ${borderColor}`, paddingTop: '16px' }}>
        <details>
          <summary>[ VIEW RAW PROPOSAL JSON ]</summary>
          <pre className="raw-code">
            {JSON.stringify(proposal, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}
