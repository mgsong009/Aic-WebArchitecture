from fastapi import HTTPException
from sqlalchemy import desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import (
    AnalysisJob,
    AnalysisRun,
    Assignment,
    Class,
    ClassEnrollment,
    Metric,
    Submission,
    TeacherFeedback,
    User,
)
from app.services.job_service import create_and_dispatch_job


async def get_admin_dashboard_stats(db: AsyncSession) -> dict:
    # Users by role
    user_rows = (await db.execute(
        select(User.role, func.count(User.id).label("cnt")).group_by(User.role)
    )).all()
    role_map = {r: c for r, c in user_rows}

    # Classes
    class_count = (await db.execute(select(func.count(Class.id)))).scalar_one()
    enrollment_count = (await db.execute(select(func.count(ClassEnrollment.id)))).scalar_one()
    avg_students_per_class = round(enrollment_count / class_count, 1) if class_count else 0.0

    # Assignments and submissions
    assignment_count = (await db.execute(select(func.count(Assignment.id)))).scalar_one()
    submission_count = (await db.execute(select(func.count(Submission.id)))).scalar_one()
    analyzed_count = (await db.execute(
        select(func.count(Metric.id)).where(Metric.aic_score.isnot(None))
    )).scalar_one()
    submission_rate = round(submission_count / enrollment_count * 100, 1) if enrollment_count else 0.0
    analysis_rate = round(analyzed_count / submission_count * 100, 1) if submission_count else 0.0

    # Analysis job status counts
    job_rows = (await db.execute(
        select(AnalysisJob.status, func.count(AnalysisJob.id).label("cnt")).group_by(AnalysisJob.status)
    )).all()
    job_map = {s: c for s, c in job_rows}
    done = job_map.get("done", 0)
    failed = job_map.get("failed", 0)
    total_finished = done + failed
    completion_rate = round(done / total_finished * 100, 1) if total_finished else 0.0

    # Score averages
    score_row = (await db.execute(
        select(
            func.round(func.avg(Metric.aic_score), 1),
            func.round(func.avg(Metric.pi_score), 1),
            func.round(func.avg(Metric.ui_score), 1),
            func.round(func.avg(Metric.oi_score), 1),
        ).where(Metric.aic_score.isnot(None))
    )).one()

    # Feedback count
    feedback_count = (await db.execute(select(func.count(TeacherFeedback.id)))).scalar_one()

    return {
        "users": {
            "total": sum(role_map.values()),
            "students": role_map.get("student", 0),
            "teachers": role_map.get("teacher", 0),
            "admins": role_map.get("admin", 0),
        },
        "classes": {
            "total": class_count,
            "avg_students_per_class": avg_students_per_class,
        },
        "submissions": {
            "total": submission_count,
            "analyzed": analyzed_count,
            "submission_rate": submission_rate,
            "analysis_rate": analysis_rate,
        },
        "jobs": {
            "pending": job_map.get("pending", 0),
            "running": job_map.get("running", 0),
            "done": done,
            "failed": failed,
            "completion_rate": completion_rate,
        },
        "scores": {
            "avg_aic": score_row[0],
            "avg_pi": score_row[1],
            "avg_ui": score_row[2],
            "avg_oi": score_row[3],
        },
        "feedback": {
            "total": feedback_count,
        },
    }


async def get_latest_analysis_run(db: AsyncSession) -> dict:
    run = (await db.execute(
        select(AnalysisRun).order_by(desc(AnalysisRun.created_at), desc(AnalysisRun.id)).limit(1)
    )).scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="No analysis run data is available")
    return _serialize_analysis_run(run)


async def get_analysis_run_quality(db: AsyncSession, run_id: str) -> dict:
    run = await _get_analysis_run(db, run_id)
    return {
        "runId": run.run_id,
        "status": run.status,
        "successRate": run.success_rate,
        "dataHealth": run.data_health or {},
        "backend": run.backend_info or {},
        "readiness": run.readiness or {},
    }


async def get_analysis_run_pipeline_steps(db: AsyncSession, run_id: str) -> dict:
    run = await _get_analysis_run(db, run_id)
    return {
        "runId": run.run_id,
        "pipelineSteps": run.pipeline_steps or [],
    }


async def get_analysis_run_runtime(db: AsyncSession, run_id: str) -> dict:
    run = await _get_analysis_run(db, run_id)
    return {
        "runId": run.run_id,
        "totalRuntimeSec": run.total_runtime_sec,
        "avgRuntimePerSample": run.avg_runtime_per_sample,
        "pipelineSteps": run.pipeline_steps or [],
    }


async def reprocess_analysis_run(db: AsyncSession, run_id: str) -> dict:
    run = await _get_analysis_run(db, run_id)
    if not run.submission_id:
        raise HTTPException(status_code=409, detail="Run is not linked to a submission")

    job_id = await create_and_dispatch_job(run.submission_id, db)
    return {
        "ok": True,
        "previousRunId": run.run_id,
        "jobId": job_id,
    }


async def _get_analysis_run(db: AsyncSession, run_id: str) -> AnalysisRun:
    run = (await db.execute(
        select(AnalysisRun).where(AnalysisRun.run_id == run_id)
    )).scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail=f"Analysis run {run_id} was not found")
    return run


def _serialize_analysis_run(run: AnalysisRun) -> dict:
    return {
        "runId": run.run_id,
        "course": run.course,
        "assignment": run.assignment,
        "status": run.status,
        "processedRows": run.processed_rows,
        "validRows": run.valid_rows,
        "successRate": _round_number(run.success_rate, 1),
        "totalRuntimeSec": _round_number(run.total_runtime_sec, 3),
        "avgRuntimePerSample": _round_number(run.avg_runtime_per_sample, 3),
        "dataHealth": run.data_health or {},
        "backend": run.backend_info or {},
        "pipelineSteps": run.pipeline_steps or [],
        "readiness": run.readiness or {},
        "errorMessage": run.error_message,
        "createdAt": run.created_at,
        "completedAt": run.completed_at,
    }


def _round_number(value, digits: int):
    return round(value, digits) if value is not None else 0
