# AIC Platform — 풀스택 웹아키텍처 구현 설계서

> **목적**: 정적 HTML 프로토타입을 4개 컨테이너 기반 웹 시스템으로 마이그레이션.
> 이 문서를 구현 AI가 읽으면 질문 없이 전체를 구현할 수 있도록 충분히 구체적으로 작성함.

---

## 1. 아키텍처 개요

```
┌──────────────────────────────────────────────────────────────────┐
│                      외부 브라우저 (HTTP)                         │
└───────────────────────────┬──────────────────────────────────────┘
                            │ :80
┌───────────────────────────▼──────────────────────────────────────┐
│  Container: frontend  (nginx:alpine)                             │
│  Vue 3 SPA dist/ 서빙 + /api/* → backend:8000 프록시            │
└───────────────────────────┬──────────────────────────────────────┘
                            │ HTTP 내부 Docker 네트워크
┌───────────────────────────▼──────────────────────────────────────┐
│  Container: backend  (python:3.11-slim, uvicorn :8000)           │
│  FastAPI — JWT 인증, 비즈니스 로직, DB ORM, 비동기 작업 디스패치 │
└──────────────┬───────────────────────────┬───────────────────────┘
               │ MySQL :3306               │ HTTP 내부
               ▼                           ▼
┌──────────────────────┐    ┌─────────────────────────────────────┐
│  Container: db       │    │  Container: pipeline                │
│  mysql:8.0           │    │  (python:3.11, uvicorn :9000)       │
│  Volume: mysql_data  │    │  FastAPI — aic_pipeline.py 래퍼     │
└──────────────────────┘    │  Volume: model_cache (SBERT 420MB)  │
                            └─────────────────────────────────────┘
```

### 핵심 원칙
- 컨테이너 간 통신은 Docker 내부 네트워크 호스트명 사용 (`db`, `backend`, `pipeline`, `frontend`)
- 프론트엔드는 파이프라인을 직접 호출하지 않는다. 백엔드만이 파이프라인을 호출한다.
- 파이프라인 0.0-1.0 float 출력 → 백엔드가 ×100 반올림 → DB 정수 저장 → 프론트에 정수 전달
- 파이프라인 포트 9000은 외부에 절대 노출하지 않는다
- JWT: Access Token 30분 / Refresh Token 7일(HttpOnly 쿠키)

---

## 2. 플랫폼 도메인 이해

**AIC (AI Collaboration Index) 플랫폼**: 학생의 생성형 AI 활용 능력을 정량 평가하는 교육 분석 시스템

### 평가 지표
| 지표 | 의미 | 계산 기반 |
|------|------|----------|
| **PI** (Prompt Insight) | 학생이 AI에게 던진 질문의 깊이·비판성·복잡도 | `user` 컬럼(학생 프롬프트) |
| **UI** (User Intervention) | 학생이 AI 초안을 얼마나 의미 있게 수정했는지 | `chatgpt_before` vs `essay` 의미 거리 |
| **OI** (Originality Index) | 최종 에세이에서 학생 고유 관점이 얼마나 드러나는지 | topic_score 편차 |
| **AIC** | 종합 점수 | `w_pi×PI + w_ui×UI + w_oi×OI` |

### 사용자 역할
- **학생(Student)**: 자신의 과제별 점수, 성장 추이, 피드백 가이드 열람
- **교사(Teacher)**: 반 전체 현황, 개별 학생 모니터링, 위험군 관리, 피드백 작성

---

## 3. 데이터베이스 스키마 (MySQL 8.0)

