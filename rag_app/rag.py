import google.generativeai as genai
from config import GEMINI_API_KEY, LLM_MODEL

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Strict System Prompt
SYSTEM_PROMPT = """
You are a financial explanation assistant for real estate.

CRITICAL RULES:
1.  **NO NEW NUMBERS**: You MUST NOT strictly invent, estimate, or calculate any new numbers (ROI, Yield, EMI, etc.). Use ONLY the numbers provided in the context.
2.  **NO DECISIONS**: You MUST NOT make a BUY/RENT decision yourself. Report the decision found in the context.
3.  **EXPLAIN ONLY**: Your job is to Explain the "Why" behind the provided financial analysis.
4.  **CONSISTENCY**: Do not change the conclusions provided in the context.

Response Format:
- **Decision Overview**: Briefly state the decision (BUY vs RENT) found in the analysis.
- **Key Drivers**: Explain 2-3 key factors from the text (e.g., specific wealth difference, tax savings, EMI vs Rent).
- **Comparison**: Briefly compare the final wealth numbers if available.
"""

def generate_answer(question: str, contexts: list[str]) -> str:
    """
    Generates an answer using Gemini Flash based on strict context.
    """
    context_block = "\n\n---\n\n".join(contexts)
    
    prompt = f"""
    Context Data:
    {context_block}
    
    User Question:
    {question}
    
    Task: Explain the financial logic using ONLY the above context. Follow the CRITICAL RULES.
    """
    
    full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
    
    try:
        model = genai.GenerativeModel(
            model_name=LLM_MODEL
        )
        
        response = model.generate_content(full_prompt)
        
        # Check if we have a valid candidate
        if not response.candidates:
             return f"Error: No candidates returned. Feedback: {response.prompt_feedback}"
             
        candidate = response.candidates[0]
        if candidate.finish_reason != 1: # 1 = STOP
             return f"Error: Generation stopped. Reason: {candidate.finish_reason}. Safety: {candidate.safety_ratings}"
        
        # Safe text extraction
        if candidate.content and candidate.content.parts:
             return candidate.content.parts[0].text
        else:
             return "Error: Candidate has no content parts."

    except ValueError:
        # If response.text fails (e.g. safety block), return feedback
        return f"Error: blocked. Feedback: {response.prompt_feedback}"
    except Exception as e:
        return f"Error generating answer: {e}"
