"use client";

import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/card";
import { Activity, Zap, CheckCircle2 } from "lucide-react";

export default function AnalyticsPage() {
  return (
    <>
      <PageHeader 
        title="Analytics" 
        description="System-wide performance and cost metrics." 
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="flex flex-col relative overflow-hidden">
          <div className="text-[14px] font-bold text-[#64748B] flex items-center gap-2 mb-4">
            <Activity className="w-4 h-4" /> Detection Accuracy
          </div>
          <div className="text-[42px] font-bold text-[#111827] font-mono leading-none tracking-tighter mb-4">
            99.2<span className="text-[20px]">%</span>
          </div>
          {/* Simple Sparkline */}
          <div className="w-full h-12 mt-auto">
             <svg viewBox="0 0 100 30" className="w-full h-full preserve-3d" preserveAspectRatio="none">
               <path d="M0 30 C 20 15, 40 25, 60 5 S 80 10, 100 0 L 100 30 Z" fill="#F1F5F9" />
               <path d="M0 30 C 20 15, 40 25, 60 5 S 80 10, 100 0" fill="none" stroke="#64748B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
             </svg>
          </div>
        </Card>

        <Card className="flex flex-col relative overflow-hidden">
          <div className="text-[14px] font-bold text-[#64748B] flex items-center gap-2 mb-4">
            <CheckCircle2 className="w-4 h-4" /> Repair Success
          </div>
          <div className="text-[42px] font-bold text-[#111827] font-mono leading-none tracking-tighter mb-4">
            96.8<span className="text-[20px]">%</span>
          </div>
          {/* Simple Sparkline */}
          <div className="w-full h-12 mt-auto">
             <svg viewBox="0 0 100 30" className="w-full h-full preserve-3d" preserveAspectRatio="none">
               <path d="M0 30 C 20 20, 40 28, 60 10 S 80 5, 100 0 L 100 30 Z" fill="#F0FDF4" />
               <path d="M0 30 C 20 20, 40 28, 60 10 S 80 5, 100 0" fill="none" stroke="#16A34A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
             </svg>
          </div>
        </Card>

        <Card className="flex flex-col relative overflow-hidden">
          <div className="text-[14px] font-bold text-[#64748B] flex items-center gap-2 mb-4">
            <Zap className="w-4 h-4" /> Response Time
          </div>
          <div className="text-[42px] font-bold text-[#111827] font-mono leading-none tracking-tighter mb-4">
            45<span className="text-[20px]">ms</span>
          </div>
          {/* Simple Sparkline */}
          <div className="w-full h-12 mt-auto">
             <svg viewBox="0 0 100 30" className="w-full h-full preserve-3d" preserveAspectRatio="none">
               <path d="M0 30 L 20 15 L 40 20 L 60 5 L 80 25 L 100 10 L 100 30 Z" fill="#FFF1F2" />
               <path d="M0 30 L 20 15 L 40 20 L 60 5 L 80 25 L 100 10" fill="none" stroke="#E11D48" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
             </svg>
          </div>
        </Card>
      </div>
    </>
  );
}
