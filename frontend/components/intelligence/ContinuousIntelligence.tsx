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
    return <div style={{ color: 'var(--text-secondary)', padding: '48px', textAlign: 'center', fontFamily: 'var(--font-mono)' }}>GATHERING INTELLIGENCE...</div>;
  }

  if (error || !collector) {
    return (
      <div style={{ color: 'var(--accent-magenta)', padding: '24px', border: '1px solid rgba(255,0,85,0.2)', backgroundColor: 'rgba(255,0,85,0.05)', borderRadius: '4px' }}>
        <strong>ERROR:</strong> {error || 'Collector not found'}
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Current State */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
        <div>
          <h2 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '8px' }}>Target: <span className="mono">{collector.bright_data_collector_id}</span></h2>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Contract v{collector.current_contract_version}</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>CURRENT HEALTH</div>
          <HealthBadge state={collector.state} score={collector.latest_health_score} />
        </div>
      </div>

      <hr style={{ border: 'none', borderTop: '1px solid var(--border-subtle)' }} />
      
      <h3 style={{ fontSize: '1.125rem', color: 'var(--text-primary)', marginTop: '8px' }}>Verified Historical Intelligence</h3>

      {snapshots.length === 0 ? (
        <div style={{ padding: '48px', textAlign: 'center', backgroundColor: 'var(--bg-card)', border: '1px dashed var(--border-subtle)', borderRadius: '4px' }}>
          <h4 style={{ color: 'var(--text-primary)', marginBottom: '8px' }}>Insufficient Verified Data</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Continuous Intelligence metrics require verified, HEALTHY snapshots. 
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
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
      
      <MetricCard title="AVERAGE HEALTH" value={avgHealth.toFixed(1)} sparkline={snapshots.map(s => s.health_score || 0)} />
      <MetricCard title="COMPLETENESS TREND" value={avgCompleteness.toFixed(1)} sparkline={snapshots.map(s => s.completeness_score || 0)} />
      <MetricCard title="SCHEMA STABILITY" value={avgStability.toFixed(1)} sparkline={snapshots.map(s => s.stability_score || 0)} />
      
      <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '16px', fontFamily: 'var(--font-mono)' }}>VERIFIED PAYLOAD SCHEMA</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {domainKeys.length > 0 ? domainKeys.map(k => (
            <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
              <span style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{k}</span>
              <span style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>{typeof payload[k]}</span>
            </div>
          )) : (
            <span style={{ color: 'var(--text-muted)' }}>No top-level keys detected</span>
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
    <div style={{ padding: '24px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px' }}>
      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px', fontFamily: 'var(--font-mono)' }}>{title}</div>
      <div style={{ fontSize: '2rem', fontWeight: 600, fontFamily: 'var(--font-mono)', marginBottom: '16px' }}>{value}</div>
      
      <div style={{ height: '40px', width: '100%' }}>
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
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
