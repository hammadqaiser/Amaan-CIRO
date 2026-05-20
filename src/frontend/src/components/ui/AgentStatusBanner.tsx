import { useCiroStore } from '../../store/useCiroStore'
import { Cpu } from 'lucide-react'

export default function AgentStatusBanner() {
  const { agentStatus, isLoading } = useCiroStore()

  if (!isLoading && agentStatus === 'System Ready') return null

  return (
    <div className="absolute top-14 left-1/2 -translate-x-1/2 z-[60] animate-fade-in-down">
      <div className="bg-[#050505] border border-emerald-500/50 px-4 py-2 flex items-center gap-3 rounded shadow-[0_0_20px_rgba(16,185,129,0.2)]">
        {isLoading ? (
          <div className="relative flex items-center justify-center">
            <div className="w-5 h-5 border-2 border-emerald-500/30 border-t-emerald-400 rounded-full animate-spin"></div>
            <Cpu className="w-2.5 h-2.5 text-emerald-400 absolute" />
          </div>
        ) : (
          <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"></div>
        )}
        <span className="text-emerald-400 text-[11px] font-bold tracking-wider uppercase">
          {agentStatus}
        </span>
      </div>
    </div>
  )
}
