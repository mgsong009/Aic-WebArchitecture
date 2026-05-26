import sys
import time
import tracemalloc
import numpy as np
import pandas as pd

sys.path.insert(0, "/app")

# aic_pipeline.py must be copied to /app (container root) — see Dockerfile
from aic_pipeline import (
    EmbeddingBackend,
    compute_PI,
    compute_UI_OI,
    fit_weights_and_aic,
    safe_text,
)

_backend = None  # module-level singleton; loaded once at startup

DEFAULT_KEYWORDS = [
    "however", "although", "because", "why", "how", "compare",
    "contrast", "analyze", "evaluate", "critique", "moreover",
    "therefore", "consequently", "alternatively", "nevertheless",
]

METRIC_VERSION = "aic-metrics-v1"
OPTIMIZED_VERSION = "pipeline-wrapper-v1"


def preload_model():
    global _backend
    preferred_backend = EmbeddingBackend(prefer="sbert", sbert_model="paraphrase-multilingual-mpnet-base-v2")
    try:
        preferred_backend.fit(["warmup text for initialization"])
        _backend = preferred_backend
        print("[pipeline] Embedding backend initialized: sbert", flush=True)
    except Exception as exc:
        fallback_backend = EmbeddingBackend(prefer="tfidf")
        fallback_backend.fit(["warmup text for initialization"])
        _backend = fallback_backend
        print(f"[pipeline] Embedding fallback activated: tfidf ({exc})", flush=True)


