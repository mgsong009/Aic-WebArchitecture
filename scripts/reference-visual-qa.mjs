import { createServer } from 'node:http'
import { access, mkdir, readFile, writeFile } from 'node:fs/promises'
import { extname, resolve } from 'node:path'
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'

const ROOT = resolve(import.meta.dirname, '..')
const FRONTEND_DIR = resolve(ROOT, 'aic-frontend')
const requireFromFrontend = createRequire(resolve(FRONTEND_DIR, 'package.json'))
const DIST_DIR = resolve(FRONTEND_DIR, 'dist')
const OUT_DIR = resolve(FRONTEND_DIR, 'qa-captures')
const APP_ORIGIN = process.env.QA_BACKEND_ORIGIN || 'http://127.0.0.1'
const API_ORIGIN = `${APP_ORIGIN}/api/v1`
const QA_PORT = Number(process.env.QA_PORT || 5174)
const QA_ORIGIN = `http://127.0.0.1:${QA_PORT}`
const REFERENCE_ORIGIN = process.env.QA_REFERENCE_ORIGIN || 'https://genspark.genspark.site/api/code_sandbox_light/preview/c66a59ad-6a9b-45f6-bda6-5cbf0f5ea36d'
const READY_TIMEOUT_MS = Number(process.env.QA_READY_TIMEOUT_MS || 45000)
const SETTLE_MS = Number(process.env.QA_SETTLE_MS || 1500)
const ROUTE_FILTER = (process.env.QA_ROUTES || '')
  .split(',')
  .map((route) => route.trim())
  .filter(Boolean)

const CHROME_PATHS = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
]

const viewports = [
  { key: 'desktop', width: 1440, height: 1000 },
  { key: 'mobile', width: 390, height: 844 },
]

const routes = [
  { slug: 'index', reference: 'index.html', vue: '/' },
  { slug: 'login', reference: 'login.html', vue: '/login', minTextLength: 40 },
  { slug: 'student-dashboard', reference: 'student-dashboard.html', vue: '/student/dashboard', role: 'student' },
  { slug: 'student-assignment', reference: 'student-assignment.html', vue: ({ ids }) => `/student/assignments/${ids.studentAssignmentId}`, role: 'student' },
  { slug: 'student-growth', reference: 'student-growth.html', vue: '/student/growth', role: 'student' },
  { slug: 'student-feedback', reference: 'student-feedback.html', vue: ({ ids }) => `/student/feedback/${ids.studentAssignmentId}`, role: 'student' },
  { slug: 'teacher-dashboard', reference: 'teacher-dashboard.html', vue: '/teacher/dashboard', role: 'teacher' },
  { slug: 'teacher-students', reference: 'teacher-students.html', vue: '/teacher/students', role: 'teacher' },
  { slug: 'teacher-student-detail', reference: 'teacher-student-detail.html', vue: ({ ids }) => `/teacher/students/${ids.teacherStudentId}`, role: 'teacher' },
  { slug: 'teacher-risk', reference: 'teacher-risk.html', vue: '/teacher/risk', role: 'teacher' },
  { slug: 'teacher-assignment-analytics', reference: 'teacher-assignment-analytics.html', vue: ({ ids }) => `/teacher/analytics/assignment/${ids.teacherAssignmentId}`, role: 'teacher' },
  { slug: 'teacher-advanced', reference: 'teacher-advanced.html', vue: '/teacher/advanced', role: 'teacher' },
]

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.ico': 'image/x-icon',
}

async function pathExists(path) {
  try {
    await access(path)
    return true
  } catch {
    return false
  }
}

async function findBrowser() {
  for (const candidate of CHROME_PATHS) {
    if (await pathExists(candidate)) return candidate
  }
  throw new Error('No local Chrome or Edge executable found.')
}

