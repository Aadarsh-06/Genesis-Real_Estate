from fastapi import FastAPI
from intent import classify_intent
from db import fetch_properties, fetch_explanations
from embeddings import semantic_search
from rag import generate_answer

app = FastAPI()


@app.post("/ask")
def ask(query: str):
    intent = classify_intent(query)

    # Step 1: SQL FIRST
    sql = """
    SELECT id, final_decision
    FROM properties_analysis
    WHERE city = :city
    LIMIT 5
    """

    # Example param extraction (simplified)
    city = "Surat"
    rows = fetch_properties(sql, {"city": city})

    property_ids = [r["id"] for r in rows]

    # Step 2: Semantic refinement (RAG)
    rag_ids = semantic_search(query)
    rag_ids = list(set(rag_ids) & set(property_ids))

    explanations = fetch_explanations(rag_ids)
    contexts = [e["explanation_text"] for e in explanations]

    # Step 3: Explain
    answer = generate_answer(query, contexts)

    return {
        "intent": intent,
        "answer": answer
    }
