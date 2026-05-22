from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.db_models import AnalysisJob, Metric, Submission, Assignment
from app.schemas.submission import JobStatus, MetricsSummary
from app.services import teacher_service as teacher_svc

router = APIRouter()


@router.get("/jobs/{job_uuid}/status", response_model=JobStatus)
async def job_status(
    job_uuid: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AnalysisJob, Submission.student_id, Assignment.class_id)
        .join(Submission, AnalysisJob.submission_id == Submission.id)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .where(AnalysisJob.job_uuid == job_uuid)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    job, submission_owner_id, class_id = row

    if user.get("role") == "student":
        if submission_owner_id != user["id"]:
            raise HTTPException(status_code=404, detail="Job not found")
    elif user.get("role") == "teacher":
        teacher_cls = await teacher_svc.get_teacher_class(user["id"], db)
        if not teacher_cls or teacher_cls.id != class_id:
            raise HTTPException(status_code=404, detail="Job not found")
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

    metrics = None
    if job.status == "done":
        m_result = await db.execute(select(Metric).where(Metric.submission_id == job.submission_id))
        m = m_result.scalar_one_or_none()
        if m:
            metrics = MetricsSummary(
                aic=m.aic_score, pi=m.pi_score, ui=m.ui_score, oi=m.oi_score, topic=m.topic_score
            )

    return JobStatus(
        job_id=job_uuid,
        status=job.status,
        metrics=metrics,
        error=job.error_message,
    )