async function importPlaywright() {
  try {
    const playwrightModule = await import(pathToFileURL(requireFromFrontend.resolve('playwright-core')).href)
    return playwrightModule.chromium ? playwrightModule : playwrightModule.default
  } catch (error) {
    throw new Error('Missing playwright-core. Run `cd aic-frontend && npm install --save-dev playwright-core` before QA capture.')
  }
}

async function login(role) {
  const userId = role === 'teacher' ? 'teacher_kim' : 'student_001'
  const response = await fetch(`${API_ORIGIN}/auth/login`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ user_id: userId, password: 'password123', role }),
  })
  if (!response.ok) throw new Error(`${role} login failed: ${response.status}`)
  return response.json()
}

async function apiGet(path, token) {
  const response = await fetch(`${API_ORIGIN}${path}`, {
    headers: { authorization: `Bearer ${token}` },
  })
  if (!response.ok) return null
  return response.json()
}

async function resolveIds(tokens) {
  const studentAssignments = await apiGet('/student/assignments', tokens.student.access_token)
  const teacherAssignments = await apiGet('/teacher/assignments', tokens.teacher.access_token)
  const teacherStudents = await apiGet('/teacher/students', tokens.teacher.access_token)
  return {
    studentAssignmentId: studentAssignments?.[0]?.id || 1,
    teacherAssignmentId: teacherAssignments?.[0]?.id || 1,
    teacherStudentId: teacherStudents?.students?.[0]?.id || teacherStudents?.[0]?.id || 2,
  }
}

function authPayload(auth) {
  return JSON.stringify({
    user: auth.user,
    accessToken: auth.access_token,
  })
}

function createQaServer() {
  const server = createServer(async (request, response) => {
    try {
      const url = new URL(request.url, QA_ORIGIN)

      if (url.pathname.startsWith('/api/')) {
        const proxyUrl = `${APP_ORIGIN}${url.pathname}${url.search}`
        const proxyResponse = await fetch(proxyUrl, {
          method: request.method,
          headers: request.headers,
          body: ['GET', 'HEAD'].includes(request.method || 'GET') ? undefined : request,
          duplex: 'half',
        })
        response.writeHead(proxyResponse.status, Object.fromEntries(proxyResponse.headers.entries()))
        response.end(Buffer.from(await proxyResponse.arrayBuffer()))
        return
      }

      const requested = url.pathname === '/' ? '/index.html' : url.pathname
      const normalized = requested.replace(/^\/+/, '')
      let filePath = resolve(DIST_DIR, normalized)
      if (!filePath.startsWith(DIST_DIR)) {
        response.writeHead(403)
        response.end('Forbidden')
        return
      }
      if (!(await pathExists(filePath))) filePath = resolve(DIST_DIR, 'index.html')
      const content = await readFile(filePath)
      response.writeHead(200, { 'content-type': mimeTypes[extname(filePath)] || 'application/octet-stream' })
      response.end(content)
    } catch (error) {
      response.writeHead(500)
      response.end(String(error?.stack || error))
    }
  })

  return new Promise((resolveServer, rejectServer) => {
    server.once('error', rejectServer)
    server.listen(QA_PORT, '127.0.0.1', () => resolveServer(server))
  })
}

async function withPage(browser, viewport, auth, fn) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
    deviceScaleFactor: 1,
    isMobile: viewport.key === 'mobile',
  })
  if (auth) {
    await context.addInitScript((value) => {
      window.localStorage.setItem('auth', value)
    }, authPayload(auth))
  } else {
    await context.addInitScript(() => {
      window.localStorage.removeItem('auth')
    })
  }
  const page = await context.newPage()
  const diagnostics = {
    consoleErrors: [],
    pageErrors: [],
    failedRequests: [],
  }
  page.on('console', (message) => {
    if (['error', 'warning'].includes(message.type())) diagnostics.consoleErrors.push(message.text())
  })
  page.on('pageerror', (error) => diagnostics.pageErrors.push(error.message))
  page.on('requestfailed', (request) => {
    diagnostics.failedRequests.push(`${request.method()} ${request.url()} ${request.failure()?.errorText || ''}`.trim())
  })

  try {
    const result = await fn(page, diagnostics)
    await context.close()
    return result
  } catch (error) {
    await context.close()
    throw error
  }
}

