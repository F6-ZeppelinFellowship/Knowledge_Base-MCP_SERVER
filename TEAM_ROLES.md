# 👥 Team Roles & Task Division

## Project: Personal Knowledge-Base MCP Server & Web App
**Timeline:** 6 Days  
**Team Allocation:** 3 Engineers (Equal AI + Balanced Software Engineering Distribution)

---

## 🎯 Division Summary

To avoid bottlenecks and ensure everyone gets equal experience across **AI Engineering**, **Backend Development**, and **Frontend UI**, tasks are assigned vertically by feature layer:

| Engineer | Core Focus Area | AI/GenAI Ownership | Software Engineering Ownership |
| :--- | :--- | :--- | :--- |
| **Engineer 1** | **Vector DB & Ingestion Engine** | Ingestion pipeline, dynamic text chunking, and Qdrant similarity search engine | Core storage layer, file parsers (`.pdf`, `.md`, `.txt`), and vector schemas |
| **Engineer 2** | **MCP Protocol & Evaluation** | FastMCP server tools, Claude Desktop wire-up, and retrieval benchmarking (`Precision@K`, `MRR`) | FastMCP STDIO execution, evaluation scripts, and benchmark reporting |
| **Engineer 3** | **Multi-Tenant API & Frontend UI** | Multi-tenant payload filtering, score confidence badges, and citation visualizer | FastAPI REST API, JWT auth, and React management dashboard |

---

## 📋 Detailed Responsibilities

### 🔹 Member 1: Ingestion Pipeline & Vector Core
* **AI & Retrieval Tasks:**
  * Implement document parsing for Markdown, PDF, and Text files.
  * Implement dynamic text chunking strategies using token-based or recursive splitters with configurable overlap.
  * Configure embedding generation with local `sentence-transformers` models or OpenAI embeddings.
  * Build the core Qdrant similarity search engine with score filtering in `backend/app/services/retrieval.py`.
* **Software Engineering Tasks:**
  * Manage `backend/app/db/qdrant.py` database connections and payload collection schemas.
  * Write unit tests for chunking outputs and embedding vector dimensionality.
* **Key Code Deliverables:**
  * `backend/app/services/ingestion.py`
  * `backend/app/services/embeddings.py`
  * `backend/app/services/retrieval.py`
  * `backend/app/db/qdrant.py`

---

### 🔹 Member 2: FastMCP Server & Quantitative Evaluation
* **AI & Retrieval Tasks:**
  * Wrap Engineer 1's retrieval engine into protocol-level FastMCP tools (`search_notes`, `get_document`, `list_sources`).
  * Enforce "no-confident-match" score cutoffs (e.g., Cosine `< 0.72`) to reject low-relevance results.
  * Create a dataset of 15–20 hand-labeled query-document test pairs for evaluation.
  * Build the benchmark script to compute **Precision@K** and **Mean Reciprocal Rank (MRR)**.
* **Software Engineering Tasks:**
  * Configure STDIO JSON-RPC messaging for local MCP execution.
  * Set up `claude_desktop_config.json` integration and verify live tool calling inside Claude Desktop.
* **Key Code Deliverables:**
  * `backend/app/mcp_server/server.py`
  * `backend/app/mcp_server/tools.py`
  * `backend/app/eval/evaluate.py`
  * `docs/claude_desktop_config.json`

---

### 🔹 Member 3: Multi-Tenant REST API & Web Dashboard
* **AI & Retrieval Tasks:**
  * Implement tenant-scoped vector search queries passing `user_id` metadata payload filters to Qdrant.
  * Build UI components displaying chunk similarity scores, match confidence indicators, and source citations.
* **Software Engineering Tasks:**
  * Implement JWT authentication endpoints (`/auth/signup`, `/auth/login`) in FastAPI.
  * Create file upload and management REST endpoints (`/documents/upload`, `/documents/list`, `/documents/delete`).
  * Build the React UI dashboard with user login, document management, and an interactive semantic search view.
* **Key Code Deliverables:**
  * `backend/app/api/auth.py`
  * `backend/app/api/documents.py`
  * `backend/app/api/search.py`
  * `frontend/src/*` (React dashboard and components)

---

## 🔄 Daily Collaboration Flow

1. **Day 1 (Contract Definition):** Define mock interface models for retrieval functions (`search_qdrant(query, user_id, top_k)`) so Engineers 2 & 3 can build against mock data immediately.
2. **Days 2–4 (Parallel Execution):** All three engineers build their respective components concurrently.
3. **Day 5 (Integration):** Wire Engineer 1's vector store into Engineer 2's MCP tools and Engineer 3's FastAPI routes.
4. **Day 6 (Evaluation & Demo):** Run precision benchmarks, capture demo videos for Claude Desktop, and finalize documentation.