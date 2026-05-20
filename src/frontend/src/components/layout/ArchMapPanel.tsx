import { Map, Navigation, ShieldCheck } from 'lucide-react'

export default function ArchMapPanel() {
  return (
    <div className="glass-panel p-5 h-full flex flex-col gap-4 min-h-[300px] overflow-hidden border border-[#222] hover:border-blue-500/30 transition-all duration-300">
      <h2 className="panel-header flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Map className="w-5 h-5 text-blue-400" />
          <span className="text-blue-400 tracking-widest text-sm font-bold font-mono">TACTICAL MAP CANVAS</span>
        </div>
        <span className="text-[10px] bg-blue-500/10 text-blue-400 px-2 py-1 rounded border border-blue-500/20 font-mono">
          GEOSPATIAL CORE
        </span>
      </h2>

      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        <p className="text-[13px] text-gray-300 leading-relaxed font-sans mb-4 text-justify">
          During heavy downpours, streets instantly submerge. In past disasters, rescue operations were paralyzed because dispatchers lacked visibility into active hazard boundaries.
        </p>

        <p className="text-[13px] text-gray-300 leading-relaxed font-sans mb-6 text-justify">
          Amaan transforms emergency mapping. The <strong>Tactical Map Canvas</strong> overlays active hazard zones, sensor telemetries, and live responder coordinates—creating an absolute source of truth.
        </p>

        <div className="space-y-5 border-l-2 border-blue-500/20 pl-4 ml-2 relative">
          <div className="absolute top-0 bottom-0 left-[-2px] w-[2px] bg-gradient-to-b from-blue-500/50 to-transparent"></div>
          
          <div className="relative">
            <div className="absolute -left-[23px] top-1.5 w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></div>
            <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-1.5 font-mono">
              <ShieldCheck className="w-4 h-4 text-blue-400" /> Dynamic Hazard Zones
            </h3>
            <p className="text-xs text-gray-400 mt-1 font-sans">
              Auto-generates visual high-risk flood boundaries directly over vulnerable sectors.
            </p>
          </div>

          <div className="relative">
            <div className="absolute -left-[23px] top-1.5 w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
            <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-1.5 font-mono">
              <Navigation className="w-4 h-4 text-emerald-400 animate-pulse" /> Safe Corridor Routing
            </h3>
            <p className="text-xs text-gray-400 mt-1 font-sans">
              Utilizes spatial pathfinding algorithms to map non-submerged evacuation routes.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
