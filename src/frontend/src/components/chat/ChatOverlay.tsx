import { useState, useRef, useEffect } from 'react'
import { MessageSquare, X, Send, Loader2 } from 'lucide-react'
import { apiClient } from '../../api/client'
import { useCiroStore } from '../../store/useCiroStore'

interface Message {
  role: 'user' | 'agent';
  content: string;
}

export default function ChatOverlay() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    { role: 'agent', content: 'Hello! I am Amaan. You can ask me about nearby crises or safety instructions in English, Urdu, or Roman Urdu.' }
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
  }, [messages, isOpen])

  const handleSend = async () => {
    if (!input.trim()) return
    
    const userMsg = input.trim()
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setInput('')
    setIsTyping(true)

    try {
      const payload = {
        user_message: userMsg,
        user_location: userLocation || { lat: 33.6844, lng: 73.0479, address: "Islamabad" },
        language_preference: "auto",
        conversation_history: []
      }
      const response = await apiClient.post('/chat', payload)
      
      setMessages(prev => [...prev, { role: 'agent', content: response.data.response }])
    } catch (error) {
      console.error("Chat error:", error)
      setMessages(prev => [...prev, { role: 'agent', content: "Sorry, I am currently unable to process your request." }])
    } finally {
      setIsTyping(false)
    }
  }

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-52 right-4 md:bottom-8 md:right-8 bg-emerald-600 hover:bg-emerald-700 text-white p-4 rounded-full shadow-[0_0_25px_rgba(16,185,129,0.5)] border border-emerald-400 hover:scale-105 active:scale-95 transition-all z-50 flex items-center justify-center select-none cursor-pointer"
        title="Emergency Communications Network (Amaan AI)"
      >
        <MessageSquare className="w-6 h-6 shrink-0" />
        <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-red-500 rounded-full animate-ping"></span>
      </button>
    )
  }

  return (
    <div className="fixed right-4 bottom-52 md:right-8 md:bottom-8 w-96 h-[480px] max-w-[calc(100vw-2rem)] bg-[#050505] shadow-[0_0_50px_rgba(0,0,0,0.95)] rounded border border-[#333] flex flex-col z-50 overflow-hidden animate-fade-in-up font-mono font-bold">
      {/* Header */}
      <div className="p-4 bg-[#111] border-b border-[#333] flex justify-between items-center shrink-0 select-none">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-8 h-8 rounded-full bg-emerald-600/20 border border-emerald-500/50 flex items-center justify-center text-emerald-400 font-bold text-sm">
              A
            </div>
            <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-500 rounded-full shadow-[0_0_5px_rgba(16,185,129,1)]"></div>
          </div>
          <div>
            <h3 className="font-bold text-sm text-emerald-400 tracking-wider uppercase">Amaan AI</h3>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest">Secure Comms Channel</p>
          </div>
        </div>
        <button onClick={() => setIsOpen(false)} className="p-2 text-gray-500 hover:text-white rounded-full transition-colors cursor-pointer">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#0a0a0a] custom-scrollbar">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-3 text-xs leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-blue-600/20 text-blue-100 border border-blue-500/30 rounded shadow-[0_0_10px_rgba(37,99,235,0.1)]' 
                : 'bg-[#1a1a1a] text-gray-300 border border-[#333] shadow-sm rounded'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-[#1a1a1a] text-emerald-500 p-3 rounded shadow-sm border border-[#333] flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" /> <span className="text-[10px] uppercase tracking-wider">Amaan is typing...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 bg-[#0a0a0a] border-t border-[#222] shrink-0">
        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your query..."
            style={{ 
              color: '#ffffff', 
              backgroundColor: '#0c0c0c', 
              borderColor: '#444444',
              caretColor: '#10b981' 
            }}
            className="flex-1 border rounded px-3 py-2 text-xs placeholder-gray-500 focus:border-emerald-500 focus:outline-none transition-all text-white font-mono"
          />
          <button 
            type="submit" 
            disabled={isTyping || !input.trim()}
            className="bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-4 rounded transition-colors flex items-center justify-center shrink-0 cursor-pointer disabled:opacity-30"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  )
}
