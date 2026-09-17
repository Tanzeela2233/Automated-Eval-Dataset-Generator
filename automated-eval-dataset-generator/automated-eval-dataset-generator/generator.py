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


def generate_dataset(topic: str, count: int, difficulty: str):
    client = _client()

    prompt = f"""
You are an expert evaluation-dataset designer.

Create exactly {count} evaluation examples for this task/domain:
{topic}

Difficulty: {difficulty}

Each example must test a useful capability rather than repeat another example.
Make examples diverse, realistic, and self-contained.

Return ONLY valid JSON in this exact shape:
[
  {{
    "input": "the user/task input",
    "expected_output": "the ideal answer or expected behavior"
  }}
]

Do not include markdown, commentary, or extra keys.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You create precise, diverse evaluation datasets and always return valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_completion_tokens=8000,
    )

    data = _extract_json(response.choices[0].message.content)

    if not isinstance(data, list):
        raise ValueError("The model did not return a JSON list.")

    cleaned = []
    for item in data:
        if not isinstance(item, dict):
            continue
        if "input" not in item or "expected_output" not in item:
            continue
        cleaned.append(
            {
                "input": str(item["input"]).strip(),
                "expected_output": str(item["expected_output"]).strip(),
            }
        )

    if len(cleaned) != count:
        raise ValueError(
            f"Expected {count} examples, but received {len(cleaned)} valid examples. Please try again."
        )

    return cleaned
