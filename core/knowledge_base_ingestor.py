"""
Knowledge Base Ingestor
Watches knowledge_input/ folder for dropped PDFs/text files.
Chunks, embeds via sentence-transformers, stores in ChromaDB.
Provides query() for any trading system to consult.
"""
import asyncio
import hashlib
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

KNOWLEDGE_INPUT = Path(__file__).parent.parent / "knowledge_input"
KNOWLEDGE_VECTORS = Path(__file__).parent.parent / "knowledge_vectors"
CHUNK_SIZE = 500        # words per chunk
CHUNK_OVERLAP = 50      # words overlap between chunks
COLLECTION_NAME = "prometheus_user_docs"
EMBED_MODEL = "all-MiniLM-L6-v2"   # already used in oracle engine

# Module-level lazy-loaded singletons
_embedder = None
_chroma_client = None
_collection = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def _get_collection():
    global _chroma_client, _collection
    if _collection is None:
        import chromadb
        KNOWLEDGE_VECTORS.mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=str(KNOWLEDGE_VECTORS))
        _collection = _chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def _chunk_text(text: str) -> List[str]:
    """Split text into overlapping word-chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i: i + CHUNK_SIZE]
        chunks.append(" ".join(chunk_words))
        i += CHUNK_SIZE - CHUNK_OVERLAP
    return [c for c in chunks if len(c.strip()) > 50]


def _extract_text(path: Path) -> str:
    """Extract plain text from PDF or text file."""
    suffix = path.suffix.lower()
    try:
        if suffix == ".pdf":
            try:
                import pdfminer.high_level as pdfminer
                return pdfminer.extract_text(str(path))
            except ImportError:
                try:
                    import pypdf
                    reader = pypdf.PdfReader(str(path))
                    return "\n".join(page.extract_text() or "" for page in reader.pages)
                except ImportError:
                    logger.warning("[KBIngestor] No PDF library — install pdfminer.six or pypdf")
                    return ""
        else:
            return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        logger.debug(f"[KBIngestor] Text extraction error {path.name}: {e}")
        return ""


def ingest_file(path: Path) -> int:
    """
    Ingest a single file into ChromaDB.
    Returns number of chunks added (0 if already ingested or error).
    """
    try:
        collection = _get_collection()
        embedder = _get_embedder()

        text = _extract_text(path)
        if not text or len(text.strip()) < 100:
            logger.debug(f"[KBIngestor] Skipping empty file: {path.name}")
            return 0

        chunks = _chunk_text(text)
        if not chunks:
            return 0

        # Use file hash as namespace to avoid duplicates
        file_hash = hashlib.md5(path.read_bytes()).hexdigest()[:12]
        ids = [f"{file_hash}_{i}" for i in range(len(chunks))]

        # Check if already ingested
        existing = collection.get(ids=[ids[0]])
        if existing and existing.get("ids"):
            logger.debug(f"[KBIngestor] Already ingested: {path.name}")
            return 0

        embeddings = embedder.encode(chunks, show_progress_bar=False).tolist()
        metadatas = [{"source": path.name, "file_hash": file_hash, "chunk": i} for i in range(len(chunks))]

        collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
        logger.info(f"[KBIngestor] Ingested {path.name}: {len(chunks)} chunks")
        return len(chunks)

    except Exception as e:
        logger.warning(f"[KBIngestor] Ingest error {path.name}: {e}")
        return 0


def query(question: str, symbol: str = "", top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Query the knowledge base for relevant context.
    Returns list of {'text': str, 'source': str, 'distance': float}
    """
    try:
        collection = _get_collection()
        embedder = _get_embedder()

        query_text = f"{symbol} {question}".strip() if symbol else question
        query_embedding = embedder.encode([query_text], show_progress_bar=False).tolist()

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, max(collection.count(), 1)),
            include=["documents", "metadatas", "distances"],
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        return [
            {"text": doc, "source": meta.get("source", "unknown"), "distance": dist}
            for doc, meta, dist in zip(docs, metas, dists)
        ]
    except Exception as e:
        logger.debug(f"[KBIngestor] Query error: {e}")
        return []


async def watch_and_ingest(folder: Optional[Path] = None):
    """
    Async background loop — watches knowledge_input/ every 5 minutes.
    Ingests any new .pdf, .txt, .md files dropped by the user.
    """
    watch_dir = folder or KNOWLEDGE_INPUT
    watch_dir.mkdir(parents=True, exist_ok=True)
    processed: set = set()

    logger.info(f"[KBIngestor] Watching {watch_dir} for new documents...")

    while True:
        try:
            for ext in ("*.pdf", "*.txt", "*.md"):
                for fpath in watch_dir.glob(ext):
                    if fpath not in processed:
                        chunks = ingest_file(fpath)
                        processed.add(fpath)
                        if chunks > 0:
                            logger.info(f"[KBIngestor] New document ingested: {fpath.name} ({chunks} chunks)")
        except Exception as e:
            logger.debug(f"[KBIngestor] Watch loop error: {e}")

        await asyncio.sleep(300)  # check every 5 minutes


def get_ingestor_summary() -> Dict[str, Any]:
    """Return stats about the knowledge base."""
    try:
        collection = _get_collection()
        count = collection.count()
        return {"total_chunks": count, "collection": COLLECTION_NAME, "status": "ok"}
    except Exception as e:
        return {"total_chunks": 0, "collection": COLLECTION_NAME, "status": str(e)}
