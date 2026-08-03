"""
Google Lens OCR client — extracts text from screenshots using Chrome Lens API.
Free, no API key required. Uses chrome-lens-py library.

Architecture:
  Screenshot → Lens OCR (free) → Extracted text → Gemini text-only (cheap) → Answer

This avoids sending images to Gemini (saves tokens) while leveraging
Google's OCR accuracy which uses their full search index.
"""

from __future__ import annotations

import asyncio
import re
import tempfile
import os
from typing import Optional


# Watermark/noise patterns to filter out from OCR output
NOISE_PATTERNS = [
    # Name/watermark patterns (accenture proctoring watermark)
    r"gideon\.r\.?\s*linsangan\s*@?\s*accenture",
    r"gideon\s*[.:]?\s*[rRt]?\s*\.?\s*linsangan",
    r"gideon\s*\w*",
    r"linsangan\s*@?\s*accenture",
    r"@[a-zA-Z]+",
    r"centure",
    r"accenture",
    r"videon\w*",
    r"gan\s*@",
    r"nr\s+limsangan",
    r"nsangan\s*@",
    r"leon\w*\s*@",
    r"leon\.r",
    r"on\s+luangan",
    r"on\s+lu",
    r"an@",
    r"ideon",
    r"gidgon",
    r"gidee",
    r"nure",
    r"enture",
    r"ridan\s+rim",
    r"ridean\s+rim",
    r"rideon",
    r"gideo",
    r"gidyon",
    r"gia\s",
    r"em\s+",
    # Exam platform UI elements
    r"Mettl Online Assessment.*",
    r"Recorded Session",
    r"Powered By Mercer.*",
    r"Mercer\s+metti",
    r"Gideon\s+R",
    r"Need Help\?.*",
    r"\+91\s+\d+-\d+",
    r"Test Time:\s*\d+:\d+:\d+",
    r"Attempted:\s*\d+/\d+",
    r"Finish Test",
    r"Revisit Later",
    r"Clear Response",
    r"Select an option",
    r"Choose the best option\(s\)",
    # VLC/media player
    r"ScreenCapture.*",
    r"VLC media player",
    r"Media Playback.*",
    r"View Help",
    r"Saved:\s*\d+\s*seconds?\s*ago",
    # Short UI noise
    r"^Next$",
    r"^X$",
    r"^A$",
    r"^O$",
    r"^eng$",
    r"^eideo\.?$",
    r"^gia\s",
    # Time/date/system
    r"^\d{1,2}:\d{2}\s*(AM|PM)?\s*$",
    r"^\d{1,2}:\d{2}\s+(AM|PM)\s+\d{1,2}/\d{1,2}/\d{4}",
    r"^\d{1,2}/\d{1,2}/\d{4}$",
    r"ENG\s+US",
    r"^US$",
    r"^\d+%$",  # percentages
    r"^\d+\s*$",  # lone numbers
    # Navigation
    r"^>\s*\d+",
    r"^\d+\s+\d+\s+\d+",
    r"^\d+\s+Section\s+\d+",
    # Browser UI
    r"^https?://\S+$",
    r"^backend-vercel.*",
    r"^Deployment.*",
    r"^Screen Stream.*",
    r"^iCloud.*",
    r"^Manga:.*",
    r"^Free\s+On.*",
    r"^Chat$",
    r"^Edit$",
    r"^Π$",
    r"^\+$",
    r"^backend.*",
    r"^vercel.*",
]


def _clean_ocr_text(raw_text: str) -> str:
    """Remove watermark noise and clean up OCR text."""
    lines = raw_text.split('\n')
    cleaned = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Skip lines that are pure noise
        is_noise = False
        for pattern in NOISE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                is_noise = True
                break

        if not is_noise:
            cleaned.append(line)

    # Remove duplicate consecutive lines
    deduped = []
    for line in cleaned:
        if not deduped or line.lower() != deduped[-1].lower():
            deduped.append(line)

    return '\n'.join(deduped)


class LensClient:
    """Google Lens OCR client for extracting text from screenshots."""

    def __init__(self):
        self._lens = None

    def _get_lens(self):
        """Lazy-load the LensAPI."""
        if self._lens is None:
            from chrome_lens_py import LensAPI
            self._lens = LensAPI()
        return self._lens

    def ocr_from_path(self, image_path: str) -> Optional[str]:
        """Extract and clean text from an image file using Google Lens OCR.

        Args:
            image_path: Path to the image file

        Returns:
            Cleaned OCR text, or None on failure.
        """
        try:
            print(f"[LENS] Scanning image: {image_path}")

            # Run async LensAPI in sync context
            loop = asyncio.new_event_loop()
            try:
                api = self._get_lens()
                result = loop.run_until_complete(
                    api.process_image(
                        image_path=image_path,
                        output_format='full_text'
                    )
                )
            finally:
                loop.close()

            raw_text = result.get('ocr_text', '')
            if not raw_text:
                print("[LENS] No text extracted")
                return None

            # Clean the text
            cleaned = _clean_ocr_text(raw_text)
            print(f"[LENS] Extracted {len(cleaned)} chars (from {len(raw_text)} raw)")

            return cleaned

        except Exception as e:
            print(f"[LENS] Error: {e}")
            return None

    def ocr_from_bytes(self, image_bytes: bytes) -> Optional[str]:
        """Extract text from image bytes using Google Lens OCR.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Cleaned OCR text, or None on failure.
        """
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                f.write(image_bytes)
                tmp_path = f.name

            return self.ocr_from_path(tmp_path)

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)


def get_lens_client() -> LensClient:
    """Get or create a cached LensClient instance."""
    if not hasattr(get_lens_client, '_instance'):
        get_lens_client._instance = LensClient()
    return get_lens_client._instance
