import google.generativeai as genai
from rag_app.config import GEMINI_API_KEY, LLM_MODEL

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Base system prompt
BASE_SYSTEM_PROMPT = """You are Genesis, a professional real estate financial assistant.

CRITICAL RULES:
1. **NO INVENTED NUMBERS**: Use ONLY numbers from the provided context. Never calculate or estimate new values.
2. **NO PERSONAL ADVICE**: Report decisions found in the data, don't make your own recommendations.
3. **CLEAR COMMUNICATION**: Write in a clear, professional tone.
4. **STAY GROUNDED**: Only discuss properties mentioned in the context.

FORMATTING RULES (VERY IMPORTANT):
- Use clear paragraph breaks between each property (double line breaks)
- Use "---" horizontal rules between different properties
- Use **bold** for property type, location, and key numbers
- Keep each property description to 4-5 short lines
- Add blank lines for visual breathing room
- Do NOT use emojis

WRITING STYLE:
- Be professional and informative
- Use short sentences (1-2 lines each)
- Each property should be its own clear block
- Avoid emojis entirely
"""

# Intent-specific prompt additions
INTENT_PROMPTS = {
    "COMPARE": """
TASK: Compare properties in a clear, structured way.

FORMAT LIKE THIS:

Here is my comparison of these properties:

---

### Property 1: [Type] in [Location]

**Location:** [Area, City]
**Price:** ₹[X] Lakhs | **Rent:** ₹[X]/month
**Size:** [X] sqft

**Verdict:** [BUY/RENT] is better — you'd save ₹[X] in wealth.

---

### Property 2: [Type] in [Location]
[Same format...]

---

### Summary

[2-3 sentences comparing which is better overall based on the data]
""",
    
    "EXPLAIN": """
TASK: Explain the financial logic in a clear, structured way.

FORMAT LIKE THIS:

Let me break this down:

---

### The Numbers

- **Monthly EMI:** ₹[X]
- **Monthly Rent:** ₹[X]
- **Difference:** ₹[X]/month

---

### Long-term Impact

[2-3 sentences explaining the wealth difference]

---

### Bottom Line

[1-2 sentences with the conclusion]
""",
    
    "FILTER": """
TASK: Present properties in a clean, card-like format.

FORMAT EACH PROPERTY LIKE THIS (with clear separation):

---

### [X] BHK in [Location], [City]

**Size:** [X] sqft
**Price:** ₹[X] Lakhs
**Rent:** ₹[X]/month

**Recommendation:** [BUY/RENT] is financially better.
**Why?** You'd gain ₹[X] more in wealth.

---

[Repeat for each property with --- between them]

After all properties, ask if they want to see more.
""",
    
    "QUERY": """
TASK: Answer the question in a clean, readable format.

Use clear sections with headers (###).
Use --- between different topics.
Keep paragraphs short (2-3 sentences max).
Use bullet points for lists.
"""
}


def generate_answer(question: str, contexts: list[str], intent: str = "QUERY", 
                    page: int = 1, has_more: bool = False, total_in_db: int = 0) -> str:
    """
    Generates a human-like, conversational answer using Gemini.
    Shows ~5 properties with explanation and asks if user wants more.
    """
    context_block = "\n\n---\n\n".join(contexts)
    num_properties = len(contexts)
    
    # Get intent-specific prompt
    intent_prompt = INTENT_PROMPTS.get(intent, INTENT_PROMPTS["QUERY"])
    
    # Add continuation context
    if page > 1:
        continuation_note = f"\n\nNote: This is page {page}. The user asked for more properties."
    else:
        continuation_note = ""
    
    # Add "more available" prompt
    if has_more:
        more_prompt = f"""

IMPORTANT: After presenting these {num_properties} properties, end your response by asking:
"Would you like me to show you more properties? There are many more options available!"
"""
    else:
        more_prompt = ""
    
    prompt = f"""
{intent_prompt}

You have {num_properties} properties to discuss. Present them in a conversational, helpful way.
{continuation_note}
{more_prompt}

---
PROPERTY DATA:
{context_block}
---

USER QUESTION: {question}

Remember: 
- Be conversational and friendly, not like a database listing
- Explain each property briefly with key numbers
- Highlight the buy/rent recommendation and WHY
- Use markdown formatting for readability
"""
    
    full_prompt = f"{BASE_SYSTEM_PROMPT}\n\n{prompt}"
    
    try:
        model = genai.GenerativeModel(
            model_name=LLM_MODEL
        )
        
        response = model.generate_content(full_prompt)
        
        # Check if we have a valid candidate
        if not response.candidates:
             return f"Error: No response generated. Please try rephrasing your question."
             
        candidate = response.candidates[0]
        if candidate.finish_reason != 1: # 1 = STOP
             return f"Error: Generation incomplete. Please try again."
        
        # Safe text extraction
        if candidate.content and candidate.content.parts:
             return candidate.content.parts[0].text
        else:
             return "Error: Empty response. Please try again."

    except ValueError:
        return f"Error: Could not process this query. Please try rephrasing."
    except Exception as e:
        return f"Error: {str(e)}"


