from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.dependencies import require_role
from app.models.db_models import User, Assignment, Submission, Metric, ClassEnrollment
from app.schemas.teacher import FeedbackCreate, FeedbackCreated, TeacherAssignmentList
from app.services import teacher_service as svc

router = APIRouter()
teacher_only = require_role("teacher")


@router.get("/dashboard")
async def teacher_dashboard(user: dict = Depends(teacher_only), db: AsyncSession = Depends(get_db)):
    cls = await svc.get_teacher_class(user["id"], db)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    rows = await svc.get_all_student_latest_metrics(cls.id, db)
    trend_rows = await svc.get_class_trend(cls.id, db)

    scores = [m.aic_score if m else None for _, _, m in rows]
    risk_students = []
    top_students = []
    pi_scores, ui_scores, oi_scores, aic_scores = [], [], [], []

    for student, sub, m in rows:
        aic = m.aic_score if m else None
        pi = m.pi_score if m else None
        ui = m.ui_score if m else None
        oi = m.oi_score if m else None
        status = svc._status(aic)

        if aic is not None:
            aic_scores.append(aic)
        if pi is not None:
            pi_scores.append(pi)
        if ui is not None:
            ui_scores.append(ui)
        if oi is not None:
            oi_scores.append(oi)

        if status == "risk":
            risk_students.append({
                "id": student.id, "name": student.name,
                "aic": aic, "pi": pi, "ui": ui, "oi": oi,
                "risk_types": svc._risk_types(pi, ui, oi),
                "status": "risk",
            })
        if status in ("excellent", "good"):
            top_students.append({
                "id": student.id, "name": student.name,
                "aic": aic, "pi": pi, "ui": ui, "oi": oi, "status": status,
            })

    top_students.sort(key=lambda x: x["aic"] or 0, reverse=True)

    class_avg = {
        "aic": round(sum(aic_scores) / len(aic_scores), 1) if aic_scores else None,
        "pi": round(sum(pi_scores) / len(pi_scores), 1) if pi_scores else None,
        "ui": round(sum(ui_scores) / len(ui_scores), 1) if ui_scores else None,
        "oi": round(sum(oi_scores) / len(oi_scores), 1) if oi_scores else None,
    }

    trend = []
    for i, row in enumerate(trend_rows):
        trend.append({
            "label": f"A{i+1}",
            "aic": round(float(row.avg_aic), 1) if row.avg_aic else None,
            "pi": round(float(row.avg_pi), 1) if row.avg_pi else None,
        })

    total_students = len(rows)
    asgn_count_result = await db.execute(
        select(func.count(Assignment.id)).where(Assignment.class_id == cls.id)
    )
    asgn_count = asgn_count_result.scalar() or 0

    return {
        "cls": {
            "code": cls.class_code, "name": cls.class_name,
            "student_count": total_students, "assignment_count": asgn_count,
        },
        "class_avg": class_avg,
        "risk_count": len(risk_students),
        "excellent_count": sum(1 for _, _, m in rows if svc._status(m.aic_score if m else None) == "excellent"),
        "trend": trend,
        "risk_students": risk_students[:4],
        "top_students": top_students[:5],
        "aic_distribution": svc.build_aic_distribution(scores),
    }


@router.get("/students")
async def teacher_students(
    search: str = Query(""),
    status: str = Query(""),
    sort: str = Query("aic_desc"),
    page: int = Query(1),
    per_page: int = Query(20),
    user: dict = Depends(teacher_only),
    db: AsyncSession = Depends(get_db),
):
    cls = await svc.get_teacher_class(user["id"], db)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    rows = await svc.get_all_student_latest_metrics(cls.id, db)
    submission_counts = await svc.get_submission_counts_for_class(cls.id, db)
    students = []
    for student, sub, m in rows:
        aic = m.aic_score if m else None
        st = svc._status(aic)
        if search and search.lower() not in student.name.lower() and search not in student.user_id_str:
            continue
        if status and st != status:
            continue

        sub_count = int(submission_counts.get(student.id, 0))

        students.append({
            "id": student.id, "name": student.name, "user_id_str": student.user_id_str,
            "aic": aic, "pi": m.pi_score if m else None, "ui": m.ui_score if m else None,
            "oi": m.oi_score if m else None, "topic": m.topic_score if m else None,
            "status": st, "submission_count": sub_count,
        })

    # Sort
    reverse = "desc" in sort
    key = "aic" if "aic" in sort else "name"
    students.sort(key=lambda x: (x.get(key) or 0), reverse=reverse)

    total = len(students)
    start = (page - 1) * per_page
    return {"total": total, "students": students[start: start + per_page]}


