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

## 기존 DB 볼륨의 분석 품질 메타데이터 보정

`mysql_data` 볼륨이 이미 생성된 환경에서는 `init.sql`이 다시 실행되지 않습니다. `/admin/analysis-quality`에서 최신 실행이 404로 조회되면 아래 명령을 1회 실행해 데모용 집계 메타데이터를 보정합니다. 원문, 프롬프트, 개인정보는 추가 저장하지 않고 기존 submission 5번의 metric에 연결되는 실행 집계만 추가합니다.

```powershell
Get-Content scripts/seed_analysis_quality_metadata.sql |
  docker-compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_PASSWORD" mysql -uaic_user aic_db'
```
