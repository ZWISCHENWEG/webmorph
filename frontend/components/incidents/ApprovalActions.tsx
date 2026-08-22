import React, { useState } from 'react';
import { approveHeal } from '../../lib/api';

export function ApprovalActions({ incidentId, onActionSubmitted }: { incidentId: number, onActionSubmitted: (jobId?: string) => void }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAction = async (approved: boolean) => {
    try {
      setLoading(true);
      setError(null);
      const res = await approveHeal(incidentId, approved);
      onActionSubmitted(res.job_id);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to submit approval');
      setLoading(false);
    }
  };

  return (
    <div className="angular-panel glass-panel" style={{ padding: '24px', borderTop: '4px solid var(--accent-warning)', backgroundColor: 'rgba(255,170,0,0.05)' }}>
      <h3 className="section-header" style={{ marginBottom: '16px' }}>Human Approval Required</h3>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px', fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>
        Please review the proposed changes above. This action will apply the schema changes and trigger a verification run.
      </p>

      {error && (
        <div className="chromatic-error" style={{ marginBottom: '24px', color: 'var(--accent-red)', fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>
          {error}
        </div>
      )}

      <div className="flex-row">
        <button
          onClick={() => handleAction(true)}
          disabled={loading}
          style={{
            padding: '12px 24px',
            backgroundColor: 'rgba(0, 229, 255, 0.1)',
            color: 'var(--accent-cyan)',
            border: '1px solid var(--border-cyan)',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1,
            fontFamily: 'var(--font-mono)',
            letterSpacing: '0.05em',
          }}
          onMouseOver={(e) => { if(!loading) e.currentTarget.style.backgroundColor = 'rgba(0, 229, 255, 0.2)'; }}
          onMouseOut={(e) => { if(!loading) e.currentTarget.style.backgroundColor = 'rgba(0, 229, 255, 0.1)'; }}
        >
          {loading ? 'PROCESSING...' : '[ APPROVE HEAL ]'}
        </button>

        <button
          onClick={() => handleAction(false)}
          disabled={loading}
          style={{
            padding: '12px 24px',
            backgroundColor: 'rgba(255, 42, 42, 0.05)',
            color: 'var(--accent-red)',
            border: '1px solid var(--border-red)',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1,
            fontFamily: 'var(--font-mono)',
            letterSpacing: '0.05em',
          }}
          onMouseOver={(e) => { if(!loading) e.currentTarget.style.backgroundColor = 'rgba(255, 42, 42, 0.15)'; }}
          onMouseOut={(e) => { if(!loading) e.currentTarget.style.backgroundColor = 'rgba(255, 42, 42, 0.05)'; }}
        >
          [ REJECT ]
        </button>
      </div>
    </div>
  );
}
