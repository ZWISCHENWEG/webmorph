"use client";

import { AlertCircle, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { IncidentSummary } from "@/types";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/button";

export function IncidentCenter({ incidents }: { incidents: IncidentSummary[] }) {
  return (
    <Card className="h-full">
      <CardHeader 
        icon={<AlertCircle className="w-4 h-4 stroke-[1.5]" />} 
        title="AI Incident Center" 
        status={
          incidents.length > 0 ? (
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[#E11D48] text-[10px] font-bold text-white leading-none">
              {incidents.length}
            </span>
          ) : (
            <StatusBadge variant="success">Ready</StatusBadge>
          )
        }
      />

      <CardContent className="p-0 relative flex flex-col h-full min-h-0 overflow-y-auto mt-4 px-6 pb-6">
        {incidents.length === 0 ? (
          <div className="flex flex-col h-full mt-4">
            <div className="flex flex-col items-center justify-center text-center mb-8">
              <div className="w-12 h-12 bg-[#F8FAFC] border border-[#E5E7EB] rounded-2xl flex items-center justify-center mb-5 shadow-sm">
                <ShieldCheck className="w-6 h-6 text-[#16A34A] stroke-[1.5]" />
              </div>
              <p className="text-[13px] font-bold text-[#111827] mb-1">SYSTEM READY</p>
              <p className="text-[12px] text-[#64748B] max-w-[240px] leading-relaxed">
                No active threats detected.<br/>
                AI monitoring engine continuously analyzing infrastructure.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-8">
               <div className="flex flex-col p-4 bg-[#F8FAFC] border border-[#E5E7EB] rounded-xl text-center">
                  <span className="text-[9px] font-bold text-[#64748B] uppercase tracking-widest mb-1">Monitored Nodes</span>
                  <span className="text-[20px] font-bold text-[#111827] font-mono leading-none">0</span>
               </div>
               <div className="flex flex-col p-4 bg-[#F8FAFC] border border-[#E5E7EB] rounded-xl text-center">
                  <span className="text-[9px] font-bold text-[#64748B] uppercase tracking-widest mb-1">Confidence Score</span>
                  <span className="text-[20px] font-bold text-[#16A34A] font-mono leading-none">100<span className="text-[12px]">%</span></span>
               </div>
            </div>

            <div className="w-full text-left mb-4 mt-auto">
               <span className="text-[10px] font-bold text-[#64748B] uppercase tracking-widest">Recent Activity</span>
            </div>
            <div className="flex flex-col gap-3">
               {[
                 { label: 'System initialized', time: '2m ago' },
                 { label: 'AI engine ready', time: '1m ago' },
                 { label: 'Monitoring infrastructure', time: 'Just now' }
               ].map((log, i) => (
                 <div key={i} className="flex items-center gap-3">
                   <div className="w-1.5 h-1.5 rounded-full bg-[#16A34A]" />
                   <div className="flex-1 text-[11px] font-bold text-[#111827]">{log.label}</div>
                   <div className="text-[10px] text-[#64748B]">{log.time}</div>
                 </div>
               ))}
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {incidents.map((incident) => {
              const diagnosisMessage = (incident.diagnosis as any)?.message || 'Schema mismatch detected on target structure.';
              const confidence = (incident.diagnosis as any)?.confidence || 98;
              
              return (
                <div key={incident.id} className="p-5 border border-[#E5E7EB] bg-[#F8FAFC] rounded-xl flex flex-col gap-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="text-[10px] font-bold text-[#E11D48] uppercase tracking-widest mb-1 flex items-center gap-1.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#E11D48]" />
                        High Severity
                      </div>
                      <div className="text-[13px] font-bold text-[#111827]">COLLECTOR-{incident.collector_id}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-[11px] font-mono font-bold text-[#111827] mb-0.5">Target Config</div>
                      <div className="text-[9px] text-[#64748B] uppercase tracking-wider font-bold">Location</div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col gap-2">
                    <div className="text-[10px] font-bold text-[#64748B] uppercase tracking-widest">AI Diagnosis</div>
                    <div className="text-[12px] text-[#111827] bg-white p-3 border border-[#E5E7EB] rounded-lg shadow-sm">
                      {diagnosisMessage}
                      <div className="mt-2 flex items-center gap-2 pt-2 border-t border-[#F1F5F9]">
                         <span className="text-[10px] font-bold text-[#16A34A] uppercase tracking-wider">{confidence}% Confidence</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 mt-1">
                    <Link 
                      href={`/incidents/${incident.id}`}
                      className="flex-1 inline-flex items-center justify-center bg-[#E11D48] text-white hover:bg-[#BE123C] shadow-sm font-bold tracking-widest text-[10px] uppercase rounded-lg h-8 px-4 transition-colors"
                    >
                      View Incident
                    </Link>
                    <Button variant="outline" className="flex-1 font-bold tracking-widest text-[10px] uppercase rounded-lg h-8 text-[#111827]">
                      Approve Repair
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
