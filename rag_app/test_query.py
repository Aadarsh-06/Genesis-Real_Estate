import chromadb
from pathlib import Path
from tfidf_embedding import TfidfEmbeddingFunction

# Constants
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DB_DIR = BASE_DIR / "rag_app" / "chroma_db"
VECTORIZER_PATH = BASE_DIR / "rag_app" / "vectorizer.pkl"
COLLECTION_NAME = "real_estate"

def test_query():
    print(f"🔎 querying {CHROMA_DB_DIR}...")
    
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    
    # Load the TF-IDF embedding function
    print("⏳ Loading embedding function...")
    ef = TfidfEmbeddingFunction(vectorizer_path=str(VECTORIZER_PATH))
    
    collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
    
    query_text = "3 BHK in Mumbai under 2 crores"
    print(f"❓ Query: '{query_text}'")
    
    results = collection.query(
        query_texts=[query_text],
        n_results=1
    )
    
    if not results['documents'][0]:
        print("❌ No results found.")
        return

    doc = results['documents'][0][0]
    meta = results['metadatas'][0][0]
    
    print("\n✅ Top Result:")
    print(f"📄 Content: {doc}")
    print(f"ℹ️  Metadata: {meta}")

if __name__ == "__main__":
    test_query()
