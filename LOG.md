# LOG

이 파일은 완료된 프로젝트 작업을 날짜별로 기록합니다. 이후 유지보수자가 이해할 수 있도록 사실 중심으로 간결하게 작성합니다.

## 운영 규칙

- 작업이 완료, 병합, 또는 의도적으로 종료되었을 때 항목을 추가합니다.
- 영역, 요약, 수행한 확인, 후속 작업을 함께 기록합니다.
- 관련 파일, 이슈, Pull Request가 있으면 함께 적습니다.
- 완료된 작업은 이곳에 기록한 뒤 `TODO.md`에서 제거합니다.
- 비밀값, 실제 인증 정보, 로컬 `.env` 값, 비공개 배포 정보는 기록하지 않습니다.

## 기록 템플릿

```md
## YYYY-MM-DD

| 영역 | 요약 | 확인 | 후속 작업 |
| --- | --- | --- | --- |
| Frontend/Backend/Pipeline/Docs | 완료한 작업 요약입니다. | 수행한 빌드/테스트/확인, 또는 `Not run`. | 남은 작업, 이슈 링크, 또는 `None`. |
```

## 기록

## 2026-05-25 (TODO P1 안정화)

| 영역 | 요약 | 확인 | 후속 작업 |
| --- | --- | --- | --- |
| Backend/Frontend | 교사 심화 분석 fallback 제거 작업을 완료했습니다. `/teacher/analytics/advanced`가 metric 기반 `clusters`, `strategies`, `effort_samples`, `effort_correlation`, `topic_oi_samples`, `similarity_bands`를 반환하도록 확장했고, `TeacherAdvancedView.vue`는 `teacherReferenceData.js`의 고급 분석 reference fallback 없이 API 응답만 렌더링합니다. API 계약 문서도 새 응답 필드와 effort proxy 기준에 맞게 갱신했습니다. | `python -m compileall app` 성공. `npm.cmd run build` 성공. | 실제 운영 DB에서 `ui_distance`/`ui_cos_similarity` 분포가 충분한지 화면 데이터 품질 확인이 필요합니다. |
| Auth/Admin | 관리자 유저네임 한글 표시 경로를 점검하고 MySQL 연결 문자열에 `charset=utf8mb4`를 명시했습니다. `init.sql`의 admin seed는 정상 한글 값과 utf8mb4 DB 설정을 유지합니다. | `python -m compileall app` 성공. `npm.cmd run build` 성공. | 이미 생성된 DB 볼륨에 깨진 저장값이 남아 있으면 운영 DB 값 보정이 별도로 필요합니다. |
| Frontend/Charts | 공통 Chart.js 생성 경로에서 `x/y` 데이터 값을 수집해 고정 축 `min/max` 밖 또는 경계에 있는 실제 데이터 포인트가 여백을 두고 보이도록 축 범위를 자동 확장했습니다. | `npm.cmd run build` 성공. | None. |
| Backend/Frontend | 교사 대시보드 상위 5명 API를 `excellent/good` 필터가 아니라 분석된 전체 학생 AIC 내림차순 기준으로 최대 5명 반환하도록 수정하고, 프론트에서도 정렬/슬라이스를 방어적으로 보장했습니다. | `python -m compileall app` 성공. `npm.cmd run build` 성공. | None. |

## 2026-05-25 (통계 검증 신뢰구간 그래프 보정)

| 영역 | 요약 | 확인 | 후속 작업 |
| --- | --- | --- | --- |
| Frontend/Teacher | 통계 검증 신뢰성 탭의 AIC 신뢰구간 그래프를 추가 보정했습니다. 95% 범위 음영이 더 넓게 보이도록 차트 표시 도메인의 좌우 여백을 줄이고, 시안처럼 하단 x축 선을 추가했으며, 평균선이 곡선 꼭대기 위로 튀어나오지 않도록 평균선 시작점을 곡선 peak에 맞췄습니다. | `npm run build` 성공. `docker compose build frontend` 성공. `docker compose up -d frontend` 성공. 브라우저에서 `/teacher/statistics?tab=confidence` 확인: `.ci-range-fill` 1개, `.x-axis-line` 1개, `.ci-boundary-line` 2개, 평균선 `y1=42`, 곡선 peak `y=42`, CI 음영 폭 비율 약 0.423 확인. | None. |

## 2026-05-25 (통계 검증 신뢰구간 그래프)

| 영역 | 요약 | 확인 | 후속 작업 |
| --- | --- | --- | --- |
| Frontend/Teacher | 통계 검증 페이지의 신뢰성 검증 탭에서 `선택 대상의 AIC 신뢰구간` 그래프를 그림판 시안에 맞춰 조정했습니다. 95% CI 내부 구간을 옅은 파란색으로 채우고, 하한/상한 경계는 점선으로, 평균은 중앙 실선과 점으로 표시했습니다. 하단에는 하한·평균·상한 값과 라벨을 배치했습니다. | `npm run build` 성공. `docker compose build frontend` 성공. `docker compose up -d frontend` 성공. 브라우저에서 `/teacher/statistics?tab=confidence` 접속 후 `.ci-range-fill` 1개, `.ci-boundary-line` 2개, `.mean-line` 1개, `.ci-bracket-line` 3개, 하단 `하한/평균/상한` 라벨 표시를 확인했습니다. | None. |

