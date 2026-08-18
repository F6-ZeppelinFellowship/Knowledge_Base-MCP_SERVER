import io
import uuid
import logging
from typing import List, Dict, Any, Optional, Union

from app.core.config import settings
from app.db.qdrant import qdrant_db, QdrantStorage
from app.services.embeddings import embedding_service, EmbeddingService

logger = logging.getLogger(__name__)


class RecursiveTextSplitter:
    """Native recursive character text splitter with configurable chunk size and overlap."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, text: str, separators: List[str]) -> List[str]:
        final_chunks = []
        separator = separators[-1]
        new_separators = []

        for i, s in enumerate(separators):
            if s == "":
                separator = s
                break
            if s in text:
                separator = s
                new_separators = separators[i + 1 :]
                break

        splits = text.split(separator) if separator != "" else list(text)
        good_splits: List[str] = []
        _separator = separator if separator != "" else ""

        for s in splits:
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    merged = self._merge_splits(good_splits, _separator)
                    final_chunks.extend(merged)
                    good_splits = []
                if new_separators:
                    sub_chunks = self._split(s, new_separators)
                    final_chunks.extend(sub_chunks)
                else:
                    final_chunks.append(s)

        if good_splits:
            merged = self._merge_splits(good_splits, _separator)
            final_chunks.extend(merged)

        return final_chunks

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        docs = []
        current_doc: List[str] = []
        total = 0

        for s in splits:
            len_s = len(s)
            sep_len = len(separator) if current_doc else 0

            if total + len_s + sep_len > self.chunk_size and current_doc:
                doc = separator.join(current_doc)
                if doc.strip():
                    docs.append(doc)

                while total > self.chunk_overlap and current_doc:
                    popped = current_doc.pop(0)
                    total -= len(popped) + len(separator)

            current_doc.append(s)
            total += len_s + (len(separator) if len(current_doc) > 1 else 0)

        if current_doc:
            doc = separator.join(current_doc)
            if doc.strip():
                docs.append(doc)

        return docs


def parse_markdown(content: Union[bytes, str]) -> str:
    """Parse Markdown content to text string."""
    if isinstance(content, bytes):
        text = content.decode("utf-8", errors="replace")
    else:
        text = str(content)
    return text.strip()


def parse_text(content: Union[bytes, str]) -> str:
    """Parse plain text content."""
    if isinstance(content, bytes):
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1", errors="replace")
    else:
        text = str(content)
    return text.strip()


def parse_pdf(content: bytes) -> str:
    """Extract text content page by page from PDF bytes using pypdf."""
    try:
        from pypdf import PdfReader
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        pages_text = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text.strip())
        return "\n\n".join(pages_text)
    except Exception as e:
        logger.error(f"Error parsing PDF file: {e}")
        raise ValueError(f"Failed to parse PDF document: {e}")


def parse_document(file_content: Union[bytes, str], filename: str) -> str:
    """Detect file format from filename extension and extract clean text."""
    ext = filename.lower().split(".")[-1] if "." in filename else ""

    if ext == "pdf":
        if isinstance(file_content, str):
            file_bytes = file_content.encode("utf-8")
        else:
            file_bytes = file_content
        return parse_pdf(file_bytes)
    elif ext in ["md", "markdown"]:
        return parse_markdown(file_content)
    else:
        return parse_text(file_content)


def chunk_text(
    text: str,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Split text dynamically using RecursiveTextSplitter with configurable overlap.
    Returns a list of dicts with content and metadata.
    """
    c_size = chunk_size or settings.DEFAULT_CHUNK_SIZE
    c_overlap = chunk_overlap if chunk_overlap is not None else settings.DEFAULT_CHUNK_OVERLAP

    if not text or not text.strip():
        return []

    # Attempt langchain_text_splitters first, fallback to native RecursiveTextSplitter
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=c_size,
            chunk_overlap=c_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        raw_chunks = splitter.split_text(text)
    except Exception as err:
        logger.debug(f"Using native RecursiveTextSplitter (fallback reason: {err})")
        splitter = RecursiveTextSplitter(chunk_size=c_size, chunk_overlap=c_overlap)
        raw_chunks = splitter.split_text(text)

    chunks = []
    for i, chunk_str in enumerate(raw_chunks):
        if chunk_str and chunk_str.strip():
            chunks.append({
                "content": chunk_str,
                "metadata": {
                    "chunk_index": i,
                    "total_chunks": len(raw_chunks),
                    "char_length": len(chunk_str),
                }
            })

    return chunks


def _fallback_split_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Fallback recursive/character chunking implementation."""
    splitter = RecursiveTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)


def ingest_document(
    file_content: Union[bytes, str],
    filename: str,
    user_id: str,
    document_id: Optional[str] = None,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    storage: Optional[QdrantStorage] = None,
    embedder: Optional[EmbeddingService] = None,
) -> Dict[str, Any]:
    """
    Complete document ingestion pipeline:
    1. Parse document (.pdf, .md, .txt)
    2. Dynamically split text into chunks
    3. Generate vector embeddings for chunks
    4. Store chunks and vector embeddings in Qdrant DB
    """
    doc_id = document_id or str(uuid.uuid4())
    db = storage or qdrant_db
    emb_service = embedder or embedding_service

    # 1. Parse text from document
    extracted_text = parse_document(file_content, filename)
    if not extracted_text:
        raise ValueError(f"No readable text content found in document '{filename}'")

    # 2. Chunk text
    chunks = chunk_text(extracted_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    if not chunks:
        raise ValueError(f"Failed to create chunks from document '{filename}'")

    # 3. Generate embeddings
    chunk_texts = [c["content"] for c in chunks]
    vectors = emb_service.embed_documents(chunk_texts)

    # 4. Upsert into Qdrant
    point_ids = db.upsert_chunks(
        chunks=chunks,
        vectors=vectors,
        user_id=user_id,
        document_id=doc_id,
        filename=filename,
    )

    return {
        "document_id": doc_id,
        "filename": filename,
        "user_id": user_id,
        "chunk_count": len(chunks),
        "point_ids": point_ids,
        "status": "success",
    }
