import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Bot, User } from 'lucide-react'
import { apiClient } from '../../api/client'
import { useCiroStore } from '../../store/useCiroStore'

interface Message {
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
}

export default function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([
    { 
      role: 'agent', 
      content: 'Hello! I am Amaan, your autonomous crisis intelligence agent. Ask me about ongoing disasters, evacuation alerts, resource deployments, or general safety instructions in English, Urdu, or Roman Urdu.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const { userLocation } = useCiroStore()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return
    
    const userMsg = input.trim()
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    
    setMessages(prev => [...prev, { role: 'user', content: userMsg, timestamp: now }])
    setInput('')
    setIsTyping(true)

    try {
      const payload = {
        user_message: userMsg,
        user_location: userLocation || { lat: 33.6844, lng: 73.0479, address: "Islamabad" },
        language_preference: "auto",
        conversation_history: messages.map(m => ({ role: m.role, content: m.content }))
      }
      const response = await apiClient.post('/chat', payload)
      
      setMessages(prev => [...prev, { 
        role: 'agent', 
        content: response.data.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }])
    } catch (error) {
      console.error("Chat error:", error)
      setMessages(prev => [...prev, { 
        role: 'agent', 
        content: "Operational link degraded. I am currently unable to fetch live telemetry. Please check server linkage or network connection.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }])
    } finally {
      setIsTyping(false)
    }
  }

  return (
    <div className="w-full h-full flex flex-col bg-[#020202] font-mono">
      {/* HUD Header Banner */}
      <div className="px-4 py-3 bg-[#070707] border-b border-[#1f1f1f] flex justify-between items-center shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_#10b981]"></div>
          <span className="text-[10px] font-black text-emerald-400 tracking-widest uppercase">AMAAN SECURE AI LINK</span>
        </div>
        <span className="text-[7.5px] font-bold text-gray-500 uppercase tracking-widest bg-gray-900 border border-gray-800 px-1.5 py-0.5 rounded">
          CRYPTO CHANNEL
        </span>
      </div>

      {/* Message History Board */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 custom-scrollbar bg-[#020202] pb-24">
        {messages.map((msg, idx) => {
          const isAgent = msg.role === 'agent';
          return (
            <div key={idx} className={`flex flex-col ${isAgent ? 'items-start' : 'items-end'} gap-1.5 animate-fade-in-up`}>
              <div className="flex items-center gap-1.5 px-1.5 text-[7.5px] font-bold text-gray-500 uppercase tracking-wider font-mono">
                {isAgent ? (
                  <>
                    <Bot className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span className="text-emerald-400">Amaan Core AI</span>
                  </>
                ) : (
                  <>
                    <User className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                    <span className="text-blue-400">Tactical Operator</span>
                  </>
                )}
                <span>•</span>
                <span>{msg.timestamp}</span>
              </div>
              
              <div className={`max-w-[90%] p-4 text-[13px] leading-relaxed font-mono ${
                isAgent 
                  ? 'bg-[#090909] text-gray-100 border border-[#1f1f1f] rounded-r-xl rounded-bl-xl shadow-lg' 
                  : 'bg-blue-950/20 text-blue-100 border border-blue-500/25 rounded-l-xl rounded-br-xl shadow-md'
              }`}>
                {msg.content}
              </div>
            </div>
          )
        })}

        {isTyping && (
          <div className="flex flex-col items-start gap-1.5 animate-pulse">
            <div className="flex items-center gap-1.5 px-1.5 text-[7.5px] font-bold text-emerald-500 uppercase tracking-wider font-mono">
              <Bot className="w-3.5 h-3.5 text-emerald-400" />
              <span>Amaan Core AI is thinking...</span>
            </div>
            <div className="bg-[#090909] text-emerald-400 p-3 rounded-r-xl rounded-bl-xl border border-[#1f1f1f] flex items-center gap-2 shadow-lg">
              <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
              <span className="text-[9px] uppercase tracking-widest font-extrabold">Synthesizing raw signals...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Inline Text Input Console */}
      <div className="p-3 bg-[#070707] border-t border-[#1f1f1f] shrink-0 pb-5">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSend(); }} 
          className="flex gap-2 bg-[#020202] border border-[#2c2c2c] rounded-md p-1 items-center focus-within:border-emerald-500/50 transition-colors"
        >
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Query crisis details, maps, safety tips..."
            style={{ 
              color: '#ffffff', 
              backgroundColor: 'transparent', 
              caretColor: '#10b981' 
            }}
            className="flex-1 border-none bg-transparent px-3 py-2 text-xs placeholder-gray-600 focus:outline-none text-white font-mono"
            disabled={isTyping}
          />
          <button 
            type="submit" 
            disabled={isTyping || !input.trim()}
            className="h-8 w-8 bg-emerald-500 hover:bg-emerald-600 text-black rounded transition-all flex items-center justify-center shrink-0 cursor-pointer disabled:opacity-30 active:scale-95"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  )
}
