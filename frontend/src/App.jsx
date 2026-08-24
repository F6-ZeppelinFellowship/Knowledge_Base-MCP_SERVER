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
  
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(5)
  const [searchResults, setSearchResults] = useState([])
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

    try {
      const results = await search.query(query, topK)
      setSearchResults(Array.isArray(results) ? results : results?.results || [])
    } catch (err) {
      console.error('Search query failed:', err)
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  if (!isAuthenticated) {
    return <LandingPage onAuthSuccess={handleAuthSuccess} />
  }

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-[#0B0F17] text-slate-100 font-sans antialiased relative overflow-hidden">
      {/* Background Glows */}
      <div className="absolute top-1/4 left-1/3 w-[500px] h-[500px] bg-emerald-500/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-10 right-10 w-[400px] h-[400px] bg-cyan-500/5 rounded-full blur-[120px] pointer-events-none" />

      {/* Structured Sidebar */}
      <Sidebar
        userEmail={userEmail}
        docs={docsList}
        uploads={uploads}
        onUpload={handleUpload}
        onDelete={handleDeleteDocument}
        onLogout={handleLogout}
      />

      {/* Centered Main Workspace Content */}
      <main className="flex-1 flex flex-col justify-center items-center min-w-0 p-6 md:p-12 z-10 min-h-screen">
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
          {hasSearched ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between px-1">
                <p className="text-xs uppercase tracking-wide text-slate-500 font-mono font-medium">
                  {isSearching ? 'Querying Vector Engine...' : `Results (${searchResults.length})`}
                </p>
              </div>

              {searchResults.length === 0 && !isSearching ? (
                <div className="bg-[#121824]/60 border border-white/10 rounded-2xl p-8 text-center text-slate-400 text-sm">
                  No matching vector context found. Try increasing the top-$k$ limit or rephrasing your search query.
                </div>
              ) : (
                searchResults.map((result, idx) => (
                  <ResultCard key={result.chunk_id || result.id || idx} result={result} />
                ))
              )}
            </div>
          ) : (
            <div className="bg-[#121824]/40 border border-dashed border-white/10 rounded-2xl p-10 text-center space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/20">
                <Sparkles size={20} />
              </div>
              <h3 className="text-sm font-semibold text-slate-200">Ready for semantic search</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                Enter a query above to calculate dense vector embeddings and fetch nearest neighbors from Qdrant.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}