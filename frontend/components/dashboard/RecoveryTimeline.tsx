import { AlertTriangle, Bot, Code2, User, ShieldCheck } from "lucide-react";
import { IncidentSummary } from "@/types";

const STAGES = [
  { id: 'detect', label: 'Detection', icon: AlertTriangle },
  { id: 'diagnose', label: 'Diagnosis', icon: Bot },
  { id: 'repair', label: 'Repair Gen', icon: Code2 },
  { id: 'approve', label: 'Approval', icon: User },
  { id: 'recover', label: 'Recovery', icon: ShieldCheck }
];

export function RecoveryTimeline({ incident }: { incident: IncidentSummary | null }) {
  if (!incident) {
    return (
      <div className="opacity-50 w-full h-full flex flex-col justify-center">
         <div className="flex items-center justify-between mb-4">
            <h4 className="text-[10px] font-bold text-gray-900 uppercase tracking-widest">AI Recovery Pipeline</h4>
         </div>
         <div className="flex items-center justify-center text-xs font-mono text-gray-500 h-16">No active pipeline.</div>
      </div>
    );
  }

  // Determine current stage based on incident status
  const status = incident.status;
  let currentStageIndex = 0;
  
  if (status === 'DRIFT_DETECTED') currentStageIndex = 0;
  if (status === 'DIAGNOSING') currentStageIndex = 1;
  if (status === 'HEAL_PROPOSED') currentStageIndex = 2;
  if (status === 'AWAITING_APPROVAL') currentStageIndex = 3;
  if (['APPROVED', 'HEALING', 'VERIFYING'].includes(status)) currentStageIndex = 4;
  if (['RECOVERED', 'REJECTED', 'MANUAL_INTERVENTION'].includes(status)) currentStageIndex = 5;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-6">
        <h4 className="text-[10px] font-bold text-gray-900 uppercase tracking-widest">AI Recovery Pipeline</h4>
        <span className="text-[9px] font-mono text-gray-500 uppercase">Target: INC-{incident.id}</span>
      </div>
      
      <div className="relative flex justify-between items-start w-full px-2">
        {/* Connecting Line */}
        <div className="absolute top-4 left-8 right-8 h-px bg-gray-200 z-0" />
        <div 
          className="absolute top-4 left-8 h-px bg-[#E11D48] z-0 transition-all duration-1000" 
          style={{ width: `calc(${Math.min(currentStageIndex, 4) * 25}% - 2rem)` }} 
        />

        {STAGES.map((stage, index) => {
          const isCompleted = index < currentStageIndex;
          const isCurrent = index === currentStageIndex;
          
          return (
            <div key={stage.id} className="relative z-10 flex flex-col items-center w-20">
              <div className={`w-8 h-8 rounded flex items-center justify-center border-[1.5px] mb-2 bg-white transition-colors duration-500 ${
                isCompleted ? 'border-[#E11D48] text-[#E11D48]' :
                isCurrent ? 'border-[#E11D48] text-[#E11D48]' :
                'border-[#E5E7EB] text-[#6B7280]'
              }`}>
                <IconWrapper icon={stage.icon} className="w-4 h-4" />
              </div>
              <span className={`text-[9px] font-bold uppercase tracking-wider text-center leading-tight mb-1 ${isCurrent || isCompleted ? 'text-[#111827]' : 'text-[#6B7280]'}`}>{stage.label}</span>
              <span className={`text-[9px] font-mono font-bold ${isCompleted ? 'text-[#16A34A]' : isCurrent ? 'text-[#E11D48]' : 'text-gray-300'}`}>
                {isCompleted ? 'DONE' : isCurrent ? 'ACTIVE' : 'WAIT'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function IconWrapper({ icon: Icon, className }: { icon: any, className?: string }) {
  return <Icon className={className} />;
}
