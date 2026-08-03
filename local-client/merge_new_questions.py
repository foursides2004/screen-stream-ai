"""
Process new questionnaire screenshots, check against existing databank,
report duplicates with mismatched answers, merge new questions.
"""

import sys
import os
import time
import json
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

from lens_client import get_lens_client
from gemini_client import GeminiClient
from parse_response import parse_qa_from_response
from reviewer_databank import ReviewerDatabank, QuestionEntry

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

NEW_DIR = r"C:\video-analyzer\questionnaires"
MODEL = config.get("openrouterModel", "google/gemini-3.5-flash-lite")
API_KEY = config.get("openrouterApiKey", "")
BASE_URL = config.get("openrouterBaseUrl", "https://openrouter.ai/api/v1")
DOMAIN = config.get("domain", "SFCC")


def main():
    if not API_KEY:
        print("ERROR: openrouterApiKey not set")
        sys.exit(1)

    lens = get_lens_client()
    gemini = GeminiClient(api_key=API_KEY, model=MODEL, base_url=BASE_URL)
    databank = ReviewerDatabank()

    initial_count = databank.count()
    print(f"Existing databank: {initial_count} entries")

    files = sorted([f for f in os.listdir(NEW_DIR) if f.endswith('.png')])
    print(f"New screenshots: {len(files)}\n")

    # Track results
    new_entries = []
    duplicates_same = []
    duplicates_mismatch = []
    failed = []

    for i, f in enumerate(files, 1):
        path = os.path.join(NEW_DIR, f)
        print(f"\n[{i}/{len(files)}] {f}")

        # Step 1: OCR
        ocr_text = lens.ocr_from_path(path)
        if not ocr_text:
            print("  OCR FAILED")
            failed.append({"file": f, "reason": "OCR_FAILED"})
            continue

        # Step 2: Gemini text-only
        try:
            response = gemini.analyze_text(ocr_text, DOMAIN, timeout=30)
        except Exception as e:
            print(f"  GEMINI ERROR: {e}")
            failed.append({"file": f, "reason": f"GEMINI_ERROR: {e}"})
            continue

        if not response:
            print("  NO RESPONSE")
            failed.append({"file": f, "reason": "NO_RESPONSE"})
            continue

        # Step 3: Parse
        parsed = parse_qa_from_response(response)
        if not parsed:
            print(f"  PARSE FAILED")
            failed.append({"file": f, "reason": "PARSE_FAILED"})
            continue

        new_answer = ", ".join(parsed["correctAnswer"])
        print(f"  Answer: {new_answer}")
        print(f"  Question: {parsed['question'][:80]}...")

        # Step 4: Check for duplicates
        existing = databank.find(parsed["question"])
        if existing:
            existing_answer = ", ".join(existing.correct_answer)
            existing_normalized = set(existing_answer.replace(" ", "").split(","))
            new_normalized = set(new_answer.replace(" ", "").split(","))

            if existing_normalized == new_normalized:
                # Same answer — already have it
                print(f"  DUPLICATE (same answer: {existing_answer}) — skipping")
                duplicates_same.append({
                    "file": f,
                    "question": parsed["question"],
                    "answer": existing_answer,
                })
            else:
                # Different answer — report!
                print(f"  ⚠ MISMATCH! Existing: {existing_answer} | New: {new_answer}")
                duplicates_mismatch.append({
                    "file": f,
                    "question": parsed["question"],
                    "existing_answer": existing_answer,
                    "new_answer": new_answer,
                    "existing_seen": existing.seen_count,
                })

                # Update the databank entry with the new answer (Lens is more accurate)
                existing.correct_answer = parsed["correctAnswer"]
                existing.seen_count += 1
                existing.last_seen_at = datetime.now(timezone.utc).isoformat()
                databank.save()
                print(f"  Updated databank entry with new answer")
        else:
            # New question — save it
            entry = databank.add(
                parsed["question"],
                parsed["choices"],
                parsed["correctAnswer"],
                DOMAIN,
            )
            print(f"  NEW — saved to databank")
            new_entries.append({
                "file": f,
                "question": parsed["question"],
                "answer": new_answer,
            })

        # Rate limit protection
        time.sleep(1)

    # === SUMMARY ===
    print(f"\n\n{'='*60}")
    print("MERGE SUMMARY")
    print(f"{'='*60}")
    print(f"Total screenshots: {len(files)}")
    print(f"New entries added: {len(new_entries)}")
    print(f"Duplicates (same answer): {len(duplicates_same)}")
    print(f"Duplicates (MISMATCH): {len(duplicates_mismatch)}")
    print(f"Failed: {len(failed)}")
    print(f"Databank: {initial_count} → {databank.count()}")

    # === MISMATCH REPORT ===
    if duplicates_mismatch:
        print(f"\n\n{'='*60}")
        print("⚠ MISMATCH REPORT — Questions with different answers")
        print("="*60)
        for m in duplicates_mismatch:
            print(f"\n  File: {m['file']}")
            print(f"  Question: {m['question'][:100]}")
            print(f"  Existing answer: {m['existing_answer']} (seen {m['existing_seen']}x)")
            print(f"  New answer:      {m['new_answer']}")
            print(f"  → Databank UPDATED with new answer")

    # === FAILED REPORT ===
    if failed:
        print(f"\n\n{'='*60}")
        print("FAILED SCREENSHOTS")
        print("="*60)
        for f in failed:
            print(f"  {f['file']}: {f['reason']}")

    # === NEW ENTRIES ===
    if new_entries:
        print(f"\n\n{'='*60}")
        print("NEW ENTRIES ADDED")
        print("="*60)
        for n in new_entries:
            print(f"  {n['file']}: {n['answer']} — {n['question'][:60]}...")

    # Save report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": len(files),
        "new": len(new_entries),
        "duplicates_same": len(duplicates_same),
        "duplicates_mismatch": len(duplicates_mismatch),
        "failed": len(failed),
        "databank_before": initial_count,
        "databank_after": databank.count(),
        "mismatches": duplicates_mismatch,
        "new_entries": new_entries,
        "failed_list": failed,
    }
    with open("merge_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport saved to merge_report.json")


if __name__ == "__main__":
    main()
