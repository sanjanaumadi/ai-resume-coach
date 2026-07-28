"""
Semantic (embedding-based) similarity between resume text and a job description.

Deliberately NOT using a vector database (ChromaDB) here - for a single
resume-vs-JD comparison, embedding both texts and computing cosine similarity
directly is simpler, faster, and has one less moving part than a database.
A vector DB earns its place when searching across many stored documents,
which isn't what this milestone needs.

The model loads lazily on first use and is cached in memory for the life of
the process, since loading it (~80MB download on first run, then fast) is
too slow to do per-request.
"""
from functools import lru_cache

import numpy as np


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def compute_semantic_similarity(resume_text: str, job_description: str) -> int:
    """Returns a 0-100 semantic similarity score between resume and JD text."""
    model = _get_model()
    embeddings = model.encode([resume_text, job_description])
    similarity = cosine_similarity(embeddings[0], embeddings[1])

    # Raw cosine similarity for unrelated sentence-embedding pairs rarely goes
    # below ~0.2 even for genuinely dissimilar text, so a naive *100 would
    # compress everything into a narrow 20-60 band. Rescale so the useful
    # range (0.2-0.9 in practice) spreads across the full 0-100 score.
    scaled = max(0.0, min(1.0, (similarity - 0.2) / 0.7))
    return round(scaled * 100)
