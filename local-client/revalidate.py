"""
Revalidate: retry 3 failed screenshots + re-check 9 that already existed.
"""

import sys
import os
import time
import json

sys.stdout.reconfigure(encoding='utf-8')

from lens_client import get_lens_client
from gemini_client import GeminiClient
from parse_response import parse_qa_from_response
from reviewer_databank import ReviewerDatabank

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

TEST_DIR = r"C:\done"
MODEL = config.get("openrouterModel", "google/gemini-3.5-flash-lite")
API_KEY = config.get("openrouterApiKey", "")
BASE_URL = config.get("openrouterBaseUrl", "https://openrouter.ai/api/v1")
DOMAIN = config.get("domain", "SFCC")

# Screenshots that FAILED (no parse or OCR error)
FAILED = [
    "Screenshot 2026-06-26 082727.png",  # NO PARSE
    "Screenshot 2026-06-26 082922.png",  # NO PARSE
    "Screenshot 2026-06-26 083239.png",  # OCR 502 error
]

# Screenshots that already existed (need revalidation)
EXISTING = [
    ("Screenshot 2026-06-26 082503.png", "A"),
    ("Screenshot 2026-06-26 082530.png", "C"),
    ("Screenshot 2026-06-26 082659.png", "A, B"),
    ("Screenshot 2026-06-26 082744.png", "B"),
    ("Screenshot 2026-06-26 082846.png", "B"),
    ("Screenshot 2026-06-26 083042.png", "C"),
    ("Screenshot 2026-06-26 083056.png", "B"),
    ("Screenshot 2026-06-26 083104.png", "A, B, D"),
    ("Screenshot 2026-06-26 083112.png", "A"),
]


def main():
    if not API_KEY:
        print("ERROR: openrouterApiKey not set")
        sys.exit(1)

    lens = get_lens_client()
    gemini = GeminiClient(api_key=API_KEY, model=MODEL, base_url=BASE_URL)
    databank = ReviewerDatabank()

    # === RETRY FAILED ===
    print("=" * 60)
    print("RETRYING 3 FAILED SCREENSHOTS")
    print("=" * 60)

    for f in FAILED:
        path = os.path.join(TEST_DIR, f)
        print(f"\n--- {f} ---")

        ocr_text = lens.ocr_from_path(path)
        if not ocr_text:
            print("  STILL FAILED: OCR returned nothing")
            continue

        print(f"  OCR: {ocr_text[:150]}...")

        response = gemini.analyze_text(ocr_text, DOMAIN, timeout=30)
        if not response:
            print("  STILL FAILED: No Gemini response")
            continue

        parsed = parse_qa_from_response(response)
        if not parsed:
            print(f"  STILL FAILED: Could not parse response")
            print(f"  Raw: {response[:200]}")
            continue

        answer = ", ".join(parsed["correctAnswer"])
        print(f"  SUCCESS — Answer: {answer}")
        print(f"  Question: {parsed['question'][:100]}")

        # Save to databank
        entry = databank.add(
            parsed["question"],
            parsed["choices"],
            parsed["correctAnswer"],
            DOMAIN,
        )
        print(f"  Saved to databank (seen {entry.seen_count}x)")

        time.sleep(1)

    # === REVALIDATE EXISTING ===
    print(f"\n{'=' * 60}")
    print("REVALIDATING 9 EXISTING ENTRIES")
    print("=" * 60)

    matches = 0
    mismatches = 0

    for f, expected_answer in EXISTING:
        path = os.path.join(TEST_DIR, f)
        print(f"\n--- {f} (expected: {expected_answer}) ---")

        ocr_text = lens.ocr_from_path(path)
        if not ocr_text:
            print("  OCR FAILED")
            continue

        response = gemini.analyze_text(ocr_text, DOMAIN, timeout=30)
        if not response:
            print("  No Gemini response")
            continue

        parsed = parse_qa_from_response(response)
        if not parsed:
            print(f"  Could not parse")
            continue

        new_answer = ", ".join(parsed["correctAnswer"])
        print(f"  Got: {new_answer}")

        # Compare
        old_normalized = set(expected_answer.replace(" ", "").split(","))
        new_normalized = set(new_answer.replace(" ", "").split(","))

        if old_normalized == new_normalized:
            print(f"  ✓ MATCH")
            matches += 1
        else:
            print(f"  ✗ MISMATCH (expected {expected_answer}, got {new_answer})")
            mismatches += 1

            # Update databank with new answer
            existing_entry = databank.find(parsed["question"])
            if existing_entry:
                existing_entry.correct_answer = parsed["correctAnswer"]
                existing_entry.seen_count += 1
                databank.save()
                print(f"  Updated databank with new answer")

        time.sleep(1)

    # Summary
    print(f"\n{'=' * 60}")
    print("REVALIDATION SUMMARY")
    print("=" * 60)
    print(f"Failed screenshots retried: 3")
    print(f"Existing entries rechecked: 9")
    print(f"  Matches: {matches}")
    print(f"  Mismatches: {mismatches}")
    print(f"Databank total: {databank.count()}")


if __name__ == "__main__":
    main()
