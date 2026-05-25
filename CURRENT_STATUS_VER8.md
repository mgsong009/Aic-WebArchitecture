# 현재 코드 현황 Ver.8 (최종 상세판)

작성일: 2026-05-22 (KST)
대상 폴더: `aic-web_ver4/`
기준 설계서: `ai-validated-dongarra.md`
문서 목적: **이 문서 하나로 현재 코드 구조·알고리즘·설정·검증 결과·품질 분석·디버깅 방법까지 파악 가능하도록 정리**

---

## 목차

1. 프로젝트 개요
2. 전체 아키텍처
3. 실제 디렉토리/코드 규모
4. 핵심 설정값 및 런타임 구성
5. 데이터베이스 스키마 및 시드 데이터
6. 백엔드 API 구현 현황
7. 프론트엔드 구현 현황
8. 분석 파이프라인 알고리즘 상세
9. 비동기 제출-분석 처리 흐름
10. 설계서 대비 구현 부합성 점검
11. 검증/실험(스모크) 결과
12. 코드 품질 분석 (강점/리스크)
13. 디버깅 진입점 가이드
14. 실행 및 운영 가이드 (아주 구체적)
15. 개선 로드맵 (우선순위)
16. 결론

---

## 1. 프로젝트 개요

본 저장소는 AIC 플랫폼의 프로토타입 UI/UX를 유지하면서, 다음 4개 서비스 구조로 구현된 웹 시스템이다.

- Frontend: Vue 3 SPA (`aic-frontend`)
- Backend: FastAPI (`aic-backend`)
- Analysis Pipeline: FastAPI + Python 분석 모듈 래퍼 (`aic-pipeline`)
- DB: MySQL 8.0 (`init.sql`)

Ver.8 기준 핵심 상태:

- 구조 목표(4서버 분리, 비동기 제출-분석, Docker 배포)는 유지
- 보안/권한 검증(P0) 보강 완료
- 파이프라인 startup 복원력(P0) 보강 완료
- 백엔드 재시작 복구(P1) 및 프론트 토큰 갱신 동시성(P1) 보강 완료
- Docker 재현성/환경변수 검증(P2) 보강 완료

---

## 2. 전체 아키텍처

```text
Browser
  ↓ HTTP :80
frontend (nginx)
  - Vue dist 정적 서빙
  - /api/* -> backend:8000 프록시
  ↓ internal network
backend (FastAPI)
  - 인증/JWT
  - 학생/교사 API
  - 제출 수신 + 비동기 job dispatch
  - pipeline:9000 호출
  - startup 시 incomplete job recovery
  ↙                          ↘
db (MySQL 8.0)              pipeline (FastAPI wrapper)
  - users/classes/...         - /analyze
  - submissions/metrics       - aic_pipeline.py 호출
  - analysis_jobs             - SBERT/TFIDF 임베딩 처리
```

네트워크/노출 정책:

- 외부 공개 포트: `frontend`의 `80:80`만 공개
- `backend`, `pipeline`, `db`는 내부 네트워크 통신
- 파이프라인 포트 `9000` 외부 미노출

---

## 3. 실제 디렉토리/코드 규모

### 3.1 루트 구성

- `aic-backend/`
- `aic-frontend/`
- `aic-pipeline/`
- `프로토타입/`
- `이전프로젝트_코드구현/`
- `입력데이터/`
- `scripts/` (Ver.8 추가: env 검증)
- `docker-compose.yml`, `init.sql`, `.env.example`

### 3.2 핵심 파일 줄 수 (Ver.8 실측)

#### Backend

| 파일 | 줄 수 | 역할 |
|---|---:|---|
| `aic-backend/app/main.py` | 26 | FastAPI 엔트리 + startup recovery |
| `aic-backend/app/models/db_models.py` | 122 | ORM 모델 정의 |
| `aic-backend/app/routers/auth.py` | 68 | 로그인/리프레시/로그아웃 |
| `aic-backend/app/routers/student.py` | 205 | 학생 API |
| `aic-backend/app/routers/teacher.py` | 279 | 교사 API + 권한 강화 |
| `aic-backend/app/routers/submissions.py` | 53 | 제출 API + 소속 검증 |
| `aic-backend/app/routers/jobs.py` | 48 | job 상태 API + 접근 검증 |
| `aic-backend/app/services/job_service.py` | 133 | job 생성/실행/recovery |
| `aic-backend/app/services/student_service.py` | 87 | 학생 조회 로직 |
| `aic-backend/app/services/teacher_service.py` | 145 | 교사 조회/집계 로직 |

#### Pipeline

| 파일 | 줄 수 | 역할 |
|---|---:|---|
| `aic-pipeline/app/main.py` | 24 | pipeline 엔트리 + startup 예외 완화 |
| `aic-pipeline/app/pipeline_runner.py` | 97 | 분석 래퍼 + fallback |
| `aic-pipeline/aic_pipeline.py` | 874 | 핵심 분석 엔진 |

