# Personal Knowledge-Base MCP Server & Web App

> **F6-Zeppelin Fellowship — Project 3**  
> A multi-tenant Model Context Protocol (MCP) server and web application enabling semantic search over personal document corpora backed by Qdrant vector search and FastMCP.

---

## 🚀 Overview

Static keyword search fails when notes, research papers, and technical documents use different wording for the same concepts. This project implements a protocol-level **FastMCP server** paired with a **Qdrant Vector Database** to enable context-aware semantic search over real-world documents.

The system supports dual modes of interaction:
1. **MCP Client Integration**: Native tools callable from MCP-compliant clients like Claude Desktop or Claude Code.
2. **Multi-Tenant Web UI**: A web dashboard providing isolated document management, uploading, and search capabilities per user.

---

## ✨ Key Features

* **Protocol-Level Integration (`FastMCP`)**: Exposes structured MCP tools (`search_notes`, `get_document`, `list_sources`) for native AI agent invocation.
* **Multi-Tenant Isolation**: Payload-level tenant isolation in Qdrant ensures document chunks and search results are strictly scoped per user.
* **Strict Relevance Cutoff**: Rejects low-confidence vector matches below similarity thresholds to prevent low-relevance hallucination propagation.
* **Automated Ingestion Pipeline**: Handles PDF, Markdown, and TXT parsing, dynamic chunking, and embedding generation.
* **Quantitative Retrieval Benchmarking**: Hand-labeled evaluation suite tracking Mean Reciprocal Rank (MRR) and Precision@K across test queries.

---

## 🛠️ Architecture & Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Protocol** | FastMCP (Python) | Tool registry and JSON-RPC over STDIO / HTTP transport |
| **Backend API** | FastAPI | User authentication (JWT), file upload, REST search endpoints |
| **Vector DB** | Qdrant | HNSW similarity search with payload-based user isolation |
| **Embeddings** | sentence-transformers / OpenAI | Dense vectorization of document chunks |
| **Frontend** | React / Tailwind CSS | Web dashboard for uploading documents and testing queries |

---

## 📊 Evaluation & Metrics

| Metric | Target | Result |
| :--- | :--- | :--- |
| **Precision@3** | ≥ 80% | *TBD* |
| **MRR (Mean Reciprocal Rank)** | ≥ 0.85 | *TBD* |
| **Relevance Threshold** | Cosine ≥ 0.72 | Enforced |

---

## ⚡ Quick Start

### 1. Environment Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure Claude Desktop (claude_desktop_config.json)
```JSON
{
  "mcpServers": {
    "personal-kb": {
      "command": "python",
      "args": ["-m", "app.mcp_server.server"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_API_KEY": "your-api-key"
      }
    }
  }
}
```

## 📂 Repository Structure

```bash
KNOWLEDGE_BASE-MCP_SERVER/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints (Auth, Documents, Search)
│   │   ├── core/            # App configuration & JWT security settings
│   │   ├── db/              # Qdrant vector database initialization & schemas
│   │   ├── eval/            # Precision@K and MRR benchmark scripts
│   │   ├── mcp_server/      # FastMCP server definition & tool implementations
│   │   └── services/        # Ingestion, embedding, & similarity search services
│   ├── tests/               # Backend API and retrieval test suite
│   ├── main.py              # Application entry point
│   ├── requirements.txt     # Python backend dependencies
│   └── .env.example         # Template for environment variables
├── data/
│   └── sample_docs/         # Document corpus for local testing
├── docs/                    # Architecture diagrams & project documentation
├── frontend/                # React / Tailwind web application for multi-user management
│   └── src/
│       ├── components/      # UI components (Uploaders, Search bar, Score badges)
│       ├── context/         # Auth & Session state providers
│       ├── pages/           # Document dashboard & Search playground
│       └── services/        # API client bindings
├── .gitignore               # Ignored files (venvs, keys, vector storage)
├── docker-compose.yml       # Local Qdrant & FastAPI orchestration
└── README.md                # Project documentation 
```


