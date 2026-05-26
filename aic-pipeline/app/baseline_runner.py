import importlib.util
import sys
import time
import tracemalloc
from pathlib import Path

import numpy as np
import pandas as pd

LEGACY_PIPELINE_PATH = Path("/app/before_project/aic_pipeline.py")
BASELINE_VERSION = "pre-optimization-pipeline"
METRIC_VERSION = "aic-metrics-v1"

DEFAULT_KEYWORDS = [
    "however", "although", "because", "why", "how", "compare",
    "contrast", "analyze", "evaluate", "critique", "moreover",
    "therefore", "consequently", "alternatively", "nevertheless",
]

_legacy = None
_backend = None


def preload_baseline_model():
    global _backend
    legacy = _load_legacy_pipeline()
    preferred_backend = legacy.EmbeddingBackend(
        prefer="sbert",
        sbert_model="paraphrase-multilingual-mpnet-base-v2",
    )
    try:
        preferred_backend.fit(["warmup text for initialization"])
        _backend = preferred_backend
        print("[pipeline] Baseline embedding backend initialized: sbert", flush=True)
    except Exception as exc:
        fallback_backend = legacy.EmbeddingBackend(prefer="tfidf")
        fallback_backend.fit(["warmup text for initialization"])
        _backend = fallback_backend
        print(f"[pipeline] Baseline fallback activated: tfidf ({exc})", flush=True)


def run_baseline_analysis(payload: dict) -> dict:
    global _backend
    legacy = _load_legacy_pipeline()
    started = time.perf_counter()
    stage_runtimes = {}
    trace_started_here = not tracemalloc.is_tracing()
    if trace_started_here:
        tracemalloc.start()

    def _mark_stage(name, stage_started):
        stage_runtimes[name] = round((time.perf_counter() - stage_started) * 1000, 3)

    try:
        if _backend is None:
            preload_baseline_model()

        sub = payload["submission"]
        cfg = payload.get("config") or {}

        stage_started = time.perf_counter()
        df = pd.DataFrame([{
            "sample_id": sub.get("sample_id", "x"),
            "course": sub.get("course", "default"),
            "student_id": sub.get("student_id", "x"),
            "chatgpt_before": legacy.safe_text(sub["chatgpt_before"]),
            "user": legacy.safe_text(sub["user"]),
            "essay": legacy.safe_text(sub["essay"]),
            "rating": np.nan,
        }])
        _mark_stage("prepare_input", stage_started)

        keywords = cfg.get("critical_keywords") or DEFAULT_KEYWORDS
        stage_started = time.perf_counter()
        df = legacy.compute_PI(df, keywords, weights=cfg.get("pi_weights", [0.4, 0.3, 0.3]))
        _mark_stage("compute_pi", stage_started)

        pipeline_cfg = {
            "ui_oi": {
                "topic_score_alpha": cfg.get("topic_score_alpha", 1.0),
                "topic_score_beta": cfg.get("topic_score_beta", 1.0),
                "min_course_samples": 1,
            }
        }
        stage_started = time.perf_counter()
        df = legacy.compute_UI_OI(df, _backend, pipeline_cfg)
        _mark_stage("compute_ui_oi", stage_started)

        weights_cfg = {
            "weights": {
                "mode": "equal",
                "clip_negative": True,
                "min_ratings": 10,
                "n_folds": 5,
            }
        }
        stage_started = time.perf_counter()
        df, weights = legacy.fit_weights_and_aic(df, weights_cfg)
        _mark_stage("fit_weights_and_aic", stage_started)

        row = df.iloc[0]
        scores = {
            "pi": _float(row.get("PI")),
            "ui": _float(row.get("UI")),
            "oi": _float(row.get("OI")),
            "aic": _float(row.get("AIC")),
        }
        _, peak_bytes = tracemalloc.get_traced_memory()
        total_runtime_ms = round((time.perf_counter() - started) * 1000, 3)

        return {
            "job_id": payload["job_id"],
            "pi": scores["pi"],
            "ui": scores["ui"],
            "oi": scores["oi"],
            "aic": scores["aic"],
            "topic_score": _float(row.get("topic_score")),
            "weight_pi": float(weights[0]),
            "weight_ui": float(weights[1]),
            "weight_oi": float(weights[2]),
            "pi_depth_tokens": _int(row.get("pi_depth_tokens")),
            "pi_depth_norm": _float(row.get("pi_depth_norm")),
            "pi_critical_ratio": _float(row.get("pi_critical_ratio")),
            "pi_avg_sent_len": _float(row.get("pi_avg_sent_len")),
            "pi_ttr": _float(row.get("pi_ttr")),
            "pi_complexity": _float(row.get("pi_complexity")),
            "ui_cos_similarity": _float(row.get("ui_cos_similarity")),
            "ui_distance": _float(row.get("ui_distance")),
            "ui_newinfo_ratio": _float(row.get("ui_newinfo_ratio")),
            "oi_topic_score_raw": _float(row.get("topic_score")),
            "embedding_backend": _backend.kind if _backend else "unknown",
            "analysis_metadata": {
                "metric_version": METRIC_VERSION,
                "optimized_version": BASELINE_VERSION,
                "baseline_version": None,
                "processed_count": 1,
                "total_runtime_ms": total_runtime_ms,
                "memory_peak_kb": round(peak_bytes / 1024, 3),
                "stage_runtimes_ms": stage_runtimes,
                "baseline_runtime_ms": None,
                "baseline_memory_peak_kb": None,
                "baseline_scores": scores,
                "runtime_delta_pct": None,
                "memory_delta_pct": None,
                "score_deltas": None,
                "quality_passed": None,
                "bootstrap_passed": None,
            },
        }
    except Exception as exc:
        backend_name = _backend.kind if _backend else "uninitialized"
        raise RuntimeError(f"run_baseline_analysis failed (embedding_backend={backend_name}): {exc}") from exc
    finally:
        if trace_started_here and tracemalloc.is_tracing():
            tracemalloc.stop()


