import { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import SearchBar from './components/SearchBar'
import ResultCard from './components/ResultCard'
import LandingPage from './components/LandingPage'
import { auth, documents, search } from './api/client'
import { Activity, Sparkles } from 'lucide-react'

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(auth.isAuthenticated())
  const [userEmail, setUserEmail] = useState(auth.getUserEmail())
  const [docsList, setDocsList] = useState([])
  const [uploads, setUploads] = useState([])
  

  // Inside App.jsx
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(5)
  const [searchResults, setSearchResults] = useState([])
  const [generatedAnswer, setGeneratedAnswer] = useState('') // New state
  const [isSearching, setIsSearching] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  const fetchDocuments = useCallback(async () => {
    if (!isAuthenticated) return
    try {
      const data = await documents.list()
      setDocsList(Array.isArray(data) ? data : [])
    } catch (err) {
      console.error('Failed to fetch document list:', err)
      setDocsList([])
    }
  }, [isAuthenticated])

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  const handleAuthSuccess = (email) => {
    setIsAuthenticated(true)
    setUserEmail(email)
  }

  const handleLogout = () => {
    auth.logout()
    setIsAuthenticated(false)
    setUserEmail('')
    setDocsList([])
    setSearchResults([])
    setHasSearched(false)
  }

  const handleUpload = async (file) => {
    const uploadId = `${file.name}-${Date.now()}`
    setUploads((prev) => [...prev, { id: uploadId, name: file.name, progress: 0, status: 'uploading' }])

    try {
      await documents.upload(file, (progress) => {
        setUploads((prev) => prev.map((item) => item.id === uploadId ? { ...item, progress } : item))
      })
      setUploads((prev) => prev.map((item) => item.id === uploadId ? { ...item, progress: 100, status: 'complete' } : item))
      await fetchDocuments()
      setTimeout(() => setUploads((prev) => prev.filter((item) => item.id !== uploadId)), 2000)
    } catch (err) {
      console.error('Upload failed:', err)
      setUploads((prev) => prev.map((item) => item.id === uploadId ? { ...item, status: 'error' } : item))
    }
  }

  const handleDeleteDocument = async (documentId) => {
    try {
      await documents.remove(documentId)
      await fetchDocuments()
    } catch (err) {
      console.error('Failed to delete document:', err)
    }
  }



const handleSearch = async () => {
  if (!query.trim()) return
  setIsSearching(true)
  setHasSearched(true)
  setGeneratedAnswer('') // Reset previous answer

  try {
    const data = await search.query(query, topK)
    // FastAPI returns { answer: "...", sources: [...] }
    setGeneratedAnswer(data.answer || '')
    setSearchResults(data.sources || [])
  } catch (err) {
    console.error('Search query failed:', err)
    setGeneratedAnswer('An error occurred while generating the answer.')
    setSearchResults([])
  } finally {
    setIsSearching(false)
  }
}

  if (!isAuthenticated) {
    return <LandingPage onAuthSuccess={handleAuthSuccess} />
  }

  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 font-sans antialiased relative">
      {/* Background Glows */}
      <div className="fixed top-1/4 left-1/3 w-[500px] h-[500px] bg-emerald-500/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="fixed bottom-10 right-10 w-[400px] h-[400px] bg-cyan-500/5 rounded-full blur-[120px] pointer-events-none" />

      {/* Fixed Sidebar */}
      <Sidebar
        userEmail={userEmail}
        docs={docsList}
        uploads={uploads}
        onUpload={handleUpload}
        onDelete={handleDeleteDocument}
        onLogout={handleLogout}
      />

      {/* Main Workspace Content (Shifted right by Sidebar's width w-80 / md:ml-80) */}
      <main className="md:ml-80 min-h-screen flex flex-col items-center p-6 md:p-12 z-10 relative">
        <div className="max-w-3xl w-full space-y-8 my-auto">
          
          {/* Header Status Section */}
          <div className="flex items-center justify-between pb-2 border-b border-white/[0.08]">
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Search Workspace</h1>
              <p className="text-xs text-slate-400 mt-1">
                Query index across <span className="text-emerald-400 font-semibold">{docsList.length}</span> ingested document{docsList.length === 1 ? '' : 's'}.
              </p>
            </div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
              <Activity size={12} />
              Index Online
            </span>
          </div>

          {/* Search Box */}
          <SearchBar
            query={query}
            setQuery={setQuery}
            topK={topK}
            setTopK={setTopK}
            onSearch={handleSearch}
            loading={isSearching}
          />

          {/* Results Container */}
{/* Results Container */}
{hasSearched && (
  <div className="space-y-6">
    
    {/* 1. AI Synthesized Answer Card */}
    <div className="bg-[#121824] border border-emerald-500/30 rounded-2xl p-6 space-y-3 shadow-lg shadow-emerald-950/20">
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-semibold uppercase tracking-wider">
          <Sparkles size={16} />
          AI Synthesized Answer
        </div>
        <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/20 font-mono">
          RAG Pipeline
        </span>
      </div>

      {isSearching ? (
        <div className="flex items-center gap-3 text-slate-400 text-sm py-2">
          <div className="w-4 h-4 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
          <span>Reading context chunks & synthesizing answer...</span>
        </div>
      ) : (
        <p className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">
          {generatedAnswer || "No answer could be generated."}
        </p>
      )}
    </div>

    {/* 2. Source Context Chunks Header */}
    <div className="flex items-center justify-between px-1">
      <p className="text-xs uppercase tracking-wide text-slate-500 font-mono font-medium">
        {isSearching ? 'Fetching sources...' : `Retrieved Context Chunks (${searchResults.length})`}
      </p>
    </div>

    {/* 3. Source Cards */}
    {searchResults.length === 0 && !isSearching ? (
      <div className="bg-[#121824]/60 border border-white/10 rounded-2xl p-8 text-center text-slate-400 text-sm">
        No matching vector context found in your documents.
      </div>
    ) : (
      searchResults.map((result, idx) => (
        <ResultCard key={result.chunk_id || result.id || idx} result={result} />
      ))
    )}
  </div>
)}
        </div>
      </main>
    </div>
  )
}