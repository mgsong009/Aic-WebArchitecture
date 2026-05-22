from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.db_models import User, Class, ClassEnrollment
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo, RefreshResponse
from app.services.auth_service import verify_password, create_access_token, create_refresh_token, decode_token
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.user_id_str == body.user_id))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if user.role != body.role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Role mismatch")

    # Find class_code for student
    class_code = None
    if user.role == "student":
        enroll_result = await db.execute(
            select(Class.class_code)
            .join(ClassEnrollment, ClassEnrollment.class_id == Class.id)
            .where(ClassEnrollment.student_id == user.id)
            .limit(1)
        )
        row = enroll_result.first()
        if row:
            class_code = row[0]
    elif user.role == "teacher":
        cls_result = await db.execute(
            select(Class.class_code).where(Class.teacher_id == user.id).limit(1)
        )
        row = cls_result.first()
        if row:
            class_code = row[0]

    token_data = {"sub": user.user_id_str, "role": user.role, "id": user.id, "name": user.name}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path="/api/v1/auth/refresh",
        max_age=7 * 24 * 3600,
    )

    return TokenResponse(
        access_token=access_token,
        user=UserInfo(id=user.id, name=user.name, role=user.role, class_code=class_code),
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    payload = decode_token(token, "refresh")
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_data = {"sub": payload["sub"], "role": payload["role"], "id": payload["id"], "name": payload["name"]}
    new_access = create_access_token(token_data)
    return RefreshResponse(access_token=new_access)


@router.post("/logout")
async def logout(response: Response, user: dict = Depends(get_current_user)):
    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
    return {"ok": True}
