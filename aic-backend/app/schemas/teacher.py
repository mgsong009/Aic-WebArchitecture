from pydantic import BaseModel
from typing import Optional, List


class ClassInfo(BaseModel):
    code: str
    name: str
    student_count: int
    assignment_count: int


class ClassAvg(BaseModel):
    aic: Optional[float] = None
    pi: Optional[float] = None
    ui: Optional[float] = None
    oi: Optional[float] = None


class TrendPoint(BaseModel):
    label: str
    aic: Optional[float] = None
    pi: Optional[float] = None


class RiskStudentSummary(BaseModel):
    id: int
    name: str
    aic: Optional[int] = None
    pi: Optional[int] = None
    ui: Optional[int] = None
    oi: Optional[int] = None
    risk_types: List[str]
    status: str = "risk"


class TopStudentSummary(BaseModel):
    id: int
    name: str
    aic: Optional[int] = None
    pi: Optional[int] = None
    ui: Optional[int] = None
    oi: Optional[int] = None
    status: str


class TeacherDashboard(BaseModel):
    cls: ClassInfo
    class_avg: ClassAvg
    risk_count: int
    excellent_count: int
    trend: List[TrendPoint]
    risk_students: List[RiskStudentSummary]
    top_students: List[TopStudentSummary]
    aic_distribution: List[int]  # 7 buckets: 0-40,40-50,...,90+


class StudentListItem(BaseModel):
    id: int
    name: str
    user_id_str: str
    aic: Optional[int] = None
    pi: Optional[int] = None
    ui: Optional[int] = None
    oi: Optional[int] = None
    topic: Optional[int] = None
    status: str
    submission_count: int


class StudentList(BaseModel):
    total: int
    students: List[StudentListItem]


class TeacherAssignmentItem(BaseModel):
    id: int
    title: str
    course_code: Optional[str] = None
    due_date: Optional[str] = None
    submission_count: int
    analyzed_submission_count: int


class TeacherAssignmentList(BaseModel):
    assignments: List[TeacherAssignmentItem]


class AssignmentHistoryItem(BaseModel):
    id: int
    title: str
    aic: Optional[int] = None
    pi: Optional[int] = None
    ui: Optional[int] = None
    oi: Optional[int] = None
    submitted_at: Optional[str] = None


class FeedbackInfo(BaseModel):
    content: Optional[str] = None
    updated_at: Optional[str] = None


class StudentDetailTrend(BaseModel):
    label: str
    aic: Optional[int] = None
    pi: Optional[int] = None
    ui: Optional[int] = None
    oi: Optional[int] = None


class StudentDetail(BaseModel):
    student: dict
    latest_metrics: dict
    trend: List[StudentDetailTrend]
    assignments: List[AssignmentHistoryItem]
    teacher_feedback: Optional[FeedbackInfo] = None
    weak_metrics: List[str]


class RiskStudentDetail(BaseModel):
    id: int
    name: str
    aic: Optional[int] = None
    pi: Optional[int] = None
    ui: Optional[int] = None
    oi: Optional[int] = None
    risk_types: List[str]
    last_submitted: Optional[str] = None


class RiskStudentList(BaseModel):
    risk_students: List[RiskStudentDetail]


class FeedbackCreate(BaseModel):
    assignment_id: int
    student_id: int
    content: str


class FeedbackCreated(BaseModel):
    id: int
    created_at: str


class AssignmentAnalytics(BaseModel):
    assignment: dict
    class_avg: ClassAvg
    distribution: List[int]
    top5: List[dict]
    bottom5: List[dict]
    difficulty: float


class AdvancedAnalytics(BaseModel):
    scatter_data: List[dict]
    correlation_matrix: dict
