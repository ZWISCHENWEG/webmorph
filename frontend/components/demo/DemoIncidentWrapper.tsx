"use client";

import { ArrowLeft, Clock, ShieldCheck, Zap, AlertTriangle, FileCode2, CheckCircle2, Bot, Server, XCircle, Activity, Code2, Loader2 } from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";
import { useState } from "react";
import { Button } from "@/components/ui/button";

export function DemoIncidentWrapper() {
  const [demoStage, setDemoStage] = useState("APPROVAL");
  
  const isRecovered = demoStage === "RECOVERED";
  const isVerifying = demoStage === "HEALING";
  const isHealing = demoStage === "HEALING";
  const isAwaitingApproval = demoStage === "APPROVAL";

  let statusText = "AWAITING APPROVAL";
  if (isHealing) statusText = "HEALING";
  if (isRecovered) statusText = "RECOVERED";

  const approveRepair = () => {
    setDemoStage("HEALING");
    setTimeout(() => {
      setDemoStage("RECOVERED");
    }, 3000);
  };

  return (
    <main className="min-h-screen bg-[#FAFAFA] font-sans">
      {/* Top Navbar */}
      <header className="h-14 border-b border-gray-200 bg-white flex items-center px-6 sticky top-0 z-50 shadow-sm">
        <Link href="/" className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-gray-500 hover:text-gray-900 transition-colors group">
          <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-1 transition-transform" />
          Dashboard
        </Link>
        <div className="mx-4 h-4 w-px bg-gray-200" />
        <span className="text-[11px] font-bold uppercase tracking-widest text-gray-900">Incident Report INC-demo</span>
      </header>

      <div className="max-w-[800px] mx-auto py-12 px-6">
        
        {/* HEADER */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-widest uppercase ${isRecovered ? 'bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/20' : 'bg-[#E11D48]/10 text-[#E11D48] border border-[#E11D48]/20'}`}>
              {isRecovered ? 'RESOLVED' : 'HIGH SEVERITY'}
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-widest uppercase bg-gray-100 text-gray-600 border border-gray-200">
              {statusText}
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-gray-900 mb-3">
            E-commerce scraper schema drift
          </h1>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1.5 font-mono"><Server className="w-4 h-4 text-gray-400" /> Collector-ecommerce-scraper-prod</span>
            <span className="flex items-center gap-1.5 font-mono"><Clock className="w-4 h-4 text-gray-400" /> {format(new Date(), 'MMM d, yyyy HH:mm:ss')}</span>
          </div>
        </div>

        <div className="space-y-12">
          
          {/* SECTION 1: Detection */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-4 h-4 text-gray-400" />
              <h2 className="text-[11px] font-bold text-gray-900 uppercase tracking-widest">1. Detection</h2>
            </div>
            <div className="p-6 bg-white border border-gray-200 rounded-xl shadow-sm">
              <p className="text-sm text-gray-700 leading-relaxed">
                AI diagnostic engine detected structural mutation on the target data source. The extracted data payload no longer satisfies the baseline data contract established in run #148.
              </p>
              <div className="mt-4 p-4 bg-gray-50 border border-gray-100 rounded-lg">
                <p className="text-xs font-mono text-gray-600">
                  <strong className="text-gray-900 font-sans text-sm block mb-1">Root Cause:</strong>
                  The target website structure changed. Product price field changed from primitive value to nested object.
                </p>
              </div>
            </div>
          </section>

          {/* SECTION 2: AI Reasoning */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Bot className="w-4 h-4 text-gray-400" />
              <h2 className="text-[11px] font-bold text-gray-900 uppercase tracking-widest">2. AI Reasoning</h2>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
              <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-gray-200">
                <div className="p-6 bg-gray-50">
                  <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                    <XCircle className="w-3.5 h-3.5 text-[#E11D48]" /> Contract Violation (Before)
                  </h3>
                  <pre className="text-xs font-mono text-gray-600">
{`{
  "product_id": "SKU-994",
  "price": "49.99", // FAILED: Expected Object
  "in_stock": true
}`}
                  </pre>
                </div>
                <div className="p-6 bg-white">
                  <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#22C55E]" /> AI Reconstruction (After)
                  </h3>
                  <pre className="text-xs font-mono text-gray-900">
{`{
  "product_id": "SKU-994",
  "price": {
    "value": 49.99,
    "currency": "USD"
  },
  "in_stock": true
}`}
                  </pre>
                </div>
              </div>
            </div>
          </section>

          {/* SECTION 3: AI Repair */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Code2 className="w-4 h-4 text-gray-400" />
              <h2 className="text-[11px] font-bold text-gray-900 uppercase tracking-widest">3. AI Repair Patch</h2>
            </div>
            <div className="bg-gray-900 rounded-xl shadow-sm overflow-hidden border border-gray-800">
              <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800 bg-black/50">
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">extract.js</span>
                  <span className="text-[10px] font-mono text-[#22C55E]">AST_DIFF_GENERATED</span>
              </div>
              <div className="p-4 text-xs font-mono text-gray-300 overflow-x-auto leading-relaxed">
                <pre><code>{`function normalizePrice(data){
  return data.price.value;
}`}</code></pre>
              </div>
            </div>
          </section>

          {/* SECTION 4: Human Approval */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <ShieldCheck className="w-4 h-4 text-gray-400" />
              <h2 className="text-[11px] font-bold text-gray-900 uppercase tracking-widest">4. Operator Approval</h2>
            </div>
            
            {isAwaitingApproval ? (
              <div className="p-6 bg-white border border-gray-200 rounded-xl shadow-sm">
                <p className="text-sm text-gray-600 mb-6">Review the AI-generated patch above. If approved, the system will apply the patch and verify data extraction.</p>
                <div className="flex items-center gap-3">
                  <Button 
                    onClick={approveRepair}
                    className="bg-[#111827] hover:bg-black text-white"
                  >
                    <CheckCircle2 className="w-4 h-4 mr-2" />
                    Approve AI Repair
                  </Button>
                  <Button variant="outline" className="text-[#E11D48] border-[#E11D48]/20 hover:bg-[#E11D48]/5">
                    <XCircle className="w-4 h-4 mr-2" />
                    Reject Patch
                  </Button>
                </div>
              </div>
            ) : (
              <div className="p-6 bg-white border border-gray-200 rounded-xl shadow-sm flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-gray-900">Patch Approved</h3>
                  <p className="text-xs text-gray-500 mt-1">Operator authorized the deployment of the AI generated patch.</p>
                </div>
                <div className="w-8 h-8 rounded-full bg-emerald-50 border border-emerald-100 flex items-center justify-center">
                  <CheckCircle2 className="w-4 h-4 text-[#22C55E]" />
                </div>
              </div>
            )}
          </section>

          {/* SECTION 5: Recovery */}
          {!isAwaitingApproval && (
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Activity className="w-4 h-4 text-gray-400" />
                <h2 className="text-[11px] font-bold text-gray-900 uppercase tracking-widest">5. Recovery</h2>
              </div>
              
              {isHealing || isVerifying ? (
                <div className="p-6 bg-white border border-gray-200 rounded-xl shadow-sm">
                  <div className="flex flex-col items-center justify-center py-6 text-center">
                    <Loader2 className="w-8 h-8 text-[#111827] animate-spin mb-4" />
                    <h3 className="text-sm font-bold text-gray-900">{isHealing ? 'Applying Patch...' : 'Verifying Data Contract...'}</h3>
                    <p className="text-xs text-gray-500 mt-1 max-w-sm">
                      {isHealing ? 'Deploying code changes to collector node.' : 'Running validation suite against production data to verify patch fixes the extraction error.'}
                    </p>
                  </div>
                </div>
              ) : isRecovered ? (
                <div className="p-6 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center shadow-sm">
                    <ShieldCheck className="w-5 h-5 text-[#22C55E]" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-emerald-900">Recovery Complete</h3>
                    <p className="text-xs text-emerald-700 mt-1 font-mono">Data contract is now satisfied. Scraper operations have resumed.</p>
                  </div>
                </div>
              ) : null}
            </section>
          )}

        </div>
      </div>
    </main>
  );
}
