# Warehouse Validation

이 문서는 로컬 Docker Compose 환경에서 PostgreSQL warehouse와 일회성 ELT 작업을 검증하는 절차를 정리합니다. 실제 비밀번호나 로컬 `.env` 값은 기록하지 않습니다.

## 접속 정보

- VSCode DB 클라이언트 host: `localhost`
- Port: `5433`
- Database: `aic_warehouse`
- User: `warehouse_user`
- Password: 로컬 `.env`의 `WAREHOUSE_PASSWORD` 값

Docker 네트워크 내부에서는 ELT 서비스가 `warehouse:5432`로 접속합니다.

## 기본 실행

```powershell
docker compose up --build -d warehouse
docker compose ps warehouse
docker compose run --rm elt
```

`warehouse` 상태가 `healthy`이고 ELT가 `Validation: PASS`와 `ELT completed successfully.`를 출력하면 기본 기동, 적재, 변환, mart 집계 검증 경로가 정상입니다. 검증 실패 시 실패 항목과 원인을 출력하고 non-zero 종료 코드로 종료합니다.

## 통합 검증 스크립트

ELT를 다시 실행하지 않고 현재 운영 DB와 warehouse 상태만 검증하려면 같은 컨테이너 이미지의 검증 모듈을 실행합니다.

```powershell
docker compose run --rm elt python -m app.validate
```

이 명령은 다음 내용을 한 번에 확인합니다.

- 운영 DB `users/classes/assignments/submissions/metrics` row count와 warehouse `raw_*` row count 일치
- `raw_submissions`, `stg_submission_metrics`, `mart_student_assignment_metrics` row count 일치
- `mart_assignment_summary.submission_count`와 raw 과제별 제출 수 일치
- `mart_class_summary.submission_count`와 raw 클래스별 제출 수 일치

## ELT 실행 이력 확인

`docker compose run --rm elt`는 실행이 끝날 때마다 warehouse의 `elt_run_history`에 결과를 기록합니다. backend API나 관리자 화면을 통하지 않고 DB에서 직접 확인합니다.

최근 실행 5건:

```powershell
docker compose exec -T warehouse psql -U warehouse_user -d aic_warehouse -c "SELECT run_id, status, started_at, finished_at, duration_ms, error_message FROM elt_run_history ORDER BY started_at DESC LIMIT 5;"
```

마지막 성공 실행의 row count:

```powershell
docker compose exec -T warehouse psql -U warehouse_user -d aic_warehouse -c "SELECT run_id, raw_loaded_counts, source_counts, warehouse_counts FROM elt_run_history WHERE status = 'success' ORDER BY started_at DESC LIMIT 1;"
```

마지막 실패 실행의 검증 실패 목록과 오류 메시지:

```powershell
docker compose exec -T warehouse psql -U warehouse_user -d aic_warehouse -c "SELECT run_id, validation_failures, error_message FROM elt_run_history WHERE status = 'failed' ORDER BY started_at DESC LIMIT 1;"
```

`status='success'`이면 적재와 검증이 모두 통과한 실행입니다. `status='failed'`이면 `validation_failures` 또는 `error_message`를 먼저 확인합니다. 운영 DB나 warehouse 연결 자체가 불가능한 경우에는 이력 기록도 실패할 수 있으므로 컨테이너 로그를 함께 확인합니다.

## 호스트 Cron 주기 실행

EC2 같은 배포 서버에서는 cron이 repo 스크립트만 호출하게 둡니다. 스크립트는 repo root로 이동한 뒤 `docker compose run --rm elt`를 실행하고, 호스트 로그를 `logs/elt/elt-YYYYMMDDTHHMMSSZ.log`에 남깁니다. 성공/실패의 최종 운영 상태는 warehouse의 `elt_run_history`에서 확인합니다.

1회 수동 실행:

```bash
cd ~/Aic-WebArchitecture
bash scripts/run_elt_once.sh
```

prod compose 파일을 함께 쓰는 배포 서버에서 실행:

```bash
cd ~/Aic-WebArchitecture
AIC_ELT_USE_PROD_COMPOSE=1 bash scripts/run_elt_once.sh
```

매일 새벽 3시 UTC에 실행하는 cron 예시:

