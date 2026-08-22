import React from 'react';
import { Diagnosis } from '../../types';

export function DiagnosisPanel({ diagnosis, status }: { diagnosis: Diagnosis | null, status: string }) {
  if (status === 'DIAGNOSING' && !diagnosis) {
    return (
      <div className="angular-panel glass-panel halftone-bg stat-card">
        <h3 style={{ fontSize: '1rem', color: 'var(--accent-warning)', marginBottom: '16px', fontFamily: 'var(--font-mono)' }} className="chromatic-error">DIAGNOSTIC ENGINE ACTIVE</h3>
        <p style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>System is currently analyzing payload drift...</p>
      </div>
    );
  }

  if (!diagnosis) {
    return (
      <div className="angular-panel glass-panel halftone-bg stat-card">
        <h3 className="section-header" style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>Diagnosis</h3>
        <p style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>[ NO DIAGNOSTIC INFORMATION AVAILABLE ]</p>
      </div>
    );
  }

  return (
    <div className="angular-panel glass-panel halftone-bg stat-card">
      <h3 className="section-header" style={{ marginBottom: '24px' }}>Drift Diagnosis</h3>
      
      {diagnosis.issue && (
        <div className="system-error" style={{ marginBottom: '24px', padding: '16px' }}>
          <strong style={{ color: 'var(--accent-red)', fontFamily: 'var(--font-mono)' }}>ISSUE DETECTED: </strong>
          <span style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{diagnosis.issue}</span>
        </div>
      )}

      {diagnosis.missing_fields && diagnosis.missing_fields.length > 0 && (
        <div style={{ marginBottom: '24px' }}>
          <h4 style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '12px', fontFamily: 'var(--font-mono)' }}>MISSING FIELDS</h4>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {diagnosis.missing_fields.map((field: string) => (
              <span key={field} style={{ padding: '4px 8px', backgroundColor: 'var(--bg-panel-secondary)', border: '1px solid var(--border-tech)', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-primary)' }}>
                {field}
              </span>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: '24px', borderTop: '1px dashed var(--border-tech)', paddingTop: '16px' }}>
        <details>
          <summary>[ VIEW RAW FORENSICS ]</summary>
          <pre className="raw-code">
            {JSON.stringify(diagnosis, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}
