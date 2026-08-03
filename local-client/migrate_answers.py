"""
Migrate existing databank entries: resolve answer labels (A, B, C) to actual content.
e.g., ["A"] → ["Paris"] if choice A is "Paris"
"""

import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

from reviewer_databank import ReviewerDatabank


def main():
    databank = ReviewerDatabank()
    updated = 0

    for entry in databank.entries:
        # Build label → content map
        label_to_content = {}
        for choice in entry.choices:
            if isinstance(choice, dict) and "label" in choice and "content" in choice:
                label_to_content[choice["label"].strip().upper()] = choice["content"].strip()

        if not label_to_content:
            continue

        # Check if answers are labels that need resolving
        new_answers = []
        changed = False
        for answer in entry.correct_answer:
            answer_upper = answer.strip().upper()
            if answer_upper in label_to_content and answer.strip() != label_to_content[answer_upper]:
                # Resolve label to content
                new_answers.append(label_to_content[answer_upper])
                changed = True
            else:
                new_answers.append(answer)

        if changed:
            old = ", ".join(entry.correct_answer)
            new = ", ".join(new_answers)
            print(f"  {entry.question[:60]}...")
            print(f"    {old} → {new}")
            entry.correct_answer = new_answers
            updated += 1

    if updated:
        databank.save()
        print(f"\nUpdated {updated}/{len(databank.entries)} entries")
    else:
        print("No entries needed updating")


if __name__ == "__main__":
    main()
