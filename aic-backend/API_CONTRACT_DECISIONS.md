# API Contract Decisions

This document records the current decision for prototype analytics elements that are not fully represented by the existing backend API. The goal is to keep the frontend on `/api/v1`, avoid direct pipeline calls, and avoid inventing frontend-only scoring semantics.

## Decision Summary

| Prototype need | Current API coverage | Decision | Rationale |
| --- | --- | --- | --- |
| Teacher assignment selection | Partial | Add backend API | `/teacher/analytics/assignment/{assignment_id}` exists, but the frontend has no teacher-scoped assignment list, which forces a hardcoded route target. Add a teacher-owned assignment list endpoint before final navigation polish. |
| Assignment score distribution | Covered | Keep current API | `/teacher/analytics/assignment/{assignment_id}` returns `distribution`, `class_avg`, top/bottom students, and difficulty. |
| Assignment box plot / IQR | Missing | Reduce for now | IQR needs per-assignment quartile semantics and UI-specific chart data. Do not add it until the product decides whether this is required beyond the existing distribution. |
| Advanced scatter and correlations | Covered | Keep current API | `/teacher/analytics/advanced` returns `scatter_data` and `correlation_matrix`, enough for the current supported advanced analytics view. |
| Cluster analysis | Missing | Reduce for now | Real clusters require a stable algorithm, labels, and backend-owned computation. Keep prototype-only cluster UI marked temporary until the scoring semantics are decided. |
| Effort-score | Missing | Reduce for now | Effort needs revision count, draft history, or similar process data that is not currently modeled as a backend metric. |
| Draft similarity | Missing | Reduce for now | Similarity requires a defined comparison method and privacy/product semantics. Do not derive it in the frontend. |

## Follow-up Tasks

| Area | Task | Completion Criteria |
| --- | --- | --- |
| Backend | Add teacher assignment list API | A teacher-scoped endpoint returns assignment ids, titles, course codes, due dates, submission counts, and analyzed submission counts for the teacher's class. |
| Frontend | Replace hardcoded teacher assignment analytics link | Sidebar and assignment analytics route use backend assignment metadata instead of `/teacher/analytics/assignment/1`. Empty assignment classes show a clear empty state. |

## Guardrails

- Frontend continues to call only `/api/v1` backend routes.
- Backend owns authorization, persistence, and analytics contract semantics.
- Unsupported prototype analytics must stay clearly reduced or temporary until backend and pipeline semantics are defined.