#### Frontend

| 파일 | 줄 수 | 역할 |
|---|---:|---|
| `aic-frontend/src/views/student/StudentDashboardView.vue` | 285 | 학생 대시보드 |
| `aic-frontend/src/views/student/StudentAssignmentDetailView.vue` | 188 | 과제 상세/제출/폴링 |
| `aic-frontend/src/views/teacher/TeacherDashboardView.vue` | 154 | 교사 대시보드 |
| `aic-frontend/src/views/teacher/TeacherStudentsView.vue` | 155 | 학생 목록/필터 |
| `aic-frontend/src/views/teacher/TeacherStudentDetailView.vue` | 174 | 학생 상세/피드백 |
| `aic-frontend/src/components/layout/AppSidebar.vue` | 173 | 역할별 사이드바 |
| `aic-frontend/src/api/index.js` | 53 | axios 인터셉터/401 동시성 제어 |
| `aic-frontend/src/composables/useJobPoller.js` | 34 | job polling |

---

## 4. 핵심 설정값 및 런타임 구성

### 4.1 Docker Compose

파일: `docker-compose.yml`

- `version` 키 제거 (obsolete 경고 대응)
- `db`: mysql 8.0, healthcheck 유지
- `pipeline`: `TRANSFORMERS_CACHE=/app/models`
- `backend`: `DB_URL`, `JWT_SECRET`, `PIPELINE_URL`
- `frontend`: `80:80` 공개

### 4.2 환경변수

파일: `.env.example`

- `MYSQL_ROOT_PASSWORD`
- `MYSQL_PASSWORD`
- `JWT_SECRET`

주의:

- 예시값은 placeholder이며 그대로 운영 불가
- Ver.8에서 env 검증 스크립트 추가됨

### 4.3 백엔드 런타임 설정

파일: `aic-backend/app/config.py`

- `ACCESS_TOKEN_EXPIRE_MINUTES = 30`
- `REFRESH_TOKEN_EXPIRE_DAYS = 7`
- `PIPELINE_URL = http://pipeline:9000`
- `COOKIE_SECURE = False` (환경별 조정)
- `JWT_SECRET` validator:
  - 32자 미만 차단
  - placeholder 텍스트 포함 차단

### 4.4 실행 전 검증 스크립트 (Ver.8 추가)

- `scripts/check_env.py`
- `scripts/check_env.ps1`

검증 항목:

- 필수 키 존재 여부
- 최소 길이 (JWT 32+, DB 패스워드 12+)
- 문자열 복잡도 (영문/숫자/특수문자 조합)
- placeholder 패턴 포함 여부

---

## 5. 데이터베이스 스키마 및 시드 데이터

파일: `init.sql`

### 5.1 주요 테이블

- `users`
- `classes`
- `class_enrollments`
- `assignments`
- `submissions`
- `metrics`
- `analysis_jobs`
- `teacher_feedback`

### 5.2 관계 핵심

- 학생/교사 단일 `users` + `role` 분기
- 제출 unique: `(assignment_id, student_id)`
- metric unique: `submission_id`
- job 테이블: `analysis_jobs(job_uuid, submission_id, status)`

### 5.3 시드 데이터

- 교사 1명: `teacher_kim`
- 학생 10명: `student_001` ~ `student_010`
- 과제 5개
- 제출/metrics/피드백 샘플 데이터 포함

---

## 6. 백엔드 API 구현 현황

### 6.1 엔드포인트 개수

- 총 17개 (`@router.get/post` 기준 실측)

### 6.2 인증 API (`/api/v1/auth`)

- `POST /login`
- `POST /refresh`
- `POST /logout`

Ver.8 변경:

- refresh cookie에 `secure=settings.COOKIE_SECURE` 적용 가능

### 6.3 학생 API (`/api/v1/student`)

- `GET /dashboard`
- `GET /assignments`
- `GET /assignments/{assignment_id}`
- `GET /growth`
- `GET /feedback/{assignment_id}`

### 6.4 교사 API (`/api/v1/teacher`)

- `GET /dashboard`
- `GET /students`
- `GET /students/{student_id}`
- `GET /risk-students`
- `POST /feedback`
- `GET /analytics/assignment/{assignment_id}`
- `GET /analytics/advanced`

Ver.8 변경:

- `feedback`, `assignment analytics`에 담당 클래스 소유권 검증 추가
- `students` 목록에서 submission count N+1 제거

### 6.5 제출/잡 API (`/api/v1`)

- `POST /submissions`
- `GET /jobs/{job_uuid}/status`

Ver.8 변경:

- 제출 시 학생-과제 소속 검증 추가
- job status 조회 시 학생/교사 권한 검증 강화

---

