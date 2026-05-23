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
