import { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import SearchBar from './components/SearchBar'
import ResultCard from './components/ResultCard'
import AuthModal from './components/AuthModal'
import { auth, documents, search } from './api/client'

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(auth.isAuthenticated())
  const [userEmail, setUserEmail] = useState(auth.getUserEmail())
  const [docsList, setDocsList] = useState([])
  const [uploads, setUploads] = useState([])
  
  // Search state
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(5)
  const [searchResults, setSearchResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  // Load user documents on mount / auth state change
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

  // Auth Handlers
  const handleLoginSuccess = (email) => {
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

  // Upload Handler with progress tracking & auto-refresh
  const handleUpload = async (file) => {
    const uploadId = `${file.name}-${Date.now()}`
    
    setUploads((prev) => [
      ...prev,
      { id: uploadId, name: file.name, progress: 0, status: 'uploading' },
    ])

    try {
      await documents.upload(file, (progress) => {
        setUploads((prev) =>
          prev.map((item) =>
            item.id === uploadId ? { ...item, progress } : item
          )
        )
      })

      setUploads((prev) =>
        prev.map((item) =>
          item.id === uploadId ? { ...item, progress: 100, status: 'complete' } : item
        )
      )

      await fetchDocuments()

      setTimeout(() => {
        setUploads((prev) => prev.filter((item) => item.id !== uploadId))
      }, 2000)
    } catch (err) {
      console.error('Upload failed:', err)
      setUploads((prev) =>
        prev.map((item) =>
          item.id === uploadId ? { ...item, status: 'error' } : item
        )
      )
    }
  }

  // Delete Document Handler
  const handleDeleteDocument = async (documentId) => {
    try {
      await documents.remove(documentId)
      await fetchDocuments()
    } catch (err) {
      console.error('Failed to delete document:', err)
    }
  }

  // Search Handler
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
    return <AuthModal onAuthSuccess={handleLoginSuccess} />
  }

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-base-900 text-slate-100 font-sans antialiased">
      {/* Sidebar */}
      <Sidebar
        userEmail={userEmail}
        docs={docsList}
        uploads={uploads}
        onUpload={handleUpload}
        onDelete={handleDeleteDocument}
        onLogout={handleLogout}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 px-4 py-6 md:px-8 md:py-8">
        <div className="max-w-4xl mx-auto w-full space-y-6">
          <SearchBar
            query={query}
            setQuery={setQuery}
            topK={topK}
            setTopK={setTopK}
            onSearch={handleSearch}
            loading={isSearching}
          />

          {/* Search Results Display */}
          {hasSearched && (
            <div className="space-y-4">
              <p className="text-xs uppercase tracking-wide text-slate-500 font-medium px-1">
                {isSearching ? 'Searching Vector Database...' : `Results (${searchResults.length})`}
              </p>

              {searchResults.length === 0 && !isSearching ? (
                <div className="glass-card p-8 text-center text-slate-400">
                  No matching vector context found for standard query thresholds.
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