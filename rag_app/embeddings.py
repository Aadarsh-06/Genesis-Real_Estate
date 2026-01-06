import faiss
import numpy as np
from openai import OpenAI
from config import OPENAI_API_KEY, EMBEDDING_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

index = faiss.read_index("faiss.index")

# mapping: faiss_index -> property_id
property_id_map = np.load("id_map.npy")


def embed(text: str) -> np.ndarray:
    res = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return np.array(res.data[0].embedding).astype("float32")


def semantic_search(query: str, top_k=3):
    q_vec = embed(query).reshape(1, -1)
    _, indices = index.search(q_vec, top_k)
    return [int(property_id_map[i]) for i in indices[0]]
