import numpy as np
import faiss
from src.embedder import get_model, load_or_build

def search(query, df, top_k=10):
    """Search theses semantically."""
    texts = df["title"].fillna("") + ". " + df["abstract"].fillna("")
    embeddings, index = load_or_build(texts.tolist())

    model = get_model()
    q_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)

    scores, indices = index.search(q_emb, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        row = df.iloc[idx]
        results.append({
            "score":       round(float(score), 4),
            "title":       row.get("title", ""),
            "abstract":    str(row.get("abstract", ""))[:300],
            "year":        row.get("year", ""),
            "author":      row.get("author", ""),
            "institution": row.get("institution", ""),
            "subjects":    row.get("subjects", ""),
        })
    return results