def run_baseline_analysis_batch(payload: dict) -> dict:
    global _backend
    legacy = _load_legacy_pipeline()
    started = time.perf_counter()
    stage_runtimes = {}
    trace_started_here = not tracemalloc.is_tracing()
    if trace_started_here:
        tracemalloc.start()

    def _mark_stage(name, stage_started):
        stage_runtimes[name] = round((time.perf_counter() - stage_started) * 1000, 3)

    try:
        if _backend is None:
            preload_baseline_model()

        submissions = payload.get("submissions") or []
        if not submissions:
            raise ValueError("Batch baseline analysis requires at least one submission")
        cfg = payload.get("config") or {}

        stage_started = time.perf_counter()
        df = pd.DataFrame([
            {
                "sample_id": sub.get("sample_id", f"x-{idx}"),
                "course": sub.get("course", "default"),
                "student_id": sub.get("student_id", "x"),
                "chatgpt_before": legacy.safe_text(sub["chatgpt_before"]),
                "user": legacy.safe_text(sub["user"]),
                "essay": legacy.safe_text(sub["essay"]),
                "rating": np.nan,
            }
            for idx, sub in enumerate(submissions)
        ])
        _mark_stage("prepare_input", stage_started)

        keywords = cfg.get("critical_keywords") or DEFAULT_KEYWORDS
        stage_started = time.perf_counter()
        df = legacy.compute_PI(df, keywords, weights=cfg.get("pi_weights", [0.4, 0.3, 0.3]))
        _mark_stage("compute_pi", stage_started)

        pipeline_cfg = {
            "ui_oi": {
                "topic_score_alpha": cfg.get("topic_score_alpha", 1.0),
                "topic_score_beta": cfg.get("topic_score_beta", 1.0),
                "min_course_samples": 1,
            }
        }
        stage_started = time.perf_counter()
        df = legacy.compute_UI_OI(df, _backend, pipeline_cfg)
        _mark_stage("compute_ui_oi", stage_started)

        weights_cfg = {
            "weights": {
                "mode": "equal",
                "clip_negative": True,
                "min_ratings": 10,
                "n_folds": 5,
            }
        }
        stage_started = time.perf_counter()
        df, weights = legacy.fit_weights_and_aic(df, weights_cfg)
        _mark_stage("fit_weights_and_aic", stage_started)

        results = [_row_response(payload["job_id"], row, weights) for _, row in df.iterrows()]
        scores = _average_scores(results)
        _, peak_bytes = tracemalloc.get_traced_memory()
        total_runtime_ms = round((time.perf_counter() - started) * 1000, 3)
        analysis_metadata = {
            "metric_version": METRIC_VERSION,
            "optimized_version": BASELINE_VERSION,
            "baseline_version": None,
            "processed_count": len(results),
            "total_runtime_ms": total_runtime_ms,
            "memory_peak_kb": round(peak_bytes / 1024, 3),
            "stage_runtimes_ms": stage_runtimes,
            "baseline_runtime_ms": None,
            "baseline_memory_peak_kb": None,
            "baseline_scores": scores,
            "runtime_delta_pct": None,
            "memory_delta_pct": None,
            "score_deltas": None,
            "quality_passed": None,
            "bootstrap_passed": None,
        }

        return {
            "job_id": payload["job_id"],
            "processed_count": len(results),
            "scores": scores,
            "results": results,
            "analysis_metadata": analysis_metadata,
        }
    except Exception as exc:
        backend_name = _backend.kind if _backend else "uninitialized"
        raise RuntimeError(f"run_baseline_analysis_batch failed (embedding_backend={backend_name}): {exc}") from exc
    finally:
        if trace_started_here and tracemalloc.is_tracing():
            tracemalloc.stop()


