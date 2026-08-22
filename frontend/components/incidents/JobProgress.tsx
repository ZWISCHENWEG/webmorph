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
    <div style={{ padding: '24px', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--accent-cyan)', borderRadius: '4px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: '1rem', color: 'var(--accent-cyan)' }}>EXECUTING REPAIR...</h3>
        <span style={{ fontSize: '0.875rem', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
          {jobState || 'QUEUED'}
        </span>
      </div>
      
      {error && (
        <div style={{ marginTop: '12px', fontSize: '0.75rem', color: 'var(--accent-magenta)' }}>
          {error}
        </div>
      )}
      
      <div style={{ marginTop: '16px', height: '4px', backgroundColor: 'var(--bg-card)', borderRadius: '2px', overflow: 'hidden' }}>
        <div style={{ 
          height: '100%', 
          backgroundColor: 'var(--accent-cyan)',
          width: jobState === 'SUCCEEDED' ? '100%' : '50%',
          transition: 'width 1s ease',
          animation: jobState === 'RUNNING' ? 'pulse 2s infinite' : 'none'
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
