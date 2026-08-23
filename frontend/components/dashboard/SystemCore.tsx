"use client";

import { ShieldCheck, Database, Zap, Activity } from "lucide-react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/button";
import { useDemo } from "@/components/demo/DemoContext";

import { useState, useEffect } from "react";

export function SystemCore({ health: propsHealth, activeCollectors, incidents: propsIncidents, repairs: propsRepairs }: { health: number, activeCollectors: number, incidents: number, repairs: number }) {
  const [demoActive, setDemoActive] = useState(false);
  
  useEffect(() => {
    if (typeof window !== "undefined" && sessionStorage.getItem("demoMode") === "true") {
      setDemoActive(true);
    }
  }, []);
  
  let health = propsHealth;
  let incidents = propsIncidents;
  let repairs = propsRepairs;

  if (demoActive) {
    health = 72;
    incidents = 1;
  }

  const isHealthy = health >= 90;
  
  return (
    <Card className="h-full relative overflow-hidden">
      <CardHeader 
        icon={<ShieldCheck className="w-4 h-4 stroke-[1.5]" />} 
        title="System Core" 
        status={
          <Button variant="outline" size="sm" className="h-7 text-[10px] font-bold uppercase tracking-widest px-2.5">
            All Systems
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="ml-1"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </Button>
        }
      />

      <CardContent className="flex flex-col items-center justify-center p-6 flex-1 min-h-0 pt-8 pb-10">
        
        {/* Central Health Circle */}
        <div className="relative w-[280px] h-[280px] rounded-full bg-white border border-[#E5E7EB] flex items-center justify-center mb-10 shrink-0 shadow-sm">
          {/* SVG Progress Ring */}
          <svg className="absolute inset-0 w-full h-full transform -rotate-90 pointer-events-none" viewBox="0 0 100 100">
             {/* Background Ring */}
             <circle cx="50" cy="50" r="46" fill="none" stroke="#F8FAFC" strokeWidth="2" strokeDasharray="2 4" />
             {/* Progress Ring */}
             <circle cx="50" cy="50" r="46" fill="none" stroke={isHealthy ? "#16A34A" : "#E11D48"} strokeWidth="1.5" strokeDasharray={`${health * 2.89} 289`} strokeLinecap="round" className="opacity-90" />
             {/* Tick markers */}
             <line x1="50" y1="0" x2="50" y2="4" stroke="#E5E7EB" strokeWidth="1" />
             <line x1="50" y1="96" x2="50" y2="100" stroke="#E5E7EB" strokeWidth="1" />
             <line x1="0" y1="50" x2="4" y2="50" stroke="#E5E7EB" strokeWidth="1" />
             <line x1="96" y1="50" x2="100" y2="50" stroke="#E5E7EB" strokeWidth="1" />
          </svg>
          
          <div className="flex flex-col items-center text-center z-10">
             <span className="text-[10px] font-bold text-[#64748B] tracking-widest uppercase mb-1">System Health</span>
             <div className="flex items-start justify-center">
                <span className="text-[72px] font-bold font-mono tracking-tighter leading-none text-[#111827]">
                  {health}
                </span>
                <span className="text-[32px] text-[#111827] font-mono leading-none mt-2">%</span>
             </div>
             
             <StatusBadge variant={isHealthy ? "success" : "error"} className="mt-4 px-3 py-1">
                <div className={`w-1.5 h-1.5 rounded-full ${isHealthy ? 'bg-[#16A34A]' : 'bg-[#E11D48]'} mr-2`} />
                {isHealthy ? "Operational" : "Degraded"}
             </StatusBadge>
          </div>
        </div>

        {/* 3 Status Cards */}
        <div className="grid grid-cols-3 gap-4 w-full mb-8 shrink-0">
           <div className="flex flex-col items-center p-4 bg-[#F8FAFC] border border-[#E5E7EB] rounded-xl">
              <Database className="w-5 h-5 text-[#64748B] stroke-[1.5] mb-2" />
              <div className="text-[9px] font-bold text-[#64748B] uppercase tracking-widest mb-1">Collectors</div>
              <div className="text-[13px] font-bold text-[#111827]">{activeCollectors} Active</div>
           </div>
           
           <div className="flex flex-col items-center p-4 bg-[#F8FAFC] border border-[#E5E7EB] rounded-xl">
              <Activity className="w-5 h-5 text-[#64748B] stroke-[1.5] mb-2" />
              <div className="text-[9px] font-bold text-[#64748B] uppercase tracking-widest mb-1">AI Engine</div>
              <div className="text-[13px] font-bold text-[#111827]">Monitoring</div>
           </div>
           
           <div className="flex flex-col items-center p-4 bg-[#F8FAFC] border border-[#E5E7EB] rounded-xl">
              <ShieldCheck className="w-5 h-5 text-[#64748B] stroke-[1.5] mb-2" />
              <div className="text-[9px] font-bold text-[#64748B] uppercase tracking-widest mb-1">Recovery</div>
              <div className="text-[13px] font-bold text-[#111827]">{repairs} Repaired</div>
           </div>
        </div>

        {/* Recovery Pipeline Block */}
        <div className="w-full bg-[#F8FAFC] border border-[#E5E7EB] rounded-xl p-5 shrink-0 mt-auto">
           <div className="w-full text-left mb-4 flex items-center justify-between">
              <span className="text-[10px] font-bold text-[#64748B] uppercase tracking-widest">Recovery Pipeline</span>
           </div>
           
           <div className="flex flex-col items-center justify-center text-center py-2 mb-5">
             <p className="text-[13px] font-bold text-[#111827] mb-1">
               {demoActive ? "Pipeline Active" : "No active pipeline"}
             </p>
             <p className="text-[12px] text-[#64748B]">
               {demoActive ? "Processing recovery operations" : "All systems operating normally"}
             </p>
           </div>
           
           <div className="flex items-center justify-between relative">
              <div className="absolute top-1/2 left-0 w-full h-px bg-[#E5E7EB] -translate-y-1/2 z-0" />
              
              {["Detection", "Diagnosis", "Repair", "Approval", "Recovery"].map((step, i) => {
                let isActiveStep = false;
                if (demoActive && i <= 1) isActiveStep = true;
                return (
                  <div key={step} className="flex flex-col items-center z-10 gap-2 bg-[#F8FAFC] px-2">
                    <div className={`w-2.5 h-2.5 rounded-full border flex items-center justify-center ${isActiveStep ? 'border-[#16A34A] bg-[#16A34A]' : 'border-[#E5E7EB] bg-white'}`}>
                      <div className={`w-1 h-1 rounded-full ${isActiveStep ? 'bg-white' : 'bg-[#E5E7EB]'}`} />
                    </div>
                    <span className={`text-[9px] font-bold uppercase tracking-wider ${isActiveStep ? 'text-[#16A34A]' : 'text-[#64748B]'}`}>{step}</span>
                  </div>
                );
              })}
           </div>
        </div>
      </CardContent>
    </Card>
  );
}
