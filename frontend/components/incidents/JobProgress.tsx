import React, { useEffect, useState } from 'react';
import { getJobStatus } from '../../lib/api';
import { Job } from '../../types';

export function JobProgress({ jobId, onComplete }: { jobId: string, onComplete: () => void }) {
  const [jobState, setJobState] = useState<Job['status'] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    let isSubscribed = true;

    const poll = async () => {
      try {
        const job = await getJobStatus(jobId);
        if (isSubscribed) {
          setJobState(job.status);
          if (['SUCCEEDED', 'FAILED', 'TIMED_OUT', 'CANCELLED'].includes(job.status)) {
            setTimeout(() => {
              if (isSubscribed) onComplete();
            }, 1000);
          }
        }
      } catch (err: unknown) {
        if (isSubscribed) {
          setError((err as Error).message || 'Error polling job');
          setTimeout(() => {
            if (isSubscribed) onComplete();
          }, 3000);
        }
      }
    };

    poll();
    const interval = setInterval(() => {
      if (!['SUCCEEDED', 'FAILED', 'TIMED_OUT', 'CANCELLED'].includes(jobState || '')) {
        poll();
      }
    }, 2000);

    return () => {
      isSubscribed = false;
      clearInterval(interval);
    };
  }, [jobId, jobState, onComplete]);

  return (
    <div className="angular-panel glass-panel" style={{ padding: '24px', borderLeft: '4px solid var(--accent-cyan)' }}>
      <div className="flex-row" style={{ justifyContent: 'space-between' }}>
        <h3 className="section-header" style={{ color: 'var(--accent-cyan)' }}>Executing Repair Pipeline</h3>
        <span style={{ fontSize: '0.875rem', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', padding: '4px 8px', backgroundColor: 'var(--bg-panel-secondary)', border: '1px solid var(--border-tech)' }}>
          {jobState || 'QUEUED'}
        </span>
      </div>
      
      {error && (
        <div className="chromatic-error" style={{ marginTop: '16px', fontSize: '0.75rem', color: 'var(--accent-red)', fontFamily: 'var(--font-mono)' }}>
          {error}
        </div>
      )}
      
      <div style={{ marginTop: '24px', height: '2px', backgroundColor: 'var(--border-tech)', overflow: 'hidden', position: 'relative' }}>
        <div style={{ 
          height: '100%', 
          backgroundColor: 'var(--accent-cyan)',
          width: jobState === 'SUCCEEDED' ? '100%' : '50%',
          transition: 'width var(--transition-medium)',
          animation: jobState === 'RUNNING' ? 'pulse 2s infinite' : 'none',
          boxShadow: 'var(--shadow-cyan)'
        }} />
      </div>
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes pulse {
          0% { opacity: 0.6; width: 30%; }
          50% { opacity: 1; width: 70%; }
          100% { opacity: 0.6; width: 30%; }
        }
      `}} />
    </div>
  );
}
