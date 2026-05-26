from pydantic import BaseModel
from typing import Dict, List, Optional


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
    baseline_version: Optional[str] = None
    baseline_runtime_ms: Optional[float] = None
    baseline_memory_peak_kb: Optional[float] = None
    baseline_scores: Optional[Dict[str, float]] = None
    bootstrap_passed: Optional[bool] = None


class AnalysisMetadata(BaseModel):
    metric_version: str
    optimized_version: str
    baseline_version: Optional[str] = None
    processed_count: int
    total_runtime_ms: float
    memory_peak_kb: float
    stage_runtimes_ms: Dict[str, float]
    baseline_runtime_ms: Optional[float] = None
    baseline_memory_peak_kb: Optional[float] = None
    baseline_scores: Optional[Dict[str, float]] = None
    runtime_delta_pct: Optional[float] = None
    memory_delta_pct: Optional[float] = None
    score_deltas: Optional[Dict[str, float]] = None
    quality_passed: Optional[bool] = None
    bootstrap_passed: Optional[bool] = None


class AnalyzeRequest(BaseModel):
    job_id: str
    submission: SubmissionPayload
    config: AnalyzeConfig = AnalyzeConfig()


class BatchAnalyzeRequest(BaseModel):
    job_id: str
    submissions: List[SubmissionPayload]
    config: AnalyzeConfig = AnalyzeConfig()


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
    analysis_metadata: Optional[AnalysisMetadata] = None


class BatchAnalyzeResponse(BaseModel):
    job_id: str
    processed_count: int
    scores: Dict[str, float]
    results: List[AnalyzeResponse]
    analysis_metadata: Optional[AnalysisMetadata] = None
