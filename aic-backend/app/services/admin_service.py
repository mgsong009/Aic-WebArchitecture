from sqlalchemy import desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import (
    User,
    Class,
    ClassEnrollment,
    Assignment,
    Submission,
    Metric,
    AnalysisJob,
    AnalysisRunMetadata,
    TeacherFeedback,
)
from app.services.job_service import create_and_dispatch_job


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


async def get_latest_analysis_run_quality(db: AsyncSession) -> dict | None:
    row = (await db.execute(
        select(AnalysisJob, AnalysisRunMetadata, Metric, Submission, Assignment)
        .join(AnalysisRunMetadata, AnalysisRunMetadata.job_id == AnalysisJob.id)
        .join(Submission, Submission.id == AnalysisJob.submission_id)
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .outerjoin(Metric, Metric.submission_id == Submission.id)
        .order_by(desc(AnalysisRunMetadata.measured_at), desc(AnalysisJob.completed_at))
        .limit(1)
    )).first()
    return _quality_response(row) if row else None


async def get_analysis_run_quality(job_uuid: str, db: AsyncSession) -> dict | None:
    row = (await db.execute(
        select(AnalysisJob, AnalysisRunMetadata, Metric, Submission, Assignment)
        .join(AnalysisRunMetadata, AnalysisRunMetadata.job_id == AnalysisJob.id)
        .join(Submission, Submission.id == AnalysisJob.submission_id)
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .outerjoin(Metric, Metric.submission_id == Submission.id)
        .where(AnalysisJob.job_uuid == job_uuid)
    )).first()
    return _quality_response(row) if row else None


async def reprocess_analysis_run(job_uuid: str, db: AsyncSession) -> dict | None:
    result = await db.execute(
        select(AnalysisJob).where(AnalysisJob.job_uuid == job_uuid)
    )
    job = result.scalar_one_or_none()
    if not job:
        return None

    next_job_uuid = await create_and_dispatch_job(job.submission_id, db)
    return {
        "ok": True,
        "runId": next_job_uuid,
        "sourceRunId": job_uuid,
    }


def _quality_response(row) -> dict:
    job, metadata, metric, _submission, assignment = row
    score_deltas = metadata.score_deltas or {}
    stage_runtimes = metadata.stage_runtimes_ms or {}
    status = "success" if metadata.quality_passed is not False else "warning"
    processed_count = metadata.processed_count or 0
    runtime_ms = metadata.total_runtime_ms
    baseline_runtime_ms = metadata.baseline_runtime_ms
    memory_peak_kb = metadata.memory_peak_kb
    baseline_memory_peak_kb = metadata.baseline_memory_peak_kb
    current_scores = _current_scores(metric)

    return {
        "runId": job.job_uuid,
        "course": assignment.course_code or "default",
        "assignment": assignment.title,
        "status": status,
        "processedRows": processed_count,
        "validRows": processed_count,
        "successRate": 100.0 if job.status == "done" else 0.0,
        "totalRuntimeSec": _ms_to_sec(runtime_ms),
        "avgRuntimePerSample": _avg_runtime_sec(runtime_ms, processed_count),
        "dataHealth": {
            "score": 100 if job.status == "done" else 0,
            "requiredColumns": "normal",
            "missingRows": 0,
            "duplicateRows": 0,
            "textOutliers": 0,
            "ratingCoverage": 0,
            "lowSampleCourses": 0,
        },
        "comparison": {
            "metricVersion": metadata.metric_version,
            "baselineVersion": metadata.baseline_version,
            "optimizedVersion": metadata.optimized_version,
            "runtimeMs": runtime_ms,
            "baselineRuntimeMs": baseline_runtime_ms,
            "runtimeDeltaPct": metadata.runtime_delta_pct,
            "memoryPeakKb": memory_peak_kb,
            "baselineMemoryPeakKb": baseline_memory_peak_kb,
            "memoryDeltaPct": metadata.memory_delta_pct,
            "throughputPerSec": _throughput_per_sec(processed_count, runtime_ms),
            "baselineThroughputPerSec": _throughput_per_sec(processed_count, baseline_runtime_ms),
            "throughputDeltaPct": _delta_pct(
                _throughput_per_sec(processed_count, runtime_ms),
                _throughput_per_sec(processed_count, baseline_runtime_ms),
            ),
            "scoreDeltas": score_deltas,
            "currentScores": current_scores,
            "scoreRows": _score_rows(current_scores, score_deltas),
            "performanceRows": _performance_rows(
                processed_count,
                runtime_ms,
                baseline_runtime_ms,
                memory_peak_kb,
                baseline_memory_peak_kb,
            ),
            "scoreTolerance": 0.01,
            "qualityPassed": metadata.quality_passed,
            "bootstrapPassed": metadata.bootstrap_passed,
            "measuredAt": metadata.measured_at.isoformat() if metadata.measured_at else None,
        },
        "backend": {
            "embeddingBackend": metric.embedding_backend if metric else None,
            "model": "paraphrase-multilingual-mpnet-base-v2",
            "fallback": "TF-IDF" if metric and metric.embedding_backend == "tfidf" else None,
            "metricVersion": metadata.metric_version,
            "pipelineVersion": metadata.optimized_version,
            "configHash": None,
            "createdAt": job.created_at.isoformat() if job.created_at else None,
        },
        "pipelineSteps": [
            {"name": name, "status": "success", "seconds": _ms_to_sec(seconds)}
            for name, seconds in stage_runtimes.items()
        ],
        "readiness": _readiness(metadata),
    }


