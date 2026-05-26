import argparse
import random
from pathlib import Path

import pandas as pd


COURSES = ["writing-101", "science-writing", "history-seminar", "media-literacy"]
CRITICAL_TERMS = ["however", "because", "therefore", "analyze", "compare", "evaluate"]
BASE_TERMS = [
    "evidence", "claim", "source", "draft", "argument", "revision", "context",
    "example", "reader", "paragraph", "feedback", "interpretation", "topic",
]


def make_text(rng: random.Random, n_tokens: int, include_critical: bool = False) -> str:
    words = []
    for i in range(n_tokens):
        if include_critical and i % 17 == 0:
            words.append(rng.choice(CRITICAL_TERMS))
        else:
            words.append(rng.choice(BASE_TERMS))

    sentences = []
    for start in range(0, len(words), 18):
        sentence = " ".join(words[start:start + 18]).capitalize()
        if sentence:
            sentences.append(sentence + ".")
    return " ".join(sentences)


def build_dummy_frame(rows: int, seed: int = 42) -> pd.DataFrame:
    rng = random.Random(seed)
    records = []
    for idx in range(rows):
        course = COURSES[idx % len(COURSES)]
        records.append({
            "sample_id": f"sample-{idx + 1}",
            "course": course,
            "student_id": f"student-{idx % 80 + 1}",
            "week": idx % 12 + 1,
            "session": idx % 3 + 1,
            "idx": idx,
            "chatgpt_before": make_text(rng, rng.randint(55, 95)),
            "user": make_text(rng, rng.randint(25, 80), include_critical=True),
            "essay": make_text(rng, rng.randint(90, 170), include_critical=idx % 4 == 0),
            "rating": round(2.0 + (idx % 31) / 10.0, 1),
        })
    return pd.DataFrame.from_records(records)


def main():
    parser = argparse.ArgumentParser(description="Generate representative dummy AIC pipeline data.")
    parser.add_argument("--rows", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path("benchmark/dummy_aic_data.csv"))
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    build_dummy_frame(args.rows, args.seed).to_csv(args.out, index=False, encoding="utf-8")
    print(f"Wrote {args.rows} rows to {args.out}")


if __name__ == "__main__":
    main()
