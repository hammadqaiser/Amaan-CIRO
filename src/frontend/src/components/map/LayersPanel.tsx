import { useState } from 'react'
import { Layers, CheckSquare, Square } from 'lucide-react'
import { useCiroStore } from '../../store/useCiroStore'

export default function LayersPanel() {
  const [isExpanded, setIsExpanded] = useState(false)
  const { 
    showCrisisZones, 
    showResources, 
    showWeatherRadar, 
    showShelters, 
    showVulnerabilities, 
    showSignals, 
    toggleLayer 
  } = useCiroStore()

  if (!isExpanded) {
    return (
      <button 
        onClick={() => setIsExpanded(true)}
        className="absolute top-4 left-4 z-10 p-3 bg-[#0a0a0a]/95 backdrop-blur border border-[#1f1f1f] hover:border-emerald-500/50 rounded-full shadow-[0_0_15px_rgba(0,0,0,0.85)] flex items-center justify-center transition-all cursor-pointer group active:scale-95"
        title="Toggle Map Layers"
      >
        <Layers className="w-5 h-5 text-emerald-400 group-hover:scale-110 transition-transform" />
      </button>
    )
  }

  return (
    <div className="absolute top-4 left-4 bg-[#0a0a0a]/95 backdrop-blur border border-[#1f1f1f] rounded shadow-[0_0_20px_rgba(0,0,0,0.9)] z-10 w-52 overflow-hidden animate-fade-in-right">
      <div className="px-3 py-2 border-b border-[#1a1a1a] flex items-center justify-between bg-[#0e0e0e]">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-500" />
          <h3 className="text-[10px] font-bold text-gray-200 tracking-widest uppercase font-mono">Layers</h3>
        </div>
        <button 
          onClick={() => setIsExpanded(false)}
          className="text-gray-500 hover:text-white text-[10px] font-bold font-mono transition-colors cursor-pointer"
        >
          [✕]
        </button>
      </div>
      <div className="flex flex-col py-1">
        {/* CRISIS ZONES */}
        <button 
          onClick={() => toggleLayer('showCrisisZones')}
          className="flex items-center justify-between px-3 py-1.5 hover:bg-[#151515] transition-colors text-left cursor-pointer"
        >
          <span className="text-[9px] text-gray-300 font-bold uppercase tracking-wider flex items-center gap-2 font-mono">
            {showCrisisZones ? <CheckSquare className="w-3.5 h-3.5 text-emerald-400" /> : <Square className="w-3.5 h-3.5 text-gray-600" />}
            CRISIS ZONES
          </span>
          {showCrisisZones && <div className="w-1.5 h-1.5 bg-red-500 rounded-full shadow-[0_0_5px_rgba(239,68,68,0.8)] animate-pulse"></div>}
        </button>
        
        {/* ALLOCATIONS */}
        <button 
          onClick={() => toggleLayer('showResources')}
          className="flex items-center justify-between px-3 py-1.5 hover:bg-[#151515] transition-colors text-left cursor-pointer"
        >
          <span className="text-[9px] text-gray-300 font-bold uppercase tracking-wider flex items-center gap-2 font-mono">
            {showResources ? <CheckSquare className="w-3.5 h-3.5 text-emerald-400" /> : <Square className="w-3.5 h-3.5 text-gray-600" />}
            ALLOCATIONS
          </span>
          {showResources && <div className="w-1.5 h-1.5 bg-blue-500 rounded-full shadow-[0_0_5px_rgba(59,130,246,0.8)] animate-pulse"></div>}
        </button>

        {/* EMERGENCY SHELTERS */}
        <button 
          onClick={() => toggleLayer('showShelters')}
          className="flex items-center justify-between px-3 py-1.5 hover:bg-[#151515] transition-colors text-left border-t border-[#1a1a1a] cursor-pointer"
        >
          <span className="text-[9px] text-gray-300 font-bold uppercase tracking-wider flex items-center gap-2 font-mono">
            {showShelters ? <CheckSquare className="w-3.5 h-3.5 text-emerald-400" /> : <Square className="w-3.5 h-3.5 text-gray-600" />}
            SHELTERS & EVAC
          </span>
          {showShelters && <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full shadow-[0_0_5px_rgba(16,185,129,0.8)] animate-pulse"></div>}
        </button>

        {/* VULNERABILITY INDEX */}
        <button 
          onClick={() => toggleLayer('showVulnerabilities')}
          className="flex items-center justify-between px-3 py-1.5 hover:bg-[#151515] transition-colors text-left cursor-pointer"
        >
          <span className="text-[9px] text-gray-300 font-bold uppercase tracking-wider flex items-center gap-2 font-mono">
            {showVulnerabilities ? <CheckSquare className="w-3.5 h-3.5 text-emerald-400" /> : <Square className="w-3.5 h-3.5 text-gray-600" />}
            VULNERABILITY INDEX
          </span>
          {showVulnerabilities && <div className="w-1.5 h-1.5 bg-amber-500 rounded-full shadow-[0_0_5px_rgba(245,158,11,0.8)] animate-pulse"></div>}
        </button>

        {/* WEATHER RADAR */}
        <button 
          onClick={() => toggleLayer('showWeatherRadar')}
          className="flex items-center justify-between px-3 py-1.5 hover:bg-[#151515] transition-colors text-left border-t border-[#1a1a1a] cursor-pointer"
        >
          <span className="text-[9px] text-gray-300 font-bold uppercase tracking-wider flex items-center gap-2 font-mono">
            {showWeatherRadar ? <CheckSquare className="w-3.5 h-3.5 text-emerald-400" /> : <Square className="w-3.5 h-3.5 text-gray-600" />}
            WEATHER RADAR
          </span>
          {showWeatherRadar && <div className="w-1.5 h-1.5 bg-cyan-500 rounded-full shadow-[0_0_5px_rgba(6,182,212,0.8)] animate-pulse"></div>}
        </button>

        {/* FIELD SIGNALS */}
        <button 
          onClick={() => toggleLayer('showSignals')}
          className="flex items-center justify-between px-3 py-1.5 hover:bg-[#151515] transition-colors text-left cursor-pointer"
        >
          <span className="text-[9px] text-gray-300 font-bold uppercase tracking-wider flex items-center gap-2 font-mono">
            {showSignals ? <CheckSquare className="w-3.5 h-3.5 text-emerald-400" /> : <Square className="w-3.5 h-3.5 text-gray-600" />}
            FIELD SIGNALS
          </span>
          {showSignals && <div className="w-1.5 h-1.5 bg-orange-500 rounded-full shadow-[0_0_5px_rgba(249,115,22,0.8)] animate-pulse"></div>}
        </button>
      </div>
    </div>
  )
}

