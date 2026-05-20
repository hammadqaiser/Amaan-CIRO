import { 
  ShieldAlert, 
  RadioTower, 
  Activity, 
  Flame, 
  FileText,
  AlertTriangle
} from 'lucide-react'
import { useCiroStore, type Alert } from '../../store/useCiroStore'

interface AlertsPanelProps {
  audience: 'ndma' | 'emergency_services' | 'hospitals' | 'public' | 'media';
}

const AUDIENCE_CONFIGS = {
  ndma: {
    title: 'NDMA COMMAND CORE',
    icon: ShieldAlert,
    textColor: 'text-amber-400',
    borderColor: 'border-amber-500/20',
    bgColor: 'bg-amber-500/5',
    indicatorColor: 'bg-amber-500'
  },
  emergency_services: {
    title: 'RESCUE 1122 DISPATCH',
    icon: Flame,
    textColor: 'text-red-400',
    borderColor: 'border-red-500/20',
    bgColor: 'bg-red-500/5',
    indicatorColor: 'bg-red-500'
  },
  hospitals: {
    title: 'PIMS HOSPITAL INFLOW',
    icon: Activity,
    textColor: 'text-blue-400',
    borderColor: 'border-blue-500/20',
    bgColor: 'bg-blue-500/5',
    indicatorColor: 'bg-blue-500'
  },
  public: {
    title: 'CIVIC DEFENSE BROADCAST',
    icon: RadioTower,
    textColor: 'text-emerald-400',
    borderColor: 'border-emerald-500/20',
    bgColor: 'bg-emerald-500/5',
    indicatorColor: 'bg-emerald-500'
  },
  media: {
    title: 'PRESS BROADCAST DESK',
    icon: FileText,
    textColor: 'text-purple-400',
    borderColor: 'border-purple-500/20',
    bgColor: 'bg-purple-500/5',
    indicatorColor: 'bg-purple-500'
  }
}

export default function AlertsPanel({ audience }: AlertsPanelProps) {
  const { allAlerts, isLoading } = useCiroStore()

  const config = AUDIENCE_CONFIGS[audience] || AUDIENCE_CONFIGS.public
  const Icon = config.icon

  // Filter alerts matching our target audience
  const filteredAlerts = allAlerts.filter(
    (alert: Alert) => alert.audience.toLowerCase() === audience.toLowerCase()
  )

  if (isLoading) {
    return (
      <div className="glass-panel p-4 h-full animate-pulse border border-[#333]">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-4 h-4 bg-[#222] rounded"></div>
          <div className="h-4 bg-[#222] w-32 rounded"></div>
        </div>
        <div className="space-y-2">
          <div className="h-14 bg-[#111] rounded border border-[#222]"></div>
          <div className="h-14 bg-[#111] rounded border border-[#222]"></div>
        </div>
      </div>
    )
  }

  return (
    <div className={`glass-panel p-4 h-full flex flex-col gap-3 border border-[#333] min-w-[280px]`}>
      {/* Dynamic Tactical Header */}
      <div className="flex justify-between items-center mb-1 pb-1 border-b border-[#222]">
        <h2 className="flex items-center gap-2 m-0 p-0">
          <Icon className={`w-4 h-4 ${config.textColor}`} />
          <span className={`tracking-widest text-[10px] font-bold ${config.textColor} font-mono`}>
            {config.title}
          </span>
        </h2>
        
        {/* Pulsating status light */}
        <div className="flex items-center gap-1.5">
          <span className="text-[8px] text-gray-500 tracking-wider font-mono">STATUS</span>
          <span className={`relative flex h-2 w-2`}>
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${config.indicatorColor} opacity-75`}></span>
            <span className={`relative inline-flex rounded-full h-2 w-2 ${config.indicatorColor}`}></span>
          </span>
        </div>
      </div>

      {/* Communications feed */}
      <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-4 custom-scrollbar max-h-[550px]">
        {filteredAlerts.length === 0 ? (
          <div className="text-center text-[9px] text-gray-600 mt-6 font-mono uppercase tracking-wider flex flex-col items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5 text-gray-600 opacity-40 mb-1" />
            STANDBY — COMMS VECTOR IDLE
          </div>
        ) : (
          filteredAlerts.map((alert: Alert) => {
            return (
              <div 
                key={alert.id} 
                className={`border ${config.borderColor} ${config.bgColor} rounded-xl p-5 flex flex-col gap-3 shadow-xl relative overflow-hidden transition-all duration-300 hover:scale-[1.01]`}
              >
                {/* Visual side accent bar */}
                <div className={`absolute top-0 bottom-0 left-0 w-1 ${config.indicatorColor}`}></div>
                
                <div className="flex items-center justify-between pl-1 border-b border-[#222]/40 pb-2 mb-0.5">
                  <span className={`text-[9px] font-black uppercase tracking-widest font-mono ${
                    alert.urgency_level?.toLowerCase() === 'high' || alert.urgency_level?.toLowerCase() === 'critical' ? 'text-red-400 font-extrabold' : 'text-gray-400'
                  }`}>
                    PRIORITY: {alert.urgency_level || 'STANDARD'}
                  </span>
                  <span className="text-[9px] text-gray-500 font-mono font-bold">
                    {new Date(alert.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                
                <div className="text-sm sm:text-base font-black text-white leading-snug pl-1 font-mono uppercase tracking-wide">
                  {alert.subject}
                </div>
                
                <div className="text-xs sm:text-[13px] text-gray-200 leading-relaxed pl-1 font-mono">
                  {alert.body}
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
