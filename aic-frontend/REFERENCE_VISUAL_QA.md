# Reference Visual QA Checklist

This checklist defines the repeatable visual verification pass for the 12 remote reference HTML screens and their Vue route equivalents.

## Goal

Confirm that each Vue route preserves the reference screen's structure, section order, colors, card/button/badge styling, spacing, typography, chart placement, sidebar, and header composition across desktop and mobile viewports.

## Required Checks

Run these checks before marking reference parity work complete:

1. Build the frontend.
   ```powershell
   cd aic-frontend
   npm run build
   ```
2. Start a local Vue target for capture.
   ```powershell
   cd aic-frontend
   npm run dev -- --host 127.0.0.1
   ```
3. Run the Playwright-based local QA harness.
   ```powershell
   cd aic-frontend
   npm run qa:reference
   ```
4. Capture each pair at desktop and mobile sizes.
   - Desktop: `1440 x 1000`
   - Mobile: `390 x 844`
5. Wait for the page to finish meaningful rendering before capture.
   - Default readiness timeout: `45000ms`.
   - Default post-ready settle wait: `1500ms`.
   - Slow network retry: set `QA_READY_TIMEOUT_MS=60000` or `QA_SETTLE_MS=3000`.
6. Compare the captures for:
   - Missing or extra sections.
   - Section order changes.
   - Sidebar, header, and breadcrumb differences.
   - Color, card, button, badge, and table style drift.
   - Spacing, alignment, and typography differences.
   - Text overlap, clipped labels, or horizontal overflow.
   - Blank charts, collapsed chart canvases, or unreadable chart labels.
   - Loading, empty, and error states that obscure the expected layout.

## Route Matrix

Reference site base URL:

`https://genspark.genspark.site/api/code_sandbox_light/preview/c66a59ad-6a9b-45f6-bda6-5cbf0f5ea36d`

| Reference HTML | Vue route | Desktop capture | Mobile capture | Required comparison notes |
| --- | --- | --- | --- | --- |
| `index.html` | `/` | `2026-05-24T04-37-17`: pass | `2026-05-24T04-37-17`: pass | Hero, navigation links, role cards, metric/stat sections, footer. |
| `login.html` | `/login` | `2026-05-24T04-37-17`: pass | `2026-05-24T04-37-17`: pass | Branding panel, role toggle, login card, demo actions, home link. |
| `student-dashboard.html` | `/student/dashboard` | `2026-05-24T04-37-17`: pass | `2026-05-24T04-37-17`: pass | Greeting, KPI cards, AIC donut, trend/chart cards, recent assignments, guide sections. |
| `student-assignment.html` | `/student/assignments/:id` | `2026-05-24T04-37-17`: pass | `2026-05-24T04-37-17`: pass | Assignment hero, metric cards, comparison blocks, submit/reanalysis form, feedback and guide cards. |
| `student-growth.html` | `/student/growth` | `2026-05-24T04-37-17`: pass | `2026-05-24T04-37-17`: horizontal overflow | Growth hero, period controls, trend charts, profile cards, insights. |
| `student-feedback.html` | `/student/feedback/:assignmentId` | `2026-05-24T04-37-17`: pass | `2026-05-24T04-37-17`: pass | Assignment selector, feedback hero, metric guides, teacher feedback, checklist. |
| `teacher-dashboard.html` | `/teacher/dashboard` | `2026-05-24T04-37-17`: pass | `2026-05-24T04-37-17`: 2/2 blank canvas | Class KPI grid, distribution/trend charts, risk and top student sections. |
| `teacher-students.html` | `/teacher/students` | `2026-05-24T04-37-17`: pass | `2026-05-24T04-37-17`: pass | Summary cards, search/filter controls, table density, badges, pagination. |
| `teacher-student-detail.html` | `/teacher/students/:id` | `2026-05-24T04-37-17`: 1/1 blank canvas | `2026-05-24T04-37-17`: horizontal overflow, 1/1 blank canvas | Profile hero, metric breakdown, growth chart, assignment history, feedback composer. |
| `teacher-risk.html` | `/teacher/risk` | `2026-05-24T04-37-17`: 2/2 blank canvas | `2026-05-24T04-37-17`: horizontal overflow, 2/2 blank canvas | Risk hero, risk cards, scatter chart, comparison chart, action/status badges. |
| `teacher-assignment-analytics.html` | `/teacher/analytics/assignment/:id` | `2026-05-24T04-37-17`: pass | `2026-05-24T04-37-17`: horizontal overflow | Assignment selector, KPI cards, distribution chart, metric panels, student table. |
| `teacher-advanced.html` | `/teacher/advanced` | `2026-05-24T04-37-17`: pass | `2026-05-24T04-37-17`: pass | Advanced hero, cluster/strategy panels, heatmap, scatter charts, student table. |