@router.get("/assignments", response_model=TeacherAssignmentList)
async def teacher_assignments(user: dict = Depends(teacher_only), db: AsyncSession = Depends(get_db)):
    cls = await svc.get_teacher_class(user["id"], db)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    rows = await svc.get_teacher_assignments(cls.id, db)
    assignments = []
    for row in rows:
        due_date = row["due_date"].strftime("%Y-%m-%dT%H:%M:%S") if row["due_date"] else None
        assignments.append({
            "id": row["id"],
            "title": row["title"],
            "course_code": row["course_code"],
            "due_date": due_date,
            "submission_count": int(row["submission_count"] or 0),
            "analyzed_submission_count": int(row["analyzed_submission_count"] or 0),
        })

    return {"assignments": assignments}


@router.get("/students/{student_id}")
async def teacher_student_detail(
    student_id: int,
    user: dict = Depends(teacher_only),
    db: AsyncSession = Depends(get_db),
):
    cls = await svc.get_teacher_class(user["id"], db)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    in_class = await svc.student_belongs_to_class(student_id, cls.id, db)
    if not in_class:
        raise HTTPException(status_code=404, detail="Student not found")

    student_result = await db.execute(select(User).where(User.id == student_id, User.role == "student"))
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    rows = await svc.get_student_all_submissions(student_id, cls.id, db)

    trend, assignments = [], []
    latest_m = None
    for i, (sub, asgn, m) in enumerate(rows):
        label = f"A{i+1}"
        trend.append({"label": label, "aic": m.aic_score if m else None,
                      "pi": m.pi_score if m else None, "ui": m.ui_score if m else None,
                      "oi": m.oi_score if m else None})
        assignments.append({
            "id": asgn.id, "title": asgn.title,
            "aic": m.aic_score if m else None, "pi": m.pi_score if m else None,
            "ui": m.ui_score if m else None, "oi": m.oi_score if m else None,
            "submitted_at": sub.submitted_at.strftime("%Y-%m-%d") if sub else None,
        })
        if i == len(rows) - 1:
            latest_m = m

    latest_asgn_id = rows[-1][1].id if rows else None
    fb = await svc.get_student_feedback(student_id, latest_asgn_id, db) if latest_asgn_id else None

    weak_metrics = []
    if latest_m:
        if latest_m.pi_score and latest_m.pi_score < 65:
            weak_metrics.append("pi")
        if latest_m.ui_score and latest_m.ui_score < 65:
            weak_metrics.append("ui")
        if latest_m.oi_score and latest_m.oi_score < 65:
            weak_metrics.append("oi")

    return {
        "student": {"id": student.id, "name": student.name, "user_id_str": student.user_id_str},
        "latest_metrics": {
            "aic": latest_m.aic_score if latest_m else None,
            "pi": latest_m.pi_score if latest_m else None,
            "ui": latest_m.ui_score if latest_m else None,
            "oi": latest_m.oi_score if latest_m else None,
        },
        "trend": trend,
        "assignments": assignments,
        "teacher_feedback": {"content": fb.content, "updated_at": fb.updated_at.strftime("%Y-%m-%d")} if fb else None,
        "weak_metrics": weak_metrics,
    }


@router.get("/risk-students")
async def teacher_risk_students(user: dict = Depends(teacher_only), db: AsyncSession = Depends(get_db)):
    cls = await svc.get_teacher_class(user["id"], db)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    rows = await svc.get_all_student_latest_metrics(cls.id, db)
    risk = []
    for student, sub, m in rows:
        aic = m.aic_score if m else None
        if svc._status(aic) == "risk":
            risk.append({
                "id": student.id, "name": student.name,
                "aic": aic, "pi": m.pi_score if m else None,
                "ui": m.ui_score if m else None, "oi": m.oi_score if m else None,
                "risk_types": svc._risk_types(m.pi_score if m else None, m.ui_score if m else None, m.oi_score if m else None),
                "last_submitted": sub.submitted_at.strftime("%Y-%m-%d") if sub else None,
            })
    return {"risk_students": risk}


