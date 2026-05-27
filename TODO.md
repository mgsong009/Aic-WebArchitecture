# TODO

이 파일은 앞으로 진행할 프로젝트 작업을 기록합니다. 각 항목은 간결하고 실행 가능하게 작성하며, `AGENTS.md`의 서비스 경계와 운영 규칙을 따릅니다.

## 운영 규칙

- 의미 있는 변경을 시작하기 전에 작업 항목을 먼저 추가합니다.
- 한 행에는 하나의 작업만 기록하고, 담당 영역과 완료 기준을 명확히 적습니다.
- 완료된 작업은 이 파일에 남겨두지 않고 `LOG.md`로 옮깁니다.
- 코드 동작과 문서화된 규칙이 달라지면 관련 서비스 문서도 함께 갱신합니다.
- 비밀값, 실제 인증 정보, 로컬 `.env` 값, 비공개 배포 정보는 기록하지 않습니다.

## 상태 값

| 상태 | 의미 |
| --- | --- |
| `Backlog` | 아직 시작하지 않은 작업입니다. |
| `Ready` | 바로 시작할 수 있을 만큼 명확한 작업입니다. |
| `In Progress` | 현재 진행 중인 작업입니다. |
| `Blocked` | 결정, 의존성, 외부 이슈 때문에 대기 중인 작업입니다. |

## 우선순위 값

| 우선순위 | 의미 |
| --- | --- |
| `P0` | 긴급한 운영 영향 이슈 또는 릴리스 차단 작업입니다. |
| `P1` | 중요한 사용자 영향 작업 또는 여러 서비스에 걸친 작업입니다. |
| `P2` | 유용한 개선, 정리, 낮은 위험도의 수정 작업입니다. |
| `P3` | 나중에 검토할 아이디어 또는 선택적인 개선입니다. |

## 참고 기준

- 기준 사이트: https://genspark.genspark.site/api/code_sandbox_light/preview/c66a59ad-6a9b-45f6-bda6-5cbf0f5ea36d/index.html
- 목표: 참고 사이트의 12개 HTML 화면을 `aic-frontend` Vue 라우트에서 최대한 동일하게 재현합니다.
- 기준 화면: `index.html`, `login.html`, `student-dashboard.html`, `student-assignment.html`, `student-growth.html`, `student-feedback.html`, `teacher-dashboard.html`, `teacher-students.html`, `teacher-student-detail.html`, `teacher-risk.html`, `teacher-assignment-analytics.html`, `teacher-advanced.html`.
- 동일성 기준: 화면 구조, 섹션 순서, 색상, 카드/버튼/배지 스타일, 여백, 타이포그래피, 차트 배치, 사이드바/헤더 구성을 reference와 맞춥니다.
- 구현 원칙: 정적 HTML을 그대로 배포하지 않고 Vue 3 SFC, Pinia, Vue Router, 기존 Axios API 경계를 유지하며 reference를 화면별로 이식합니다.

## 작업 목록

| 영역 | 우선순위 | 상태 | 작업 | 완료 기준 | 비고 |
| --- | --- | --- | --- | --- | --- |
| Backend/Frontend/Pipeline | P1 | Ready | 관리자 `AIC 분석 품질 모니터` 측정 방식을 실제 품질 검증 기준으로 보정 | `analysis_runs`가 단일 제출 고정값이 아니라 최근 분석 실행의 실제 처리 수·유효 수·성공률을 저장/반환하고, `processedRows`, `validRows`, `successRate`가 분석 job/metric 결과 기반으로 계산됨 | 현재 `processed_rows=1`, `valid_rows=1`, `success_rate=100.0` 고정값은 운영 품질 KPI로 부적절함 |
| Backend/DB | P1 | Ready | `Data Health` 지표를 제출/분석 데이터 집계 기반으로 계산 | 결측 데이터, 중복 제출, 텍스트 길이 이상치, metric null 비율, 분석 실패 수, fallback 사용률 등이 `submissions`, `metrics`, `analysis_jobs`, `analysis_runs` 실제 데이터에서 계산되고 `data_health` JSON 및 API 응답에 반영됨 | 현재 `duplicateRows=0`, `ratingCoverage=0.0`, `lowSampleCourses=0` 등 고정값 제거 필요 |
| Pipeline/Backend | P1 | Ready | 파이프라인 단계별 런타임을 추정 비율이 아닌 실제 계측값으로 저장 | `PI`, `Embedding`, `UI/OI`, `AIC fit`, `Validation`, `Save` 등 단계별 seconds가 실제 코드 실행 시간으로 측정되어 pipeline 응답 또는 backend 저장 경로를 통해 `pipeline_steps`에 기록됨 | 현재 전체 pipeline 시간을 15/55/25%로 나누는 추정값 사용 중 |
| Frontend | P2 | Ready | 분석 품질 화면의 가짜 표시 산식과 고정 경고 문구 제거 | `DataHealthCard.vue`의 `rating 결측 {{ dataHealth.missingRows * 2 + 591 }}건` 같은 화면 산식이 제거되고, 백엔드가 제공한 실제 수치/상태만 표시하며, `PipelineStepper` 경고 문구가 실제 warning 사유를 기반으로 렌더링됨 | 프론트가 품질 값을 임의 생성하지 않도록 정리 |
| Backend/Frontend | P2 | Ready | `latest analysis run`의 대표 범위와 라벨을 명확화 | 최신 run이 단일 제출인지 과제/코스 단위 batch인지 API 응답에 `scope`, `course`, `assignment`, `submissionId` 등으로 명시되고, 화면 라벨이 해당 범위와 일치하도록 조정됨 | 현재 최신 1건만 반환되어 전체 품질 대표값처럼 보일 수 있음 |

## 결정된 방향

- 기존 TODO 작업은 초기화하고, 참고 사이트 12개 화면을 Vue 프론트엔드에서 동일하게 재현하는 작업으로 새로 관리합니다.
- “비슷한 디자인”이 아니라 reference HTML의 화면 구조와 시각 구성을 기준으로 구현합니다.
- 구현은 `aic-frontend` 내부 Vue 화면과 공통 컴포넌트에 한정하고, 인증/권한/서비스 경계는 유지합니다.
- 정적 HTML을 그대로 복사해 배포하지 않고, 실제 화면은 backend API 데이터와 기존 라우팅에 맞게 구성합니다.
- 관리자 유저네임 글자 깨짐은 사용자 식별 정보 표시 품질 문제로 보고, 표시 계층만이 아니라 API 응답과 저장 경로까지 확인합니다.
- 그래프 축 범위 문제는 차트별 임시 보정보다 공통 Chart.js 옵션 또는 재사용 가능한 축 범위 계산으로 우선 해결합니다.
- 교사 대시보드의 상위 5명 컴포넌트는 프론트 렌더링만이 아니라 백엔드 집계/API 응답과 데이터 매핑까지 함께 확인합니다.
- 관리자 `AIC 분석 품질 모니터`는 `analysis_runs` 저장 데이터와 `/api/v1/admin/analysis-runs/*` API 기반으로 표시합니다.

## 열린 질문

- 데모 배포 이후 실제 연결할 도메인, TLS 인증서 발급 방식, HTTP to HTTPS 리다이렉트 적용 범위는 배포 단계에서 확정이 필요합니다.
