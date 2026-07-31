"""
Parse structured Q&A data from Gemini's response text.
"""

from __future__ import annotations

import json
import re
from typing import Optional


def extract_json_block(text: str) -> Optional[dict]:
    """Extract the last ```json ... ``` code block from text."""
    pattern = r'```json\s*\n(.*?)\n\s*```'
    matches = list(re.finditer(pattern, text, re.DOTALL))
    if not matches:
        return None

    try:
        return json.loads(matches[-1].group(1))
    except (json.JSONDecodeError, ValueError):
        return None


def validate_qa_entry(data: dict) -> bool:
    """Validate that a dict has the required Q&A fields."""
    if not isinstance(data.get("question"), str) or not data["question"].strip():
        return False
    if not isinstance(data.get("choices"), list) or len(data["choices"]) == 0:
        return False
    if not isinstance(data.get("correctAnswer"), list) or len(data["correctAnswer"]) == 0:
        return False

    # Validate choices have label and content
    for choice in data["choices"]:
        if not isinstance(choice, dict):
            return False
        if not isinstance(choice.get("label"), str) or not isinstance(choice.get("content"), str):
            return False

    return True


def parse_qa_from_response(text: str) -> Optional[dict]:
    """Extract and validate Q&A data from a Gemini response.

    Returns a dict with keys: question, choices, correctAnswer.
    Returns None if extraction or validation fails.
    """
    data = extract_json_block(text)
    if data is None:
        return None
    if not validate_qa_entry(data):
        return None
    return {
        "question": data["question"].strip(),
        "choices": data["choices"],
        "correctAnswer": data["correctAnswer"],
    }
