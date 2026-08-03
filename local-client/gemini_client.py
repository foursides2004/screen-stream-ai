"""
Gemini API client — calls OpenRouter directly from the Python client.
Uses the same prompt and model as the Vercel /api/analyze endpoint.
"""

from __future__ import annotations

import json
from typing import Optional

import requests
from rag_search import get_knowledge_base


# System prompt — must match backend-vercel/src/app/api/analyze/route.ts
SYSTEM_PROMPT = """You are an AI assistant that reads screen captures and solves problems visible on screen.

PRIMARY TASK: Look at the screen capture carefully. If there are questions, quizzes, tests, or assessments visible, READ each question and PROVIDE THE CORRECT ANSWER(S) directly.

IMPORTANT RULES:
- If there is a question on screen, answer it correctly with the right answer
- If there are MULTIPLE questions, answer ALL of them, each clearly labeled
- If there are multiple-choice options, identify the correct option(s)
- CRITICAL: Look for "Choose the best option(s)" or checkboxes - this means MULTIPLE answers may be correct
- For multi-select questions, you MUST list ALL correct options, not just one
- Provide the actual answer content, not a description of the test
- NO explanations about what you see, NO descriptions like "taking a test"
- NO markdown, NO introductions, NO conclusions
- Just the answer(s), nothing else{domain_context}

AFTER your answer, you MUST also output a JSON code block with this exact structure:
```json
{
  "question": "the full question text from the screen",
  "choices": [
    {"label": "A", "content": "choice text"},
    {"label": "B", "content": "choice text"}
  ],
  "correctAnswer": ["A"]
}
```

For questions without choices (fill-in-the-blank), use an empty choices array and put the answer text in correctAnswer.
For multi-select questions, list all correct labels in the correctAnswer array.

EXAMPLES OF GOOD RESPONSES:
- "C" (for a single multiple choice)
- "Paris" (for "What is the capital of France?")
- "A, B, D" (for multi-select with options A, B, D correct)
- "CurrentSession, CurrentRequest, CurrentCustomer, CurrentHttpParameterMap" (for multi-select)

EXAMPLES OF BAD RESPONSES:
- "Taking an online test"
- "The user is answering a quiz"
- "I see a multiple choice question"
- Listing only 1 of 4 correct answers for a multi-select question"""

USER_PROMPT = "Read the questions on this screen and provide the correct answer(s) for each one. If there are multiple questions, answer all of them."


class GeminiClient:
    """Calls Gemini via OpenRouter API directly from the Python client."""

    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def analyze(self, image_data_url: str, domain: str = "", timeout: int = 30) -> Optional[str]:
        """Call Gemini via OpenRouter and return the response text.

        Args:
            image_data_url: Base64 data URL (e.g., "data:image/webp;base64,...")
            domain: Optional domain context (e.g., "SFCC", "AWS")
            timeout: Request timeout in seconds

        Returns:
            Response text, or None on failure.
        """
        domain_context = ""
        if domain:
            domain_context = (
                f"\n\nDOMAIN CONTEXT: This is an official {domain} exam/assessment. "
                f"Treat all questions as formal {domain} exam questions and provide "
                f"accurate answers based on {domain} documentation, official guidelines, "
                f"and established best practices."
            )

            # RAG: retrieve relevant knowledge base chunks
            try:
                kb = get_knowledge_base(domain)
                # Use the system prompt keywords to search for relevant context
                search_query = f"{domain} {' '.join(self.model.split('.'))} exam"
                chunks = kb.search(search_query, top_n=3)
                if chunks:
                    rag_text = "\n---\n".join(chunks)
                    domain_context += f"\n\nREFERENCE MATERIAL (use this to answer accurately):\n{rag_text}"
            except Exception as e:
                print(f"[RAG] Failed to retrieve context: {e}")

        system_content = SYSTEM_PROMPT.replace("{domain_context}", domain_context)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_content},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": USER_PROMPT},
                        {"type": "image_url", "image_url": {"url": image_data_url}},
                    ],
                },
            ],
            "max_tokens": 2048,
            "temperature": 0.3,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Screen Stream AI Assistant",
        }

        try:
            url = f"{self.base_url}/chat/completions"
            print(f"[GEMINI] Calling {self.model} via {url}")
            response = self.session.post(url, json=payload, headers=headers, timeout=timeout)

            if response.status_code != 200:
                print(f"[GEMINI] API error {response.status_code}: {response.text[:500]}")
                return None

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            print(f"[GEMINI] Got response ({len(content)} chars)")
            return content

        except requests.exceptions.Timeout:
            print("[GEMINI] Request timeout")
            return None
        except requests.exceptions.ConnectionError:
            print("[GEMINI] Connection error")
            return None
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"[GEMINI] Failed to parse response: {e}")
            return None
        except Exception as e:
            print(f"[GEMINI] Unexpected error: {e}")
            return None
