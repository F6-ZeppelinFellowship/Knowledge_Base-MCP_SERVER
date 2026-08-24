import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from app.core.config import settings

# Force load .env file from the current or parent directory
load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openrouter/free"


def get_openrouter_client() -> OpenAI:
    # 1. Check settings, then os.environ
    api_key = getattr(settings, "OPENROUTER_API_KEY", None) or os.getenv("OPENROUTER_API_KEY", "")

    # Clean formatting
    api_key = api_key.strip().strip("'").strip('"')

    # Debug print to verify the key is loading (prints masked key to terminal)
    if api_key:
        print(f"[DEBUG] Loaded OPENROUTER_API_KEY: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("[DEBUG] ERROR: OPENROUTER_API_KEY is empty or missing!")

    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
        default_headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "Recall RAG",
        }
    )


def generate_rag_answer(query: str, search_results: List[Dict[str, Any]]) -> str:
    if not search_results:
        return "No relevant context found in the uploaded documents to answer your query."

    context_blocks = []
    for idx, item in enumerate(search_results, start=1):
        filename = item.get("filename") or item.get("source") or "Document"
        content = item.get("content") or item.get("text") or ""
        context_blocks.append(f"--- Document Chunk {idx} ({filename}) ---\n{content.strip()}")

    formatted_context = "\n\n".join(context_blocks)

    system_prompt = (
        "You are an AI assistant. Answer the user's question accurately and concisely "
        "based ONLY on the provided context chunks. If the context does not contain enough "
        "information, state that clearly."
    )

    user_prompt = f"Context:\n{formatted_context}\n\nQuestion: {query}"

    try:
        client = get_openrouter_client()
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or "Unable to generate an answer."
    except Exception as e:
        logger.error(f"OpenRouter Exception: {e}")
        return f"LLM Error: {str(e)}"