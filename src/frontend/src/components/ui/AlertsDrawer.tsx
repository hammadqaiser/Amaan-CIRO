import { useState, useEffect } from 'react'
import { Bell, ChevronUp, ChevronDown, ShieldAlert, Info } from 'lucide-react'
import { useCiroStore } from '../../store/useCiroStore'
import { formatDistanceToNow } from 'date-fns'

export default function AlertsDrawer() {
  const [isOpen, setIsOpen] = useState(false)
  const { publicAlerts, loadLocalAlerts } = useCiroStore()

  useEffect(() => {
    loadLocalAlerts()
  }, [])

  // Auto-open if a new high-urgency alert comes in
  useEffect(() => {
    if (publicAlerts.length > 0 && publicAlerts[0].urgency_level?.toLowerCase() === 'high') {
      setIsOpen(true)
    }
  }, [publicAlerts])

  return (
    <div className={`absolute bottom-0 left-0 right-0 z-30 transition-transform duration-300 ease-in-out ${isOpen ? 'translate-y-0' : 'translate-y-[calc(100%-3rem)]'}`}>
      <div className="glass-panel w-full max-h-[60vh] flex flex-col">
        {/* Drag Handle / Header */}
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className="w-full h-12 flex items-center justify-between px-4 border-b border-gray-200 bg-white/50 hover:bg-white/80 transition-colors rounded-t-2xl shrink-0"
        >
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-[var(--color-primary)]" />
            <span className="font-semibold text-sm text-[var(--color-text-main)]">
              Local Alerts
              {publicAlerts.length > 0 && (
                <span className="ml-2 bg-[var(--color-danger)] text-white text-[10px] px-1.5 py-0.5 rounded-full">
                  {publicAlerts.length}
                </span>
              )}
            </span>
          </div>
          {isOpen ? <ChevronDown className="w-5 h-5 text-gray-400" /> : <ChevronUp className="w-5 h-5 text-gray-400" />}
        </button>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-[#f8fafc]">
          {publicAlerts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-gray-400">
              <ShieldAlert className="w-12 h-12 mb-2 opacity-20" />
              <p className="text-sm">No active alerts in your area.</p>
            </div>
          ) : (
            publicAlerts.map(alert => (
              <div key={alert.id} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col gap-2">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-1.5">
                    {alert.urgency_level?.toLowerCase() === 'high' ? (
                      <ShieldAlert className="w-4 h-4 text-[var(--color-danger)]" />
                    ) : (
                      <Info className="w-4 h-4 text-[var(--color-secondary)]" />
                    )}
                    <h3 className="font-bold text-sm text-[var(--color-text-main)]">{alert.subject || 'Public Alert'}</h3>
                  </div>
                  <span className="text-[10px] text-gray-400 font-medium">
                    {formatDistanceToNow(new Date(alert.sent_at), { addSuffix: true })}
                  </span>
                </div>
                <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">
                  {alert.body}
                </p>
                <div className="mt-1 flex gap-2">
                   <span className="text-[9px] uppercase tracking-wider bg-gray-100 text-gray-500 px-2 py-0.5 rounded">
                     {alert.channel}
                   </span>
                   {alert.language && (
                     <span className="text-[9px] uppercase tracking-wider bg-gray-100 text-gray-500 px-2 py-0.5 rounded">
                       {alert.language}
                     </span>
                   )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
