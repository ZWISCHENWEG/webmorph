import React from 'react';
import { Diagnosis } from '../../types';

export function DiagnosisPanel({ diagnosis, status }: { diagnosis: Diagnosis | null, status: string }) {
  if (status === 'DIAGNOSING' && !diagnosis) {
    return (
      <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
        <h3 style={{ fontSize: '1rem', color: 'var(--accent-amber)', marginBottom: '16px' }}>Diagnostic Engine Active</h3>
        <p style={{ color: 'var(--text-secondary)' }}>System is currently analyzing the payload drift...</p>
      </div>
    );
  }

  if (!diagnosis) {
    return (
      <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
        <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>Diagnosis</h3>
        <p style={{ color: 'var(--text-muted)' }}>No diagnostic information available.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
      <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '16px' }}>Drift Diagnosis</h3>
      
      {diagnosis.issue && (
        <div style={{ marginBottom: '16px', padding: '16px', backgroundColor: 'rgba(255,0,85,0.05)', borderLeft: '2px solid var(--accent-magenta)' }}>
          <strong style={{ color: 'var(--accent-magenta)' }}>ISSUE DETECTED: </strong>
          <span style={{ color: 'var(--text-primary)' }}>{diagnosis.issue}</span>
        </div>
      )}

      {diagnosis.missing_fields && diagnosis.missing_fields.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <h4 style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>MISSING FIELDS</h4>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {diagnosis.missing_fields.map((field: string) => (
              <span key={field} style={{ padding: '4px 8px', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: '4px', fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                {field}
              </span>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: '24px' }}>
        <details>
          <summary style={{ cursor: 'pointer', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>View Raw Diagnostic JSON</summary>
          <pre style={{ marginTop: '12px', padding: '16px', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: '4px', overflowX: 'auto', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {JSON.stringify(diagnosis, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}
