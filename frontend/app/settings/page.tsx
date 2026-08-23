"use client";

import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/card";
import { Settings2, Key, Bell, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  return (
    <>
      <PageHeader 
        title="Settings" 
        description="Configure WebMorph parameters and integrations." 
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Sidebar Nav */}
        <div className="lg:col-span-1 flex flex-col gap-2">
          <button className="w-full flex items-center gap-3 px-4 py-3 text-[13px] font-bold bg-white border border-[#E5E7EB] text-[#111827] rounded-xl shadow-sm">
            <Settings2 className="w-4 h-4 text-[#111827]" />
            General
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-3 text-[13px] font-bold text-[#64748B] hover:bg-white hover:text-[#111827] rounded-xl transition-colors">
            <Key className="w-4 h-4" />
            API Configuration
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-3 text-[13px] font-bold text-[#64748B] hover:bg-white hover:text-[#111827] rounded-xl transition-colors">
            <Bell className="w-4 h-4" />
            Notifications
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-3 text-[13px] font-bold text-[#64748B] hover:bg-white hover:text-[#111827] rounded-xl transition-colors">
            <Shield className="w-4 h-4" />
            Security
          </button>
        </div>

        {/* Content Area */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <Card>
            <h2 className="text-[14px] font-bold text-[#111827] mb-6 border-b border-[#E5E7EB] pb-4">General Configuration</h2>
            
            <div className="flex flex-col gap-6">
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-widest text-[#64748B] mb-2">Organization Name</label>
                <input 
                  type="text" 
                  defaultValue="Acme Corp" 
                  className="w-full max-w-md px-4 py-2.5 text-[14px] border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#111827] focus:border-transparent shadow-sm"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-widest text-[#64748B] mb-2">Alert Webhook URL</label>
                <input 
                  type="text" 
                  placeholder="https://hooks.slack.com/services/..." 
                  className="w-full max-w-md px-4 py-2.5 text-[14px] border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#111827] focus:border-transparent shadow-sm"
                />
                <p className="text-[12px] text-[#64748B] mt-2">We will send immediate notifications when AI detects a drift.</p>
              </div>

              <div className="pt-4 border-t border-[#E5E7EB]">
                <Button variant="default" className="w-fit">
                  Save Changes
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </>
  );
}
