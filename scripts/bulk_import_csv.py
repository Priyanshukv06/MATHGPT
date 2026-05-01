"""
scripts/bulk_import_csv.py
──────────────────────────
Import questions from a CSV file into the MathGPT question bank.

CSV FORMAT:
  topic, difficulty, question, solution, source (optional), tags (optional)

VALID TOPICS:
  🔢 Algebra | 📈 Calculus | 📐 Trigonometry
  🎲 Probability | 📊 Linear Algebra | 🔷 Geometry

VALID DIFFICULTIES:
  Easy | Medium | Hard

RUN:
  python scripts/bulk_import_csv.py --file data/questions_template.csv
  python scripts/bulk_import_csv.py --file data/my_questions.csv --dry-run
"""

import sys
import csv
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

VALID_TOPICS = [
    "🔢 Algebra", "📈 Calculus", "📐 Trigonometry",
    "🎲 Probability", "📊 Linear Algebra", "🔷 Geometry",
]
VALID_DIFFS = ["Easy", "Medium", "Hard"]


def import_csv(filepath: str, dry_run: bool = False) -> None:
    from utils.question_bank import add_question

    path = Path(filepath)
    if not path.exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    total = imported = skipped = 0
    errors = []

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows   = list(reader)

    print(f"\n📄 File: {filepath}  ({len(rows)} rows)")
    if dry_run:
        print("   [DRY RUN — nothing will be saved]")

    for i, row in enumerate(rows, start=2):
        total += 1
        topic      = row.get("topic",      "").strip()
        difficulty = row.get("difficulty", "").strip()
        question   = row.get("question",   "").strip()
        solution   = row.get("solution",   "").strip()
        source     = row.get("source",     "").strip()
        tags       = row.get("tags",       "").strip()

        row_errors = []
        if not topic:
            row_errors.append("topic missing")
        elif topic not in VALID_TOPICS:
            row_errors.append(f"invalid topic '{topic}'")
        if difficulty not in VALID_DIFFS:
            row_errors.append(f"invalid difficulty '{difficulty}' (must be Easy/Medium/Hard)")
        if not question:
            row_errors.append("question is empty")
        if not solution:
            row_errors.append("solution is empty")

        if row_errors:
            errors.append(f"  Row {i}: {'; '.join(row_errors)}")
            skipped += 1
            continue

        if not dry_run:
            add_question(topic, difficulty, question, solution, source, tags)

        imported += 1
        if imported % 100 == 0:
            tag = "[DRY] " if dry_run else ""
            print(f"  {tag}✅ Processed {imported}...")

    # ── Summary ───────────────────────────────────────────────────────
    print(f"\n{'─'*45}")
    print(f"  Total rows   : {total}")
    print(f"  Imported     : {imported}")
    print(f"  Skipped      : {skipped}")
    if errors:
        print(f"\n  ⚠️  Errors:")
        for e in errors[:10]:
            print(e)
        if len(errors) > 10:
            print(f"  ...and {len(errors)-10} more")
    if dry_run:
        print(f"\n  ℹ️  Dry run complete. Run WITHOUT --dry-run to import.")
    else:
        print(f"\n  ✅ Done! Restart Streamlit and check the Practice tab.")
    print(f"{'─'*45}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file",    required=True, help="Path to your CSV file")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, do not save")
    args = parser.parse_args()
    import_csv(args.file, args.dry_run)
