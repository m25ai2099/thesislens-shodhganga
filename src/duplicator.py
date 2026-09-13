import numpy as np
import faiss
from src.embedder import get_model, load_or_build


def check_duplicate(synopsis, df, top_k=5, threshold=0.85):
    """Check synopsis similarity against corpus."""
    from src.data_loader import load_data
    full_df = load_data()

    texts = (full_df["title"].fillna("") + ". " +
             full_df["abstract"].fillna("")).tolist()

    embeddings, index = load_or_build(texts)
    model = get_model()

    q_emb = model.encode([synopsis], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)

    # Search more to allow for filtering
    scores, indices = index.search(q_emb, min(top_k * 5, len(full_df)))

    # Filter to only records in filtered df
    filtered_ids = set(df.index.tolist())

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(full_df):
            continue

        if idx not in filtered_ids:
            continue

        row = full_df.iloc[idx]
        results.append({
            "similarity":   round(float(score) * 100, 1),
            "title":        row.get("title", ""),
            "author":       row.get("author", ""),
            "institution":  row.get("institution", ""),
            "year":         row.get("year", ""),
            "discipline":   row.get("discipline", "N/A"),
            "abstract":     str(row.get("abstract", ""))[:200],
            "is_duplicate": float(score) >= threshold
        })

        if len(results) >= top_k:
            break

    return results