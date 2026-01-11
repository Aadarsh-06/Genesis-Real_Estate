"""
Intent Classification Module for Genesis RAG System

Classifies user queries into one of:
- FILTER: User wants a subset of properties (search/browse)
- EXPLAIN: User wants reasoning behind a specific property's BUY/RENT decision
- COMPARE: User wants comparison between two or more properties
- EDUCATIONAL: User wants explanation of concepts (rent vs buy logic, EMI, tax)
- GREETING: Simple greeting (no RAG needed)
- CHITCHAT: Small talk (no RAG needed)

Intent classification runs BEFORE any Chroma retrieval.
"""

from dataclasses import dataclass
from typing import List
import re


@dataclass
class IntentResult:
    """Structured intent classification result."""
    intent: str
    confidence: float
    requires_retrieval: bool
    extracted_entities: dict
    clarification_needed: bool
    missing_info: List[str]


# ==================== PATTERN DEFINITIONS ====================

# GREETING patterns - no RAG needed
GREETING_PATTERNS = [
    r"^(hi|hello|hey+|howdy|greetings|yo)[\s!?.]*$",
    r"^good\s+(morning|afternoon|evening|day)[\s!?.]*$",
    r"^(namaste|namaskar)[\s!?.]*$",
]

# CHITCHAT patterns - no RAG needed
CHITCHAT_PATTERNS = [
    r"how are you",
    r"what'?s up",
    r"who are you",
    r"what is your name",
    r"thank(s| you)",
    r"(bye|goodbye|see you)",
    r"nice to meet",
    r"(help me|can you help)",
    r"what can you do",
    r"what do you do",
]

# EDUCATIONAL patterns - explain concepts, not specific properties
EDUCATIONAL_KEYWORDS = [
    # Concept questions
    "what is roi", "what is emi", "what is wealth difference",
    "how does emi work", "how is emi calculated", "emi calculation",
    "how does tax saving work", "tax benefit", "tax deduction", "80c", "24b",
    "what is appreciation", "property appreciation", "how appreciation works",
    "rent vs buy logic", "buy vs rent logic", "rent or buy decision",
    "wealth difference meaning", "wealth difference logic",
    "loan amortization", "how loan works", "interest calculation",
    "down payment", "how much down payment",
    "investment return", "sip", "mutual fund", "fd return",
    # General concept starters
    "explain the concept", "explain how", "what does .* mean",
    "how is .* calculated", "what are the factors",
    "why do we", "logic behind",
    "teach me", "tell me about", "i want to understand",
    "what factors", "how to decide", "general advice",
]

# COMPARE patterns - comparing properties
COMPARE_KEYWORDS = [
    "compare", "vs", "versus", "difference between",
    "which is better", "which one", "better option",
    "between .* and", "or should i", 
    "first property .* second", "property a .* property b",
    "both properties", "these two", "these properties",
    "comparing", "comparison",
]

# EXPLAIN patterns - specific property reasoning
EXPLAIN_KEYWORDS = [
    "why is buying better", "why is renting better",
    "why buy", "why rent", "why should i",
    "explain this property", "explain the decision",
    "reason for", "reasoning behind",
    "why this property", "what makes this",
    "how come", "justify",
    "why is .* recommended", "why does .* show",
    "the first property", "the second property", "property you showed",
    "for this property", "for that property",
    "breakdown", "detailed analysis",
]

# FILTER patterns - searching for properties
FILTER_KEYWORDS = [
    "show", "list", "find", "search", "get", "fetch", "display",
    "properties in", "apartments in", "flats in", "houses in",
    "bhk in", "bedroom in",
    "under .* lakhs", "below .* lakhs", "budget",
    "near", "around", "close to",
    "affordable", "cheap", "expensive", "luxury",
    "for rent", "for buy", "to rent", "to buy",
    "available", "options",
]

# Location entities - Only Bangalore, Surat, Mumbai available in database
LOCATIONS = [
    "mumbai", "bangalore", "bengaluru", "surat",
    # Mumbai localities
    "andheri", "bandra", "worli", "powai", "malad", "goregaon", "borivali",
    "dadar", "kurla", "chembur", "mulund", "thane", "navi mumbai",
    # Bangalore localities
    "whitefield", "electronic city", "koramangala", "indiranagar", "hsr layout",
    "marathahalli", "sarjapur", "hebbal", "yelahanka", "jp nagar", "btm layout",
    # Surat localities
    "adajan", "vesu", "piplod", "althan", "pal", "dumas", "athwa",
]


