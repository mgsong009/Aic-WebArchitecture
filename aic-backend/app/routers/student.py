from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import require_role
from app.models.db_models import User, Assignment, Submission, Metric, TeacherFeedback
from app.services import student_service as svc

router = APIRouter()
student_only = require_role("student")


@router.get("/dashboard")
async def student_dashboard(user: dict = Depends(student_only), db: AsyncSession = Depends(get_db)):
    cls = await svc.get_student_class(user["id"], db)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    rows = await svc.get_student_submissions_with_metrics(user["id"], cls.id, db)
    class_avgs = await svc.get_class_avg_per_assignment(cls.id, db)

    trend = []
    metrics_history = []
    latest_metrics = {}
    prev_metrics = {}

    for i, (sub, asgn, m) in enumerate(rows):
        label = f"A{i+1}"
        avg_row = class_avgs.get(asgn.id)
        trend.append({
            "assignment_id": asgn.id,
            "label": label,
            "aic": m.aic_score if m else None,
            "class_avg": round(float(avg_row.avg_aic), 1) if avg_row and avg_row.avg_aic else None,
        })
        metrics_history.append({
            "label": label,
            "pi": m.pi_score if m else None,
            "ui": m.ui_score if m else None,
            "oi": m.oi_score if m else None,
        })
        if i == len(rows) - 2 and m:
            prev_metrics = {"aic": m.aic_score, "pi": m.pi_score, "ui": m.ui_score, "oi": m.oi_score}
        if i == len(rows) - 1 and m:
            latest_metrics = {
                "aic": m.aic_score, "pi": m.pi_score, "ui": m.ui_score,
                "oi": m.oi_score, "topic": m.topic_score,
                "weight_pi": m.weight_pi, "weight_ui": m.weight_ui, "weight_oi": m.weight_oi,
                "pi_depth_tokens": m.pi_depth_tokens, "pi_critical_ratio": m.pi_critical_ratio,
                "pi_complexity": m.pi_complexity, "ui_distance": m.ui_distance,
                "ui_newinfo_ratio": m.ui_newinfo_ratio, "embedding_backend": m.embedding_backend,
            }

    delta = {}
    if latest_metrics and prev_metrics:
        for k in ["aic", "pi", "ui", "oi"]:
            lv = latest_metrics.get(k)
            pv = prev_metrics.get(k)
            delta[k] = (lv - pv) if lv is not None and pv is not None else None

    # Class average (latest assignment)
    latest_asgn_id = rows[-1][1].id if rows else None
    class_avg_row = class_avgs.get(latest_asgn_id) if latest_asgn_id else None
    class_avg = {}
    if class_avg_row:
        class_avg = {
            "aic": round(float(class_avg_row.avg_aic), 1) if class_avg_row.avg_aic else None,
            "pi": round(float(class_avg_row.avg_pi), 1) if class_avg_row.avg_pi else None,
            "ui": round(float(class_avg_row.avg_ui), 1) if class_avg_row.avg_ui else None,
            "oi": round(float(class_avg_row.avg_oi), 1) if class_avg_row.avg_oi else None,
        }

    rank, total = (None, 0)
    if latest_asgn_id:
        rank, total = await svc.get_student_rank(user["id"], cls.id, latest_asgn_id, db)

    recent = []
    for sub, asgn, m in reversed(rows[-3:]):
        recent.append({
            "id": asgn.id,
            "title": asgn.title,
            "submitted_at": sub.submitted_at.strftime("%Y-%m-%d") if sub else None,
            "aic": m.aic_score if m else None,
            "status": "done" if m and m.aic_score is not None else "pending",
        })

    return {
        "student": {"id": user["id"], "name": user["name"], "class_code": cls.class_code},
        "latest_metrics": latest_metrics,
        "latest_delta": delta,
        "class_avg": class_avg,
        "rank": rank,
        "total_students": total,
        "trend": trend,
        "recent_assignments": recent,
        "metrics_history": metrics_history,
    }


@router.get("/assignments")
async def student_assignments(user: dict = Depends(student_only), db: AsyncSession = Depends(get_db)):
    cls = await svc.get_student_class(user["id"], db)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    rows = await svc.get_student_submissions_with_metrics(user["id"], cls.id, db)
    assignments = []
    for sub, asgn, m in rows:
        assignments.append({
            "id": asgn.id,
            "title": asgn.title,
            "due_date": asgn.due_date.strftime("%Y-%m-%d") if asgn.due_date else None,
            "submitted_at": sub.submitted_at.strftime("%Y-%m-%d") if sub else None,
            "aic": m.aic_score if m else None,
            "pi": m.pi_score if m else None,
            "ui": m.ui_score if m else None,
            "oi": m.oi_score if m else None,
            "status": "done" if m and m.aic_score is not None else ("pending" if sub else "not_submitted"),
        })
    return {"assignments": assignments}


