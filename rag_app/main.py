from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List
import re
import chromadb

from statistics import median
import numpy as np

from rag_app.intent import classify_intent, is_query_broad
from rag_app.tfidf_embedding import TfidfEmbeddingFunction
from rag_app.rag import generate_answer, generate_explanation, generate_flip_explanation

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Constants
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DB_DIR = BASE_DIR / "rag_app" / "chroma_db"
VECTORIZER_PATH = BASE_DIR / "rag_app" / "vectorizer.pkl"
COLLECTION_NAME = "real_estate"

# Initialize ChromaDB client and collection at startup
client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
ef = TfidfEmbeddingFunction(vectorizer_path=str(VECTORIZER_PATH))
collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)



# ...existing code...

# Helper function to get all property metadata
def get_all_metadatas():
    all_docs = collection.get(include=["metadatas"])
    metadatas = all_docs.get("metadatas", [])
    if not metadatas:
        return []
    if isinstance(metadatas[0], list):
        metadatas = [item for sublist in metadatas for item in sublist]
    return metadatas

# Get available filter options
@app.get("/market_filters")
def get_market_filters():
    """Returns available filter options for the market snapshot"""
    metadatas = get_all_metadatas()
    cities = ["Bangalore", "Mumbai"]
    
    # Get localities per city
    localities = {city: set() for city in cities}
    bhk_options = set()
    prices = []
    areas = []
    
    for meta in metadatas:
        city = meta.get("city", "").capitalize()
        if city in cities:
            loc = meta.get("location", "")
            if loc:
                localities[city].add(loc)
            
            # Extract BHK
            bedrooms = meta.get("bedrooms")
            if bedrooms:
                try:
                    bhk = int(float(bedrooms))
                    if 1 <= bhk <= 5:
                        bhk_options.add(bhk)
                except:
                    pass
            
            # Price range
            price = meta.get("price_lakhs")
            if price:
                try:
                    prices.append(float(price))
                except:
                    pass
            
            # Area range
            area = meta.get("area_sqft")
            if area:
                try:
                    areas.append(float(area))
                except:
                    pass
    
    return {
        "localities": {city: sorted(list(locs)) for city, locs in localities.items()},
        "bhk_options": sorted(list(bhk_options)),
        "price_range": {
            "min": round(min(prices), 0) if prices else 0,
            "max": round(max(prices), 0) if prices else 500
        },
        "area_range": {
            "min": round(min(areas), 0) if areas else 0,
            "max": round(max(areas), 0) if areas else 3000
        }
    }

# Place this after app, collection, etc. are defined
@app.get("/market_snapshot")
def market_snapshot(
    bhk: Optional[str] = Query(None, description="Comma-separated BHK values like '2,3'"),
    min_price: Optional[float] = Query(None, description="Min price in lakhs"),
    max_price: Optional[float] = Query(None, description="Max price in lakhs"),
    min_area: Optional[float] = Query(None, description="Min area in sqft"),
    max_area: Optional[float] = Query(None, description="Max area in sqft"),
    localities: Optional[str] = Query(None, description="Comma-separated localities")
):
    """Returns market snapshot with optional filters"""
    cities = ["Bangalore", "Mumbai"]
    metadatas = get_all_metadatas()
    
    if not metadatas:
        return {"error": "No data found"}

    # Parse filter values
    bhk_filter = [int(b.strip()) for b in bhk.split(",")] if bhk else None
    locality_filter = [l.strip() for l in localities.split(",")] if localities else None

    # Filter and organize by city
    city_data = {city: [] for city in cities}
    for meta in metadatas:
        city = meta.get("city", "").capitalize()
        if city not in city_data:
            continue
        
        # Apply BHK filter
        if bhk_filter:
            try:
                prop_bhk = int(float(meta.get("bedrooms", 0)))
                if prop_bhk not in bhk_filter:
                    continue
            except:
                continue
        
        # Apply price filter
        if min_price is not None or max_price is not None:
            try:
                price = float(meta.get("price_lakhs", 0))
                if min_price is not None and price < min_price:
                    continue
                if max_price is not None and price > max_price:
                    continue
            except:
                continue
        
        # Apply area filter
        if min_area is not None or max_area is not None:
            try:
                area = float(meta.get("area_sqft", 0))
                if min_area is not None and area < min_area:
                    continue
                if max_area is not None and area > max_area:
                    continue
            except:
                continue
        
        # Apply locality filter
        if locality_filter:
            prop_loc = meta.get("location", "")
            if prop_loc not in locality_filter:
                continue
        
        city_data[city].append(meta)

    # Check if we have enough data
    total_filtered = sum(len(props) for props in city_data.values())
    if total_filtered < 5:
        return {
            "error": "insufficient_data",
            "message": "Not enough data for selected filters",
            "total_filtered": total_filtered
        }

    # 1. BUY vs RENT Distribution
    buy_rent_dist = {}
    for city in cities:
        buy_count = sum(1 for m in city_data[city] if str(m.get("decision", "")).lower().startswith("buy"))
        rent_count = sum(1 for m in city_data[city] if str(m.get("decision", "")).lower().startswith("rent"))
        total = buy_count + rent_count
        buy_pct = round(100 * buy_count / total, 1) if total else 0
        rent_pct = round(100 * rent_count / total, 1) if total else 0
        buy_rent_dist[city] = {"buy": buy_pct, "rent": rent_pct, "buy_count": buy_count, "rent_count": rent_count, "total": total}

    # 2. Median Price per Sq Ft
    median_price_sqft = {}
    for city in cities:
        prices = []
        for m in city_data[city]:
            price = m.get("price_lakhs")
            area = m.get("area_sqft")
            if price and area and float(area) > 0:
                prices.append((float(price) * 100000) / float(area))
        median_price_sqft[city] = round(float(median(prices)), 0) if prices else 0

    # 3. Average Break-Even Year
    avg_break_even = {}
    for city in cities:
        years = []
        for m in city_data[city]:
            price = m.get("price_lakhs")
            rent = m.get("monthly_rent") or m.get("estimated_monthly_rent")
            if price and rent:
                try:
                    price_val = float(price) * 100000
                    rent_val = float(rent)
                    if rent_val > 0:
                        annual_rent = rent_val * 12
                        break_even_years = price_val / annual_rent
                        if 1 < break_even_years < 50:
                            years.append(break_even_years)
                except (ValueError, TypeError):
                    pass
        avg_break_even[city] = round(float(np.mean(years)), 1) if years else 0

    return {
        "buy_rent_distribution": buy_rent_dist,
        "median_price_per_sqft": median_price_sqft,
        "avg_break_even_year": avg_break_even,
        "total_filtered": total_filtered,
        "filters_applied": {
            "bhk": bhk_filter,
            "price_range": [min_price, max_price] if min_price or max_price else None,
            "area_range": [min_area, max_area] if min_area or max_area else None,
            "localities": locality_filter
        }
    }


