import { useState } from 'react'
import { Search, Shield, Zap, Database, ArrowRight, Lock, Mail, Key, BrainCircuit } from 'lucide-react'
import { auth } from '../api/client'

export default function LandingPage({ onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        await auth.login(email, password)
      } else {
        await auth.register(email, password)
      }
      onAuthSuccess(email)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Authentication failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 flex flex-col justify-between p-6 sm:p-10 relative overflow-hidden font-sans">
      {/* Background Glows */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header Branding */}
      <header className="max-w-6xl w-full mx-auto flex items-center gap-2.5 z-10 pb-6">
        <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
          <BrainCircuit size={22} />
        </div>
        <span className="text-xl font-bold tracking-tight text-white">Recall</span>
      </header>

      {/* Hero & Form Grid */}
      <main className="max-w-6xl w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 items-center z-10 py-6">
        
        {/* Left Hero Section */}
        <div className="lg:col-span-7 space-y-8">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono font-medium tracking-wide">
            <Zap size={13} />
            <span>PERSONAL VECTOR RECALL ENGINE</span>
          </div>

          <div className="space-y-4">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
              Recall standardizes knowledge retrieval.
            </h1>
            <p className="text-slate-400 text-base sm:text-lg leading-relaxed max-w-xl">
              Upload your documents, generate dense Qdrant vector embeddings, and search your personal data with natural language queries.
            </p>
          </div>

          {/* Key Feature Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] space-y-2">
              <Database size={18} className="text-emerald-400" />
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Qdrant DB</h3>
              <p className="text-xs text-slate-400 leading-normal">Fast local vector indexing.</p>
            </div>
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] space-y-2">
              <Search size={18} className="text-cyan-400" />
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Semantic Search</h3>
              <p className="text-xs text-slate-400 leading-normal">Query meaning over text match.</p>
            </div>
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] space-y-2">
              <Shield size={18} className="text-emerald-400" />
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Scoped Payloads</h3>
              <p className="text-xs text-slate-400 leading-normal">Filtered user data privacy.</p>
            </div>
          </div>
        </div>

        {/* Right Auth Card */}
        <div className="lg:col-span-5">
          <div className="bg-[#121824]/90 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">
                {isLogin ? 'Sign In to Recall' : 'Create Account'}
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                {isLogin
                  ? 'Access your personal document knowledge base.'
                  : 'Register an account to start chunking and indexing files.'}
              </p>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs text-slate-300 font-medium">Username / Email</label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="user@domain.com"
                    className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-10 py-2.5 text-sm text-slate-100 placeholder:text-slate-600 outline-none focus:border-emerald-500/50 transition-colors"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-slate-300 font-medium">Password</label>
                <div className="relative">
                  <Key size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-10 py-2.5 text-sm text-slate-100 placeholder:text-slate-600 outline-none focus:border-emerald-500/50 transition-colors"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold py-2.5 rounded-xl text-sm transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/10 disabled:opacity-50"
              >
                {loading ? 'Processing...' : isLogin ? 'Sign In' : 'Register Account'}
                <ArrowRight size={16} />
              </button>
            </form>

            <div className="pt-4 border-t border-white/[0.06] text-center">
              <p className="text-xs text-slate-400">
                {isLogin ? "Don't have an account?" : 'Already registered?'}
                <button
                  type="button"
                  onClick={() => {
                    setIsLogin(!isLogin)
                    setError('')
                  }}
                  className="ml-1.5 font-semibold text-emerald-400 hover:underline"
                >
                  {isLogin ? 'Register here' : 'Sign in here'}
                </button>
              </p>
            </div>
          </div>
        </div>

      </main>

      <footer className="max-w-6xl w-full mx-auto text-xs text-slate-600 text-center z-10 pt-6">
        Recall • Vector Search System
      </footer>
    </div>
  )
}