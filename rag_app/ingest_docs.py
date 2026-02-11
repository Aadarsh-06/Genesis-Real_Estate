"""
Documentation Ingestion Script for Genesis RAG System

Creates a second ChromaDB collection for educational content:
- Simulation assumptions
- Tax rules and benefits
- Decision logic explanations

This collection is used for EDUCATIONAL intent queries.
"""

import chromadb
from pathlib import Path
from tfidf_embedding import TfidfEmbeddingFunction
import re

# Constants
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "documentation"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"
VECTORIZER_PATH = BASE_DIR / "vectorizer_docs.pkl"
COLLECTION_NAME = "documentation"


def chunk_document(content: str, chunk_size: int = 500) -> list[dict]:
    """
    Split a markdown document into semantic chunks.
    Each chunk includes the section header for context.
    """
    chunks = []
    
    # Split by headers (##, ###)
    sections = re.split(r'\n(?=#{1,3}\s)', content)
    
    current_header = ""
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        # Extract header if present
        header_match = re.match(r'^(#{1,3}\s+.+?)(?:\n|$)', section)
        if header_match:
            current_header = header_match.group(1).strip()
        
        # If section is too long, split into smaller chunks
        if len(section) > chunk_size:
            # Split by paragraphs
            paragraphs = section.split('\n\n')
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk) + len(para) < chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk.strip():
                        chunks.append({
                            "content": current_chunk.strip(),
                            "header": current_header
                        })
                    current_chunk = para + "\n\n"
            
            if current_chunk.strip():
                chunks.append({
                    "content": current_chunk.strip(),
                    "header": current_header
                })
        else:
            chunks.append({
                "content": section,
                "header": current_header
            })
    
    return chunks


def ingest_documentation():
    """
    Ingests markdown documentation files into ChromaDB.
    """
    print(f"🚀 Starting documentation ingestion from {DOCS_DIR}...")
    
    if not DOCS_DIR.exists():
        print(f"❌ Error: Documentation directory not found at {DOCS_DIR}")
        return
    
    # Find all markdown files
    md_files = list(DOCS_DIR.glob("*.md"))
    if not md_files:
        print(f"❌ Error: No markdown files found in {DOCS_DIR}")
        return
    
    print(f"📄 Found {len(md_files)} documentation files")
    
    # Process all documents
    documents = []
    metadatas = []
    ids = []
    
    doc_id = 0
    for md_file in md_files:
        print(f"  📖 Processing {md_file.name}...")
        
        content = md_file.read_text(encoding="utf-8")
        
        # Get document category from filename
        category = md_file.stem.replace("_", " ").title()
        
        # Chunk the document
        chunks = chunk_document(content)
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk["content"])
            metadatas.append({
                "source_file": md_file.name,
                "category": category,
                "section": chunk["header"],
                "chunk_index": i,
                "doc_type": "documentation"
            })
            ids.append(f"doc_{doc_id}")
            doc_id += 1
        
        print(f"    → Created {len(chunks)} chunks")
    
    print(f"\n📊 Total chunks: {len(documents)}")
    
    # Train TF-IDF on documentation
    print("🧠 Training TF-IDF vectorizer for documentation...")
    ef = TfidfEmbeddingFunction(vectorizer_path=str(VECTORIZER_PATH), max_features=384)
    ef.fit(documents)
    print("✅ Vectorizer trained and saved.")
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    
    # Delete existing collection if exists
    try:
        print(f"ℹ️  Recreating collection '{COLLECTION_NAME}'...")
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=ef)
    
    # Add documents
    print("💾 Ingesting into ChromaDB...")
    
    try:
        embeddings = ef(documents)
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Ingestion Complete! Collection '{COLLECTION_NAME}' has {collection.count()} chunks.")
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()


def test_query():
    """Test the documentation collection with a sample query."""
    print("\n" + "=" * 50)
    print("Testing Documentation Collection")
    print("=" * 50)
    
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    ef = TfidfEmbeddingFunction(vectorizer_path=str(VECTORIZER_PATH))
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
    except Exception as e:
        print(f"❌ Collection not found: {e}")
        return
    
    test_queries = [
        "What is EMI and how is it calculated?",
        "What tax benefits are available for home loans?",
        "How does Genesis decide between buy and rent?",
        "What appreciation rate is used?",
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: '{query}'")
        
        results = collection.query(
            query_texts=[query],
            n_results=1
        )
        
        if results['documents'][0]:
            doc = results['documents'][0][0]
            meta = results['metadatas'][0][0]
            print(f"📄 Source: {meta['source_file']} → {meta['section']}")
            print(f"📝 {doc[:200]}...")


if __name__ == "__main__":
    ingest_documentation()
    test_query()
