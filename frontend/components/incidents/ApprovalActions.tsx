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
    <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--accent-amber)', borderRadius: '4px' }}>
      <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '16px' }}>Human Approval Required</h3>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', fontSize: '0.875rem' }}>
        Please review the proposed changes above. This action will apply the schema changes and trigger a verification run.
      </p>

      {error && (
        <div style={{ marginBottom: '16px', color: 'var(--accent-magenta)', fontSize: '0.875rem' }}>
          {error}
        </div>
      )}

      <div style={{ display: 'flex', gap: '16px' }}>
        <button
          onClick={() => handleAction(true)}
          disabled={loading}
          style={{
            padding: '12px 24px',
            backgroundColor: 'var(--accent-cyan)',
            color: '#000',
            border: 'none',
            borderRadius: '4px',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1,
          }}
        >
          {loading ? 'PROCESSING...' : 'APPROVE HEAL'}
        </button>

        <button
          onClick={() => handleAction(false)}
          disabled={loading}
          style={{
            padding: '12px 24px',
            backgroundColor: 'transparent',
            color: 'var(--accent-magenta)',
            border: '1px solid var(--accent-magenta)',
            borderRadius: '4px',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1,
          }}
        >
          REJECT
        </button>
      </div>
    </div>
  );
}
