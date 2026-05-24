from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import User, Class, ClassEnrollment, Assignment, Submission, Metric, AnalysisJob, TeacherFeedback


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
