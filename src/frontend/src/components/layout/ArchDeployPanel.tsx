import { ShieldCheck, Activity } from 'lucide-react'

export default function ArchDeployPanel() {
  return (
    <div className="glass-panel p-3 h-full shrink-0 flex-1 min-w-[300px] flex flex-col gap-2 overflow-hidden">
      <h2 className="panel-header flex items-center gap-2 mb-1">
        <ShieldCheck className="w-4 h-4 text-emerald-400" />
        <span className="text-emerald-400 tracking-widest text-[10px]">SIMULATION & DEPLOYMENT</span>
      </h2>

      <div className="flex-1 overflow-y-auto pr-1">
        <p className="text-[10px] text-gray-300 leading-relaxed font-medium mb-3">
          Predictive modeling algorithms forecast exact crisis severity matrices. Logistics agents allocate constrained physical assets (ambulances, rescue boats) mathematically optimizing for max lives saved.
        </p>

        <div className="space-y-3 border-l border-[#333] pl-3 ml-2 relative">
          <div className="absolute top-0 bottom-0 left-[-1px] w-[1px] bg-gradient-to-b from-blue-500/50 to-red-500/50"></div>
          
          <div className="relative">
            <div className="absolute -left-[19px] top-1 w-2.5 h-2.5 rounded-full bg-blue-500 border-2 border-[#0a0a0a]"></div>
            <h3 className="text-[10px] font-bold text-gray-200 uppercase tracking-wider flex items-center gap-1">
              <Activity className="w-3 h-3 text-blue-400" /> Cascade Prediction
            </h3>
            <p className="text-[9px] text-gray-400 mt-0.5">
              Identifies geometric risk spread and cascading infrastructure dependencies.
            </p>
          </div>

          <div className="relative">
            <div className="absolute -left-[19px] top-1 w-2.5 h-2.5 rounded-full bg-red-500 border-2 border-[#0a0a0a]"></div>
            <h3 className="text-[10px] font-bold text-gray-200 uppercase tracking-wider">
              Asset Orchestration
            </h3>
            <p className="text-[9px] text-gray-400 mt-0.5">
              Evaluates travel matrices via Google Distance API to deploy physical units to ground zero dynamically.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
