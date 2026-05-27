from pydantic import BaseModel, Field
from typing import Optional, List


class SubmissionPayload(BaseModel):
    sample_id: str
    course: str
    student_id: str
    chatgpt_before: str
    user: str
    essay: str


class AnalyzeConfig(BaseModel):
    pi_weights: List[float] = [0.4, 0.3, 0.3]
    critical_keywords: List[str] = []
    topic_score_alpha: float = 1.0
    topic_score_beta: float = 1.0
    backend_prefer: str = "sbert"


class AnalyzeRequest(BaseModel):
    job_id: str
    submission: SubmissionPayload
    config: AnalyzeConfig = AnalyzeConfig()


class PipelineStep(BaseModel):
    name: str
    status: str
    seconds: float


class AnalyzeResponse(BaseModel):
    job_id: str
    pi: float
    ui: float
    oi: float
    aic: float
    topic_score: float
    weight_pi: float
    weight_ui: float
    weight_oi: float
    pi_depth_tokens: int
    pi_depth_norm: float
    pi_critical_ratio: float
    pi_avg_sent_len: float
    pi_ttr: float
    pi_complexity: float
    ui_cos_similarity: float
    ui_distance: float
    ui_newinfo_ratio: float
    oi_topic_score_raw: float
    embedding_backend: str
    pipeline_steps: List[PipelineStep] = Field(default_factory=list)
