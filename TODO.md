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
| Pipeline | P1 | Backlog | `aic_pipeline.py`를 도메인별 모듈로 단계적으로 분리한다. | `app/config.py`, `app/utils.py`, `app/embedding.py`, `app/metrics.py`, `app/pipeline.py`로 책임이 나뉘고, `app/pipeline_runner.py`의 public response contract와 `run_in_executor` 패턴이 유지된다. | `aic-pipeline/AGENTS.md`의 “core metric formulas” 규칙과 함께 갱신 필요. |
| Pipeline | P2 | Ready | 파이프라인 최적화 회귀 테스트와 API 호환성 체크를 추가한다. | 대표 `/analyze` 요청에서 `AnalyzeResponse` 필드가 모두 존재하고 numeric metric이 유효하며, 최적화 전후 핵심 점수 차이가 허용 오차 안에 있음을 검증한다. | backend `pipeline_client`와 metric persistence 영향 확인. |
| Backend/Frontend | P1 | Ready | AIC Analysis Quality Monitor에 최적화 전후 차이 섹션을 추가한다. | `/admin/analysis-quality`에서 선택한 analysis run의 before/after runtime, memory, throughput, 품질 점수 delta, 허용 오차 통과 여부를 카드/표/차트로 확인할 수 있다. | 학생 성과 해석 화면과 중복되는 AIC 분포/개별 학생 분석은 제외. |
| Frontend | P2 | Ready | 최적화 비교 UI에 회귀 경고와 측정 신뢰도 표시를 추가한다. | AIC/PI/UI/OI delta가 허용 오차를 넘거나 샘플 수가 부족하면 관리자에게 경고 배지와 원인 후보를 보여주며, 정상 범위면 배포 반영 가능 상태로 표시한다. | `admin.md`의 품질 보증 목적을 유지한다. |

## 결정된 방향

- 기존 TODO 작업은 초기화하고, 참고 사이트 12개 화면을 Vue 프론트엔드에서 동일하게 재현하는 작업으로 새로 관리합니다.
- “비슷한 디자인”이 아니라 reference HTML의 화면 구조와 시각 구성을 기준으로 구현합니다.
- 구현은 `aic-frontend` 내부 Vue 화면과 공통 컴포넌트에 한정하고, 인증/권한/서비스 경계는 유지합니다.
- 정적 HTML을 그대로 복사해 배포하지 않고, 실제 화면은 backend API 데이터와 기존 라우팅에 맞게 구성합니다.
- 관리자 유저네임 글자 깨짐은 사용자 식별 정보 표시 품질 문제로 보고, 표시 계층만이 아니라 API 응답과 저장 경로까지 확인합니다.
- 그래프 축 범위 문제는 차트별 임시 보정보다 공통 Chart.js 옵션 또는 재사용 가능한 축 범위 계산으로 우선 해결합니다.
- 교사 대시보드의 상위 5명 컴포넌트는 프론트 렌더링만이 아니라 백엔드 집계/API 응답과 데이터 매핑까지 함께 확인합니다.
- 파이프라인 최적화는 성능 기준선 측정, 반복 토큰화 제거, 임베딩 배치 처리, bootstrap 병렬화, 모듈화 순서로 진행합니다.
- 파이프라인 리팩터링 중에도 backend는 `/api/v1` 경유로만 pipeline을 호출하고, pipeline 응답 필드명과 저장 metric contract는 유지합니다.
- SBERT 모델명, CPU-only Docker 이미지, FastAPI handler의 executor 패턴, SBERT 실패 시 TF-IDF fallback은 최적화 중에도 보존합니다.
- `aic_pipeline.py`의 책임을 `app/` 모듈로 분리할 때는 `aic-pipeline/AGENTS.md` 운영 규칙도 함께 갱신합니다.
- AIC Analysis Quality Monitor에는 학생별 성과 해석이 아니라 파이프라인 실행 품질과 최적화 전후 회귀 여부만 표시합니다.
- 최적화 비교 데이터는 개인정보나 원문 텍스트를 저장하지 않고, 실행 시간/메모리/처리량/점수 delta/검증 통과 여부 같은 집계 지표로 관리합니다.

## 열린 질문

- 데모 배포 이후 실제 연결할 도메인, TLS 인증서 발급 방식, HTTP to HTTPS 리다이렉트 적용 범위는 배포 단계에서 확정이 필요합니다.
- 파이프라인 성능 목표는 벤치마크 기준선을 만든 뒤 데이터 크기별 목표 실행 시간과 메모리 한도로 확정이 필요합니다.
- 최적화 전후 품질 회귀 허용 오차(예: PI/UI/OI/AIC delta 임계값)와 기준 데이터셋 크기는 벤치마크 기준선 수립 후 확정이 필요합니다.
