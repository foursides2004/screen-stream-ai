"""Retry the 41 failed screenshots from the merge."""

import sys
import os
import time
import json
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

from lens_client import get_lens_client
from gemini_client import GeminiClient
from parse_response import parse_qa_from_response
from reviewer_databank import ReviewerDatabank

with open("config.json", "r") as f:
    config = json.load(f)

NEW_DIR = r"C:\video-analyzer\questionnaires"
MODEL = config.get("openrouterModel", "google/gemini-3.5-flash-lite")
API_KEY = config.get("openrouterApiKey", "")
BASE_URL = config.get("openrouterBaseUrl", "https://openrouter.ai/api/v1")
DOMAIN = config.get("domain", "SFCC")

# Only the failed ones (10-50)
FAILED_FILES = [f"question_{i:02d}.png" for i in range(10, 51)]


def main():
    if not API_KEY:
        print("ERROR: openrouterApiKey not set")
        sys.exit(1)

    lens = get_lens_client()
    gemini = GeminiClient(api_key=API_KEY, model=MODEL, base_url=BASE_URL)
    databank = ReviewerDatabank()

    initial_count = databank.count()
    print(f"Existing databank: {initial_count} entries")
    print(f"Retrying {len(FAILED_FILES)} failed screenshots\n")

    new_entries = []
    duplicates_same = []
    duplicates_mismatch = []
    failed = []

    for i, f in enumerate(FAILED_FILES, 1):
        path = os.path.join(NEW_DIR, f)
        print(f"\n[{i}/{len(FAILED_FILES)}] {f}")

        ocr_text = lens.ocr_from_path(path)
        if not ocr_text:
            print("  OCR FAILED")
            failed.append(f)
            continue

        try:
            response = gemini.analyze_text(ocr_text, DOMAIN, timeout=30)
        except Exception as e:
            print(f"  GEMINI ERROR: {e}")
            failed.append(f)
            continue

        if not response:
            print("  NO RESPONSE")
            failed.append(f)
            continue

        parsed = parse_qa_from_response(response)
        if not parsed:
            print("  PARSE FAILED")
            failed.append(f)
            continue

        new_answer = ", ".join(parsed["correctAnswer"])
        print(f"  Answer: {new_answer}")
        print(f"  Question: {parsed['question'][:80]}...")

        existing = databank.find(parsed["question"])
        if existing:
            existing_answer = ", ".join(existing.correct_answer)
            existing_normalized = set(existing_answer.replace(" ", "").split(","))
            new_normalized = set(new_answer.replace(" ", "").split(","))

            if existing_normalized == new_normalized:
                print(f"  DUPLICATE (same) — skipping")
                duplicates_same.append(f)
            else:
                print(f"  ⚠ MISMATCH! Existing: {existing_answer} | New: {new_answer}")
                duplicates_mismatch.append({
                    "file": f,
                    "question": parsed["question"],
                    "existing_answer": existing_answer,
                    "new_answer": new_answer,
                })
                existing.correct_answer = parsed["correctAnswer"]
                existing.seen_count += 1
                existing.last_seen_at = datetime.now(timezone.utc).isoformat()
                databank.save()
        else:
            entry = databank.add(
                parsed["question"],
                parsed["choices"],
                parsed["correctAnswer"],
                DOMAIN,
            )
            print(f"  NEW — saved")
            new_entries.append({"file": f, "question": parsed["question"], "answer": new_answer})

        time.sleep(1)

    # Summary
    print(f"\n{'='*60}")
    print("RETRY SUMMARY")
    print(f"{'='*60}")
    print(f"Retried: {len(FAILED_FILES)}")
    print(f"New entries: {len(new_entries)}")
    print(f"Duplicates (same): {len(duplicates_same)}")
    print(f"Mismatches: {len(duplicates_mismatch)}")
    print(f"Still failed: {len(failed)}")
    print(f"Databank: {initial_count} → {databank.count()}")

    if duplicates_mismatch:
        print(f"\n{'='*60}")
        print("⚠ MISMATCH REPORT")
        print("="*60)
        for m in duplicates_mismatch:
            print(f"\n  {m['file']}")
            print(f"  Q: {m['question'][:100]}")
            print(f"  Existing: {m['existing_answer']}")
            print(f"  New:      {m['new_answer']}")

    if failed:
        print(f"\nStill failed: {failed}")


if __name__ == "__main__":
    main()
