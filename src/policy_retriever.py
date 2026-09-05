from __future__ import annotations
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .config import DATA_DIR

def retrieve_policies(query: str, top_k: int = 3) -> list[dict]:
    sections = []
    for path in (DATA_DIR / "policies").glob("*.txt"):
        for i, text in enumerate(filter(str.strip, path.read_text(encoding="utf-8").split("\n\n")), 1):
            sections.append({"source": path.name, "section": i, "text": text})
    if not sections: return []
    matrix = TfidfVectorizer(stop_words="english").fit_transform([query] + [s["text"] for s in sections])
    scores = cosine_similarity(matrix[0], matrix[1:]).ravel()
    return [dict(sections[i], relevance=float(scores[i])) for i in scores.argsort()[::-1][:top_k] if scores[i] > 0]