## 7. 프론트엔드 구현 현황

### 7.1 라우팅/상태관리

- 학생/교사 역할별 라우트 분리 유지
- Pinia 기반 auth/student/teacher store 유지

### 7.2 API 인터셉터

파일: `aic-frontend/src/api/index.js`

기존:

- 401 시 refresh 1회 시도

Ver.8:

- refresh Promise 공유 방식 적용
- 동시 401 요청에서 refresh 중복 호출 방지
- 재시도 루프 방지 플래그(`_retry`) 추가

### 7.3 디자인 시스템 일치

- `프로토타입/design-system.css`와 `aic-frontend/src/assets/design-system.css` SHA256 동일
- 디자인 토큰/상태 배지 기준 유지

---

## 8. 분석 파이프라인 알고리즘 상세

### 8.1 알고리즘 정의 (유지)

- `PI = w1*Depth + w2*Criticality + w3*Complexity`
- `UI = (Distance * NewInfo) * TopicScore^alpha`
- `OI = (1 - TopicScore) * TopicScore^beta`
- `AIC`는 현재 `equal` 모드 중심 산출

### 8.2 Ver.8 가동성 보강

1. startup preload 실패가 앱 기동 전체 실패로 이어지지 않도록 처리
2. SBERT 실패 시 TF-IDF fallback 강제
3. 로그 문자열 ASCII 안전화 (Windows 콘솔 인코딩 오류 방지)
4. `run_analysis` 실패 메시지에 embedding backend 정보 포함

### 8.3 코드 동일성/변경성 판단

- 디자인 CSS는 해시 동일
- `aic_pipeline.py`는 Ver.8에서 로그 안전성 개선이 반영되어 이전 해시와 다름
- 알고리즘 수식/핵심 계산 경로는 유지

---

## 9. 비동기 제출-분석 처리 흐름

```text
[학생 화면]
POST /api/v1/submissions
  -> 제출 upsert
  -> analysis_jobs 생성(status=pending)
  -> asyncio.create_task(_run_pipeline)
  -> 202 + job_uuid 반환

[백엔드 startup]
recover_incomplete_jobs()
  -> pending/running 재큐잉

[프론트]
GET /api/v1/jobs/{job_uuid}/status polling
  -> done / failed 시 종료
```

Ver.8 보강 포인트:

- 프로세스 재시작 후 incomplete job 복구 경로 추가
- recovery 실패가 서버 전체 startup 실패로 전파되지 않도록 보호

---

## 10. 설계서 대비 구현 부합성 점검

| 목표 | Ver.8 판정 | 근거 |
|---|---|---|
| 4서버 분리 | 강하게 부합 | compose 4서비스 유지 |
| 프로토타입 스타일 유지 | 강하게 부합 | design-system 해시 동일 |
| 비동기 제출-분석 | 부합 | create_task + polling + recovery |
| 지정 스택(Vue/FastAPI/MySQL/Python) | 부합 | 실제 코드/의존성 확인 |
| 운영 안전성 | Ver.7 대비 개선 | 권한 검증, fallback, env validation 추가 |

---

## 11. 검증/실험(스모크) 결과

실행 일시: 2026-05-22 (KST)

### 11.1 성공 항목

1. 프론트 빌드
- `npm run build` 성공

2. 백엔드 health
- FastAPI TestClient로 `/health` 응답 `200 {"status":"ok"}`

3. 파이프라인 health
- startup 포함 health 확인 성공

4. SBERT 실패 시 fallback 검증
- SBERT 강제 실패 시 `_backend.kind == "tfidf"` 확인

5. 컴파일 점검
- backend/pipeline `python -m compileall` 성공

6. compose 파싱
- `docker compose config` 성공 (`version` obsolete 경고 제거)

### 11.2 의도된 실패 항목

- `scripts/check_env.ps1`는 현재 `.env` placeholder 상태에서 실패
- 보안 가드 정상 동작으로 판단

---

## 12. 코드 품질 분석 (강점/리스크)

### 12.1 강점

1. 보안 경계 강화
- job/status, submissions, teacher analytics/feedback 권한 검증 보강

2. 가동 복원력 향상
- pipeline fallback
- backend job recovery

3. 프론트 인증 흐름 안정화
- 401 동시성 제어로 refresh race 완화

4. 운영 재현성 향상
- `npm ci`, env validator, compose 정리

### 12.2 잔여 리스크

1. `asyncio.create_task` 기반 한계
- 단일 프로세스 수준의 복구로 충분하지 않을 수 있음
- 대규모 운영은 큐 워커 분리 권장

2. `.env` 관리
- 문서대로 강한 값을 직접 관리해야 함
- secrets manager 부재

3. pipeline 모델 다운로드 정책
- 네트워크 제한 환경에서 SBERT warmup은 실패 가능
- fallback으로 기능 유지되지만 결과 특성이 달라질 수 있음

