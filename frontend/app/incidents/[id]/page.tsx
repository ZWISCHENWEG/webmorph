import { getIncident } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ArrowLeft, Clock, ShieldCheck, Zap, AlertTriangle, FileCode2, CheckCircle2, Bot, Server, XCircle, Activity } from "lucide-react";
import Link from "next/link";
import { formatDistanceToNow, format } from "date-fns";
import { ApprovalActions } from "./ApprovalActions";
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
      <div className="min-h-screen bg-background p-12 flex flex-col items-center justify-center">
        <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
        <h1 className="text-2xl font-bold">Incident Not Found</h1>
        <p className="text-muted-foreground mt-2">Could not retrieve details for incident #{incidentId}</p>
        <Link href="/" className="mt-6 text-primary hover:underline">Return to Dashboard</Link>
      </div>
    );
  }

  const activeHealingEvent = incident.healing_events?.[incident.healing_events.length - 1] || null;
  const proposal = activeHealingEvent?.proposal as any;
  const diagnosis = incident.diagnosis as any;

  // Timeline derivation based on incident status
  const isDetected = true; // Always true if incident exists
  const isDiagnosed = !!proposal?.ai_diagnosis || incident.status !== 'DRIFT_DETECTED';
  const isProposed = !!activeHealingEvent;
  const isApproved = activeHealingEvent?.approval_status === 'APPROVED';
  const isRejected = activeHealingEvent?.approval_status === 'REJECTED';
  const isRecovered = incident.status === 'RECOVERED';

  return (
    <main className="min-h-screen bg-background text-foreground p-6 md:p-12">
      {/* Back Navigation */}
      <Link href="/" className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors font-mono text-sm mb-8 group">
        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
        RETURN TO DASHBOARD
      </Link>

      {/* 1. Incident Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-12 border-b border-border/50 pb-8">
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <Badge variant="outline" className="bg-amber-500/10 text-amber-400 border-amber-500/30 font-mono text-xs px-2 py-0.5">
              {diagnosis?.severity || "HIGH"} SEVERITY
            </Badge>
            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30 font-mono text-xs px-2 py-0.5">
              {incident.status.replace(/_/g, ' ')}
            </Badge>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
            {diagnosis?.message || "Schema Drift Detected"}
          </h1>
          <p className="text-muted-foreground font-mono flex items-center gap-4">
            <span className="flex items-center gap-1.5"><Server className="w-4 h-4" /> Collector #{incident.collector_id}</span>
            <span className="flex items-center gap-1.5"><Clock className="w-4 h-4" /> {format(new Date(incident.created_at), 'MMM d, yyyy HH:mm:ss')}</span>
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Timeline & Overview */}
        <div className="lg:col-span-4 space-y-8">
          {/* 2. Detection Timeline */}
          <Card className="bg-card/40 backdrop-blur-sm border-border/50">
            <CardHeader>
              <CardTitle className="text-lg">Execution Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6 relative before:absolute before:inset-y-0 before:left-[17px] before:w-[2px] before:bg-border/50">
                {/* Detected */}
                <div className="flex gap-4 relative">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 z-10 transition-colors duration-500 ${isDetected ? 'bg-amber-500/20 border border-amber-500/30 text-amber-400' : 'bg-muted border border-border text-muted-foreground'}`}>
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <div className="pt-1.5">
                    <p className={`text-sm font-medium ${isDetected ? 'text-foreground' : 'text-muted-foreground'}`}>Failure Detected</p>
                    {isDetected && <p className="text-xs text-muted-foreground font-mono mt-0.5">Schema signature mismatch</p>}
                  </div>
                </div>

                {/* AI Diagnosis */}
                <div className="flex gap-4 relative">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 z-10 transition-colors duration-500 ${isDiagnosed ? 'bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 animate-pulse' : 'bg-muted border border-border text-muted-foreground'}`}>
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="pt-1.5">
                    <p className={`text-sm font-medium ${isDiagnosed ? 'text-foreground' : 'text-muted-foreground'}`}>AI Diagnosis Complete</p>
                    {isDiagnosed && <p className="text-xs text-muted-foreground font-mono mt-0.5">Root cause isolated</p>}
                  </div>
                </div>

                {/* Fix Generated */}
                <div className="flex gap-4 relative">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 z-10 transition-colors duration-500 ${isProposed ? 'bg-purple-500/20 border border-purple-500/30 text-purple-400' : 'bg-muted border border-border text-muted-foreground'}`}>
                    <FileCode2 className="w-4 h-4" />
                  </div>
                  <div className="pt-1.5">
                    <p className={`text-sm font-medium ${isProposed ? 'text-foreground' : 'text-muted-foreground'}`}>Fix Generated</p>
                    {isProposed && <p className="text-xs text-muted-foreground font-mono mt-0.5">Proposal ready for review</p>}
                  </div>
                </div>

                {/* Approval */}
                <div className="flex gap-4 relative">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 z-10 transition-colors duration-500 ${isApproved ? 'bg-emerald-500/20 border border-emerald-500/30 text-emerald-400' : isRejected ? 'bg-destructive/20 border border-destructive/30 text-destructive' : 'bg-muted border border-border text-muted-foreground'}`}>
                    {isApproved ? <CheckCircle2 className="w-4 h-4" /> : isRejected ? <XCircle className="w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
                  </div>
                  <div className="pt-1.5">
                    <p className={`text-sm font-medium ${isApproved || isRejected ? 'text-foreground' : 'text-muted-foreground'}`}>
                      {isApproved ? 'Recovery Approved' : isRejected ? 'Recovery Rejected' : 'Awaiting Approval'}
                    </p>
                    {(isApproved || isRejected) && <p className="text-xs text-muted-foreground font-mono mt-0.5">Operator action recorded</p>}
                  </div>
                </div>

                {/* Verification */}
                <div className="flex gap-4 relative">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 z-10 transition-colors duration-500 ${isRecovered ? 'bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.3)]' : 'bg-muted border border-border text-muted-foreground'}`}>
                    <Zap className="w-4 h-4" />
                  </div>
                  <div className="pt-1.5">
                    <p className={`text-sm font-medium ${isRecovered ? 'text-foreground' : 'text-muted-foreground'}`}>Recovery Verified</p>
                    {isRecovered && <p className="text-xs text-emerald-400 font-mono mt-0.5">System healed automatically</p>}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Details & Actions */}
        <div className="lg:col-span-8 space-y-8">
          
          {/* 3. AI Analysis Panel */}
          <Card className="bg-card/40 backdrop-blur-sm border-border/50 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
            <CardHeader className="border-b border-border/30 pb-4">
              <div className="flex justify-between items-center">
                <CardTitle className="text-xl flex items-center gap-2">
                  <Bot className="w-5 h-5 text-cyan-400" /> AI Decision Record
                </CardTitle>
                {proposal?.confidence_score && (
                  <Badge variant="outline" className="bg-cyan-500/10 text-cyan-400 border-cyan-500/30 font-mono">
                    {proposal.confidence_score}% CONFIDENCE
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="pt-6 space-y-6">
              <div>
                <h3 className="text-xs font-mono text-muted-foreground uppercase tracking-wider mb-2">Evidence & Root Cause</h3>
                <p className="text-sm leading-relaxed bg-background/50 p-4 rounded-md border border-border/30 font-mono">
                  {proposal?.root_cause || "Analyzing DOM structure... Target node formatting has deviated from known schema signature."}
                </p>
              </div>
              
              {proposal?.ai_diagnosis && (
                <div>
                  <h3 className="text-xs font-mono text-muted-foreground uppercase tracking-wider mb-2">AI Diagnosis Summary</h3>
                  <p className="text-sm leading-relaxed text-foreground/90">
                    {proposal.ai_diagnosis}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 4. Recovery Proposal (Diff View) */}
          {proposal?.proposed_fix && (
            <Card className="bg-card/40 backdrop-blur-sm border-border/50">
              <CardHeader className="border-b border-border/30 pb-4">
                <CardTitle className="text-xl flex items-center gap-2">
                  <FileCode2 className="w-5 h-5 text-purple-400" /> Proposed Recovery Patch
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="rounded-md overflow-hidden border border-border/50">
                  <div className="flex bg-muted/50 text-xs font-mono border-b border-border/50">
                    <div className="flex-1 p-2 border-r border-border/50 text-center text-muted-foreground">PREVIOUS PARSER</div>
                    <div className="flex-1 p-2 text-center text-purple-400 font-medium bg-purple-500/5">AI GENERATED PARSER</div>
                  </div>
                  <div className="flex flex-col md:flex-row bg-[#0b0c10] text-sm font-mono overflow-x-auto">
                    <div className="flex-1 p-4 border-b md:border-b-0 md:border-r border-border/30 text-red-400/80">
                      <pre><code>{`// Outdated parser logic\nconst rawPrice = $('#price').text();\nreturn parseFloat(rawPrice);`}</code></pre>
                    </div>
                    <div className="flex-1 p-4 text-emerald-400/90 relative">
                      <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500/50" />
                      <pre><code>{proposal.proposed_fix.replace(/```javascript/g, '').replace(/```/g, '').trim()}</code></pre>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 5. Approval Action / Verification Result */}
          <div className="sticky bottom-6 z-50">
            {incident.status === 'AWAITING_APPROVAL' ? (
              <ApprovalActions incidentId={incidentId} />
            ) : isRecovered ? (
              <Card className="bg-emerald-500/10 border-emerald-500/30 backdrop-blur-md shadow-[0_0_30px_rgba(16,185,129,0.15)]">
                <CardContent className="p-6 flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0">
                    <ShieldCheck className="w-6 h-6 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-emerald-400">Verification Passed: Recovery Complete</h3>
                    <p className="text-sm text-emerald-400/80 font-mono mt-1">Data contract is now satisfied. Scraper has resumed normal operations.</p>
                  </div>
                </CardContent>
              </Card>
            ) : isRejected ? (
              <Card className="bg-destructive/10 border-destructive/30 backdrop-blur-md">
                <CardContent className="p-6 flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-destructive/20 flex items-center justify-center shrink-0">
                    <XCircle className="w-6 h-6 text-destructive" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-destructive">Recovery Rejected</h3>
                    <p className="text-sm text-destructive/80 font-mono mt-1">Manual intervention is now required by engineering team.</p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="bg-card/80 border-border/50 backdrop-blur-md">
                <CardContent className="p-6 flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center shrink-0 animate-pulse">
                    <Activity className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-foreground">Executing Recovery...</h3>
                    <p className="text-sm text-muted-foreground font-mono mt-1">Applying patch and verifying data contract constraints.</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

        </div>
      </div>
    </main>
  );
}
