from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import require_role
from app.models.db_models import Assignment, Submission, ClassEnrollment
from app.schemas.submission import SubmissionCreate, SubmissionCreated
from app.services.job_service import create_and_dispatch_job

router = APIRouter()
student_only = require_role("student")


@router.post("/submissions", response_model=SubmissionCreated, status_code=status.HTTP_202_ACCEPTED)
async def create_submission(
    body: SubmissionCreate,
    user: dict = Depends(student_only),
    db: AsyncSession = Depends(get_db),
):
    asgn_result = await db.execute(select(Assignment).where(Assignment.id == body.assignment_id))
    assignment = asgn_result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    enroll_result = await db.execute(
        select(ClassEnrollment.id).where(
            ClassEnrollment.student_id == user["id"],
            ClassEnrollment.class_id == assignment.class_id,
        )
    )
    if not enroll_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Upsert submission (one per student per assignment)
    existing = await db.execute(
        select(Submission).where(
            Submission.assignment_id == body.assignment_id,
            Submission.student_id == user["id"],
        )
    )
    sub = existing.scalar_one_or_none()
    if sub:
        sub.chatgpt_before = body.chatgpt_before
        sub.user_prompt = body.user_prompt
        sub.essay = body.essay
    else:
        sub = Submission(
            assignment_id=body.assignment_id,
            student_id=user["id"],
            chatgpt_before=body.chatgpt_before,
            user_prompt=body.user_prompt,
            essay=body.essay,
        )
        db.add(sub)

    await db.commit()
    await db.refresh(sub)

    job_uuid = await create_and_dispatch_job(sub.id, db)
    return SubmissionCreated(submission_id=sub.id, job_id=job_uuid, status="pending")