def _load_legacy_pipeline():
    global _legacy
    if _legacy is not None:
        return _legacy
    if not LEGACY_PIPELINE_PATH.exists():
        raise RuntimeError(f"Pre-optimization pipeline not found: {LEGACY_PIPELINE_PATH}")
    spec = importlib.util.spec_from_file_location("pre_optimization_aic_pipeline", LEGACY_PIPELINE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _legacy = module
    return module


def _float(value) -> float:
    return float(value) if value is not None and not (isinstance(value, float) and np.isnan(value)) else 0.0


def _int(value) -> int:
    return int(value) if value is not None and not (isinstance(value, float) and np.isnan(value)) else 0


def _row_response(job_id, row, weights):
    return {
        "job_id": job_id,
        "pi": _float(row.get("PI")),
        "ui": _float(row.get("UI")),
        "oi": _float(row.get("OI")),
        "aic": _float(row.get("AIC")),
        "topic_score": _float(row.get("topic_score")),
        "weight_pi": float(weights[0]),
        "weight_ui": float(weights[1]),
        "weight_oi": float(weights[2]),
        "pi_depth_tokens": _int(row.get("pi_depth_tokens")),
        "pi_depth_norm": _float(row.get("pi_depth_norm")),
        "pi_critical_ratio": _float(row.get("pi_critical_ratio")),
        "pi_avg_sent_len": _float(row.get("pi_avg_sent_len")),
        "pi_ttr": _float(row.get("pi_ttr")),
        "pi_complexity": _float(row.get("pi_complexity")),
        "ui_cos_similarity": _float(row.get("ui_cos_similarity")),
        "ui_distance": _float(row.get("ui_distance")),
        "ui_newinfo_ratio": _float(row.get("ui_newinfo_ratio")),
        "oi_topic_score_raw": _float(row.get("topic_score")),
        "embedding_backend": _backend.kind if _backend else "unknown",
        "analysis_metadata": None,
    }


def _average_scores(results):
    keys = ("pi", "ui", "oi", "aic")
    return {
        key: round(sum(float(result[key]) for result in results) / len(results), 6)
        for key in keys
    }
