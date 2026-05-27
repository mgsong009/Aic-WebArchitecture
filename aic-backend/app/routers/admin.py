from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import require_role
from app.database import get_db
from app.schemas.benchmark import (
    BenchmarkComparison,
    BenchmarkRunCreate,
    BenchmarkRunCreated,
    BenchmarkRunDetail,
    BenchmarkRunList,
)
from app.services.admin_service import (
    get_admin_dashboard_stats,
    get_analysis_run_pipeline_steps,
    get_analysis_run_quality,
    get_analysis_run_runtime,
    get_latest_analysis_run,
    reprocess_analysis_run,
)
from app.services.benchmark_service import (
    compare_benchmark_runs,
    create_benchmark_run,
    get_benchmark_run_detail,
    list_benchmark_runs,
)

router = APIRouter()
admin_only = require_role("admin")


@router.get("/dashboard")
async def admin_dashboard(
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    return await get_admin_dashboard_stats(db)


@router.get("/analysis-runs/latest")
async def latest_analysis_run(
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    return await get_latest_analysis_run(db)


@router.get("/analysis-runs/{run_id}/quality")
async def analysis_run_quality(
    run_id: str,
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    return await get_analysis_run_quality(db, run_id)


@router.get("/analysis-runs/{run_id}/pipeline-steps")
async def analysis_run_pipeline_steps(
    run_id: str,
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    return await get_analysis_run_pipeline_steps(db, run_id)


@router.get("/analysis-runs/{run_id}/runtime")
async def analysis_run_runtime(
    run_id: str,
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    return await get_analysis_run_runtime(db, run_id)


@router.post("/analysis-runs/{run_id}/reprocess")
async def analysis_run_reprocess(
    run_id: str,
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    return await reprocess_analysis_run(db, run_id)


@router.post("/benchmarks", response_model=BenchmarkRunCreated, status_code=status.HTTP_202_ACCEPTED)
async def benchmark_create(
    body: BenchmarkRunCreate = Body(default_factory=BenchmarkRunCreate),
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    return await create_benchmark_run(db, body)


@router.get("/benchmarks", response_model=BenchmarkRunList)
async def benchmark_list(
    limit: int = 20,
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    return await list_benchmark_runs(db, limit)


@router.get("/benchmarks/compare", response_model=BenchmarkComparison)
async def benchmark_compare(
    baselineRunId: str,
    optimizedRunId: str,
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    return await compare_benchmark_runs(db, baselineRunId, optimizedRunId)


@router.get("/benchmarks/{run_id}", response_model=BenchmarkRunDetail)
async def benchmark_detail(
    run_id: str,
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    return await get_benchmark_run_detail(db, run_id)