def generate_explanation(property_info: dict) -> str:
    """
    Generate a structured explanation for why BUY or RENT was chosen.
    Uses ONLY the pre-computed data - no new calculations or assumptions.
    """
    # Format numbers for display
    def format_currency(val):
        if val >= 10000000:  # 1 Crore+
            return f"₹{val/10000000:.2f} Cr"
        elif val >= 100000:  # 1 Lakh+
            return f"₹{val/100000:.2f} Lakhs"
        else:
            return f"₹{val:,.0f}"
    
    # Build the data block for the prompt
    decision = property_info.get("decision", "N/A")
    is_buy = "buy" in decision.lower()
    
    data_block = f"""
PROPERTY DETAILS (Pre-computed - DO NOT modify these numbers):
- Location: {property_info.get('bedrooms')} BHK in {property_info.get('location', '')}, {property_info.get('city')}
- Size: {property_info.get('area_sqft', 0):,.0f} sqft
- Price: ₹{property_info.get('price_lakhs', 0):.2f} Lakhs

FINANCIAL BREAKDOWN (Pre-computed by backend):
- Down Payment: {format_currency(property_info.get('down_payment', 0))}
- Loan Amount: {format_currency(property_info.get('loan_amount', 0))}
- Monthly EMI: {format_currency(property_info.get('monthly_emi', 0))}
- Effective EMI (after tax benefit): {format_currency(property_info.get('effective_emi', 0))}
- Monthly Rent: {format_currency(property_info.get('monthly_rent', 0))}
- Total Tax Saved (over loan tenure): {format_currency(property_info.get('total_tax_saved', 0))}

WEALTH PROJECTION (20-year outlook, pre-computed):
- Final Property Value: {format_currency(property_info.get('final_property_value', 0))}
- Final Renting Wealth (if invested instead): {format_currency(property_info.get('final_renting_wealth', 0))}
- Wealth Difference: {format_currency(abs(property_info.get('wealth_difference', 0)))}

DECISION: {decision}
"""

    prompt = f"""You are explaining a pre-computed BUY vs RENT decision to a user.

CRITICAL RULES:
1. DO NOT calculate or derive any new numbers
2. DO NOT make assumptions or add hypothetical scenarios
3. Use ONLY the numbers provided below
4. Be clear, trustworthy, and non-salesy
5. No speculative language

{data_block}

Generate a structured explanation in this EXACT format with proper spacing:

## Final Decision: {"BUY" if is_buy else "RENT"} is financially better

---

### EMI vs Rent Comparison

**Monthly EMI:** {format_currency(property_info.get('monthly_emi', 0))}
**Monthly Rent:** {format_currency(property_info.get('monthly_rent', 0))}
**Effective EMI (after tax):** {format_currency(property_info.get('effective_emi', 0))}

{"EMI is higher than rent, but you're building equity." if property_info.get('monthly_emi', 0) > property_info.get('monthly_rent', 0) else "EMI is lower than rent — buying is clearly more affordable monthly."}

---

### Long-term Wealth (20 Years)

**If you BUY:** Your property would be worth {format_currency(property_info.get('final_property_value', 0))}

**If you RENT:** Your invested savings would grow to {format_currency(property_info.get('final_renting_wealth', 0))}

**Wealth Difference:** {format_currency(abs(property_info.get('wealth_difference', 0)))} {"more with buying" if is_buy else "more with renting"}

---

### Tax Benefits

**Total Tax Saved:** {format_currency(property_info.get('total_tax_saved', 0))} over the loan tenure

This reduces your effective cost of buying significantly.

---

### Summary

{"**BUYING** wins because the property appreciation and tax benefits outweigh the higher monthly costs." if is_buy else "**RENTING** wins because investing the down payment and monthly savings generates more wealth than property appreciation."}

Be concise and use the exact numbers provided. Do not add disclaimers.
"""

    try:
        model = genai.GenerativeModel(model_name=LLM_MODEL)
        response = model.generate_content(prompt)
        
        if not response.candidates:
            return "Unable to generate explanation. Please try again."
        
        candidate = response.candidates[0]
        if candidate.content and candidate.content.parts:
            return candidate.content.parts[0].text
        else:
            return "Unable to generate explanation. Please try again."
            
    except Exception as e:
        return f"Error generating explanation: {str(e)}"


