"use client";

import { PageHeader } from "@/components/ui/PageHeader";
import { EmptyState } from "@/components/ui/EmptyState";
import { Search, Filter, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function IncidentsPage() {
  return (
    <>
      <PageHeader 
        title="Incidents" 
        description="Review historical pipeline anomalies and AI repairs." 
        actions={
          <>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#F8FAFC] border border-[#E5E7EB]">
              <div className="w-2 h-2 rounded-full bg-[#16A34A]" />
              <span className="text-[11px] font-bold text-[#111827] tracking-widest uppercase">System Stable</span>
            </div>
            
            <div className="relative">
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="text" 
                placeholder="Search incidents..." 
                className="pl-9 pr-4 py-2 text-[13px] border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#111827] focus:border-transparent w-64 shadow-sm"
              />
            </div>
            
            <Button variant="outline" className="gap-2">
              <Filter className="w-4 h-4" /> Filter
            </Button>
          </>
        }
      />

      <div className="flex-1 flex items-center justify-center pt-8">
        <EmptyState 
          icon={<ShieldCheck className="w-6 h-6 text-[#16A34A]" />}
          title="Incident History"
          description={
            <>
              No active incidents.<br/>
              All infrastructure pipelines are operating normally.
            </>
          }
        />
      </div>
    </>
  );
}
