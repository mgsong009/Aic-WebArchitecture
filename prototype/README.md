# AIC Index — AI Collaboration Index Platform
## 교육 평가 웹플랫폼 프론트엔드 디자인 프로토타입

---

## 프로젝트 개요

**AIC Index Platform**은 생성형 AI를 활용한 학생 과제 수행 과정에서 결과물이 아닌 **협업 과정**을 정량적으로 평가하는 교육 플랫폼의 프론트엔드 디자인 프로토타입입니다.

### 핵심 지표 체계
| 지표 | 이름 | 설명 | 색상 |
|------|------|------|------|
| **PI** | Prompt Insight | 질문의 깊이, 구체성, 비판성 | 파랑 #3B82F6 |
| **UI** | User Intervention | AI 초안에 대한 의미 있는 수정/개입 정도 | 주황 #F97316 |
| **OI** | Originality Index | 주제 내 자기 관점과 독창성 | 초록 #10B981 |
| **TS** | Topic Score | 주제 적합성 | 보라 #8B5CF6 |
| **AIC** | AI Collaboration Index | PI+UI+OI 종합 가중 지수 | 네이비 #1E3A5F |

---

## 구현된 페이지 목록

### 공통 페이지
| 페이지 | 파일 | 설명 |
|--------|------|------|
| Landing | `index.html` | 플랫폼 소개, 역할 선택 |
| Login | `login.html` | 학생/교사 로그인, 데모 빠른 접속 |

### 학생 페이지 (Student)
| 페이지 | 파일 | 설명 |
|--------|------|------|
| Dashboard | `student-dashboard.html` | AIC/PI/UI/OI 요약, 반 평균 비교, 성장 추이 |
| Assignment Detail | `student-assignment.html` | 특정 과제 깊은 분석, AI vs 학생 기여도, Essay Evolution |
| Growth Analysis | `student-growth.html` | 과제별 지표 성장 추이, AI 의존도 변화 |
| Feedback Guide | `student-feedback.html` | 교사 피드백, 지표별 개선 가이드, 다음 과제 체크리스트 |

### 교사 페이지 (Teacher)
| 페이지 | 파일 | 설명 |
|--------|------|------|
| Dashboard | `teacher-dashboard.html` | 반 전체 현황 KPI, 분포 히스토그램, 위험군 요약 |
| Student List | `teacher-students.html` | 학생 검색/정렬/필터, 상태 배지, 전체 점수 표 |
| Student Detail | `teacher-student-detail.html` | 개인 상세 분석, 취약 지표, 피드백 작성/이력 |
| Risk Students | `teacher-risk.html` | 위험군 카드, 유형 태그, Scatter plot |
| Assignment Analytics | `teacher-assignment-analytics.html` | 과제별 평균/분포/난이도/편차 분석 |
| Advanced Analytics | `teacher-advanced.html` | 군집 분석, 상관관계 히트맵, 전략 유형 지도, Effort-Score |

---

## 파일 구조

```
/
├── index.html                       # Landing 페이지
├── login.html                       # Login 페이지
├── student-dashboard.html           # 학생 대시보드
├── student-assignment.html          # 과제 결과 상세
├── student-growth.html              # 성장 분석
├── student-feedback.html            # 피드백 가이드
├── teacher-dashboard.html           # 교사 대시보드
├── teacher-students.html            # 학생 목록
├── teacher-student-detail.html      # 학생 상세 분석
├── teacher-risk.html                # 위험군 학생
├── teacher-assignment-analytics.html # 과제 분석
├── teacher-advanced.html            # 심화 분석
├── css/
│   └── design-system.css            # 공통 CSS 디자인 시스템
└── js/
    └── common.js                    # 공통 JS (아이콘, 헬퍼 함수)
```

---

## 디자인 시스템

### 색상 토큰
```css
--color-aic:   #1E3A5F  /* AIC Navy */
--color-pi:    #3B82F6  /* PI Blue */
--color-ui:    #F97316  /* UI Orange */
--color-oi:    #10B981  /* OI Green */
--color-topic: #8B5CF6  /* Topic Purple */
```

### 상태 배지
- `Excellent` — AIC ≥ 80 (녹색)
- `Good` — AIC ≥ 65 (파랑)
- `Average` — AIC ≥ 50 (노랑)
- `Risk` — AIC < 50 (빨강)

### 사용 라이브러리
- **Chart.js** — 모든 차트 (Line, Bar, Scatter, Radar)
- **Google Fonts** — Inter (영문), Pretendard (한글)

---

## 빠른 접속 경로

| 역할 | 시작 URL |
|------|----------|
| 학생 데모 | `login.html` → "학생 데모" 버튼 → `student-dashboard.html` |
| 교사 데모 | `login.html` → "교사 데모" 버튼 → `teacher-dashboard.html` |
| Landing | `index.html` |

---

## 구현된 시각화 목록

| 차트 유형 | 사용 위치 |
|-----------|-----------|
| AIC 도넛 차트 (SVG) | student-dashboard, student-assignment, teacher-student-detail |
| PI/UI/OI 막대 그래프 | 모든 대시보드 |
| Line chart (AIC 성장) | student-dashboard, student-growth, teacher-dashboard |
| Multi-line trend | student-growth |
| Stacked Area | student-growth |
| Grouped Bar | student-dashboard, teacher-assignment-analytics |
| AIC Histogram | teacher-dashboard |
| Box Plot (simulated) | teacher-assignment-analytics |
| Scatter Plot | teacher-risk, teacher-advanced |
| Radar Chart | student-assignment |
| Correlation Heatmap (CSS) | teacher-advanced |
| Strategy Type Map (CSS) | teacher-advanced |

---

## 다음 개발 단계 (백엔드 연동 시)

1. **Vue 3 + Pinia 마이그레이션** — 현재 정적 HTML → Vue SPA로 전환
2. **FastAPI 연동** — 실제 AIC 지표 데이터 API 연결
3. **JWT 인증** — 학생/교사 역할 기반 접근 제어
4. **실시간 분석 파이프라인** — Pandas/SBERT 분석 결과 연동
5. **Sankey Diagram** — 협업 흐름 시각화 추가
6. **학생 알림** — 피드백 수신 알림 시스템
7. **반응형 모바일** — 모바일 사이드바 toggle 완성

---

*© 2025 AIC Index Platform — AI Collaboration Assessment System*
