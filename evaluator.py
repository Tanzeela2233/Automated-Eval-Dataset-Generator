import json
import os
from groq import Groq

MODEL = "openai/gpt-oss-20b"


def _client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key = None

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to Streamlit Secrets or your local environment."
        )

    return Groq(api_key=api_key)


def _extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:-1]
        text = "\n".join(lines)
    return json.loads(text)


def evaluate_one(client, row, topic):
    prompt = f"""
Evaluate this evaluation-dataset example for the task/domain:
{topic}

INPUT:
{row["input"]}

EXPECTED OUTPUT:
{row["expected_output"]}

Assess:
- relevance to the task
- clarity
- correctness/verifiability
- usefulness for evaluating an AI system
- absence of ambiguity

Return ONLY valid JSON:
{{
  "score": 0,
  "passed": true,
  "reason": "short explanation"
}}

Score from 0 to 10. Set passed=true when score >= 7.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a strict but fair evaluation-dataset quality reviewer. Return only valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_completion_tokens=800,
    )

    result = _extract_json(response.choices[0].message.content)

    score = max(0, min(10, int(result.get("score", 0))))
    return {
        "score": score,
        "passed": bool(result.get("passed", score >= 7)),
        "reason": str(result.get("reason", "No reason provided.")).strip(),
    }


def evaluate_dataset(rows, topic):
    client = _client()
    results = []

    for row in rows:
        evaluation = evaluate_one(client, row, topic)
        results.append({**row, "evaluation": evaluation})

    return results
