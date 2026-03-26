"""
LlamaIndex SEC Filings Analyzer for PROMETHEUS.

Retrieval-Augmented Generation (RAG) pipeline that indexes SEC 10-K/10-Q filings
and answers natural-language questions about a company's financials.

Uses:
    - llama-index (core RAG framework)
    - llama-index-readers-sec-filings (SEC EDGAR reader)
    - Ollama (local LLM backend) or OpenAI

Install:
    pip install llama-index llama-index-readers-sec-filings

Architecture:
    SEC EDGAR → Download 10-K/10-Q → Chunk → Embed (local) → Vector Index
    User asks question → Retrieve top-k chunks → LLM synthesizes answer
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

LLAMAINDEX_AVAILABLE = False
SEC_READER_AVAILABLE = False

try:
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        Settings,
        Document,
    )
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    logger.info("llama-index not installed. Run: pip install llama-index")

try:
    from llama_index.readers.sec_filings import SECFilingsLoader
    SEC_READER_AVAILABLE = True
except ImportError:
    try:
        # Alternative import path
        from llama_index_readers_sec_filings import SECFilingsLoader
        SEC_READER_AVAILABLE = True
    except ImportError:
        logger.info("SEC filings reader not installed. Run: pip install llama-index-readers-sec-filings")


class LlamaIndexSECAnalyzer:
    """
    SEC filings RAG pipeline using LlamaIndex.

    Indexes 10-K annual reports and 10-Q quarterly filings from SEC EDGAR,
    and answers natural-language questions about company financials.
    """

    CACHE_DIR = Path("data/sec_filings_cache")

    def __init__(self):
        self.available = LLAMAINDEX_AVAILABLE
        self.sec_reader_available = SEC_READER_AVAILABLE
        self.indices: Dict[str, Any] = {}  # ticker -> VectorStoreIndex
        self.query_count = 0
        self.last_query_time = None

        # Create cache directory
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Configure LlamaIndex to use Ollama (local) if available
        if LLAMAINDEX_AVAILABLE:
            self._configure_llm()

    def _configure_llm(self):
        """Configure LlamaIndex to use local Ollama or OpenAI."""
        try:
            # Try Ollama first (free, local)
            from llama_index.llms.ollama import Ollama
            Settings.llm = Ollama(
                model=os.getenv("LLAMA_MODEL", "llama3.1:8b-trading"),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                request_timeout=120.0,
            )
            logger.info("LlamaIndex configured with Ollama LLM")
        except ImportError:
            try:
                # Fall back to OpenAI
                from llama_index.llms.openai import OpenAI as LlamaOpenAI
                api_key = os.getenv("OPENAI_API_KEY", "")
                if api_key:
                    Settings.llm = LlamaOpenAI(model="gpt-4o-mini", api_key=api_key)
                    logger.info("LlamaIndex configured with OpenAI LLM")
                else:
                    logger.warning("No LLM backend available for LlamaIndex")
            except ImportError:
                logger.warning("No LLM provider installed for LlamaIndex (need llama-index-llms-ollama or llama-index-llms-openai)")

        # Use simple local embedding
        try:
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
            logger.info("LlamaIndex embeddings: BAAI/bge-small-en-v1.5")
        except ImportError:
            # Fall back to default
            logger.info("Using default LlamaIndex embeddings")

    def load_sec_filings(
        self,
        ticker: str,
        filing_type: str = "10-K",
        num_filings: int = 3,
    ) -> bool:
        """
        Download and index SEC filings for a company.

        Args:
            ticker: Stock ticker (e.g., 'AAPL')
            filing_type: '10-K' (annual) or '10-Q' (quarterly)
            num_filings: Number of recent filings to download

        Returns:
            True if successfully indexed.
        """
        if not self.available:
            logger.error("LlamaIndex not available")
            return False

        ticker = ticker.upper()
        cache_key = f"{ticker}_{filing_type}"

        # Check if already indexed
        if cache_key in self.indices:
            logger.info(f"SEC index for {cache_key} already loaded")
            return True

        try:
            documents = []

            if self.sec_reader_available:
                # Use SEC EDGAR reader
                loader = SECFilingsLoader(
                    tickers=[ticker],
                    amount=num_filings,
                    filing_type=filing_type,
                )
                documents = loader.load_data()
                logger.info(f"Loaded {len(documents)} SEC filings for {ticker}")
            else:
                # Fallback: check local cache
                local_dir = self.CACHE_DIR / ticker
                if local_dir.exists():
                    reader = SimpleDirectoryReader(str(local_dir))
                    documents = reader.load_data()
                    logger.info(f"Loaded {len(documents)} documents from local cache for {ticker}")
                else:
                    logger.warning(f"No SEC filings available for {ticker} (SEC reader not installed)")
                    return False

            if not documents:
                logger.warning(f"No documents found for {ticker}")
                return False

            # Build vector index
            index = VectorStoreIndex.from_documents(documents)
            self.indices[cache_key] = index
            logger.info(f"SEC index built for {cache_key}: {len(documents)} documents indexed")
            return True

        except Exception as exc:
            logger.debug(f"SEC EDGAR unavailable for {ticker}: {exc}")
            return False

    def query(
        self,
        ticker: str,
        question: str,
        filing_type: str = "10-K",
    ) -> Dict[str, Any]:
        """
        Ask a question about a company's SEC filings.

        Args:
            ticker: Stock ticker
            question: Natural language question
            filing_type: '10-K' or '10-Q'

        Returns:
            Dict with 'answer', 'sources', 'confidence', etc.
        """
        if not self.available:
            return {"success": False, "error": "LlamaIndex not available"}

        ticker = ticker.upper()
        cache_key = f"{ticker}_{filing_type}"

        # Auto-load if not indexed
        if cache_key not in self.indices:
            loaded = self.load_sec_filings(ticker, filing_type)
            if not loaded:
                return {
                    "success": False,
                    "error": f"Could not load SEC filings for {ticker}",
                }

        try:
            index = self.indices[cache_key]
            query_engine = index.as_query_engine(similarity_top_k=5)
            response = query_engine.query(question)

            self.query_count += 1
            self.last_query_time = datetime.now()

            # Extract source nodes
            sources = []
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes[:3]:
                    sources.append({
                        "text": node.text[:200] + "..." if len(node.text) > 200 else node.text,
                        "score": round(node.score, 3) if hasattr(node, 'score') and node.score else None,
                    })

            return {
                "success": True,
                "answer": str(response),
                "sources": sources,
                "ticker": ticker,
                "filing_type": filing_type,
                "query": question,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as exc:
            logger.error(f"SEC query failed for {ticker}: {exc}")
            return {"success": False, "error": str(exc)}

    def analyze_financials(self, ticker: str) -> Dict[str, Any]:
        """
        Run a standard set of financial analysis questions against SEC filings.

        Returns a structured financial summary.
        """
        questions = [
            "What was the total revenue and net income for the most recent fiscal year?",
            "What are the main risk factors mentioned in the filing?",
            "What is the company's total debt and cash position?",
            "What is management's outlook and guidance for the next year?",
        ]

        results = {}
        for q in questions:
            key = q.split("?")[0].strip().lower().replace(" ", "_")[:30]
            results[key] = self.query(ticker, q)

        return {
            "success": True,
            "ticker": ticker,
            "analyses": results,
            "timestamp": datetime.now().isoformat(),
        }

    def get_status(self) -> Dict[str, Any]:
        """Get analyzer status."""
        return {
            "available": self.available,
            "sec_reader_available": self.sec_reader_available,
            "indexed_tickers": list(self.indices.keys()),
            "total_queries": self.query_count,
            "last_query": self.last_query_time.isoformat() if self.last_query_time else None,
        }

    def is_available(self) -> bool:
        return self.available


# Singleton
_sec_analyzer: Optional[LlamaIndexSECAnalyzer] = None

def get_sec_analyzer() -> LlamaIndexSECAnalyzer:
    """Get global SEC analyzer instance."""
    global _sec_analyzer
    if _sec_analyzer is None:
        _sec_analyzer = LlamaIndexSECAnalyzer()
    return _sec_analyzer
