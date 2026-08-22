"use client";

import React, { useEffect, useState } from 'react';
import { getIncident } from '../../lib/api';
import { IncidentDetail } from '../../types';
import { DiagnosisPanel } from './DiagnosisPanel';
import { HealingProposal } from './HealingProposal';
import { ApprovalActions } from './ApprovalActions';
import { JobProgress } from './JobProgress';
import { HealthBadge } from '../HealthBadge';

export function IncidentView({ incidentId }: { incidentId: number }) {
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  const fetchIncident = async () => {
    try {
      setError(null);
      const data = await getIncident(incidentId);
      setIncident(data);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to load incident');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchIncident();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [incidentId]);

  if (loading && !incident) {
    return (
      <div style={{ color: 'var(--text-secondary)', padding: '48px', textAlign: 'center', fontFamily: 'var(--font-mono)' }}>
        LOADING INCIDENT DATA...
      </div>
    );
  }

  if (error || !incident) {
    return (
      <div style={{ color: 'var(--accent-magenta)', padding: '24px', border: '1px solid rgba(255,0,85,0.2)', backgroundColor: 'rgba(255,0,85,0.05)', borderRadius: '4px' }}>
        <strong>SYSTEM ERROR:</strong> {error || 'Incident not found'}
        <div style={{ marginTop: '16px' }}>
          <button onClick={fetchIncident} style={{ color: 'var(--text-primary)', textDecoration: 'underline' }}>RETRY</button>
        </div>
      </div>
    );
  }

  const activeHealingEvent = incident.healing_events.length > 0 
    ? incident.healing_events[incident.healing_events.length - 1] 
    : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Meta Section */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '24px' }}>
        <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>COLLECTOR TARGET</div>
          <div style={{ fontSize: '1.25rem', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>{incident.collector_id}</div>
        </div>
        
        <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>TRIGGER RUN</div>
          <div style={{ fontSize: '1.25rem', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>{incident.trigger_run_id}</div>
        </div>
        
        <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>CURRENT STATUS</div>
          <div><HealthBadge state={incident.status} score={null} /></div>
        </div>
        
        <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>TIMESTAMP</div>
          <div style={{ fontSize: '0.875rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
            {new Date(incident.created_at).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Diagnosis Section */}
      <DiagnosisPanel diagnosis={incident.diagnosis} status={incident.status} />

      {/* Active Job Progress (if any) */}
      {activeJobId && (
        <JobProgress 
          jobId={activeJobId} 
          onComplete={() => {
            setActiveJobId(null);
            fetchIncident();
          }} 
        />
      )}

      {/* Healing Proposal & Actions */}
      {activeHealingEvent && (
        <HealingProposal 
          event={activeHealingEvent} 
          incidentStatus={incident.status}
        />
      )}
      
      {incident.status === 'AWAITING_APPROVAL' && !activeJobId && (
        <ApprovalActions 
          incidentId={incidentId} 
          onActionSubmitted={(jobId) => {
            if (jobId) {
              setActiveJobId(jobId);
            } else {
              fetchIncident(); // Refreshes if rejected without job
            }
          }} 
        />
      )}

      {incident.status === 'MANUAL_INTERVENTION' && (
        <div style={{ padding: '24px', border: '1px solid rgba(255,170,0,0.3)', backgroundColor: 'rgba(255,170,0,0.05)', borderRadius: '4px' }}>
          <h3 style={{ color: 'var(--accent-amber)', marginBottom: '8px' }}>⚠️ MANUAL INTERVENTION REQUIRED</h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            The automated recovery pipeline has halted. This incident requires manual engineering review.
            The schema or target site changes cannot be safely healed automatically.
          </p>
        </div>
      )}

    </div>
  );
}
