import { MessageSquare, Languages, HeartHandshake } from 'lucide-react'

export default function ArchChatPanel() {
  return (
    <div className="glass-panel p-5 h-full flex flex-col gap-4 min-h-[300px] overflow-hidden border border-[#222] hover:border-amber-500/30 transition-all duration-300">
      <h2 className="panel-header flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-amber-400" />
          <span className="text-amber-400 tracking-widest text-sm font-bold font-mono">LIVE CITIZEN LIFELINE</span>
        </div>
        <span className="text-[10px] bg-amber-500/10 text-amber-400 px-2 py-1 rounded border border-amber-500/20 font-mono">
          CITIZEN CHAT
        </span>
      </h2>

      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        <p className="text-[13px] text-gray-300 leading-relaxed font-sans mb-4 text-justify">
          When storms strike, telephone switchboards are overwhelmed. Standard systems exclude vulnerable populations by requiring formal English or complex forms.
        </p>

        <p className="text-[13px] text-gray-300 leading-relaxed font-sans mb-6 text-justify">
          The <strong>Live Citizen Lifeline</strong> is a direct conversational link. It understands natural queries in <strong>Urdu, Roman Urdu, and English</strong>, delivering instant life-saving advice to anyone, anywhere.
        </p>

        <div className="space-y-5 border-l-2 border-amber-500/20 pl-4 ml-2 relative">
          <div className="absolute top-0 bottom-0 left-[-2px] w-[2px] bg-gradient-to-b from-amber-500/50 to-transparent"></div>
          
          <div className="relative">
            <div className="absolute -left-[23px] top-1.5 w-2.5 h-2.5 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]"></div>
            <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-1.5 font-mono">
              <Languages className="w-4 h-4 text-amber-400" /> Multilingual Support
            </h3>
            <p className="text-xs text-gray-400 mt-1 font-sans">
              Interacts fluently in the citizen's choice of language, ensuring zero exclusion.
            </p>
          </div>

          <div className="relative">
            <div className="absolute -left-[23px] top-1.5 w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
            <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-1.5 font-mono">
              <HeartHandshake className="w-4 h-4 text-emerald-400 animate-pulse" /> Active Feedback Loop
            </h3>
            <p className="text-xs text-gray-400 mt-1 font-sans">
              Extracts actionable geolocation signals from conversations to update command overlays.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
