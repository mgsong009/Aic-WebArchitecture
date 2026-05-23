# Reference HTML to Vue Route Map

This document fixes the implementation baseline for reproducing the 12 reference HTML screens in the Vue frontend while preserving the existing Vue Router, Pinia, Axios, and `/api/v1` backend boundary.

## Source Baseline

- Reference preview: `https://genspark.genspark.site/api/code_sandbox_light/preview/c66a59ad-6a9b-45f6-bda6-5cbf0f5ea36d/index.html`
- Local reference copy: `prototype/*.html`
- Shared reference styling: `prototype/design-system.css`
- Vue router: `src/router/index.js`
- API client and normalizers: `src/api/index.js`

The local `prototype` folder contains the same 12-screen reference set named in the root `TODO.md`, so local files are the primary source for repeated comparisons.

## Coverage Summary

The Vue app already has route coverage for every reference screen. It also keeps one Vue-only support route, `/student/assignments`, because students need an assignment list before opening a specific assignment detail screen.

| Reference file | Vue route | Vue component | Needed API data | Static or display-only elements | Missing or reduced sections |
| --- | --- | --- | --- | --- | --- |
| `index.html` | `/` | `src/views/LandingView.vue` | Auth state only for redirect target. | Platform copy, metric chips, statistics, metric cards, role cards, footer. | Reference background blobs are reduced to the current dark gradient treatment. |
| `login.html` | `/login` | `src/views/LoginView.vue` | `POST /auth/login`, auth refresh/logout state. | Role toggle, demo account labels, metric explainer panel, home link. | Reference "remember me" and password recovery text are visual-only unless auth policy is extended. |
| `student-dashboard.html` | `/student/dashboard` | `src/views/student/StudentDashboardView.vue` | `GET /student/dashboard`: student profile, latest metrics, deltas, class average, rank, trend, recent assignments, metric history. | Greeting text, KPI shell, guide copy, visual density and section order. | Reference-only decorative chart treatments may be approximated by reusable Chart.js components. |
| `student-assignment.html` | `/student/assignments/:id` | `src/views/student/StudentAssignmentDetailView.vue` | `GET /student/assignments/{id}`, `POST /submissions`, `GET /jobs/{job_uuid}/status`. | Assignment hero, status blocks, AI draft/student revision comparison, submit and reanalysis flow labels. | Only backend-supported result fields should be rendered as real analytics. |
| none | `/student/assignments` | `src/views/student/StudentAssignmentsView.vue` | `GET /student/assignments`. | Assignment selection/list navigation. | Vue-only support screen; no reference HTML equivalent. |
| `student-growth.html` | `/student/growth` | `src/views/student/StudentGrowthView.vue` | `GET /student/growth`: assignments and class average trend. | Growth hero, filter controls, cumulative/profile cards, insight copy. | Stacked area and AI-dependency visuals are reduced unless backed by available fields. |
| `student-feedback.html` | `/student/feedback`, `/student/feedback/:assignmentId` | `src/views/student/StudentFeedbackView.vue` | `GET /student/assignments`, `GET /student/feedback/{assignment_id}`. | Feedback hero, metric guide cards, checklist and improvement tips. | Assignment selection is added for `/student/feedback` because the backend feedback API is assignment-scoped. |
| `teacher-dashboard.html` | `/teacher/dashboard` | `src/views/teacher/TeacherDashboardView.vue` | `GET /teacher/dashboard`: class info, averages, trend, risk students, top students, distribution, counts. | KPI layout, distribution and risk summary sections. | Reference-only flourishes should stay secondary to real API values. |
| `teacher-students.html` | `/teacher/students` | `src/views/teacher/TeacherStudentsView.vue` | `GET /teacher/students` with search, status, sort, and pagination params. | Search/filter/table layout, status badges, row actions. | None known. |
| `teacher-student-detail.html` | `/teacher/students/:id` | `src/views/teacher/TeacherStudentDetailView.vue` | `GET /teacher/students/{id}`, `POST /teacher/feedback`. | Student profile, weak metric cards, assignment history, feedback writing UI. | Feedback history is limited to fields currently returned by the backend. |
| `teacher-risk.html` | `/teacher/risk` | `src/views/teacher/TeacherRiskView.vue` | `GET /teacher/risk-students`. | Risk hero, risk type badges, card list, scatter plot placement. | Scatter axes follow current PI/UI risk data rather than inventing additional fields. |
| `teacher-assignment-analytics.html` | `/teacher/analytics/assignment`, `/teacher/analytics/assignment/:id` | `src/views/teacher/TeacherAssignmentAnalyticsView.vue` | `GET /teacher/assignments`, `GET /teacher/analytics/assignment/{assignment_id}`. | Assignment selector, KPI cards, distribution, top/bottom student sections, difficulty display. | Box plot/IQR style reference sections are reduced to supported distribution and difficulty data. |
| `teacher-advanced.html` | `/teacher/advanced` | `src/views/teacher/TeacherAdvancedView.vue` | `GET /teacher/analytics/advanced`: scatter data and correlation matrix. | Advanced hero, scatter, heatmap, student table, temporary explanatory advanced panels. | Cluster, strategy type, effort score, and draft similarity are temporary/display-only until backend contracts exist. |

## Shared Layout Mapping

| Reference element | Vue owner | Notes |
| --- | --- | --- |
| Fixed left sidebar | `src/components/layout/AppSidebar.vue` | Role-aware navigation, role badge, bottom user area, logout, and teacher assignment dynamic path live here. |
| Header and breadcrumb | `src/components/layout/AppLayout.vue` | Keeps page title, breadcrumb, actions slot, and mobile menu/backdrop behavior. |
| Visual tokens | `src/assets/design-system.css` | Mirrors prototype colors, metric states, cards, tables, and chart shell utilities. |
| Charts | `src/components/charts/*`, `src/composables/useChart.js` | Chart.js lifecycle is centralized; views should not instantiate Chart.js directly. |
| Authenticated API access | `src/api/index.js` | All frontend requests stay under `/api/v1` through the shared Axios client and interceptors. |

## Implementation Guardrails

- Preserve route `meta.public` and `meta.role` protection in `src/router/index.js`.
- Keep student and teacher navigation separate.
- Do not copy static HTML into the app as deployable pages; translate the reference into Vue SFC structure.
- Do not render random analytics as real data. If a section is not backed by an API contract, mark it as temporary/display-only or reduce the section.
- Keep visual comparisons focused on structure, section order, color, spacing, card/button/badge style, chart placement, sidebar, and header composition.

