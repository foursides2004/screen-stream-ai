"""
RAG (Retrieval-Augmented Generation) search module.
Searches a local knowledge base of markdown files and returns relevant chunks.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


# Common English stopwords to exclude from search
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "dare",
    "ought", "used", "if", "then", "else", "when", "where", "how", "what",
    "which", "who", "whom", "this", "that", "these", "those", "i", "me",
    "my", "we", "our", "you", "your", "he", "him", "his", "she", "her",
    "it", "its", "they", "them", "their", "not", "no", "nor", "so", "too",
    "very", "just", "about", "above", "after", "again", "all", "also",
    "any", "because", "before", "below", "between", "both", "each",
    "few", "more", "most", "other", "some", "such", "than", "up",
    "here", "there", "why", "way", "out", "only", "own", "same",
    "now", "new", "one", "two", "three", "following", "select",
    "choose", "best", "option", "options", "valid", "statement",
    "statements", "question", "code", "use", "using", "which",
}


def _extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from text, excluding stopwords."""
    # Lowercase and split on non-alphanumeric
    words = re.findall(r'[a-zA-Z0-9_]+', text.lower())
    # Filter stopwords and very short words
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 1]
    return keywords


def _score_chunk(chunk_text: str, question_keywords: list[str]) -> float:
    """Score a chunk based on keyword overlap with the question."""
    chunk_lower = chunk_text.lower()
    chunk_words = set(re.findall(r'[a-zA-Z0-9_]+', chunk_lower))

    if not question_keywords:
        return 0.0

    # Count matching keywords
    matches = sum(1 for kw in question_keywords if kw in chunk_words)

    # Bonus for exact phrase matches (multi-word terms)
    question_text = " ".join(question_keywords)
    if question_text in chunk_lower:
        matches += 2

    # Normalize by number of question keywords
    return matches / len(question_keywords)


def _chunk_markdown(text: str, source: str) -> list[dict]:
    """Split markdown text into chunks by headers."""
    chunks = []
    # Split on ## or ### headers
    sections = re.split(r'\n(?=##\s)', text)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Get the header as title
        header_match = re.match(r'^##\s+(.+)', section)
        title = header_match.group(1) if header_match else source

        chunks.append({
            "text": section,
            "source": source,
            "title": title,
        })

    return chunks


class KnowledgeBase:
    """Searchable knowledge base loaded from markdown files."""

    def __init__(self, domain: str, knowledge_dir: str = "knowledge"):
        """Load markdown files for the given domain.

        Args:
            domain: Domain name (e.g., "SFCC", "AWS")
            knowledge_dir: Base directory for knowledge files
        """
        self.domain = domain
        self.chunks = self._load_chunks(domain, knowledge_dir)
        print(f"[RAG] Loaded {len(self.chunks)} chunks for domain '{domain}'")

    def _load_chunks(self, domain: str, knowledge_dir: str) -> list[dict]:
        """Load and chunk all markdown files for the domain."""
        domain_dir = Path(knowledge_dir) / domain.lower()

        if not domain_dir.exists():
            print(f"[RAG] No knowledge directory found: {domain_dir}")
            return []

        all_chunks = []
        for md_file in sorted(domain_dir.glob("*.md")):
            try:
                text = md_file.read_text(encoding="utf-8")
                chunks = _chunk_markdown(text, md_file.stem)
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"[RAG] Failed to load {md_file}: {e}")

        return all_chunks

    def search(self, question: str, top_n: int = 3) -> list[str]:
        """Find most relevant chunks for the question.

        Args:
            question: The question text to search for
            top_n: Number of top chunks to return

        Returns:
            List of relevant chunk text strings
        """
        if not self.chunks:
            return []

        question_keywords = _extract_keywords(question)
        if not question_keywords:
            return []

        # Score all chunks
        scored = []
        for chunk in self.chunks:
            score = _score_chunk(chunk["text"], question_keywords)
            if score > 0:
                scored.append((score, chunk))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Return top N chunks
        results = []
        for score, chunk in scored[:top_n]:
            results.append(chunk["text"])

        return results


# Singleton cache to avoid reloading knowledge base on every call
_kb_cache: dict[str, KnowledgeBase] = {}


def get_knowledge_base(domain: str) -> KnowledgeBase:
    """Get or create a cached KnowledgeBase for the domain."""
    domain_key = domain.upper().strip()
    if domain_key not in _kb_cache:
        _kb_cache[domain_key] = KnowledgeBase(domain_key)
    return _kb_cache[domain_key]
