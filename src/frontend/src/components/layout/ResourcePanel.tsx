import { Ambulance, CarFront, ShieldCheck, Zap } from 'lucide-react'
import { useCiroStore } from '../../store/useCiroStore'

export default function ResourcePanel() {
  const { resourceAllocation, isLoading } = useCiroStore()

  if (isLoading) {
    return (
      <div className="glass-panel p-4 h-full animate-pulse border border-[#333] flex flex-col gap-2">
        <div className="h-4 bg-[#222] w-32 rounded mb-2"></div>
        <div className="space-y-3">
          <div className="h-12 bg-[#111] border border-[#222] rounded"></div>
          <div className="h-12 bg-[#111] border border-[#222] rounded"></div>
        </div>
      </div>
    )
  }

  if (!resourceAllocation || !resourceAllocation.crisis_allocations) {
    return (
      <div className="glass-panel p-4 h-full flex flex-col items-center justify-center text-gray-500 font-mono text-[9px] uppercase tracking-wider text-center gap-2 border border-[#333]">
        <ShieldCheck className="w-6 h-6 text-gray-600 opacity-40 animate-pulse" />
        STANDBY — RESOURCE INVENTORY IDLE
      </div>
    )
  }

  const allocation = resourceAllocation.crisis_allocations[0]
  const resources = allocation?.resources_assigned || {}
  const dispatchOrder = allocation?.dispatch_order || []

  return (
    <div className="glass-panel p-4 h-full flex flex-col gap-3 border border-[#333] overflow-hidden">
      <h2 className="panel-header flex items-center gap-2 mb-1">
        <Zap className="w-4 h-4 text-amber-400" />
        <span className="tracking-widest text-[10px] text-amber-400 font-bold">RESOURCE ALLOCATION</span>
      </h2>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-2 gap-2 shrink-0">
        {Object.entries(resources).map(([key, value]) => {
          if (!value) return null;
          const label = key.replace('_', ' ')
          return (
            <div key={key} className="bg-[#050505] border border-[#222] p-2 rounded flex flex-col items-center justify-center gap-1 font-mono">
              <span className="text-[8px] text-gray-500 uppercase tracking-widest truncate w-full text-center">{label}</span>
              <span className="text-sm font-bold text-white">QTY: {value as number}</span>
            </div>
          )
        })}
      </div>

      {/* Dispatch List */}
      <h3 className="text-[9px] font-bold text-gray-500 uppercase tracking-widest mt-1 font-mono shrink-0">DISPATCH UNIT LOG</h3>
      <div className="space-y-2 flex-1 overflow-y-auto pr-1 custom-scrollbar max-h-[140px]">
        {dispatchOrder.map((unit: any, idx: number) => {
          const isAmbulance = unit.unit_id.includes('AMB')
          return (
            <div key={idx} className="bg-[#050505] border border-[#222] p-2 rounded flex items-center justify-between font-mono text-[10px]">
              <div className="flex items-center gap-2.5">
                <div className={`p-1 rounded-sm ${isAmbulance ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'}`}>
                  {isAmbulance ? <Ambulance className="w-3.5 h-3.5" /> : <CarFront className="w-3.5 h-3.5" />}
                </div>
                <div className="flex flex-col">
                  <span className="font-bold text-gray-200">{unit.unit_id}</span>
                  <span className="text-[8px] text-gray-500 uppercase">PRIORITY: <span className="text-red-400 font-bold">{unit.priority}</span></span>
                </div>
              </div>
              <div className="flex flex-col items-end">
                <span className="font-bold text-white">{Math.round(unit.travel_time_min)} MIN</span>
                <span className="text-[8px] text-gray-500 uppercase">ETA</span>
              </div>
            </div>
          )
        })}
      </div>
      
      {/* Cost/Info Footer */}
      <div className="text-[9px] text-gray-400 leading-relaxed bg-[#050505] p-2 rounded border border-[#222] shrink-0 font-mono">
        <span className="text-amber-500 font-bold uppercase block mb-0.5">DEPLOYMENT STRATEGY</span>
        {allocation?.justification}
      </div>
    </div>
  )
}
