import numpy as np
import os
from sentence_transformers import SentenceTransformer
import faiss

MODEL_NAME   = "allenai/specter2_base"
EMB_PATH     = "data/embeddings.npy"
INDEX_PATH   = "data/faiss.index"

_model = None
_index = None
_embeddings = None

def get_model():
    global _model
    if _model is None:
        print("Loading SPECTER2...")
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def build_embeddings(texts):
    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    np.save(EMB_PATH, embeddings)
    return embeddings

def build_index(embeddings):
    dim = embeddings.shape[1]
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)
    return index

def load_or_build(texts):
    global _index, _embeddings
    if os.path.exists(EMB_PATH) and os.path.exists(INDEX_PATH):
        _embeddings = np.load(EMB_PATH)
        _index = faiss.read_index(INDEX_PATH)
    else:
        _embeddings = build_embeddings(texts)
        emb_copy = _embeddings.copy()
        _index = build_index(emb_copy)
    return _embeddings, _index