import os, sys, warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

import chromadb
from sentence_transformers import SentenceTransformer

print("=" * 60)
print("PROMETHEUS Knowledge Base Test")
print("=" * 60)

client = chromadb.PersistentClient('./knowledge_vectors')
collection = client.get_or_create_collection('prometheus_knowledge')
embedder = SentenceTransformer('all-MiniLM-L6-v2')

print(f"\nVectors in database: {collection.count()}")

queries = [
    "deep reinforcement learning portfolio optimization",
    "momentum trading LSTM neural network Sharpe ratio",
    "risk management position sizing drawdown",
    "sentiment analysis financial news NLP",
    "transformer attention mechanism time series"
]

for query in queries:
    print(f"\n{'─' * 60}")
    print(f"Query: {query}")
    
    embedding = embedder.encode(query).tolist()
    results = collection.query(query_embeddings=[embedding], n_results=2)
    
    if results['documents'] and results['documents'][0]:
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0], 
            results['distances'][0]
        ), 1):
            relevance = max(0, 100 - dist * 50)
            source = meta.get('source', 'Unknown')
            print(f"\n  [{i}] {source} (Relevance: {relevance:.0f}%)")
            print(f"      {doc[:200]}...")

print("\n" + "=" * 60)
print("Knowledge retrieval working!")
print("=" * 60)
