import argparse
import cProfile
import json
import pstats
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path

import pandas as pd

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from aic_pipeline import EmbeddingBackend, compute_PI, compute_UI_OI, fit_weights_and_aic, safe_text, validate
from dummy_data_gen import build_dummy_frame


KEYWORDS = [
    "however", "although", "because", "why", "how", "compare",
    "contrast", "analyze", "evaluate", "critique", "moreover",
    "therefore", "consequently", "alternatively", "nevertheless",
]


def run_once(rows: int, backend_name: str, bootstrap_jobs: int, seed: int):
    df = build_dummy_frame(rows, seed=seed)
    for col in ["chatgpt_before", "user", "essay"]:
        df[col] = df[col].fillna("").apply(safe_text)

    timings = {}

    t0 = time.perf_counter()
    df = compute_PI(df, KEYWORDS)
    timings["compute_PI"] = time.perf_counter() - t0

    backend = EmbeddingBackend(prefer=backend_name, sbert_batch_size=16, sbert_chunk_size=64)
    cfg = {"ui_oi": {"topic_score_alpha": 1.0, "topic_score_beta": 1.0, "min_course_samples": 3}}
    t0 = time.perf_counter()
    df = compute_UI_OI(df, backend, cfg)
    timings["compute_UI_OI"] = time.perf_counter() - t0

    weights_cfg = {"weights": {"mode": "equal", "clip_negative": True, "min_ratings": 10, "n_folds": 5}}
    t0 = time.perf_counter()
    df, weights = fit_weights_and_aic(df, weights_cfg)
    timings["fit_weights_and_aic"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    validation = validate(df, n_jobs=bootstrap_jobs)
    timings["validate"] = time.perf_counter() - t0

    return {
        "rows": rows,
        "backend": backend.kind,
        "timings_sec": timings,
        "weights": list(weights),
        "validation": validation,
        "metric_means": {
            metric: float(df[metric].mean())
            for metric in ["PI", "UI", "OI", "AIC"]
        },
    }


def profile_run(rows: int, backend_name: str, bootstrap_jobs: int, seed: int, profile_path: Path):
    profiler = cProfile.Profile()
    tracemalloc.start()
    started = time.perf_counter()
    profiler.enable()
    result = run_once(rows, backend_name, bootstrap_jobs, seed)
    profiler.disable()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    result["total_sec"] = time.perf_counter() - started
    result["memory_peak_mb"] = peak / (1024 * 1024)

    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profiler.dump_stats(profile_path)
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmp:
        stats = pstats.Stats(profiler, stream=tmp).sort_stats("cumtime")
        stats.print_stats(30)
        tmp_path = Path(tmp.name)
    result["profile_top"] = tmp_path.read_text(encoding="utf-8")
    tmp_path.unlink(missing_ok=True)
    return result


def main():
    parser = argparse.ArgumentParser(description="Benchmark AIC pipeline metrics on dummy data.")
    parser.add_argument("--sizes", nargs="+", type=int, default=[25, 100, 500])
    parser.add_argument("--backend", choices=["tfidf", "sbert"], default="tfidf")
    parser.add_argument("--bootstrap-jobs", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path("benchmark/benchmark_results.json"))
    args = parser.parse_args()

    results = []
    for rows in args.sizes:
        profile_path = args.out.with_name(f"{args.out.stem}_{rows}.prof")
        results.append(profile_run(rows, args.backend, args.bootstrap_jobs, args.seed, profile_path))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps([
        {
            "rows": item["rows"],
            "backend": item["backend"],
            "total_sec": round(item["total_sec"], 4),
            "memory_peak_mb": round(item["memory_peak_mb"], 2),
            "timings_sec": {k: round(v, 4) for k, v in item["timings_sec"].items()},
        }
        for item in results
    ], indent=2))
    print(f"Wrote benchmark details to {args.out}")


if __name__ == "__main__":
    main()
