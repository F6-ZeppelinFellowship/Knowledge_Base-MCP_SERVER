import { useState } from 'react'
import { X, Lock, Mail, Loader2, ScanSearch } from 'lucide-react'
import { auth } from '../api/client'

export default function AuthModal({ onAuthenticated, onClose }) {
  const [tab, setTab] = useState('login') // 'login' | 'signup'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const isSignup = tab === 'signup'

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (isSignup && password !== confirmPassword) {
      setError("Passwords don't match.")
      return
    }

    setLoading(true)
    try {
      if (isSignup) {
        await auth.signup(email, password)
      } else {
        await auth.login(email, password)
      }
      
      // Notify parent component on success
      if (onAuthenticated) {
        onAuthenticated(email)
      }
    } catch (err) {
      console.error('Auth Error Details:', err?.response?.data)
      const detail = err?.response?.data?.detail

      // Handle FastAPI string vs validation object list details
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(', '))
      } else if (typeof detail === 'string') {
        setError(detail)
      } else {
        setError('Authentication failed. Please verify server is running on port 8000.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-base-950/80 backdrop-blur-sm p-4">
      <div className="glass-card w-full max-w-sm p-6 relative animate-in">
        {onClose && (
          <button
            onClick={onClose}
            aria-label="Close"
            className="absolute right-4 top-4 text-slate-500 hover:text-slate-200 transition-colors"
          >
            <X size={18} />
          </button>
        )}

        {/* Header branding */}
        <div className="flex items-center gap-2 mb-6">
          <div className="w-8 h-8 rounded-lg bg-match-high/15 flex items-center justify-center">
            <ScanSearch size={16} className="text-match-high" />
          </div>
          <span className="font-display font-semibold text-lg text-slate-100">Knowledge Base AI</span>
        </div>

        {/* Tab Switcher */}
        <div className="flex gap-1 p-1 mb-6 rounded-lg bg-base-900/80 border border-white/5">
          {['login', 'signup'].map((t) => (
            <button
              key={t}
              onClick={() => {
                setTab(t)
                setError('')
              }}
              className={`flex-1 rounded-md py-1.5 text-sm font-medium transition-colors ${
                tab === t ? 'bg-match-high text-base-950' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {t === 'login' ? 'Log in' : 'Sign up'}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label htmlFor="email" className="sr-only">Email</label>
            <div className="relative">
              <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="input-field pl-9"
              />
            </div>
          </div>

          <div>
            <label htmlFor="password" className="sr-only">Password</label>
            <div className="relative">
              <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                id="password"
                type="password"
                required
                minLength={6}
                autoComplete={isSignup ? 'new-password' : 'current-password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className="input-field pl-9"
              />
            </div>
          </div>

          {isSignup && (
            <div>
              <label htmlFor="confirm" className="sr-only">Confirm password</label>
              <div className="relative">
                <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  id="confirm"
                  type="password"
                  required
                  minLength={6}
                  autoComplete="new-password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm password"
                  className="input-field pl-9"
                />
              </div>
            </div>
          )}

          {error && (
            <p role="alert" className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2 mt-2">
            {loading && <Loader2 size={15} className="animate-spin" />}
            {isSignup ? 'Create account' : 'Log in'}
          </button>
        </form>
      </div>
    </div>
  )
}