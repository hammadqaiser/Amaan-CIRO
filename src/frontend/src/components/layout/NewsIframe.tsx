import { Radio, X } from 'lucide-react'
import { useCiroStore } from '../../store/useCiroStore'

interface NewsIframeProps {
  index: number;
  title: string;
}

export default function NewsIframe({ index, title }: NewsIframeProps) {
  const { newsFeeds, removeNewsFeed } = useCiroStore()
  const feed = newsFeeds[index]

  if (!feed) return null;

  return (
    <div className="glass-panel p-4 h-full flex flex-col gap-2 overflow-hidden border border-[#333]">
      <div className="flex justify-between items-center mb-1">
        <h2 className="panel-header flex items-center gap-2 m-0 p-0 border-b-0 pb-0">
          <Radio className="w-4 h-4 text-red-500 animate-pulse shrink-0" />
          <span className="text-red-400 tracking-wider text-xs font-bold font-mono">{title}</span>
        </h2>
        {newsFeeds.length > 2 && index >= 2 && (
          <button 
            onClick={() => removeNewsFeed(index)}
            className="text-gray-500 hover:text-white p-1 hover:bg-[#222] rounded transition-colors shrink-0"
            title="Disconnect Stream"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      <div className="flex-1 rounded overflow-hidden border border-[#222] bg-black relative">
        {/* Sleek scanlines overlay for old television broadcast command feel */}
        <div className="absolute inset-0 bg-[radial-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_100%)] pointer-events-none z-10"></div>
        <iframe 
          src={feed}
          title={title}
          className="w-full h-full object-cover"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; picture-in-picture"
          allowFullScreen
        ></iframe>
      </div>
    </div>
  )
}
