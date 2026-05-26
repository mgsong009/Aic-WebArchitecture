import argparse
import asyncio
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "aic-backend"))

from app.database import AsyncSessionLocal  # noqa: E402
from app.models.db_models import AnalysisJob, AnalysisRunMetadata, Assignment, Submission, User  # noqa: E402
from app.services.pipeline_client import DEFAULT_KEYWORDS  # noqa: E402


async def main():
    args = parse_args()
    async with AsyncSessionLocal() as session:
        payload = await build_payload(session, args.submission_id)
        result, elapsed_ms = await run_pipeline(args.pipeline_url, payload)
        await record_baseline(session, args.submission_id, args.baseline_version, result, elapsed_ms)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Record measured pre-optimization AIC pipeline metadata without storing submission text."
    )
    parser.add_argument("--submission-id", type=int, required=True)
    parser.add_argument("--pipeline-url", required=True, help="Base URL for the pre-optimization pipeline runner.")
    parser.add_argument("--baseline-version", default="3e07857-pre-optimization")
    return parser.parse_args()


async def build_payload(session, submission_id: int) -> dict:
    result = await session.execute(
        select(Submission, Assignment, User)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .join(User, Submission.student_id == User.id)
        .where(Submission.id == submission_id)
    )
    row = result.first()
    if not row:
        raise ValueError(f"Submission {submission_id} not found")

    submission, assignment, student = row
    return {
        "job_id": f"baseline-{submission_id}",
        "submission": {
            "sample_id": f"sub-{submission_id}",
            "course": assignment.course_code or "default",
            "student_id": student.user_id_str,
            "chatgpt_before": submission.chatgpt_before,
            "user": submission.user_prompt,
            "essay": submission.essay,
        },
        "config": {
            "pi_weights": [0.4, 0.3, 0.3],
            "critical_keywords": DEFAULT_KEYWORDS,
            "topic_score_alpha": 1.0,
            "topic_score_beta": 1.0,
            "backend_prefer": "sbert",
        },
    }


async def run_pipeline(pipeline_url: str, payload: dict) -> tuple[dict, float]:
    started = time.perf_counter()
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{pipeline_url.rstrip('/')}/analyze-baseline", json=payload)
        response.raise_for_status()
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    return response.json(), elapsed_ms


async def record_baseline(session, submission_id: int, baseline_version: str, result: dict, elapsed_ms: float):
    job_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"aic-analysis-baseline:{submission_id}:{baseline_version}"))
    now = datetime.now(timezone.utc)
    metadata = result.get("analysis_metadata") or {}
    baseline_scores = {
        "pi": _float_score(result.get("pi")),
        "ui": _float_score(result.get("ui")),
        "oi": _float_score(result.get("oi")),
        "aic": _float_score(result.get("aic")),
    }

    job = await _get_or_create_job(session, job_uuid, submission_id)
    job.status = "done"
    job.error_message = None
    job.started_at = now
    job.completed_at = now

    run_metadata = await _get_or_create_metadata(session, job)
    run_metadata.metric_version = metadata.get("metric_version")
    run_metadata.baseline_version = None
    run_metadata.optimized_version = baseline_version
    run_metadata.processed_count = metadata.get("processed_count") or 1
    run_metadata.total_runtime_ms = metadata.get("total_runtime_ms") or elapsed_ms
    run_metadata.baseline_runtime_ms = None
    run_metadata.runtime_delta_pct = None
    run_metadata.memory_peak_kb = metadata.get("memory_peak_kb")
    run_metadata.baseline_memory_peak_kb = None
    run_metadata.memory_delta_pct = None
    run_metadata.baseline_scores = baseline_scores
    run_metadata.stage_runtimes_ms = metadata.get("stage_runtimes_ms")
    run_metadata.score_deltas = None
    run_metadata.quality_passed = None
    run_metadata.bootstrap_passed = metadata.get("bootstrap_passed")
    run_metadata.measured_at = now

    await session.commit()
    print(f"Recorded baseline {baseline_version} for submission {submission_id} as job {job_uuid}")


async def _get_or_create_job(session, job_uuid: str, submission_id: int) -> AnalysisJob:
    result = await session.execute(select(AnalysisJob).where(AnalysisJob.job_uuid == job_uuid))
    job = result.scalar_one_or_none()
    if job:
        return job
    job = AnalysisJob(job_uuid=job_uuid, submission_id=submission_id, status="pending")
    session.add(job)
    await session.flush()
    return job


async def _get_or_create_metadata(session, job: AnalysisJob) -> AnalysisRunMetadata:
    result = await session.execute(select(AnalysisRunMetadata).where(AnalysisRunMetadata.job_id == job.id))
    metadata = result.scalar_one_or_none()
    if metadata:
        return metadata
    metadata = AnalysisRunMetadata(job_id=job.id)
    session.add(metadata)
    return metadata


def _float_score(value) -> float:
    if value is None:
        raise ValueError("Pipeline response is missing a required baseline score")
    return round(float(value), 6)


if __name__ == "__main__":
    asyncio.run(main())
