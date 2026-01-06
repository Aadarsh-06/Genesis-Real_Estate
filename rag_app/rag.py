from openai import OpenAI
from config import OPENAI_API_KEY, LLM_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = """
You are a financial explanation assistant.

Rules:
- You MUST NOT calculate numbers.
- You MUST NOT invent values.
- You MUST ONLY explain using the provided context.
- Do NOT change conclusions.
- Do NOT introduce new assumptions.
"""


def generate_answer(question: str, contexts: list[str]) -> str:
    context_block = "\n\n".join(contexts)

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Question:
{question}

Verified Context:
{context_block}

Explain the reasoning clearly.
"""
            }
        ]
    )

    return response.choices[0].message.content
