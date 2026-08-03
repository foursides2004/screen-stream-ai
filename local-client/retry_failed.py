"""Retry the 2 remaining failed screenshots with fixed parser."""

import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8')

from lens_client import get_lens_client
from gemini_client import GeminiClient
from parse_response import parse_qa_from_response
from reviewer_databank import ReviewerDatabank

with open("config.json", "r") as f:
    config = json.load(f)

lens = get_lens_client()
gemini = GeminiClient(
    api_key=config["openrouterApiKey"],
    model=config.get("openrouterModel", "google/gemini-3.5-flash-lite"),
    base_url=config.get("openrouterBaseUrl", "https://openrouter.ai/api/v1"),
)
databank = ReviewerDatabank()

for fname in ["Screenshot 2026-06-26 082727.png", "Screenshot 2026-06-26 082922.png"]:
    path = rf"C:\done\{fname}"
    print(f"\n--- {fname} ---")

    ocr = lens.ocr_from_path(path)
    if not ocr:
        print("OCR FAILED")
        continue

    resp = gemini.analyze_text(ocr, "SFCC", timeout=30)
    if not resp:
        print("NO RESPONSE")
        continue

    parsed = parse_qa_from_response(resp)
    if not parsed:
        print(f"PARSE FAILED. Raw: {resp[:300]}")
        continue

    answer = ", ".join(parsed["correctAnswer"])
    print(f"Answer: {answer}")
    print(f"Question: {parsed['question'][:100]}")

    entry = databank.add(
        parsed["question"],
        parsed["choices"],
        parsed["correctAnswer"],
        "SFCC",
    )
    print(f"Saved (seen {entry.seen_count}x)")
    time.sleep(1)

print(f"\nDatabank total: {databank.count()}")
