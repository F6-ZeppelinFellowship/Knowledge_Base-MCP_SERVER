import { useCallback, useRef, useState } from 'react'
import { UploadCloud, FileText, Trash2, LogOut, ScanSearch, Loader2 } from 'lucide-react'

const ACCEPTED = '.pdf,.md,.markdown,.txt'

function formatBytes(bytes) {
  if (!bytes && bytes !== 0) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function Sidebar({ userEmail, docs, uploads, onUpload, onDelete, onLogout }) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)

  const handleFiles = useCallback(
    (fileList) => {
      Array.from(fileList).forEach((file) => onUpload(file))
    },
    [onUpload],
  )

  return (
    <aside className="w-full md:w-72 shrink-0 flex flex-col gap-4 md:h-screen md:sticky md:top-0 p-4 md:py-6">
      {/* Brand */}
      <div className="flex items-center gap-2 px-1">
        <div className="w-8 h-8 rounded-lg bg-match-high/15 flex items-center justify-center">
          <ScanSearch size={16} className="text-match-high" />
        </div>
        <span className="font-display font-semibold text-lg text-slate-100">Recall</span>
      </div>

      {/* Account status */}
      <div className="glass-card px-3.5 py-3 flex items-center justify-between">
        <div className="min-w-0">
          <p className="text-[11px] uppercase tracking-wide text-slate-500 font-medium">Signed in as</p>
          <p className="text-sm text-slate-200 truncate">{userEmail}</p>
        </div>
        <button
          onClick={onLogout}
          aria-label="Log out"
          className="text-slate-500 hover:text-red-400 transition-colors shrink-0 p-1.5 rounded-md hover:bg-white/5"
        >
          <LogOut size={16} />
        </button>
      </div>

      {/* Dropzone */}
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setIsDragging(false)
          handleFiles(e.dataTransfer.files)
        }}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
        className={`glass-card border-dashed cursor-pointer px-4 py-6 flex flex-col items-center text-center gap-2 transition-colors ${
          isDragging ? 'border-match-high/60 bg-match-high/[0.04]' : 'hover:border-white/15'
        }`}
      >
        <UploadCloud size={22} className={isDragging ? 'text-match-high' : 'text-slate-500'} />
        <p className="text-sm text-slate-300">
          <span className="text-match-high font-medium">Choose files</span> or drag them here
        </p>
        <p className="text-[11px] text-slate-500">PDF, Markdown, or TXT</p>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          multiple
          className="hidden"
          onChange={(e) => {
            if (e.target.files?.length) handleFiles(e.target.files)
            e.target.value = ''
          }}
        />
      </div>

      {/* Upload progress */}
      {uploads.length > 0 && (
        <div className="space-y-2">
          {uploads.map((u) => (
            <div key={u.id} className="px-3.5 py-2.5 rounded-lg bg-base-800/50 border border-white/[0.06]">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="truncate text-slate-300 max-w-[70%]">{u.name}</span>
                <span className="text-slate-500 shrink-0">
                  {u.status === 'error' ? 'Failed' : `${u.progress}%`}
                </span>
              </div>
              <div className="h-1 rounded-full bg-base-900 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-200 ${
                    u.status === 'error' ? 'bg-red-500' : 'bg-match-high'
                  }`}
                  style={{ width: `${u.status === 'error' ? 100 : u.progress}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Document list */}
      <div className="flex-1 min-h-0 flex flex-col">
        <div className="flex items-center justify-between px-1 mb-2">
          <p className="text-[11px] uppercase tracking-wide text-slate-500 font-medium">
            Documents
          </p>
          <span className="text-[11px] text-slate-600 font-mono">{docs.length}</span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-1.5 pr-0.5">
          {docs.length === 0 ? (
            <p className="text-xs text-slate-600 px-1 py-3 leading-relaxed">
              Nothing indexed yet. Upload a document to start building your knowledge base.
            </p>
          ) : (
            docs.map((doc) => (
              <div
                key={doc.id}
                className="group flex items-center gap-2.5 px-3 py-2.5 rounded-lg hover:bg-white/[0.04] transition-colors"
              >
                <div className="w-7 h-7 rounded-md bg-base-700/70 flex items-center justify-center shrink-0">
                  {doc.status === 'processing' ? (
                    <Loader2 size={13} className="text-amber-400 animate-spin" />
                  ) : (
                    <FileText size={13} className="text-slate-400" />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-slate-200 truncate">{doc.filename}</p>
                  <p className="text-[11px] text-slate-500 font-mono">
                    {doc.status === 'processing' ? 'Indexing…' : formatBytes(doc.size_bytes)}
                  </p>
                </div>
                <button
                  onClick={() => onDelete(doc.id)}
                  aria-label={`Delete ${doc.filename}`}
                  className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-all p-1 rounded"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </aside>
  )
}
