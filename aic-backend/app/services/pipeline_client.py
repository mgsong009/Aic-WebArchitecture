import httpx
from app.config import settings

DEFAULT_KEYWORDS = [
    "however", "although", "because", "why", "how", "compare",
    "contrast", "analyze", "evaluate", "critique", "moreover",
    "therefore", "consequently", "alternatively", "nevertheless",
]


async def call_pipeline(job_id: str, submission: dict) -> dict:
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
        "config": {
            "pi_weights": [0.4, 0.3, 0.3],
            "critical_keywords": DEFAULT_KEYWORDS,
            "topic_score_alpha": 1.0,
            "topic_score_beta": 1.0,
            "backend_prefer": "sbert",
        },
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{settings.PIPELINE_URL}/analyze", json=payload)
        response.raise_for_status()
        return response.json()
