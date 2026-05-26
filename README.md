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