# ==================== CLASSIFICATION FUNCTIONS ====================

def extract_entities(query: str) -> dict:
    """Extract relevant entities from the query."""
    q = query.lower().strip()
    entities = {
        "locations": [],
        "bhk": None,
        "budget_min": None,
        "budget_max": None,
        "intent_keywords": [],
    }
    
    # Extract locations
    for loc in LOCATIONS:
        if loc in q:
            entities["locations"].append(loc)
    
    # Extract BHK
    bhk_match = re.search(r'(\d)\s*bhk', q)
    if bhk_match:
        entities["bhk"] = int(bhk_match.group(1))
    
    # Extract budget mentions
    budget_match = re.search(r'(\d+)\s*(lakh|lac|l|crore|cr)', q)
    if budget_match:
        amount = int(budget_match.group(1))
        unit = budget_match.group(2).lower()
        if unit in ["crore", "cr"]:
            amount *= 100  # Convert to lakhs
        
        if any(w in q for w in ["under", "below", "less than", "max", "upto"]):
            entities["budget_max"] = amount
        elif any(w in q for w in ["above", "over", "more than", "min", "atleast"]):
            entities["budget_min"] = amount
        else:
            # Default to max budget
            entities["budget_max"] = amount
    
    return entities


def classify_intent(query: str) -> IntentResult:
    """
    Classify user query into one of the defined intents.
    
    Returns an IntentResult with:
    - intent: The classified intent type
    - confidence: Confidence score (0-1)
    - requires_retrieval: Whether ChromaDB retrieval is needed
    - extracted_entities: Extracted locations, BHK, budget, etc.
    - clarification_needed: Whether more info is needed
    - missing_info: What info is missing
    """
    q = query.lower().strip()
    entities = extract_entities(query)
    
    # ========== GREETING CHECK ==========
    for pattern in GREETING_PATTERNS:
        if re.match(pattern, q, re.IGNORECASE):
            return IntentResult(
                intent="GREETING",
                confidence=1.0,
                requires_retrieval=False,
                extracted_entities=entities,
                clarification_needed=False,
                missing_info=[]
            )
    
    # ========== CHITCHAT CHECK ==========
    for pattern in CHITCHAT_PATTERNS:
        if re.search(pattern, q, re.IGNORECASE):
            return IntentResult(
                intent="CHITCHAT",
                confidence=0.95,
                requires_retrieval=False,
                extracted_entities=entities,
                clarification_needed=False,
                missing_info=[]
            )
    
    # ========== EDUCATIONAL CHECK ==========
    # Educational queries are about concepts, not specific properties
    for keyword in EDUCATIONAL_KEYWORDS:
        if re.search(keyword, q, re.IGNORECASE):
            return IntentResult(
                intent="EDUCATIONAL",
                confidence=0.9,
                requires_retrieval=True,  # May need context for examples
                extracted_entities=entities,
                clarification_needed=False,
                missing_info=[]
            )
    
    # ========== COMPARE CHECK ==========
    for keyword in COMPARE_KEYWORDS:
        if re.search(keyword, q, re.IGNORECASE):
            return IntentResult(
                intent="COMPARE",
                confidence=0.85,
                requires_retrieval=True,
                extracted_entities=entities,
                clarification_needed=False,
                missing_info=[]
            )
    
    # ========== EXPLAIN CHECK ==========
    # User asking about a specific property's decision
    for keyword in EXPLAIN_KEYWORDS:
        if re.search(keyword, q, re.IGNORECASE):
            return IntentResult(
                intent="EXPLAIN",
                confidence=0.85,
                requires_retrieval=True,
                extracted_entities=entities,
                clarification_needed=False,
                missing_info=[]
            )
    
    # ========== FILTER CHECK ==========
    # Check for filter keywords or property search patterns
    has_filter_keyword = any(re.search(kw, q, re.IGNORECASE) for kw in FILTER_KEYWORDS)
    has_location = len(entities["locations"]) > 0
    has_bhk = entities["bhk"] is not None
    
    # If has location or BHK or filter keyword, it's a FILTER intent
    if has_filter_keyword or has_location or has_bhk:
        # Check if query is too vague
        missing = []
        if not has_location:
            missing.append("location")
        
        # Very generic single-word queries
        generic_words = ["properties", "property", "flat", "flats", "apartment", 
                         "apartments", "house", "houses", "home", "homes"]
        is_too_vague = len(q.split()) <= 2 and any(w in q for w in generic_words) and not has_location
        
        return IntentResult(
            intent="FILTER",
            confidence=0.8 if has_location else 0.6,
            requires_retrieval=True,
            extracted_entities=entities,
            clarification_needed=is_too_vague,
            missing_info=missing if is_too_vague else []
        )
    
    # ========== DEFAULT: FILTER ==========
    # If we can't determine intent, treat as a filter query
    # but ask for clarification
    return IntentResult(
        intent="FILTER",
        confidence=0.5,
        requires_retrieval=True,
        extracted_entities=entities,
        clarification_needed=True,
        missing_info=["location"]
    )


