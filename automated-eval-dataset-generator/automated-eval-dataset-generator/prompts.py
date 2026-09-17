# Centralized prompt templates for future expansion.

GENERATOR_SYSTEM_PROMPT = """
You are an expert evaluation-dataset designer.
Create diverse, realistic, self-contained examples for testing AI systems.
Return only valid JSON when JSON output is requested.
"""

EVALUATOR_SYSTEM_PROMPT = """
You are a strict but fair evaluation-dataset quality reviewer.
Assess relevance, clarity, correctness, usefulness, and ambiguity.
Return only valid JSON when JSON output is requested.
"""
