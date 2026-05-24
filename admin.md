# Claude 작업 지시서: 관리자용 AIC 분석 품질 관리 페이지 구현

## 0. 작업 목적

현재 프로젝트는 단순 정적 HTML 프로토타입이 아니라 **Vue SPA + FastAPI + MySQL + AIC 분석 파이프라인** 기반 웹 아키텍처로 구현하는 방향이다.

따라서 이번 작업은 `admin-analysis-quality.html` 같은 정적 HTML 파일을 추가하는 것이 아니다.  
Vue SPA 내부에 **관리자 전용 분석 품질 관리 화면**을 추가하는 작업이다.

이 페이지의 목적은 학생 성과를 해석하는 것이 아니라, **AIC 분석 실행 결과가 신뢰 가능한 상태인지 관리자 관점에서 점검하는 것**이다.

핵심 질문은 다음이다.

> 이번 AIC 분석 실행은 정상적으로 완료되었는가?  
> 데이터 품질은 충분한가?  
> 분석 파이프라인은 어느 단계에서 시간이 많이 걸렸는가?  
> 현재 분석 결과를 서비스에 반영해도 되는가?

---

## 1. 이번 작업의 범위

이번 작업에서 구현할 것은 **관리자용 한 페이지**다.

### 구현 대상

```txt
/admin/analysis-quality
```

### Vue 파일 기준 구현 대상

```txt
frontend/src/views/admin/AnalysisQualityView.vue
frontend/src/components/admin/AdminKpiCard.vue
frontend/src/components/admin/DataHealthCard.vue
frontend/src/components/admin/BackendInfoCard.vue
frontend/src/components/admin/PipelineStepper.vue
frontend/src/components/admin/RuntimeBreakdownChart.vue
frontend/src/components/admin/ServiceReadinessCard.vue
frontend/src/stores/adminAnalysisStore.ts
frontend/src/services/adminAnalysisApi.ts
```

프로젝트가 JavaScript 기반이면 `.ts` 대신 `.js`를 사용해도 된다.  
단, 역할 분리는 반드시 유지한다.

---

## 2. 절대 하지 말아야 할 것

이번 작업은 관리자 페이지 하나에 집중한다. 다른 작업으로 확장하지 않는다.

### 금지 사항

```txt
1. admin-analysis-quality.html 같은 정적 HTML 파일을 새로 만들지 않는다.
2. 기존 교사/학생 분석 화면을 수정하지 않는다.
3. 백엔드 전체 구조를 새로 만들지 않는다.
4. 인증/권한 시스템을 새로 구현하지 않는다.
5. MySQL 테이블을 실제로 생성하거나 마이그레이션하지 않는다.
6. AIC 계산 로직을 수정하지 않는다.
7. 학생 성과 해석 차트를 추가하지 않는다.
8. 과제별/학생별 분석 화면으로 확장하지 않는다.
9. 여러 페이지를 만들지 않는다.
10. 사이드바 전체 구조를 대규모로 갈아엎지 않는다.
```

---

## 3. 기존 분석 화면과 중복 금지

아래 항목은 이미 교사 또는 학생 화면에 있는 분석/시각화이므로 관리자 페이지에 넣지 않는다.

```txt
AIC 점수 분포
지표 평균 가로 막대
반 전체 AIC 추이
과제별 평균 AIC
과제별 분포 Box Plot
과제별 PI/UI/OI 비교
과제별 편차 점곡선
학생 군집분석 산점도
협업 전략 유형지도
지표 상관관계 히트맵
Effort vs AIC 산점도
Topic Score vs OI 산점도
Draft Similarity Matrix
과제 난이도 보정 AIC
AIC 신뢰구간 그래프
이상패턴 감지
학생 성장 추이
AI vs 학생 기여도
PI 세부 분석
글 변화 과정
AIC 구성 누적 면적 차트
최신 프로파일
```

관리자 페이지는 **AIC 결과 해석 화면**이 아니라 **AIC 분석 실행 품질 보증 화면**이다.

---

## 4. 최종 페이지 컨셉

페이지 이름:

```txt
AIC Analysis Quality Monitor
```

역할:

```txt
Admin 전용 분석 실행 품질 관리 화면
```

핵심 구성:

```txt
1. Page Header
2. Run Status KPI 4개
3. Data Health 카드
4. System / Backend Info 카드
5. Pipeline Stepper
6. Runtime Breakdown 차트
7. Service Readiness 카드
```

