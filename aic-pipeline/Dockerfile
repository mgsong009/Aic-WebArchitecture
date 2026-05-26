FROM python:3.11-slim
WORKDIR /app

COPY aic-pipeline/requirements.txt .
# CPU-only torch to avoid 6GB GPU image
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download SBERT model at build time (prevents first-request timeout)
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('paraphrase-multilingual-mpnet-base-v2', cache_folder='/app/models')"

# Copy current and pre-optimization pipeline sources
COPY aic-pipeline/aic_pipeline.py .
COPY aic-pipeline/app/ ./app/
COPY before_project/ ./before_project/

ENV TRANSFORMERS_CACHE=/app/models

# Single worker: SBERT _backend singleton is not safe with multiple processes
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000", "--workers", "1"]