def _readiness(metadata: AnalysisRunMetadata) -> dict:
    if metadata.quality_passed is False:
        return {
            "status": "blocked",
            "reason": "핵심 점수 delta가 허용 오차를 벗어났습니다.",
            "actions": ["PI/UI/OI/AIC delta와 기준 데이터셋을 확인하세요."],
        }
    if metadata.bootstrap_passed is False:
        return {
            "status": "caution",
            "reason": "Bootstrap 검증이 통과되지 않았습니다.",
            "actions": ["표본 수와 재표본 추출 결과를 확인하세요."],
        }
    return {
        "status": "ready",
        "reason": "수집된 실행 메타데이터에서 품질 회귀가 감지되지 않았습니다.",
        "actions": [],
    }


def _ms_to_sec(value) -> float | None:
    return round(float(value) / 1000, 3) if value is not None else None


def _avg_runtime_sec(total_ms, processed_count) -> float | None:
    if not total_ms or not processed_count:
        return None
    return round(float(total_ms) / 1000 / int(processed_count), 3)


def _current_scores(metric: Metric | None) -> dict:
    if not metric:
        return {}
    return {
        "pi": metric.pi_score,
        "ui": metric.ui_score,
        "oi": metric.oi_score,
        "aic": metric.aic_score,
    }


def _score_rows(current_scores: dict, score_deltas: dict) -> list[dict]:
    labels = {"pi": "PI", "ui": "UI", "oi": "OI", "aic": "AIC"}
    rows = []
    for key, label in labels.items():
        current = current_scores.get(key)
        delta = score_deltas.get(key)
        baseline = None
        if current is not None and delta is not None:
            baseline = round(float(current) - float(delta), 3)
        rows.append({
            "key": key,
            "label": label,
            "baseline": baseline,
            "optimized": current,
            "delta": delta,
            "tolerance": 0.01,
            "passed": None if delta is None else abs(float(delta)) <= 0.01,
        })
    return rows


def _performance_rows(
    processed_count: int,
    runtime_ms: float | None,
    baseline_runtime_ms: float | None,
    memory_peak_kb: float | None,
    baseline_memory_peak_kb: float | None,
) -> list[dict]:
    throughput = _throughput_per_sec(processed_count, runtime_ms)
    baseline_throughput = _throughput_per_sec(processed_count, baseline_runtime_ms)
    return [
        {
            "key": "runtime",
            "label": "Runtime",
            "unit": "s",
            "baseline": _ms_to_sec(baseline_runtime_ms),
            "optimized": _ms_to_sec(runtime_ms),
            "deltaPct": _delta_pct(runtime_ms, baseline_runtime_ms),
            "betterDirection": "down",
        },
        {
            "key": "memory",
            "label": "Memory peak",
            "unit": "MB",
            "baseline": _kb_to_mb(baseline_memory_peak_kb),
            "optimized": _kb_to_mb(memory_peak_kb),
            "deltaPct": _delta_pct(memory_peak_kb, baseline_memory_peak_kb),
            "betterDirection": "down",
        },
        {
            "key": "throughput",
            "label": "Throughput",
            "unit": "rows/s",
            "baseline": baseline_throughput,
            "optimized": throughput,
            "deltaPct": _delta_pct(throughput, baseline_throughput),
            "betterDirection": "up",
        },
    ]


def _throughput_per_sec(processed_count: int, runtime_ms: float | None) -> float | None:
    if not processed_count or not runtime_ms:
        return None
    seconds = float(runtime_ms) / 1000
    return round(processed_count / seconds, 3) if seconds else None


def _kb_to_mb(value) -> float | None:
    return round(float(value) / 1024, 3) if value is not None else None


def _delta_pct(current, baseline) -> float | None:
    if current is None or baseline in (None, 0):
        return None
    return round((float(current) - float(baseline)) / float(baseline) * 100, 3)