def generate_flip_explanation(property_info: dict) -> str:
    """
    Generate a structured explanation for what would flip the decision.
    Uses ONLY pre-computed flip thresholds - no new calculations or assumptions.
    """
    # Format numbers for display
    def format_currency(val):
        if val >= 10000000:  # 1 Crore+
            return f"₹{val/10000000:.2f} Cr"
        elif val >= 100000:  # 1 Lakh+
            return f"₹{val/100000:.2f} Lakhs"
        else:
            return f"₹{val:,.0f}"
    
    decision = property_info.get("decision", "N/A")
    is_buy = "buy" in decision.lower()
    opposite = "RENT" if is_buy else "BUY"
    current = "BUY" if is_buy else "RENT"
    
    # Get flip thresholds
    current_rate = property_info.get("current_interest_rate", 0)
    interest_flip = property_info.get("interest_rate_flip", 0)
    rent_flip = property_info.get("rent_flip", 0)
    holding_flip = property_info.get("holding_period_flip", 0)
    current_rent = property_info.get("monthly_rent", 0)
    
    # Build conditions list
    conditions = []
    if interest_flip and interest_flip > 0:
        direction = "increases above" if is_buy else "decreases below"
        conditions.append(f"Interest rates {direction} **{interest_flip}%** (currently {current_rate}%)")
    
    if rent_flip and rent_flip > 0:
        direction = "rises above" if is_buy else "falls below"
        conditions.append(f"Monthly rent {direction} **{format_currency(rent_flip)}** (currently {format_currency(current_rent)})")
    
    if holding_flip and holding_flip > 0:
        direction = "shorter than" if is_buy else "longer than"
        conditions.append(f"Ownership period is {direction} **{int(holding_flip)} years**")
    
    # Build the data block
    conditions_text = "\n".join([f"• {c}" for c in conditions]) if conditions else "• No significant flip conditions identified for this property"
    
    prompt = f"""You are explaining the sensitivity of a pre-computed BUY vs RENT decision.

CRITICAL RULES:
1. DO NOT calculate or derive any new numbers
2. DO NOT make predictions or forecasts
3. Use ONLY the flip thresholds provided below
4. Be informative and cautionary, not advisory
5. No speculative language

PROPERTY: {property_info.get('bedrooms')} BHK in {property_info.get('location', '')}, {property_info.get('city')}
CURRENT DECISION: {decision}
CURRENT INTEREST RATE: {current_rate}%
CURRENT MONTHLY RENT: {format_currency(current_rent)}

FLIP THRESHOLDS (Pre-computed by backend):
- Interest Rate Flip: {interest_flip}% (decision flips if rate {"exceeds" if is_buy else "falls below"} this)
- Rent Flip: {format_currency(rent_flip)} (decision flips if rent {"rises above" if is_buy else "falls below"} this)
- Holding Period Flip: {int(holding_flip) if holding_flip else "N/A"} years (decision flips if holding period is {"shorter" if is_buy else "longer"} than this)

Generate a structured explanation in this EXACT format with proper spacing:

## What Would Flip the Decision?

**Current Recommendation:** {current}

---

### The decision would change to {opposite} if:

{conditions_text}

---

### Sensitivity Analysis

**Interest Rate**
- Current: {current_rate}%
- Flip Threshold: {interest_flip}%

**Monthly Rent**
- Current: {format_currency(current_rent)}
- Flip Threshold: {format_currency(rent_flip)}

**Holding Period**
- Current: 20 years
- Flip Threshold: {int(holding_flip) if holding_flip else "N/A"} years

---

### Why This Matters

{"Higher interest rates would increase your EMI, making renting more attractive." if is_buy else "Lower interest rates would reduce EMI, making buying more attractive."}

{"If rent rises significantly, buying becomes the better choice." if is_buy else "If rent falls, the case for renting strengthens."}

Keep it factual and grounded in the pre-computed thresholds.
"""

    try:
        model = genai.GenerativeModel(model_name=LLM_MODEL)
        response = model.generate_content(prompt)
        
        if not response.candidates:
            return "Unable to generate flip explanation. Please try again."
        
        candidate = response.candidates[0]
        if candidate.content and candidate.content.parts:
            return candidate.content.parts[0].text
        else:
            return "Unable to generate flip explanation. Please try again."
            
    except Exception as e:
        return f"Error generating flip explanation: {str(e)}"


