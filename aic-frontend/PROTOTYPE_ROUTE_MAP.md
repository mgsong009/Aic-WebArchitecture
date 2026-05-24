# Prototype to Vue Route Map

This document maps the static prototype screens to the current Vue routes and view components. It is the working baseline for replacing prototype-only UI with Vue, Pinia, router, and backend API driven screens.

## Source Baseline

- Prototype index: `prototype/README.md`
- Vue router: `aic-frontend/src/router/index.js`
- Frontend boundary: Vue calls the backend through `/api/v1` only; it must not call the pipeline directly.

## Coverage Summary

`prototype/README.md` lists 12 HTML screens: 2 public, 4 student, and 6 teacher screens. The older TODO item mentioned 11 screens, but the actual prototype folder contains 12 HTML files.

The current Vue app has a route for every prototype screen. It also has one additional student assignment list route that is not represented by a dedicated prototype HTML file.

## Route Mapping

| Prototype file | Prototype screen | Vue route | Vue view | Mapping status | Notes |
| --- | --- | --- | --- | --- | --- |
| `prototype/index.html` | Landing | `/` | `src/views/LandingView.vue` | 1:1 | Keep public route metadata. |
| `prototype/login.html` | Login | `/login` | `src/views/LoginView.vue` | 1:1 | Preserve `useAuthStore` login, refresh, logout, and role redirect behavior. |
| `prototype/student-dashboard.html` | Student dashboard | `/student/dashboard` | `src/views/student/StudentDashboardView.vue` | 1:1 | Render dashboard data from `/student/dashboard`; keep class comparison and recent assignment navigation. |
| `prototype/student-assignment.html` | Student assignment detail | `/student/assignments/:id` | `src/views/student/StudentAssignmentDetailView.vue` | 1:1 | Combine assignment detail, submission form, analysis status, and result charts behind the backend assignment/submission/job APIs. |
| None | Student assignment list | `/student/assignments` | `src/views/student/StudentAssignmentsView.vue` | Vue-only support route | Required for navigation and assignment selection; use `/student/assignments`. |
| `prototype/student-growth.html` | Student growth analysis | `/student/growth` | `src/views/student/StudentGrowthView.vue` | 1:1 | Implement trend charts from `/student/growth`; stacked area may be approximated with Chart.js if needed. |
| `prototype/student-feedback.html` | Student feedback guide | `/student/feedback/:assignmentId` | `src/views/student/StudentFeedbackView.vue` | 1:1 with route parameter | The Vue route currently requires an assignment id; provide selection or redirect from assignment detail when no target is known. |
| `prototype/teacher-dashboard.html` | Teacher dashboard | `/teacher/dashboard` | `src/views/teacher/TeacherDashboardView.vue` | 1:1 | Render class KPIs, distribution, trends, risk students, and top students from `/teacher/dashboard`. |
| `prototype/teacher-students.html` | Teacher student list | `/teacher/students` | `src/views/teacher/TeacherStudentsView.vue` | 1:1 | Search, filter, sort, and pagination should be API backed through `/teacher/students`. |
| `prototype/teacher-student-detail.html` | Teacher student detail | `/teacher/students/:id` | `src/views/teacher/TeacherStudentDetailView.vue` | 1:1 | Use `/teacher/students/{id}` and `/teacher/feedback`; assignment target selection remains a UX decision. |
| `prototype/teacher-risk.html` | Teacher risk students | `/teacher/risk` | `src/views/teacher/TeacherRiskView.vue` | 1:1 | Align risk tags and scatter axes with backend `/teacher/risk-students` fields. |
| `prototype/teacher-assignment-analytics.html` | Teacher assignment analytics | `/teacher/analytics/assignment/:id` | `src/views/teacher/TeacherAssignmentAnalyticsView.vue` | 1:1 with route parameter | Needs a teacher-facing assignment selection/list source; current sidebar hardcodes assignment id `1`. |
| `prototype/teacher-advanced.html` | Teacher advanced analytics | `/teacher/advanced` | `src/views/teacher/TeacherAdvancedView.vue` | 1:1 | Current API can support scatter and correlation views; prototype-only cluster, effort-score, and similarity concepts require backend scope decisions. |

## Prototype Elements To Exclude Or Reduce

| Prototype element | Decision | Reason |
| --- | --- | --- |
| Static `.html` navigation links | Exclude | Vue screens must use `<RouterLink>` or `router.push` with role metadata. |
| Prototype direct script behavior in `common.js` | Exclude as-is | Shared behavior should move into Vue components, composables, or stores. |
| Direct pipeline calls | Exclude | Service boundary requires frontend to call only the backend under `/api/v1`. |
| Random, simulated, or hardcoded analytics data | Exclude from final Vue screens | Dynamic screens should use backend responses; demo auth labels are the only intended exception. |
| Prototype cluster analysis, effort-score, draft similarity, and box plot/IQR data | Reduce until API scope is decided | These concepts are not fully represented by the current API contract. |
| Standalone student feedback page without assignment context | Reduce to assignment-scoped flow for now | Current route and API are assignment-scoped. Add selection UX only after target behavior is decided. |

## Follow-up Decisions

- Decide whether to replace the current Vue view/layout/style layer all at once or migrate screen by screen.
- Decide whether teacher assignment selection needs a new backend endpoint or a reduced UI flow.
- Decide whether advanced analytics should add backend data for cluster, effort-score, similarity, and IQR concepts or omit those prototype sections.
