"use client";

import React, { useEffect, useState } from 'react';
import { getCollector, getCollectorSnapshots } from '../../lib/api';
import { Collector, Snapshot } from '../../types';
import { HealthBadge } from '../HealthBadge';

export function ContinuousIntelligence({ collectorId }: { collectorId: number }) {
  const [collector, setCollector] = useState<Collector | null>(null);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setError(null);
      const [colData, snapData] = await Promise.all([
        getCollector(collectorId),
        getCollectorSnapshots(collectorId, 0, 500) // fetch up to 500
      ]);
      setCollector(colData);
      
      // CRITICAL DATA FILTERING RULE:
      // ONLY consume verified/healthy snapshots for Continuous Intelligence.
      const verifiedSnapshots = snapData.data.filter(s => s.validation_state === 'HEALTHY');
      
      // Sort ascending by time for trends
      verifiedSnapshots.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      
      setSnapshots(verifiedSnapshots);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to load intelligence data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [collectorId]);

  if (loading) {
    return <div className="halftone-bg angular-panel empty-state">GATHERING INTELLIGENCE...</div>;
  }

  if (error || !collector) {
    return (
      <div className="angular-panel system-error">
        <strong className="chromatic-error">ERROR:</strong> {error || 'Collector not found'}
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      
      {/* Current State */}
      <div className="angular-panel glass-panel halftone-bg flex-row" style={{ justifyContent: 'space-between', padding: '24px' }}>
        <div>
          <h2 className="section-header" style={{ marginBottom: '8px' }}>Target: <span className="mono" style={{ color: 'var(--accent-cyan)' }}>{collector.bright_data_collector_id}</span></h2>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>[ CONTRACT v{collector.current_contract_version} ]</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="stat-label">CURRENT HEALTH</div>
          <HealthBadge state={collector.state} score={collector.latest_health_score} />
        </div>
      </div>

      <div className="flex-row">
        <h3 className="section-header" style={{ margin: 0 }}>Verified Historical Intelligence</h3>
        <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', border: '1px solid var(--border-cyan)', padding: '4px 8px', fontFamily: 'var(--font-mono)', backgroundColor: 'rgba(0, 229, 255, 0.05)' }}>VERIFIED DATA ONLY</span>
      </div>

      {snapshots.length === 0 ? (
        <div className="halftone-bg angular-panel glass-panel empty-state">
          <h4 className="section-header" style={{ marginBottom: '16px' }}>Insufficient Verified Data</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>
            Continuous Intelligence metrics require verified, HEALTHY snapshots. <br/>
            Currently, there are no healthy historical snapshots available for this collector.
          </p>
        </div>
      ) : (
        <IntelligenceMetrics snapshots={snapshots} />
      )}

    </div>
  );
}

function IntelligenceMetrics({ snapshots }: { snapshots: Snapshot[] }) {
  const latest = snapshots[snapshots.length - 1];
  
  // Averages
  const avgHealth = snapshots.reduce((acc, s) => acc + (s.health_score || 0), 0) / snapshots.length;
  const avgCompleteness = snapshots.reduce((acc, s) => acc + (s.completeness_score || 0), 0) / snapshots.length;
  const avgStability = snapshots.reduce((acc, s) => acc + (s.stability_score || 0), 0) / snapshots.length;
  
  // Domain-specific extraction from normalized payload.
  // We don't invent anything; we just safely check if the data exists in the latest payload.
  const payload = latest.normalized_payload || {};
  const domainKeys = Object.keys(payload).slice(0, 4); // Show up to 4 schema keys as an example of what is being extracted

  return (
    <div className="grid-stats">
      
      <MetricCard title="AVERAGE HEALTH" value={avgHealth.toFixed(1)} sparkline={snapshots.map(s => s.health_score || 0)} />
      <MetricCard title="COMPLETENESS TREND" value={avgCompleteness.toFixed(1)} sparkline={snapshots.map(s => s.completeness_score || 0)} />
      <MetricCard title="SCHEMA STABILITY" value={avgStability.toFixed(1)} sparkline={snapshots.map(s => s.stability_score || 0)} />
      
      <div className="angular-panel glass-panel stat-card" style={{ borderTop: '2px solid var(--border-tech)' }}>
        <div className="stat-label" style={{ marginBottom: '24px' }}>VERIFIED PAYLOAD SCHEMA</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {domainKeys.length > 0 ? domainKeys.map(k => (
            <div key={k} className="flex-row" style={{ justifyContent: 'space-between', fontSize: '0.875rem', paddingBottom: '8px', borderBottom: '1px dashed var(--border-tech)' }}>
              <span style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{k}</span>
              <span style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>{typeof payload[k]}</span>
            </div>
          )) : (
            <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>[ NO TOP-LEVEL KEYS DETECTED ]</span>
          )}
        </div>
      </div>

    </div>
  );
}

function MetricCard({ title, value, sparkline }: { title: string, value: string, sparkline: number[] }) {
  // Simple SVG sparkline
  const max = 100;
  const min = 0;
  const range = max - min;
  
  const points = sparkline.map((val, i) => {
    const x = (i / Math.max(1, sparkline.length - 1)) * 100;
    const y = 100 - (((val - min) / range) * 100);
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="angular-panel glass-panel stat-card" style={{ borderTop: '2px solid var(--border-cyan)' }}>
      <div className="stat-label" style={{ marginBottom: '12px' }}>{title}</div>
      <div className="stat-value" style={{ marginBottom: '24px' }}>{value}</div>
      
      <div style={{ height: '48px', width: '100%', position: 'relative' }}>
        <div style={{ position: 'absolute', inset: 0, opacity: 0.1, backgroundImage: 'linear-gradient(to right, transparent, var(--accent-cyan))' }} />
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ width: '100%', height: '100%', overflow: 'visible', position: 'relative', zIndex: 1 }}>
          <polyline 
            points={points} 
            fill="none" 
            stroke="var(--accent-cyan)" 
            strokeWidth="2"
            vectorEffect="non-scaling-stroke"
          />
        </svg>
      </div>
    </div>
  );
}