@router.get("/assignments/{assignment_id}")
async def student_assignment_detail(
    assignment_id: int,
    user: dict = Depends(student_only),
    db: AsyncSession = Depends(get_db),
):
    cls = await svc.get_student_class(user["id"], db)
    asgn_result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    asgn = asgn_result.scalar_one_or_none()
    if not asgn:
        raise HTTPException(status_code=404, detail="Assignment not found")

    sub_result = await db.execute(
        select(Submission).where(
            Submission.assignment_id == assignment_id,
            Submission.student_id == user["id"],
        )
    )
    sub = sub_result.scalar_one_or_none()
    m = None
    if sub:
        m_result = await db.execute(select(Metric).where(Metric.submission_id == sub.id))
        m = m_result.scalar_one_or_none()

    class_avgs = await svc.get_class_avg_per_assignment(asgn.class_id, db) if cls else {}
    avg_row = class_avgs.get(assignment_id)

    return {
        "assignment": {"id": asgn.id, "title": asgn.title, "course_code": asgn.course_code},
        "submission": {
            "id": sub.id,
            "chatgpt_before": sub.chatgpt_before,
            "user_prompt": sub.user_prompt,
            "essay": sub.essay,
        } if sub else None,
        "metrics": {
            "aic": m.aic_score, "pi": m.pi_score, "ui": m.ui_score,
            "oi": m.oi_score, "topic": m.topic_score,
            "weight_pi": m.weight_pi, "weight_ui": m.weight_ui, "weight_oi": m.weight_oi,
            "pi_depth_tokens": m.pi_depth_tokens, "pi_critical_ratio": m.pi_critical_ratio,
            "pi_complexity": m.pi_complexity, "ui_distance": m.ui_distance,
            "ui_newinfo_ratio": m.ui_newinfo_ratio, "embedding_backend": m.embedding_backend,
        } if m else None,
        "class_avg": {
            "aic": round(float(avg_row.avg_aic), 1) if avg_row and avg_row.avg_aic else None,
            "pi": round(float(avg_row.avg_pi), 1) if avg_row and avg_row.avg_pi else None,
            "ui": round(float(avg_row.avg_ui), 1) if avg_row and avg_row.avg_ui else None,
            "oi": round(float(avg_row.avg_oi), 1) if avg_row and avg_row.avg_oi else None,
        } if avg_row else None,
    }


@router.get("/growth")
async def student_growth(user: dict = Depends(student_only), db: AsyncSession = Depends(get_db)):
    cls = await svc.get_student_class(user["id"], db)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    rows = await svc.get_student_submissions_with_metrics(user["id"], cls.id, db)
    class_avgs = await svc.get_class_avg_per_assignment(cls.id, db)

    assignments = []
    class_avg_trend = []
    for i, (sub, asgn, m) in enumerate(rows):
        label = f"A{i+1}"
        assignments.append({
            "assignment_id": asgn.id, "label": label, "title": asgn.title,
            "aic": m.aic_score if m else None, "pi": m.pi_score if m else None,
            "ui": m.ui_score if m else None, "oi": m.oi_score if m else None,
            "topic": m.topic_score if m else None,
        })
        avg_row = class_avgs.get(asgn.id)
        class_avg_trend.append({
            "label": label,
            "aic": round(float(avg_row.avg_aic), 1) if avg_row and avg_row.avg_aic else None,
            "pi": round(float(avg_row.avg_pi), 1) if avg_row and avg_row.avg_pi else None,
            "ui": round(float(avg_row.avg_ui), 1) if avg_row and avg_row.avg_ui else None,
            "oi": round(float(avg_row.avg_oi), 1) if avg_row and avg_row.avg_oi else None,
        })

    return {"assignments": assignments, "class_avg_trend": class_avg_trend}


@router.get("/feedback/{assignment_id}")
async def student_feedback(
    assignment_id: int,
    user: dict = Depends(student_only),
    db: AsyncSession = Depends(get_db),
):
    fb = await svc.get_feedback_for_assignment(user["id"], assignment_id, db)

    sub_result = await db.execute(
        select(Submission).where(
            Submission.assignment_id == assignment_id,
            Submission.student_id == user["id"],
        )
    )
    sub = sub_result.scalar_one_or_none()
    m = None
    if sub:
        m_result = await db.execute(select(Metric).where(Metric.submission_id == sub.id))
        m = m_result.scalar_one_or_none()

    auto_guide = svc.build_auto_guide(m)

    return {
        "teacher_feedback": {
            "content": fb.content,
            "created_at": fb.created_at.strftime("%Y-%m-%d"),
        } if fb else None,
        "auto_guide": auto_guide,
    }
