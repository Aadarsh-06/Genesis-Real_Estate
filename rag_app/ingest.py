import pandas as pd
import chromadb
from pathlib import Path
import os
from tqdm import tqdm
from tfidf_embedding import TfidfEmbeddingFunction

# Constants
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "calaculate_financial_terms" / "output" / "buy_vs_rent_FINAL_ANALYSIS.csv"
CHROMA_DB_DIR = BASE_DIR / "rag_app" / "chroma_db"
VECTORIZER_PATH = BASE_DIR / "rag_app" / "vectorizer.pkl"
COLLECTION_NAME = "real_estate"

def ingest_data():
    """
    Ingests the real-estate CSV data into a local ChromaDB using TF-IDF embeddings.
    """
    print(f"🚀 Starting ingestion from {DATA_PATH} using TF-IDF...")
    
    if not DATA_PATH.exists():
        print(f"❌ Error: Data file not found at {DATA_PATH}")
        return

    # Load Data
    df = pd.read_csv(DATA_PATH)
    df = df.fillna("")
    
    # Prepare Documents
    print(f"📄 Processing {len(df)} records...")
    documents = []
    metadatas = []
    ids = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        text_content = (
            f"Property: {row['title']}. "
            f"Location: {row['city']}, {row['location']}. "
            f"Details: {row['bedrooms']} BHK, {row['area_sqft']} sqft. "
            f"Price: ₹{row['price_lakhs']} Lakhs. "
            f"Rent: ₹{row['estimated_monthly_rent']}/month. "
            f"Buy vs Rent Decision: {row['decision']} (Wealth Diff: ₹{row['wealth_difference']})."
        )
        
        documents.append(text_content)
        metadatas.append({
            "city": str(row["city"]),
            "bedrooms": str(row["bedrooms"]),
            "price_lakhs": float(row["price_lakhs"]) if row["price_lakhs"] != "" else 0.0,
            "decision": str(row["decision"]),
            "source_row": idx
        })
        ids.append(str(idx))

    # Fit Vectorizer first (TF-IDF needs to know the vocabulary)
    print("🧠 Training TF-IDF vectorizer...")
    ef = TfidfEmbeddingFunction(vectorizer_path=str(VECTORIZER_PATH), max_features=384)
    ef.fit(documents)
    print("✅ Vectorizer trained and saved.")

    # Initialize ChromaDB Client
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    
    # Get or Create Collection
    try:
        # Note: Chroma might complain if we change embedding function on existing collection
        print(f"ℹ️  Recreating collection '{COLLECTION_NAME}'...")
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
        
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=ef)

    # Batch Ingestion
    BATCH_SIZE = 100
    total_batches = (len(documents) + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"💾 Ingesting into ChromaDB in {total_batches} batches...")
    
    for i in tqdm(range(0, len(documents), BATCH_SIZE)):
        batch_ids = ids[i : i + BATCH_SIZE]
        batch_docs = documents[i : i + BATCH_SIZE]
        batch_metas = metadatas[i : i + BATCH_SIZE]
        
        try:
            # Generate embeddings explicitly to debug/control types
            batch_embeddings = ef(batch_docs)
            
            collection.add(
                documents=batch_docs,
                embeddings=batch_embeddings,
                metadatas=batch_metas,
                ids=batch_ids
            )
        except Exception as e:
            print(f"\n❌ Error adding batch {i}: {e}")
            import traceback
            traceback.print_exc()
            break
        
    print(f"✅ Ingestion Complete! Collection '{COLLECTION_NAME}' has {collection.count()} documents.")

if __name__ == "__main__":
    ingest_data()
