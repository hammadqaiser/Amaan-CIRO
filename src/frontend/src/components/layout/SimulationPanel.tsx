import { Users, AlertOctagon, Timer, ShieldAlert } from 'lucide-react'
import { useCiroStore } from '../../store/useCiroStore'

export default function SimulationPanel() {
  const { simulationResult, isLoading } = useCiroStore()

  if (isLoading) {
    return (
      <div className="glass-panel p-4 h-64 shrink-0 animate-pulse border border-[#333]">
        <div className="h-4 bg-[#222] w-24 rounded mb-4"></div>
        <div className="space-y-2">
          <div className="h-16 bg-[#111] rounded border border-[#222]"></div>
          <div className="h-16 bg-[#111] rounded border border-[#222]"></div>
        </div>
      </div>
    )
  }

  if (!simulationResult) {
    return (
      <div className="glass-panel p-4 h-64 shrink-0 flex flex-col items-center justify-center text-gray-500 font-mono text-[9px] uppercase tracking-wider text-center gap-2 border border-[#333]">
        <ShieldAlert className="w-6 h-6 text-gray-600 opacity-40 animate-pulse" />
        STANDBY — PIPELINE RESULTS REQUIRED
      </div>
    )
  }

  const metrics = simulationResult.metrics || {}
  const baseline = simulationResult.baseline_comparison || {}

  return (
    <div className="glass-panel p-4 h-64 shrink-0 flex flex-col gap-3 border border-[#333]">

      <div className="grid grid-cols-2 gap-3 flex-1">
        <div className="bg-[#050505] p-3 rounded border border-[#222] flex flex-col justify-center">
          <div className="flex items-center gap-1.5 mb-1">
            <Timer className="w-4 h-4 text-blue-400" />
            <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider">Response Time</span>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-white font-mono">{baseline.amaan_response_time_minutes || 0}</span>
            <span className="text-xs text-gray-400 font-mono">min</span>
          </div>
          <span className="text-[9px] text-emerald-400 font-bold font-mono mt-1">
            -{metrics.response_time_improvement_pct || 0}% VS BASELINE
          </span>
        </div>

        <div className="bg-[#050505] p-3 rounded border border-[#222] flex flex-col justify-center">
          <div className="flex items-center gap-1.5 mb-1">
            <Users className="w-4 h-4 text-emerald-400" />
            <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider">Lives Protected</span>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-white font-mono">{metrics.estimated_lives_protected || 0}</span>
          </div>
          <span className="text-[9px] text-gray-400 font-mono mt-1">
            FROM {metrics.population_protected?.toLocaleString() || 0} AT RISK
          </span>
        </div>
      </div>

      <div className="bg-blue-950/20 border border-blue-900/40 p-2 rounded flex gap-2 items-start mt-auto">
        <AlertOctagon className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
        <p className="text-[9px] text-gray-300 leading-relaxed font-mono uppercase tracking-wide">
          {baseline.improvement_summary || "SIMULATION COMPLETE — INTRUSIVE CRISIS LOGISTICS DEPLOYED."}
        </p>
      </div>
    </div>
  )
}
