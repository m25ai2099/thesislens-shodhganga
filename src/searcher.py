import numpy as np
import faiss
import pandas as pd
from src.embedder import get_model, load_or_build


def search(query, df, top_k=10):
    """Search theses semantically using cached model and index."""
    # Always build index on FULL dataset
    # then filter results after
    from src.data_loader import load_data
    full_df = load_data()

    texts = (full_df["title"].fillna("") + ". " +
             full_df["abstract"].fillna("")).tolist()

    embeddings, index = load_or_build(texts)
    model = get_model()

    q_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)

    # Search more results than needed so we can filter
    scores, indices = index.search(q_emb, min(top_k * 5, len(full_df)))

    # Filter results to only those in filtered df
    filtered_ids = set(df.index.tolist())

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(full_df):
            continue

        # Only include if in filtered dataset
        if idx not in filtered_ids:
            continue

        row = full_df.iloc[idx]
        results.append({
            "score":       round(float(score), 4),
            "title":       row.get("title", ""),
            "abstract":    str(row.get("abstract", ""))[:300],
            "year":        row.get("year", ""),
            "author":      row.get("author", ""),
            "institution": row.get("institution", ""),
            "subjects":    row.get("subjects", ""),
            "discipline":  row.get("discipline", "N/A"),
        })

        if len(results) >= top_k:
            break

    return results