# Frontend Migration Scope

This document decides what to preserve, replace, or newly implement while migrating the static prototype UX into the existing Vue frontend.

## Preserve

| Area | Files | Decision | Reason |
| --- | --- | --- | --- |
| API client | `src/api/index.js` | Preserve and extend only through this module | It owns `/api/v1`, auth headers, refresh retry, and logout-on-refresh-failure behavior. |
| Auth store | `src/stores/auth.js` | Preserve | It already matches backend login, refresh, logout, persisted auth state, and role-aware user data. |
| Router guard | `src/router/index.js` | Preserve | It already has public routes, student/teacher `meta.role`, and fallback behavior. Add or adjust routes here only when needed. |
| App bootstrap | `src/main.js`, `src/App.vue` | Preserve | Pinia persisted state, router, and global design-system import are already in place. |
| Job polling | `src/composables/useJobPoller.js` | Preserve and reuse | Student submission analysis should continue through backend job status polling. |
| Chart lifecycle | `src/composables/useChart.js` | Preserve and reuse | Chart.js setup and cleanup should stay centralized. |
| Chart components | `src/components/charts/*.vue` | Preserve and extend | Existing wrappers should absorb prototype chart needs before new chart code is added. |
| Common metric components | `src/components/common/DonutChart.vue`, `KpiCard.vue`, `MetricBars.vue`, `StatusBadge.vue`, `LoadingSkeleton.vue` | Preserve and restyle as needed | These map directly to repeated prototype widgets and keep screen code smaller. |
| Data stores | `src/stores/student.js`, `src/stores/teacher.js` | Preserve and expand | Shared fetches should move here when more than one view needs them. |

## Replace Or Heavily Restyle

| Area | Files | Decision | Reason |
| --- | --- | --- | --- |
| Public screens | `src/views/LandingView.vue`, `src/views/LoginView.vue` | Restyle with prototype layout while preserving auth behavior | The prototype is the UX baseline, but Vue login must keep real backend auth. |
| Student screens | `src/views/student/*.vue` | Replace static or incomplete view layout with prototype-based Vue SFCs | Keep API-driven data and route params; remove prototype/random hardcoding. |
| Teacher screens | `src/views/teacher/*.vue` | Replace static or incomplete view layout with prototype-based Vue SFCs | Keep backend-owned authorization and persistence; surface missing API needs explicitly. |
| Shared layout | `src/components/layout/AppLayout.vue`, `src/components/layout/AppSidebar.vue` | Rebuild around prototype navigation UX | Preserve role-based menu behavior and router links. |
| Global styles | `src/assets/design-system.css` | Merge prototype tokens and patterns, then prune duplicates | This is the right home for migrated tokens, tables, badges, layout, and responsive rules. |

## Newly Implement Or Add

| Need | Recommended location | Notes |
| --- | --- | --- |
| Prototype-to-Vue route reference | `aic-frontend/PROTOTYPE_ROUTE_MAP.md` | Already created as the migration baseline. |
| Repeated API normalization | `src/stores/*.js` or `src/composables/*` | Use stores for shared state, composables for view-local formatting or polling helpers. |
| Assignment selection for teacher analytics | Router/sidebar plus backend-backed selector component | Avoid hardcoded `/teacher/analytics/assignment/1` once an assignment source exists. |
| Feedback target selection | Student and teacher feedback views | Keep assignment-scoped API calls; add selection UX only after deciding source data. |
| Missing advanced analytics data | Backend API or reduced UI sections | Cluster, effort-score, similarity, and IQR concepts need a product/API decision. |

## Remove Or Avoid

| Item | Decision |
| --- | --- |
| Static prototype `.html` files copied into `src` | Do not copy directly; translate into Vue SFCs. |
| Direct DOM manipulation from prototype scripts | Do not port as-is; use Vue state and components. |
| Per-view Axios instances or hardcoded backend URLs | Do not add; use `src/api/index.js`. |
| Frontend calls to pipeline service | Do not add; frontend talks to backend only. |
| Random analytics arrays, simulated scores, fixed student/teacher data | Remove from final dynamic views, except harmless demo login labels. |
| New auth transport or refresh-token storage in Pinia/local storage | Do not add without a coordinated auth redesign. |

## Migration Order

1. Merge the prototype design system into `src/assets/design-system.css`.
2. Rebuild `AppLayout.vue` and `AppSidebar.vue` around role-aware prototype navigation.
3. Restyle public login/landing views while keeping existing auth actions.
4. Migrate student screens, starting with dashboard and assignments because they drive feedback and growth navigation.
5. Migrate teacher screens, starting with dashboard and student list/detail before advanced analytics.
6. Audit static hardcoding and verify the build.
