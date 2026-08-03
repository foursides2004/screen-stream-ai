"""
Mock responder — returns canned Gemini responses for development/testing.
Responses are in the format expected by parse_qa_from_response.
"""

from __future__ import annotations

import time
from itertools import cycle


# Mock responses that match the format parse_qa_from_response expects:
# - Plain text answer at the top
# - A ```json block with question, choices, correctAnswer
# IMPORTANT: correctAnswer uses actual answer content, NOT labels (A, B, C)
# because answer order may be randomized between sessions
MOCK_RESPONSES = [
    """CurrentSession, CurrentRequest, CurrentCustomer

```json
{
  "question": "Which of the following are valid SFCC session attributes?",
  "choices": [
    {"label": "A", "content": "CurrentSession"},
    {"label": "B", "content": "CurrentRequest"},
    {"label": "C", "content": "InvalidAttribute"},
    {"label": "D", "content": "CurrentCustomer"}
  ],
  "correctAnswer": ["CurrentSession", "CurrentRequest", "CurrentCustomer"]
}
```""",

    """Paris

```json
{
  "question": "What is the capital of France?",
  "choices": [
    {"label": "A", "content": "London"},
    {"label": "B", "content": "Paris"},
    {"label": "C", "content": "Berlin"},
    {"label": "D", "content": "Madrid"}
  ],
  "correctAnswer": ["Paris"]
}
```""",

    """GET, PUT

```json
{
  "question": "Which HTTP methods are idempotent?",
  "choices": [
    {"label": "A", "content": "GET"},
    {"label": "B", "content": "POST"},
    {"label": "C", "content": "PUT"},
    {"label": "D", "content": "PATCH"}
  ],
  "correctAnswer": ["GET", "PUT"]
}
```""",

    """301 Moved Permanently, 302 Found, 307 Temporary Redirect

```json
{
  "question": "Which of the following are valid HTTP status codes for redirects?",
  "choices": [
    {"label": "A", "content": "200 OK"},
    {"label": "B", "content": "301 Moved Permanently"},
    {"label": "C", "content": "404 Not Found"},
    {"label": "D", "content": "302 Found"},
    {"label": "E", "content": "307 Temporary Redirect"}
  ],
  "correctAnswer": ["301 Moved Permanently", "302 Found", "307 Temporary Redirect"]
}
```""",

    """Cascading Style Sheets

```json
{
  "question": "What does CSS stand for?",
  "choices": [
    {"label": "A", "content": "Computer Style Sheets"},
    {"label": "B", "content": "Creative Style System"},
    {"label": "C", "content": "Cascading Style Sheets"},
    {"label": "D", "content": "Colorful Style Syntax"}
  ],
  "correctAnswer": ["Cascading Style Sheets"]
}
```""",
]


class MockResponder:
    """Returns canned Gemini responses for development/testing."""

    def __init__(self, delay: float = 0.5):
        """Initialize the mock responder.

        Args:
            delay: Simulated API latency in seconds.
        """
        self.delay = delay
        self._cycle = cycle(MOCK_RESPONSES)

    def generate(self) -> str:
        """Return a mock Gemini response.

        Returns:
            A canned response in the format parse_qa_from_response expects.
        """
        time.sleep(self.delay)
        response = next(self._cycle)
        print(f"[MOCK] Generated mock response ({len(response)} chars)")
        return response