## 2026-05-25 (관리자 시스템 현황)

| 영역 | 요약 | 확인 | 후속 작업 |
| --- | --- | --- | --- |
| Frontend/Admin | 관리자 `시스템 현황` 페이지의 학습 현황 지표를 정리했습니다. `제출률`과 `과제 수` 표시를 제거하고, `학습 과정 기록` 및 `학생당 평균 로그`를 표시하도록 변경했습니다. `학생당 평균 로그`는 전체 학습 과정 기록 수를 전체 학생 수로 나누어 소수점 둘째 자리까지 `건` 단위로 보여줍니다. | `rg`로 관리자 대시보드에서 `제출률`, `submission_rate`, `과제 수` 표시가 제거되고 `학습 과정 기록`, `학생당 평균 로그`가 남은 것을 확인했습니다. `npm run build` 성공. | None. |
| Frontend/Admin | 관리자 대시보드 카드 색상 톤을 운영형 화면에 맞게 낮췄습니다. 사용자/학습 기본 카드는 무채색 중심으로 통일하고, 상태 카드와 AIC/PI/UI/OI 점수 카드만 얇은 border와 숫자 색상으로 의미를 표현하도록 정리했습니다. | `AdminDashboardView.vue`에서 기존 광범위 컬러 클래스(`stat-card--blue/orange/green/yellow/red`) 참조가 제거된 것을 확인했습니다. `npm run build` 성공. | None. |

## 2026-05-25 (김증 페이지)

| 영역 | 요약 | 확인 | 후속 작업 |
| --- | --- | --- | --- |
| Frontend | 신뢰성 검증 탭의 AIC 신뢰구간 그래프를 compact chart로 다듬었습니다. 제목을 `선택 대상의 AIC 신뢰구간`으로 바꾸고, 선택 대상명을 설명에 포함했으며, 큰 사각형 CI 음영을 제거하고 얇은 CI bracket과 lower/mean/upper 수치 라벨을 표시했습니다. 평균 marker는 AIC primary 계열로 완화했고 선택된 테이블 행 강조를 보강했습니다. | `npm run build` 성공. `docker compose up --build -d frontend` 성공. Chrome headless에서 그래프 제목, 220px SVG 높이, CI bracket 1개, 기존 `ci-band` 0개, lower/mean/upper 수치 라벨 3개, primary 계열 mean marker, 테이블 행 클릭 선택 변경, horizontal overflow 없음 확인. | None. |
| Backend/DB | mysql_data 볼륨이 이미 존재해 init.sql이 재실행되지 않아 admin ENUM과 계정이 DB에 미반영된 상태였습니다. `docker compose exec db mysql` 로 직접 ALTER TABLE(role ENUM에 'admin' 추가)과 INSERT IGNORE(관리자 계정 생성)를 실행해 기존 데이터를 보존하면서 마이그레이션했습니다. 이후 프론트엔드를 `--no-cache` 옵션으로 강제 재빌드해 AdminDashboardView 번들을 포함시키고 컨테이너를 재기동했습니다. | DB: `SELECT role FROM users WHERE role='admin'`으로 계정 존재 확인. `SHOW COLUMNS FROM users LIKE 'role'`으로 ENUM 값 확인. 빌드 출력에서 `AdminDashboardView-*.css/js` 생성 확인. 전체 컨테이너 Started 상태 확인. | None. |
| Backend/Frontend | AIC 통계 검증 페이지를 공정성/신뢰성/해석 안정성 3개 탭 전환형 화면으로 재구성했습니다. `/teacher/statistics/validation` 전용 API를 추가해 난이도 보정 AIC, AIC 신뢰구간, 이상패턴 신호를 기본값 포함 계약으로 반환하고, `/teacher/statistics?tab=fairness|confidence|anomaly`에서 탭 상태를 유지합니다. 신뢰성 탭에는 새 chart library 없이 SVG 기반 단일 CI Curve Graph를 추가했습니다. | `python -m compileall app` 성공. `npm run build` 성공. `docker compose up --build -d backend frontend` 성공. 교사 로그인 후 `/api/v1/teacher/statistics/validation`에서 `difficulty_adjusted_aic`, `confidence_intervals`, `anomaly_detection.rule_counts`, `ci_width` 반환 확인. Chrome headless에서 3개 탭 전환, query 유지, CI SVG 렌더링, 테이블 행 클릭 선택 변경, Top 5/탐지 규칙 접힘 영역, 금지 표현 미노출, horizontal overflow 없음 확인. 기존 `/teacher/advanced`도 정상 렌더링 확인. | None. |

## 2026-05-25 (AIC 분석 품질 모니터 페이지)