---

## 13. 디버깅 진입점 가이드

### 13.1 로그인 실패

1. `.env`의 `JWT_SECRET` 유효성 확인
2. `scripts/check_env.ps1` 통과 여부 확인
3. 시드 계정/비번 확인 (`teacher_kim`, `student_001`)

### 13.2 제출은 되는데 job이 안 끝나는 경우

1. `analysis_jobs.status`가 `running`으로 전환되는지 확인
2. backend 로그에서 pipeline 호출 에러 확인
3. pipeline 로그에서 fallback 여부 확인

### 13.3 특정 job 조회가 404인 경우

1. 의도된 권한 차단인지 확인
2. 학생은 본인 job만, 교사는 담당 클래스 job만 허용됨

### 13.4 교사 학생목록 응답 이슈

1. 집계 쿼리 결과 확인
2. 대량 데이터에서 DB 인덱스 상태 확인

### 13.5 startup 직후 장애

1. backend startup recovery 로그 확인
2. pipeline preload 실패 로그 확인
3. `/health` 응답 가능 여부 우선 확인

---

## 14. 실행 및 운영 가이드 (아주 구체적)

아래는 Windows PowerShell 기준이다.

### 14.1 1단계: 루트 이동

```powershell
cd "d:\04_Work\02_오픈소스프로젝트\AIC-WEBARCHITECTURE"
```

### 14.2 2단계: 도구 설치 확인

```powershell
docker compose version
npm --version
```

확인 기준:
- 두 명령 모두 버전 문자열 출력

### 14.3 3단계: `.env` 실제값 입력

```powershell
notepad .env
```

예시(직접 변경 권장):

```env
MYSQL_ROOT_PASSWORD=R00tDb_2026_SecureA
MYSQL_PASSWORD=AppDb_2026_SecureB
JWT_SECRET=Qx9Vk2nM7pL4zT8yR1uW6eC3hA5xN2mK
```

규칙:
- JWT_SECRET 32자 이상
- placeholder 문자열 금지
- 영문/숫자/특수문자 혼합

### 14.4 4단계: env 검증

```powershell
.\scripts\check_env.ps1
```

정상:
- `[env-check] OK: ...\.env`

실패:
- 출력된 항목 수정 후 재검증

### 14.5 5단계: 컨테이너 빌드

```powershell
docker compose build --no-cache
```

### 14.6 6단계: 컨테이너 기동

```powershell
docker compose up -d
```

### 14.7 7단계: 상태 확인

```powershell
docker compose ps
```

정상 기대:
- `aic_db`
- `aic_pipeline`
- `aic_backend`
- `aic_frontend`
모두 Up

### 14.8 8단계: 헬스체크

1. 프론트 접속
- 브라우저: `http://localhost/`

2. 백엔드 health

```powershell
curl http://localhost/health
```

3. 파이프라인 health (컨테이너 내부)

```powershell
docker compose exec pipeline sh -lc "wget -qO- http://127.0.0.1:9000/health"
```

### 14.9 9단계: 로그인/기능 점검

- 교사: `teacher_kim / password123`
- 학생: `student_001 / password123`

점검 시나리오:

1. 학생 로그인
2. 과제 상세 진입 후 제출
3. job polling 완료 확인
4. 지표 렌더링 확인
5. 교사 로그인 후 대시보드/학생목록/분석 확인

### 14.10 10단계: 운영 명령

재시작:

```powershell
docker compose restart
```

중지:

```powershell
docker compose down
```

DB/캐시 포함 초기화:

```powershell
docker compose down -v
```

주의:
- `-v`는 데이터 영구 삭제

---

## 15. 개선 로드맵 (우선순위)

### Phase 1 (완료: Ver.8 반영)

- job status 권한 검증
- submissions 소속 검증
- teacher analytics/feedback 클래스 검증
- pipeline startup/fallback 안정화
- backend startup recovery
- refresh 동시성 제어
- N+1 개선, `npm ci`, env validator

### Phase 2 (권장)

1. 백그라운드 작업을 큐 워커로 분리
2. 비밀정보 관리(Secrets Manager) 도입
3. recovery/job 상태 전이 모니터링 지표 추가

### Phase 3 (품질 자동화)

1. 권한 회귀 테스트 자동화
2. 제출-분석 E2E 테스트 자동화
3. 오프라인 fallback 성능/정확도 회귀 테스트

---

## 16. 결론

Ver.8은 Ver.7 대비 핵심 리스크(P0/P1/P2)를 실제 코드에 반영한 **운영 준비형 상태**다.

실행 관점 결론:

- 코드 자체: 실행 준비 완료
- 필수 선행조건: `.env`를 placeholder에서 실제 강한 값으로 교체
- 이 선행조건 충족 시: 로컬/데모 운영을 수월하게 진행 가능