```sql
CREATE DATABASE IF NOT EXISTS aic_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aic_db;

-- 사용자 (학생 + 교사 통합)
CREATE TABLE users (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id_str   VARCHAR(64)  NOT NULL UNIQUE,   -- "student_001", "teacher_kim"
    password_hash VARCHAR(256) NOT NULL,
    role          ENUM('student','teacher') NOT NULL,
    name          VARCHAR(128) NOT NULL,
    email         VARCHAR(256),
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role)
) ENGINE=InnoDB;

-- 수업/클래스
CREATE TABLE classes (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    class_code  VARCHAR(32)  NOT NULL UNIQUE,   -- "CS101"
    class_name  VARCHAR(256) NOT NULL,
    teacher_id  INT UNSIGNED NOT NULL,
    semester    VARCHAR(32),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 수강 관계 (학생 ↔ 수업)
CREATE TABLE class_enrollments (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    class_id    INT UNSIGNED NOT NULL,
    student_id  INT UNSIGNED NOT NULL,
    enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id)   REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id)   ON DELETE CASCADE,
    UNIQUE KEY uq_enrollment (class_id, student_id)
) ENGINE=InnoDB;

-- 과제 (수업당 N개)
CREATE TABLE assignments (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    class_id     INT UNSIGNED NOT NULL,
    title        VARCHAR(512) NOT NULL,
    description  TEXT,
    course_code  VARCHAR(32),    -- pipeline CSV "course" 컬럼과 매핑
    due_date     DATETIME,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    INDEX idx_class (class_id)
) ENGINE=InnoDB;

-- 제출 (학생의 원본 텍스트)
-- chatgpt_before: AI가 처음 출력한 텍스트 (학생이 작업 기반으로 삼은 것)
-- user_prompt:    학생이 AI에게 입력한 프롬프트
-- essay:          학생 최종 제출물
CREATE TABLE submissions (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    assignment_id   INT UNSIGNED NOT NULL,
    student_id      INT UNSIGNED NOT NULL,
    chatgpt_before  MEDIUMTEXT NOT NULL,
    user_prompt     MEDIUMTEXT NOT NULL,
    essay           MEDIUMTEXT NOT NULL,
    submitted_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id)    REFERENCES users(id)       ON DELETE CASCADE,
    UNIQUE KEY uq_submission (assignment_id, student_id),  -- 과제당 1회 제출
    INDEX idx_student (student_id)
) ENGINE=InnoDB;

-- 지표 (파이프라인 결과 저장)
-- 주요 점수: 0-100 정수 (pipeline float × 100 반올림)
-- 세부 지표: float 그대로 보존
CREATE TABLE metrics (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    submission_id         INT UNSIGNED NOT NULL UNIQUE,
    pi_score              TINYINT UNSIGNED,     -- NULL = 분석 미완료
    ui_score              TINYINT UNSIGNED,
    oi_score              TINYINT UNSIGNED,
    aic_score             TINYINT UNSIGNED,
    topic_score           TINYINT UNSIGNED,
    weight_pi             FLOAT,
    weight_ui             FLOAT,
    weight_oi             FLOAT,
    pi_depth_tokens       INT,
    pi_depth_norm         FLOAT,
    pi_critical_ratio     FLOAT,
    pi_avg_sent_len       FLOAT,
    pi_ttr                FLOAT,
    pi_complexity         FLOAT,
    ui_cos_similarity     FLOAT,
    ui_distance           FLOAT,
    ui_newinfo_ratio      FLOAT,
    oi_topic_score_raw    FLOAT,
    embedding_backend     VARCHAR(16),           -- 'sbert' or 'tfidf'
    computed_at           DATETIME,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 비동기 분석 작업 추적
CREATE TABLE analysis_jobs (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    job_uuid        CHAR(36) NOT NULL UNIQUE,    -- UUID v4, 클라이언트에 반환
    submission_id   INT UNSIGNED NOT NULL,
    status          ENUM('pending','running','done','failed') DEFAULT 'pending',
    error_message   TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at      DATETIME,
    completed_at    DATETIME,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- 교사 피드백
CREATE TABLE teacher_feedback (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    assignment_id   INT UNSIGNED NOT NULL,
    student_id      INT UNSIGNED NOT NULL,
    teacher_id      INT UNSIGNED NOT NULL,
    content         TEXT NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id)    REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id)    REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uq_feedback (assignment_id, student_id)
) ENGINE=InnoDB;
```

---

## 4. API 명세

### Base URL
- 백엔드 내부: `http://backend:8000`
- 프론트엔드 접근: `/api/` (nginx가 백엔드로 프록시)
- 모든 엔드포인트 prefix: `/api/v1/`

### 4.1 인증

**POST /api/v1/auth/login**
```json
// Request
{ "user_id": "student_001", "password": "pass123", "role": "student" }
// Response 200
{ "access_token": "<jwt>", "token_type": "bearer", "user": { "id": 1, "name": "김민준", "role": "student", "class_code": "CS101" } }
// Set-Cookie: refresh_token=<jwt>; HttpOnly; SameSite=Lax; Path=/api/v1/auth/refresh
```

**POST /api/v1/auth/refresh**
```json
// HttpOnly 쿠키 자동 전송
// Response 200
{ "access_token": "<new_jwt>" }
```

**POST /api/v1/auth/logout**
```json
// Authorization: Bearer <token>
// Response 200 + refresh_token 쿠키 삭제
{ "ok": true }
```

### 4.2 학생 엔드포인트 (JWT role=student 필요)

**GET /api/v1/student/dashboard**
```json
{
  "student": { "id": 1, "name": "김민준", "class_code": "CS101" },
  "latest_metrics": { "aic": 71, "pi": 72, "ui": 68, "oi": 75, "topic": 83 },
  "latest_delta": { "aic": 5, "pi": 3, "ui": -2, "oi": 7 },
  "class_avg": { "aic": 66, "pi": 65, "ui": 70, "oi": 62, "topic": 74 },
  "rank": 7, "total_students": 28,
  "trend": [
    { "assignment_id": 1, "label": "A1", "aic": 54, "class_avg": 60 },
    { "assignment_id": 2, "label": "A2", "aic": 63, "class_avg": 62 }
  ],
  "recent_assignments": [
    { "id": 5, "title": "생성형 AI 윤리 에세이", "submitted_at": "2025-03-18", "aic": 71, "status": "done" }
  ],
  "metrics_history": [
    { "label": "A1", "pi": 52, "ui": 58, "oi": 51 }
  ]
}
```

**GET /api/v1/student/assignments** — 전체 과제 목록 + 점수

**GET /api/v1/student/assignments/{assignment_id}** — 과제 상세 (원문 + 지표 + 반 평균)

**GET /api/v1/student/growth** — 전체 과제 성장 추이 + 반 평균 추이

**GET /api/v1/student/feedback/{assignment_id}** — 교사 피드백 + 자동 개선 가이드

### 4.3 교사 엔드포인트 (JWT role=teacher 필요)