| 영역 | 요약 | 확인 | 후속 작업 |
| --- | --- | --- | --- |
| Frontend | `/admin/analysis-quality` AIC 분석 품질 모니터 페이지를 구현했습니다. `adminAnalysisApi.js`(mock API, 향후 `/api/v1/admin/analysis-runs/*` 교체 가능), `adminAnalysisStore.js`(Pinia), `AdminKpiCard.vue` · `DataHealthCard.vue` · `BackendInfoCard.vue` · `PipelineStepper.vue` · `RuntimeBreakdownChart.vue` · `ServiceReadinessCard.vue` 6개 컴포넌트, `AnalysisQualityView.vue` 메인 뷰를 신규 추가했습니다. 라우터에 `{ path: '/admin/analysis-quality', meta: { role: 'admin' } }`를 등록하고 AppSidebar adminNav에 `분석 품질` 항목을 추가했습니다. `DataHealthCard.vue`의 Options API + Composition API 혼용 버그도 함께 수정했습니다. | `docker compose build --no-cache frontend` 성공. 빌드 출력에서 `AnalysisQualityView-*.css/js` 생성 확인. `docker compose up -d frontend` 성공. | 백엔드 API 준비 시 `adminAnalysisApi.js`의 mock return을 실제 axios 호출로 교체합니다. |

## 2026-05-25 (admin 계정 및 대시보드)

| 영역 | 요약 | 확인 | 후속 작업 |
| --- | --- | --- | --- |
| Backend | `admin` 역할을 시스템에 추가했습니다. `init.sql`의 `role ENUM`에 `'admin'` 값을 추가하고, SQLAlchemy 모델(`db_models.py`)의 Enum 정의도 함께 확장했습니다. init.sql 시드 데이터에 관리자 계정 1개를 삽입했습니다. | Not run — `docker compose up --build` 재시작 시 init.sql이 적용됩니다. | None. |
| Backend | `GET /api/v1/admin/dashboard` 엔드포인트를 구현했습니다. `admin_service.py`에서 사용자/클래스/제출/잡/점수/피드백 6개 섹션을 비동기 집계 쿼리로 반환하고, `admin.py` 라우터에 `require_role("admin")`으로 보호했습니다. `main.py`에 라우터를 등록했습니다. | Not run. | None. |
| Frontend | `/admin/dashboard` 단일 어드민 대시보드 페이지를 구현했습니다. `AdminDashboardView.vue`(4개 섹션: 사용자/학습/잡/점수), `stores/admin.js`, `api/index.js`의 `getAdminDashboard()` 함수를 추가했습니다. | Not run. | `docker compose up --build` 후 admin 계정으로 로그인하여 검증 필요. |
| Frontend | 로그인/라우팅/사이드바/헤더에 admin 역할을 추가했습니다. `LoginView.vue`에 관리자 역할 선택지(3열 그리드)를 추가하고, `router/index.js`에 `/admin/dashboard` 라우트(`meta: { role: 'admin' }`)를 등록했습니다. `AppSidebar.vue`와 `AppLayout.vue`에서 role 분기를 admin까지 확장했습니다. | Not run. | None. |
| Frontend | 고급 분석 화면 내부의 `통계 검증` 버튼과 탭 링크를 제거하고, 통계 검증 페이지 헤더를 심화 분석 화면과 동일한 gradient hero, 태그, 제목, pill 항목 규격으로 맞췄습니다. 별도 `/teacher/statistics` 페이지와 사이드바 진입은 유지했습니다. | `npm run build` 성공. `docker compose up --build -d frontend` 성공. Chrome headless에서 `/teacher/advanced` hero와 main에 통계 검증 링크가 없고, `/teacher/statistics` hero가 심화 분석 hero와 같은 gradient/background 및 16px radius를 쓰며 horizontal overflow가 없음을 확인했습니다. | None. |
| Frontend | 고급 분석 화면에서 별도 통계 검증 페이지로 이동하는 버튼과 탭 링크를 추가했습니다. `/teacher/advanced`의 상단 actions와 분석 탭 영역에서 `통계 검증`을 누르면 `/teacher/statistics`로 이동합니다. | `npm run build` 성공. `docker compose up --build -d frontend` 성공. Chrome headless에서 `/teacher/advanced`의 통계 검증 링크를 클릭해 `/teacher/statistics`로 이동하고 `통계 검증` 페이지 제목이 렌더링되는 것을 확인했습니다. | None. |
| Backend/Frontend | 교사 심화분석 API와 화면에 통계 검증 레이어를 추가했습니다. 기존 `/api/v1/teacher/analytics/advanced`의 `scatter_data`, `correlation_matrix` 타입은 유지하고, 난이도 보정 AIC, AIC 95% 신뢰구간, 이상패턴/해석 주의 신호를 기본값 포함 응답으로 확장했습니다. 프론트는 `TeacherAdvancedView.vue`에 과제 난이도 보정, 신뢰구간, 교사 확인 필요 신호 섹션을 추가했습니다. | `python -m compileall app` 성공. `npm ci` 성공. `npm run build` 성공. helper edge-case 인메모리 검증 성공. `docker compose up --build -d backend frontend` 성공. 교사 로그인 후 `/api/v1/teacher/analytics/advanced`에서 신규 필드와 기존 `correlation_matrix` 객체 유지 확인. Chrome headless에서 desktop/mobile `/teacher/advanced` 렌더링 확인, mobile horizontal overflow 없음. | None. |
| Frontend | 통계 검증 화면을 고급 분석 화면과 별도 교사 페이지로 분리했습니다. `TeacherAdvancedView.vue`는 군집/상관/전략/Effort 분석 전용으로 되돌리고, `TeacherStatisticalValidationView.vue`와 `/teacher/statistics` 라우트, 사이드바 `통계 검증` 메뉴를 추가했습니다. | `npm run build` 성공. `docker compose up --build -d frontend` 성공. Chrome headless에서 `/teacher/advanced`에 통계 섹션이 없고 `/teacher/statistics`가 독립 렌더링되는지 확인했습니다. 모바일 `/teacher/statistics` horizontal overflow 없음. | None. |