@router.post("/feedback", response_model=FeedbackCreated)
async def teacher_feedback(
    body: FeedbackCreate,
    user: dict = Depends(teacher_only),
    db: AsyncSession = Depends(get_db),
):
    cls = await svc.get_teacher_class(user["id"], db)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    asgn_ok = await svc.assignment_belongs_to_class(body.assignment_id, cls.id, db)
    student_ok = await svc.student_belongs_to_class(body.student_id, cls.id, db)
    if not asgn_ok or not student_ok:
        raise HTTPException(status_code=404, detail="Not found")

    fb = await svc.upsert_feedback(body.assignment_id, body.student_id, user["id"], body.content, db)
    return FeedbackCreated(id=fb.id, created_at=fb.created_at.strftime("%Y-%m-%dT%H:%M:%S"))


@router.get("/analytics/assignment/{assignment_id}")
async def teacher_assignment_analytics(
    assignment_id: int,
    user: dict = Depends(teacher_only),
    db: AsyncSession = Depends(get_db),
):
    cls = await svc.get_teacher_class(user["id"], db)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    asgn_result = await db.execute(
        select(Assignment).where(Assignment.id == assignment_id, Assignment.class_id == cls.id)
    )
    asgn = asgn_result.scalar_one_or_none()
    if not asgn:
        raise HTTPException(status_code=404, detail="Assignment not found")

    result = await db.execute(
        select(User, Submission, Metric)
        .join(Submission, (Submission.student_id == User.id) & (Submission.assignment_id == assignment_id))
        .join(Metric, Metric.submission_id == Submission.id)
        .join(ClassEnrollment, ClassEnrollment.student_id == User.id)
        .where(User.role == "student", ClassEnrollment.class_id == cls.id)
    )
    rows = result.all()

    aic_scores = [m.aic_score for _, _, m in rows if m.aic_score is not None]
    pi_avg = sum(m.pi_score for _, _, m in rows if m.pi_score) / len(rows) if rows else 0
    ui_avg = sum(m.ui_score for _, _, m in rows if m.ui_score) / len(rows) if rows else 0
    oi_avg = sum(m.oi_score for _, _, m in rows if m.oi_score) / len(rows) if rows else 0
    aic_avg = sum(aic_scores) / len(aic_scores) if aic_scores else 0

    sorted_rows = sorted(rows, key=lambda x: x[2].aic_score or 0, reverse=True)
    top5 = [{"name": s.name, "aic": m.aic_score} for s, _, m in sorted_rows[:5]]
    bottom5 = [{"name": s.name, "aic": m.aic_score} for s, _, m in sorted_rows[-5:]]

    return {
        "assignment": {"id": asgn.id, "title": asgn.title},
        "class_avg": {"aic": round(aic_avg, 1), "pi": round(pi_avg, 1), "ui": round(ui_avg, 1), "oi": round(oi_avg, 1)},
        "distribution": svc.build_aic_distribution(aic_scores),
        "top5": top5,
        "bottom5": bottom5,
        "difficulty": round(1 - aic_avg / 100, 2) if aic_avg else 0,
    }


@router.get("/analytics/advanced")
async def teacher_advanced_analytics(user: dict = Depends(teacher_only), db: AsyncSession = Depends(get_db)):
    cls = await svc.get_teacher_class(user["id"], db)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    rows = await svc.get_all_student_latest_metrics(cls.id, db)

    scatter_data = []
    for student, sub, m in rows:
        if m:
            scatter_data.append({
                "student_id": student.id, "name": student.name,
                "pi": m.pi_score, "ui": m.ui_score, "oi": m.oi_score, "aic": m.aic_score,
            })

    # Simple correlation: pi vs ui (Pearson)
    def pearson(xs, ys):
        n = len(xs)
        if n < 2:
            return 0
        mx, my = sum(xs) / n, sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        dx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
        dy = (sum((y - my) ** 2 for y in ys)) ** 0.5
        return round(num / (dx * dy), 2) if dx * dy else 0

    pi_list = [d["pi"] or 0 for d in scatter_data]
    ui_list = [d["ui"] or 0 for d in scatter_data]
    oi_list = [d["oi"] or 0 for d in scatter_data]
    aic_list = [d["aic"] or 0 for d in scatter_data]

    corr = {
        "pi_ui": pearson(pi_list, ui_list),
        "pi_oi": pearson(pi_list, oi_list),
        "ui_oi": pearson(ui_list, oi_list),
        "pi_aic": pearson(pi_list, aic_list),
        "ui_aic": pearson(ui_list, aic_list),
        "oi_aic": pearson(oi_list, aic_list),
    }

    return {"scatter_data": scatter_data, "correlation_matrix": corr}
