"use client";

import { PageHeader } from "@/components/ui/PageHeader";
import { EmptyState } from "@/components/ui/EmptyState";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Database } from "lucide-react";

export default function CollectorsPage() {
  return (
    <>
      <PageHeader 
        title="Collectors" 
        description="Manage and monitor active data pipelines." 
        actions={
          <>
            <div className="relative">
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="text" 
                placeholder="Search collectors..." 
                className="pl-9 pr-4 py-2 text-[13px] border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#111827] focus:border-transparent w-64 shadow-sm"
              />
            </div>
            <Button className="px-5 font-bold tracking-wider text-[12px] h-9 rounded-lg bg-[#111827] text-white hover:bg-[#334155] shadow-sm transition-all">
              + New Collector
            </Button>
          </>
        }
      />

      <div className="flex-1 flex items-center justify-center pt-8">
        <EmptyState>
          <div className="relative w-64 h-64 mb-8 flex items-center justify-center">
             {/* Custom Network Visualization */}
             <svg width="256" height="256" viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg" className="absolute inset-0">
                {/* Connections */}
                <line x1="128" y1="128" x2="64" y2="48" stroke="#E5E7EB" strokeWidth="2" strokeDasharray="4 4" />
                <line x1="128" y1="128" x2="192" y2="48" stroke="#E5E7EB" strokeWidth="2" strokeDasharray="4 4" />
                <line x1="128" y1="128" x2="224" y2="128" stroke="#E5E7EB" strokeWidth="2" strokeDasharray="4 4" />
                <line x1="128" y1="128" x2="192" y2="208" stroke="#E5E7EB" strokeWidth="2" strokeDasharray="4 4" />
                <line x1="128" y1="128" x2="64" y2="208" stroke="#E5E7EB" strokeWidth="2" strokeDasharray="4 4" />
                <line x1="128" y1="128" x2="32" y2="128" stroke="#E5E7EB" strokeWidth="2" strokeDasharray="4 4" />

                {/* Nodes */}
                <circle cx="64" cy="48" r="6" fill="#CBD5E1" />
                <circle cx="192" cy="48" r="6" fill="#CBD5E1" />
                <circle cx="224" cy="128" r="6" fill="#CBD5E1" />
                <circle cx="192" cy="208" r="6" fill="#CBD5E1" />
                <circle cx="64" cy="208" r="6" fill="#CBD5E1" />
                
                {/* Red Center Node */}
                <circle cx="32" cy="128" r="5" fill="#E11D48" />
             </svg>

             {/* Central Hub */}
             <div className="w-20 h-20 bg-[#F8FAFC] border border-[#E5E7EB] rounded-full flex items-center justify-center z-10 shadow-sm relative">
                <Database className="w-8 h-8 text-[#64748B] stroke-[1.5]" />
             </div>
          </div>
          
          <h3 className="text-[20px] font-[700] text-[#111827] mb-3">Your monitoring network is waiting</h3>
          <p className="text-[14px] text-[#64748B] max-w-sm mx-auto mb-8 leading-relaxed">
            Connect your first collector to begin detecting infrastructure drift.
          </p>
          
          <Button className="px-6 font-bold tracking-wider uppercase text-[12px] h-10 rounded-xl bg-[#E11D48] text-white hover:bg-[#BE123C] shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
            + NEW COLLECTOR
          </Button>
        </EmptyState>
      </div>
    </>
  );
}
