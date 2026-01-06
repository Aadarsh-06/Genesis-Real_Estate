def classify_intent(query: str) -> str:
    q = query.lower()

    if any(w in q for w in ["compare", "vs", "difference"]):
        return "COMPARE"
    if any(w in q for w in ["why", "explain", "reason"]):
        return "EXPLAIN"
    if any(w in q for w in ["show", "list", "find"]):
        return "FILTER"
    return "EDUCATIONAL"
