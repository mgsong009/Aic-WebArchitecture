from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MetricsFull(BaseModel):
    aic: Optional[int] = None
    pi: Optional[int] = None
    ui: Optional[int] = None
    oi: Optional[int] = None
    topic: Optional[int] = None
    weight_pi: Optional[float] = None
    weight_ui: Optional[float] = None
    weight_oi: Optional[float] = None
    pi_depth_tokens: Optional[int] = None
    pi_critical_ratio: Optional[float] = None
    pi_complexity: Optional[float] = None
    ui_distance: Optional[float] = None
    ui_newinfo_ratio: Optional[float] = None
    embedding_backend: Optional[str] = None


class MetricsDelta(BaseModel):
    aic: Optional[int] = None
    pi: Optional[int] = None
    ui: Optional[int] = None
    oi: Optional[int] = None


class ClassAvg(BaseModel):
    aic: Optional[float] = None
    pi: Optional[float] = None
    ui: Optional[float] = None
    oi: Optional[float] = None
    topic: Optional[float] = None


class TrendPoint(BaseModel):
    assignment_id: int
    label: str
    aic: Optional[int] = None
    class_avg: Optional[float] = None


class MetricsHistoryPoint(BaseModel):
    label: str
    pi: Optional[int] = None
    ui: Optional[int] = None
    oi: Optional[int] = None


class RecentAssignment(BaseModel):
    id: int
    title: str
    submitted_at: Optional[str] = None
    aic: Optional[int] = None
    status: str


class StudentInfo(BaseModel):
    id: int
    name: str
    class_code: Optional[str] = None


class StudentDashboard(BaseModel):
    student: StudentInfo
    latest_metrics: MetricsFull
    latest_delta: MetricsDelta
    class_avg: ClassAvg
    rank: Optional[int] = None
    total_students: int
    trend: List[TrendPoint]
    recent_assignments: List[RecentAssignment]
    metrics_history: List[MetricsHistoryPoint]


class AssignmentListItem(BaseModel):
    id: int
    title: str
    due_date: Optional[str] = None
    submitted_at: Optional[str] = None
    aic: Optional[int] = None
    pi: Optional[int] = None
    ui: Optional[int] = None
    oi: Optional[int] = None
    status: str  # "done" | "pending" | "not_submitted"


class AssignmentList(BaseModel):
    assignments: List[AssignmentListItem]


class SubmissionDetail(BaseModel):
    id: int
    chatgpt_before: str
    user_prompt: str
    essay: str


class AssignmentInfo(BaseModel):
    id: int
    title: str
    course_code: Optional[str] = None


class AssignmentDetail(BaseModel):
    assignment: AssignmentInfo
    submission: Optional[SubmissionDetail] = None
    metrics: Optional[MetricsFull] = None
    class_avg: Optional[ClassAvg] = None


class GrowthTrendPoint(BaseModel):
    assignment_id: int
    label: str
    title: str
    aic: Optional[int] = None
    pi: Optional[int] = None
    ui: Optional[int] = None
    oi: Optional[int] = None
    topic: Optional[int] = None


class ClassAvgTrendPoint(BaseModel):
    label: str
    aic: Optional[float] = None
    pi: Optional[float] = None
    ui: Optional[float] = None
    oi: Optional[float] = None


class GrowthData(BaseModel):
    assignments: List[GrowthTrendPoint]
    class_avg_trend: List[ClassAvgTrendPoint]


class AutoGuide(BaseModel):
    strengths: List[str]
    improvements: List[str]
    tips: List[str]


class FeedbackTeacher(BaseModel):
    content: Optional[str] = None
    created_at: Optional[str] = None


class FeedbackData(BaseModel):
    teacher_feedback: Optional[FeedbackTeacher] = None
    auto_guide: AutoGuide