```bash
crontab -e
```

```cron
0 3 * * * cd /home/ubuntu/Aic-WebArchitecture && AIC_ELT_USE_PROD_COMPOSE=1 bash scripts/run_elt_once.sh
```

등록 확인:

```bash
crontab -l
```

cron 제거:

```bash
crontab -e
```

위 `scripts/run_elt_once.sh` 행을 삭제하고 저장합니다.

cron 자체 로그는 Ubuntu 기준 `/var/log/syslog`에서 확인할 수 있습니다.

```bash
grep CRON /var/log/syslog | tail -50
```

스크립트 실행 로그:

```bash
ls -lt logs/elt | head
tail -100 logs/elt/elt-YYYYMMDDTHHMMSSZ.log
```

## ELT Health Check

`scripts/check_elt_health.sh`는 warehouse의 `elt_run_history`를 조회해 두 조건을 확인합니다.

- 가장 최근 ELT run의 `status`가 `success`
- 마지막 성공 run이 25시간 이내

정상이면 exit code `0`, 비정상이면 non-zero로 종료합니다. 기본 freshness 기준은 `AIC_ELT_MAX_SUCCESS_AGE_HOURS`로 조정할 수 있습니다.

1회 수동 점검:

```bash
cd ~/Aic-WebArchitecture
AIC_ELT_USE_PROD_COMPOSE=1 bash scripts/check_elt_health.sh
```

Discord 실패 알림까지 포함해 점검:

```bash
cd ~/Aic-WebArchitecture
AIC_ELT_USE_PROD_COMPOSE=1 bash scripts/check_elt_health_and_notify.sh
```

`scripts/check_elt_health_and_notify.sh`는 health check 실패 시에만 `DISCORD_WEBHOOK_URL`로 Discord webhook을 호출합니다. 성공 시에는 알림을 보내지 않습니다. `DISCORD_WEBHOOK_URL`이 없으면 알림은 건너뛰고 원래 health check 실패 exit code를 그대로 반환합니다.

`.env`에 변수 이름만 추가하고 실제 webhook 값은 문서나 커밋에 기록하지 않습니다.

