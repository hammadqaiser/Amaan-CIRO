import { Cpu, ShieldAlert, Sparkles } from 'lucide-react'

export default function ArchEnginePanel() {
  return (
    <div className="glass-panel p-5 h-full flex flex-col gap-4 min-h-[300px] overflow-hidden border border-[#222] hover:border-emerald-500/30 transition-all duration-300">
      <h2 className="panel-header flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-emerald-400 animate-pulse" />
          <span className="text-emerald-400 tracking-widest text-sm font-bold font-mono">AMAAN CIRO ENGINE</span>
        </div>
        <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded border border-emerald-500/20 font-mono">
          AUTONOMOUS CORE
        </span>
      </h2>

      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        <p className="text-[13px] text-gray-300 leading-relaxed font-sans mb-4 text-justify">
          The catastrophic 2022 floods across Pakistan exposed a fatal flaw: legacy response networks were paralyzed by information lag. Critical hours were lost to scattered data and isolated operations.
        </p>

        <p className="text-[13px] text-gray-300 leading-relaxed font-sans mb-6 text-justify">
          <strong>Amaan CIRO</strong> is the sovereign solution. Its autonomous multi-agent intelligence core fuses planetary weather data, live traffic, and citizen reports—transforming chaotic noise into immediate, verified action.
        </p>

        <div className="space-y-5 border-l-2 border-emerald-500/20 pl-4 ml-2 relative">
          <div className="absolute top-0 bottom-0 left-[-2px] w-[2px] bg-gradient-to-b from-emerald-500/50 to-transparent"></div>
          
          <div className="relative">
            <div className="absolute -left-[23px] top-1.5 w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
            <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-1.5 font-mono">
              <Sparkles className="w-4 h-4 text-emerald-400" /> Multi-Agent Intelligence
            </h3>
            <p className="text-xs text-gray-400 mt-1 font-sans">
              Agents coordinate in milliseconds to classify risks and optimize life-saving logistics.
            </p>
          </div>

          <div className="relative">
            <div className="absolute -left-[23px] top-1.5 w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></div>
            <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-1.5 font-mono">
              <ShieldAlert className="w-4 h-4 text-blue-400" /> Contradiction Resolution
            </h3>
            <p className="text-xs text-gray-400 mt-1 font-sans">
              Instantly cross-references credibility to filter out false alarms and authenticate threats.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