차트는 **Runtime Breakdown 가로 막대그래프 1개만 사용**한다.  
나머지는 카드, 배지, 체크리스트, 스텝퍼로 구성한다.

---

## 5. 화면 레이아웃

전체 화면은 한 페이지로 구성한다.

```txt
┌────────────────────────────────────────────────────────────┐
│ Page Header                                                 │
│ Admin · AIC Analysis Quality Monitor                        │
│ 이번 분석 실행이 정상적으로 완료되었는지 확인합니다.            │
│ [Course] [Assignment] [Analysis Run] [재분석 실행] [Export]  │
└────────────────────────────────────────────────────────────┘

┌────────────┬────────────┬────────────┬────────────┐
│ Run Status │ Processed  │ Success %  │ Runtime    │
│ Success    │ 1,913 rows │ 98.7%      │ 421.8s     │
└────────────┴────────────┴────────────┴────────────┘

┌──────────────────────────────┬──────────────────────────────┐
│ Data Health                  │ System / Backend Info         │
│ Health Score 87/100          │ Backend: SBERT                │
│ 결측 37건                    │ Model: multilingual-mpnet     │
│ 중복 12건                    │ Fallback: None                │
│ 이상치 18건                  │ Metric Version: v1.0.3        │
│ rating 보유율 65.2%          │ Pipeline Version: 2025.11.23  │
└──────────────────────────────┴──────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ Pipeline Stepper                                            │
│ Load → Preprocess → PI → Embedding → UI/OI → Validation → Save│
│  ✓        ✓         ✓       ✓          ✓          !        ✓ │
└────────────────────────────────────────────────────────────┘

┌──────────────────────────────┬──────────────────────────────┐
│ Runtime Breakdown            │ Service Readiness             │
│ 단계별 처리시간 막대그래프      │ 상태: Caution                 │
│ Embedding 구간이 92% 차지      │ 이유: rating 보유율 낮음        │
│                              │ 권장: rating 수집률 개선        │
└──────────────────────────────┴──────────────────────────────┘
```

---

## 6. 라우터 추가

`frontend/src/router/index.ts` 또는 현재 프로젝트의 라우터 파일에 아래 라우트를 추가한다.

```ts
{
  path: '/admin/analysis-quality',
  name: 'admin-analysis-quality',
  component: () => import('@/views/admin/AnalysisQualityView.vue'),
  meta: {
    requiresAuth: true,
    role: 'admin',
    layout: 'admin'
  }
}
```

현재 프로젝트가 `meta.layout`을 사용하지 않는다면 해당 필드는 생략해도 된다.  
단, 라우트 경로와 View 컴포넌트는 반드시 추가한다.

---

## 7. 관리자 레이아웃 처리

현재 프로젝트에 `AdminLayout.vue`가 있으면 그것을 사용한다.

없다면 이번 작업에서는 최소한의 관리자 레이아웃만 추가한다.

권장 파일:

```txt
frontend/src/layouts/AdminLayout.vue
```

관리자 사이드바 메뉴는 최소한 아래 항목을 표시한다.

```txt
Dashboard
Analysis Quality
System Logs
User Management
Settings
```

이번에 실제 동작이 필요한 메뉴는 `Analysis Quality` 하나뿐이다.

주의:

```txt
- 기존 TeacherLayout이나 StudentLayout을 망가뜨리지 않는다.
- 기존 사이드바 컴포넌트가 공통화되어 있다면, props로 role='admin'만 추가하는 방식이 좋다.
- 공통화가 복잡하면 AnalysisQualityView 내부에서 임시 관리자 레이아웃을 구성해도 된다.
```

---

## 8. 상태 관리 파일

`frontend/src/stores/adminAnalysisStore.ts`를 만든다.

Pinia를 사용하는 경우 다음 역할을 갖도록 한다.

```txt
- 현재 선택된 course
- 현재 선택된 assignment
- 현재 선택된 analysisRun
- adminAnalysisRun mock data
- loading 상태
- error 상태
- fetchLatestRun()
- reprocessRun()
```

### 더미 데이터

백엔드 연동 전에는 아래 데이터를 사용한다.

