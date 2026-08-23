import { getIncident } from "@/lib/api";
import { ArrowLeft, Clock, ShieldCheck, Zap, AlertTriangle, FileCode2, CheckCircle2, Bot, Server, XCircle, Activity, Code2 } from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";
import { ApprovalActions } from "./ApprovalActions";
import { VerifyActions } from "./VerifyActions";
import { HealActions } from "./HealActions";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function IncidentPage({ params }: { params: { id: string } }) {
  const incidentId = parseInt(params.id, 10);
  if (isNaN(incidentId)) return notFound();

  let incident;
  try {
    incident = await getIncident(incidentId);
  } catch (err) {
    return (
      <div className="min-h-screen bg-[#FAFAFA] p-12 flex flex-col items-center justify-center">
        <AlertTriangle className="h-12 w-12 text-[#E11D48] mb-4" />
        <h1 className="text-2xl font-bold text-gray-900">Incident Not Found</h1>
        <p className="text-gray-500 mt-2 text-sm">Could not retrieve details for incident #{incidentId}</p>
        <Link href="/" className="mt-6 px-4 py-2 bg-gray-900 text-white text-sm font-semibold rounded hover:bg-gray-800 transition-colors">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  const activeHealingEvent = incident.healing_events?.[incident.healing_events.length - 1] || null;
  const proposal = activeHealingEvent?.proposal as any;
  const diagnosis = incident.diagnosis as any;

  const isRecovered = incident.status === 'RECOVERED';
  const isRejected = activeHealingEvent?.approval_status === 'REJECTED';

  return (
    <main className="min-h-screen bg-[#FAFAFA] font-sans">
      {/* Top Navbar */}
      <header className="h-14 border-b border-gray-200 bg-white flex items-center px-6 sticky top-0 z-50 shadow-sm">
        <Link href="/" className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-gray-500 hover:text-gray-900 transition-colors group">
          <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-1 transition-transform" />
          Dashboard
        </Link>
        <div className="mx-4 h-4 w-px bg-gray-200" />
        <span className="text-[11px] font-bold uppercase tracking-widest text-gray-900">Incident Report INC-{incident.id}</span>
      </header>

      <div className="max-w-[800px] mx-auto py-12 px-6">
        
        {/* HEADER */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-widest uppercase ${isRecovered ? 'bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/20' : 'bg-[#E11D48]/10 text-[#E11D48] border border-[#E11D48]/20'}`}>
              {isRecovered ? 'RESOLVED' : diagnosis?.severity || "HIGH SEVERITY"}
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-widest uppercase bg-gray-100 text-gray-600 border border-gray-200">
              {incident.status.replace(/_/g, ' ')}
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-gray-900 mb-3">
            {diagnosis?.message || "Schema Drift Detected"}
          </h1>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1.5 font-mono"><Server className="w-4 h-4 text-gray-400" /> Collector-{incident.collector_id}</span>
            <span className="flex items-center gap-1.5 font-mono"><Clock className="w-4 h-4 text-gray-400" /> {format(new Date(incident.created_at), 'MMM d, yyyy HH:mm:ss')}</span>
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
                AI diagnostic engine detected structural mutation on the target data source. The extracted data payload no longer satisfies the baseline data contract established in run #{incident.trigger_run_id}.
              </p>
              <div className="mt-4 p-4 bg-gray-50 border border-gray-100 rounded-lg">
                <p className="text-xs font-mono text-gray-600">
                  <strong className="text-gray-900 font-sans text-sm block mb-1">Root Cause:</strong>
                  {proposal?.root_cause || "Target DOM changed structure. Target node formatting has deviated from known schema signature."}
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
  "price": "199", // FAILED: Expected Object
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
    "value": 199.00,
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
          {proposal?.proposed_fix && (
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
                  <pre><code>{proposal.proposed_fix.replace(/```javascript/g, '').replace(/```/g, '').trim()}</code></pre>
                </div>
              </div>
            </section>
          )}

          {/* SECTION 4: Human Approval */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <ShieldCheck className="w-4 h-4 text-gray-400" />
              <h2 className="text-[11px] font-bold text-gray-900 uppercase tracking-widest">4. Operator Approval</h2>
            </div>
            
            {incident.status === 'DRIFT_DETECTED' || incident.status === 'DIAGNOSING' ? (
              <HealActions incidentId={incidentId} />
            ) : incident.status === 'AWAITING_APPROVAL' ? (
              <ApprovalActions incidentId={incidentId} />
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
          {(incident.status === 'VERIFYING' || incident.status === 'HEALING' || incident.status === 'APPROVED' || isRecovered || isRejected) && (
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Activity className="w-4 h-4 text-gray-400" />
                <h2 className="text-[11px] font-bold text-gray-900 uppercase tracking-widest">5. Recovery</h2>
              </div>
              
              {incident.status === 'HEALING' || incident.status === 'APPROVED' || incident.status === 'VERIFYING' ? (
                <VerifyActions incidentId={incidentId} />
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
              ) : isRejected ? (
                <div className="p-6 bg-[#E11D48]/10 border border-[#E11D48]/20 rounded-xl flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center shadow-sm">
                    <XCircle className="w-5 h-5 text-[#E11D48]" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-[#E11D48]">Recovery Rejected</h3>
                    <p className="text-xs text-[#E11D48]/80 mt-1 font-mono">Manual intervention required by engineering team.</p>
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
