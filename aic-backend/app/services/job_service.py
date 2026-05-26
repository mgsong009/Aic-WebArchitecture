import uuid
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select, update
from app.database import AsyncSessionLocal
from app.models.db_models import AnalysisJob, Metric, Submission, Assignment, User
from app.services.pipeline_client import call_pipeline


async def create_and_dispatch_job(submission_id: int, db) -> str:
    job_uuid_str = str(uuid.uuid4())

    submission_data = await _build_submission_payload(db, submission_id)

    # Create job record
    job = AnalysisJob(job_uuid=job_uuid_str, submission_id=submission_id, status="pending")
    db.add(job)
    await db.commit()

    # Fire background task without awaiting
    asyncio.create_task(_run_pipeline(job_uuid_str, submission_id, submission_data))
    return job_uuid_str


async def recover_incomplete_jobs():
    """
    Recover jobs that were interrupted by process restart.
    pending/running -> pending, then re-dispatch.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AnalysisJob).where(AnalysisJob.status.in_(("pending", "running")))
        )
        jobs = list(result.scalars().all())
        if not jobs:
            return

        for job in jobs:
            job.status = "pending"
            job.error_message = None
            job.started_at = None
            job.completed_at = None
        await session.commit()

        for job in jobs:
            try:
                payload = await _build_submission_payload(session, job.submission_id)
            except Exception as exc:
                await session.execute(
                    update(AnalysisJob)
                    .where(AnalysisJob.id == job.id)
                    .values(
                        status="failed",
                        error_message=f"Recovery failed: {exc}",
                        completed_at=datetime.now(timezone.utc),
                    )
                )
                await session.commit()
                continue

            asyncio.create_task(_run_pipeline(job.job_uuid, job.submission_id, payload))


async def _build_submission_payload(db, submission_id: int) -> dict:
    sub_result = await db.execute(
        select(Submission, Assignment, User)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .join(User, Submission.student_id == User.id)
        .where(Submission.id == submission_id)
    )
    row = sub_result.first()
    if not row:
        raise ValueError(f"Submission {submission_id} not found")

    sub, assignment, student = row
    return {
        "submission_id": submission_id,
        "course_code": assignment.course_code or "default",
        "user_id_str": student.user_id_str,
        "chatgpt_before": sub.chatgpt_before,
        "user_prompt": sub.user_prompt,
        "essay": sub.essay,
    }


async def _run_pipeline(job_uuid_str: str, submission_id: int, submission_data: dict):
    async with AsyncSessionLocal() as session:
        # Mark as running
        await session.execute(
            update(AnalysisJob)
            .where(AnalysisJob.job_uuid == job_uuid_str)
            .values(status="running", started_at=datetime.now(timezone.utc))
        )
        await session.commit()

        try:
            result = await call_pipeline(job_uuid_str, submission_data)
            scaled = _scale_metrics(result)

            # Upsert metrics
            existing = await session.execute(
                select(Metric).where(Metric.submission_id == submission_id)
            )
            metric = existing.scalar_one_or_none()
            if metric:
                for k, v in scaled.items():
                    setattr(metric, k, v)
            else:
                metric = Metric(submission_id=submission_id, **scaled)
                session.add(metric)

            await session.execute(
                update(AnalysisJob)
                .where(AnalysisJob.job_uuid == job_uuid_str)
                .values(status="done", completed_at=datetime.now(timezone.utc))
            )
            await session.commit()

        except Exception as exc:
            await session.execute(
                update(AnalysisJob)
                .where(AnalysisJob.job_uuid == job_uuid_str)
                .values(status="failed", error_message=str(exc), completed_at=datetime.now(timezone.utc))
            )
            await session.commit()


def _scale_metrics(result: dict) -> dict:
    return {
        "pi_score": _safe_round(result.get("pi")),
        "ui_score": _safe_round(result.get("ui")),
        "oi_score": _safe_round(result.get("oi")),
        "aic_score": _safe_round(result.get("aic")),
        "topic_score": _safe_round(result.get("topic_score")),
        "weight_pi": result.get("weight_pi"),
        "weight_ui": result.get("weight_ui"),
        "weight_oi": result.get("weight_oi"),
        "pi_depth_tokens": result.get("pi_depth_tokens"),
        "pi_depth_norm": result.get("pi_depth_norm"),
        "pi_critical_ratio": result.get("pi_critical_ratio"),
        "pi_avg_sent_len": result.get("pi_avg_sent_len"),
        "pi_ttr": result.get("pi_ttr"),
        "pi_complexity": result.get("pi_complexity"),
        "ui_cos_similarity": result.get("ui_cos_similarity"),
        "ui_distance": result.get("ui_distance"),
        "ui_newinfo_ratio": result.get("ui_newinfo_ratio"),
        "oi_topic_score_raw": result.get("oi_topic_score_raw"),
        "embedding_backend": result.get("embedding_backend"),
        "computed_at": datetime.now(timezone.utc),
    }


def _safe_round(value) -> int:
    if value is None:
        return None
    return round(float(value) * 100)
