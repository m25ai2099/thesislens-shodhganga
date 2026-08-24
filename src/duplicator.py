import numpy as np
from sentence_transformers import SentenceTransformer
from src.embedder import get_model, load_or_build

def check_duplicate(synopsis, df, top_k=5, threshold=0.85):
    """
    Check if a synopsis is similar to existing theses.
    Returns top matches with similarity scores.
    """
    texts = df["title"].fillna("") + ". " + df["abstract"].fillna("")
    embeddings, index = load_or_build(texts.tolist())

    model = get_model()

    import faiss
    q_emb = model.encode([synopsis], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)

    scores, indices = index.search(q_emb, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        row = df.iloc[idx]
        results.append({
            "similarity":  round(float(score) * 100, 1),
            "title":       row.get("title", ""),
            "author":      row.get("author", ""),
            "institution": row.get("institution", ""),
            "year":        row.get("year", ""),
            "abstract":    str(row.get("abstract", ""))[:200],
            "is_duplicate": float(score) >= threshold
        })
    return results