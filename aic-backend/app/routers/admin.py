from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import require_role
from app.database import get_db
from app.services.admin_service import get_admin_dashboard_stats

router = APIRouter()
admin_only = require_role("admin")


@router.get("/dashboard")
async def admin_dashboard(
    user: dict = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
):
    return await get_admin_dashboard_stats(db)
