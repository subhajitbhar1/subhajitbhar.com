---
authors:
    - subhajit
title: "LightRAG as a LangChain Retriever"
description: Integrate LightRAG's minimal retrieval into LangChain chains by implementing a custom BaseRetriever.
slug: lightrag-langchain-retriever-integration
draft: true
date:
    created: 2025-01-29
categories:
    - LLM Engineering
tags:
    - RAG
    - LightRAG
    - LangChain
    - Retrival
meta:
    - name: keywords
      content: LightRAG, LangChain, Retriever, RAG Integration, LangChain Retriever
---

Want LightRAG's lean retrieval with LangChain's chain ecosystem? Here's how to wrap LightRAG as a LangChain-compatible retriever.

<!-- more -->

## Why Combine LightRAG with LangChain

LightRAG gives you minimal, fast retrieval. LangChain gives you chains, agents, and tooling. Sometimes you want both:

- Use LightRAG's tight FAISS retrieval for speed
- Plug into LangChain chains for downstream processing
- Keep retrieval explicit while using LangChain's callbacks and tracing

## Implementing the Retriever

LangChain's `BaseRetriever` requires implementing `_get_relevant_documents`. Here's a complete wrapper:

```python
from typing import List
import faiss
import numpy as np
from openai import OpenAI
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun


class LightRAGRetriever(BaseRetriever):
    """LangChain retriever backed by LightRAG's FAISS index."""
    
    index: faiss.IndexFlatIP
    texts: List[str]
    sources: List[str]
    k: int = 4
    embedding_model: str = "text-embedding-3-small"
    
    class Config:
        arbitrary_types_allowed = True
    
    def _embed(self, text: str) -> np.ndarray:
        client = OpenAI()
        resp = client.embeddings.create(input=[text], model=self.embedding_model)
        vec = np.array([resp.data[0].embedding]).astype("float32")
        faiss.normalize_L2(vec)
        return vec
    
    def _get_relevant_documents(
        self, 
        query: str, 
        *, 
        run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        q = self._embed(query)
        D, I = self.index.search(q, self.k)
        
        docs = []
        for j, i in enumerate(I[0]):
            docs.append(Document(
                page_content=self.texts[i],
                metadata={"source": self.sources[i], "score": float(D[0][j])}
            ))
        return docs
```

## Building and Using the Retriever

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Build FAISS index (from LightRAG)
def build_lightrag_index(pairs):
    client = OpenAI()
    texts = [t for _, t in pairs]
    sources = [s for s, _ in pairs]
    
    vecs = client.embeddings.create(
        input=texts, 
        model="text-embedding-3-small"
    ).data
    X = np.array([v.embedding for v in vecs]).astype("float32")
    faiss.normalize_L2(X)
    
    idx = faiss.IndexFlatIP(X.shape[1])
    idx.add(X)
    return idx, texts, sources

# Create retriever
idx, texts, sources = build_lightrag_index(corpus_pairs)
retriever = LightRAGRetriever(index=idx, texts=texts, sources=sources, k=4)

# Use in LangChain chain
prompt = ChatPromptTemplate.from_template(
    "Answer from context only.\n\nContext: {context}\n\nQuestion: {question}"
)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

answer = chain.invoke("What is the return policy?")
```

## When to Use This Pattern

Use LightRAG + LangChain when:

- You need LangChain's tracing/callbacks but want lean retrieval
- Your team uses LangChain for other parts of the pipeline
- You want to gradually migrate from LangChain to pure LightRAG

Stick with pure LightRAG if you don't need LangChain's abstractions. See the [main LightRAG guide](/blogs/lightrag-fast-retrieval-augmented-generation) for the standalone approach.

## Related

- [LightRAG: Lean RAG with Benchmarks](/blogs/lightrag-fast-retrieval-augmented-generation)
- [Does LangChain Use RAG?](/blogs/does-langchain-use-rag)
