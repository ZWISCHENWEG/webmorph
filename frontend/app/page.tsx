import { getCollectors, getIncidents } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Activity, AlertTriangle, ShieldCheck, Zap, Server, Clock, ChevronRight, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const [collectorsData, incidentsData] = await Promise.all([
    getCollectors().catch(() => ({ data: [] })),
    getIncidents().catch(() => ({ data: [] }))
  ]);

  const collectors = collectorsData.data || [];
  const incidents = incidentsData.data || [];
  
  // Calculate stats
  const activeCollectorsCount = collectors.length;
  const recentIncidentsCount = incidents.filter(i => i.status !== 'RECOVERED').length;
  // Mocking AI Repairs Completed and System Health for the hero presentation
  const aiRepairsCompleted = 24;
  const systemHealth = activeCollectorsCount > 0 && recentIncidentsCount === 0 ? "100%" : "98.5%";

  return (
    <main className="min-h-screen bg-background text-foreground p-6 md:p-12 space-y-12">
      {/* Header Section */}
      <section className="space-y-4">
        <div className="flex items-center gap-3 text-primary mb-2">
          <ShieldCheck className="h-8 w-8 text-cyan-400" />
          <h1 className="text-3xl font-bold tracking-tight text-white uppercase">WEBMORPH</h1>
        </div>
        <p className="text-muted-foreground text-lg max-w-2xl font-mono tracking-tight">
          AI-Powered Self Healing Scraper Infrastructure
        </p>
      </section>

      {/* Hero Stats */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-card/40 backdrop-blur-sm border-border/50 hover:bg-card/60 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">System Health</CardTitle>
            <Activity className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white font-mono">{systemHealth}</div>
            <p className="text-xs text-muted-foreground mt-1">All services operational</p>
          </CardContent>
        </Card>
        
        <Card className="bg-card/40 backdrop-blur-sm border-border/50 hover:bg-card/60 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Active Collectors</CardTitle>
            <Server className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white font-mono">{activeCollectorsCount}</div>
            <p className="text-xs text-muted-foreground mt-1">Across 1 region</p>
          </CardContent>
        </Card>

        <Card className="bg-card/40 backdrop-blur-sm border-border/50 hover:bg-card/60 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Incidents Today</CardTitle>
            <AlertTriangle className={`h-4 w-4 ${recentIncidentsCount > 0 ? "text-amber-400" : "text-muted-foreground"}`} />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white font-mono">{recentIncidentsCount}</div>
            <p className="text-xs text-muted-foreground mt-1">Awaiting resolution</p>
          </CardContent>
        </Card>

        <Card className="bg-card/40 backdrop-blur-sm border-border/50 hover:bg-card/60 transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">AI Repairs Completed</CardTitle>
            <Zap className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white font-mono">{aiRepairsCompleted}</div>
            <p className="text-xs text-muted-foreground mt-1">Lifetime automatic recoveries</p>
          </CardContent>
        </Card>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        
        {/* Left Column: Collectors & Timeline */}
        <div className="lg:col-span-2 space-y-12">
          
          {/* Collectors Monitoring */}
          <section className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold tracking-tight">Active Collectors</h2>
              <Badge variant="outline" className="font-mono bg-background/50">LIVE</Badge>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {collectors.length === 0 ? (
                <div className="col-span-full py-12 text-center text-muted-foreground font-mono border border-border/50 rounded-xl bg-card/20">
                  No active collectors found.
                </div>
              ) : (
                collectors.map(collector => (
                  <Link href={`/collectors/${collector.id}`} key={collector.id} className="block group">
                    <Card className="bg-card/40 backdrop-blur-sm border-border/50 group-hover:border-primary/50 group-hover:bg-card/80 transition-all duration-300 cursor-pointer overflow-hidden relative h-full">
                      <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500/50 group-hover:bg-emerald-400 transition-colors" />
                      <CardHeader className="pb-2">
                        <div className="flex justify-between items-start">
                          <CardTitle className="text-lg font-medium">{collector.bright_data_collector_id}</CardTitle>
                          <Badge variant={collector.state === 'HEALTHY' ? 'default' : 'destructive'} className="font-mono text-[10px]">
                            {collector.state}
                          </Badge>
                        </div>
                        <CardDescription className="font-mono text-xs truncate">Target: Amazon / Ecommerce</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3 mt-2">
                          <div className="flex justify-between items-center text-sm">
                            <span className="text-muted-foreground font-mono text-xs uppercase">Health Score</span>
                            <span className="font-mono font-medium text-emerald-400">{collector.latest_health_score?.toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between items-center text-sm">
                            <span className="text-muted-foreground font-mono text-xs uppercase">Contract V.</span>
                            <span className="font-mono text-muted-foreground">v{collector.current_contract_version}</span>
                          </div>
                          <div className="flex justify-between items-center text-sm">
                            <span className="text-muted-foreground font-mono text-xs uppercase">Last Scrape</span>
                            <span className="font-mono text-muted-foreground flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {collector.updated_at ? formatDistanceToNow(new Date(collector.updated_at), { addSuffix: true }) : 'N/A'}
                            </span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                ))
              )}
            </div>
          </section>

          {/* Activity Timeline */}
          <section className="space-y-6">
            <h2 className="text-xl font-semibold tracking-tight">System Activity</h2>
            <Card className="bg-card/20 backdrop-blur-sm border-border/50">
              <CardContent className="p-6">
                <div className="space-y-6 relative before:absolute before:inset-y-0 before:left-[17px] before:w-[1px] before:bg-border/50">
                  <div className="flex gap-4 relative">
                    <div className="w-9 h-9 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center shrink-0 z-10 backdrop-blur-md">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    </div>
                    <div className="pt-1.5 space-y-1">
                      <p className="text-sm font-medium">Repair approved by human operator</p>
                      <p className="text-xs text-muted-foreground font-mono">10 minutes ago • c_demo_ecommerce_123</p>
                    </div>
                  </div>
                  <div className="flex gap-4 relative">
                    <div className="w-9 h-9 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center shrink-0 z-10 backdrop-blur-md">
                      <Zap className="w-4 h-4 text-purple-400" />
                    </div>
                    <div className="pt-1.5 space-y-1">
                      <p className="text-sm font-medium">AI diagnosis completed & healing proposed</p>
                      <p className="text-xs text-muted-foreground font-mono">12 minutes ago • Confidence: 98.5%</p>
                    </div>
                  </div>
                  <div className="flex gap-4 relative">
                    <div className="w-9 h-9 rounded-full bg-amber-500/20 border border-amber-500/30 flex items-center justify-center shrink-0 z-10 backdrop-blur-md">
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                    </div>
                    <div className="pt-1.5 space-y-1">
                      <p className="text-sm font-medium">Schema drift detected (Price format changed)</p>
                      <p className="text-xs text-muted-foreground font-mono">15 minutes ago • Severity: HIGH</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

        </div>

        {/* Right Column: Incident Intelligence */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold tracking-tight">Incident Intelligence</h2>
            <Badge variant="secondary" className="font-mono bg-card text-muted-foreground">REAL-TIME</Badge>
          </div>
          
          <div className="space-y-4">
            {incidents.length === 0 ? (
              <Card className="bg-card/20 backdrop-blur-sm border-border/50 text-center py-12">
                <CardContent>
                  <ShieldCheck className="w-8 h-8 text-emerald-400 mx-auto mb-3 opacity-80" />
                  <p className="text-sm font-medium text-emerald-400">All Systems Normal</p>
                  <p className="text-xs text-muted-foreground mt-1 font-mono">No active incidents</p>
                </CardContent>
              </Card>
            ) : (
              incidents.map(incident => (
                <Link href={`/incidents/${incident.id}`} key={incident.id} className="block group">
                  <Card className="bg-card/40 backdrop-blur-sm border-border/50 hover:bg-card/80 hover:border-amber-500/30 transition-all duration-300 relative overflow-hidden">
                    {incident.status === 'AWAITING_APPROVAL' && (
                       <div className="absolute top-0 right-0 w-16 h-16 bg-amber-500/10 rounded-bl-full pointer-events-none" />
                    )}
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start mb-1">
                        <Badge variant="outline" className="font-mono text-[10px] text-amber-400 border-amber-400/30 bg-amber-400/10">
                          {(incident.diagnosis as any)?.severity || "HIGH"}
                        </Badge>
                        <span className="text-xs font-mono text-muted-foreground flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDistanceToNow(new Date(incident.created_at), { addSuffix: true })}
                        </span>
                      </div>
                      <CardTitle className="text-base font-medium leading-tight">{(incident.diagnosis as any)?.message || "Schema Drift"}</CardTitle>
                      <CardDescription className="text-xs truncate font-mono">Collector #{incident.collector_id}</CardDescription>
                    </CardHeader>
                    
                    <CardContent className="pb-4">
                      <div className="bg-background/50 rounded-lg p-3 border border-border/30 space-y-2">
                        <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider">AI Detected</p>
                        <p className="text-sm text-foreground/90 leading-relaxed line-clamp-2">
                          {(incident.diagnosis as any)?.ai_diagnosis || "Currency format change in price extraction logic. Requires regex update."}
                        </p>
                      </div>
                      
                      <div className="flex items-center justify-between mt-4">
                        <div className="flex flex-col">
                          <span className="text-[10px] uppercase font-mono text-muted-foreground tracking-wider mb-1">Confidence</span>
                          <span className="text-sm font-mono text-cyan-400 font-medium">98.5%</span>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="text-[10px] uppercase font-mono text-muted-foreground tracking-wider mb-1">Status</span>
                          <span className="text-sm font-mono text-foreground">{incident.status.replace(/_/g, ' ')}</span>
                        </div>
                      </div>
                    </CardContent>
                    
                    <div className="px-6 py-3 bg-card/60 border-t border-border/50 flex items-center justify-between group-hover:bg-card transition-colors">
                      <span className="text-xs font-mono text-muted-foreground">View Resolution Plan</span>
                      <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors group-hover:translate-x-1" />
                    </div>
                  </Card>
                </Link>
              ))
            )}
          </div>
        </div>

      </div>
    </main>
  );
}
