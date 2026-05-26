import httpx
from app.config import settings

DEFAULT_KEYWORDS = [
    "however", "although", "because", "why", "how", "compare",
    "contrast", "analyze", "evaluate", "critique", "moreover",
    "therefore", "consequently", "alternatively", "nevertheless",
]


async def call_pipeline(job_id: str, submission: dict, baseline_config: dict | None = None) -> dict:
    config = {
        "pi_weights": [0.4, 0.3, 0.3],
        "critical_keywords": DEFAULT_KEYWORDS,
        "topic_score_alpha": 1.0,
        "topic_score_beta": 1.0,
        "backend_prefer": "sbert",
    }
    if baseline_config:
        config.update({key: value for key, value in baseline_config.items() if value is not None})

    payload = {
        "job_id": job_id,
        "submission": {
            "sample_id": f"sub-{submission['submission_id']}",
            "course": submission.get("course_code", "default"),
            "student_id": submission.get("user_id_str", "unknown"),
            "chatgpt_before": submission["chatgpt_before"],
            "user": submission["user_prompt"],
            "essay": submission["essay"],
        },
        "config": config,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{settings.PIPELINE_URL}/analyze", json=payload)
        response.raise_for_status()
        return response.json()


async def call_preoptimization_pipeline(job_id: str, submission: dict) -> dict:
    payload = _payload(job_id, submission, {
        "pi_weights": [0.4, 0.3, 0.3],
        "critical_keywords": DEFAULT_KEYWORDS,
        "topic_score_alpha": 1.0,
        "topic_score_beta": 1.0,
        "backend_prefer": "sbert",
    })

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{settings.PIPELINE_URL}/analyze-baseline", json=payload)
        response.raise_for_status()
        return response.json()


async def call_pipeline_batch(job_id: str, submissions: list[dict], baseline_config: dict | None = None) -> dict:
    config = _default_config()
    if baseline_config:
        config.update({key: value for key, value in baseline_config.items() if value is not None})
    payload = _batch_payload(job_id, submissions, config)

    async with httpx.AsyncClient(timeout=1200.0) as client:
        response = await client.post(f"{settings.PIPELINE_URL}/analyze-batch", json=payload)
        response.raise_for_status()
        return response.json()


async def call_preoptimization_pipeline_batch(job_id: str, submissions: list[dict]) -> dict:
    payload = _batch_payload(job_id, submissions, _default_config())

    async with httpx.AsyncClient(timeout=1200.0) as client:
        response = await client.post(f"{settings.PIPELINE_URL}/analyze-baseline-batch", json=payload)
        response.raise_for_status()
        return response.json()


def _payload(job_id: str, submission: dict, config: dict) -> dict:
    return {
        "job_id": job_id,
        "submission": {
            "sample_id": f"sub-{submission['submission_id']}",
            "course": submission.get("course_code", "default"),
            "student_id": submission.get("user_id_str", "unknown"),
            "chatgpt_before": submission["chatgpt_before"],
            "user": submission["user_prompt"],
            "essay": submission["essay"],
        },
        "config": config,
    }


def _batch_payload(job_id: str, submissions: list[dict], config: dict) -> dict:
    return {
        "job_id": job_id,
        "submissions": [
            {
                "sample_id": f"sub-{submission['submission_id']}",
                "course": submission.get("course_code", "default"),
                "student_id": submission.get("user_id_str", "unknown"),
                "chatgpt_before": submission["chatgpt_before"],
                "user": submission["user_prompt"],
                "essay": submission["essay"],
            }
            for submission in submissions
        ],
        "config": config,
    }


def _default_config() -> dict:
    return {
        "pi_weights": [0.4, 0.3, 0.3],
        "critical_keywords": DEFAULT_KEYWORDS,
        "topic_score_alpha": 1.0,
        "topic_score_beta": 1.0,
        "backend_prefer": "sbert",
    }