class QueryRequest(BaseModel):
    query: str
    page: Optional[int] = 1  # For pagination


class ExplainRequest(BaseModel):
    source_row: int  # The source_row ID of the property to explain


# Direct responses for non-RAG intents
GREETING_RESPONSES = {
    "default": "Hello! I'm your Genesis Real Estate Assistant. I can help you understand property investment decisions, compare buy vs rent scenarios, and explain the financial logic behind property analyses. What would you like to know?"
}

CHITCHAT_RESPONSES = {
    "how are you": "I'm doing great, thanks for asking! Ready to help you with real estate insights.",
    "thank": "You're welcome! Feel free to ask if you have more questions about properties.",
    "bye": "Goodbye! Come back anytime you need help with real estate decisions.",
    "who are you": "I'm Genesis, your AI real estate assistant. I help explain financial decisions about properties - like whether to buy or rent, and why.",
    "what can you do": "I can help you:\n\n• **Understand buy vs rent decisions** for specific properties\n• **Explain the financial logic** behind investment analyses\n• **Compare properties** and their investment potential\n• **Answer questions** about EMI, ROI, wealth projections, and more\n\nJust ask about any property or financial concept!",
    "default": "I'm here to help with real estate questions! Ask me about properties, buy vs rent decisions, or financial analyses."
}

# Filter options for UI chips
# Only these cities are available in the database
FILTER_OPTIONS = {
    "cities": [
        {"label": "Mumbai", "value": "mumbai"},
        {"label": "Bangalore", "value": "bangalore"},
        {"label": "Surat", "value": "surat"}
    ],
    "property_types": [
        {"label": "1 BHK", "value": "1bhk"},
        {"label": "2 BHK", "value": "2bhk"},
        {"label": "3 BHK", "value": "3bhk"},
        {"label": "4 BHK", "value": "4bhk"}
    ],
    "intent": [
        {"label": "Buy", "value": "buy"},
        {"label": "Rent", "value": "rent"}
    ]
}


def get_chitchat_response(query: str) -> str:
    """Get appropriate response for chitchat queries."""
    q = query.lower()
    for key, response in CHITCHAT_RESPONSES.items():
        if key in q:
            return response
    return CHITCHAT_RESPONSES["default"]


# Number of properties to show initially
INITIAL_RESULTS = 5


