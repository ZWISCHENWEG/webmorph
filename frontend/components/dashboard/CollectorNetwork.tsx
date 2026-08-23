"use client";

import { useState } from "react";
import { Collector } from "@/types";
import { Database, Loader2 } from "lucide-react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/button";

export function CollectorNetwork({ collectors }: { collectors: Collector[] }) {
  const healthy = collectors.filter((c) => c.state === 'HEALTHY').length;
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  
  return (
    <Card className="h-full">
      <CardHeader 
        icon={<Database className="w-4 h-4 stroke-[1.5]" />} 
        title="Collector Network" 
        status={
          <span className="text-[11px] font-bold text-[#111827]">{healthy}/{collectors.length} Active</span>
        }
      />
      <CardContent className="p-0 relative flex flex-col h-full min-h-0 overflow-y-auto mt-4 px-6 pb-6">
        {collectors.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full w-full relative pt-4 pb-2">
            {/* WebMorph Network Visualization */}
            <div className="relative w-48 h-48 flex items-center justify-center mb-4">
              {/* Lines */}
              <svg className="absolute inset-0 w-full h-full text-[#E5E7EB] pointer-events-none" viewBox="0 0 100 100">
                <line x1="50" y1="50" x2="20" y2="20" stroke="currentColor" strokeWidth="1" />
                <line x1="50" y1="50" x2="80" y2="30" stroke="currentColor" strokeWidth="1" />
                <line x1="50" y1="50" x2="20" y2="70" stroke="currentColor" strokeWidth="1" />
                <line x1="50" y1="50" x2="80" y2="80" stroke="currentColor" strokeWidth="1" />
                <line x1="50" y1="50" x2="50" y2="10" stroke="currentColor" strokeWidth="1" />
                <line x1="50" y1="50" x2="50" y2="90" stroke="currentColor" strokeWidth="1" />
                
                <circle cx="20" cy="20" r="3" fill="#F8FAFC" stroke="currentColor" strokeWidth="1" />
                <circle cx="80" cy="30" r="3" fill="#F8FAFC" stroke="currentColor" strokeWidth="1" />
                <circle cx="20" cy="70" r="3" fill="#F8FAFC" stroke="currentColor" strokeWidth="1" />
                <circle cx="80" cy="80" r="3" fill="#F8FAFC" stroke="currentColor" strokeWidth="1" />
                <circle cx="50" cy="10" r="3" fill="#F8FAFC" stroke="currentColor" strokeWidth="1" />
                <circle cx="50" cy="90" r="3" fill="#F8FAFC" stroke="currentColor" strokeWidth="1" />
              </svg>
              
              {/* Central Node */}
              <div className="relative z-10 w-10 h-10 bg-white border border-[#E5E7EB] shadow-sm rounded-full flex items-center justify-center">
                <img src="/logo.svg" alt="Logo" className="w-5 h-5" />
              </div>
            </div>
            
            <p className="text-[13px] font-bold text-[#111827] mb-1">No collectors connected</p>
            <p className="text-[12px] text-[#64748B] text-center mb-6">Initialize monitoring to start collecting data</p>
            
            <Button 
              className="w-full font-bold tracking-widest text-[11px] uppercase rounded-lg"
              disabled={isDemoLoading}
              onClick={() => {
                alert("clicked");
                sessionStorage.setItem("demoMode", "true");
                window.location.href = '/';
              }}
            >
              RUN DEMO
            </Button>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {collectors.slice(0, 8).map((collector) => (
              <div key={collector.id} className="flex items-center justify-between p-3 border border-[#E5E7EB] rounded-lg bg-[#F8FAFC]">
                <div className="flex items-center gap-3">
                  <div>
                    <div className="text-[12px] font-mono font-bold text-[#111827] mb-0.5">COLLECTOR-{collector.id}</div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-medium">v{collector.current_contract_version}</span>
                      <StatusBadge variant={collector.state === 'HEALTHY' ? 'success' : 'error'}>
                        {collector.state}
                      </StatusBadge>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-[11px] font-mono font-bold text-[#111827] mb-0.5">
                    {collector.bright_data_collector_id.replace('c_', '')}
                  </div>
                  <div className="text-[9px] text-[#64748B] uppercase tracking-wider font-bold">Target Config</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
      {collectors.length > 0 && (
        <div className="p-4 border-t border-[#E5E7EB] bg-[#F8FAFC] rounded-b-2xl mt-auto">
          <Button variant="ghost" className="w-full font-bold tracking-widest text-[11px] uppercase h-8 hover:bg-transparent text-[#64748B] hover:text-[#111827]">
            View All Collectors →
          </Button>
        </div>
      )}
    </Card>
  );
}
