import { useState, useEffect } from 'react'
import { Radio } from 'lucide-react'

/**
 * LiveStatusTicker — Slim real-time Islamabad ICT clock bar.
 * Compact height matching the CIRO Tactical Console bar below it.
 */
export default function LiveStatusTicker() {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const formattedDate = currentTime.toLocaleDateString('en-US', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    timeZone: 'Asia/Karachi'
  }).toUpperCase()

  const formattedTime = currentTime.toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    timeZone: 'Asia/Karachi'
  })

  return (
    <div className="h-12 w-full bg-[#070707] border-b border-[#1a1a1a] px-4 flex items-center justify-center gap-3 select-none shrink-0">
      <Radio className="w-3 h-3 text-emerald-500 animate-pulse" />
      <span className="text-[10px] text-gray-400 font-bold tracking-wider">
        {formattedDate}
      </span>
      <span className="text-[12px] text-emerald-400 font-extrabold tracking-widest tabular-nums">
        {formattedTime}
      </span>
      <span className="text-[9px] text-gray-600 font-bold tracking-wider">
        PKT
      </span>
    </div>
  )
}