def parse_filters_from_query(query: str) -> dict:
    """Extract city, bedrooms, and intent filters from query text."""
    q = query.lower()
    filters = {}
    
    # City detection - support multiple cities for comparison queries
    cities = []
    if "mumbai" in q:
        cities.append("Mumbai")
    if "bangalore" in q or "bengaluru" in q:
        cities.append("Bangalore")
    if "surat" in q:
        cities.append("Surat")
    
    # If multiple cities, store as list for comparison; otherwise single city
    if len(cities) == 1:
        filters["city"] = cities[0]
    elif len(cities) > 1:
        filters["cities"] = cities  # Multiple cities for comparison
    
    # Bedroom detection
    bhk_match = re.search(r'(\d)\s*bhk', q)
    if bhk_match:
        filters["bedrooms"] = bhk_match.group(1)  # Store as "3" not "3.0"
    
    # Buy vs Rent preference (for context in prompts)
    if "rent" in q and "buy" not in q:
        filters["prefer_rent"] = True
    elif "buy" in q and "rent" not in q:
        filters["prefer_buy"] = True
    
    return filters


def build_chroma_where_clause(filters: dict) -> dict:
    """Build ChromaDB where clause from parsed filters."""
    conditions = []
    
    # Handle single city
    if "city" in filters:
        conditions.append({"city": {"$eq": filters["city"]}})
    # Handle multiple cities (for comparison queries)
    elif "cities" in filters:
        conditions.append({"city": {"$in": filters["cities"]}})
    
    if "bedrooms" in filters:
        conditions.append({"bedrooms": {"$eq": filters["bedrooms"]}})
    
    if len(conditions) == 0:
        return None
    elif len(conditions) == 1:
        return conditions[0]
    else:
        return {"$and": conditions}


@app.post("/ask")
def ask(request: QueryRequest):
    query = request.query
    page = request.page or 1
    
    # ========== STEP 1: INTENT CLASSIFICATION (BEFORE RETRIEVAL) ==========
    intent_result = classify_intent(query)
    intent = intent_result.intent
    
    # Log intent for debugging
    print(f"[INTENT] Query: '{query}' -> Intent: {intent} (confidence: {intent_result.confidence})")

    # ========== STEP 2: HANDLE NON-RETRIEVAL INTENTS ==========
    
    # Handle greetings - no RAG needed
    if intent == "GREETING":
        return {
            "intent": intent,
            "answer": GREETING_RESPONSES["default"],
            "requires_retrieval": False
        }
    
    # Handle chitchat - no RAG needed
    if intent == "CHITCHAT":
        return {
            "intent": intent,
            "answer": get_chitchat_response(query),
            "requires_retrieval": False
        }

    # ========== STEP 3: CHECK IF CLARIFICATION NEEDED ==========
    if intent_result.clarification_needed:
        return {
            "intent": "CLARIFICATION_NEEDED",
            "answer": "Let me help you find the perfect property! Select your preferences below:",
            "show_filters": True,
            "filters": {
                "cities": FILTER_OPTIONS["cities"],
                "property_types": FILTER_OPTIONS["property_types"],
                "intent": FILTER_OPTIONS["intent"]
            },
            "missing": intent_result.missing_info,
            "requires_retrieval": False
        }

    # ========== STEP 4: RETRIEVAL FOR PROPERTY-RELATED INTENTS ==========
    # Now we know we need to retrieve from ChromaDB
    
    # Use extracted entities for filtering
    entities = intent_result.extracted_entities
    parsed_filters = parse_filters_from_query(query)
    where_clause = build_chroma_where_clause(parsed_filters)
    
    # Query is specific enough - run retrieval with filters
    n_results = INITIAL_RESULTS if page == 1 else INITIAL_RESULTS * page
    
    # Use metadata filtering if we have specific filters
    try:
        if where_clause:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )
        else:
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
    except Exception as e:
        # Fallback to unfiltered query if filter fails
        print(f"Filter query failed: {e}, falling back to unfiltered")
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )

    # Extract contexts and metadatas
    all_contexts = results['documents'][0] if results['documents'] and results['documents'][0] else []
    all_metadatas = results['metadatas'][0] if results.get('metadatas') and results['metadatas'][0] else []

    if not all_contexts:
        return {
            "intent": intent,
            "answer": "I couldn't find any properties matching your query. Try specifying a city like Mumbai, Bangalore, or Surat with a property type (1-5 BHK).",
            "total_results": 0,
            "properties": []
        }

    total_in_db = collection.count()
    results_shown = len(all_contexts)
    
    # For pagination, get the contexts for current "page"
    if page > 1:
        start_idx = INITIAL_RESULTS * (page - 1)
        page_contexts = all_contexts[start_idx:start_idx + INITIAL_RESULTS]
        page_metadatas = all_metadatas[start_idx:start_idx + INITIAL_RESULTS]
    else:
        page_contexts = all_contexts[:INITIAL_RESULTS]
        page_metadatas = all_metadatas[:INITIAL_RESULTS]
    
    has_more = results_shown < total_in_db

    # Build structured property cards from metadata
    properties = []
    for i, (ctx, meta) in enumerate(zip(page_contexts, page_metadatas)):
        # Parse property info from context text
        prop = {
            "id": i + 1,
            "source_row": meta.get("source_row"),  # Include source_row for "Why?" feature
            "city": meta.get("city", "Unknown"),
            "location": meta.get("location", ""),
            "bedrooms": meta.get("bedrooms", "N/A"),
            "decision": meta.get("decision", "N/A"),
            "price_lakhs": meta.get("price_lakhs", 0),
        }
        
        # Extract more details from context string
        import re
        area_match = re.search(r'(\d+\.?\d*)\s*sqft', ctx)
        rent_match = re.search(r'Rent:\s*₹([\d,]+)', ctx)
        wealth_match = re.search(r'Wealth Diff:\s*₹([\d,\-]+)', ctx)
        
        prop["area_sqft"] = float(area_match.group(1)) if area_match else None
        prop["monthly_rent"] = rent_match.group(1) if rent_match else None
        prop["wealth_difference"] = wealth_match.group(1) if wealth_match else None
        
        properties.append(prop)

    # Generate a brief summary instead of detailed text
    answer = generate_answer(query, page_contexts, intent, page, has_more, total_in_db)
    
    return {
        "intent": intent,
        "answer": answer,
        "properties": properties,
        "total_results": total_in_db,
        "page": page,
        "results_shown": results_shown,
        "has_more": has_more
    }