```dotenv
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

매일 새벽 3시 ELT 실행 후 3시 30분 UTC에 health check와 실패 알림을 실행하는 cron 예시:

```cron
0 3 * * * cd /home/ubuntu/Aic-WebArchitecture && AIC_ELT_USE_PROD_COMPOSE=1 bash scripts/run_elt_once.sh
30 3 * * * cd /home/ubuntu/Aic-WebArchitecture && AIC_ELT_USE_PROD_COMPOSE=1 bash scripts/check_elt_health_and_notify.sh >> logs/elt/health.log 2>&1
```

health check 로그 확인:

```bash
tail -100 logs/elt/health.log
```

## 수동 운영 DB Row Count

MySQL 컨테이너 내부의 환경 변수를 사용해 실행합니다.

```powershell
docker compose exec -T db sh -c "MYSQL_PWD=`$MYSQL_PASSWORD mysql -uaic_user aic_db -e 'SELECT (SELECT COUNT(1) FROM users) AS users_count, (SELECT COUNT(1) FROM classes) AS classes_count, (SELECT COUNT(1) FROM assignments) AS assignments_count, (SELECT COUNT(1) FROM submissions) AS submissions_count, (SELECT COUNT(1) FROM metrics) AS metrics_count'"
```

## 수동 Warehouse Raw/Staging/Mart Row Count

```powershell
docker compose exec -T warehouse psql -U warehouse_user -d aic_warehouse -c "SELECT 'raw_users' AS table_name, COUNT(*) AS row_count FROM raw_users UNION ALL SELECT 'raw_classes', COUNT(*) FROM raw_classes UNION ALL SELECT 'raw_assignments', COUNT(*) FROM raw_assignments UNION ALL SELECT 'raw_submissions', COUNT(*) FROM raw_submissions UNION ALL SELECT 'raw_metrics', COUNT(*) FROM raw_metrics UNION ALL SELECT 'stg_submission_metrics', COUNT(*) FROM stg_submission_metrics UNION ALL SELECT 'mart_student_assignment_metrics', COUNT(*) FROM mart_student_assignment_metrics UNION ALL SELECT 'mart_assignment_summary', COUNT(*) FROM mart_assignment_summary UNION ALL SELECT 'mart_class_summary', COUNT(*) FROM mart_class_summary;"
```

운영 DB의 `users`, `classes`, `assignments`, `submissions`, `metrics` 건수는 각각 warehouse의 `raw_users`, `raw_classes`, `raw_assignments`, `raw_submissions`, `raw_metrics`와 일치해야 합니다.

## 수동 Mart 집계 검증

과제별 제출 수:

```powershell
docker compose exec -T warehouse psql -U warehouse_user -d aic_warehouse -c "SELECT a.source_assignment_id, a.submission_count AS mart_count, r.raw_count FROM mart_assignment_summary a JOIN (SELECT source_assignment_id, COUNT(*) AS raw_count FROM raw_submissions GROUP BY source_assignment_id) r USING (source_assignment_id) ORDER BY a.source_assignment_id;"
```

클래스별 제출 수:

```powershell
docker compose exec -T warehouse psql -U warehouse_user -d aic_warehouse -c "SELECT c.source_class_id, c.submission_count AS mart_count, r.raw_count FROM mart_class_summary c JOIN (SELECT a.source_class_id, COUNT(*) AS raw_count FROM raw_submissions s JOIN raw_assignments a USING (source_assignment_id) GROUP BY a.source_class_id) r USING (source_class_id) ORDER BY c.source_class_id;"
```

`mart_count`와 `raw_count`가 모든 행에서 같아야 합니다.

## Volume 호환성 확인

`warehouse_data`가 PostgreSQL 데이터 디렉터리인지 확인합니다.

```powershell
docker volume ls
docker run --rm -v aic-webarchitecture_warehouse_data:/data postgres:16 bash -lc "ls -la /data | sed -n '1,40p'"
```

정상 PostgreSQL 볼륨에는 `PG_VERSION`, `base`, `global`, `pg_wal`, `postgresql.conf` 등이 보입니다. MySQL 데이터 디렉터리 흔적이 있거나 PostgreSQL 기동이 실패하면, 볼륨 재생성 전 데이터 손실 영향을 확인하고 사용자 승인을 받아야 합니다.

## 자주 발생하는 실패

- `WAREHOUSE_PASSWORD` 누락: `.env`에 변수 이름은 두되 실제 값은 문서나 커밋에 기록하지 않습니다.
- `warehouse` unhealthy: `docker compose logs warehouse`로 PostgreSQL 초기화 또는 인증 오류를 확인합니다.
- `elt` 연결 실패: `db`와 `warehouse`가 모두 healthy인지 먼저 확인합니다.
- `elt_run_history`에 실패 이력이 없는 실패: warehouse 연결 또는 인증 이전에 실패했을 수 있으므로 `docker compose run --rm elt` 출력과 `docker compose logs warehouse`를 함께 확인합니다.
- cron이 실행되지 않음: `crontab -l`의 경로가 실제 배포 경로와 같은지 확인하고, Docker 그룹 권한이 적용된 사용자 crontab에 등록했는지 확인합니다.
- health check 실패: `elt_run_history`의 최신 run 상태와 `logs/elt/health.log`를 먼저 확인합니다. 최신 run이 `failed`이면 `validation_failures`와 `error_message`를 확인하고, 마지막 성공이 25시간보다 오래됐으면 ELT cron 실행 여부를 확인합니다.
- Discord 알림 미전송: `DISCORD_WEBHOOK_URL`이 cron 실행 환경 또는 `.env`에 설정되어 있는지 확인합니다. `curl`이 설치되어 있지 않으면 health check exit code는 유지되지만 Discord 전송은 건너뜁니다.
- 기존 볼륨 충돌: `warehouse_data` 내부가 PostgreSQL 파일 구조인지 확인하고, 재생성이 필요하면 삭제 대상과 데이터 손실 가능성을 먼저 공유합니다.
- PowerShell 인용 문제: MySQL 비밀번호는 컨테이너 내부 환경 변수로 전달하고, `$`는 `` `$ ``처럼 이스케이프합니다.
