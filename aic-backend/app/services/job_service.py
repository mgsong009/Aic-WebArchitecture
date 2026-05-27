import uuid
import asyncio
import hashlib
import json
from time import perf_counter
from datetime import datetime, timezone
from sqlalchemy import select, update
from app.database import AsyncSessionLocal
from app.models.db_models import AnalysisJob, AnalysisRun, Metric, Submission, Assignment, User
from app.services.pipeline_client import DEFAULT_KEYWORDS, call_pipeline

PIPELINE_MODEL = "paraphrase-multilingual-mpnet-base-v2"
METRIC_VERSION = "v1.0.0"
PIPELINE_VERSION = "1.0"


async def create_and_dispatch_job(submission_id: int, db) -> str:
    job_uuid_str = str(uuid.uuid4())

    submission_data = await _build_submission_payload(db, submission_id)

    # Create job record
    job = AnalysisJob(job_uuid=job_uuid_str, submission_id=submission_id, status="pending")
    db.add(job)
    await db.commit()

    # Fire background task without awaiting
    asyncio.create_task(_run_pipeline(job_uuid_str, submission_id, submission_data))
    return job_uuid_str


async def recover_incomplete_jobs():
    """
    Recover jobs that were interrupted by process restart.
    pending/running -> pending, then re-dispatch.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AnalysisJob).where(AnalysisJob.status.in_(("pending", "running")))
        )
        jobs = list(result.scalars().all())
        if not jobs:
            return

        for job in jobs:
            job.status = "pending"
            job.error_message = None
            job.started_at = None
            job.completed_at = None
        await session.commit()

        for job in jobs:
            try:
                payload = await _build_submission_payload(session, job.submission_id)
            except Exception as exc:
                await session.execute(
                    update(AnalysisJob)
                    .where(AnalysisJob.id == job.id)
                    .values(
                        status="failed",
                        error_message=f"Recovery failed: {exc}",
                        completed_at=datetime.now(timezone.utc),
                    )
                )
                await session.commit()
                continue

            asyncio.create_task(_run_pipeline(job.job_uuid, job.submission_id, payload))


async def _build_submission_payload(db, submission_id: int) -> dict:
    sub_result = await db.execute(
        select(Submission, Assignment, User)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .join(User, Submission.student_id == User.id)
        .where(Submission.id == submission_id)
    )
    row = sub_result.first()
    if not row:
        raise ValueError(f"Submission {submission_id} not found")

    sub, assignment, student = row
    return {
        "submission_id": submission_id,
        "course_code": assignment.course_code or "default",
        "assignment_title": assignment.title,
        "user_id_str": student.user_id_str,
        "chatgpt_before": sub.chatgpt_before,
        "user_prompt": sub.user_prompt,
        "essay": sub.essay,
    }


async def _run_pipeline(job_uuid_str: str, submission_id: int, submission_data: dict):
    async with AsyncSessionLocal() as session:
        run_id = _make_run_id(job_uuid_str)
        existing_run = (await session.execute(
            select(AnalysisRun).where(AnalysisRun.job_uuid == job_uuid_str)
        )).scalar_one_or_none()
        running_values = {
            "submission_id": submission_id,
            "course": submission_data.get("course_code"),
            "assignment": submission_data.get("assignment_title"),
            "status": "running",
            "processed_rows": 1,
            "valid_rows": 0,
            "success_rate": 0.0,
            "total_runtime_sec": 0.0,
            "avg_runtime_per_sample": 0.0,
            "data_health": _build_data_health(submission_data),
            "backend_info": _build_backend_info(),
            "pipeline_steps": [],
            "readiness": {
                "status": "caution",
                "reason": "분석 실행이 진행 중입니다.",
                "actions": ["실행 완료 후 품질 지표를 다시 확인하세요."],
            },
            "error_message": None,
            "completed_at": None,
        }
        if existing_run:
            for key, value in running_values.items():
                setattr(existing_run, key, value)
        else:
            session.add(AnalysisRun(run_id=run_id, job_uuid=job_uuid_str, **running_values))

        # Mark as running
        await session.execute(
            update(AnalysisJob)
            .where(AnalysisJob.job_uuid == job_uuid_str)
            .values(status="running", started_at=datetime.now(timezone.utc))
        )
        await session.commit()

        total_start = perf_counter()
        pipeline_seconds = 0.0
        save_seconds = 0.0
        try:
            pipeline_start = perf_counter()
            result = await call_pipeline(job_uuid_str, submission_data)
            pipeline_seconds = perf_counter() - pipeline_start
            scaled = _scale_metrics(result)

            # Upsert metrics
            save_start = perf_counter()
            existing = await session.execute(
                select(Metric).where(Metric.submission_id == submission_id)
            )
            metric = existing.scalar_one_or_none()
            if metric:
                for k, v in scaled.items():
                    setattr(metric, k, v)
            else:
                metric = Metric(submission_id=submission_id, **scaled)
                session.add(metric)

            save_seconds = perf_counter() - save_start
            total_seconds = perf_counter() - total_start
            data_health = _build_data_health(submission_data)
            backend_info = _build_backend_info(result.get("embedding_backend"))
            pipeline_steps = _build_pipeline_steps(pipeline_seconds, save_seconds, "success")
            readiness = _build_readiness("completed", 100.0, data_health, backend_info)

            await session.execute(
                update(AnalysisJob)
                .where(AnalysisJob.job_uuid == job_uuid_str)
                .values(status="done", completed_at=datetime.now(timezone.utc))
            )
            await session.execute(
                update(AnalysisRun)
                .where(AnalysisRun.job_uuid == job_uuid_str)
                .values(
                    status="completed",
                    valid_rows=1,
                    success_rate=100.0,
                    total_runtime_sec=round(total_seconds, 3),
                    avg_runtime_per_sample=round(total_seconds, 3),
                    data_health=data_health,
                    backend_info=backend_info,
                    pipeline_steps=pipeline_steps,
                    readiness=readiness,
                    completed_at=datetime.now(timezone.utc),
                )
            )
            await session.commit()

        except Exception as exc:
            total_seconds = perf_counter() - total_start
            data_health = _build_data_health(submission_data)
            backend_info = _build_backend_info()
            pipeline_steps = _build_pipeline_steps(pipeline_seconds, save_seconds, "failed")
            await session.execute(
                update(AnalysisJob)
                .where(AnalysisJob.job_uuid == job_uuid_str)
                .values(status="failed", error_message=str(exc), completed_at=datetime.now(timezone.utc))
            )
            await session.execute(
                update(AnalysisRun)
                .where(AnalysisRun.job_uuid == job_uuid_str)
                .values(
                    status="failed",
                    valid_rows=0,
                    success_rate=0.0,
                    total_runtime_sec=round(total_seconds, 3),
                    avg_runtime_per_sample=round(total_seconds, 3),
                    data_health=data_health,
                    backend_info=backend_info,
                    pipeline_steps=pipeline_steps,
                    readiness=_build_readiness("failed", 0.0, data_health, backend_info, str(exc)),
                    error_message=str(exc),
                    completed_at=datetime.now(timezone.utc),
                )
            )
            await session.commit()


def _scale_metrics(result: dict) -> dict:
    return {
        "pi_score": _safe_round(result.get("pi")),
        "ui_score": _safe_round(result.get("ui")),
        "oi_score": _safe_round(result.get("oi")),
        "aic_score": _safe_round(result.get("aic")),
        "topic_score": _safe_round(result.get("topic_score")),
        "weight_pi": result.get("weight_pi"),
        "weight_ui": result.get("weight_ui"),
        "weight_oi": result.get("weight_oi"),
        "pi_depth_tokens": result.get("pi_depth_tokens"),
        "pi_depth_norm": result.get("pi_depth_norm"),
        "pi_critical_ratio": result.get("pi_critical_ratio"),
        "pi_avg_sent_len": result.get("pi_avg_sent_len"),
        "pi_ttr": result.get("pi_ttr"),
        "pi_complexity": result.get("pi_complexity"),
        "ui_cos_similarity": result.get("ui_cos_similarity"),
        "ui_distance": result.get("ui_distance"),
        "ui_newinfo_ratio": result.get("ui_newinfo_ratio"),
        "oi_topic_score_raw": result.get("oi_topic_score_raw"),
        "embedding_backend": result.get("embedding_backend"),
        "computed_at": datetime.now(timezone.utc),
    }


def _safe_round(value) -> int:
    if value is None:
        return None
    return round(float(value) * 100)


def _make_run_id(job_uuid_str: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"RUN-{stamp}-{job_uuid_str[:8]}"


def _build_data_health(submission_data: dict) -> dict:
    required_fields = ["chatgpt_before", "user_prompt", "essay"]
    missing_rows = sum(1 for field in required_fields if not submission_data.get(field))
    text_lengths = [len(str(submission_data.get(field) or "")) for field in required_fields]
    text_outliers = sum(1 for length in text_lengths if length < 20 or length > 20000)
    score = max(0, 100 - (missing_rows * 25) - (text_outliers * 10))
    return {
        "score": score,
        "requiredColumns": "normal" if missing_rows == 0 else "warning",
        "missingRows": missing_rows,
        "duplicateRows": 0,
        "textOutliers": text_outliers,
        "ratingCoverage": 0.0,
        "lowSampleCourses": 0,
    }


def _build_backend_info(embedding_backend: str | None = None) -> dict:
    backend = (embedding_backend or "unknown").lower()
    config = {
        "pi_weights": [0.4, 0.3, 0.3],
        "critical_keywords": DEFAULT_KEYWORDS,
        "topic_score_alpha": 1.0,
        "topic_score_beta": 1.0,
        "backend_prefer": "sbert",
    }
    config_hash = hashlib.sha1(json.dumps(config, sort_keys=True).encode("utf-8")).hexdigest()[:7]
    return {
        "embeddingBackend": backend.upper() if backend != "unknown" else "Unknown",
        "model": PIPELINE_MODEL,
        "fallback": "TF-IDF" if backend == "tfidf" else "None",
        "metricVersion": METRIC_VERSION,
        "pipelineVersion": PIPELINE_VERSION,
        "configHash": config_hash,
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }


def _build_pipeline_steps(pipeline_seconds: float, save_seconds: float, status: str) -> list[dict]:
    analyze_status = "failed" if status == "failed" else "success"
    save_status = "pending" if status == "failed" and save_seconds == 0 else "success"
    return [
        {"name": "Data Load", "status": "success", "seconds": 0.001},
        {"name": "Preprocess", "status": "success", "seconds": 0.001},
        {"name": "PI", "status": analyze_status, "seconds": round(pipeline_seconds * 0.15, 3)},
        {"name": "Embedding", "status": analyze_status, "seconds": round(pipeline_seconds * 0.55, 3)},
        {"name": "UI/OI", "status": analyze_status, "seconds": round(pipeline_seconds * 0.25, 3)},
        {"name": "Validation", "status": "warning", "seconds": 0.001},
        {"name": "Save", "status": save_status, "seconds": round(save_seconds, 3)},
    ]


def _build_readiness(
    status: str,
    success_rate: float,
    data_health: dict,
    backend_info: dict,
    error_message: str | None = None,
) -> dict:
    if status == "failed":
        return {
            "status": "blocked",
            "reason": f"분석 실행이 실패했습니다: {error_message}",
            "actions": ["파이프라인 로그와 입력 텍스트를 확인한 뒤 재분석을 실행하세요."],
        }

    actions = []
    if success_rate < 98:
        actions.append("분석 실패 항목을 재처리해 성공률을 98% 이상으로 회복하세요.")
    if data_health.get("ratingCoverage", 0) < 70:
        actions.append("rating 보유율이 70% 미만이므로 검증 지표 해석에 주의하세요.")
    if backend_info.get("fallback") != "None":
        actions.append("SBERT 모델 초기화 실패 여부를 확인하고 fallback 원인을 점검하세요.")

    if actions:
        return {
            "status": "caution",
            "reason": "분석은 완료됐지만 일부 데이터 품질 또는 백엔드 상태가 기준에 미달합니다.",
            "actions": actions,
        }

    return {
        "status": "ready",
        "reason": "분석 성공률, 데이터 품질, 백엔드 상태가 기준을 충족합니다.",
        "actions": ["현재 설정으로 다음 분석을 진행할 수 있습니다."],
    }
