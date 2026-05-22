from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.models.db_models import (
    User, Class, ClassEnrollment, Assignment, Submission, Metric, TeacherFeedback
)


def _status(aic: Optional[int]) -> str:
    if aic is None:
        return "pending"
    if aic >= 80:
        return "excellent"
    if aic >= 65:
        return "good"
    if aic >= 50:
        return "average"
    return "risk"


async def get_student_class(student_id: int, db: AsyncSession):
    result = await db.execute(
        select(Class)
        .join(ClassEnrollment, ClassEnrollment.class_id == Class.id)
        .where(ClassEnrollment.student_id == student_id)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_student_submissions_with_metrics(student_id: int, class_id: int, db: AsyncSession):
    result = await db.execute(
        select(Submission, Assignment, Metric)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .outerjoin(Metric, Metric.submission_id == Submission.id)
        .where(Submission.student_id == student_id)
        .where(Assignment.class_id == class_id)
        .order_by(Assignment.created_at.asc())
    )
    return result.all()


async def get_class_avg_per_assignment(class_id: int, db: AsyncSession) -> dict:
    result = await db.execute(
        select(
            Assignment.id,
            func.avg(Metric.aic_score).label("avg_aic"),
            func.avg(Metric.pi_score).label("avg_pi"),
            func.avg(Metric.ui_score).label("avg_ui"),
            func.avg(Metric.oi_score).label("avg_oi"),
        )
        .join(Submission, Submission.assignment_id == Assignment.id)
        .join(Metric, Metric.submission_id == Submission.id)
        .where(Assignment.class_id == class_id)
        .group_by(Assignment.id)
    )
    return {row.id: row for row in result.all()}


async def get_student_rank(student_id: int, class_id: int, latest_assignment_id: int, db: AsyncSession):
    result = await db.execute(
        select(Submission.student_id, Metric.aic_score)
        .join(Metric, Metric.submission_id == Submission.id)
        .where(Submission.assignment_id == latest_assignment_id)
    )
    scores = [(row.student_id, row.aic_score) for row in result.all()]
    if not scores:
        return None, 0
    scores.sort(key=lambda x: (x[1] or 0), reverse=True)
    rank = next((i + 1 for i, (sid, _) in enumerate(scores) if sid == student_id), None)
    return rank, len(scores)


async def get_feedback_for_assignment(student_id: int, assignment_id: int, db: AsyncSession):
    result = await db.execute(
        select(TeacherFeedback)
        .where(TeacherFeedback.student_id == student_id)
        .where(TeacherFeedback.assignment_id == assignment_id)
    )
    return result.scalar_one_or_none()


def build_auto_guide(metrics) -> dict:
    strengths = []
    improvements = []
    tips = []

    if metrics is None:
        return {"strengths": [], "improvements": ["분석 결과를 기다리는 중입니다."], "tips": []}

    if metrics.oi_score and metrics.oi_score >= 70:
        strengths.append(f"OI 독창성 {metrics.oi_score}점 — 자신만의 관점이 잘 드러납니다.")
    if metrics.pi_score and metrics.pi_score >= 70:
        strengths.append(f"PI 질문 깊이 {metrics.pi_score}점 — AI에게 깊이 있는 질문을 하고 있습니다.")

    if metrics.ui_score and metrics.ui_score < 65:
        improvements.append(f"UI {metrics.ui_score}점: AI 초안을 더 적극적으로 수정해보세요. 단락 순서를 바꾸거나 새 정보를 30% 이상 추가하세요.")
    if metrics.pi_score and metrics.pi_score < 65:
        improvements.append(f"PI {metrics.pi_score}점: '왜', '어떻게', '한계는 무엇인가' 같은 심화 질문어를 사용해보세요.")
    if metrics.oi_score and metrics.oi_score < 65:
        improvements.append(f"OI {metrics.oi_score}점: 반대 의견도 포함하고 외부 자료와 직접 연결해보세요.")

    tips.append("다음 과제에서 AI 초안 수정 비율을 30% 이상 목표로 설정하세요.")
    tips.append("프롬프트에 구체적인 제약 조건(분량, 형식, 관점)을 명시하세요.")

    return {"strengths": strengths, "improvements": improvements, "tips": tips}