**GET /api/v1/teacher/dashboard** — 반 전체 현황, 위험군 목록, AIC 분포

**GET /api/v1/teacher/students** — 학생 목록 (쿼리: `?search=&sort=aic_desc&status=risk&page=1&per_page=20`)

**GET /api/v1/teacher/students/{student_id}** — 학생 상세 + 성장 추이 + 교사 피드백

**GET /api/v1/teacher/risk-students** — 위험군 상세 (risk_types: `["all","pi","ui"]` 등)

**POST /api/v1/teacher/feedback** — 피드백 작성/수정
```json
// Request
{ "assignment_id": 5, "student_id": 3, "content": "UI 점수 개선이 필요합니다..." }
// Response
{ "id": 12, "created_at": "2025-03-20T10:30:00" }
```

**GET /api/v1/teacher/analytics/assignment/{assignment_id}** — 과제별 분석

**GET /api/v1/teacher/analytics/advanced** — 산점도, 상관관계 행렬

### 4.4 제출 + 작업 (비동기 흐름)

**POST /api/v1/submissions**
```json
// Request
{ "assignment_id": 5, "chatgpt_before": "...", "user_prompt": "...", "essay": "..." }
// Response 202
{ "submission_id": 10, "job_id": "550e8400-e29b-41d4-a716-446655440000", "status": "pending" }
```

**GET /api/v1/jobs/{job_uuid}/status** — 클라이언트가 3초마다 폴링
```json
{ "job_id": "550e8400-...", "status": "done", "metrics": { "aic": 71, "pi": 72, ... }, "error": null }
// status: "pending" | "running" | "done" | "failed"
```

### 4.5 파이프라인 내부 엔드포인트 (백엔드 → 파이프라인 전용)

**POST /analyze** (pipeline:9000, 외부 노출 없음)
```json
// Request
{
  "job_id": "550e8400-...",
  "submission": {
    "sample_id": "sub-10", "course": "CS101", "student_id": "student_001",
    "chatgpt_before": "...", "user": "...", "essay": "..."
  },
  "config": {
    "pi_weights": [0.4, 0.3, 0.3],
    "critical_keywords": ["however", "although", "why", "how", ...],
    "topic_score_alpha": 1.0, "topic_score_beta": 1.0,
    "backend_prefer": "sbert"
  }
}
// Response 200
{
  "job_id": "550e8400-...",
  "pi": 0.72, "ui": 0.68, "oi": 0.75, "aic": 0.71, "topic_score": 0.83,
  "weight_pi": 0.38, "weight_ui": 0.31, "weight_oi": 0.31,
  "pi_depth_tokens": 142, "pi_depth_norm": 0.68, "pi_critical_ratio": 0.12,
  "pi_avg_sent_len": 0.55, "pi_ttr": 0.71, "pi_complexity": 0.63,
  "ui_cos_similarity": 0.56, "ui_distance": 0.44, "ui_newinfo_ratio": 0.37,
  "oi_topic_score_raw": 0.83, "embedding_backend": "sbert"
}
```

---

## 5. 비동기 흐름 설계

```
학생 에세이 제출
    │
    ▼ POST /api/v1/submissions
백엔드: DB에 submission 저장
    │
    ▼ analysis_jobs 레코드 생성 (status=pending) → job_uuid 반환
    │
    ▼ asyncio.create_task(_run_pipeline(...))  ← 응답 즉시 반환, 대기 없음
    │
클라이언트: job_id 수신 → 3초마다 GET /jobs/{id}/status 폴링
    │
백그라운드 태스크:
    ├─ job.status = "running"
    ├─ POST http://pipeline:9000/analyze (동기적 대기)
    ├─ 결과 수신 → metrics 테이블 저장
    └─ job.status = "done"
    │
클라이언트: status="done" 감지 → metrics 표시
```

**주의**: `_run_pipeline`은 새 DB 세션을 직접 열어야 한다. 요청 핸들러의 세션은 응답 발송 시 닫힌다.

---

## 6. 프론트엔드 (Vue 3 SPA)

### 프로젝트 생성
```bash
npm create vue@latest aic-frontend
# TypeScript: No, Router: Yes, Pinia: Yes, ESLint: Yes
npm install axios pinia-plugin-persistedstate chart.js
```

