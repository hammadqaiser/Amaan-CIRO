import { Cpu, Network, ServerCog, ShieldCheck } from 'lucide-react'

export default function ArchitecturePanel() {
  return (
    <div className="glass-panel p-4 flex-1 overflow-y-auto flex flex-col gap-3 min-w-[300px]">
      <h2 className="panel-header flex items-center gap-2">
        <ServerCog className="w-4 h-4 text-emerald-400" />
        <span className="text-emerald-400 tracking-widest">AMAAN AI CORE</span>
      </h2>

      <p className="text-[11px] text-gray-300 leading-relaxed font-medium">
        Welcome to the most advanced Crisis Intelligence & Response Orchestrator (CIRO) ever built. Amaan is a state-of-the-art, autonomous multi-agent system powered by Llama-3 70B. It fuses real-time telemetry, out-thinks cascading failures, and orchestrates life-saving deployments with zero human latency.
      </p>

      <div className="space-y-3 mt-2 border-l border-[#333] pl-3 ml-2 relative">
        <div className="absolute top-0 bottom-0 left-[-1px] w-[1px] bg-gradient-to-b from-emerald-500/50 via-blue-500/50 to-red-500/50"></div>
        
        {/* Step 1 */}
        <div className="relative">
          <div className="absolute -left-[19px] top-1 w-2.5 h-2.5 rounded-full bg-emerald-500 border-2 border-[#0a0a0a]"></div>
          <h3 className="text-[11px] font-bold text-gray-200 flex items-center gap-1.5 uppercase tracking-wider">
            <Network className="w-3 h-3 text-emerald-400" /> Hyperscale Ingestion
          </h3>
          <p className="text-[10px] text-gray-400 mt-0.5">
            Ingests live planetary data—Open-Meteo telemetry, GDELT global social signals, and ground-truth citizen reports. Cross-validates credibility instantly.
          </p>
        </div>

        {/* Step 2 */}
        <div className="relative">
          <div className="absolute -left-[19px] top-1 w-2.5 h-2.5 rounded-full bg-blue-500 border-2 border-[#0a0a0a]"></div>
          <h3 className="text-[11px] font-bold text-gray-200 flex items-center gap-1.5 uppercase tracking-wider">
            <Cpu className="w-3 h-3 text-blue-400" /> Autonomous Classification
          </h3>
          <p className="text-[10px] text-gray-400 mt-0.5">
            Our proprietary classification agent resolves contradictory signals in real-time, predicting crisis evolution and cascading infrastructure failures.
          </p>
        </div>

        {/* Step 3 */}
        <div className="relative">
          <div className="absolute -left-[19px] top-1 w-2.5 h-2.5 rounded-full bg-red-500 border-2 border-[#0a0a0a]"></div>
          <h3 className="text-[11px] font-bold text-gray-200 flex items-center gap-1.5 uppercase tracking-wider">
            <ShieldCheck className="w-3 h-3 text-red-400" /> Dynamic Allocation
          </h3>
          <p className="text-[10px] text-gray-400 mt-0.5">
            Optimizes constrained physical assets (ambulances, rescue boats) across multiple simultaneous crises, maximizing lives saved under rigid constraints.
          </p>
        </div>
      </div>
    </div>
  )
}
