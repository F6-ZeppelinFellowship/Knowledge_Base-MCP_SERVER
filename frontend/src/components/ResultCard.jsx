import { FileText } from 'lucide-react'

const HIGH_THRESHOLD = 0.85

function confidenceLevel(score) {
  return score >= HIGH_THRESHOLD ? 'high' : 'mid'
}

function ScoreBadge({ score }) {
  const level = confidenceLevel(score)
  const pct = Math.round(score * 100)

  return (
    <div className="relative flex items-center justify-center shrink-0">
      <span
        className={`absolute inline-flex h-9 w-9 rounded-full opacity-20 animate-pulse-ring ${
          level === 'high' ? 'bg-match-high' : 'bg-match-mid'
        }`}
      />
      <div
        className={`relative w-9 h-9 rounded-full flex items-center justify-center font-mono text-[11px] font-medium ${
          level === 'high'
            ? 'bg-match-high/15 text-match-high border border-match-high/30'
            : 'bg-match-mid/15 text-match-mid border border-match-mid/30'
        }`}
      >
        {pct}
      </div>
    </div>
  )
}

export default function ResultCard({ result }) {
  const { chunk_text, score, source } = result

  return (
    <article className="glass-card p-4 sm:p-5 flex gap-4">
      <ScoreBadge score={score} />

      <div className="min-w-0 flex-1">
        <p className="text-sm leading-relaxed text-slate-200">{chunk_text}</p>

        <div className="flex items-center gap-1.5 mt-3 text-xs text-slate-500">
          <FileText size={12} className="shrink-0" />
          <span className="truncate">{source?.filename}</span>
          {typeof source?.page === 'number' && (
            <>
              <span className="text-slate-700">·</span>
              <span className="font-mono">p.{source.page}</span>
            </>
          )}
        </div>
      </div>
    </article>
  )
}
