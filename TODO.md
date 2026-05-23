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

## 작업 목록

| 영역 | 우선순위 | 상태 | 작업 | 완료 기준 | 비고 |
| --- | --- | --- | --- | --- | --- |
| Frontend | P1 | Ready | 프로토타입 디자인 시스템을 Vue 자산으로 이식 | `prototype/design-system.css`의 토큰, 레이아웃, 테이블, 배지, 차트 스타일이 `aic-frontend/src/assets/design-system.css`에 통합되고 중복/미사용 스타일이 정리됩니다. | 기존 CSS 변수명과 충돌 여부 확인 필요 |
| Frontend | P1 | Ready | 공통 레이아웃을 프로토타입 기준으로 재구성 | `AppLayout.vue`, `AppSidebar.vue`, 공통 헤더/브레드크럼/모바일 사이드바가 프로토타입 UX와 동일하게 동작하고 역할별 메뉴가 현재 라우터와 연결됩니다. | 프론트엔드는 백엔드만 호출하고 pipeline 직접 호출 금지 |
| Frontend | P1 | Ready | 로그인/랜딩 화면 이식 및 실제 인증 연결 유지 | `index.html`, `login.html`의 시각 구조가 Vue 화면으로 이식되고, 로그인은 `useAuthStore`와 `/auth/login`, `/auth/refresh`, `/auth/logout` 흐름을 그대로 사용합니다. | 데모 로그인 계정은 시드 데이터 기준으로만 유지 |
| Frontend | P1 | Ready | 학생 대시보드 API 동적화 | `StudentDashboardView.vue`가 `/student/dashboard` 응답으로 AIC 도넛, KPI, 반 평균 비교, 최근 과제, 성장 차트를 렌더링하고 정적 점수 배열이 제거됩니다. | 빈 값/null 상태와 로딩/오류 상태 포함 |
| Frontend | P1 | Ready | 학생 과제 목록/상세/제출 흐름 동적화 | `/student/assignments`, `/student/assignments/{id}`, `/submissions`, `/jobs/{job_uuid}/status`를 사용해 과제 목록, 제출 폼, 분석 대기/완료 폴링, 결과 차트를 구현합니다. | 기존 `useJobPoller.js` 재사용 |
| Frontend | P1 | Ready | 학생 성장 분석 화면 동적화 | `StudentGrowthView.vue`가 `/student/growth` 응답으로 AIC/PI/UI/OI 추세, 반 평균 비교, 과제별 변화 시각화를 렌더링하고 하드코딩 배열을 제거합니다. | 프로토타입의 stacked area는 Chart.js 구현 가능성 확인 |
| Frontend | P1 | Ready | 학생 피드백 화면 동적화 | `StudentFeedbackView.vue`가 `/student/feedback/{assignment_id}` 응답으로 교사 피드백과 자동 개선 가이드를 보여주고 과제 선택/이동 흐름을 제공합니다. | assignment id가 없는 진입 경로를 라우터에서 어떻게 처리할지 결정 필요 |
| Frontend | P1 | Ready | 교사 대시보드 API 동적화 | `TeacherDashboardView.vue`가 `/teacher/dashboard` 응답으로 반 KPI, AIC 분포, 성장 추세, 위험군, 상위 학생을 렌더링하고 정적 차트 데이터를 제거합니다. | 분포 bucket 라벨은 backend 응답과 UI 표기 통일 |
| Frontend | P1 | Ready | 교사 학생 목록 동적화 | `TeacherStudentsView.vue`가 `/teacher/students`의 `search`, `status`, `sort`, `page`, `per_page` 파라미터를 사용하고 검색/필터/정렬/페이지네이션을 API 기반으로 동작시킵니다. | 클라이언트 필터링 중복 제거 |
| Frontend | P1 | Ready | 교사 학생 상세 및 피드백 작성 동적화 | `TeacherStudentDetailView.vue`가 `/teacher/students/{id}`와 `/teacher/feedback`을 사용해 개인 지표, 과제 이력, 취약 지표, 피드백 작성/갱신을 처리합니다. | 피드백 대상 assignment_id 선택 UX 필요 |
| Frontend | P1 | Ready | 교사 위험군 화면 동적화 | `TeacherRiskView.vue`가 `/teacher/risk-students` 응답으로 위험군 카드와 산점도를 렌더링하고 위험 유형 태그를 backend 산출값과 맞춥니다. | 산점도 x/y 축 의미를 현재 API 필드로 재정의 필요 |
| Frontend | P1 | Ready | 교사 과제 분석 화면 동적화 | `TeacherAssignmentAnalyticsView.vue`가 `/teacher/analytics/assignment/{assignment_id}` 응답으로 평균, 분포, top/bottom, 난이도 지표를 렌더링합니다. | 과제 선택 목록 API가 없으면 `/student/assignments` 재사용 불가, 교사용 과제 목록 API 추가 검토 |
| Frontend | P1 | Ready | 교사 고급 분석 화면 동적화 | `TeacherAdvancedView.vue`가 `/teacher/analytics/advanced` 응답으로 scatter, correlation heatmap을 렌더링하고 프로토타입의 랜덤/시뮬레이션 데이터를 제거합니다. | 군집/effort/유사도 데이터는 현재 API에 없음 |
| Backend | P1 | Blocked | 프론트 이식에 부족한 API 계약 보강 여부 결정 | 프로토타입 화면 중 현재 API로 표현할 수 없는 데이터가 목록화되고, 백엔드 추가 API 또는 프론트 표시 축소 중 하나가 결정됩니다. | 후보: 교사용 과제 목록, assignment별 상세 분포/IQR, 군집, effort-score, 초안 유사도 |
| Frontend | P1 | Ready | API 어댑터/정규화 레이어 정리 | `src/api/index.js`를 통해서만 요청하고, 화면에서 반복되는 응답 변환은 Pinia store action 또는 composable로 모읍니다. | per-view Axios 인스턴스 생성 금지 |
| Frontend | P1 | Ready | 차트 컴포넌트 재사용 구조 확정 | 기존 `components/charts/*`, `useChart.js`, 공통 KPI/배지 컴포넌트를 프로토타입 화면에 맞게 재사용하거나 확장합니다. | Chart.js 생명주기 중복 구현 금지 |
| Frontend | P1 | Ready | 로딩/빈 데이터/오류 상태를 전 화면에 반영 | 모든 API 화면이 skeleton 또는 명확한 empty/error 상태를 표시하고, 인증 만료는 기존 interceptor 흐름으로 로그인 화면에 복귀합니다. | null metric, 미제출 과제, 분석 대기 job 포함 |
| Frontend | P1 | Ready | 라우터와 네비게이션 정리 | 프로토타입 URL 흐름을 Vue Router 경로로 변환하고, 모든 링크가 `<RouterLink>` 또는 `router.push`를 사용하며 역할별 `meta.role`이 유지됩니다. | 정적 `.html` 링크 제거 |
| Frontend | P1 | Ready | 정적 하드코딩 데이터 제거 감사 | `aic-frontend/src`에서 프로토타입에서 옮긴 점수 배열, 랜덤 데이터, 고정 학생명/교사명, 직접 DOM 조작이 남아 있지 않은지 `rg`로 점검합니다. | 허용: 데모 로그인 계정, UI 라벨, 디자인 토큰 |
| Frontend | P1 | Ready | 반응형 UI 검증 | 학생/교사 핵심 화면이 모바일과 데스크톱에서 겹침 없이 표시되고 사이드바 토글, 표 스크롤, 차트 크기가 안정적으로 동작합니다. | 최소 375px, 768px, 1440px 확인 |
| Frontend | P1 | Ready | 프론트엔드 빌드 검증 | `cd aic-frontend && npm run build`가 성공하고 Vite 번들에서 명백한 경고/오류가 없습니다. | 의존성 추가 시 `npm install` 후 lockfile 갱신 |
| Full Stack | P1 | Ready | Docker 통합 스모크 테스트 | `docker compose up --build` 기준으로 로그인, 학생 대시보드, 제출/분석 폴링, 교사 대시보드, 학생 상세, 피드백 작성이 동작합니다. | backend/pipeline/db 서비스 경계 유지 |

