---
authors:
    - subhajit
title: "NLP Entity Matching with Fuzzy Search"
description: Product catalogs rarely match 1:1. I combine lexical and semantic similarity with thresholds to minimize false matches.
slug: nlp-entity-matching-with-fuzzy-search
date:
    created: 2025-08-14
categories:
    - Python
    - NLP
meta:
    - name: keywords
      content: Entity Matching, Fuzzy Search, NLP
---

Product catalogs rarely match 1:1. I combine lexical and semantic similarity with thresholds to minimize false matches.

<!-- more -->

## Problem

Product catalogs rarely match 1:1. I combine lexical and semantic similarity with thresholds to minimize false matches.

## Approach

- Candidate generation with TF-IDF cosine
- Re-ranking with Jaro-Winkler for surface similarity
- Final semantic tie-breaker with small embeddings

```python
from __future__ import annotations
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def jaro_winkler(a: str, b: str) -> float:
    try:
        import jellyfish
        return jellyfish.jaro_winkler(a, b)
    except Exception:
        return 0.0


def match_entities(left: list[str], right: list[str], top_k: int = 5) -> list[tuple[str, str, float]]:
    tfidf = TfidfVectorizer(min_df=1, ngram_range=(1, 2))
    Xl = tfidf.fit_transform(left)
    Xr = tfidf.transform(right)
    sims = cosine_similarity(Xl, Xr)
    matches = []
    for i, row in enumerate(sims):
        idx = int(np.argmax(row))
        jw = jaro_winkler(left[i], right[idx])
        score = 0.7 * row[idx] + 0.3 * jw
        matches.append((left[i], right[idx], float(score)))
    return matches


if __name__ == "__main__":
    a = ["Apple iPhone 13 Pro", "Samsung Galaxy S22"]
    b = ["iPhone 13 Pro Max by Apple", "Galaxy S22 Ultra Samsung"]
    for m in match_entities(a, b):
        print(m)
```

## Thresholds and QA

- Accept ≥ 0.8 as confident match; 0.6–0.8 → manual review; < 0.6 reject.
- Evaluate with precision@1 and manual spot-checks.

## Architecture & workflow

1. Normalize product titles (case, unicode, punctuation)
2. Generate candidates via TF-IDF cosine (top-10)
3. Re-rank with Jaro-Winkler; compute blended score
4. Optional: embed with `text-embedding-3-small` for semantic tie-breakers
5. Threshold routing: accept/review/reject

## Evaluation harness

```python
from __future__ import annotations
import numpy as np


def precision_at_1(gold: list[tuple[str, str]], preds: list[tuple[str, str, float]]):
    lookup = {a: b for a, b in gold}
    hits = 0
    for a, b, _ in preds:
        hits += int(lookup.get(a) == b)
    return hits / max(1, len(preds))


if __name__ == "__main__":
    gold = [("Apple iPhone 13 Pro", "iPhone 13 Pro Max by Apple"), ("Samsung Galaxy S22", "Galaxy S22 Ultra Samsung")]
    preds = match_entities([g[0] for g in gold], [g[1] for g in gold])
    print({"p@1": precision_at_1(gold, preds)})
```

Target: ≥ 0.9 p@1 on clean catalogs; add human review queue for ambiguous ranges.

## Edge cases and fixes

- Brand aliases (e.g., Google vs Alphabet) → maintain alias map pre-match.
- Units and pack sizes ("500ml" vs "0.5 L") → normalize units.
- Noise tokens ("new", "sale") → remove stopwords tailored to catalog domain.

## Integrations

- Push accepted matches to MDM with versioned lineage.
- Emit ambiguous matches to a human-review dashboard with audit logs.
- Schedule nightly diffs; alert on drift in p@1.