## 2026-05-24

| 영역 | 요약 | 확인 | 후속 작업 |
| --- | --- | --- | --- |
| Frontend | reference 12개 HTML과 Vue 라우트의 1:1 매핑표를 `aic-frontend/REFERENCE_ROUTE_MAP.md`에 작성했습니다. 각 reference 파일, 대응 Vue route/component, 필요한 API 데이터, 정적 유지 가능 요소, 누락/축소 섹션을 정리하고 완료된 TODO 항목을 제거했습니다. | `TODO.md`, `prototype/README.md`, `prototype/*.html`, `src/router/index.js`, `src/api/index.js`, layout 컴포넌트를 대조했습니다. | `index.html` 기준 랜딩 화면 동일성 구현을 이어갑니다. |
| Frontend | `LandingView.vue`를 reference `index.html`에 더 가깝게 정리했습니다. 4개 네비게이션 링크, 히어로 아이콘/CTA 아이콘, gradient title, reference 통계 문구, 역할 카드 영문 병기, 카드 hover와 어두운 배경 밀도를 반영했습니다. | `npm.cmd run build` 성공. dev server에서 `/` HTTP 200 응답 확인. 인앱 브라우저 자동화는 sandbox 초기화 오류로 캡처하지 못했습니다. | `login.html` 기준 로그인 화면 동일성 구현을 이어갑니다. |
| Frontend | `LoginView.vue`를 reference `login.html`에 맞춰 보강했습니다. 왼쪽 브랜딩 문구/gradient 강조, 중앙 카드의 role toggle 밀도, 로그인 상태 유지 checkbox, 비밀번호 찾기 텍스트, 로그인/데모 버튼 문구, 홈 링크를 reference 흐름에 맞췄고 기존 auth store 로그인 기능은 유지했습니다. | `npm.cmd run build` 성공. dev server에서 `/login` HTTP 200 응답 확인. | reference 사이드바/헤더 레이아웃 정합성 작업을 이어갑니다. |
| Frontend | reference의 사이드바/헤더 레이아웃을 공통 컴포넌트에 반영했습니다. `AppSidebar.vue`는 reference SVG 아이콘, role badge, Navigation label, 하단 사용자 영역과 logout 아이콘을 사용하고, `AppLayout.vue`는 breadcrumb 구분자, 검색 입력, 알림 버튼, 로그아웃 버튼을 기본 헤더 액션으로 제공합니다. 모바일 사이드바 토글/백드롭과 기존 actions slot은 유지했습니다. | `npm.cmd run build` 성공. | 학생 대시보드 reference 동일성 작업을 이어갑니다. |
| Frontend | `StudentDashboardView.vue`를 reference `student-dashboard.html` 흐름에 맞춰 정리했습니다. greeting banner, 5개 KPI, AIC 도넛, 지표별 비교, 반 내 위치, 성장 추이, 최근 과제, 과제별 지표 변화, 개선 가이드 구성을 유지하면서 공통 헤더와 중복되던 검색/알림/로그아웃 액션을 제거하고 AIC 상태 배지가 실제 점수 구간을 반영하도록 조정했습니다. | `npm.cmd run build` 성공. | 학생 과제 상세 화면 reference 동일성 작업을 이어갑니다. |
| Frontend | `StudentAssignmentDetailView.vue`를 reference `student-assignment.html` 흐름에 맞춰 확장했습니다. 과제 선택 탭, 과제 히어로, AIC/PI/UI/OI/Topic 점수 카드, AI/학생 기여도, PI 레이더, AI 초안-프롬프트-최종본 비교, 제출/재분석 폼, 상세 분석 카드, 교사 피드백, 자동 개선 가이드를 같은 화면 구조로 제공하며 기존 제출 및 job polling 기능은 유지했습니다. | `npm.cmd run build` 성공. Docker 스택을 `docker compose up --build -d`로 기동하고 nginx 경유 `/student/assignments/1` HTTP 200, 학생 로그인/과제 상세 API 응답을 확인했습니다. Browser 플러그인은 Windows sandbox 초기화 오류로 캡처하지 못했습니다. | 학생 성장 분석 화면 reference 동일성 작업을 이어갑니다. |
| Frontend | `StudentGrowthView.vue`를 reference `student-growth.html` 흐름에 맞춰 확장했습니다. 성장 히어로 4개 통계, 헤더 기간 필터와 CSV 내보내기, 내 AIC/반 평균 비교, PI/UI/OI 변화, 최신 지표 구성, 누적 면적 차트, 최신 프로파일, 동적 성장 인사이트를 실제 `/student/growth` 데이터 기반으로 렌더링합니다. | `npm.cmd run build` 성공. | 학생 피드백 화면 reference 동일성 작업을 이어갑니다. |
| Frontend | `StudentFeedbackView.vue`를 reference `student-feedback.html` 흐름에 맞춰 확장했습니다. 과제 선택 UX를 유지하면서 선택된 과제에는 피드백 히어로, PI/UI/OI 지표별 가이드 카드, 교사 피드백 이력 형태, 다음 과제 체크리스트, 자동 강점/개선/실행 팁 섹션을 실제 `/student/assignments`와 `/student/feedback/{assignment_id}` 데이터 기반으로 렌더링합니다. | `npm.cmd run build` 성공. | 교사 기본 화면 reference 동일성 작업을 이어갑니다. |
| Frontend | `TeacherDashboardView.vue`, `TeacherStudentsView.vue`, `TeacherStudentDetailView.vue`를 reference 교사 기본 화면 흐름에 맞춰 확장했습니다. 대시보드의 수업 요약/KPI/분포/추이/위험군/상하위 학생, 학생 목록의 요약 KPI/검색/필터/표/페이지네이션, 학생 상세의 프로필/도넛/취약 지표/성장 추이/과제 이력/피드백 작성 및 이력 UI를 구현하고, API 데이터가 없을 때만 reference fallback 데이터를 사용하도록 분리했습니다. | `npm.cmd run build` 성공. | 교사 분석 화면 reference 동일성 작업을 이어갑니다. |
| Frontend | `TeacherRiskView.vue`, `TeacherAssignmentAnalyticsView.vue`, `TeacherAdvancedView.vue`를 reference 교사 분석 화면 흐름에 맞춰 재구성했습니다. 위험군 히어로/학생 카드/Effort-AI 의존도 산점도/위험군 비교 차트, 과제별 KPI/평균/분포/지표/편차/상세 표, 심화 분석 히어로/군집/전략 유형/상관 히트맵/Effort/Topic/유사도 카드를 구현하고 API가 없는 분석 데이터는 `teacherReferenceData.js` fallback으로 분리했습니다. | `npm.cmd run build` 성공. Vite dev server에서 `/teacher/risk` HTTP 200 응답 확인. Browser 플러그인은 Windows sandbox 초기화 오류로 캡처하지 못했습니다. | reference 동일성 검증 절차 문서화를 이어갑니다. |
| Frontend | 12개 reference HTML 화면과 Vue 라우트의 데스크톱/모바일 시각 비교 절차를 `aic-frontend/REFERENCE_VISUAL_QA.md`에 문서화했습니다. 캡처 대상, viewport, 비교 항목, route matrix, pass 기준을 정리하고 완료된 TODO 항목을 제거했습니다. | `npm.cmd run build` 성공. | 실제 desktop/mobile 캡처 결과는 다음 시각 검증 pass에서 route matrix에 기록합니다. |
| Frontend | `REFERENCE_VISUAL_QA.md`와 `scripts/reference-visual-qa.mjs`의 reference 기준을 로컬 `prototype/*.html` 사본에서 원격 genspark reference HTML URL로 변경했습니다. | `node --check scripts/reference-visual-qa.mjs` 성공. | 실제 캡처 pass는 원격 reference 사이트 접근이 가능한 환경에서 진행합니다. |
| Frontend | 기존 Chrome CLI 캡처 스크립트를 Playwright 기반 로컬 QA 하네스로 교체했습니다. 각 route는 DOM/text/font/Vue root/network idle/settle 대기를 거친 뒤 캡처되고, console/page/request 오류, 수평 overflow, blank canvas, broken image를 `summary.json`과 `summary.md`에 기록합니다. `playwright-core` devDependency와 `npm run qa:reference`를 추가하고 캡처 산출물은 `.gitignore`에 포함했습니다. | `npm.cmd install --save-dev playwright-core@^1.52.0` 성공, `node --check scripts/reference-visual-qa.mjs` 성공, `npm.cmd run build` 성공, `QA_ROUTES=index,login npm.cmd run qa:reference` 스모크 성공. | 전체 12개 route matrix 기록을 이어갑니다. |
| Frontend | Playwright reference QA 전체 pass를 수행해 `REFERENCE_VISUAL_QA.md` route matrix에 결과를 기록했습니다. 12개 reference 화면과 12개 Vue 화면을 desktop/mobile로 캡처했고, 모든 캡처는 완료됐습니다. 자동 진단에서 teacher chart canvas blank와 일부 mobile horizontal overflow가 발견되어 후속 TODO로 분리했습니다. | `npm.cmd run build` 성공. `QA_READY_TIMEOUT_MS=60000`, `QA_SETTLE_MS=2500`, `npm.cmd run qa:reference` 성공. 결과: `aic-frontend/qa-captures/2026-05-24T04-37-17/summary.md`. | Blank chart canvas와 mobile overflow 수정 작업을 이어갑니다. |
| Frontend | reference QA에서 발견된 blank chart canvas와 모바일 horizontal overflow를 수정했습니다. 공통 Chart.js 훅은 재생성 전 애니메이션을 중지하고 기본 캔버스 배경을 칠하도록 보강했으며, 모바일 헤더/액션/위험군 카드/학생 상세/성장 분석/과제 분석 레이아웃의 폭 수축 규칙을 정리했습니다. | `npm.cmd run build` 성공. Chrome headless + Vite preview에서 mobile `/student/growth`, `/teacher/dashboard`, `/teacher/students/6`, `/teacher/risk`, `/teacher/analytics/assignment/5` 모두 `overflowX: false`, 대상 chart `blankCanvasCount: 0` 확인. desktop `/teacher/dashboard`, `/teacher/students/6`, `/teacher/risk`도 `blankCanvasCount: 0` 확인. | None. |