def parse_property_from_context(context: str) -> dict:
    """
    Parse property details from context string.
    Returns a dict with extracted property information.
    """
    import re
    
    property_info = {
        "type": "",
        "location": "",
        "price": "",
        "rent": "",
        "size": "",
        "decision": "",
        "wealth_diff": "",
        "raw": context
    }
    
    # Try to extract common patterns
    text = context.lower()
    
    # Property type (1/2/3/4 BHK)
    bhk_match = re.search(r'(\d+)\s*bhk', text)
    if bhk_match:
        property_info["type"] = f"{bhk_match.group(1)} BHK"
    
    # Location/City
    cities = ["mumbai", "delhi", "hyderabad", "bangalore", "bengaluru", "pune", "surat", 
              "chennai", "kolkata", "thane", "navi mumbai", "gurgaon", "noida"]
    for city in cities:
        if city in text:
            property_info["location"] = city.title()
            break
    
    # Price (in Lakhs/Cr)
    price_match = re.search(r'(?:price|cost)[:\s]*[₹rs.]*\s*([\d.]+)\s*(lakh|lakhs|cr|crore)?', text)
    if price_match:
        property_info["price"] = f"₹{price_match.group(1)} {price_match.group(2) or 'Lakhs'}"
    
    # Rent
    rent_match = re.search(r'rent[:\s]*[₹rs.]*\s*([\d,]+)', text)
    if rent_match:
        property_info["rent"] = f"₹{rent_match.group(1)}/month"
    
    # Size (sqft)
    size_match = re.search(r'([\d,]+)\s*(?:sq\.?\s*ft|sqft|square feet)', text)
    if size_match:
        property_info["size"] = f"{size_match.group(1)} sqft"
    
    # Decision (Buy/Rent)
    if "buying is" in text and "better" in text:
        property_info["decision"] = "BUY"
    elif "renting is" in text and "better" in text:
        property_info["decision"] = "RENT"
    elif "buy" in text and "decision" in text:
        property_info["decision"] = "BUY"
    elif "rent" in text and "decision" in text:
        property_info["decision"] = "RENT"
    
    # Wealth difference
    wealth_match = re.search(r'wealth\s*(?:diff|difference)[:\s]*[₹rs.]*\s*([\d,]+)', text)
    if wealth_match:
        property_info["wealth_diff"] = f"₹{wealth_match.group(1)}"
    
    return property_info


def format_property_listings(query: str, contexts: list[str], page: int, 
                             total_results: int, start_idx: int, end_idx: int) -> str:
    """
    Format property listings in a clean, bullet-based format.
    One listing per block, no truncation.
    """
    output_lines = []
    
    # Header
    output_lines.append(f"## 🔍 Property Listings")
    output_lines.append(f"**Showing results {start_idx + 1}–{end_idx} of {total_results}**\n")
    output_lines.append("---\n")
    
    for i, context in enumerate(contexts):
        prop = parse_property_from_context(context)
        listing_num = start_idx + i + 1
        
        # Property header
        prop_title = f"{prop['type']} Apartment" if prop['type'] else "Property"
        location = prop['location'] if prop['location'] else "Location not specified"
        
        output_lines.append(f"### {listing_num}. {prop_title} – {location}\n")
        
        # Property details as bullets
        if prop['price']:
            output_lines.append(f"• **Price**: {prop['price']}")
        if prop['size']:
            output_lines.append(f"• **Size**: {prop['size']}")
        if prop['rent']:
            output_lines.append(f"• **Rent**: {prop['rent']}")
        if prop['decision']:
            output_lines.append(f"• **Recommendation**: **{prop['decision']}**")
        if prop['wealth_diff']:
            output_lines.append(f"• **Wealth Difference**: {prop['wealth_diff']}")
        
        output_lines.append("")  # Empty line between listings
        output_lines.append("---\n")
    
    # Pagination footer
    total_pages = (total_results + 19) // 20  # PAGE_SIZE = 20
    if total_pages > 1:
        output_lines.append(f"\n**Page {page} of {total_pages}**")
        if page < total_pages:
            output_lines.append(f"*Send `page {page + 1}` or `more` to see next results*")
    
    return "\n".join(output_lines)
