import { BrainCircuit, Upload, FileText, Trash2, LogOut, HardDrive } from 'lucide-react'

export default function Sidebar({ userEmail, docs, uploads, onUpload, onDelete, onLogout }) {
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0])
    }
  }

  return (
    <aside className="w-80 fixed left-0 top-0 h-screen bg-[#121824]/80 backdrop-blur-xl border-r border-white/10 flex flex-col justify-between p-6 z-20 shrink-0">
      <div className="space-y-6 flex-1 flex flex-col min-h-0">
        
        {/* Brand Header */}
        <div className="flex items-center gap-2.5 pb-4 border-b border-white/[0.08] shrink-0">
          <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <BrainCircuit size={22} />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">Recall</span>
        </div>

        {/* File Upload Zone */}
        <div className="shrink-0">
          <label className="group relative flex flex-col items-center justify-center p-5 border-2 border-dashed border-white/15 hover:border-emerald-500/50 rounded-2xl cursor-pointer bg-white/[0.02] hover:bg-emerald-500/[0.03] transition-all text-center">
            <input type="file" className="hidden" onChange={handleFileChange} accept=".pdf,.md,.txt" />
            <div className="p-2.5 rounded-full bg-white/[0.05] group-hover:bg-emerald-500/20 text-slate-300 group-hover:text-emerald-400 transition-colors mb-2">
              <Upload size={18} />
            </div>
            <span className="text-xs font-semibold text-slate-200">
              <span className="text-emerald-400">Choose files</span> or drag here
            </span>
            <span className="text-[10px] text-slate-500 mt-1 font-mono">PDF, Markdown, or TXT</span>
          </label>

          {/* Uploading Progress Items */}
          {uploads.length > 0 && (
            <div className="mt-3 space-y-2 max-h-32 overflow-y-auto custom-scrollbar">
              {uploads.map((u) => (
                <div key={u.id} className="p-2.5 bg-white/[0.03] border border-white/10 rounded-xl space-y-1 text-xs">
                  <div className="flex justify-between text-slate-300 truncate">
                    <span className="truncate">{u.name}</span>
                    <span className="font-mono text-emerald-400">{u.progress}%</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1 overflow-hidden">
                    <div className="bg-emerald-500 h-1 transition-all duration-300" style={{ width: `${u.progress}%` }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Document List Section - Fixed Height Container with Overflow Scroll */}
        <div className="flex-1 min-h-0 flex flex-col space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 uppercase tracking-wider px-1 shrink-0">
            <span className="flex items-center gap-1.5"><HardDrive size={13} /> Documents</span>
            <span className="px-1.5 py-0.5 rounded bg-white/[0.05] text-[10px]">{docs.length}</span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-1.5 pr-1 custom-scrollbar min-h-0">
            {docs.length === 0 ? (
              <p className="text-xs text-slate-500 italic p-3 text-center">No documents uploaded yet.</p>
            ) : (
              docs.map((doc) => {
  const docId = doc.document_id || doc.id || doc.filename
  return (
    <div
      key={docId}
      className="group flex items-center justify-between p-2.5 rounded-xl bg-white/[0.02] hover:bg-white/[0.06] border border-white/[0.04] transition-all text-xs"
    >
      <div className="flex items-center gap-2.5 min-w-0 pr-2">
        <FileText size={15} className="text-emerald-400 shrink-0" />
        <span className="text-slate-300 truncate font-medium">{doc.filename || doc.name}</span>
      </div>
      <button
        onClick={() => onDelete(docId)}
        className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-opacity p-1 shrink-0"
        title="Delete document"
      >
        <Trash2 size={14} />
      </button>
    </div>
  )
})
            )}
          </div>
        </div>
      </div>

      {/* Profile & Logout Footer */}
      <div className="pt-4 border-t border-white/[0.08] flex items-center justify-between shrink-0">
        <div className="min-w-0 pr-2">
          <p className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Signed in as</p>
          <p className="text-xs font-medium text-slate-200 truncate">{userEmail}</p>
        </div>
        <button
          onClick={onLogout}
          className="p-2 rounded-xl bg-white/[0.04] hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition-colors"
          title="Sign Out"
        >
          <LogOut size={16} />
        </button>
      </div>
    </aside>
  )
}