def run_analysis(payload: dict) -> dict:
    global _backend
    started = time.perf_counter()
    stage_runtimes = {}
    trace_started_here = not tracemalloc.is_tracing()
    if trace_started_here:
        tracemalloc.start()

    def _mark_stage(name, stage_started):
        stage_runtimes[name] = round((time.perf_counter() - stage_started) * 1000, 3)

    try:
        if _backend is None:
            preload_model()

        sub = payload["submission"]
        cfg = payload["config"]

        stage_started = time.perf_counter()
        df = pd.DataFrame([{
            "sample_id": sub.get("sample_id", "x"),
            "course": sub.get("course", "default"),
            "student_id": sub.get("student_id", "x"),
            "chatgpt_before": safe_text(sub["chatgpt_before"]),
            "user": safe_text(sub["user"]),
            "essay": safe_text(sub["essay"]),
            "rating": np.nan,
        }])
        _mark_stage("prepare_input", stage_started)

        keywords = cfg.get("critical_keywords") or DEFAULT_KEYWORDS
        stage_started = time.perf_counter()
        df = compute_PI(df, keywords, weights=cfg.get("pi_weights", [0.4, 0.3, 0.3]))
        _mark_stage("compute_pi", stage_started)

        pipeline_cfg = {
            "ui_oi": {
                "topic_score_alpha": cfg.get("topic_score_alpha", 1.0),
                "topic_score_beta": cfg.get("topic_score_beta", 1.0),
                "min_course_samples": 1,
            }
        }
        stage_started = time.perf_counter()
        df = compute_UI_OI(df, _backend, pipeline_cfg)
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
        df, w = fit_weights_and_aic(df, weights_cfg)
        _mark_stage("fit_weights_and_aic", stage_started)

        row = df.iloc[0]

        def _f(col):
            v = row.get(col)
            return float(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else 0.0

        def _i(col):
            v = row.get(col)
            return int(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else 0

        scores = {
            "pi": _f("PI"),
            "ui": _f("UI"),
            "oi": _f("OI"),
            "aic": _f("AIC"),
        }
        _, peak_bytes = tracemalloc.get_traced_memory()
        total_runtime_ms = round((time.perf_counter() - started) * 1000, 3)
        analysis_metadata = _build_analysis_metadata(cfg, scores, total_runtime_ms, peak_bytes, stage_runtimes)

        return {
            "job_id": payload["job_id"],
            "pi": scores["pi"],
            "ui": scores["ui"],
            "oi": scores["oi"],
            "aic": scores["aic"],
            "topic_score": _f("topic_score"),
            "weight_pi": float(w[0]),
            "weight_ui": float(w[1]),
            "weight_oi": float(w[2]),
            "pi_depth_tokens": _i("pi_depth_tokens"),
            "pi_depth_norm": _f("pi_depth_norm"),
            "pi_critical_ratio": _f("pi_critical_ratio"),
            "pi_avg_sent_len": _f("pi_avg_sent_len"),
            "pi_ttr": _f("pi_ttr"),
            "pi_complexity": _f("pi_complexity"),
            "ui_cos_similarity": _f("ui_cos_similarity"),
            "ui_distance": _f("ui_distance"),
            "ui_newinfo_ratio": _f("ui_newinfo_ratio"),
            "oi_topic_score_raw": _f("topic_score"),
            "embedding_backend": _backend.kind if _backend else "unknown",
            "analysis_metadata": analysis_metadata,
        }
    except Exception as exc:
        backend_name = _backend.kind if _backend else "uninitialized"
        raise RuntimeError(f"run_analysis failed (embedding_backend={backend_name}): {exc}") from exc
    finally:
        if trace_started_here and tracemalloc.is_tracing():
            tracemalloc.stop()


def run_analysis_batch(payload: dict) -> dict:
    global _backend
    started = time.perf_counter()
    stage_runtimes = {}
    trace_started_here = not tracemalloc.is_tracing()
    if trace_started_here:
        tracemalloc.start()

    def _mark_stage(name, stage_started):
        stage_runtimes[name] = round((time.perf_counter() - stage_started) * 1000, 3)

    try:
        if _backend is None:
            preload_model()

        submissions = payload.get("submissions") or []
        if not submissions:
            raise ValueError("Batch analysis requires at least one submission")
        cfg = payload["config"]

        stage_started = time.perf_counter()
        df = pd.DataFrame([
            {
                "sample_id": sub.get("sample_id", f"x-{idx}"),
                "course": sub.get("course", "default"),
                "student_id": sub.get("student_id", "x"),
                "chatgpt_before": safe_text(sub["chatgpt_before"]),
                "user": safe_text(sub["user"]),
                "essay": safe_text(sub["essay"]),
                "rating": np.nan,
            }
            for idx, sub in enumerate(submissions)
        ])
        _mark_stage("prepare_input", stage_started)

        keywords = cfg.get("critical_keywords") or DEFAULT_KEYWORDS
        stage_started = time.perf_counter()
        df = compute_PI(df, keywords, weights=cfg.get("pi_weights", [0.4, 0.3, 0.3]))
        _mark_stage("compute_pi", stage_started)

        pipeline_cfg = {
            "ui_oi": {
                "topic_score_alpha": cfg.get("topic_score_alpha", 1.0),
                "topic_score_beta": cfg.get("topic_score_beta", 1.0),
                "min_course_samples": 1,
            }
        }
        stage_started = time.perf_counter()
        df = compute_UI_OI(df, _backend, pipeline_cfg)
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
        df, weights = fit_weights_and_aic(df, weights_cfg)
        _mark_stage("fit_weights_and_aic", stage_started)

        results = [_row_response(payload["job_id"], row, weights) for _, row in df.iterrows()]
        scores = _average_scores(results)
        _, peak_bytes = tracemalloc.get_traced_memory()
        total_runtime_ms = round((time.perf_counter() - started) * 1000, 3)
        analysis_metadata = _build_analysis_metadata(
            cfg,
            scores,
            total_runtime_ms,
            peak_bytes,
            stage_runtimes,
            processed_count=len(results),
        )

        return {
            "job_id": payload["job_id"],
            "processed_count": len(results),
            "scores": scores,
            "results": results,
            "analysis_metadata": analysis_metadata,
        }
    except Exception as exc:
        backend_name = _backend.kind if _backend else "uninitialized"
        raise RuntimeError(f"run_analysis_batch failed (embedding_backend={backend_name}): {exc}") from exc
    finally:
        if trace_started_here and tracemalloc.is_tracing():
            tracemalloc.stop()


def _row_response(job_id, row, weights):
    def _f(col):
        v = row.get(col)
        return float(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else 0.0

    def _i(col):
        v = row.get(col)
        return int(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else 0

    return {
        "job_id": job_id,
        "pi": _f("PI"),
        "ui": _f("UI"),
        "oi": _f("OI"),
        "aic": _f("AIC"),
        "topic_score": _f("topic_score"),
        "weight_pi": float(weights[0]),
        "weight_ui": float(weights[1]),
        "weight_oi": float(weights[2]),
        "pi_depth_tokens": _i("pi_depth_tokens"),
        "pi_depth_norm": _f("pi_depth_norm"),
        "pi_critical_ratio": _f("pi_critical_ratio"),
        "pi_avg_sent_len": _f("pi_avg_sent_len"),
        "pi_ttr": _f("pi_ttr"),
        "pi_complexity": _f("pi_complexity"),
        "ui_cos_similarity": _f("ui_cos_similarity"),
        "ui_distance": _f("ui_distance"),
        "ui_newinfo_ratio": _f("ui_newinfo_ratio"),
        "oi_topic_score_raw": _f("topic_score"),
        "embedding_backend": _backend.kind if _backend else "unknown",
        "analysis_metadata": None,
    }


def _average_scores(results):
    keys = ("pi", "ui", "oi", "aic")
    return {
        key: round(sum(float(result[key]) for result in results) / len(results), 6)
        for key in keys
    }


def _build_analysis_metadata(cfg, scores, total_runtime_ms, peak_bytes, stage_runtimes, processed_count=1):
    baseline_scores = cfg.get("baseline_scores") or {}
    score_deltas = {
        key: round(scores[key] - float(baseline_scores[key]), 6)
        for key in ("pi", "ui", "oi", "aic")
        if key in baseline_scores and baseline_scores[key] is not None
    }
    baseline_runtime_ms = cfg.get("baseline_runtime_ms")
    baseline_memory_peak_kb = cfg.get("baseline_memory_peak_kb")

    return {
        "metric_version": METRIC_VERSION,
        "optimized_version": OPTIMIZED_VERSION,
        "baseline_version": cfg.get("baseline_version"),
        "processed_count": processed_count,
        "total_runtime_ms": total_runtime_ms,
        "memory_peak_kb": round(peak_bytes / 1024, 3),
        "stage_runtimes_ms": stage_runtimes,
        "baseline_runtime_ms": baseline_runtime_ms,
        "baseline_memory_peak_kb": baseline_memory_peak_kb,
        "baseline_scores": baseline_scores or None,
        "runtime_delta_pct": _delta_pct(total_runtime_ms, baseline_runtime_ms),
        "memory_delta_pct": _delta_pct(round(peak_bytes / 1024, 3), baseline_memory_peak_kb),
        "score_deltas": score_deltas or None,
        "quality_passed": _quality_passed(score_deltas) if score_deltas else None,
        "bootstrap_passed": cfg.get("bootstrap_passed"),
    }


def _delta_pct(current, baseline):
    if baseline in (None, 0):
        return None
    return round((float(current) - float(baseline)) / float(baseline) * 100, 3)


def _quality_passed(score_deltas):
    tolerance = 0.01
    return all(abs(delta) <= tolerance for delta in score_deltas.values())
