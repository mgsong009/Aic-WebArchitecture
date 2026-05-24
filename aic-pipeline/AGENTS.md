# AGENTS.md

## Module Context

This service computes PI, UI, OI, AIC, topic, and embedding-derived metrics for a single submission. It is called only by the backend and wraps the legacy analysis code in `aic_pipeline.py`.

## Tech Stack & Constraints

- Use FastAPI, Pydantic, pandas, NumPy, scikit-learn, sentence-transformers, PyTorch CPU, and PyYAML.
- Keep Docker on Python 3.11 slim and CPU-only Torch.
- Preserve the SBERT model name `paraphrase-multilingual-mpnet-base-v2` unless scoring behavior is intentionally changed.
- The Dockerfile pre-downloads the model into `/app/models`; avoid first-request downloads.
- Uvicorn must stay single-worker unless the module-level embedding backend is redesigned.

## Implementation Patterns

- API schemas live in `app/schemas.py`; runtime orchestration lives in `app/pipeline_runner.py`.
- Keep FastAPI handlers thin; CPU-bound model load and analysis should run via `loop.run_in_executor`.
- `preload_model()` initializes a module-level backend and falls back from SBERT to TF-IDF when model loading fails.
- `run_analysis()` accepts backend-shaped payloads and returns backend/frontend field names directly; preserve these keys when refactoring.
- Core metric formulas should remain in `aic_pipeline.py` unless the wrapper contract is the only thing changing.

## Testing Strategy

- Install dependencies: `pip install -r requirements.txt`
- Local server: `python -m uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload`
- Container check: `docker compose up --build pipeline`
- For scoring changes, send a representative `/analyze` request and verify all `AnalyzeResponse` fields are present and numeric where expected.

## Local Golden Rules

- Do keep model loading and analysis off the event loop.
- Do preserve fallback behavior so the service can still respond when SBERT initialization fails.
- Do validate response field compatibility with backend `pipeline_client` and metric persistence before renaming any metric.
- Do not increase image size with GPU Torch or large optional NLP assets without an explicit deployment decision.
- Do not make the backend depend on internal pandas columns beyond the stable JSON response.
- Do not add concurrent workers around the current singleton backend.
