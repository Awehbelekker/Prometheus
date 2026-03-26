#!/usr/bin/env python3
"""Test knowledge retrieval from ingested papers"""

from knowledge_ingestion_pipeline import KnowledgeIngestionPipeline

pipeline = KnowledgeIngestionPipeline()

# Get stats
stats = pipeline.get_stats()
print(f"\n{'='*60}")
print("KNOWLEDGE BASE STATUS")
print(f"{'='*60}")
print(f"Total Documents: {stats['total_documents']}")
print(f"Total Chunks: {stats['total_chunks']}")
print(f"Vector Count: {stats['vector_count']}")
print(f"By Type: {stats['by_type']}")

# Test queries
queries = [
    'deep reinforcement learning portfolio optimization',
    'momentum strategy LSTM neural network Sharpe ratio',
    'sentiment analysis stock prediction FinBERT',
    'transformer attention time series forecasting',
    'position sizing risk management drawdown',
]

print(f"\n{'='*60}")
print("TESTING KNOWLEDGE RETRIEVAL")
print(f"{'='*60}")

for query in queries:
    print(f"\nQuery: '{query}'")
    results = pipeline.query(query, n_results=3)
    for i, r in enumerate(results):
        title = r.get('metadata', {}).get('title', 'Unknown')
        relevance = r.get('relevance', 0)
        content_preview = r.get('content', '')[:100].replace('\n', ' ')
        print(f"  [{i+1}] {title}")
        print(f"      Relevance: {relevance:.2f}")
        print(f"      Preview: {content_preview}...")

print(f"\n{'='*60}")
print("KNOWLEDGE BASE READY FOR TRADING DECISIONS")
print(f"{'='*60}")
