"""
Local JSON databank for storing question/answer data from screen captures.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class QuestionEntry:
    """A single question/answer entry in the databank."""

    def __init__(
        self,
        id: str,
        question: str,
        choices: list[dict[str, str]],
        correct_answer: list[str],
        domain: str = "",
        seen_count: int = 1,
        last_seen_at: str = "",
        created_at: str = "",
    ):
        self.id = id
        self.question = question
        self.choices = choices
        self.correct_answer = correct_answer
        self.domain = domain
        self.seen_count = seen_count
        self.last_seen_at = last_seen_at or datetime.now(timezone.utc).isoformat()
        self.created_at = created_at or self.last_seen_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "choices": self.choices,
            "correctAnswer": self.correct_answer,
            "domain": self.domain,
            "seenCount": self.seen_count,
            "lastSeenAt": self.last_seen_at,
            "createdAt": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuestionEntry:
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            question=data["question"],
            choices=data.get("choices", []),
            correct_answer=data.get("correctAnswer", []),
            domain=data.get("domain", ""),
            seen_count=data.get("seenCount", 1),
            last_seen_at=data.get("lastSeenAt", ""),
            created_at=data.get("createdAt", ""),
        )


class ReviewerDatabank:
    """Local JSON file storage for Q&A entries."""

    def __init__(self, file_path: str = "reviewer_databank.json"):
        self.file_path = Path(file_path)
        self.entries: list[QuestionEntry] = []
        self.load()

    def load(self) -> None:
        """Load databank from disk. Creates empty databank if file doesn't exist."""
        if not self.file_path.exists():
            self.entries = []
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.entries = [QuestionEntry.from_dict(e) for e in data.get("entries", [])]
            print(f"[REVIEWER] Loaded {len(self.entries)} entries from {self.file_path}")
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"[WARN] Failed to load databank: {e} — starting empty")
            self.entries = []

    def save(self) -> None:
        """Persist current state to disk."""
        data = {
            "version": 1,
            "entries": [e.to_dict() for e in self.entries],
        }
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"[ERROR] Failed to save databank: {e}")

    @staticmethod
    def normalize_question(text: str) -> str:
        """Normalize question text for matching."""
        import re
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

    def find(self, question_text: str) -> Optional[QuestionEntry]:
        """Find an entry by normalized question text."""
        normalized = self.normalize_question(question_text)
        for entry in self.entries:
            if self.normalize_question(entry.question) == normalized:
                return entry
        return None

    def add(
        self,
        question: str,
        choices: list[dict[str, str]],
        correct_answer: list[str],
        domain: str = "",
    ) -> QuestionEntry:
        """Add a new entry or update if question already exists. Returns the entry."""
        existing = self.find(question)
        now = datetime.now(timezone.utc).isoformat()

        if existing:
            existing.seen_count += 1
            existing.last_seen_at = now
            if domain and not existing.domain:
                existing.domain = domain
            self.save()
            return existing

        entry = QuestionEntry(
            id=str(uuid.uuid4()),
            question=question,
            choices=choices,
            correct_answer=correct_answer,
            domain=domain,
            seen_count=1,
            last_seen_at=now,
            created_at=now,
        )
        self.entries.append(entry)
        self.save()
        return entry

    def get_all(self) -> list[QuestionEntry]:
        """Return all entries sorted by last seen (most recent first)."""
        return sorted(
            self.entries,
            key=lambda e: e.last_seen_at,
            reverse=True,
        )

    def count(self) -> int:
        """Return the number of entries."""
        return len(self.entries)
