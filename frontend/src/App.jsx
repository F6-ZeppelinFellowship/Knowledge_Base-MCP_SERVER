import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import SearchBar from './components/SearchBar'
import ResultCard from './components/ResultCard'
import { auth, documents, search } from './api/client'
import AuthModal from './components/AuthModal'
import { Sparkles, Search as SearchIcon, Server } from 'lucide-react'

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(auth.isAuthenticated())
  const [userEmail, setUserEmail] = useState(auth.getUserEmail())
  const [activeTab, setActiveTab] = useState('search') // 'search' | 'mcp'
  
  const [docs, setDocs] = useState([])
  const [uploads, setUploads] = useState([])
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(5)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isAuthenticated) {
      loadDocuments()
    }
  }, [isAuthenticated])

  const loadDocuments = async () => {
    try {
      const data = await documents.list()
      setDocs(data)
    } catch (err) {
      console.error("Failed to load documents", err)
    }
  }

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const res = await search.query(query, topK)
      setResults(res)
    } catch (err) {
      console.error("Search failed", err)
    } finally {
      setLoading(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <AuthModal
        onAuthenticated={(email) => {
          setUserEmail(email)
          setIsAuthenticated(true)
        }}
      />
    )
  }

  return (
    <div className="min-h-screen bg-base-950 flex flex-col md:flex-row text-slate-100">
      {/* Sidebar: Ingestion & Document List (Member 1) */}
      <Sidebar
        userEmail={userEmail}
        docs={docs}
        uploads={uploads}
        onUpload={(file) => { /* handle file upload flow */ }}
        onDelete={async (id) => { await documents.remove(id); loadDocuments() }}
        onLogout={() => { auth.logout(); setIsAuthenticated(false) }}
      />

      {/* Main Workspace Area */}
      <main className="flex-1 p-4 md:p-8 max-w-5xl mx-auto w-full flex flex-col gap-6">
        {/* Navigation Tabs for Team Integrations */}
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
          <div>
            <h1 className="text-xl font-semibold text-slate-100">Workspace</h1>
            <p className="text-xs text-slate-400">Search indexed vector chunks or interface with MCP tool servers.</p>
          </div>
          <div className="flex gap-2 bg-base-900 p-1 rounded-lg border border-white/5">
            <button
              onClick={() => setActiveTab('search')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                activeTab === 'search' ? 'bg-match-high/20 text-match-high' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <SearchIcon size={14} /> Search Index
            </button>
            <button
              onClick={() => setActiveTab('mcp')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                activeTab === 'mcp' ? 'bg-match-high/20 text-match-high' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Server size={14} /> MCP Tools (Member 2)
            </button>
          </div>
        </div>

        {/* Tab 1: Member 3 Search Interface */}
        {activeTab === 'search' && (
          <div className="space-y-6">
            <SearchBar
              query={query}
              setQuery={setQuery}
              topK={topK}
              setTopK={setTopK}
              onSearch={handleSearch}
              loading={loading}
            />

            {/* Results Grid / List */}
            <div className="space-y-3">
              {results.length > 0 ? (
                results.map((res, idx) => <ResultCard key={idx} result={res} />)
              ) : (
                <div className="text-center py-12 text-slate-500 text-sm">
                  {loading ? 'Searching Qdrant collection...' : 'No query executed. Type a search above to query document vectors.'}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 2: Slot for Member 2's MCP integration */}
        {activeTab === 'mcp' && (
          <div className="glass-card p-6 rounded-xl text-center text-slate-400 text-sm space-y-2">
            <Sparkles className="mx-auto text-match-high mb-2" size={24} />
            <p className="font-medium text-slate-200">Model Context Protocol Server Ready</p>
            <p className="text-xs max-w-md mx-auto text-slate-500">
              Member 2 can attach MCP agent execution interfaces, prompt templates, or custom tool inspection cards here.
            </p>
          </div>
        )}
      </main>
    </div>
  )
}