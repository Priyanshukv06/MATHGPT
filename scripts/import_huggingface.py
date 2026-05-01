"""
scripts/import_huggingface.py  v3 (FIXED)
─────────────────────────────────────────
CORRECTED dataset names (2025/2026):
  competition_math → DigitalLearningGmbH/MATH-lighteval
  gsm8k            → gsm8k  (no "openai/" prefix)
  deepmind         → deepmind/math_dataset

All trust_remote_code removed.

RUN:
  python scripts/import_huggingface.py --dataset all
  python scripts/import_huggingface.py --dataset math
  python scripts/import_huggingface.py --dataset gsm8k
  python scripts/import_huggingface.py --dataset deepmind --deepmind-per-module 2000
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Topic maps ────────────────────────────────────────────────────────
HF_TOPIC_MAP = {
    "algebra"                  : "🔢 Algebra",
    "intermediate_algebra"     : "🔢 Algebra",
    "prealgebra"               : "🔢 Algebra",
    "number_theory"            : "🔢 Algebra",
    "arithmetic"               : "🔢 Algebra",
    "polynomials"              : "🔢 Algebra",
    "precalculus"              : "📈 Calculus",
    "calculus"                 : "📈 Calculus",
    "differentiate"            : "📈 Calculus",
    "integrate"                : "📈 Calculus",
    "geometry"                 : "🔷 Geometry",
    "counting_and_probability" : "🎲 Probability",
    "probability"              : "🎲 Probability",
    "linear_algebra"           : "📊 Linear Algebra",
    "matrix"                   : "📊 Linear Algebra",
    "trigonometry"             : "📐 Trigonometry",
}

DEEPMIND_ALL_MODULES = [
    ("algebra__linear_1d",                "🔢 Algebra",        "Easy",   "linear equations"),
    ("algebra__linear_1d_composed",       "🔢 Algebra",        "Medium", "linear equations composed"),
    ("algebra__linear_2d",                "🔢 Algebra",        "Medium", "linear equations 2 variables"),
    ("algebra__linear_2d_composed",       "🔢 Algebra",        "Hard",   "linear equations 2 variables composed"),
    ("algebra__polynomial_roots",         "🔢 Algebra",        "Medium", "polynomial roots"),
    ("algebra__polynomial_roots_composed","🔢 Algebra",        "Hard",   "polynomial roots composed"),
    ("algebra__sequence_next_term",       "🔢 Algebra",        "Easy",   "sequences"),
    ("algebra__sequence_nth_term",        "🔢 Algebra",        "Medium", "sequences nth term"),
    ("arithmetic__add_or_sub",            "🔢 Algebra",        "Easy",   "addition subtraction"),
    ("arithmetic__add_or_sub_in_base",    "🔢 Algebra",        "Medium", "number base arithmetic"),
    ("arithmetic__add_sub_multiple",      "🔢 Algebra",        "Medium", "multi-step arithmetic"),
    ("arithmetic__div",                   "🔢 Algebra",        "Easy",   "division"),
    ("arithmetic__mixed",                 "🔢 Algebra",        "Medium", "mixed arithmetic"),
    ("arithmetic__mul",                   "🔢 Algebra",        "Easy",   "multiplication"),
    ("arithmetic__mul_div_multiple",      "🔢 Algebra",        "Medium", "multiplication division"),
    ("arithmetic__nearest_integer_root",  "🔢 Algebra",        "Medium", "integer roots"),
    ("calculus__differentiate",           "📈 Calculus",       "Medium", "differentiation"),
    ("calculus__differentiate_composed",  "📈 Calculus",       "Hard",   "differentiation chain rule"),
    ("comparison__closest",               "🔢 Algebra",        "Easy",   "comparison"),
    ("comparison__kth_biggest",           "🔢 Algebra",        "Easy",   "ordering"),
    ("comparison__pair",                  "🔢 Algebra",        "Easy",   "comparison pairs"),
    ("comparison__pair_composed",         "🔢 Algebra",        "Medium", "comparison composed"),
    ("comparison__sort",                  "🔢 Algebra",        "Easy",   "sorting"),
    ("geometry__area",                    "🔷 Geometry",       "Easy",   "area"),
    ("geometry__volume",                  "🔷 Geometry",       "Medium", "volume"),
    ("geometry__circle_area_by_formula",  "🔷 Geometry",       "Easy",   "circle area"),
    ("linear_algebra__eigenvalues",       "📊 Linear Algebra", "Hard",   "eigenvalues"),
    ("linear_algebra__matrix_vector_mul", "📊 Linear Algebra", "Medium", "matrix multiplication"),
    ("linear_algebra__vector_norms",      "📊 Linear Algebra", "Medium", "vector norms"),
    ("measurement__conversion",           "🔢 Algebra",        "Easy",   "unit conversion"),
    ("measurement__time",                 "🔢 Algebra",        "Easy",   "time problems"),
    ("numbers__base_conversion",          "🔢 Algebra",        "Medium", "number bases"),
    ("numbers__div_remainder",            "🔢 Algebra",        "Easy",   "division remainder"),
    ("numbers__div_remainder_composed",   "🔢 Algebra",        "Medium", "division composed"),
    ("numbers__gcd",                      "🔢 Algebra",        "Medium", "GCD HCF"),
    ("numbers__is_factor",                "🔢 Algebra",        "Easy",   "factors"),
    ("numbers__is_prime",                 "🔢 Algebra",        "Easy",   "prime numbers"),
    ("numbers__lcm",                      "🔢 Algebra",        "Medium", "LCM"),
    ("numbers__list_prime_factors",       "🔢 Algebra",        "Medium", "prime factorisation"),
    ("numbers__place_value",              "🔢 Algebra",        "Easy",   "place value"),
    ("numbers__round_number",             "🔢 Algebra",        "Easy",   "rounding"),
    ("polynomials__add",                  "🔢 Algebra",        "Easy",   "polynomial addition"),
    ("polynomials__coefficient_named",    "🔢 Algebra",        "Easy",   "polynomial coefficients"),
    ("polynomials__compose",              "🔢 Algebra",        "Hard",   "polynomial composition"),
    ("polynomials__evaluate",             "🔢 Algebra",        "Easy",   "polynomial evaluation"),
    ("polynomials__evaluate_composed",    "🔢 Algebra",        "Medium", "polynomial evaluation composed"),
    ("polynomials__expand",               "🔢 Algebra",        "Medium", "polynomial expansion"),
    ("polynomials__roots",                "🔢 Algebra",        "Medium", "polynomial roots"),
    ("probability__swr_p_level_set",      "🎲 Probability",    "Medium", "probability sampling"),
    ("probability__swr_p_sequence",       "🎲 Probability",    "Hard",   "probability sequences"),
]


def _map_difficulty(level_str: str) -> str:
    """Convert 'Level 1'-'Level 5' → Easy/Medium/Hard."""
    try:
        n = int(str(level_str).strip().replace("Level ", "").replace("level", "").strip())
        if n <= 2: return "Easy"
        if n == 3: return "Medium"
        return "Hard"
    except Exception:
        return "Medium"


# ══════════════════════════════════════════════════════════════════════
# Dataset 1 — competition_math (12,500 problems)
# NEW name: DigitalLearningGmbH/MATH-lighteval
# Fields: problem, solution, level, type
# ══════════════════════════════════════════════════════════════════════

def import_competition_math() -> int:
    from datasets import load_dataset
    from utils.question_bank import add_question

    # Try multiple known working names in order
    CANDIDATE_NAMES = [
        ("DigitalLearningGmbH/MATH-lighteval", "train"),
        ("qwedsacf/competition_math",          "train"),
        ("lighteval/MATH",                     "train"),
    ]

    ds = None
    used_name = ""
    for name, split in CANDIDATE_NAMES:
        try:
            print(f"  Trying {name}…")
            ds = load_dataset(name, split=split)
            used_name = name
            print(f"  ✅ Loaded from {name}")
            break
        except Exception as e:
            print(f"  ❌ {name} failed: {e}")

    if ds is None:
        print("  ❌ All competition_math sources failed. Skipping.")
        return 0

    print(f"\n📥 competition_math ({used_name}) — {len(ds)} questions…")
    count = 0
    for item in ds:
        # field names vary slightly by dataset
        question = (item.get("problem") or item.get("question") or "").strip()
        solution = (item.get("solution") or item.get("answer") or "").strip()
        level    = item.get("level", "Level 3")
        subject  = (item.get("type") or item.get("subject") or "algebra").lower().replace(" ", "_")

        if not question or not solution:
            continue

        topic      = HF_TOPIC_MAP.get(subject, "🔢 Algebra")
        difficulty = _map_difficulty(level)

        add_question(
            topic=topic, difficulty=difficulty,
            question=question, solution=solution,
            source=f"AMC/AIME Competition Math ({used_name})",
            tags=subject,
        )
        count += 1
        if count % 500 == 0:
            print(f"  ✅ {count} imported…")

    print(f"  🎉 competition_math TOTAL: {count}")
    return count


# ══════════════════════════════════════════════════════════════════════
# Dataset 2 — gsm8k (8,792 problems)
# CORRECT name: "gsm8k" (NOT "openai/gsm8k")
# Fields: question, answer (answer ends with "#### <number>")
# ══════════════════════════════════════════════════════════════════════

def import_gsm8k() -> int:
    from datasets import load_dataset
    from utils.question_bank import add_question

    print("\n📥 gsm8k — importing ALL 8,792 questions…")
    count = 0

    for split in ["train", "test"]:
        try:
            # CORRECT: just "gsm8k", not "openai/gsm8k"
            ds = load_dataset("gsm8k", "main", split=split)
            split_count = 0
            for item in ds:
                question = item.get("question", "").strip()
                answer   = item.get("answer",   "").strip()
                if not question:
                    continue
                # answer format: "...reasoning... #### 42"
                # Keep the full reasoning as solution — it's valuable!
                add_question(
                    topic="🔢 Algebra", difficulty="Easy",
                    question=question, solution=answer,
                    source=f"GSM8K Grade School Math [{split}]",
                    tags="word problem, arithmetic, reasoning",
                )
                count += 1
                split_count += 1
                if split_count % 500 == 0:
                    print(f"  [{split}] ✅ {split_count}…")
            print(f"  [{split}] done → {split_count} questions")
        except Exception as e:
            print(f"  [{split}] ❌ Failed: {e}")

    print(f"  🎉 gsm8k TOTAL: {count}")
    return count


# ══════════════════════════════════════════════════════════════════════
# Dataset 3 — deepmind/math_dataset (50 modules, 2M each)
# CORRECT name: "deepmind/math_dataset"
# Fields: question, answer
# ══════════════════════════════════════════════════════════════════════

def import_deepmind_math(per_module: int = 2000) -> int:
    from datasets import load_dataset
    from utils.question_bank import add_question

    cap_str = "ALL" if per_module == 0 else str(per_module)
    print(f"\n📥 deepmind/math_dataset — {len(DEEPMIND_ALL_MODULES)} modules, {cap_str}/module…")

    grand_total = 0
    skipped_modules = []

    for idx, (module, topic, difficulty, tags) in enumerate(DEEPMIND_ALL_MODULES, 1):
        module_total = 0
        try:
            # CORRECT name: "deepmind/math_dataset"
            ds = load_dataset("deepmind/math_dataset", module, split="train")
            for item in ds:
                if per_module > 0 and module_total >= per_module:
                    break
                q = item.get("question", "").strip()
                a = item.get("answer",   "").strip()
                if not q:
                    continue
                add_question(
                    topic=topic, difficulty=difficulty,
                    question=q, solution=a,
                    source=f"DeepMind Math Dataset ({module})",
                    tags=tags,
                )
                module_total += 1
                grand_total  += 1

            print(f"  [{idx:02d}/{len(DEEPMIND_ALL_MODULES)}] {module}: {module_total} ✅")

        except Exception as e:
            skipped_modules.append(module)
            print(f"  [{idx:02d}/{len(DEEPMIND_ALL_MODULES)}] {module}: SKIPPED — {e}")

    if skipped_modules:
        print(f"\n  ⚠️  {len(skipped_modules)} modules skipped: {skipped_modules}")

    print(f"  🎉 deepmind TOTAL: {grand_total}")
    return grand_total


# ══════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        choices=["math", "gsm8k", "deepmind", "all"],
        default="all",
    )
    parser.add_argument(
        "--deepmind-per-module",
        type=int, default=2000,
        help="Questions per DeepMind module. 0 = unlimited. Default: 2000",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  MathGPT — HuggingFace Question Importer  v3")
    print("=" * 60)

    if args.dataset == "all":
        dm = args.deepmind_per_module * len(DEEPMIND_ALL_MODULES) if args.deepmind_per_module > 0 else "unlimited"
        print(f"\n📊 Estimated import:")
        print(f"  competition_math : ~12,500 (all)")
        print(f"  gsm8k            : ~8,792  (all)")
        print(f"  deepmind         : ~{dm}")
        print()

    total = 0
    if args.dataset in ("math",     "all"): total += import_competition_math()
    if args.dataset in ("gsm8k",    "all"): total += import_gsm8k()
    if args.dataset in ("deepmind", "all"): total += import_deepmind_math(args.deepmind_per_module)

    print("\n" + "=" * 60)
    print(f"  ✅ GRAND TOTAL: {total:,} questions imported")
    print(f"  📁 Saved → question_bank.json")
    print(f"  🔁 Restart Streamlit to use them!")
    print("=" * 60)
