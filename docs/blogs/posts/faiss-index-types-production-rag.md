---
authors:
    - subhajit
title: "FAISS Index Types for Production RAG"
description: Choose the right FAISS index for your corpus size - from Flat to IVF to HNSW with memory and accuracy trade-offs.
slug: faiss-index-types-production-rag
draft: true
date:
    created: 2025-01-29
categories:
    - AI ML
meta:
    - name: keywords
      content: FAISS, LightRAG, Vector Index, IVF, HNSW, Production RAG, Vector Search
---

`IndexFlatIP` works for small corpora. For production with 100K+ vectors, you need smarter indexes. Here's how to choose and implement them.

<!-- more -->

## FAISS Index Types Overview

| Index           | Corpus Size | Memory | Accuracy | Build Time |
| --------------- | ----------- | ------ | -------- | ---------- |
| `IndexFlatIP`   | < 50K       | High   | Exact    | Fast       |
| `IndexIVFFlat`  | 50K - 1M    | Medium | ~95-99%  | Medium     |
| `IndexHNSWFlat` | 50K - 10M   | High   | ~95-99%  | Slow       |
| `IndexIVFPQ`    | 1M+         | Low    | ~90-95%  | Slow       |

## IndexFlatIP (Baseline)

Exact search, no training required. Use for prototypes and small corpora.

```python
import faiss
import numpy as np

def build_flat_index(vectors: np.ndarray) -> faiss.IndexFlatIP:
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index
```

**Pros:** Exact results, simple  
**Cons:** O(n) search time, doesn't scale

## IndexIVFFlat (Clustered Search)

Partitions vectors into clusters. Searches only nearby clusters for speed.

```python
def build_ivf_index(
    vectors: np.ndarray, 
    nlist: int = 100,
    nprobe: int = 10
) -> faiss.IndexIVFFlat:
    """
    Args:
        vectors: Normalized embedding vectors
        nlist: Number of clusters (sqrt(n) is a good start)
        nprobe: Clusters to search at query time
    """
    faiss.normalize_L2(vectors)
    dim = vectors.shape[1]
    
    # Quantizer for cluster centroids
    quantizer = faiss.IndexFlatIP(dim)
    index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
    
    # Must train before adding
    index.train(vectors)
    index.add(vectors)
    
    # Set search-time parameter
    index.nprobe = nprobe
    return index
```

**Tuning:**

- `nlist`: Start with `sqrt(n)`. More clusters = faster search, lower recall
- `nprobe`: Start with `nlist / 10`. Increase for better recall

## IndexHNSWFlat (Graph-Based)

Hierarchical Navigable Small World graph. Excellent recall with fast search.

```python
def build_hnsw_index(
    vectors: np.ndarray,
    M: int = 32,
    ef_construction: int = 200,
    ef_search: int = 64
) -> faiss.IndexHNSWFlat:
    """
    Args:
        vectors: Normalized embedding vectors
        M: Connections per node (higher = more accurate, more memory)
        ef_construction: Build-time search depth
        ef_search: Query-time search depth
    """
    faiss.normalize_L2(vectors)
    dim = vectors.shape[1]
    
    index = faiss.IndexHNSWFlat(dim, M, faiss.METRIC_INNER_PRODUCT)
    index.hnsw.efConstruction = ef_construction
    index.hnsw.efSearch = ef_search
    index.add(vectors)
    return index
```

**Trade-offs:**

- Higher `M` = better recall, 4-8x more memory
- HNSW doesn't support removal; rebuild for updates

## Persistence

Save and load indexes for production:

```python
def save_index(index: faiss.Index, path: str):
    faiss.write_index(index, path)

def load_index(path: str) -> faiss.Index:
    return faiss.read_index(path)

# Usage
save_index(index, "vectors.index")
index = load_index("vectors.index")
```

For IVF indexes, you can also memory-map for reduced RAM:

```python
index = faiss.read_index("vectors.index", faiss.IO_FLAG_MMAP)
```

## Choosing an Index

```
Corpus < 50K vectors?
  └─> IndexFlatIP (exact, simple)

Corpus 50K - 500K?
  └─> IndexIVFFlat (nlist=sqrt(n), nprobe=10-20)

Corpus 500K - 5M?
  └─> IndexHNSWFlat (M=32, ef=64-128)

Corpus > 5M or memory constrained?
  └─> IndexIVFPQ (compressed, ~90% recall)
```

## Production Checklist

- [ ] Benchmark recall on held-out queries before deploying
- [ ] Set `nprobe` / `efSearch` based on latency budget
- [ ] Use `faiss.write_index` for persistence
- [ ] Monitor p99 latency; increase search params if recall drops
- [ ] For updates: IVF supports `add()`, HNSW requires rebuild

## Related

- [LightRAG: Lean RAG with Benchmarks](/blogs/lightrag-fast-retrieval-augmented-generation)
- [BM25 Hybrid Search with LightRAG](/blogs/lightrag-bm25-hybrid-search)
