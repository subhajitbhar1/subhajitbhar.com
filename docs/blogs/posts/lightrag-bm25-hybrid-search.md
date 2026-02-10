---
authors:
    - subhajit
title: "BM25 Hybrid Search with LightRAG"
description: Combine BM25 lexical search with vector search using Reciprocal Rank Fusion for better retrieval.
slug: lightrag-bm25-hybrid-search
date:
    created: 2025-01-29
categories:
    - LLM Engineering
tags:
    - RAG
    - LightRAG
    - Retrival
meta:
    - name: keywords
      content: LightRAG, BM25, Hybrid Search, RAG, Reciprocal Rank Fusion, Vector Search
---

Vector search misses keyword-heavy queries. BM25 misses semantic similarity. Combine both with hybrid search for better retrieval recall.

<!-- more -->

## Why Hybrid Search

Pure vector search struggles with:

- Exact product codes, IDs, or technical terms
- Queries where the user's exact phrasing matters
- Sparse vocabularies (legal, medical)

BM25 (lexical) handles these well but misses paraphrases and synonyms. Hybrid search combines both for the best of both worlds.

## Implementation

Install dependencies:

```bash
uv pip install faiss-cpu rank-bm25 openai
```

Hybrid retriever with Reciprocal Rank Fusion (RRF):

```python
from typing import List, Tuple
import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from openai import OpenAI


class HybridRetriever:
    """Combines FAISS vector search with BM25 lexical search."""
    
    def __init__(
        self, 
        texts: List[str], 
        sources: List[str],
        embedding_model: str = "text-embedding-3-small"
    ):
        self.texts = texts
        self.sources = sources
        self.embedding_model = embedding_model
        
        # Build FAISS index
        self.faiss_index = self._build_faiss_index()
        
        # Build BM25 index
        tokenized = [t.lower().split() for t in texts]
        self.bm25 = BM25Okapi(tokenized)
    
    def _build_faiss_index(self) -> faiss.IndexFlatIP:
        client = OpenAI()
        vecs = client.embeddings.create(
            input=self.texts, 
            model=self.embedding_model
        ).data
        X = np.array([v.embedding for v in vecs]).astype("float32")
        faiss.normalize_L2(X)
        
        idx = faiss.IndexFlatIP(X.shape[1])
        idx.add(X)
        return idx
    
    def _embed_query(self, query: str) -> np.ndarray:
        client = OpenAI()
        resp = client.embeddings.create(input=[query], model=self.embedding_model)
        vec = np.array([resp.data[0].embedding]).astype("float32")
        faiss.normalize_L2(vec)
        return vec
    
    def _vector_search(self, query: str, k: int) -> List[Tuple[int, float]]:
        q = self._embed_query(query)
        D, I = self.faiss_index.search(q, k)
        return [(int(I[0][i]), float(D[0][i])) for i in range(len(I[0]))]
    
    def _bm25_search(self, query: str, k: int) -> List[Tuple[int, float]]:
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        top_k = np.argsort(scores)[::-1][:k]
        return [(int(i), float(scores[i])) for i in top_k]
    
    def search(
        self, 
        query: str, 
        k: int = 4, 
        vector_weight: float = 0.5,
        rrf_k: int = 60
    ) -> List[Tuple[str, str, float]]:
        """
        Hybrid search using Reciprocal Rank Fusion.
        
        Args:
            query: Search query
            k: Number of results to return
            vector_weight: Weight for vector results (0-1)
            rrf_k: RRF constant (default 60)
        """
        # Get more candidates than needed for fusion
        n_candidates = k * 3
        
        vector_results = self._vector_search(query, n_candidates)
        bm25_results = self._bm25_search(query, n_candidates)
        
        # Build rank maps
        vector_ranks = {idx: rank for rank, (idx, _) in enumerate(vector_results)}
        bm25_ranks = {idx: rank for rank, (idx, _) in enumerate(bm25_results)}
        
        # RRF fusion
        all_indices = set(vector_ranks.keys()) | set(bm25_ranks.keys())
        scores = {}
        
        for idx in all_indices:
            v_rank = vector_ranks.get(idx, n_candidates)
            b_rank = bm25_ranks.get(idx, n_candidates)
            
            v_score = vector_weight / (rrf_k + v_rank)
            b_score = (1 - vector_weight) / (rrf_k + b_rank)
            scores[idx] = v_score + b_score
        
        # Sort and return top k
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        return [(self.texts[idx], self.sources[idx], score) for idx, score in ranked]
```

## Usage

```python
corpus = {
    "SKU-12345.md": "Product SKU-12345 is a wireless mouse with 2.4GHz connectivity.",
    "returns.md": "Customers may return items within 30 days with receipt.",
    "warranty.md": "Electronics include a 1-year limited warranty.",
}

texts, sources = [], []
for src, text in corpus.items():
    texts.append(text)
    sources.append(src)

retriever = HybridRetriever(texts, sources)

# Keyword query - BM25 helps
results = retriever.search("SKU-12345", k=3)

# Semantic query - vector helps
results = retriever.search("how long can I return a product", k=3)
```

## Tuning Hybrid Search

| Parameter       | Default | Notes                                      |
| --------------- | ------- | ------------------------------------------ |
| `vector_weight` | 0.5     | Increase for semantic-heavy queries        |
| `rrf_k`         | 60      | Standard RRF constant, rarely needs tuning |
| `n_candidates`  | k * 3   | More candidates = better fusion, more cost |

Start with equal weights. If users search exact codes/IDs often, lower `vector_weight` to 0.3.

## When to Use Hybrid

Use hybrid search when:

- Corpus contains technical terms, IDs, or codes
- Users search with exact phrases
- Pure vector search shows low recall on keyword queries

Skip hybrid if your queries are purely semantic and corpus is natural language. See [LightRAG: Lean RAG](/blogs/lightrag-fast-retrieval-augmented-generation) for the pure vector approach.

## Related

- [LightRAG: Lean RAG with Benchmarks](/blogs/lightrag-fast-retrieval-augmented-generation)
- [Reranking for Better RAG Retrieval](/blogs/reranking-rag-cross-encoder)
