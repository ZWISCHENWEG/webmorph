"use client";

import React, { useEffect, useState } from 'react';
import { getCollector, getCollectorSnapshots } from '../../lib/api';
import { Collector, Snapshot } from '../../types';
import { HealthBadge } from '../HealthBadge';
import { Card } from '../ui/card';
import { Activity, ShieldCheck, CheckCircle2, TrendingUp, AlertTriangle } from 'lucide-react';

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
        getCollectorSnapshots(collectorId, 0, 500)
      ]);
      setCollector(colData);
      
      const verifiedSnapshots = snapData.data.filter(s => s.validation_state === 'HEALTHY');
      verifiedSnapshots.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      
      setSnapshots(verifiedSnapshots);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to load intelligence data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [collectorId]);

  if (loading) {
    return <div className="p-8 text-center text-sm font-mono text-gray-500 animate-pulse">Gathering Intelligence...</div>;
  }

  if (error || !collector) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm flex items-center gap-2">
        <AlertTriangle className="w-4 h-4" />
        <strong>ERROR:</strong> {error || 'Collector not found'}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Current State */}
      <Card className="flex items-center justify-between p-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-1 flex items-center gap-2">
            Target: <span className="font-mono text-blue-600 bg-blue-50 px-2 py-0.5 rounded">{collector.bright_data_collector_id}</span>
          </h2>
          <div className="text-[11px] font-bold text-gray-400 uppercase tracking-widest mt-2">[ CONTRACT v{collector.current_contract_version} ]</div>
        </div>
        <div className="text-right">
          <div className="text-[10px] font-bold tracking-widest text-gray-500 uppercase mb-2">CURRENT HEALTH</div>
          <HealthBadge state={collector.state} score={collector.latest_health_score} />
        </div>
      </Card>

      <div>
        <div className="flex items-center gap-3 mb-4">
          <h3 className="text-[11px] font-bold text-gray-900 uppercase tracking-widest flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-gray-400" />
            Verified Historical Intelligence
          </h3>
          <span className="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded font-mono uppercase font-bold tracking-widest">
            Verified Data Only
          </span>
        </div>

        {snapshots.length === 0 ? (
          <div className="p-8 bg-white border border-gray-200 rounded-xl text-center shadow-sm">
            <ShieldCheck className="w-8 h-8 text-gray-300 mx-auto mb-3" />
            <h4 className="text-sm font-bold text-gray-900 mb-1">Insufficient Verified Data</h4>
            <p className="text-xs text-gray-500">
              Continuous Intelligence metrics require verified, HEALTHY snapshots. <br/>
              Currently, there are no healthy historical snapshots available for this collector.
            </p>
          </div>
        ) : (
          <IntelligenceMetrics snapshots={snapshots} />
        )}
      </div>
    </div>
  );
}

function IntelligenceMetrics({ snapshots }: { snapshots: Snapshot[] }) {
  const latest = snapshots[snapshots.length - 1];
  
  const avgHealth = snapshots.reduce((acc, s) => acc + (s.health_score || 0), 0) / snapshots.length;
  const avgCompleteness = snapshots.reduce((acc, s) => acc + (s.completeness_score || 0), 0) / snapshots.length;
  const avgStability = snapshots.reduce((acc, s) => acc + (s.stability_score || 0), 0) / snapshots.length;
  
  const payload = latest.normalized_payload || {};
  const domainKeys = Object.keys(payload).slice(0, 4);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <MetricCard title="Average Health" value={avgHealth.toFixed(1)} sparkline={snapshots.map(s => s.health_score || 0)} icon={<Activity className="w-4 h-4 text-gray-400"/>} color="blue" />
      <MetricCard title="Completeness Trend" value={avgCompleteness.toFixed(1)} sparkline={snapshots.map(s => s.completeness_score || 0)} icon={<CheckCircle2 className="w-4 h-4 text-gray-400"/>} color="emerald" />
      <MetricCard title="Schema Stability" value={avgStability.toFixed(1)} sparkline={snapshots.map(s => s.stability_score || 0)} icon={<TrendingUp className="w-4 h-4 text-gray-400"/>} color="indigo" />
      
      <Card className="md:col-span-3 p-6 flex flex-col shadow-sm border-t-2 border-t-gray-900">
        <div className="text-[11px] font-bold tracking-widest text-gray-500 uppercase mb-4 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          Verified Payload Schema
        </div>
        <div className="flex flex-col gap-3">
          {domainKeys.length > 0 ? domainKeys.map(k => (
            <div key={k} className="flex justify-between items-center text-sm pb-3 border-b border-gray-100 last:border-0 last:pb-0">
              <span className="font-mono text-gray-900 font-medium">{k}</span>
              <span className="font-mono text-[11px] text-gray-500 bg-gray-100 px-2.5 py-1 rounded-md uppercase tracking-wider">{typeof payload[k]}</span>
            </div>
          )) : (
            <span className="text-sm font-mono text-gray-400">[ NO TOP-LEVEL KEYS DETECTED ]</span>
          )}
        </div>
      </Card>
    </div>
  );
}

function MetricCard({ title, value, sparkline, icon, color }: { title: string, value: string, sparkline: number[], icon: React.ReactNode, color: string }) {
  const max = 100;
  const min = 0;
  const range = max - min;
  
  const points = sparkline.map((val, i) => {
    const x = (i / Math.max(1, sparkline.length - 1)) * 100;
    const y = 100 - (((val - min) / range) * 100);
    return `${x},${y}`;
  }).join(' ');

  const strokeColor = color === 'blue' ? '#3B82F6' : color === 'emerald' ? '#10B981' : '#6366F1';
  const fillColor = color === 'blue' ? '#EFF6FF' : color === 'emerald' ? '#ECFDF5' : '#EEF2FF';

  return (
    <Card className="flex flex-col relative overflow-hidden p-0 shadow-sm">
      <div className="p-6 pb-0 flex items-center justify-between mb-4">
        <div className="text-[13px] font-bold text-gray-500 flex items-center gap-2">
          {icon} {title}
        </div>
      </div>
      <div className="px-6 text-4xl font-bold text-gray-900 font-mono tracking-tighter mb-6">
        {value}<span className="text-lg text-gray-400 ml-1">%</span>
      </div>
      
      <div className="w-full h-16 mt-auto">
        <svg viewBox="0 0 100 40" className="w-full h-full preserve-3d" preserveAspectRatio="none">
          <path d={`M0 40 ${sparkline.length > 0 ? `L ${points}` : 'L 100 20'} L 100 40 Z`} fill={fillColor} />
          {sparkline.length > 0 && <polyline points={points} fill="none" stroke={strokeColor} strokeWidth="2" vectorEffect="non-scaling-stroke" />}
        </svg>
      </div>
    </Card>
  );
}
