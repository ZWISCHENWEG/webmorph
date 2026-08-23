"use client";

import { Activity } from "lucide-react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/StatusBadge";

export function PerformanceMetrics() {
  return (
    <Card className="h-full">
      <CardHeader 
        icon={<Activity className="w-4 h-4 stroke-[1.5]" />} 
        title="AI Performance" 
        status={
          <StatusBadge variant="active" className="bg-[#E11D48]/10 text-[#E11D48] border-[#E11D48]/20 border">
            <div className="w-1.5 h-1.5 rounded-full bg-[#E11D48] mr-1.5" />
            LIVE
          </StatusBadge>
        }
      />
      <CardContent className="p-0 px-6 pb-6 mt-4 flex-1 flex flex-col justify-end">
        <div className="grid grid-cols-2 gap-x-6 gap-y-5">
          <div>
            <p className="text-[10px] text-[#64748B] uppercase font-bold tracking-wider mb-1">Detection Acc</p>
            <div className="flex items-end justify-between">
              <span className="text-[20px] font-bold font-mono text-[#111827] leading-none tracking-tight">99.2<span className="text-[12px] text-[#64748B]">%</span></span>
              <svg width="48" height="16" viewBox="0 0 40 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0 14L8 10L16 12L24 6L32 8L40 2" stroke="#E11D48" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M0 14L8 10L16 12L24 6L32 8L40 2L40 16L0 16Z" fill="#E11D48" fillOpacity="0.1"/>
              </svg>
            </div>
          </div>
          
          <div>
            <p className="text-[10px] text-[#64748B] uppercase font-bold tracking-wider mb-1">Repair Success</p>
            <div className="flex items-end justify-between">
              <span className="text-[20px] font-bold font-mono text-[#111827] leading-none tracking-tight">96.8<span className="text-[12px] text-[#64748B]">%</span></span>
              <svg width="48" height="16" viewBox="0 0 40 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0 12L10 14L20 8L30 10L40 4" stroke="#E11D48" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M0 12L10 14L20 8L30 10L40 4L40 16L0 16Z" fill="#E11D48" fillOpacity="0.1"/>
              </svg>
            </div>
          </div>

          <div>
            <p className="text-[10px] text-[#64748B] uppercase font-bold tracking-wider mb-1">Avg Response</p>
            <div className="flex items-end justify-between">
              <span className="text-[20px] font-bold font-mono text-[#111827] leading-none tracking-tight">1.2<span className="text-[12px] text-[#64748B]">s</span></span>
              <svg width="48" height="16" viewBox="0 0 40 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0 8L8 10L16 6L24 12L32 4L40 8" stroke="#E11D48" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M0 8L8 10L16 6L24 12L32 4L40 8L40 16L0 16Z" fill="#E11D48" fillOpacity="0.1"/>
              </svg>
            </div>
          </div>

          <div>
            <p className="text-[10px] text-[#64748B] uppercase font-bold tracking-wider mb-1">False Positive</p>
            <div className="flex items-end justify-between">
              <span className="text-[20px] font-bold font-mono text-[#111827] leading-none tracking-tight">0.3<span className="text-[12px] text-[#64748B]">%</span></span>
              <svg width="48" height="16" viewBox="0 0 40 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0 4L10 8L20 4L30 10L40 6" stroke="#E11D48" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M0 4L10 8L20 4L30 10L40 6L40 16L0 16Z" fill="#E11D48" fillOpacity="0.1"/>
              </svg>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
