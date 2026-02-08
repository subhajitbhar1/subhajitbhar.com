---
authors:
    - subhajit
title: "Reranking for Better RAG Retrieval"
description: Add cross-encoder reranking to your RAG pipeline for higher precision on top-k results.
slug: reranking-rag-cross-encoder
draft: true
date:
    created: 2025-01-29
categories:
    - AI ML
meta:
    - name: keywords
      content: Reranking, RAG, Cross-Encoder, LightRAG, Retrieval, Sentence Transformers
---

Bi-encoder retrieval is fast but imprecise. Cross-encoder reranking improves top-k precision at the cost of some latency. Here's when and how to add it.

<!-- more -->

## Bi-Encoder vs Cross-Encoder

**Bi-encoder** (used in vector search):

- Encodes query and documents separately
- Fast: O(1) per document after indexing
- Less accurate: no direct query-document interaction

**Cross-encoder**:

- Encodes query + document together
- Slow: O(n) for n candidates
- More accurate: full attention between query and document

The pattern: retrieve many with bi-encoder, rerank few with cross-encoder.

## Two-Stage Retrieval

```
Query
  │
  ▼
┌─────────────────┐
│ Bi-encoder      │  Retrieve top-20 candidates
│ (FAISS)         │  ~10-50ms
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ Cross-encoder   │  Rerank to top-4
│ (Reranker)      │  ~100-300ms
└─────────────────┘
  │
  ▼
Final top-k results
```

## Implementation

Install dependencies:

```bash
uv pip install faiss-cpu sentence-transformers openai
```

Reranker class:

```python
from typing import List, Tuple
import faiss
import numpy as np
from openai import OpenAI
from sentence_transformers import CrossEncoder


class RerankedRetriever:
    """Two-stage retrieval: FAISS + cross-encoder reranking."""
    
    def __init__(
        self,
        texts: List[str],
        sources: List[str],
        rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        self.texts = texts
        self.sources = sources
        self.reranker = CrossEncoder(rerank_model)
        self.faiss_index = self._build_index()
    
    def _build_index(self) -> faiss.IndexFlatIP:
        client = OpenAI()
        vecs = client.embeddings.create(
            input=self.texts,
            model="text-embedding-3-small"
        ).data
        X = np.array([v.embedding for v in vecs]).astype("float32")
        faiss.normalize_L2(X)
        
        idx = faiss.IndexFlatIP(X.shape[1])
        idx.add(X)
        return idx
    
    def _embed_query(self, query: str) -> np.ndarray:
        client = OpenAI()
        resp = client.embeddings.create(input=[query], model="text-embedding-3-small")
        vec = np.array([resp.data[0].embedding]).astype("float32")
        faiss.normalize_L2(vec)
        return vec
    
    def search(
        self,
        query: str,
        k: int = 4,
        candidates: int = 20
    ) -> List[Tuple[str, str, float]]:
        """
        Args:
            query: Search query
            k: Final number of results
            candidates: Number of candidates to rerank
        """
        # Stage 1: Fast bi-encoder retrieval
        q = self._embed_query(query)
        _, I = self.faiss_index.search(q, candidates)
        candidate_indices = I[0].tolist()
        
        # Stage 2: Cross-encoder reranking
        pairs = [(query, self.texts[i]) for i in candidate_indices]
        scores = self.reranker.predict(pairs)
        
        # Sort by rerank score
        ranked = sorted(
            zip(candidate_indices, scores),
            key=lambda x: x[1],
            reverse=True
        )[:k]
        
        return [
            (self.texts[idx], self.sources[idx], float(score))
            for idx, score in ranked
        ]
```

## Usage

```python
corpus = {
    "returns.md": "Customers may return items within 30 days with receipt.",
    "shipping.md": "Standard shipping takes 3-5 business days.",
    "warranty.md": "Electronics include a 1-year limited warranty.",
}

texts = list(corpus.values())
sources = list(corpus.keys())

retriever = RerankedRetriever(texts, sources)
results = retriever.search("What is the return policy?", k=3, candidates=10)

for text, source, score in results:
    print(f"[{source}] (score: {score:.3f})")
    print(f"  {text[:100]}...")
```

## Recommended Reranker Models

| Model                     | Size  | Speed   | Accuracy |
| ------------------------- | ----- | ------- | -------- |
| `ms-marco-MiniLM-L-6-v2`  | 80MB  | Fast    | Good     |
| `ms-marco-MiniLM-L-12-v2` | 130MB | Medium  | Better   |
| `bge-reranker-base`       | 280MB | Slow    | Best     |
| `bge-reranker-large`      | 560MB | Slowest | Best     |

Start with `ms-marco-MiniLM-L-6-v2` for latency-sensitive applications.

## When to Use Reranking

**Add reranking when:**

- Top-k precision matters more than latency
- You see relevant documents in top-20 but not top-4
- Users complain about irrelevant first results

**Skip reranking when:**

- Latency budget is < 200ms
- Bi-encoder recall is already high
- Corpus is small and homogeneous

## Latency Considerations

| Stage                            | Typical Latency |
| -------------------------------- | --------------- |
| FAISS search (50K vectors)       | 5-20ms          |
| Rerank 20 candidates (MiniLM)    | 50-150ms        |
| Rerank 20 candidates (BGE-large) | 200-400ms       |

Keep candidates low (10-20) to manage latency. Reranking 50+ candidates rarely improves results enough to justify the cost.

## Related

- [LightRAG: Lean RAG with Benchmarks](/blogs/lightrag-fast-retrieval-augmented-generation)
- [BM25 Hybrid Search with LightRAG](/blogs/lightrag-bm25-hybrid-search)
- [FAISS Index Types for Production RAG](/blogs/faiss-index-types-production-rag)