async function waitForMeaningfulRender(page, kind, route) {
  const minTextLength = route.minTextLength || 80
  await page.waitForLoadState('domcontentloaded', { timeout: READY_TIMEOUT_MS })
  await page.locator('body').waitFor({ state: 'visible', timeout: READY_TIMEOUT_MS })
  await page.waitForFunction((minimumLength) => document.body && document.body.innerText.trim().length >= minimumLength, minTextLength, { timeout: READY_TIMEOUT_MS })
  await page.waitForFunction(async () => {
    if (document.fonts?.ready) await document.fonts.ready
    await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))
    return true
  }, null, { timeout: READY_TIMEOUT_MS })

  if (kind === 'vue') {
    await page.waitForFunction((minimumLength) => {
      const root = document.querySelector('#app')
      if (!root || root.innerText.trim().length < minimumLength) return false
      const lower = root.innerText.toLowerCase()
      return !lower.includes('loading') && !lower.includes('불러오는 중')
    }, minTextLength, { timeout: READY_TIMEOUT_MS })
  }

  try {
    await page.waitForLoadState('networkidle', { timeout: 10000 })
  } catch {}
  await page.waitForTimeout(SETTLE_MS)
}

async function inspectPage(page) {
  return page.evaluate(() => {
    function isBlankCanvas(canvas) {
      const width = canvas.width || canvas.clientWidth
      const height = canvas.height || canvas.clientHeight
      if (!width || !height) return true
      const context = canvas.getContext('2d')
      if (!context) return true
      const data = context.getImageData(0, 0, width, height).data
      const maxSamples = 12000
      const pixelCount = data.length / 4
      const pixelStep = Math.max(1, Math.floor(pixelCount / maxSamples))
      for (let pixel = 0; pixel < pixelCount; pixel += pixelStep) {
        const index = pixel * 4 + 3
        if (data[index] !== 0) return false
      }
      return true
    }

    const canvases = [...document.querySelectorAll('canvas')]
    const bodyText = document.body.innerText.trim()
    return {
      url: location.href,
      title: document.title,
      bodyTextLength: bodyText.length,
      bodyTextSample: bodyText.slice(0, 220),
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      canvasCount: canvases.length,
      blankCanvasCount: canvases.filter(isBlankCanvas).length,
      imageCount: document.images.length,
      brokenImageCount: [...document.images].filter((image) => image.complete && image.naturalWidth === 0).length,
      sectionCount: document.querySelectorAll('section, main, article').length,
    }
  })
}

async function capturePage(browser, viewport, target, auth, filePath, route) {
  return withPage(browser, viewport, auth, async (page, diagnostics) => {
    await page.goto(target.url, { waitUntil: 'commit', timeout: READY_TIMEOUT_MS })
    await waitForMeaningfulRender(page, target.kind, route)
    const inspection = await inspectPage(page)
    await page.screenshot({ path: filePath, fullPage: true, animations: 'disabled' })
    return {
      path: filePath,
      inspection,
      diagnostics,
      status: 'captured',
    }
  })
}

