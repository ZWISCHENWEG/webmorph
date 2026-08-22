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
      <div className="halftone-bg angular-panel empty-state">
        LOADING INCIDENT DATA...
      </div>
    );
  }

  if (error || !incident) {
    return (
      <div className="angular-panel system-error">
        <strong className="chromatic-error">SYSTEM ERROR:</strong> {error || 'Incident not found'}
        <div style={{ marginTop: '16px' }}>
          <button onClick={fetchIncident} className="action-link" style={{ background: 'none', border: 'none' }}>[ RETRY ]</button>
        </div>
      </div>
    );
  }

  const activeHealingEvent = incident.healing_events.length > 0 
    ? incident.healing_events[incident.healing_events.length - 1] 
    : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      
      {/* Top Meta Section */}
      <div className="grid-stats">
        <div className="angular-panel glass-panel halftone-bg stat-card">
          <div className="stat-label">COLLECTOR TARGET</div>
          <div className="stat-value" style={{ fontSize: '1.25rem' }}>{incident.collector_id}</div>
        </div>
        
        <div className="angular-panel glass-panel stat-card" style={{ borderTop: '2px solid var(--border-cyan)' }}>
          <div className="stat-label">TRIGGER RUN</div>
          <div className="stat-value" style={{ fontSize: '1.25rem' }}>{incident.trigger_run_id}</div>
        </div>
        
        <div className="angular-panel glass-panel stat-card" style={{ borderTop: '2px solid var(--accent-red)' }}>
          <div className="stat-label">CURRENT STATUS</div>
          <div><HealthBadge state={incident.status} score={null} /></div>
        </div>
        
        <div className="angular-panel glass-panel stat-card" style={{ borderTop: '2px solid var(--border-tech)' }}>
          <div className="stat-label">TIMESTAMP</div>
          <div style={{ fontSize: '0.875rem', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
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
        <div className="angular-panel glass-panel" style={{ padding: '24px', borderLeft: '4px solid var(--accent-warning)', backgroundColor: 'rgba(255,170,0,0.05)' }}>
          <h3 className="section-header chromatic-error" style={{ color: 'var(--accent-warning)', marginBottom: '12px' }}>⚠️ MANUAL INTERVENTION REQUIRED</h3>
          <p style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', lineHeight: 1.6 }}>
            The automated recovery pipeline has halted. This incident requires manual engineering review.
            The schema or target site changes cannot be safely healed automatically.
          </p>
        </div>
      )}

    </div>
  );
}
