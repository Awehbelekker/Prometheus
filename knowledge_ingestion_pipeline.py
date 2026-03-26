#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS KNOWLEDGE INGESTION PIPELINE
================================================================================

Ingests external knowledge sources into PROMETHEUS for enhanced trading decisions:
- Trading books (PDF, EPUB)
- Research papers (arXiv, SSRN)
- Articles and studies
- RSS feeds for news

Uses ChromaDB for vector storage and semantic retrieval.

================================================================================
"""

import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('knowledge_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add project root
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class KnowledgeDocument:
    """Represents a knowledge document"""
    id: str
    title: str
    source_type: str  # book, paper, article, study
    source_path: str
    content: str
    chunks: List[str]
    metadata: Dict[str, Any]
    ingested_at: str
    embedding_ids: List[str] = None


class KnowledgeIngestionPipeline:
    """
    Ingests and indexes external knowledge for PROMETHEUS.
    
    Supports:
    - PDF documents (trading books, research papers)
    - Text files (articles, studies)
    - JSON knowledge bases
    - RSS/Atom feeds
    """
    
    def __init__(self, 
                 knowledge_dir: str = "knowledge_base",
                 vector_db_path: str = "knowledge_vectors"):
        self.knowledge_dir = Path(knowledge_dir)
        self.vector_db_path = Path(vector_db_path)
        self.knowledge_dir.mkdir(exist_ok=True)
        self.vector_db_path.mkdir(exist_ok=True)
        
        # Knowledge index
        self.index_file = self.knowledge_dir / "knowledge_index.json"
        self.index: Dict[str, KnowledgeDocument] = {}
        
        # Chunk settings
        self.chunk_size = 1000  # characters
        self.chunk_overlap = 200
        
        # Initialize embedding model
        self.embedder = None
        self.vector_store = None
        
        self._load_index()
        self._init_embeddings()
        
        logger.info(f"Knowledge Pipeline initialized. {len(self.index)} documents indexed.")
    
    def _load_index(self):
        """Load existing knowledge index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for doc_id, doc_data in data.items():
                        self.index[doc_id] = KnowledgeDocument(**doc_data)
            except Exception as e:
                logger.error(f"Failed to load index: {e}")
    
    def _save_index(self):
        """Save knowledge index"""
        data = {doc_id: asdict(doc) for doc_id, doc in self.index.items()}
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _init_embeddings(self):
        """Initialize embedding model and vector store"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence-transformers embedder")
        except ImportError:
            logger.warning("sentence-transformers not available, using fallback")
            self.embedder = None
        
        try:
            import chromadb
            self.vector_store = chromadb.PersistentClient(path=str(self.vector_db_path))
            self.collection = self.vector_store.get_or_create_collection(
                name="prometheus_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaDB initialized with {self.collection.count()} vectors")
        except ImportError:
            logger.warning("ChromaDB not available, will use JSON fallback")
            self.vector_store = None
            self.collection = None
    
    def _generate_doc_id(self, content: str, source: str) -> str:
        """Generate unique document ID"""
        hash_input = f"{source}:{content[:1000]}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end
                for sep in ['. ', '.\n', '? ', '! ']:
                    last_sep = text[start:end].rfind(sep)
                    if last_sep > self.chunk_size // 2:
                        end = start + last_sep + len(sep)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def _extract_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            logger.warning("PyMuPDF not installed. Install with: pip install PyMuPDF")
            return ""
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ""
    
    def _extract_epub(self, epub_path: str) -> str:
        """Extract text from EPUB"""
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup
            
            book = epub.read_epub(epub_path)
            text = ""
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text += soup.get_text() + "\n"
            
            return text
        except ImportError:
            logger.warning("ebooklib not installed. Install with: pip install ebooklib beautifulsoup4")
            return ""
        except Exception as e:
            logger.error(f"EPUB extraction failed: {e}")
            return ""
    
    def ingest_pdf(self, pdf_path: str, title: str = None, 
                   source_type: str = "book", metadata: dict = None) -> Optional[str]:
        """Ingest a PDF document"""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            logger.error(f"PDF not found: {pdf_path}")
            return None
        
        logger.info(f"Ingesting PDF: {pdf_path.name}")
        
        # Extract text
        content = self._extract_pdf(str(pdf_path))
        if not content:
            logger.error("Failed to extract PDF content")
            return None
        
        title = title or pdf_path.stem
        return self._ingest_content(content, title, source_type, str(pdf_path), metadata)
    
    def ingest_text(self, text_path: str, title: str = None,
                    source_type: str = "article", metadata: dict = None) -> Optional[str]:
        """Ingest a text file"""
        text_path = Path(text_path)
        if not text_path.exists():
            logger.error(f"File not found: {text_path}")
            return None
        
        with open(text_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title = title or text_path.stem
        return self._ingest_content(content, title, source_type, str(text_path), metadata)
    
    def ingest_raw_text(self, content: str, title: str,
                        source_type: str = "study", metadata: dict = None) -> Optional[str]:
        """Ingest raw text content"""
        return self._ingest_content(content, title, source_type, "raw_input", metadata)
    
    def _ingest_content(self, content: str, title: str, source_type: str,
                        source_path: str, metadata: dict = None) -> Optional[str]:
        """Core ingestion logic"""
        # Generate ID
        doc_id = self._generate_doc_id(content, source_path)
        
        # Check if already ingested
        if doc_id in self.index:
            logger.info(f"Document already ingested: {title}")
            return doc_id
        
        # Chunk content
        chunks = self._chunk_text(content)
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Create document
        doc = KnowledgeDocument(
            id=doc_id,
            title=title,
            source_type=source_type,
            source_path=source_path,
            content=content[:5000],  # Store first 5000 chars
            chunks=chunks,
            metadata=metadata or {},
            ingested_at=datetime.now().isoformat(),
            embedding_ids=[]
        )
        
        # Generate embeddings and store in vector DB
        if self.embedder and self.collection:
            try:
                embeddings = self.embedder.encode(chunks).tolist()
                
                # Add to ChromaDB
                chunk_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
                self.collection.add(
                    ids=chunk_ids,
                    embeddings=embeddings,
                    documents=chunks,
                    metadatas=[{
                        "doc_id": doc_id,
                        "title": title,
                        "source_type": source_type,
                        "chunk_index": i
                    } for i in range(len(chunks))]
                )
                
                doc.embedding_ids = chunk_ids
                logger.info(f"Added {len(chunk_ids)} vectors to ChromaDB")
                
            except Exception as e:
                logger.error(f"Embedding failed: {e}")
        
        # Save to index
        self.index[doc_id] = doc
        self._save_index()
        
        logger.info(f"Successfully ingested: {title} (ID: {doc_id})")
        return doc_id
    
    def query(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Query knowledge base for relevant content"""
        if not self.embedder or not self.collection:
            logger.warning("Vector search not available")
            return self._fallback_search(query, n_results)
        
        try:
            # Get query embedding
            query_embedding = self.embedder.encode([query]).tolist()
            
            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            # Format results
            formatted = []
            for i, doc in enumerate(results['documents'][0]):
                formatted.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0,
                    'relevance': 1 - (results['distances'][0][i] if results['distances'] else 0)
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []
    
    def _fallback_search(self, query: str, n_results: int) -> List[Dict[str, Any]]:
        """Fallback keyword search when vector DB not available"""
        results = []
        query_terms = query.lower().split()
        
        for doc_id, doc in self.index.items():
            for chunk in doc.chunks:
                chunk_lower = chunk.lower()
                matches = sum(1 for term in query_terms if term in chunk_lower)
                if matches > 0:
                    results.append({
                        'content': chunk,
                        'metadata': {'doc_id': doc_id, 'title': doc.title},
                        'relevance': matches / len(query_terms)
                    })
        
        # Sort by relevance and return top N
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:n_results]
    
    def ingest_trading_knowledge(self):
        """Ingest built-in trading knowledge"""
        
        # Core trading concepts
        trading_knowledge = [
            {
                "title": "Trend Following Fundamentals",
                "content": """
                Trend following is a trading strategy that attempts to capture gains by analyzing momentum in a particular direction.
                
                Key Principles:
                1. The trend is your friend - trade in the direction of the prevailing trend
                2. Cut losses short, let profits run - use trailing stops
                3. Wait for confirmation before entering - don't anticipate
                4. Use multiple timeframes - align short-term with long-term trends
                
                Entry Signals:
                - Moving average crossovers (e.g., 50 MA crosses above 200 MA)
                - Breakouts above resistance with volume confirmation
                - Higher highs and higher lows pattern
                
                Exit Signals:
                - Moving average crossovers in opposite direction
                - Break below trailing stop
                - Divergence between price and momentum indicators
                """,
                "source_type": "study"
            },
            {
                "title": "Mean Reversion Strategies",
                "content": """
                Mean reversion is based on the theory that prices tend to return to their average over time.
                
                Key Concepts:
                1. Overbought/Oversold conditions indicate potential reversals
                2. Bollinger Bands measure standard deviation from mean
                3. RSI above 70 = overbought, below 30 = oversold
                4. Mean reversion works best in ranging markets
                
                Entry Signals:
                - Price touches lower Bollinger Band with RSI < 30
                - 2+ standard deviations from 20-day mean
                - Volume spike on reversal candle
                
                Risk Management:
                - Strict stop losses (mean reversion can fail in trending markets)
                - Position sizing based on volatility
                - Avoid trading during news events
                """,
                "source_type": "study"
            },
            {
                "title": "Volume Price Analysis",
                "content": """
                Volume Price Analysis (VPA) studies the relationship between price and volume to predict future moves.
                
                Key Patterns:
                1. Rising price + Rising volume = Strong trend (accumulation)
                2. Rising price + Falling volume = Weak trend (distribution warning)
                3. Falling price + Rising volume = Strong selling (panic/capitulation)
                4. Falling price + Falling volume = Weak selling (near bottom)
                
                Wyckoff Method:
                - Accumulation: Smart money buying from weak hands
                - Markup: Price rises as demand exceeds supply
                - Distribution: Smart money selling to public
                - Markdown: Price falls as supply exceeds demand
                
                Volume Indicators:
                - On-Balance Volume (OBV)
                - Volume Weighted Average Price (VWAP)
                - Accumulation/Distribution Line
                """,
                "source_type": "study"
            },
            {
                "title": "Risk Management Rules",
                "content": """
                Professional Risk Management for Trading:
                
                Position Sizing:
                1. Never risk more than 1-2% of capital per trade
                2. Calculate position size: Risk Amount / (Entry - Stop Loss)
                3. Scale into positions rather than full entry
                4. Reduce position size during drawdowns
                
                Portfolio Rules:
                1. Maximum 20% of capital in single sector
                2. Diversify across uncorrelated assets
                3. Keep 20-30% in cash for opportunities
                4. Rebalance monthly
                
                Drawdown Management:
                - 10% drawdown: Reduce position sizes by 50%
                - 20% drawdown: Stop trading, review strategy
                - Never add to losing positions
                
                Kelly Criterion:
                f* = (bp - q) / b
                Where: b=odds, p=win probability, q=loss probability
                Use half-Kelly for safety
                """,
                "source_type": "study"
            },
            {
                "title": "Chart Pattern Recognition",
                "content": """
                Classic Chart Patterns and Their Reliability:
                
                Reversal Patterns:
                1. Head and Shoulders: 83% reliability, target = height of pattern
                2. Double Top/Bottom: 75% reliability, target = height of pattern
                3. Triple Top/Bottom: 87% reliability, very strong signal
                
                Continuation Patterns:
                1. Bull/Bear Flag: 67% reliability, target = flagpole length
                2. Pennant: 60% reliability, occurs mid-trend
                3. Ascending/Descending Triangle: 75% reliability
                
                Candlestick Patterns:
                1. Engulfing patterns: Strong reversal signal
                2. Doji at resistance/support: Indecision, potential reversal
                3. Hammer/Shooting Star: Single candle reversal signals
                
                Confirmation:
                - Always wait for breakout confirmation
                - Volume should increase on breakout
                - Retest of broken level adds confidence
                """,
                "source_type": "study"
            },
            {
                "title": "Market Regime Detection",
                "content": """
                Identifying Market Regimes for Strategy Selection:
                
                Regime Types:
                1. Trending Up: Price above 200 MA, ADX > 25
                2. Trending Down: Price below 200 MA, ADX > 25
                3. Ranging: ADX < 20, price oscillating
                4. High Volatility: VIX > 25, wide ATR
                
                Strategy Mapping:
                - Trending Up: Trend following, momentum strategies
                - Trending Down: Short selling, inverse ETFs
                - Ranging: Mean reversion, options selling
                - High Volatility: Reduce position size, use wider stops
                
                Regime Change Signals:
                1. Moving average crossovers
                2. Volatility expansion/contraction
                3. Sector rotation patterns
                4. Breadth indicator divergence
                
                Avoid:
                - Trend following in ranging markets
                - Mean reversion in trending markets
                - Large positions in regime transitions
                """,
                "source_type": "study"
            },
            {
                "title": "Quantitative Factor Investing",
                "content": """
                Academic Research on Factor Premiums:
                
                Proven Factors (Fama-French and beyond):
                1. Value: Low P/B, P/E stocks outperform over time
                2. Momentum: Past winners continue winning (3-12 month horizon)
                3. Size: Small caps have higher expected returns
                4. Quality: High ROE, low debt companies outperform
                5. Low Volatility: Paradoxically, low vol stocks outperform
                
                Factor Timing:
                - Value works best after recessions
                - Momentum crashes during market reversals
                - Quality outperforms in uncertainty
                
                Implementation:
                1. Rank stocks by factor scores
                2. Go long top decile, short bottom decile
                3. Monthly or quarterly rebalancing
                4. Transaction cost aware optimization
                
                Combining Factors:
                - Multi-factor models more stable than single factor
                - Equal weight or volatility adjusted weighting
                - Watch for factor crowding
                """,
                "source_type": "paper"
            }
        ]
        
        for knowledge in trading_knowledge:
            self.ingest_raw_text(
                content=knowledge["content"],
                title=knowledge["title"],
                source_type=knowledge["source_type"],
                metadata={"category": "trading_fundamentals", "built_in": True}
            )
        
        logger.info(f"Ingested {len(trading_knowledge)} built-in trading knowledge documents")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        stats = {
            "total_documents": len(self.index),
            "by_type": {},
            "total_chunks": 0,
            "vector_count": self.collection.count() if self.collection else 0
        }
        
        for doc in self.index.values():
            source_type = doc.source_type
            stats["by_type"][source_type] = stats["by_type"].get(source_type, 0) + 1
            stats["total_chunks"] += len(doc.chunks)
        
        return stats


