"use client";

import React, { useEffect, useState } from 'react';
import { getCollectors, triggerRun, getJobStatus, getIncidents } from '../lib/api';
import { Collector, Job, IncidentSummary } from '../types';
import { HealthBadge } from './HealthBadge';

function RunAction({ collectorId }: { collectorId: number }) {
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobState, setJobState] = useState<Job['status'] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    // Poll job status
    const interval = setInterval(async () => {
      try {
        const job = await getJobStatus(jobId);
        setJobState(job.status);
        if (['SUCCEEDED', 'FAILED', 'TIMED_OUT', 'CANCELLED'].includes(job.status)) {
          clearInterval(interval);
          setLoading(false);
        }
      } catch (err: unknown) {
        setError((err as Error).message || 'Error polling job');
        clearInterval(interval);
        setLoading(false);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  const handleRun = async () => {
    try {
      setLoading(true);
      setError(null);
      setJobState(null);
      const res = await triggerRun(collectorId);
      setJobId(res.job_id);
      setJobState(res.status as Job['status']);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to trigger run');
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      <button
        onClick={handleRun}
        disabled={loading}
        style={{
          padding: '6px 12px',
          backgroundColor: loading ? 'var(--bg-secondary)' : 'var(--accent-cyan)',
          color: loading ? 'var(--text-muted)' : '#000',
          border: `1px solid ${loading ? 'var(--border-subtle)' : 'var(--accent-cyan)'}`,
          borderRadius: '4px',
          fontWeight: 600,
          fontSize: '0.875rem',
          cursor: loading ? 'not-allowed' : 'pointer',
          fontFamily: 'var(--font-sans)',
        }}
      >
        {loading ? 'RUNNING...' : 'START RUN'}
      </button>

      {jobState && (
        <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
          {jobId} • {jobState}
        </span>
      )}
      
      {error && (
        <span style={{ fontSize: '0.75rem', color: 'var(--accent-magenta)' }}>
          {error}
        </span>
      )}
    </div>
  );
}

export function CollectorDashboard() {
  const [collectors, setCollectors] = useState<Collector[]>([]);
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [colRes, incRes] = await Promise.all([
        getCollectors(),
        getIncidents()
      ]);
      setCollectors(colRes.data);
      setIncidents(incRes.data);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line
    fetchData();
  }, []);

  const total = collectors.length;
  const healthy = collectors.filter(c => c.state === 'HEALTHY').length;
  const degraded = collectors.filter(c => c.state === 'DEGRADED').length;
  const drift = collectors.filter(c => c.state === 'DRIFT_DETECTED').length;

  if (loading && collectors.length === 0) {
    return (
      <div style={{ color: 'var(--text-secondary)', padding: '48px', textAlign: 'center', fontFamily: 'var(--font-mono)' }}>
        INITIALIZING SENSORS...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ color: 'var(--accent-magenta)', padding: '24px', border: '1px solid rgba(255,0,85,0.2)', backgroundColor: 'rgba(255,0,85,0.05)', borderRadius: '4px' }}>
        <strong>SYSTEM ERROR:</strong> {error}
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '24px', marginBottom: '48px' }}>
        <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>TOTAL MONITORS</div>
          <div style={{ fontSize: '2rem', fontWeight: 600 }}>{total}</div>
        </div>
        <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid rgba(0, 240, 255, 0.2)', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>HEALTHY</div>
          <div style={{ fontSize: '2rem', fontWeight: 600, color: 'var(--text-primary)' }}>{healthy}</div>
        </div>
        <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid rgba(255, 170, 0, 0.2)', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-amber)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>DEGRADED</div>
          <div style={{ fontSize: '2rem', fontWeight: 600, color: 'var(--text-primary)' }}>{degraded}</div>
        </div>
        <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid rgba(255, 0, 85, 0.2)', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-magenta)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>DRIFT DETECTED</div>
          <div style={{ fontSize: '2rem', fontWeight: 600, color: 'var(--text-primary)' }}>{drift}</div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.25rem', color: 'var(--text-primary)' }}>Active Collectors</h2>
        <button onClick={fetchData} style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>[ REFRESH ]</button>
      </div>

      {collectors.length === 0 ? (
        <div style={{ padding: '48px', textAlign: 'center', color: 'var(--text-secondary)', border: '1px dashed var(--border-subtle)', borderRadius: '4px', marginBottom: '48px' }}>
          No collectors registered. Configure a Data Contract to begin.
        </div>
      ) : (
        <div className="table-container" style={{ marginBottom: '48px' }}>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Target Identifier</th>
                <th>State & Health</th>
                <th>Last Updated</th>
                <th>Intelligence</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {collectors.map(collector => (
                <tr key={collector.id}>
                  <td className="mono" style={{ color: 'var(--text-secondary)' }}>{collector.id}</td>
                  <td className="mono">{collector.bright_data_collector_id}</td>
                  <td>
                    <HealthBadge state={collector.state} score={collector.latest_health_score} />
                  </td>
                  <td className="mono" style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                    {new Date(collector.updated_at).toLocaleString()}
                  </td>
                  <td>
                    <a href={`/collectors/${collector.id}`} style={{ fontSize: '0.875rem', color: 'var(--accent-cyan)', textDecoration: 'none' }}>VIEW CI →</a>
                  </td>
                  <td>
                    <RunAction collectorId={collector.id} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.25rem', color: 'var(--text-primary)' }}>Incident Response</h2>
      </div>

      {incidents.length === 0 ? (
        <div style={{ padding: '48px', textAlign: 'center', color: 'var(--text-secondary)', border: '1px dashed var(--border-subtle)', borderRadius: '4px' }}>
          No active incidents.
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Incident ID</th>
                <th>Collector ID</th>
                <th>Status</th>
                <th>Timestamp</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map(incident => (
                <tr key={incident.id}>
                  <td className="mono" style={{ color: 'var(--text-secondary)' }}>{incident.id}</td>
                  <td className="mono">{incident.collector_id}</td>
                  <td>
                    <HealthBadge state={incident.status} score={null} />
                  </td>
                  <td className="mono" style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                    {new Date(incident.created_at).toLocaleString()}
                  </td>
                  <td>
                    <a href={`/incidents/${incident.id}`} style={{ fontSize: '0.875rem', color: 'var(--accent-cyan)', textDecoration: 'none' }}>VIEW DRIFT →</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
