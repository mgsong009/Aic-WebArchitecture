import asyncio
from fastapi import FastAPI, HTTPException
from app.schemas import AnalyzeRequest, AnalyzeResponse, BatchAnalyzeRequest, BatchAnalyzeResponse
from app.pipeline_runner import run_analysis, run_analysis_batch, preload_model
from app.baseline_runner import run_baseline_analysis, run_baseline_analysis_batch

app = FastAPI(title="AIC Pipeline", version="1.0")


@app.on_event("startup")
async def warmup():
    loop = asyncio.get_running_loop()
    # CPU-bound model load → run in thread pool so event loop stays free
    try:
        await loop.run_in_executor(None, preload_model)
    except Exception as exc:
        print(f"[pipeline] Model preload failed, continuing with fallback backend: {exc}", flush=True)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, run_analysis, request.dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return result


@app.post("/analyze-batch", response_model=BatchAnalyzeResponse)
async def analyze_batch(request: BatchAnalyzeRequest):
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, run_analysis_batch, request.dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return result


@app.post("/analyze-baseline", response_model=AnalyzeResponse)
async def analyze_baseline(request: AnalyzeRequest):
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, run_baseline_analysis, request.dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return result


@app.post("/analyze-baseline-batch", response_model=BatchAnalyzeResponse)
async def analyze_baseline_batch(request: BatchAnalyzeRequest):
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, run_baseline_analysis_batch, request.dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return result


@app.get("/health")
async def health():
    return {"status": "ok"}