## Latest Verification

- Run directory: `aic-frontend/qa-captures/2026-05-24T04-37-17/`
- Summary files: `summary.json`, `summary.md`
- Command: `QA_READY_TIMEOUT_MS=60000`, `QA_SETTLE_MS=2500`, `npm run qa:reference`
- Result: all 24 reference/Vue captures completed.
- Automated findings:
  - Mobile horizontal overflow: `/student/growth`, `/teacher/students/:id`, `/teacher/risk`, `/teacher/analytics/assignment/:id`.
  - Blank chart canvas: mobile `/teacher/dashboard`; desktop/mobile `/teacher/students/:id`; desktop/mobile `/teacher/risk`.
  - Console errors, page errors, failed requests, and broken images: none detected.

## Capture Setup Notes

- For public routes, compare directly.
- For reference screens, capture the remote reference site URL, not the local `prototype/*.html` copy.
- For student routes, sign in through `/login?role=student` using a seeded student account before capture.
- For teacher routes, sign in through `/login?role=teacher` using a seeded teacher account before capture.
- If a route needs a dynamic id, use an id returned by the current API instead of hardcoding an unavailable record.
- Keep browser zoom at `100%`.
- Capture the initial above-the-fold state first, then scroll through the full page to confirm later sections.
- `scripts/reference-visual-qa.mjs` uses `playwright-core`, local Chrome/Edge, the built frontend in `dist`, and the backend under `http://127.0.0.1/api/v1`.
- Run it after `npm run build` and a healthy Docker stack:
  ```powershell
  cd aic-frontend
  $env:QA_READY_TIMEOUT_MS='60000'
  npm run qa:reference
  ```
- The script stores captures under `aic-frontend/qa-captures/<timestamp>/` and writes both `summary.json` and `summary.md`.
- Each capture waits for DOM visibility, meaningful body text, font readiness, Vue root text stability, a short network idle window when available, and the configured settle wait.
- For a quick smoke pass, limit routes with comma-separated slugs:
  ```powershell
  cd aic-frontend
  $env:QA_ROUTES='index,login'
  npm run qa:reference
  ```

## Browser Capture Troubleshooting

If captures are blank or incomplete:

- Increase `QA_READY_TIMEOUT_MS` to `60000` and `QA_SETTLE_MS` to `3000`, then rerun the capture pass.
- Open the failed reference URL manually in Chrome and wait until all charts/cards are visible; if the remote site itself loads slowly, use the same larger wait in the scripted pass.
- Prefer a fresh Chrome profile for manual checks if cached broken state is suspected.

If the Codex Browser plugin fails with a Windows sandbox initialization error:

1. Close Chrome/Edge windows that were opened by previous automated runs.
2. In Task Manager, end stale `chrome.exe`, `msedge.exe`, and `node.exe` processes that are clearly leftover headless capture jobs.
3. Restart the Codex desktop app, then retry Browser plugin automation.
4. If Docker access also shows `Access is denied` for `C:\Users\김우현\.docker\config.json`, restart Docker Desktop and confirm the current Windows user can open that file.
5. As a fallback, run `npm run qa:reference`; it does not depend on the Codex Browser plugin, but it still needs local Chrome/Edge and network access to the remote reference site.

## Pass Criteria

A route passes when both desktop and mobile captures show:

- All reference sections are present or an intentional reduction is documented in `REFERENCE_ROUTE_MAP.md`.
- No text overlap, clipped controls, or unintended horizontal page overflow.
- Charts render nonblank and keep stable dimensions during loading and after data appears.
- Navigation, headers, cards, buttons, badges, and tables visually match the reference within the limits of available API data.
- Authenticated pages keep the `/api/v1` backend boundary and do not call the pipeline directly.

## Recording Results

When a verification pass is completed, replace `Pending` in the route matrix with the capture date or artifact path, then add a concise summary to the root `LOG.md`.
