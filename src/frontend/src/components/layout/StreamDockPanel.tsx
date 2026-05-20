import { useState } from 'react'
import { Plus, Tv, X, Video } from 'lucide-react'
import { useCiroStore } from '../../store/useCiroStore'

export default function StreamDockPanel() {
  const { newsFeeds, addNewsFeed, removeNewsFeed } = useCiroStore()
  const [newUrl, setNewUrl] = useState('')

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault()
    if (newUrl.trim()) {
      let url = newUrl.trim()
      // Basic youtube watch url to embed conversion
      if (url.includes('watch?v=')) {
        const videoId = url.split('v=')[1]?.split('&')[0]
        url = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1`
      } else if (url.includes('youtu.be/')) {
        const videoId = url.split('youtu.be/')[1]?.split('?')[0]
        url = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1`
      } else if (!url.includes('embed')) {
        // Fallback youtube embed pattern
        url = `https://www.youtube.com/embed/${url}?autoplay=1&mute=1`
      }
      addNewsFeed(url)
      setNewUrl('')
    }
  }

  return (
    <div className="glass-panel p-4 h-full flex flex-col gap-3 border border-[#333] justify-between">
      <div>
        <h2 className="panel-header flex items-center gap-2 mb-2">
          <Tv className="w-4.5 h-4.5 text-emerald-400" />
          <span className="text-emerald-400 tracking-widest text-xs font-bold">BROADCAST DOCK</span>
        </h2>
        <p className="text-[10px] text-gray-400 leading-relaxed mb-4">
          Establish real-time video linkages with ground reporters or broadcast news. Paste a YouTube Live stream link below to deploy a new monitoring panel.
        </p>

        <form onSubmit={handleAdd} className="flex flex-col gap-2">
          <label className="text-[9px] uppercase tracking-wider text-gray-500 font-bold">Operational Stream Source</label>
          <div className="flex gap-1.5">
            <input 
              type="text" 
              placeholder="Enter YouTube Stream URL..." 
              value={newUrl}
              onChange={(e) => setNewUrl(e.target.value)}
              className="flex-1 bg-[#050505] border border-[#333] rounded px-3 py-2 text-xs text-gray-300 focus:outline-none focus:border-emerald-500/50"
            />
            <button 
              type="submit" 
              className="bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded px-3 transition-colors flex items-center justify-center cursor-pointer"
            >
              <Plus className="w-4.5 h-4.5" />
            </button>
          </div>
        </form>
      </div>

      <div className="border-t border-[#222] pt-3 mt-2">
        <h3 className="text-[9px] uppercase tracking-wider text-gray-500 font-bold mb-2">Active Linkages</h3>
        <div className="space-y-1.5 max-h-[100px] overflow-y-auto pr-1 custom-scrollbar">
          {newsFeeds.map((feed, idx) => {
            const isGeo = feed.includes('Ecc2Id5Js9g')
            const isAry = feed.includes('K77zGtR_X58')
            const label = isGeo ? 'GEO NEWS LIVE LINK' : isAry ? 'ARY NEWS LIVE LINK' : `CUSTOM FEED LINK #${idx - 1}`
            return (
              <div key={idx} className="bg-[#050505] border border-[#222] px-2 py-1.5 rounded flex items-center justify-between text-[10px]">
                <span className="text-gray-300 flex items-center gap-1.5 truncate">
                  <Video className="w-3.5 h-3.5 text-gray-500" />
                  {label}
                </span>
                {idx >= 2 && (
                  <button 
                    onClick={() => removeNewsFeed(idx)}
                    className="text-red-500/60 hover:text-red-400 p-0.5"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
