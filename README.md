# AIC Web Ver4

## 구성
- aic-frontend (Vue)
- aic-backend (FastAPI)
- aic-pipeline (FastAPI + 분석)
- MySQL (init.sql)

## 실행 (Docker)
1. 루트에 .env 생성 (.env.example 참고)
2. 로컬 개발/확인: `docker compose up --build`
3. AWS HTTPS 배포: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d`

## AWS 데모 배포
- EC2 단일 인스턴스 Docker Compose 배포 절차: [docs/AWS_EC2_DEMO_DEPLOY.md](docs/AWS_EC2_DEMO_DEPLOY.md)

## 주요 문서
- CURRENT_STATUS_VER8.md
- ai-validated-dongarra.md

## 관리자 계정 로그인
- admin / admin1234

## 분석 품질 baseline 기록

`/admin/analysis-quality`의 전/후 비교는 synthetic seed가 아니라 최적화 전 pipeline runner에서 측정한 baseline 메타데이터를 사용합니다. 분석 job이 실행될 때 같은 submission의 baseline이 없으면 backend가 pipeline의 `/analyze-baseline`을 먼저 호출해 `before_project/aic_pipeline.py` 실측 runtime, memory, PI/UI/OI/AIC score를 `analysis_run_metadata`에 저장하고, 이어서 현재 최적화 pipeline 분석 결과와 비교합니다. 원문, 프롬프트, 개인정보는 baseline metadata에 추가 저장하지 않습니다.

기존 DB 볼륨에는 먼저 `analysis_run_metadata.baseline_scores` 컬럼을 추가해야 합니다.

```sql
ALTER TABLE analysis_run_metadata ADD COLUMN baseline_scores JSON AFTER memory_delta_pct;
```

```powershell
python scripts/record_analysis_quality_baseline.py `
  --submission-id 5 `
  --pipeline-url http://localhost:9000 `
  --baseline-version pre-optimization-pipeline
```

`scripts/seed_analysis_quality_metadata.sql`은 수동 UI 데모 전용이며 자동 배포에서는 실행하지 않습니다.
