from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import require_role
from app.database import get_db
from app.services.admin_service import (
    get_admin_dashboard_stats,
    get_analysis_run_pipeline_steps,
    get_analysis_run_quality,
    get_analysis_run_runtime,
    get_latest_analysis_run,
    reprocess_analysis_run,
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
