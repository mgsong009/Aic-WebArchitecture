from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubmissionCreate(BaseModel):
    assignment_id: int
    chatgpt_before: str
    user_prompt: str
    essay: str


class SubmissionCreated(BaseModel):
    submission_id: int
    job_id: str
    status: str = "pending"


class MetricsSummary(BaseModel):
    aic: Optional[int] = None
    pi: Optional[int] = None
    ui: Optional[int] = None
    oi: Optional[int] = None
    topic: Optional[int] = None


class JobStatus(BaseModel):
    job_id: str
    status: str
    metrics: Optional[MetricsSummary] = None
    error: Optional[str] = None
