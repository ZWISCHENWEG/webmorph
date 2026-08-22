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
    <div className="flex-row">
      <button
        onClick={handleRun}
        disabled={loading}
        className="btn-primary"
      >
        {loading ? 'RUNNING...' : 'START RUN'}
      </button>

      {jobState && (
        <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
          {jobId} • {jobState}
        </span>
      )}
      
      {error && (
        <span style={{ fontSize: '0.75rem' }} className="chromatic-error">
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
      <div className="halftone-bg angular-panel empty-state">
        INITIALIZING SENSORS...
      </div>
    );
  }

  if (error) {
    return (
      <div className="angular-panel system-error">
        <strong className="chromatic-error">SYSTEM ERROR:</strong> {error}
      </div>
    );
  }

  return (
    <div>
      <div className="grid-stats" style={{ marginBottom: '48px' }}>
        <div className="angular-panel glass-panel halftone-bg stat-card">
          <div className="stat-label color-secondary">TOTAL MONITORS</div>
          <div className="stat-value">{total}</div>
        </div>
        <div className="angular-panel glass-panel stat-card" style={{ borderTop: '2px solid var(--border-cyan)' }}>
          <div className="stat-label" style={{ color: 'var(--accent-cyan)' }}>HEALTHY</div>
          <div className="stat-value">{healthy}</div>
        </div>
        <div className="angular-panel glass-panel stat-card" style={{ borderTop: '2px solid var(--accent-warning)' }}>
          <div className="stat-label" style={{ color: 'var(--accent-warning)' }}>DEGRADED</div>
          <div className="stat-value">{degraded}</div>
        </div>
        <div className="angular-panel glass-panel stat-card" style={{ borderTop: '2px solid var(--accent-red)' }}>
          <div className="stat-label" style={{ color: 'var(--accent-red)' }}>DRIFT DETECTED</div>
          <div className={`stat-value ${drift > 0 ? "chromatic-error" : ""}`}>{drift}</div>
        </div>
      </div>

      <div className="section-header-row">
        <h2 className="section-header">Active Collectors</h2>
        <button onClick={fetchData} className="action-link" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>[ REFRESH ]</button>
      </div>

      {collectors.length === 0 ? (
        <div className="halftone-bg angular-panel empty-state" style={{ marginBottom: '48px' }}>
          No collectors registered. Configure a Data Contract to begin.
        </div>
      ) : (
        <div className="table-container angular-panel glass-panel" style={{ marginBottom: '48px' }}>
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
                    <a href={`/collectors/${collector.id}`} className="action-link">VIEW CI →</a>
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

      <div className="section-header-row">
        <h2 className="section-header">Incident Response</h2>
      </div>

      {incidents.length === 0 ? (
        <div className="halftone-bg angular-panel empty-state">
          No active incidents.
        </div>
      ) : (
        <div className="table-container angular-panel glass-panel">
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
                    <a href={`/incidents/${incident.id}`} className="action-link">VIEW DRIFT →</a>
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
