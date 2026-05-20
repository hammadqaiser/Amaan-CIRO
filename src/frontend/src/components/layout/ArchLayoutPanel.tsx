import { LayoutGrid, Tv, Users } from 'lucide-react'

export default function ArchLayoutPanel() {
  return (
    <div className="glass-panel p-5 h-full flex flex-col gap-4 min-h-[300px] overflow-hidden border border-[#222] hover:border-purple-500/30 transition-all duration-300">
      <h2 className="panel-header flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <LayoutGrid className="w-5 h-5 text-purple-400" />
          <span className="text-purple-400 tracking-widest text-sm font-bold font-mono">ADAPTIVE COMMAND LAYOUT</span>
        </div>
        <span className="text-[10px] bg-purple-500/10 text-purple-400 px-2 py-1 rounded border border-purple-500/20 font-mono">
          OPERATIONAL UX
        </span>
      </h2>

      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        <p className="text-[13px] text-gray-300 leading-relaxed font-sans mb-4 text-justify">
          Simultaneous disasters create cognitive overload. In legacy control rooms, coordinators were forced to manually toggle between multiple scattered browsers, slowing down vital decisions.
        </p>

        <p className="text-[13px] text-gray-300 leading-relaxed font-sans mb-6 text-justify">
          Amaan solves dashboard fragmentation. The <strong>Adaptive Command Layout</strong> integrates customizable satellite news, predictive simulations, and multi-agency monitors into a single high-density workspace.
        </p>

        <div className="space-y-5 border-l-2 border-purple-500/20 pl-4 ml-2 relative">
          <div className="absolute top-0 bottom-0 left-[-2px] w-[2px] bg-gradient-to-b from-purple-500/50 to-transparent"></div>
          
          <div className="relative">
            <div className="absolute -left-[23px] top-1.5 w-2.5 h-2.5 rounded-full bg-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.5)]"></div>
            <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-1.5 font-mono">
              <Tv className="w-4 h-4 text-purple-400" /> Multi-Stream Telecasts
            </h3>
            <p className="text-xs text-gray-400 mt-1 font-sans">
              Embeds live news telecast modules alongside operational telemetry.
            </p>
          </div>

          <div className="relative">
            <div className="absolute -left-[23px] top-1.5 w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></div>
            <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-1.5 font-mono">
              <Users className="w-4 h-4 text-blue-400" /> Stakeholder Desks
            </h3>
            <p className="text-xs text-gray-400 mt-1 font-sans">
              Segments public and official alerts into specialized audience desks.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