## 결정된 방향

- 프로토타입은 최종 UX 기준으로 사용하고, 데이터는 `aic-frontend`가 기존 FastAPI backend의 `/api/v1`만 호출해 공급받습니다.
- `aic-frontend`의 인증 스토어, Axios interceptor, 라우터 role guard, Chart.js 기반 컴포넌트는 가능한 한 보존합니다.
- 정적 HTML 파일을 그대로 복사하지 않고 Vue 3 SFC, Pinia action, router 기반 화면으로 이식합니다.
- frontend가 pipeline을 직접 호출하지 않고, 제출과 분석 상태는 backend의 `/submissions`, `/jobs/{job_uuid}/status`를 통해 처리합니다.

## 열린 질문

- 기존 `aic-frontend/src/views/**`를 전면 교체할지, 화면별로 프로토타입 UX를 점진 반영할지 결정이 필요합니다.
- 프로토타입의 고급 분석 요소 중 현재 API에 없는 군집, effort-score, 초안 유사도, box plot/IQR 데이터를 백엔드에 추가할지 UI에서 제외/축소할지 결정이 필요합니다.
- `StudentFeedbackView`와 `TeacherStudentDetailView`에서 피드백 대상 과제 선택 UX를 어떻게 둘지 결정이 필요합니다.
