# AIC Web Ver4

## 구성
- aic-frontend (Vue)
- aic-backend (FastAPI)
- aic-pipeline (FastAPI + 분석)
- MySQL (운영 DB, init.sql)
- PostgreSQL (분석 warehouse)

## 실행 (Docker)
1. 루트에 .env 생성 (.env.example 참고)
2. 로컬 개발/확인: `docker compose up --build`
3. 분석 warehouse 적재/변환: `docker compose run --rm elt`
4. AWS HTTPS 배포: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d`

## ELT / Warehouse
- `warehouse`는 운영 DB와 분리된 PostgreSQL 서비스이며 내부 Docker 네트워크에서만 접근합니다.
- 로컬 개발 기본 override에서는 VSCode DB 클라이언트 확인을 위해 `localhost:5433`으로 warehouse PostgreSQL에 접속할 수 있습니다.
- `elt`는 `docker compose run --rm elt`로 실행되는 일회성 작업입니다. 운영 MySQL DB에서 데이터를 읽어 PostgreSQL warehouse의 raw, staging, mart 테이블로 upsert합니다.
- ELT는 실행 말미에 source/raw/staging/mart row count와 mart 집계 정합성을 검증하고, 실패 시 non-zero 종료 코드로 종료합니다.
- ELT 실행 결과는 warehouse의 `elt_run_history`에 기록되며, 마지막 성공/실패 상태와 row count는 SQL로 확인합니다.
- ELT 없이 현재 warehouse 상태만 검증하려면 `docker compose run --rm elt python -m app.validate`를 실행합니다.
- 배포 서버에서 주기 실행할 때는 cron이 `scripts/run_elt_once.sh`를 호출하도록 설정합니다.
- cron health check는 `scripts/check_elt_health.sh`로 최근 성공 freshness와 최신 run 상태를 확인합니다.
- Discord 실패 알림은 `scripts/check_elt_health_and_notify.sh`와 `DISCORD_WEBHOOK_URL`로 선택적으로 연결합니다.
- `.env`에는 `WAREHOUSE_PASSWORD` 값을 추가해야 합니다. 실제 비밀값은 커밋하지 않습니다.
- VSCode 접속 정보: host `localhost`, port `5433`, database `aic_warehouse`, user `warehouse_user`, password는 로컬 `.env`의 `WAREHOUSE_PASSWORD` 값입니다.
- 생성 테이블: `raw_users`, `raw_classes`, `raw_assignments`, `raw_submissions`, `raw_metrics`, `stg_submission_metrics`, `mart_student_assignment_metrics`, `mart_assignment_summary`, `mart_class_summary`
- 상세 검증 절차와 문제 해결 메모: [docs/WAREHOUSE_VALIDATION.md](docs/WAREHOUSE_VALIDATION.md)
- 기본 검증은 `docker compose run --rm elt python -m app.validate` 명령을 사용합니다.

## AWS 데모 배포
- EC2 단일 인스턴스 Docker Compose 배포 절차: [docs/AWS_EC2_DEMO_DEPLOY.md](docs/AWS_EC2_DEMO_DEPLOY.md)

## 주요 문서
- CURRENT_STATUS_VER8.md
- ai-validated-dongarra.md

## 관리자 계정 로그인
- admin / admin1234
