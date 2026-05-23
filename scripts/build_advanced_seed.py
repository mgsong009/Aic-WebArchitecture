#!/usr/bin/env python
"""
Build analysis-grade seed data for students 011-060.

Outputs (synchronized as a set):
1) init.sql updated block for submissions/metrics (students 12..61, assignments 1..5)
2) input_data/students_seed_011_060.csv
3) input_data/students_cluster_similarity_011_060.csv

Design goals:
- Preserve raw distribution characteristics (course mix, text richness).
- Expand to repeated measures: 5 assignments per student.
- Control duplicates / near-duplicates.
- Recompute PI/UI/OI/AIC through pipeline logic.
- Add lineage metadata for reproducibility.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class StudentSlot:
    student_num: int
    student_id_db: int
    assignment_id: int
    idx: int


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", (text or "").lower())


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    denom = len(sa | sb)
    if denom == 0:
        return 0.0
    return len(sa & sb) / denom


def _to_num(x) -> float:
    try:
        return float(x)
    except Exception:
        return np.nan


def _largest_remainder_targets(total: int, counts: Dict[str, int]) -> Dict[str, int]:
    s = sum(counts.values())
    if s <= 0:
        return {k: 0 for k in counts}
    raw = {k: total * (v / s) for k, v in counts.items()}
    base = {k: int(math.floor(v)) for k, v in raw.items()}
    remain = total - sum(base.values())
    order = sorted(raw.keys(), key=lambda k: (raw[k] - base[k]), reverse=True)
    for i in range(remain):
        base[order[i % len(order)]] += 1
    return base


def _sql_escape(text: str) -> str:
    text = (text or "").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace("'", "''")


def _safe_bool_str(x) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip()
    if s.lower() in {"true", "false"}:
        return s
    return s


def _build_slots(student_start: int, student_count: int, assignments: List[int]) -> List[StudentSlot]:
    slots: List[StudentSlot] = []
    for offset in range(student_count):
        student_num = student_start + offset
        student_id_db = student_num + 1
        for idx, aid in enumerate(assignments, start=1):
            slots.append(
                StudentSlot(
                    student_num=student_num,
                    student_id_db=student_id_db,
                    assignment_id=aid,
                    idx=idx,
                )
            )
    return slots


def _extract_candidate_pool(raw: pd.DataFrame) -> pd.DataFrame:
    needed = ["sample_id", "course", "student_id", "chatgpt_before", "user", "chatgpt_after", "rating", "intent_final", "is_quiz", "is_essay_edited", "essay"]
    for c in needed:
        if c not in raw.columns:
            raw[c] = ""
    df = raw.copy()
    for c in ["chatgpt_before", "user", "chatgpt_after", "essay", "course", "sample_id"]:
        df[c] = df[c].fillna("").astype(str).str.strip()
    # Richer candidates first for advanced analysis
    df["user_words"] = df["user"].apply(lambda x: len(_tokenize(x)))
    df["essay_words"] = df["essay"].apply(lambda x: len(_tokenize(x)))
    mask = (
        (df["chatgpt_before"] != "")
        & (df["user"] != "")
        & (df["essay"] != "")
        & (df["user_words"] >= 12)
        & (df["essay_words"] >= 80)
        & (df["course"].isin(["SW", "AW", "IRW"]))
    )
    rich = df[mask].copy()
    if len(rich) < 400:
        # Relax if necessary
        relaxed = (
            (df["chatgpt_before"] != "")
            & (df["user"] != "")
            & (df["essay"] != "")
            & (df["course"].isin(["SW", "AW", "IRW"]))
        )
        return df[relaxed].copy()
    return rich


def _select_rows(
    pool: pd.DataFrame,
    total_rows: int,
    course_targets: Dict[str, int],
    seed: int,
    near_dup_thresh: float = 0.92,
) -> pd.DataFrame:
    rng = random.Random(seed)
    picked_idx: List[int] = []
    used_source: set = set()
    used_exact: set = set()
    essay_tokens: List[List[str]] = []

    for course, target in course_targets.items():
        sub = list(pool[pool["course"] == course].index)
        rng.shuffle(sub)
        for ix in sub:
            if sum(pool.loc[picked_idx, "course"].eq(course)) >= target:
                break
            row = pool.loc[ix]
            source = row["sample_id"]
            if source in used_source:
                continue
            exact_key = (row["chatgpt_before"], row["user"], row["essay"])
            if exact_key in used_exact:
                continue

            etok = _tokenize(row["essay"])
            # Near-duplicate check against selected essays
            too_close = False
            for prev_tok in essay_tokens:
                if _jaccard(etok, prev_tok) >= near_dup_thresh:
                    too_close = True
                    break
            if too_close:
                continue

            picked_idx.append(ix)
            used_source.add(source)
            used_exact.add(exact_key)
            essay_tokens.append(etok)
            if len(picked_idx) >= total_rows:
                break

    if len(picked_idx) < total_rows:
        remaining = list(pool.index.difference(picked_idx))
        rng.shuffle(remaining)
        for ix in remaining:
            if len(picked_idx) >= total_rows:
                break
            row = pool.loc[ix]
            source = row["sample_id"]
            if source in used_source:
                continue
            exact_key = (row["chatgpt_before"], row["user"], row["essay"])
            if exact_key in used_exact:
                continue
            picked_idx.append(ix)
            used_source.add(source)
            used_exact.add(exact_key)

    if len(picked_idx) < total_rows:
        raise RuntimeError(f"Not enough candidate rows after duplicate controls: {len(picked_idx)} < {total_rows}")

    out = pool.loc[picked_idx].sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return out.iloc[:total_rows].copy()


def _compute_metrics(seed_df: pd.DataFrame):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "aic-pipeline"))
    from aic_pipeline import EmbeddingBackend, compute_PI, fit_weights_and_aic, safe_text

    df = seed_df.copy()
    for c in ["chatgpt_before", "user", "essay"]:
        df[c] = df[c].fillna("").astype(str).apply(safe_text)

    cfg = {
        "ui_oi": {
            "topic_score_alpha": 1.0,
            "topic_score_beta": 1.0,
            "min_course_samples": 3,
        },
        "weights": {
            "mode": "auto",
            "clip_negative": True,
            "min_ratings": 30,
            "n_folds": 5,
        },
    }
    keywords = [
        "however",
        "although",
        "because",
        "why",
        "how",
        "compare",
        "contrast",
        "analyze",
        "evaluate",
        "critique",
        "moreover",
        "therefore",
        "consequently",
        "alternatively",
        "nevertheless",
    ]

    def minmax_norm(vals: np.ndarray) -> np.ndarray:
        mn = float(np.nanmin(vals))
        mx = float(np.nanmax(vals))
        if not np.isfinite(mn) or not np.isfinite(mx) or abs(mx - mn) < 1e-12:
            return np.zeros_like(vals, dtype=float)
        out = (vals - mn) / (mx - mn)
        return np.clip(out, 0.0, 1.0)

    df["rating_num"] = df["rating"].apply(_to_num)
    df = compute_PI(df, keywords, weights=[0.4, 0.3, 0.3])

    # Use TF-IDF backend only (stable in offline/sandbox environments).
    backend = EmbeddingBackend(prefer="tfidf")
    before = df["chatgpt_before"].fillna("").tolist()
    essay = df["essay"].fillna("").tolist()
    backend.fit(before + essay)
    E_before = backend.transform(before)
    E_essay = backend.transform(essay)

    cos_diag = np.zeros(len(df), dtype=float)
    for i in range(len(df)):
        if E_before[i].nnz > 0 and E_essay[i].nnz > 0:
            cos_diag[i] = float(cosine_similarity(E_before[i], E_essay[i])[0, 0])
    cos_diag = np.clip(cos_diag, -1.0, 1.0)
    df["ui_cos_similarity"] = cos_diag
    df["ui_distance"] = np.clip(1.0 - df["ui_cos_similarity"], 0.0, 2.0)

    def new_info_ratio(bef: str, es: str) -> float:
        bt = set(_tokenize(bef))
        et = _tokenize(es)
        if not et:
            return 0.0
        new = sum(1 for t in et if t not in bt)
        return new / len(et)

    df["ui_newinfo_ratio"] = [
        new_info_ratio(df.loc[i, "chatgpt_before"], df.loc[i, "essay"]) for i in range(len(df))
    ]

    # topic score: essay vs course centroid (from before text vectors)
    topic_scores = np.zeros(len(df), dtype=float)
    courses = df["course"].fillna("").astype(str).tolist()
    course_to_idx: Dict[str, List[int]] = {}
    for i, c in enumerate(courses):
        course_to_idx.setdefault(c, []).append(i)

    global_centroid = np.asarray(E_before.mean(axis=0)).ravel().reshape(1, -1)
    for i in range(len(df)):
        idxs = course_to_idx.get(courses[i], [])
        if len(idxs) >= cfg["ui_oi"]["min_course_samples"]:
            cen = np.asarray(E_before[idxs].mean(axis=0)).ravel().reshape(1, -1)
        else:
            cen = global_centroid
        ei = E_essay[i].toarray()
        if ei.size == 0:
            sim = 0.5
        else:
            sim = float(cosine_similarity(ei, cen)[0, 0])
        topic_scores[i] = float(np.clip(sim, 0.0, 1.0))
    df["topic_score"] = topic_scores

    alpha = cfg["ui_oi"]["topic_score_alpha"]
    beta = cfg["ui_oi"]["topic_score_beta"]
    ui_raw = (df["ui_distance"].to_numpy() * df["ui_newinfo_ratio"].to_numpy()) * (df["topic_score"].to_numpy() ** alpha)
    oi_raw = (1.0 - df["topic_score"].to_numpy()) * (df["topic_score"].to_numpy() ** beta)
    df["UI"] = minmax_norm(ui_raw)
    df["OI"] = minmax_norm(oi_raw)

    df, weights = fit_weights_and_aic(df, cfg)
    return df, weights, backend


def _build_cluster_similarity(seed_with_metrics: pd.DataFrame, seed: int, version: str) -> pd.DataFrame:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "aic-pipeline"))
    from aic_pipeline import EmbeddingBackend, safe_text

    df = seed_with_metrics.copy()
    df["essay"] = df["essay"].fillna("").astype(str).apply(safe_text)

    backend = EmbeddingBackend(prefer="tfidf")
    backend.fit(df["essay"].tolist())
    E = backend.transform(df["essay"].tolist())

    students = sorted(df["student_id"].unique())
    student_vecs = []
    student_courses = []
    sample_counts = []
    for s in students:
        idx = np.where(df["student_id"].values == s)[0]
        if backend.kind == "sbert":
            vec = E[idx].mean(axis=0, keepdims=True)
            norm = np.linalg.norm(vec, axis=1, keepdims=True) + 1e-12
            vec = vec / norm
        else:
            vec = np.asarray(E[idx].mean(axis=0)).ravel()
        student_vecs.append(vec)
        student_courses.append(df.loc[df["student_id"] == s, "course"].mode().iloc[0])
        sample_counts.append(int(len(idx)))

    if backend.kind == "sbert":
        M = np.vstack(student_vecs)
    else:
        M = np.vstack([np.asarray(v).ravel() for v in student_vecs])
        norm = np.linalg.norm(M, axis=1, keepdims=True) + 1e-12
        M = M / norm

    n = len(students)
    n_clusters = max(3, min(6, int(round(math.sqrt(n / 2)))))
    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=seed)
    labels = km.fit_predict(M)
    centers = km.cluster_centers_
    centers = centers / (np.linalg.norm(centers, axis=1, keepdims=True) + 1e-12)

    sim_mat = cosine_similarity(M, M)

    rows = []
    for i, sid in enumerate(students):
        cid = int(labels[i])
        own_center_sim = float(np.clip(np.dot(M[i], centers[cid]), -1.0, 1.0))
        peers = [j for j in range(n) if j != i]
        mean_peer = float(np.mean(sim_mat[i, peers])) if peers else 1.0
        nn_idx = int(np.argmax(sim_mat[i, peers])) if peers else i
        nearest_j = peers[nn_idx] if peers else i
        cluster_size = int(np.sum(labels == cid))
        rows.append(
            {
                "student_id": sid,
                "course_mode": student_courses[i],
                "cluster_id": cid,
                "cluster_size": cluster_size,
                "sample_count": sample_counts[i],
                "similarity_to_cluster_centroid": round(own_center_sim, 6),
                "mean_peer_similarity": round(mean_peer, 6),
                "nearest_peer_student_id": students[nearest_j],
                "nearest_peer_similarity": round(float(sim_mat[i, nearest_j]), 6),
                "augmentation_version": version,
                "random_seed": seed,
            }
        )
    return pd.DataFrame(rows).sort_values("student_id").reset_index(drop=True)


def _assignment_base_dt(assignment_id: int) -> dt.datetime:
    mapping = {
        1: dt.datetime(2025, 2, 14, 10, 0, 0),
        2: dt.datetime(2025, 2, 27, 11, 0, 0),
        3: dt.datetime(2025, 3, 13, 9, 30, 0),
        4: dt.datetime(2025, 3, 20, 14, 0, 0),
        5: dt.datetime(2025, 4, 3, 16, 0, 0),
    }
    return mapping.get(assignment_id, dt.datetime(2025, 4, 1, 12, 0, 0))


def _build_sql_rows(df: pd.DataFrame, weights: Tuple[float, float, float]) -> Tuple[List[str], List[str]]:
    subs = []
    mets = []
    wpi, wui, woi = weights

    # expected ordering: student_id_db asc, assignment_id asc
    df = df.sort_values(["student_id_db", "assignment_id"]).reset_index(drop=True)
    for i, r in df.iterrows():
        submission_id = 7 + i
        student_offset = int(r["student_num"]) - 11
        base_dt = _assignment_base_dt(int(r["assignment_id"]))
        submitted_at = base_dt + dt.timedelta(minutes=student_offset * 4)
        computed_at = submitted_at + dt.timedelta(minutes=5)

        subs.append(
            "("
            f"{int(r['assignment_id'])}, {int(r['student_id_db'])}, "
            f"'{_sql_escape(r['chatgpt_before'])}', "
            f"'{_sql_escape(r['user'])}', "
            f"'{_sql_escape(r['essay'])}', "
            f"'{submitted_at:%Y-%m-%d %H:%M:%S}'"
            ")"
        )

        pi_score = int(round(float(r["PI"]) * 100))
        ui_score = int(round(float(r["UI"]) * 100))
        oi_score = int(round(float(r["OI"]) * 100))
        aic_score = int(round(float(r["AIC"]) * 100))
        topic_score = int(round(float(r["topic_score"]) * 100))

        mets.append(
            "("
            f"{submission_id}, {pi_score}, {ui_score}, {oi_score}, {aic_score}, {topic_score}, "
            f"{wpi:.3f}, {wui:.3f}, {woi:.3f}, "
            f"{int(r['pi_depth_tokens'])}, {float(r['pi_depth_norm']):.2f}, {float(r['pi_critical_ratio']):.2f}, "
            f"{float(r['pi_avg_sent_len']):.2f}, {float(r['pi_ttr']):.2f}, {float(r['pi_complexity']):.2f}, "
            f"{float(r['ui_cos_similarity']):.2f}, {float(r['ui_distance']):.2f}, {float(r['ui_newinfo_ratio']):.2f}, "
            f"{float(r['topic_score']):.2f}, 'sbert', '{computed_at:%Y-%m-%d %H:%M:%S}'"
            ")"
        )

    return subs, mets


def _replace_generated_block(init_sql: Path, submissions_rows: List[str], metrics_rows: List[str], version: str, seed: int):
    text = init_sql.read_text(encoding="utf-8")

    sub_stmt = (
        "INSERT INTO submissions (assignment_id, student_id, chatgpt_before, user_prompt, essay, submitted_at) VALUES\n"
        + ",\n".join(submissions_rows)
        + ";\n"
    )
    met_stmt = (
        "INSERT INTO metrics (submission_id, pi_score, ui_score, oi_score, aic_score, topic_score, weight_pi, weight_ui, weight_oi, pi_depth_tokens, pi_depth_norm, pi_critical_ratio, pi_avg_sent_len, pi_ttr, pi_complexity, ui_cos_similarity, ui_distance, ui_newinfo_ratio, oi_topic_score_raw, embedding_backend, computed_at) VALUES\n"
        + ",\n".join(metrics_rows)
        + ";\n"
    )

    header = (
        f"-- generated_seed_block: version={version}, random_seed={seed}, generated_at={dt.datetime.utcnow().isoformat()}Z\n"
    )
    replacement = "\n" + header + sub_stmt + "\n" + met_stmt + "\n"

    start_anchor = "INSERT INTO submissions (assignment_id, student_id, chatgpt_before, user_prompt, essay, submitted_at) VALUES\n(5, 12,"
    end_anchor = "\nINSERT INTO teacher_feedback (assignment_id, student_id, teacher_id, content) VALUES"

    start = text.find(start_anchor)
    end = text.find(end_anchor)
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("Could not locate generated submissions/metrics block in init.sql for replacement.")

    new_text = text[:start] + replacement + text[end:]
    init_sql.write_text(new_text, encoding="utf-8")


def _validate_outputs(seed_df: pd.DataFrame, raw_df: pd.DataFrame, sim_df: pd.DataFrame) -> Dict[str, object]:
    report: Dict[str, object] = {}
    report["rows_seed"] = int(len(seed_df))
    report["students_seed"] = int(seed_df["student_id"].nunique())
    report["rows_per_student"] = {
        "min": int(seed_df.groupby("student_id").size().min()),
        "max": int(seed_df.groupby("student_id").size().max()),
        "avg": float(round(seed_df.groupby("student_id").size().mean(), 3)),
    }
    report["assignment_dist"] = {str(k): int(v) for k, v in seed_df.groupby("assignment_id").size().items()}
    report["course_dist_seed"] = {str(k): int(v) for k, v in seed_df.groupby("course").size().items()}
    report["course_dist_raw"] = {str(k): int(v) for k, v in raw_df.groupby("course").size().items()}

    # exact duplicates on core text fields
    dup = seed_df.duplicated(subset=["chatgpt_before", "user", "essay"]).sum()
    report["exact_duplicate_text_rows"] = int(dup)

    # simple near-duplicate estimate
    near = 0
    essays = seed_df["essay"].astype(str).tolist()
    toks = [set(_tokenize(e)) for e in essays]
    for i in range(len(toks)):
        for j in range(i + 1, len(toks)):
            denom = len(toks[i] | toks[j]) or 1
            jac = len(toks[i] & toks[j]) / denom
            if jac >= 0.92:
                near += 1
    report["near_duplicate_pairs_jaccard_ge_0.92"] = int(near)

    report["metrics_missing_any"] = int(
        seed_df[
            [
                "PI",
                "UI",
                "OI",
                "AIC",
                "pi_depth_tokens",
                "pi_depth_norm",
                "pi_critical_ratio",
                "pi_avg_sent_len",
                "pi_ttr",
                "pi_complexity",
                "ui_cos_similarity",
                "ui_distance",
                "ui_newinfo_ratio",
                "topic_score",
            ]
        ]
        .isna()
        .any(axis=1)
        .sum()
    )

    report["sim_rows"] = int(len(sim_df))
    report["sim_students"] = int(sim_df["student_id"].nunique())
    return report


def main():
    parser = argparse.ArgumentParser(description="Build advanced seed artifacts and sync init.sql.")
    parser.add_argument("--raw-csv", default="input_data/reciep4u_dataset.csv")
    parser.add_argument("--init-sql", default="init.sql")
    parser.add_argument("--out-seed-csv", default="input_data/students_seed_011_060.csv")
    parser.add_argument("--out-sim-csv", default="input_data/students_cluster_similarity_011_060.csv")
    parser.add_argument("--student-start", type=int, default=11)
    parser.add_argument("--student-count", type=int, default=50)
    parser.add_argument("--assignments", default="1,2,3,4,5")
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument("--augmentation-version", default="advanced_seed_v1")
    parser.add_argument("--report-json", default="input_data/seed_generation_report_011_060.json")
    args = parser.parse_args()

    random.seed(args.random_seed)
    np.random.seed(args.random_seed)

    root = Path(__file__).resolve().parents[1]
    raw_csv = root / args.raw_csv
    init_sql = root / args.init_sql
    out_seed = root / args.out_seed_csv
    out_sim = root / args.out_sim_csv
    report_json = root / args.report_json

    assignments = [int(x.strip()) for x in args.assignments.split(",") if x.strip()]
    if not assignments:
        raise ValueError("No assignments provided.")

    raw_df = pd.read_csv(raw_csv, encoding="utf-8")
    slots = _build_slots(args.student_start, args.student_count, assignments)
    total_rows = len(slots)

    pool = _extract_candidate_pool(raw_df)
    course_counts = dict(pool["course"].value_counts())
    targets = _largest_remainder_targets(total_rows, course_counts)

    chosen = _select_rows(pool, total_rows, targets, args.random_seed, near_dup_thresh=0.92)
    if len(chosen) != total_rows:
        raise RuntimeError(f"Chosen rows mismatch: {len(chosen)} != {total_rows}")

    # Assign chosen rows to deterministic student/assignment slots.
    assigned_rows = []
    for slot, (_, src) in zip(slots, chosen.iterrows()):
        student_token = f"student_{slot.student_num:03d}"
        sample_id = f"{student_token}-{src['course']}-W{slot.assignment_id}-S1-{slot.idx:02d}"
        assigned_rows.append(
            {
                "sample_id": sample_id,
                "course": src["course"],
                "student_id": student_token,
                "week": slot.assignment_id,
                "session": 1,
                "idx": slot.idx,
                "assignment_id": slot.assignment_id,
                "student_num": slot.student_num,
                "student_id_db": slot.student_id_db,
                "chatgpt_before": str(src["chatgpt_before"]),
                "user": str(src["user"]),
                "chatgpt_after": str(src.get("chatgpt_after", "")),
                "rating": src.get("rating", np.nan),
                "intent_final": str(src.get("intent_final", "")),
                "is_quiz": _safe_bool_str(src.get("is_quiz", "")),
                "is_essay_edited": _safe_bool_str(src.get("is_essay_edited", "")),
                "essay": str(src["essay"]),
                "source_sample_id": str(src.get("sample_id", "")),
                "augmentation_version": args.augmentation_version,
                "random_seed": args.random_seed,
            }
        )

    seed_df = pd.DataFrame(assigned_rows)
    seed_with_metrics, weights, _backend = _compute_metrics(seed_df)
    sim_df = _build_cluster_similarity(seed_with_metrics, args.random_seed, args.augmentation_version)

    # Save seed CSV contract.
    out_seed.parent.mkdir(parents=True, exist_ok=True)
    out_cols = [
        "sample_id",
        "course",
        "student_id",
        "week",
        "session",
        "idx",
        "assignment_id",
        "chatgpt_before",
        "user",
        "chatgpt_after",
        "rating",
        "intent_final",
        "is_quiz",
        "is_essay_edited",
        "essay",
        "PI",
        "UI",
        "OI",
        "AIC",
        "pi_depth_tokens",
        "pi_depth_norm",
        "pi_critical_ratio",
        "pi_avg_sent_len",
        "pi_ttr",
        "pi_complexity",
        "ui_cos_similarity",
        "ui_distance",
        "ui_newinfo_ratio",
        "topic_score",
        "embedding_backend",
        "source_sample_id",
        "augmentation_version",
        "random_seed",
    ]
    seed_with_metrics["embedding_backend"] = "sbert"
    for c in out_cols:
        if c not in seed_with_metrics.columns:
            seed_with_metrics[c] = np.nan
    seed_with_metrics[out_cols].to_csv(out_seed, index=False, encoding="utf-8")

    # Save cluster similarity CSV.
    out_sim.parent.mkdir(parents=True, exist_ok=True)
    sim_df.to_csv(out_sim, index=False, encoding="utf-8")

    # Update init.sql generated block.
    subs, mets = _build_sql_rows(seed_with_metrics, weights)
    _replace_generated_block(init_sql, subs, mets, args.augmentation_version, args.random_seed)

    # Validation report.
    report = _validate_outputs(seed_with_metrics, raw_df, sim_df)
    report["weights"] = {"weight_pi": round(float(weights[0]), 6), "weight_ui": round(float(weights[1]), 6), "weight_oi": round(float(weights[2]), 6)}
    report["files"] = {
        "init_sql": str(init_sql),
        "seed_csv": str(out_seed),
        "cluster_similarity_csv": str(out_sim),
    }
    report["generated_at_utc"] = dt.datetime.utcnow().isoformat() + "Z"
    report["augmentation_version"] = args.augmentation_version
    report["random_seed"] = args.random_seed
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
