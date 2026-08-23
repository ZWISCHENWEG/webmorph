import { getCollectors, getIncidents } from "@/lib/api";
import { SystemCore } from "@/components/dashboard/SystemCore";
import { CollectorNetwork } from "@/components/dashboard/CollectorNetwork";
import { IncidentCenter } from "@/components/dashboard/IncidentCenter";
import { PerformanceMetrics } from "@/components/dashboard/PerformanceMetrics";


export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const [collectorsRes, incidentsRes] = await Promise.all([
    getCollectors(),
    getIncidents(),
  ]);

  const collectors = Array.isArray(collectorsRes?.data) ? collectorsRes.data : [];
  const incidents = Array.isArray(incidentsRes?.data) ? incidentsRes.data : [];

  const healthyCollectors = collectors.filter((c) => c.state === "HEALTHY").length;
  const totalCollectors = collectors.length;
  const healthScore = totalCollectors > 0 ? Math.round((healthyCollectors / totalCollectors) * 100) : 100;
  
  const activeIncidents = incidents.filter((i) => i.status !== "RECOVERED");
  const activeIncidentCount = activeIncidents.length;
  const repairsCompleted = incidents.filter((i) => i.status === "RECOVERED").length;

  return (
    <>
      {/* Dashboard Grid */}
      <div className="w-full flex-1 grid gap-6 items-start grid-cols-1 lg:grid-cols-2 xl:grid-cols-[320px_minmax(500px,1fr)_360px]">
        
        {/* LEFT PANEL */}
        <div className="flex flex-col gap-6">
          <CollectorNetwork collectors={collectors} />
          <PerformanceMetrics />
        </div>
        
        {/* CENTER PANEL */}
        <div className="flex flex-col gap-6 h-full">
          <SystemCore 
            health={healthScore} 
            activeCollectors={totalCollectors} 
            incidents={activeIncidentCount} 
            repairs={repairsCompleted}
          />
        </div>

        {/* RIGHT PANEL */}
        <div className="flex flex-col gap-6 h-full">
          <IncidentCenter incidents={incidents} />
        </div>

      </div>
    </>
  );
}
