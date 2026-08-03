"""
Populate the ReviewerDatabank from screenshots using the Lens pipeline.
Runs: OCR → Gemini → parse → save to local databank → sync to Vercel
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
import requests

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

TEST_DIR = r"C:\done"
MODEL = config.get("openrouterModel", "google/gemini-3.5-flash-lite")
API_KEY = config.get("openrouterApiKey", "")
BASE_URL = config.get("openrouterBaseUrl", "https://openrouter.ai/api/v1")
DOMAIN = config.get("domain", "SFCC")
API_BASE_URL = config.get("apiBaseUrl", "http://localhost:3000")
SECRET_KEY = config.get("secretKey", "")


def sync_to_vercel(databank: ReviewerDatabank):
    """Sync all local entries to Vercel backend."""
    entries = databank.get_all()
    if not entries:
        print("[SYNC] No entries to sync")
        return

    print(f"\n[SYNC] Syncing {len(entries)} entries to Vercel...")
    synced = 0
    for entry in entries:
        try:
            r = requests.post(
                f"{API_BASE_URL}/api/reviewer/entries",
                json={
                    "question": entry.question,
                    "choices": entry.choices,
                    "correctAnswer": entry.correct_answer,
                    "domain": entry.domain,
                },
                timeout=5,
            )
            if r.status_code == 200:
                synced += 1
        except Exception as e:
            pass  # Vercel might not be running locally
    print(f"[SYNC] Synced {synced}/{len(entries)} entries to Vercel")


def main():
    if not API_KEY:
        print("ERROR: openrouterApiKey not set in config.json")
        sys.exit(1)

    lens = get_lens_client()
    gemini = GeminiClient(api_key=API_KEY, model=MODEL, base_url=BASE_URL)
    databank = ReviewerDatabank()

    files = sorted([f for f in os.listdir(TEST_DIR) if f.endswith('.png')])
    print(f"Found {len(files)} screenshots")
    print(f"Databank has {databank.count()} existing entries\n")

    saved = 0
    skipped = 0
    failed = 0

    for i, f in enumerate(files, 1):
        path = os.path.join(TEST_DIR, f)
        print(f"\n[{i}/{len(files)}] {f}")

        # Step 1: OCR
        ocr_text = lens.ocr_from_path(path)
        if not ocr_text:
            print("  OCR FAILED")
            failed += 1
            continue

        # Step 2: Gemini text-only
        try:
            response = gemini.analyze_text(ocr_text, DOMAIN, timeout=30)
        except Exception as e:
            print(f"  GEMINI ERROR: {e}")
            failed += 1
            continue

        if not response:
            print("  NO RESPONSE")
            failed += 1
            continue

        # Step 3: Parse
        parsed = parse_qa_from_response(response)
        if not parsed:
            print("  NO PARSE (raw response)")
            failed += 1
            continue

        # Step 4: Save to databank
        existing = databank.find(parsed["question"])
        entry = databank.add(
            parsed["question"],
            parsed["choices"],
            parsed["correctAnswer"],
            DOMAIN,
        )

        if existing:
            print(f"  KNOWN — seen {entry.seen_count}x — Answer: {', '.join(parsed['correctAnswer'])}")
            skipped += 1
        else:
            print(f"  NEW — Answer: {', '.join(parsed['correctAnswer'])}")
            saved += 1

        # Rate limit protection
        time.sleep(1)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total screenshots: {len(files)}")
    print(f"New entries saved: {saved}")
    print(f"Already in databank: {skipped}")
    print(f"Failed: {failed}")
    print(f"Databank total: {databank.count()}")

    # Step 5: Sync to Vercel
    if config.get("syncToVercel", False):
        sync_to_vercel(databank)
    else:
        print("\n[SYNC] syncToVercel=false, skipping Vercel sync")

    print(f"\nLocal databank: reviewer_databank.json")


if __name__ == "__main__":
    main()
