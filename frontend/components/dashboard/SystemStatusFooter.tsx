"use client";

import { ShieldCheck, Database, Zap, Activity } from "lucide-react";

export function SystemStatusFooter() {
  return (
    <footer className="w-full mt-auto border-t border-[#E5E7EB] bg-white py-6">
      <div className="w-full max-w-[1600px] mx-auto px-8">
        <div className="flex flex-col gap-2 w-full">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[11px] font-bold text-[#111827] uppercase tracking-widest">System Status Overview</span>
          </div>
          
          <div className="flex flex-wrap gap-8 text-[11px] font-bold text-[#111827]">
            <div className="flex items-center gap-2">
              <Database className="w-3.5 h-3.5 text-[#6B7280] stroke-[1.5]" /> Database <span className="text-[#16A34A] text-[9px] uppercase tracking-wider ml-1">Operational</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-3.5 h-3.5 text-[#6B7280] stroke-[1.5]" /> API Gateway <span className="text-[#16A34A] text-[9px] uppercase tracking-wider ml-1">Operational</span>
            </div>
            <div className="flex items-center gap-2">
              <Database className="w-3.5 h-3.5 text-[#6B7280] stroke-[1.5]" /> Collectors <span className="text-[#16A34A] text-[9px] uppercase tracking-wider ml-1">Operational</span>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="w-3.5 h-3.5 text-[#6B7280] stroke-[1.5]" /> AI Engine <span className="text-[#16A34A] text-[9px] uppercase tracking-wider ml-1">Operational</span>
            </div>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5 text-[#6B7280] stroke-[1.5]" /> Recovery Engine <span className="text-[#16A34A] text-[9px] uppercase tracking-wider ml-1">Operational</span>
            </div>
          </div>
          
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-[#E5E7EB] text-[11px] text-[#6B7280]">
             <span>© 2026 WebMorph. All rights reserved.</span>
             <div className="flex items-center gap-4">
               <span>v2.0.0</span>
               <a href="#" className="hover:text-[#111827] transition-colors">Privacy</a>
               <a href="#" className="hover:text-[#111827] transition-colors">Terms</a>
             </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
