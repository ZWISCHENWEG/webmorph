"use client";

import { useState } from "react";
import { Bell, Loader2 } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Image from "next/image";
import { Button } from "@/components/ui/button";

import { useDemo } from "@/components/demo/DemoContext";

export function TopNav() {
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  const pathname = usePathname();
  const demo = useDemo();

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-[#E5E7EB]">
      <div className="w-full h-[72px] px-8 grid grid-cols-[1fr_auto_1fr] items-center">
        
        {/* LEFT: Logo & Brand */}
        <div className="flex items-center gap-6 justify-start">
          <Link href="/" className="flex items-center gap-4">
            <Image src="/logo.svg" alt="WebMorph Logo" width={40} height={40} className="w-10 h-10 object-contain" />
            <div className="flex flex-col justify-center">
              <span className="font-[700] text-[20px] text-[#111827] leading-tight tracking-tight">WebMorph</span>
              <span className="text-[11px] font-[700] text-[#64748B] tracking-[1.2px] leading-tight uppercase mt-0.5">Autonomous AI Infrastructure</span>
            </div>
          </Link>
        </div>

        {/* CENTER: Navigation */}
        <nav className="hidden xl:flex items-center gap-8 h-full justify-center">
          {[
            { name: 'Overview', path: '/' },
            { name: 'Collectors', path: '/collectors' },
            { name: 'Incidents', path: '/incidents' },
            { name: 'Analytics', path: '/analytics' },
            { name: 'Settings', path: '/settings' }
          ].map((item) => {
            const isActive = pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path));
            return (
              <Link 
                key={item.name} 
                href={item.path}
                className={`text-[13px] font-[600] transition-colors relative flex items-center h-[72px] ${
                  isActive 
                    ? 'text-[#111827]' 
                    : 'text-[#64748B] hover:text-[#111827]'
                }`}
              >
                {item.name}
                {isActive && (
                  <div className="absolute bottom-0 left-0 w-full h-[3px] bg-[#E11D48] rounded-t-full" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* RIGHT: Actions */}
        <div className="flex items-center gap-6 justify-end">
          <div className="hidden lg:flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-[8px] bg-[#F8FAFC] border border-[#E5E7EB]">
              <div className="w-[8px] h-[8px] rounded-full bg-[#16A34A]" />
              <span className="text-[11px] font-[700] text-[#111827] tracking-widest uppercase">Spider Sense Active</span>
            </div>
            
            <Button 
              onClick={() => {
                alert("clicked");
                sessionStorage.setItem("demoMode", "true");
                window.location.href = '/';
              }}
              className="px-5 font-[600] tracking-widest uppercase text-[12px] h-[40px] rounded-[10px]"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
                <polygon points="5 3 19 12 5 21 5 3" fill="currentColor"/>
              </svg>
              Run Demo
            </Button>
          </div>
          
          <div className="hidden lg:block h-[32px] w-[1px] bg-[#E5E7EB]" />
          
          <button className="text-[#64748B] hover:text-[#111827] transition-colors relative p-2 rounded-lg hover:bg-[#F8FAFC]">
            <Bell className="w-[20px] h-[20px] stroke-[1.5]" />
            <span className="absolute top-1 right-1 w-[14px] h-[14px] bg-[#E11D48] rounded-full border-2 border-white flex items-center justify-center text-[8px] font-bold text-white leading-none">3</span>
          </button>
          
          <div className="flex items-center gap-3">
            <div className="hidden xl:flex flex-col text-right">
              <span className="text-[13px] font-[600] text-[#111827] leading-tight">Operator</span>
              <span className="text-[10px] font-[700] text-[#64748B] tracking-widest leading-tight uppercase mt-0.5">Admin</span>
            </div>
            <div className="w-[40px] h-[40px] rounded-full bg-[#0F172A] text-white flex items-center justify-center font-bold text-[14px] shadow-sm">
              A
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