```ts
export const adminAnalysisRun = {
  runId: 'RUN-20251123-233424',
  course: 'CS101',
  assignment: 'Assignment #5',
  status: 'success',
  processedRows: 1913,
  validRows: 1888,
  successRate: 98.7,
  totalRuntimeSec: 421.8,
  avgRuntimePerSample: 0.22,

  dataHealth: {
    score: 87,
    requiredColumns: 'normal',
    missingRows: 37,
    duplicateRows: 12,
    textOutliers: 18,
    ratingCoverage: 65.2,
    lowSampleCourses: 2
  },

  backend: {
    embeddingBackend: 'SBERT',
    model: 'paraphrase-multilingual-mpnet-base-v2',
    fallback: 'None',
    metricVersion: 'v1.0.3',
    pipelineVersion: '2025.11.23',
    configHash: 'a7f91c2',
    createdAt: '2025-11-23 23:34:24'
  },

  pipelineSteps: [
    { name: 'Data Load', status: 'success', seconds: 1.2 },
    { name: 'Preprocess', status: 'success', seconds: 0.9 },
    { name: 'PI', status: 'success', seconds: 0.8 },
    { name: 'Embedding', status: 'success', seconds: 390.4 },
    { name: 'UI/OI', status: 'success', seconds: 10.3 },
    { name: 'Validation', status: 'warning', seconds: 3.4 },
    { name: 'Save', status: 'success', seconds: 1.1 }
  ],

  readiness: {
    status: 'caution',
    reason: 'rating 보유율이 65.2%로 낮아 검증 지표 해석 시 주의가 필요합니다.',
    actions: [
      '다음 분석 전 rating 수집률을 70% 이상으로 개선',
      'course별 최소 표본 수 미달 과제 확인',
      'Embedding 단계 처리시간 최적화 검토'
    ]
  }
};
```

---

## 9. API 서비스 파일

`frontend/src/services/adminAnalysisApi.ts`를 만든다.

실제 API가 아직 없더라도, 나중에 FastAPI와 연결할 수 있도록 service 계층을 분리한다.

### 함수 명세

```ts
export async function getLatestAnalysisRun() {
  // 현재는 mock data 반환
}

export async function getAnalysisQuality(runId: string) {
  // 현재는 mock data 반환
}

export async function reprocessAnalysisRun(runId: string) {
  // 현재는 mock success 반환
}
```

### 향후 연결 예정 API

실제 FastAPI 연결 시 아래 엔드포인트로 교체할 수 있도록 주석을 남긴다.

```txt
GET /api/admin/analysis-runs/latest
GET /api/admin/analysis-runs/{runId}/quality
GET /api/admin/analysis-runs/{runId}/pipeline-steps
GET /api/admin/analysis-runs/{runId}/runtime
POST /api/admin/analysis-runs/{runId}/reprocess
```

주의:

```txt
- 이번 작업에서 FastAPI 엔드포인트를 실제 구현하지 않는다.
- 단, 프론트 서비스 파일은 API 교체가 쉽도록 분리한다.
```

---

## 10. 컴포넌트 상세 명세

### 10.1 AnalysisQualityView.vue

역할:

```txt
- 전체 페이지 조립
- store에서 adminAnalysisRun 로드
- 필터 UI 표시
- 각 하위 컴포넌트에 데이터 전달
```

포함 영역:

```txt
Page Header
Run Status KPI Grid
Data Health + Backend Info 2-column grid
Pipeline Stepper
Runtime Breakdown + Service Readiness 2-column grid
```

### 10.2 AdminKpiCard.vue

Props:

```ts
defineProps<{
  label: string;
  value: string | number;
  subText?: string;
  status?: 'success' | 'warning' | 'danger' | 'neutral';
  icon?: string;
}>()
```

표시할 KPI 4개:

```txt
Run Status: Success / 모든 주요 단계 완료
Processed Rows: 1,913 / 전체 입력 샘플
Success Rate: 98.7% / 1,888 / 1,913 rows
Total Runtime: 421.8s / 0.22s / sample
```

### 10.3 DataHealthCard.vue

Props:

```ts
defineProps<{
  dataHealth: {
    score: number;
    requiredColumns: string;
    missingRows: number;
    duplicateRows: number;
    textOutliers: number;
    ratingCoverage: number;
    lowSampleCourses: number;
  }
}>()
```

표시 내용:

