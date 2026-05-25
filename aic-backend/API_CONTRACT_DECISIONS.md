# API Contract Decisions

This document records the current decision for prototype analytics elements that are not fully represented by the existing backend API. The goal is to keep the frontend on `/api/v1`, avoid direct pipeline calls, and avoid inventing frontend-only scoring semantics.

## Decision Summary

| Prototype need | Current API coverage | Decision | Rationale |
| --- | --- | --- | --- |
| Teacher assignment selection | Partial | Add backend API | `/teacher/analytics/assignment/{assignment_id}` exists, but the frontend has no teacher-scoped assignment list, which forces a hardcoded route target. Add a teacher-owned assignment list endpoint before final navigation polish. |
| Assignment score distribution | Covered | Keep current API | `/teacher/analytics/assignment/{assignment_id}` returns `distribution`, `class_avg`, top/bottom students, and difficulty. |
| Assignment box plot / IQR | Missing | Reduce for now | IQR needs per-assignment quartile semantics and UI-specific chart data. Do not add it until the product decides whether this is required beyond the existing distribution. |
| Advanced analytics overview | Covered | Keep current API | `/teacher/analytics/advanced` returns `scatter_data`, `correlation_matrix`, `clusters`, `strategies`, `effort_samples`, `effort_correlation`, `topic_oi_samples`, and `similarity_bands` from teacher-owned submission metrics. |
| Cluster analysis | Covered | Backend-owned rule grouping | Backend groups analyzed submissions into AIC bands and returns deterministic 2D points derived from PI/UI/OI/Topic/AIC metrics. This avoids frontend-only prototype points while keeping labels stable. |
| Effort-score | Covered with metric proxy | Backend returns `effort_samples` using available UI process metrics: `ui_distance`, then inverse `ui_cos_similarity`, then `ui_newinfo_ratio`, then `ui_score` fallback. The UI labels this as 수정 강도 rather than literal revision count. |
| Draft similarity | Covered | Backend-owned metric aggregation | Backend returns draft/final similarity bands from `ui_cos_similarity`; frontend only renders the returned bands. |

## Follow-up Tasks

| Area | Task | Completion Criteria |
| --- | --- | --- |
| Backend | Add teacher assignment list API | A teacher-scoped endpoint returns assignment ids, titles, course codes, due dates, submission counts, and analyzed submission counts for the teacher's class. |
| Frontend | Replace hardcoded teacher assignment analytics link | Sidebar and assignment analytics route use backend assignment metadata instead of `/teacher/analytics/assignment/1`. Empty assignment classes show a clear empty state. |

## Guardrails

- Frontend continues to call only `/api/v1` backend routes.
- Backend owns authorization, persistence, and analytics contract semantics.
- Unsupported prototype analytics must stay clearly reduced or temporary until backend and pipeline semantics are defined.