@app.post("/explain")
def explain_property(request: ExplainRequest):
    """
    Explain why BUY or RENT was chosen for a specific property.
    Uses only pre-computed data from the backend - no new calculations.
    """
    source_row = request.source_row
    
    try:
        # Retrieve the property by source_row from ChromaDB
        result = collection.get(
            ids=[str(source_row)],
            include=["documents", "metadatas"]
        )
        
        if not result["ids"]:
            return {
                "success": False,
                "error": "Property not found"
            }
        
        # Extract property data
        document = result["documents"][0]
        metadata = result["metadatas"][0]
        
        # Build property info dict for explanation
        property_info = {
            "city": metadata.get("city", "Unknown"),
            "location": metadata.get("location", ""),
            "bedrooms": metadata.get("bedrooms", "N/A"),
            "price_lakhs": metadata.get("price_lakhs", 0),
            "area_sqft": metadata.get("area_sqft", 0),
            "decision": metadata.get("decision", "N/A"),
            "monthly_rent": metadata.get("monthly_rent", 0),
            "monthly_emi": metadata.get("monthly_emi", 0),
            "effective_emi": metadata.get("effective_emi", 0),
            "down_payment": metadata.get("down_payment", 0),
            "loan_amount": metadata.get("loan_amount", 0),
            "total_tax_saved": metadata.get("total_tax_saved", 0),
            "final_property_value": metadata.get("final_property_value", 0),
            "final_renting_wealth": metadata.get("final_renting_wealth", 0),
            "wealth_difference": metadata.get("wealth_difference", 0)
        }
        
        # Generate the structured explanation using LLM
        explanation = generate_explanation(property_info)
        
        return {
            "success": True,
            "property": property_info,
            "explanation": explanation
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/flip")
def flip_property(request: ExplainRequest):
    """
    Explain what would flip the BUY/RENT decision for a specific property.
    Uses only pre-computed sensitivity thresholds - no new calculations.
    """
    source_row = request.source_row
    
    try:
        # Retrieve the property by source_row from ChromaDB
        result = collection.get(
            ids=[str(source_row)],
            include=["documents", "metadatas"]
        )
        
        if not result["ids"]:
            return {
                "success": False,
                "error": "Property not found"
            }
        
        # Extract property data
        metadata = result["metadatas"][0]
        
        # Build property info dict for flip explanation
        property_info = {
            "city": metadata.get("city", "Unknown"),
            "location": metadata.get("location", ""),
            "bedrooms": metadata.get("bedrooms", "N/A"),
            "price_lakhs": metadata.get("price_lakhs", 0),
            "decision": metadata.get("decision", "N/A"),
            "monthly_rent": metadata.get("monthly_rent", 0),
            "monthly_emi": metadata.get("monthly_emi", 0),
            # Flip thresholds (pre-computed)
            "current_interest_rate": metadata.get("current_interest_rate", 0),
            "interest_rate_flip": metadata.get("interest_rate_flip", 0),
            "rent_flip": metadata.get("rent_flip", 0),
            "holding_period_flip": metadata.get("holding_period_flip", 0)
        }
        
        # Generate the flip explanation using LLM
        explanation = generate_flip_explanation(property_info)
        
        return {
            "success": True,
            "property": property_info,
            "explanation": explanation
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