```txt
Data Health Score: 87 / 100
필수 컬럼 상태: 정상
결측 데이터: 37건
중복 제출: 12건
텍스트 길이 이상치: 18건
rating 보유율: 65.2%
course별 표본 부족: 2개
```

체크리스트:

```txt
✓ chatgpt_before 컬럼 정상
✓ user 컬럼 정상
✓ essay 컬럼 정상
! rating 결측 665건
! course별 표본 부족 2개
```

### 10.4 BackendInfoCard.vue

Props:

```ts
defineProps<{
  backend: {
    embeddingBackend: string;
    model: string;
    fallback: string;
    metricVersion: string;
    pipelineVersion: string;
    configHash: string;
    createdAt: string;
  }
}>()
```

표시 내용:

```txt
Embedding Backend: SBERT
Model: paraphrase-multilingual-mpnet-base-v2
Fallback: None
Metric Version: v1.0.3
Pipeline Version: 2025.11.23
Config Hash: a7f91c2
Created At: 2025-11-23 23:34:24
```

Fallback 배지 기준:

```txt
None: green
TF-IDF: orange
Failed: red
```

### 10.5 PipelineStepper.vue

Props:

```ts
defineProps<{
  steps: Array<{
    name: string;
    status: 'success' | 'warning' | 'failed' | 'pending';
    seconds: number;
  }>
}>()
```

단계:

```txt
Data Load
Preprocess
PI
Embedding
UI/OI
Validation
Save
```

상태 표현:

```txt
success: 초록색 원 + 체크
warning: 주황색 원 + 느낌표
failed: 빨간색 원 + X
pending: 회색 원
```

Validation이 warning일 때 문구:

```txt
rating 보유율이 70% 미만이므로 검증 해석에 주의가 필요합니다.
```

### 10.6 RuntimeBreakdownChart.vue

Props:

```ts
defineProps<{
  steps: Array<{
    name: string;
    status: string;
    seconds: number;
  }>
}>()
```

구현 방식:

```txt
- Chart.js 또는 vue-chartjs 사용
- 가로 막대그래프 1개만 구현
- x축: seconds
- y축: step name
```

데이터:

```txt
Data Load: 1.2s
Preprocess: 0.9s
PI: 0.8s
Embedding: 390.4s
UI/OI: 10.3s
Validation: 3.4s
Save: 1.1s
```

하단 인사이트:

```txt
Embedding 단계가 전체 처리시간의 92.6%를 차지합니다.
대용량 분석 시 비동기 처리 또는 배치 처리 최적화가 필요합니다.
```

### 10.7 ServiceReadinessCard.vue

Props:

```ts
defineProps<{
  readiness: {
    status: 'ready' | 'caution' | 'blocked';
    reason: string;
    actions: string[];
  }
}>()
```

이번 mock 상태:

```txt
Service Readiness: Caution
```

본문:

```txt
분석 파이프라인은 정상적으로 완료되었으나, rating 보유율이 65.2%로 낮아 검증 지표 해석 시 주의가 필요합니다.
```

권장 조치:

```txt
1. 다음 분석 전 rating 수집률을 70% 이상으로 개선
2. course별 최소 표본 수 미달 과제 확인
3. Embedding 단계 처리시간 최적화 검토
```

상태 기준:

```txt
Ready:
- success rate >= 98%
- rating coverage >= 70%
- failed rows <= 1%
- fallback 없음

Caution:
- 분석은 완료되었지만 일부 데이터 품질 또는 검증 조건 부족
- rating coverage 50~70%
- fallback 발생 또는 특정 단계 warning

Blocked:
- 분석 실패
- success rate < 90%
- 필수 컬럼 누락
- 저장 실패
```

---

## 11. 디자인 지침

기존 AIC 플랫폼 디자인 시스템을 최대한 유지한다.

### 공통 스타일

```txt
배경: 기존 --bg-primary 또는 프로젝트 전역 배경 사용
카드: white background, border, radius-xl, shadow-sm
폰트: Inter + Pretendard 계열 유지
간격: 기존 spacing token 또는 동일한 간격 체계 사용
```

### 컬러

관리자 페이지는 시스템 품질 관리 화면이므로 과도하게 화려한 색을 쓰지 않는다.

```txt
Primary: Navy / Blue
Success: Green
Warning: Orange
Danger: Red
Muted: Gray
```

