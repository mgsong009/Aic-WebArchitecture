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