### 디렉토리 구조
```
aic-frontend/src/
├── main.js                    # import '@/assets/design-system.css'
├── App.vue                    # <RouterView /> 만
├── assets/
│   └── design-system.css      # 프로토타입 파일 완전 복사 (수정 금지)
├── router/index.js
├── stores/
│   ├── auth.js                # Pinia: user, accessToken, login/refresh/logout
│   ├── student.js             # Pinia: 학생 대시보드/과제 데이터
│   └── teacher.js             # Pinia: 교사 대시보드/학생 목록
├── api/index.js               # axios 인스턴스 + Bearer 인터셉터 + 401 자동 갱신
├── composables/
│   ├── useChart.js            # Chart.js 래퍼 (onUnmounted에서 destroy 필수)
│   └── useJobPoller.js        # 3초 폴링, status/metrics ref 반환
├── components/
│   ├── layout/
│   │   ├── AppLayout.vue      # 사이드바 + 헤더 + <slot>
│   │   ├── AppSidebar.vue     # 역할별 색상 + 네비 아이템
│   │   └── AppHeader.vue
│   ├── common/
│   │   ├── DonutChart.vue     # SVG 기반 (Chart.js 사용 금지)
│   │   ├── MetricBars.vue     # PI/UI/OI/TS 가로 막대 비교
│   │   ├── StatusBadge.vue    # Excellent/Good/Average/Risk
│   │   ├── KpiCard.vue        # 상단 컬러 테두리 카드
│   │   └── LoadingSkeleton.vue
│   └── charts/
│       ├── LineChart.vue      # Chart.js
│       ├── BarChart.vue       # Chart.js
│       ├── ScatterChart.vue   # Chart.js
│       └── RadarChart.vue     # Chart.js
└── views/
    ├── LandingView.vue
    ├── LoginView.vue
    ├── student/
    │   ├── StudentDashboardView.vue
    │   ├── StudentAssignmentView.vue
    │   ├── StudentGrowthView.vue
    │   └── StudentFeedbackView.vue
    └── teacher/
        ├── TeacherDashboardView.vue
        ├── TeacherStudentsView.vue
        ├── TeacherStudentDetailView.vue
        ├── TeacherRiskView.vue
        ├── TeacherAssignmentAnalyticsView.vue
        └── TeacherAdvancedView.vue
```

### 라우터 (`src/router/index.js`)
```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', component: () => import('@/views/LandingView.vue'), meta: { public: true } },
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  { path: '/student/dashboard', component: () => import('@/views/student/StudentDashboardView.vue'), meta: { role: 'student' } },
  { path: '/student/assignments', component: () => import('@/views/student/StudentAssignmentView.vue'), meta: { role: 'student' } },
  { path: '/student/assignments/:id', component: () => import('@/views/student/StudentAssignmentView.vue'), meta: { role: 'student' } },
  { path: '/student/growth', component: () => import('@/views/student/StudentGrowthView.vue'), meta: { role: 'student' } },
  { path: '/student/feedback/:assignmentId', component: () => import('@/views/student/StudentFeedbackView.vue'), meta: { role: 'student' } },
  { path: '/teacher/dashboard', component: () => import('@/views/teacher/TeacherDashboardView.vue'), meta: { role: 'teacher' } },
  { path: '/teacher/students', component: () => import('@/views/teacher/TeacherStudentsView.vue'), meta: { role: 'teacher' } },
  { path: '/teacher/students/:id', component: () => import('@/views/teacher/TeacherStudentDetailView.vue'), meta: { role: 'teacher' } },
  { path: '/teacher/risk', component: () => import('@/views/teacher/TeacherRiskView.vue'), meta: { role: 'teacher' } },
  { path: '/teacher/analytics/assignment/:id', component: () => import('@/views/teacher/TeacherAssignmentAnalyticsView.vue'), meta: { role: 'teacher' } },
  { path: '/teacher/advanced', component: () => import('@/views/teacher/TeacherAdvancedView.vue'), meta: { role: 'teacher' } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) return '/login'
  if (to.meta.role && auth.user?.role !== to.meta.role) return '/login'
})
```

### Axios 인터셉터 (`src/api/index.js`)
```javascript
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

export const api = axios.create({ baseURL: '/api/v1' })

api.interceptors.request.use(cfg => {
  const auth = useAuthStore()
  if (auth.accessToken) cfg.headers.Authorization = `Bearer ${auth.accessToken}`
  return cfg
})

let refreshing = false
api.interceptors.response.use(r => r, async err => {
  if (err.response?.status === 401 && !refreshing) {
    refreshing = true
    try {
      await useAuthStore().refresh()
      refreshing = false
      return api(err.config)
    } catch {
      refreshing = false
      useAuthStore().logout()
      window.location.href = '/login'
    }
  }
  return Promise.reject(err)
})
```

### Job Poller Composable (`src/composables/useJobPoller.js`)
```javascript
import { ref } from 'vue'
import { api } from '@/api'

export function useJobPoller() {
  const status = ref('idle')
  const metrics = ref(null)
  let intervalId = null

  async function startPolling(jobId) {
    status.value = 'pending'
    intervalId = setInterval(async () => {
      const { data } = await api.get(`/jobs/${jobId}/status`)
      status.value = data.status
      if (data.status === 'done') { metrics.value = data.metrics; clearInterval(intervalId) }
      else if (data.status === 'failed') clearInterval(intervalId)
    }, 3000)
  }

  function stop() { clearInterval(intervalId) }
  return { status, metrics, startPolling, stop }
}
```

---

## 7. 백엔드 (FastAPI)

### 디렉토리 구조
```
aic-backend/
├── Dockerfile
├── requirements.txt
└── app/
    ├── main.py                # FastAPI 앱 팩토리, CORS, 라우터 마운트
    ├── config.py              # pydantic-settings + 환경 변수
    ├── database.py            # SQLAlchemy async engine, SessionLocal, Base
    ├── models/db_models.py    # SQLAlchemy ORM 모델
    ├── schemas/               # Pydantic 요청/응답 스키마
    │   ├── auth.py
    │   ├── student.py
    │   ├── teacher.py
    │   └── submission.py
    ├── routers/               # 엔드포인트 정의
    │   ├── auth.py
    │   ├── student.py
    │   ├── teacher.py
    │   ├── submissions.py
    │   └── jobs.py
    ├── services/              # 비즈니스 로직
    │   ├── auth_service.py    # JWT encode/decode, bcrypt
    │   ├── student_service.py # 학생 뷰용 DB 쿼리
    │   ├── teacher_service.py # 교사 뷰용 DB 쿼리
    │   ├── job_service.py     # UUID 생성, asyncio.create_task, 상태 갱신
    │   └── pipeline_client.py # httpx 비동기 POST to pipeline
    └── dependencies.py        # get_db(), get_current_user(), require_role()
```