기존 CSS 변수가 있으면 아래 변수를 우선 사용한다.

```css
--color-aic
--color-pi
--color-success
--color-warning
--color-danger
--color-gray-*
```

---

## 12. 최종 파일 구조 예시

최종적으로 아래 구조가 생기면 된다.

```txt
frontend/src/
├── views/
│   └── admin/
│       └── AnalysisQualityView.vue
├── components/
│   └── admin/
│       ├── AdminKpiCard.vue
│       ├── DataHealthCard.vue
│       ├── BackendInfoCard.vue
│       ├── PipelineStepper.vue
│       ├── RuntimeBreakdownChart.vue
│       └── ServiceReadinessCard.vue
├── stores/
│   └── adminAnalysisStore.ts
├── services/
│   └── adminAnalysisApi.ts
└── router/
    └── index.ts
```

프로젝트가 JavaScript 기반이면 다음처럼 작성한다.

```txt
adminAnalysisStore.js
adminAnalysisApi.js
```

---

## 13. 완료 기준

아래 체크리스트를 모두 만족하면 작업 완료다.

```txt
[ ] 정적 HTML 파일을 만들지 않았다.
[ ] /admin/analysis-quality 라우트가 추가되었다.
[ ] AnalysisQualityView.vue가 생성되었다.
[ ] 관리자 전용 페이지로 보인다.
[ ] Run Status KPI 4개가 보인다.
[ ] Data Health 카드가 보인다.
[ ] System / Backend Info 카드가 보인다.
[ ] Pipeline Stepper가 보인다.
[ ] Runtime Breakdown 가로 막대그래프가 보인다.
[ ] Service Readiness 카드가 보인다.
[ ] mock data가 store/service 계층을 통해 분리되어 있다.
[ ] 기존 교사/학생 화면과 중복되는 학생 성과 차트가 없다.
[ ] AIC 계산 로직을 수정하지 않았다.
[ ] 백엔드 전체 구조를 새로 만들지 않았다.
```

---

## 14. Claude에게 줄 최종 지시문

아래 문장을 그대로 작업 시작 프롬프트로 사용한다.

```txt
현재 프로젝트는 Vue SPA + FastAPI + MySQL + AIC 분석 파이프라인 기반 웹 아키텍처로 구현하는 방향이다.

이전의 admin-analysis-quality.html 정적 HTML 생성 방식은 폐기한다.

이번 작업에서는 관리자 전용 AIC Analysis Quality Monitor 페이지를 Vue SPA 내부에 추가해라.

구현 범위는 다음으로 제한한다.

1. /admin/analysis-quality 라우트 추가
2. src/views/admin/AnalysisQualityView.vue 생성
3. src/components/admin/ 아래에 다음 컴포넌트 생성
   - AdminKpiCard.vue
   - DataHealthCard.vue
   - BackendInfoCard.vue
   - PipelineStepper.vue
   - RuntimeBreakdownChart.vue
   - ServiceReadinessCard.vue
4. src/stores/adminAnalysisStore.ts 생성
5. src/services/adminAnalysisApi.ts 생성
6. 실제 API가 없으므로 우선 mock data를 사용하되, service 계층을 분리해서 나중에 FastAPI API로 쉽게 교체 가능하게 작성

중요한 제한사항:
- 정적 HTML 파일을 만들지 마라.
- 교사/학생 기존 분석 화면을 수정하지 마라.
- AIC 계산 로직을 수정하지 마라.
- 백엔드 전체 구조를 새로 만들지 마라.
- 인증/권한 시스템을 새로 구현하지 마라.
- 기존 교사/학생 분석과 중복되는 AIC 점수 분포, 과제별 분석, 군집분석, 성장 추이, 학생 성과 해석 차트는 넣지 마라.
- 차트는 Runtime Breakdown 가로 막대그래프 1개만 사용해라.

이 페이지의 목적은 학생 평가 해석이 아니라 AIC 분석 실행 품질 보증이다.

페이지에는 다음만 포함해라.
- Page Header
- Run Status KPI 4개
- Data Health 카드
- System / Backend Info 카드
- Pipeline Stepper
- Runtime Breakdown 가로 막대그래프
- Service Readiness 카드

기존 디자인 시스템과 스타일 토큰을 최대한 재사용하고, 필요한 경우에만 페이지/컴포넌트 scoped style을 작성해라.
```
