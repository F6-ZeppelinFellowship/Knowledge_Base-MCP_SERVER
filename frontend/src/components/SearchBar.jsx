import { Search, SlidersHorizontal, Loader2 } from 'lucide-react'

export default function SearchBar({ query, setQuery, topK, setTopK, onSearch, loading }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      onSearch()
    }
  }

  return (
    <div className="bg-[#121824]/90 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-xl space-y-3">
      {/* Search Input Row */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask something your notes already know..."
            className="w-full bg-white/[0.04] border border-white/10 rounded-xl pl-10 pr-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-emerald-500/50 transition-colors"
          />
        </div>
        <button
          onClick={onSearch}
          disabled={loading || !query.trim()}
          className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold px-6 py-3 rounded-xl text-sm transition-all flex items-center gap-2 shadow-lg shadow-emerald-500/10 disabled:opacity-50 shrink-0"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
          <span>Search</span>
        </button>
      </div>

      {/* Top-K Slider Settings Row */}
      <div className="flex items-center justify-between px-1 pt-1 border-t border-white/[0.06] text-xs text-slate-400 font-mono">
        <div className="flex items-center gap-2">
          <SlidersHorizontal size={13} className="text-emerald-400" />
          <span>Top-$k$ Vector Matches:</span>
        </div>
        <div className="flex items-center gap-3 w-48">
          <input
            type="range"
            min="1"
            max="20"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="w-full accent-emerald-500 bg-slate-800 h-1.5 rounded-lg appearance-none cursor-pointer"
          />
          <span className="text-emerald-400 font-bold min-w-[1.25rem] text-right">{topK}</span>
        </div>
      </div>
    </div>
  )
}