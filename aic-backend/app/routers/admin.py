from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import require_role
from app.database import get_db
from app.services.admin_service import (
    get_admin_dashboard_stats,
    get_analysis_run_quality,
    get_latest_analysis_run_quality,
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
async def latest_analysis_run_quality(
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    result = await get_latest_analysis_run_quality(db)
    if not result:
        raise HTTPException(status_code=404, detail="No analysis run metadata found")
    return result


@router.get("/analysis-runs/{run_id}/quality")
async def analysis_run_quality(
    run_id: str,
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    result = await get_analysis_run_quality(run_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis run metadata not found")
    return result
