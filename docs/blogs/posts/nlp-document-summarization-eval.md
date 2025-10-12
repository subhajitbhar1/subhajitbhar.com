---
authors:
    - subhajit
title: "Document Summarization: Eval First"
description: Develop a summarization workflow using dataset splits, ROUGE/BERTScore, and human evaluation checklists for extractive and abstractive methods.
slug: nlp-document-summarization-eval
date:
    created: 2025-08-14
categories:
    - Python
    - NLP
meta:
    - name: keywords
      content: NLP, Summarization, Evaluation, Python
twitter_card: "summary_large_image"
---

Document summarization is a critical NLP task that helps users quickly grasp key information from long documents. But how do you know if your model is actually working? This guide shows a workflow that starts with evaluation and acceptance criteria before touching models.

<!-- more -->
## Why eval-first

When I built an extractive summarizer for finance reports, we shipped faster by defining evaluation and acceptance criteria before touching models.

## Workflow

1. Curate a small, representative dataset (20–50 docs)
2. Define extractive baseline + abstractive model
3. Compute ROUGE/BERTScore, then human checklist (coverage, faithfulness)
4. Review failure modes and iterate on chunking/prompts

```python
from __future__ import annotations
from datasets import load_metric


def rouge(refs: list[str], hyps: list[str]):
    metric = load_metric("rouge")
    scores = metric.compute(predictions=hyps, references=refs)
    return {k: v.mid.fmeasure for k, v in scores.items()}


if __name__ == "__main__":
    refs = ["Revenue increased due to subscriptions and lower churn."]
    hyps = ["Revenue increased from new subscriptions; churn was lower."]
    print(rouge(refs, hyps))
```

## Human checklist (print and use)

- Coverage: all key bullets present?
- Faithfulness: no invented numbers or facts?
- Specificity: numbers and entities preserved?
- Brevity: remove filler and boilerplate?

Related: RAG and data quality posts to improve chunking/grounding: 
[/blogs/does-langchain-use-rag](/blogs/does-langchain-use-rag), [/blogs/lightrag-fast-retrieval-augmented-generation](/blogs/lightrag-fast-retrieval-augmented-generation), and [/blogs/detect-remove-outliers-python-iqr-zscore](/blogs/detect-remove-outliers-python-iqr-zscore).

## CTA

Need production summarization with scorecards and human-in-the-loop review? [Work with me →](/services)

## Architecture

![Summarization workflow: ingest → segment → extractive baseline → abstractive refine → scoring → human review](/images/nlp-summarization-architecture.png)

1. Ingest and clean text (see text-cleaning pipeline)
2. Segment by sections; avoid cross-topic chunks
3. Extractive baseline (TextRank or embedding-based key sentence selection)
4. Abstractive refinement with constrained prompting
5. Score with ROUGE/BERTScore + human checklist

## Extractive baseline example

```python
from __future__ import annotations
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def textrank_sentences(sentences: list[str], top_k: int = 5) -> list[str]:
    tfidf = TfidfVectorizer().fit_transform(sentences)
    sim = (tfidf * tfidf.T).A
    scores = sim.sum(axis=1)
    idx = np.argsort(-scores)[:top_k]
    return [sentences[i] for i in sorted(idx)]
```

## Abstractive refinement prompt (LLM)

```text
You are summarizing a section for financial analysts.
Constraints:
- Keep numbers and entities accurate.
- No claims beyond the provided sentences.
- Max 120 words.

Sentences:
<paste extractive sentences>
```

## Metrics and acceptance criteria

- ROUGE-L ≥ 0.35 on validation set; BERTScore-F1 ≥ 0.86 on domain corpus.
- Human checklist pass rate ≥ 0.9 (sampled 20 summaries weekly).
- Drift alerts if either metric drops ≥ 10% week-over-week.

## Failure modes and fixes

- Missing critical bullet: increase top_k extractive or re-segment by section headings.
- Fabricated numbers: add unit tests scanning for number changes vs source.
- Repetition/bloat: enforce word cap and remove boilerplate via cleaning.

## Integration notes

- Store source sentence IDs alongside summaries for traceability.
- Log tokens, latency, and scores for each job; create dashboards.
- For long docs, summarize sections first, then synthesize an executive summary.


