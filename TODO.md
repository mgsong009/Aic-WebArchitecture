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
| Frontend | P1 | Ready | `student-growth.html`과 동일한 성장 분석 화면을 구현한다. | `StudentGrowthView.vue`가 reference의 성장 히어로, 기간/과제 필터, AIC 추이, PI/UI/OI 변화, 누적 성장/프로파일 카드, 인사이트 섹션을 같은 시각 구성으로 렌더링한다. | Chart.js 설정도 reference와 최대한 맞춘다. |
| Frontend | P1 | Ready | `student-feedback.html`과 동일한 피드백 가이드 화면을 구현한다. | `StudentFeedbackView.vue`가 reference의 피드백 히어로, 지표별 가이드 카드, 교사 피드백, 다음 과제 체크리스트, 개선 팁 섹션을 같은 레이아웃으로 제공한다. | 과제 선택 UX와 충돌하지 않게 구성한다. |
| Frontend | P1 | Ready | `teacher-dashboard.html`, `teacher-students.html`, `teacher-student-detail.html`과 동일한 교사 기본 화면을 구현한다. | 교사 대시보드, 학생 목록, 학생 상세가 reference의 KPI, 분포 차트, 위험/상위 학생 카드, 검색/필터/표, 학생 프로필/과제 이력/피드백 작성 UI를 같은 구조로 렌더링한다. | 기존 teacher store/API 호출은 유지한다. |
| Frontend | P1 | Ready | `teacher-risk.html`, `teacher-assignment-analytics.html`, `teacher-advanced.html`과 동일한 교사 분석 화면을 구현한다. | 위험군, 과제 분석, 심화 분석 화면이 reference의 히어로, 필터, scatter/분포/상관/군집/상하위 분석 카드와 동일한 화면 흐름으로 제공된다. | API가 없는 심화 데이터는 명시된 fallback만 사용한다. |
| Frontend | P2 | Ready | reference 동일성 검증 절차를 추가한다. | 12개 reference 화면과 12개 Vue 화면을 데스크톱/모바일에서 캡처해 섹션 누락, 레이아웃 차이, 텍스트 겹침, 차트 blank 상태를 비교하는 체크리스트가 문서화된다. | 최소 검증 명령은 `npm run build`와 브라우저 캡처 확인이다. |

## 결정된 방향

- 기존 TODO 작업은 초기화하고, 참고 사이트 12개 화면을 Vue 프론트엔드에서 동일하게 재현하는 작업으로 새로 관리합니다.
- “비슷한 디자인”이 아니라 reference HTML의 화면 구조와 시각 구성을 기준으로 구현합니다.
- 구현은 `aic-frontend` 내부 Vue 화면과 공통 컴포넌트에 한정하고, 인증/권한/서비스 경계는 유지합니다.
- 정적 HTML을 그대로 복사해 배포하지 않고, 실제 화면은 backend API 데이터와 기존 라우팅에 맞게 구성합니다.

## 열린 질문

- 없음. 참고 사이트의 전체 12개 HTML 화면을 최종 시각 기준으로 삼습니다.
