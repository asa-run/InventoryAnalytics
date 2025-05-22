from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re

def clean_json_block(content: str) -> str:
    # Remove markdown code block formatting like ```json ... ```
    cleaned = re.sub(r"^```json\n|\n```$|^```|\n```$", "", content.strip())
    return cleaned

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def classify_question(user_question: str, previous_question: str = "") -> dict:
    context_block = f"The previous question was: '{previous_question}'\n\n" if previous_question else ""

    prompt = f"""
{context_block}
You are an AI assistant for invoice analytics. Given a user question, extract structured intent as JSON.

REQUIRED FIELDS:
- intent: total_spend | trend | unit_cost | optimization | top_spender | extremes | unit_cost_trend
- target: e.g., "Cisco", "network switches"
- column: which column to filter on (e.g., "Manufacturer Part #", "Commodity Description")
- year or year_range (e.g., 2024 or [2022, 2023, 2024])
- group_by (optional)

NEVER leave out 'column' or 'target'. If missing in the question, use the previous question to infer them.

Return ONLY valid JSON.
User question: {user_question}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=300
    )

    import json
    try:
        cleaned = clean_json_block(response.choices[0].message.content)
        return json.loads(cleaned)
    except Exception:
        return {
            "intent": "unknown",
            "raw_output": response.choices[0].message.content
        }