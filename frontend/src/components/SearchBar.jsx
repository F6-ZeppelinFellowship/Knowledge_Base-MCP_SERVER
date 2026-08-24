import { Search, SlidersHorizontal, Loader2 } from 'lucide-react'

export default function SearchBar({ query, setQuery, topK, setTopK, onSearch, loading }) {
  function handleSubmit(e) {
    e.preventDefault()
    if (query.trim()) onSearch()
  }

  return (
    <form onSubmit={handleSubmit} className="glass-card p-3 sm:p-4 relative overflow-hidden">
      {/* Signature: a scan-line sweep while a query is in flight, evoking the
          vector index being swept for matches. */}
      {loading && (
        <div className="absolute inset-x-0 top-0 h-[2px] overflow-hidden">
          <div className="w-1/3 h-full bg-gradient-to-r from-transparent via-match-high to-transparent animate-scan" />
        </div>
      )}

      <div className="flex items-center gap-3">
        <Search size={17} className="text-slate-500 shrink-0" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask something your notes already know…"
          className="flex-1 bg-transparent outline-none text-sm sm:text-base text-slate-100 placeholder:text-slate-500"
        />
        <button type="submit" disabled={loading || !query.trim()} className="btn-primary flex items-center gap-1.5 shrink-0">
          {loading ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />}
          <span className="hidden sm:inline">Search</span>
        </button>
      </div>

      <div className="flex items-center gap-3 mt-3.5 pt-3.5 border-t border-white/[0.06]">
        <SlidersHorizontal size={13} className="text-slate-500 shrink-0" />
        <label htmlFor="topk" className="text-xs text-slate-500 shrink-0">
          Results
        </label>
        <input
          id="topk"
          type="range"
          min={1}
          max={10}
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          className="flex-1 accent-match-high h-1 cursor-pointer"
        />
        <span className="text-xs font-mono text-slate-300 w-6 text-right shrink-0">{topK}</span>
      </div>
    </form>
  )
}