def get_intent_string(query: str) -> str:
    """
    Backward-compatible function that returns just the intent string.
    Use classify_intent() for full structured result.
    """
    result = classify_intent(query)
    return result.intent


def is_query_broad(query: str) -> dict:
    """
    Check if a query needs clarification.
    Uses the new intent classification system.
    """
    result = classify_intent(query)
    
    return {
        "is_broad": result.clarification_needed,
        "missing": result.missing_info,
        "has_location": len(result.extracted_entities.get("locations", [])) > 0,
        "has_intent": result.confidence > 0.6,
        "is_concept_question": result.intent == "EDUCATIONAL"
    }


# ==================== EXAMPLES ====================

INTENT_EXAMPLES = {
    "FILTER": [
        "Show me 3 BHK apartments in Mumbai",
        "Properties in Bangalore under 1 crore",
        "Find 2 BHK flats in Pune",
        "List houses in Andheri",
        "Affordable apartments in Whitefield",
        "4 BHK in Bandra",
    ],
    "EXPLAIN": [
        "Why is buying better for the first property you showed?",
        "Explain why rent is recommended for this apartment",
        "What makes this property a good buy?",
        "Why should I buy this 3 BHK in Mumbai?",
        "Breakdown the decision for this property",
        "Justify the buy recommendation",
    ],
    "COMPARE": [
        "Compare the 2 BHK in Andheri vs the one in Bandra",
        "Which is better - property A or property B?",
        "Difference between these two apartments",
        "Should I go with the first or second option?",
        "Compare buying vs renting for 3 BHK in Pune",
    ],
    "EDUCATIONAL": [
        "What is ROI in real estate?",
        "How is EMI calculated?",
        "Explain the rent vs buy logic",
        "What is wealth difference?",
        "How do tax savings work for home loans?",
        "What factors affect property appreciation?",
        "Tell me about Section 80C benefits",
        "How to decide between renting and buying?",
    ],
    "GREETING": [
        "Hi",
        "Hello",
        "Hey there",
        "Good morning",
    ],
    "CHITCHAT": [
        "How are you?",
        "What can you do?",
        "Thank you",
        "Who are you?",
    ],
}


if __name__ == "__main__":
    # Test the classifier
    print("=" * 60)
    print("Intent Classification Examples")
    print("=" * 60)
    
    test_queries = [
        "Hi",
        "What is EMI?",
        "Show me 3 BHK in Mumbai",
        "Why is buying better for this property?",
        "Compare the first and second property",
        "Properties",
        "Apartments in Bangalore under 50 lakhs",
        "How does tax saving work?",
        "Explain the wealth difference logic",
    ]
    
    for query in test_queries:
        result = classify_intent(query)
        print(f"\nQuery: \"{query}\"")
        print(f"  Intent: {result.intent}")
        print(f"  Confidence: {result.confidence}")
        print(f"  Requires Retrieval: {result.requires_retrieval}")
        print(f"  Clarification Needed: {result.clarification_needed}")
        if result.extracted_entities["locations"]:
            print(f"  Locations: {result.extracted_entities['locations']}")
        if result.extracted_entities["bhk"]:
            print(f"  BHK: {result.extracted_entities['bhk']}")
