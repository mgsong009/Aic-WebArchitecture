# AGENTS.md

## Module Context

This service is the Vue 3 client for student and teacher workflows. It depends on the backend through `/api/v1` only and uses persisted Pinia auth state plus Axios interceptors for token refresh.

## Tech Stack & Constraints

- Use Vue 3 single-file components, Vite, Pinia, Vue Router, Axios, and Chart.js.
- Use npm because `package-lock.json` is authoritative.
- Keep API calls routed through `src/api/index.js`; do not create per-view Axios instances.
- The Vite dev proxy maps `/api` to `http://localhost:8000`; production nginx should continue forwarding API traffic to backend.

## Implementation Patterns

- Views live under `src/views/student` and `src/views/teacher` according to role.
- Shared visual primitives live under `src/components/common`; chart components live under `src/components/charts`.
- Use `@/` imports for `src` paths, matching `vite.config.js`.
- Keep role protection in router `meta.role`; add routes with explicit `public` or role metadata.
- Auth-sensitive requests should rely on the existing interceptor, which attaches `Authorization` and performs refresh-on-401.
- Reuse `src/assets/design-system.css` tokens and existing component structure before adding new styling patterns.

## Testing Strategy

- Build check: `npm run build`
- Local dev: `npm run dev`
- Preview production build: `npm run preview`
- There is no dedicated frontend test runner configured; for UI changes, at minimum run the build and manually exercise the affected route.

## Local Golden Rules

- Do keep student and teacher navigation separate and role-gated.
- Do update stores and views together when backend response shapes change.
- Do keep chart lifecycle logic in composables or chart components, not repeated inside every view.
- Do not store refresh tokens in Pinia or local storage; backend cookie behavior owns refresh.
- Do not bypass `api` from `src/api/index.js` for authenticated requests.
- Do not hardcode backend hostnames in components; use `/api/v1` through the configured client.