class EnhancedMarketOracle:
    """
    Market Oracle with knowledge retrieval augmentation.
    Uses RAG to enhance trading decisions with external knowledge.
    """
    
    def __init__(self, knowledge_pipeline: KnowledgeIngestionPipeline):
        self.knowledge = knowledge_pipeline
        logger.info("Enhanced Market Oracle initialized with knowledge retrieval")
    
    def get_trading_context(self, symbol: str, market_conditions: Dict[str, Any]) -> str:
        """Get relevant knowledge for trading decision"""
        
        # Build query from market conditions
        queries = []
        
        # Add trend-based query
        trend = market_conditions.get('trend', 'neutral')
        if trend == 'bullish':
            queries.append("bullish trend following entry signals momentum")
        elif trend == 'bearish':
            queries.append("bearish trend short selling risk management")
        else:
            queries.append("ranging market mean reversion strategy")
        
        # Add pattern-based query
        patterns = market_conditions.get('patterns', [])
        if patterns:
            queries.append(f"chart pattern {' '.join(patterns[:3])}")
        
        # Add volatility query
        volatility = market_conditions.get('volatility', 'normal')
        if volatility == 'high':
            queries.append("high volatility risk management position sizing")
        
        # Query knowledge base
        all_results = []
        for query in queries:
            results = self.knowledge.query(query, n_results=3)
            all_results.extend(results)
        
        # Deduplicate and sort by relevance
        seen = set()
        unique_results = []
        for r in sorted(all_results, key=lambda x: x.get('relevance', 0), reverse=True):
            content_hash = hash(r['content'][:100])
            if content_hash not in seen:
                seen.add(content_hash)
                unique_results.append(r)
        
        # Build context string
        context_parts = []
        for r in unique_results[:5]:
            title = r.get('metadata', {}).get('title', 'Unknown')
            context_parts.append(f"[{title}]: {r['content'][:500]}")
        
        return "\n\n".join(context_parts)
    
    def enhance_signal(self, symbol: str, base_signal: Dict[str, Any],
                       market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance trading signal with knowledge context"""
        
        # Get relevant knowledge
        context = self.get_trading_context(symbol, market_conditions)
        
        # Add knowledge to signal
        enhanced_signal = base_signal.copy()
        enhanced_signal['knowledge_context'] = context
        enhanced_signal['knowledge_enhanced'] = True
        
        # Adjust confidence based on knowledge alignment
        if context:
            # Simple heuristic: if knowledge supports signal direction, boost confidence
            direction = base_signal.get('direction', 'neutral')
            if direction == 'long' and 'bullish' in context.lower():
                enhanced_signal['confidence'] = min(base_signal.get('confidence', 0.5) * 1.1, 1.0)
            elif direction == 'short' and 'bearish' in context.lower():
                enhanced_signal['confidence'] = min(base_signal.get('confidence', 0.5) * 1.1, 1.0)
        
        return enhanced_signal


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("PROMETHEUS KNOWLEDGE INGESTION PIPELINE")
    print("="*70)
    
    # Initialize pipeline
    pipeline = KnowledgeIngestionPipeline()
    
    # Ingest built-in trading knowledge
    print("\n[1] Ingesting built-in trading knowledge...")
    pipeline.ingest_trading_knowledge()
    
    # Check for PDFs in knowledge directory
    print("\n[2] Scanning for documents to ingest...")
    knowledge_dir = Path("knowledge_base")
    
    for pdf_file in knowledge_dir.glob("*.pdf"):
        print(f"    Found PDF: {pdf_file.name}")
        pipeline.ingest_pdf(str(pdf_file))
    
    for txt_file in knowledge_dir.glob("*.txt"):
        print(f"    Found TXT: {txt_file.name}")
        pipeline.ingest_text(str(txt_file))
    
    # Show stats
    print("\n[3] Knowledge Base Statistics:")
    stats = pipeline.get_stats()
    print(f"    Total Documents: {stats['total_documents']}")
    print(f"    Total Chunks: {stats['total_chunks']}")
    print(f"    Vector Count: {stats['vector_count']}")
    print(f"    By Type: {stats['by_type']}")
    
    # Test query
    print("\n[4] Testing knowledge retrieval...")
    test_queries = [
        "trend following entry signals",
        "risk management position sizing",
        "mean reversion oversold"
    ]
    
    for query in test_queries:
        print(f"\n    Query: '{query}'")
        results = pipeline.query(query, n_results=2)
        for i, r in enumerate(results):
            title = r.get('metadata', {}).get('title', 'Unknown')
            relevance = r.get('relevance', 0)
            print(f"      [{i+1}] {title} (relevance: {relevance:.2f})")
    
    print("\n" + "="*70)
    print("KNOWLEDGE PIPELINE READY")
    print("="*70)
    print("\nTo add documents:")
    print("  1. Place PDF/TXT files in 'knowledge_base/' directory")
    print("  2. Run this script again to ingest")
    print("\nTo query programmatically:")
    print("  pipeline = KnowledgeIngestionPipeline()")
    print("  results = pipeline.query('your query here')")
    print("="*70)


if __name__ == "__main__":
    main()