### `app/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, student, teacher, submissions, jobs

app = FastAPI(title="AIC Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://frontend"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/api/v1/auth")
app.include_router(student.router,     prefix="/api/v1/student")
app.include_router(teacher.router,     prefix="/api/v1/teacher")
app.include_router(submissions.router, prefix="/api/v1")
app.include_router(jobs.router,        prefix="/api/v1")
```

### `app/config.py`
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "mysql+aiomysql://aic_user:password@db:3306/aic_db"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PIPELINE_URL: str = "http://pipeline:9000"

    class Config:
        env_file = ".env"

settings = Settings()
```

### `app/database.py`
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(settings.DB_URL, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase): pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### `app/services/job_service.py` (비동기 작업 핵심)
```python
import uuid, asyncio
from app.database import AsyncSessionLocal
from app.models.db_models import AnalysisJob, Metrics
from app.services.pipeline_client import call_pipeline

async def create_and_dispatch_job(submission_id, submission_data, db):
    job_uuid = str(uuid.uuid4())
    job = AnalysisJob(job_uuid=job_uuid, submission_id=submission_id, status="pending")
    db.add(job)
    await db.commit()
    # 응답 직후 반환, 백그라운드에서 실행
    asyncio.create_task(_run_pipeline(job_uuid, submission_id, submission_data))
    return job_uuid

async def _run_pipeline(job_uuid, submission_id, data):
    # 새 DB 세션 필수 (요청 세션은 이미 닫힘)
    async with AsyncSessionLocal() as session:
        job = await session.execute(...)  # job_uuid로 조회
        job.status = "running"
        await session.commit()
        try:
            result = await call_pipeline(job_uuid, data)
            metrics = Metrics(submission_id=submission_id, **_scale_metrics(result))
            session.add(metrics)
            job.status = "done"
            await session.commit()
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            await session.commit()

def _scale_metrics(result):
    return {
        "pi_score": round(result["pi"] * 100),
        "ui_score": round(result["ui"] * 100),
        "oi_score": round(result["oi"] * 100),
        "aic_score": round(result["aic"] * 100),
        "topic_score": round(result["topic_score"] * 100),
        # float 세부 지표는 그대로
        **{k: result[k] for k in ["weight_pi","weight_ui","weight_oi",
           "pi_depth_tokens","pi_depth_norm","pi_critical_ratio","pi_avg_sent_len",
           "pi_ttr","pi_complexity","ui_cos_similarity","ui_distance",
           "ui_newinfo_ratio","oi_topic_score_raw","embedding_backend"]}
    }
```

### requirements.txt
```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy[asyncio]==2.0.30
aiomysql==0.2.0
pydantic-settings==2.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.27.0
```

---

## 8. 파이프라인 서버 (FastAPI 래퍼)

### 디렉토리 구조
```
aic-pipeline/
├── Dockerfile
├── requirements.txt
├── aic_pipeline.py            # 기존 파일 완전 복사 (절대 수정 금지)
└── app/
    ├── main.py
    ├── config.py
    ├── schemas.py             # AnalyzeRequest, AnalyzeResponse Pydantic 모델
    └── pipeline_runner.py     # aic_pipeline.py 함수 래핑
```

### `app/main.py`
```python
from fastapi import FastAPI
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.pipeline_runner import run_analysis, preload_model
import asyncio

app = FastAPI(title="AIC Pipeline", version="1.0")

@app.on_event("startup")
async def warmup():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, preload_model)  # 시작 시 SBERT 모델 로드

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    loop = asyncio.get_event_loop()
    # CPU 바운드 작업 → 스레드 풀에서 실행 (이벤트 루프 블로킹 방지)
    result = await loop.run_in_executor(None, run_analysis, request.dict())
    return result
```

### `app/pipeline_runner.py`
```python
import sys, numpy as np, pandas as pd
sys.path.insert(0, '/app')
from aic_pipeline import EmbeddingBackend, compute_PI, compute_UI_OI, fit_weights_and_aic, safe_text

_backend = None  # 모듈 수준 싱글턴

DEFAULT_KEYWORDS = [
    "however", "although", "because", "why", "how", "compare",
    "contrast", "analyze", "evaluate", "critique", "moreover",
    "therefore", "consequently", "alternatively", "nevertheless"
]

def preload_model():
    global _backend
    _backend = EmbeddingBackend(prefer="sbert", sbert_model="paraphrase-multilingual-mpnet-base-v2")
    _backend.fit(["warmup text"])

def run_analysis(payload: dict) -> dict:
    sub = payload["submission"]
    cfg = payload["config"]

    df = pd.DataFrame([{
        "sample_id": sub.get("sample_id", "x"),
        "course": sub.get("course", "default"),
        "student_id": sub.get("student_id", "x"),
        "chatgpt_before": safe_text(sub["chatgpt_before"]),
        "user": safe_text(sub["user"]),
        "essay": safe_text(sub["essay"]),
        "rating": np.nan,
    }])

    keywords = cfg.get("critical_keywords", DEFAULT_KEYWORDS)
    df = compute_PI(df, keywords, weights=cfg.get("pi_weights", [0.4, 0.3, 0.3]))

    pipeline_cfg = {"ui_oi": {
        "topic_score_alpha": cfg.get("topic_score_alpha", 1.0),
        "topic_score_beta": cfg.get("topic_score_beta", 1.0),
        "min_course_samples": 1,  # 단일 제출: global centroid 사용
    }}
    df = compute_UI_OI(df, _backend, pipeline_cfg)

    weights_cfg = {"weights": {"mode": "equal", "clip_negative": True, "min_ratings": 10, "n_folds": 5}}
    df, w = fit_weights_and_aic(df, weights_cfg)

    row = df.iloc[0]
    return {
        "job_id": payload["job_id"],
        "pi": float(row["PI"]), "ui": float(row["UI"]),
        "oi": float(row["OI"]), "aic": float(row["AIC"]),
        "topic_score": float(row["topic_score"]),
        "weight_pi": float(w[0]), "weight_ui": float(w[1]), "weight_oi": float(w[2]),
        "pi_depth_tokens": int(row["pi_depth_tokens"]),
        "pi_depth_norm": float(row["pi_depth_norm"]),
        "pi_critical_ratio": float(row["pi_critical_ratio"]),
        "pi_avg_sent_len": float(row["pi_avg_sent_len"]),
        "pi_ttr": float(row["pi_ttr"]),
        "pi_complexity": float(row["pi_complexity"]),
        "ui_cos_similarity": float(row["ui_cos_similarity"]),
        "ui_distance": float(row["ui_distance"]),
        "ui_newinfo_ratio": float(row["ui_newinfo_ratio"]),
        "oi_topic_score_raw": float(row["topic_score"]),
        "embedding_backend": _backend.kind,
    }
```

### requirements.txt
```
fastapi==0.111.0
uvicorn[standard]==0.29.0
pandas==2.2.2
numpy==1.26.4
scikit-learn==1.4.2
sentence-transformers==2.7.0
--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.3.0+cpu
pyyaml==6.0.1
pydantic==2.7.1
```

---

## 9. Docker 설정

### `docker-compose.yml`
```yaml
version: '3.9'

services:
  db:
    image: mysql:8.0
    container_name: aic_db
    restart: unless-stopped
    command: --default-authentication-plugin=mysql_native_password
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: aic_db
      MYSQL_USER: aic_user
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - aic_internal
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "aic_user", "--password=${MYSQL_PASSWORD}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./aic-backend
    container_name: aic_backend
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      DB_URL: mysql+aiomysql://aic_user:${MYSQL_PASSWORD}@db:3306/aic_db
      JWT_SECRET: ${JWT_SECRET}
      PIPELINE_URL: http://pipeline:9000
    networks:
      - aic_internal

  pipeline:
    build: ./aic-pipeline
    container_name: aic_pipeline
    restart: unless-stopped
    environment:
      TRANSFORMERS_CACHE: /app/models
    volumes:
      - model_cache:/app/models
    networks:
      - aic_internal

  frontend:
    build: ./aic-frontend
    container_name: aic_frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - aic_internal

networks:
  aic_internal:
    driver: bridge

volumes:
  mysql_data:
  model_cache:
```

### Frontend `nginx.conf`
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;  # SPA 라우팅 필수
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Frontend `Dockerfile`
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### Backend `Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Pipeline `Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 빌드 시점에 SBERT 모델 다운로드 (첫 요청 타임아웃 방지)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-mpnet-base-v2', cache_folder='/app/models')"
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000", "--workers", "1"]
```

### `.env` (절대 커밋 금지)
```
MYSQL_ROOT_PASSWORD=strongrootpass
MYSQL_PASSWORD=aicdbpassword
JWT_SECRET=최소32자이상랜덤문자열사용
```

---

## 10. 구현 순서

**Phase 1: DB + 백엔드 골격 (1-2일)**
1. `init.sql` 작성 (위 CREATE TABLE 전부)
2. SQLAlchemy ORM 모델 작성 (`db_models.py`)
3. `config.py`, `database.py` 구현
4. 인증: `auth_service.py` (JWT + bcrypt) + `routers/auth.py`
5. 시드 데이터: 교사 1명, 학생 5명, 수업 1개, 과제 3개

**Phase 2: 파이프라인 서버 (2-3일)**
1. `aic_pipeline.py` 원본 복사
2. `pipeline_runner.py` 구현 (`preload_model`, `run_analysis`)
3. `schemas.py` Pydantic 모델
4. `app/main.py` (startup warmup 포함)
5. Dockerfile (모델 빌드 시 다운로드)
6. 단독 테스트: `curl -X POST http://localhost:9000/analyze -d '...'`

**Phase 3: 백엔드 API (3-5일)**
1. `pipeline_client.py` (httpx 비동기 POST)
2. `job_service.py` (UUID, `asyncio.create_task`, 상태 갱신)
3. `routers/submissions.py` + `routers/jobs.py`
4. `services/student_service.py` (전체 DB 쿼리)
5. `services/teacher_service.py` (전체 DB 쿼리)
6. 나머지 라우터 전부 구현
7. curl/httpie로 전체 엔드포인트 검증

**Phase 4: 프론트엔드 (5-8일)**
1. Vue 프로젝트 생성, 패키지 설치
2. `design-system.css` 완전 복사 → `src/assets/`
3. `api/index.js` (axios + 인터셉터)
4. `stores/auth.js` + pinia-plugin-persistedstate
5. `router/index.js` (전체 경로 + 가드)
6. `AppLayout.vue`, `AppSidebar.vue`, `AppHeader.vue`
7. 공통 컴포넌트: `DonutChart.vue`(SVG), `StatusBadge.vue`, `KpiCard.vue`
8. `LoginView.vue` (투 패널 레이아웃, 프로토타입 동일)
9. 학생 뷰: Dashboard → Assignment → Growth → Feedback
10. 교사 뷰: Dashboard → Students → StudentDetail → Risk → AssignmentAnalytics → Advanced
11. `useJobPoller.js` 구현 + 제출 흐름에 연결

**Phase 5: Docker 통합 (9일)**
1. `docker-compose.yml` 작성
2. 전체 Dockerfile 작성
3. `nginx.conf` 작성
4. `docker compose up --build` + 스모크 테스트

---

## 11. 절대 해서는 안 되는 것 (Critical Constraints)

1. **AIC 공식 수정 금지**
   `AIC = w_pi × PI + w_ui × UI + w_oi × OI`
   `fit_weights_and_aic()` 함수를 수정하거나 공식을 변경하지 않는다.

2. **PI 공식 수정 금지**
   `PI = 0.4 × depth_norm + 0.3 × criticality + 0.3 × complexity`
   `compute_PI()` 함수 내부 가중치를 변경하지 않는다.

3. **디자인 시스템 색상 변경 금지**
   아래 CSS 변수는 어떤 Vue 컴포넌트에서도 재정의하지 않는다:
   - `--color-aic: #1E3A5F` (AIC Navy)
   - `--color-pi: #3B82F6` (PI Blue)
   - `--color-ui: #F97316` (UI Orange)
   - `--color-oi: #10B981` (OI Green)
   - `--color-topic: #8B5CF6` (Topic Purple)
   - `--bg-primary: #F0F4F8`

4. **Chart.js 교체 금지**
   라인, 막대, 산점도, 레이더 차트는 모두 Chart.js를 사용한다.
   AIC 도넛은 SVG 직접 구현 (프로토타입과 동일).

5. **파이프라인 포트 9000 외부 노출 금지**
   `docker-compose.yml`에서 pipeline의 `ports`를 절대 선언하지 않는다.

6. **SQLAlchemy 동기 세션을 FastAPI async 라우터에서 사용 금지**
   반드시 `sqlalchemy.ext.asyncio`의 `AsyncSession`만 사용한다.

7. **파이프라인 서버에 `--workers 2+` 금지**
   SBERT `_backend` 싱글턴이 프로세스당 하나여야 한다. `--workers 1` 고정.

8. **Vue 라우터 hash 모드 사용 금지**
   반드시 `createWebHistory()` 사용. nginx에 `try_files /index.html` 설정 필수.

9. **상태 배지 임계값 변경 금지**
   `>= 80 = Excellent`, `>= 65 = Good`, `>= 50 = Average`, `< 50 = Risk`

10. **폰트 변경 금지**
    Inter + Pretendard (Google Fonts CDN) 그대로 유지.

11. **`aic_pipeline.py` 수정 금지**
    파이프라인 원본 파일을 수정하지 않는다. 래퍼(`pipeline_runner.py`)에서 함수 호출만 한다.

---

## 12. 주의해야 할 함정 (Pitfalls)

### SBERT 모델 첫 실행 (1-3분 소요)
`paraphrase-multilingual-mpnet-base-v2` 모델은 약 420MB.
Dockerfile의 `RUN python -c "from sentence_transformers import SentenceTransformer; ..."` 명령으로 빌드 시 다운로드하지 않으면
첫 `/analyze` 요청에서 타임아웃 발생 → 작업 실패.
`TRANSFORMERS_CACHE=/app/models` 환경변수 + `model_cache` volume 마운트 필수.

### 단일 제출 정규화 문제
`minmax_norm()`은 단일 행 DataFrame에서 `max - min = 0`이라 모든 값을 `0.0`으로 반환한다.
이는 파이프라인의 알려진 동작. 해결책:
- 반 전체 데이터를 배치로 재분석하는 기능 나중에 추가
- MVP 단계에서는 단일 제출 모드 허용 + 사용자에게 점수가 반 기준 상대값임을 고지

### JWT 갱신 경쟁 상태
여러 API 요청이 동시에 401을 받으면 axios 인터셉터가 동시 갱신 시도 → 무한루프.
`refreshing` 플래그로 한 번만 갱신하도록 보장 (위 코드 참고).

### MySQL 8.0 인증 플러그인
`docker-compose.yml`에 `command: --default-authentication-plugin=mysql_native_password` 추가.
없으면 `aiomysql`이 조용히 연결 실패할 수 있다.

### asyncio.create_task DB 세션 수명
`_run_pipeline` 백그라운드 태스크는 요청 핸들러의 DB 세션을 재사용하면 안 된다.
요청 세션은 응답 발송 시 닫힌다. 반드시 `async with AsyncSessionLocal() as session:` 새로 열 것.

### `chatgpt_after` 컬럼 혼동 주의
CSV 원본에 `chatgpt_after` 컬럼이 있지만 파이프라인에서 사용하지 않는다.
계산에 쓰이는 것은 `chatgpt_before` (학생이 작업 기반으로 삼은 AI 응답).
컬럼 매핑: `CSV chatgpt_before → DB chatgpt_before`, `CSV user → DB user_prompt`, `CSV essay → DB essay`

### 교사/학생 사이드바 색상
- 학생 사이드바: `background: var(--bg-sidebar)` = `#1E3A5F`
- 교사 사이드바: `background: #1a2438` (별도 CSS 클래스로 override)
`--bg-sidebar` 변수를 #1E3A5F로 정의하고, 교사 레이아웃에서 `.sidebar--teacher { background: #1a2438; }` scoped 스타일 적용.

### Pinia 세션 유지
`pinia-plugin-persistedstate` 설치 + auth store에 `persist: true` 설정.
없으면 페이지 새로고침 시 로그인 상태 초기화.

### 위험군 배지 카운트 실시간 반영
교사 사이드바 "위험군 학생" 네비 아이템의 숫자 배지는
`useTeacherStore().riskCount`를 reactive하게 바인딩해야 한다.
대시보드 API의 `risk_count` 필드에서 값을 가져온다.

---

## 13. 검증 방법

### DB 검증
```sql
SHOW TABLES;
SELECT id, name, role FROM users;
SELECT id, class_code FROM classes;
```

### 파이프라인 단독 테스트
```bash
curl -X POST http://localhost:9000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "test-123",
    "submission": {
      "sample_id": "s1", "course": "CS101", "student_id": "stu1",
      "chatgpt_before": "The sky is blue.",
      "user": "Why is the sky blue and how does Rayleigh scattering work?",
      "essay": "The sky appears blue due to Rayleigh scattering of light by atmospheric particles."
    },
    "config": {"pi_weights": [0.4,0.3,0.3], "topic_score_alpha": 1.0, "topic_score_beta": 1.0}
  }'
# 기대값: pi, ui, oi, aic 모두 0.0~1.0 사이 float
```

### 백엔드 인증 테스트
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id":"student_001","password":"password123","role":"student"}'
# 기대값: {"access_token":"eyJ...","token_type":"bearer","user":{...}}
```

### 제출 + 폴링 흐름 테스트
```bash
TOKEN="eyJ..."
RESULT=$(curl -s -X POST http://localhost:8000/api/v1/submissions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assignment_id":1,"chatgpt_before":"AI text","user_prompt":"my q","essay":"my essay"}')
JOB_ID=$(echo $RESULT | python -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
sleep 30
curl "http://localhost:8000/api/v1/jobs/$JOB_ID/status" -H "Authorization: Bearer $TOKEN"
# 기대값: status="done", metrics 포함
```

### 프론트엔드 페이지 체크리스트
각 페이지에서 확인:
- [ ] 사이드바 역할별 배경색 정확 (학생=#1E3A5F, 교사=#1a2438)
- [ ] KPI 카드 상단 3px 컬러 테두리 (PI=파란색, UI=주황색, OI=초록색, AIC=네이비)
- [ ] Chart.js 차트 canvas 렌더링 (콘솔 오류 없음)
- [ ] AIC 도넛 차트 SVG stroke-dashoffset 애니메이션
- [ ] 상태 배지 색상 (Excellent=초록, Good=파랑, Average=노랑, Risk=빨강)
- [ ] 교사 위험군 페이지: 사이드바 배지 카운트 표시

### Docker 통합 테스트
```bash
docker compose up --build
# http://localhost 접속
# 학생 데모 로그인 → /student/dashboard 리다이렉트 확인
# 교사 데모 로그인 → /teacher/dashboard 리다이렉트 확인
# 과제 제출 → 폴링 → ~30초 내 "done" 확인
docker compose logs pipeline | grep -i "sbert\|model\|loaded"  # 시작 시 모델 로드 확인
```

---

## 14. 참조 파일 경로

| 파일 | 용도 |
|------|------|
| `이전프로젝트_코드구현/aic_pipeline.py` | 파이프라인 원본 (pipeline 컨테이너에 복사) |
| `프로토타입/design-system.css` | Vue `src/assets/`에 그대로 복사 |
| `프로토타입/common.js` | 사이드바 구조, 라우트명, 아이콘 SVG 참고 |
| `프로토타입/student-dashboard.html` | StudentDashboardView.vue 레이아웃 참고 |
| `프로토타입/teacher-dashboard.html` | TeacherDashboardView.vue 레이아웃 참고 |
| `프로토타입/student-assignment.html` | StudentAssignmentView.vue 참고 |
| `프로토타입/student-growth.html` | StudentGrowthView.vue 참고 |
| `프로토타입/student-feedback.html` | StudentFeedbackView.vue 참고 |
| `프로토타입/teacher-students.html` | TeacherStudentsView.vue 참고 |
| `프로토타입/teacher-student-detail.html` | TeacherStudentDetailView.vue 참고 |
| `프로토타입/teacher-risk.html` | TeacherRiskView.vue 참고 |
