from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, student, teacher, submissions, jobs, admin
from app.services.job_service import recover_incomplete_jobs

app = FastAPI(title="AIC Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://frontend"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/api/v1/auth",    tags=["auth"])
app.include_router(student.router,     prefix="/api/v1/student", tags=["student"])
app.include_router(teacher.router,     prefix="/api/v1/teacher", tags=["teacher"])
app.include_router(submissions.router, prefix="/api/v1",         tags=["submissions"])
app.include_router(jobs.router,        prefix="/api/v1",         tags=["jobs"])
app.include_router(admin.router,       prefix="/api/v1/admin",   tags=["admin"])


@app.on_event("startup")
async def recover_jobs():
    try:
        await recover_incomplete_jobs()
    except Exception as exc:
        print(f"[backend] Job recovery skipped due to startup error: {exc}", flush=True)


@app.get("/health")
async def health():
    return {"status": "ok"}