async function main() {
  await mkdir(OUT_DIR, { recursive: true })
  await access(resolve(DIST_DIR, 'index.html'))

  const { chromium } = await importPlaywright()
  const browserPath = await findBrowser()
  const stamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  const runDir = resolve(OUT_DIR, stamp)
  await mkdir(runDir, { recursive: true })

  const tokens = {
    student: await login('student'),
    teacher: await login('teacher'),
  }
  const ids = await resolveIds(tokens)
  const selectedRoutes = ROUTE_FILTER.length
    ? routes.filter((route) => ROUTE_FILTER.includes(route.slug))
    : routes
  if (!selectedRoutes.length) {
    throw new Error(`QA_ROUTES did not match any route slug: ${ROUTE_FILTER.join(', ')}`)
  }

  const server = await createQaServer()
  const browser = await chromium.launch({
    executablePath: browserPath,
    headless: true,
    args: ['--disable-gpu', '--no-first-run', '--no-default-browser-check'],
  })
  const results = []

  try {
    for (const viewport of viewports) {
      for (const route of selectedRoutes) {
        const vuePath = typeof route.vue === 'function' ? route.vue({ ids }) : route.vue
        const referenceUrl = `${REFERENCE_ORIGIN}/${route.reference}`
        const vueUrl = `${QA_ORIGIN}${vuePath}`
        const referenceFile = resolve(runDir, `${viewport.key}-${route.slug}-reference.png`)
        const vueFile = resolve(runDir, `${viewport.key}-${route.slug}-vue.png`)
        const result = {
          route: route.slug,
          viewport: viewport.key,
          referenceUrl,
          vueUrl,
          reference: referenceFile,
          vue: vueFile,
          vuePath,
        }

        try {
          result.referenceResult = await capturePage(browser, viewport, { url: referenceUrl, kind: 'reference' }, null, referenceFile, route)
        } catch (error) {
          result.referenceResult = { status: 'failed', error: String(error?.message || error) }
        }

        try {
          result.vueResult = await capturePage(browser, viewport, { url: vueUrl, kind: 'vue' }, route.role ? tokens[route.role] : null, vueFile, route)
        } catch (error) {
          result.vueResult = { status: 'failed', error: String(error?.message || error) }
        }

        results.push(result)
      }
    }
  } finally {
    await browser.close()
    server.close()
  }

  const summary = {
    generatedAt: new Date().toISOString(),
    appOrigin: QA_ORIGIN,
    backendOrigin: APP_ORIGIN,
    referenceOrigin: REFERENCE_ORIGIN,
    readyTimeoutMs: READY_TIMEOUT_MS,
    settleMs: SETTLE_MS,
    routeFilter: ROUTE_FILTER,
    browserPath,
    ids,
    results,
  }
  const summaryPath = resolve(runDir, 'summary.json')
  await writeFile(summaryPath, `${JSON.stringify(summary, null, 2)}\n`)
  await writeFile(resolve(runDir, 'summary.md'), renderMarkdownSummary(summary))
  console.log(summaryPath)
}

function renderMarkdownSummary(summary) {
  const rows = summary.results.map((result) => {
    const reference = result.referenceResult.status === 'captured' ? 'captured' : `failed: ${result.referenceResult.error}`
    const vue = result.vueResult.status === 'captured' ? 'captured' : `failed: ${result.vueResult.error}`
    const vueInspection = result.vueResult.inspection
    const issues = []
    if (vueInspection?.overflowX) issues.push('horizontal overflow')
    if (vueInspection?.canvasCount && vueInspection.blankCanvasCount) issues.push(`${vueInspection.blankCanvasCount}/${vueInspection.canvasCount} blank canvas`)
    if (vueInspection?.brokenImageCount) issues.push(`${vueInspection.brokenImageCount} broken image`)
    if (result.vueResult.diagnostics?.consoleErrors?.length) issues.push(`${result.vueResult.diagnostics.consoleErrors.length} console warning/error`)
    return `| ${result.viewport} | ${result.route} | ${reference} | ${vue} | ${issues.join(', ') || 'none'} |`
  })
  return `# Reference Visual QA Summary

- Generated: ${summary.generatedAt}
- Reference: ${summary.referenceOrigin}
- App: ${summary.appOrigin}
- Ready timeout: ${summary.readyTimeoutMs}ms
- Settle wait: ${summary.settleMs}ms

| Viewport | Route | Reference | Vue | Vue issues |
| --- | --- | --- | --- | --- |
${rows.join('\n')}
`
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