## 2026-05-23

| 영역 | 요약 | 확인 | 후속 작업 |
| --- | --- | --- | --- |
| Docs | 공식 프로젝트 작업 관리를 위한 루트 `TODO.md`와 `LOG.md` 템플릿을 생성했습니다. | 파일 생성과 내용을 확인했습니다. | 앞으로 의미 있는 변경을 시작하기 전에 `TODO.md`에 작업을 추가합니다. |
| Frontend | 정적 프로토타입 화면과 현재 Vue 라우트/뷰의 매핑표를 `aic-frontend/PROTOTYPE_ROUTE_MAP.md`에 작성하고, 제외하거나 축소할 프로토타입 요소를 명시했습니다. | `prototype/README.md`, `prototype/*.html`, `aic-frontend/src/router/index.js`, `aic-frontend/src/views/**`를 대조했습니다. | Vue 제거/보존 범위 결정과 API 부족분 결정 작업을 이어갑니다. |
| Frontend | Vue 프론트엔드 마이그레이션에서 보존할 기반 파일, 교체할 view/layout/style 범위, 새로 필요한 UX/API 결정 항목을 `aic-frontend/FRONTEND_MIGRATION_SCOPE.md`에 정리했습니다. | `src/api/index.js`, Pinia stores, router, chart composables/components, layout/components 구조를 확인했습니다. | 디자인 시스템 이식과 공통 레이아웃 재구성을 이어갑니다. |
| Frontend | 프로토타입 디자인 시스템을 Vue 전역 CSS에 정렬하고 pending 상태 배지, 표 래퍼, 차트 카드, 상호작용 행, 로딩/빈 상태 유틸리티를 보강했습니다. 학생 과제 목록과 교사 대시보드의 중복 scoped 스타일 일부를 전역 디자인 시스템 클래스로 대체했습니다. | `prototype/design-system.css`와 `src/assets/design-system.css`를 비교하고 관련 Vue 화면의 클래스 사용을 확인했습니다. | 공통 레이아웃을 프로토타입 기준으로 재구성합니다. |
| Frontend | `AppLayout.vue`와 `AppSidebar.vue`를 프로토타입 기반 공통 레이아웃으로 정리했습니다. 헤더 브레드크럼, role-aware 홈 이동, 정확한 활성 메뉴 매칭, 모바일 사이드바 토글/백드롭/닫기 흐름을 추가했습니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 로그인/랜딩 화면 이식 및 실제 인증 연결 유지 작업을 이어갑니다. |
| Frontend | 프로토타입의 랜딩/로그인 시각 구조를 Vue 화면으로 이식하고, 정적 HTML 링크와 DOM 조작을 Vue Router/state 기반 흐름으로 바꿨습니다. 로그인은 기존 `useAuthStore`의 `/auth/login` 흐름과 시드 데모 계정만 유지했습니다. | `npm.cmd run build` 성공. 인앱 브라우저에서 `/`와 `/login?role=teacher` 렌더링, 교사 role preselect, 콘솔 error 0개를 확인했습니다. | 학생 대시보드 API 동적화 작업을 이어갑니다. |
| Frontend | `StudentDashboardView.vue`를 `/student/dashboard` 응답에 맞게 정규화하고 null/빈 배열/오류 상태를 방어적으로 처리했습니다. AIC 도넛, KPI, 반 평균 비교, 최근 과제, 성장 차트는 API 응답 기반으로 렌더링하며 중복 카드/그리드 스타일 일부를 전역 디자인 시스템 클래스로 대체했습니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 학생 과제 목록/상세/제출 흐름 동적화 작업을 이어갑니다. |
| Frontend | 학생 과제 목록과 상세/제출 흐름을 API 기반으로 보강했습니다. 목록은 `/student/assignments` 오류/빈/로딩 상태를 처리하고, 상세는 `/student/assignments/{id}`, `/submissions`, `/jobs/{job_uuid}/status`와 `useJobPoller.js`를 연결해 제출, 분석 대기, 완료 후 자동 결과 반영, 실패 표시를 처리합니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 학생 성장 분석 화면 동적화 작업을 이어갑니다. |
| Frontend | `StudentGrowthView.vue`를 `/student/growth` 응답 기반 화면으로 재구성했습니다. AIC/PI/UI/OI 다중 추세, 나와 반 평균 AIC 비교, 최신 레이더 프로파일, 과제별 점수 표, 로딩/오류/빈 상태를 API 데이터에서 렌더링하도록 정리했습니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 학생 피드백 화면 동적화 작업을 이어갑니다. |
| Frontend | `StudentFeedbackView.vue`를 `/student/feedback/{assignment_id}`와 `/student/assignments` 응답 기반 화면으로 정리했습니다. assignment id가 없는 `/student/feedback` 경로를 추가하고, 제출 과제 선택, 과제 상세 이동, 교사 피드백, 자동 개선 가이드, 로딩/오류/빈 상태를 처리합니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 교사 대시보드 API 동적화 작업을 이어갑니다. |
| Frontend | `TeacherDashboardView.vue`를 `/teacher/dashboard` 응답 기반으로 정규화했습니다. 반 KPI, AIC 분포, 성장 추세, 위험군, 상위 학생을 API 데이터에서 렌더링하고 로딩/오류/빈 상태와 분포 bucket 라벨을 backend 계산 구간에 맞췄습니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 교사 학생 목록 동적화 작업을 이어갑니다. |
| Frontend | `TeacherStudentsView.vue`의 검색, 상태 필터, 정렬, 페이지네이션을 `/teacher/students` API 파라미터 기반으로 마무리하고 로딩/빈/오류 상태를 보강했습니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 교사 학생 상세 및 피드백 작성 동적화 작업을 이어갑니다. |
| Frontend | `TeacherStudentDetailView.vue`를 `/teacher/students/{id}` 응답에 방어적으로 맞추고 `/teacher/feedback` 저장 흐름에 과제 선택 UX, 저장/오류/빈 상태를 추가했습니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 교사 위험군 화면 동적화 작업을 이어갑니다. |
| Frontend | `TeacherRiskView.vue`를 `/teacher/risk-students` 응답 기반으로 정리했습니다. 위험군 산점도는 현재 API의 PI/UI를 축으로 렌더링하고, backend의 `all/pi/ui/oi` 위험 유형을 UI 배지와 요약 카드에 맞췄습니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 교사 과제 분석 화면 동적화 작업을 이어갑니다. |
| Frontend | `TeacherAssignmentAnalyticsView.vue`를 `/teacher/analytics/assignment/{assignment_id}` 응답 기반으로 재구성했습니다. 평균 KPI, AIC 분포, 상위/하위 학생, 난이도 지표와 로딩/빈/오류 상태를 렌더링합니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 교사용 과제 선택 목록은 API 계약 보강 여부 결정에 포함해 검토합니다. |
| Frontend | `aic-frontend/src`의 정적 하드코딩/랜덤/직접 DOM 조작 잔여물을 감사하고, 랜딩 화면의 `document.getElementById` 스크롤을 Vue `ref` 기반으로 교체했습니다. | `rg` 감사에서 중앙 Axios 클라이언트 외 잔여 직접 DOM/랜덤/시뮬레이션 패턴 없음 확인. `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | None. |
| Frontend | `TeacherAdvancedView.vue`를 `/teacher/analytics/advanced` 응답 기반으로 정리했습니다. PI/UI 산점도, 최신 평균 지표, 4x4 상관관계 히트맵, 개별 학생 표를 실제 API 데이터에서 렌더링하고 로딩/오류/빈 상태를 추가했습니다. 현재 API에 없는 군집/effort/유사도 데이터는 화면에서 생성하지 않습니다. | `TeacherAdvancedView.vue`에서 랜덤/시뮬레이션/미지원 데이터 키워드 없음 확인. `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 군집/effort/유사도는 API 계약 보강 여부 결정 후 별도 처리합니다. |
| Frontend | `TeacherAdvancedView.vue`에 API 계약 전 임시 표시용 고급 분석 영역을 추가했습니다. 군집 분석, 협업 전략 유형, Effort vs AIC, 초안 유사도는 익명 유형 기반 하드코딩 데이터로 렌더링하며, 추후 backend 계약 확정 시 교체할 수 있도록 임시 데이터 블록을 분리했습니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 군집/effort/유사도 API 계약 확정 후 임시 데이터 블록을 실제 응답 정규화로 교체합니다. |
| Frontend | TODO의 `프론트엔드 빌드 검증` 항목을 수행하고 완료 처리했습니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | None. |
| Frontend | 라우터와 네비게이션 정리 상태를 감사하고 완료 처리했습니다. Vue Router 경로, role/public meta, `<RouterLink>`/`router.push` 기반 이동, 정적 `.html` 링크 제거 상태를 확인했습니다. | `src/router/index.js`, `src/components/layout/AppSidebar.vue`, `src/views/**` 검색 확인. | 교사용 과제 분석의 동적 과제 선택은 API 계약 보강 여부 결정 후 별도 처리합니다. |
| Frontend | 로딩/빈 데이터/오류 상태 적용 범위를 감사하고 완료 처리했습니다. 학생/교사 API 화면의 loading/error/empty 분기, null metric 표시, 미제출 과제 표시, 제출 분석 대기/실패 상태, 인증 만료 interceptor 복귀 흐름을 확인했습니다. | `src/views/student/**`, `src/views/teacher/**`, `src/api/index.js`, `src/composables/useJobPoller.js` 검색 확인. | None. |
| Frontend | 차트 컴포넌트 재사용 구조를 확정했습니다. `LineChart`, `BarChart`, `RadarChart`, `ScatterChart`의 중복 Chart.js 생성/해제 로직을 제거하고 `useChart.js` composable로 생명주기를 통합했습니다. | `rg`로 Chart.js 생성/등록이 `useChart.js`에만 남은 것을 확인했습니다. `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | None. |
| Frontend | API 어댑터/정규화 레이어를 정리했습니다. `src/api/index.js`에 학생/교사 화면용 API 함수와 응답 정규화 helper를 추가하고, 화면과 Pinia store의 반복 응답 변환 및 직접 endpoint 호출을 중앙 함수로 대체했습니다. | `rg`로 화면/store/composable의 직접 API 호출 잔여를 확인했습니다. auth store와 `src/api/index.js` 내부 호출만 남았습니다. `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | None. |
| Backend/Frontend | 프론트 이식에 부족한 API 계약 보강 여부를 결정했습니다. 교사용 과제 선택은 backend 과제 목록 API를 추가하고, IQR/군집/effort-score/초안 유사도는 현재 단계에서 표시 축소 또는 임시 영역으로 유지하기로 문서화했습니다. | `aic-backend/API_CONTRACT_DECISIONS.md` 작성. `TODO.md`의 Blocked 항목을 후속 Ready 작업 2개로 분해했습니다. | 교사용 과제 목록 API와 프론트 과제 분석 네비게이션 동적화를 이어갑니다. |
| Backend | 교사 권한의 `/api/v1/teacher/assignments` API를 추가했습니다. 교사 소속 반의 과제 id, 제목, course code, 마감일, 제출 수, 분석 완료 수를 반환합니다. | `python -m compileall app` 성공. | 프론트 교사 과제 분석 네비게이션 동적화를 이어갑니다. |
| Frontend | 교사 과제 분석 네비게이션을 backend 과제 목록 API 기반으로 동적화했습니다. 사이드바는 첫 과제로 이동하고, 분석 화면은 과제 선택기와 과제 없음 empty state를 표시합니다. | `npm.cmd run build` 성공. Vite CJS Node API deprecation 경고만 확인했습니다. | 반응형 UI 검증을 이어갑니다. |
| Frontend | 반응형 UI 안정성을 검증하고 공통 레이아웃 CSS를 보강했습니다. 앱 본문/card/chart/form에는 `min-width: 0`을 적용하고, 표는 모바일에서 가로 스크롤되도록 최소 폭을 부여했으며, 액션 버튼 줄바꿈을 공통화했습니다. | 375px/768px/1440px 기준 breakpoint와 핵심 학생/교사 화면 구조를 코드로 확인했습니다. `npm.cmd run build` 성공. 브라우저에서 `/login` 수평 overflow 없음과 console error 0개를 확인했습니다. | Docker 통합 스모크 테스트를 이어갑니다. |
| Full Stack | Docker 통합 스모크 테스트를 완료했습니다. `docker compose up --build -d`로 전체 stack을 재빌드/재기동하고 frontend nginx 경유 `/api/v1`에서 학생 로그인, 학생 대시보드, 과제 목록, 제출/분석 job polling, 교사 로그인, 교사 대시보드, 과제 목록, 학생 목록, 학생 상세, 위험군, 과제 분석, 피드백 작성을 확인했습니다. | 학생 제출 job이 `done`과 metrics 반환으로 완료됐고, 피드백 저장 후 학생 상세에서 피드백이 조회됐습니다. `docker compose ps`에서 db healthy 및 backend/pipeline/frontend up 확인. backend/pipeline/frontend log tail에서 치명적 예외 없음. | None. |
