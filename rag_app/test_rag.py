import chromadb
from pathlib import Path
from tfidf_embedding import TfidfEmbeddingFunction
from rag import generate_answer

# Constants
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DB_DIR = BASE_DIR / "rag_app" / "chroma_db"
VECTORIZER_PATH = BASE_DIR / "rag_app" / "vectorizer.pkl"
COLLECTION_NAME = "real_estate"

def test_full_rag():
    print(f"[START] RAG Pipeline Test...")
    
    # 1. Retrieval
    print("[SEARCH] Searching for: '3 BHK in Mumbai'")
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    ef = TfidfEmbeddingFunction(vectorizer_path=str(VECTORIZER_PATH))
    collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
    
    query = "Give me 3 bhk properties in pune that are priced below 2 crores "
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    if not results['documents'][0]:
        print("[ERROR] No documents found")
        return

    contexts = results['documents'][0]
    print(f"[INFO] Retrieve {len(contexts)} contexts.")
    
    # 2. Generation
    print("[AI] Calling Gemini Model...")
    answer = generate_answer(query, contexts)
    
    print("\n--- AI RESPONSE ---")
    print(answer)
    print("-------------------")

if __name__ == "__main__":
    test_full_rag()
