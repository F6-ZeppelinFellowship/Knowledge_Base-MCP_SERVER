import logging
import importlib.metadata
from typing import List, Optional

# Defensive patch for package metadata compatibility in local environment
_orig_version = importlib.metadata.version


def _safe_version(distribution_name: str) -> str:
    try:
        ver = _orig_version(distribution_name)
        if ver:
            return ver
    except Exception:
        pass
    return "2.0.0"


importlib.metadata.version = _safe_version

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating dense vector embeddings using SentenceTransformers or OpenAI."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.openai_api_key = openai_api_key or settings.OPENAI_API_KEY
        self._st_model = None
        self._dimension: int = settings.EMBEDDING_DIMENSION

    @property
    def st_model(self):
        """Lazy loader for sentence-transformers model."""
        if self._st_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer model: {self.model_name}")
                self._st_model = SentenceTransformer(self.model_name)
                self._dimension = self._st_model.get_sentence_embedding_dimension()
            except Exception as e:
                logger.error(f"Error loading SentenceTransformer model '{self.model_name}': {e}")
                raise e
        return self._st_model

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for a single text string."""
        if not text or not text.strip():
            return [0.0] * self.get_dimension()

        if self.openai_api_key:
            return self._embed_openai([text])[0]

        embedding = self.st_model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of text strings."""
        if not texts:
            return []

        cleaned_texts = [t.strip() if t and t.strip() else " " for t in texts]

        if self.openai_api_key:
            return self._embed_openai(cleaned_texts)

        embeddings = self.st_model.encode(cleaned_texts, batch_size=32, normalize_embeddings=True)
        return embeddings.tolist()

    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
            embeddings = [item.embedding for item in response.data]
            self._dimension = len(embeddings[0]) if embeddings else 1536
            return embeddings
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {e}. Falling back to SentenceTransformers.")
            embeddings = self.st_model.encode(texts, batch_size=32, normalize_embeddings=True)
            return embeddings.tolist()

    def get_dimension(self) -> int:
        """Return the vector dimensionality of the embedding model."""
        if self._st_model is not None:
            return self._st_model.get_sentence_embedding_dimension()
        return self._dimension


# Global singleton instance
embedding_service = EmbeddingService()
