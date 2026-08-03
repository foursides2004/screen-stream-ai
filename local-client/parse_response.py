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
    # choices can be empty list for fill-in-the-blank
    if not isinstance(data.get("choices"), list):
        return False
    # correctAnswer can be a string (single answer) or list
    answer = data.get("correctAnswer")
    if isinstance(answer, str):
        if not answer.strip():
            return False
    elif isinstance(answer, list):
        if len(answer) == 0:
            return False
    else:
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

    # Normalize correctAnswer to always be a list
    answer = data["correctAnswer"]
    if isinstance(answer, str):
        answer = [answer]

    # Resolve labels to actual answer content
    # e.g., ["A", "B"] → ["Paris", "London"] (if choices are A. Paris, B. London)
    choices = data.get("choices", [])
    label_to_content = {c["label"].strip().upper(): c["content"].strip() for c in choices if isinstance(c, dict)}

    resolved = []
    for a in answer:
        a_upper = a.strip().upper()
        if a_upper in label_to_content:
            resolved.append(label_to_content[a_upper])
        else:
            # Not a label — keep as-is (fill-in-the-blank, True/False, etc.)
            resolved.append(a.strip())

    return {
        "question": data["question"].strip(),
        "choices": data["choices"],
        "correctAnswer": resolved,
    }
