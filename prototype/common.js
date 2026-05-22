/**
 * AIC Platform — Common Layout & Navigation
 * Handles sidebar, routing, and shared UI components
 */

/* ============================================================
   Router — SPA-style navigation (hash-based)
   ============================================================ */
const AIC_ROUTES = {
  // Public
  '/':              'landing',
  '/login':         'login',
  '/403':           'error-403',
  '/404':           'error-404',

  // Student
  '/student/dashboard':        'student-dashboard',
  '/student/assignment':       'student-assignment',
  '/student/growth':           'student-growth',
  '/student/feedback':         'student-feedback',

  // Teacher
  '/teacher/dashboard':        'teacher-dashboard',
  '/teacher/students':         'teacher-students',
  '/teacher/student-detail':   'teacher-student-detail',
  '/teacher/risk':             'teacher-risk',
  '/teacher/assignment-analytics': 'teacher-assignment-analytics',
  '/teacher/advanced':         'teacher-advanced',
};

function getHash() {
  return window.location.hash.slice(1) || '/';
}

function navigate(path) {
  window.location.hash = path;
}

function initRouter() {
  window.addEventListener('hashchange', () => handleRoute(getHash()));
  handleRoute(getHash());
}

function handleRoute(path) {
  // Update active nav links
  document.querySelectorAll('.nav-item[data-route]').forEach(el => {
    el.classList.toggle('active', el.dataset.route === path);
  });
  // Update breadcrumbs
  updateBreadcrumb(path);
}

function updateBreadcrumb(path) {
  const breadcrumbMap = {
    '/student/dashboard':    ['Student', 'Dashboard'],
    '/student/assignment':   ['Student', 'Assignment Result'],
    '/student/growth':       ['Student', 'Growth Analysis'],
    '/student/feedback':     ['Student', 'Feedback Guide'],
    '/teacher/dashboard':    ['Teacher', 'Dashboard'],
    '/teacher/students':     ['Teacher', 'Student List'],
    '/teacher/student-detail': ['Teacher', 'Student Detail'],
    '/teacher/risk':         ['Teacher', 'Risk Students'],
    '/teacher/assignment-analytics': ['Teacher', 'Assignment Analytics'],
    '/teacher/advanced':     ['Teacher', 'Advanced Analytics'],
  };
  const el = document.getElementById('breadcrumb');
  if (!el) return;
  const parts = breadcrumbMap[path] || [];
  el.innerHTML = parts.map((p, i) =>
    i < parts.length - 1
      ? `<span class="breadcrumb-item">${p}</span><span class="breadcrumb-sep">›</span>`
      : `<span class="breadcrumb-item active">${p}</span>`
  ).join('');
}

/* ============================================================
   Sidebar Builder
   ============================================================ */
function buildSidebar(role, currentPage) {
  const studentNav = [
    { route: '/student/dashboard', icon: icons.grid, label: 'Dashboard' },
    { route: '/student/assignment', icon: icons.file, label: 'Assignment Detail' },
    { route: '/student/growth',    icon: icons.trendUp, label: 'Growth Analysis' },
    { route: '/student/feedback',  icon: icons.lightbulb, label: 'Feedback Guide' },
  ];

  const teacherNav = [
    { route: '/teacher/dashboard',  icon: icons.grid, label: 'Dashboard' },
    { route: '/teacher/students',   icon: icons.users, label: 'Student List' },
    { route: '/teacher/student-detail', icon: icons.userSearch, label: 'Student Detail' },
    { route: '/teacher/risk',       icon: icons.alertTriangle, label: 'Risk Students', badge: 4 },
    { route: '/teacher/assignment-analytics', icon: icons.barChart, label: 'Assignment Analytics' },
    { route: '/teacher/advanced',   icon: icons.cpu, label: 'Advanced Analytics' },
  ];

  const navItems = role === 'teacher' ? teacherNav : studentNav;
  const roleLabel = role === 'teacher' ? 'Teacher' : 'Student';
  const userName  = role === 'teacher' ? 'Prof. Kim' : '김민준';
  const userInitial = role === 'teacher' ? 'K' : '민';

  return `
<aside class="app-sidebar" id="sidebar">
  <div class="sidebar-logo" onclick="navigate('/')">
    <div class="sidebar-logo-icon">AIC</div>
    <span class="sidebar-logo-text">AIC <span>Index</span></span>
  </div>

  <div class="sidebar-role-badge">${roleLabel}</div>

  <nav class="sidebar-nav">
    <div class="nav-section-label">Navigation</div>
    ${navItems.map(item => `
      <a class="nav-item${item.route === currentPage ? ' active' : ''}"
         data-route="${item.route}"
         href="${'#' + item.route}">
        ${item.icon}
        <span>${item.label}</span>
        ${item.badge ? `<span class="nav-badge">${item.badge}</span>` : ''}
      </a>
    `).join('')}
  </nav>

  <div class="sidebar-user">
    <div class="user-avatar">${userInitial}</div>
    <div class="user-info">
      <div class="user-name">${userName}</div>
      <div class="user-role">${roleLabel} · CS101</div>
    </div>
    ${icons.chevronRight}
  </div>
</aside>`;
}

/* ============================================================
   Header Builder
   ============================================================ */
function buildHeader(pageTitle, pageSubtitle) {
  return `
<header class="app-header">
  <div class="header-breadcrumb" id="breadcrumb"></div>
  <div class="header-actions">
    <div class="header-search">
      ${icons.searchSm}
      <input type="text" placeholder="Search...">
    </div>
    <div class="icon-btn" title="Notifications">
      ${icons.bell}
      <span class="badge"></span>
    </div>
    <div class="icon-btn" title="Settings">
      ${icons.settings}
    </div>
  </div>
</header>`;
}

/* ============================================================
   SVG Icons (Lucide-style)
   ============================================================ */
const icons = {
  grid: `<svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>`,
  file: `<svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10,9 9,9 8,9"/></svg>`,
  trendUp: `<svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`,
  lightbulb: `<svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21h6"/><path d="M12 3a6 6 0 0 1 6 6c0 2.22-1.2 4.16-3 5.2V17H9v-2.8A6 6 0 0 1 6 9a6 6 0 0 1 6-6z"/></svg>`,
  users: `<svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
  userSearch: `<svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><circle cx="19" cy="17" r="3"/><line x1="21.5" y1="19.5" x2="23" y2="21"/></svg>`,
  alertTriangle: `<svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  barChart: `<svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>`,
  cpu: `<svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>`,
  bell: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>`,
  settings: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>`,
  searchSm: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`,
  chevronRight: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="2"><polyline points="9,18 15,12 9,6"/></svg>`,
  arrowUp: `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5,12 12,5 19,12"/></svg>`,
  arrowDown: `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19,12 12,19 5,12"/></svg>`,
  info: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
  checkCircle: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20,6 9,17 4,12"/></svg>`,
  xCircle: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
  filter: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46 22,3"/></svg>`,
  download: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7,10 12,15 17,10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`,
  edit: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>`,
  eye: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`,
  star: `<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26 12,2"/></svg>`,
};

/* ============================================================
   Score Donut Chart (SVG-based, no library needed)
   ============================================================ */
function createDonutChart(score, maxScore, color, label, size = 160) {
  const r = (size / 2) * 0.75;
  const cx = size / 2;
  const cy = size / 2;
  const circumference = 2 * Math.PI * r;
  const pct = score / maxScore;
  const dashOffset = circumference * (1 - pct);

  return `
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <circle cx="${cx}" cy="${cy}" r="${r}"
    fill="none" stroke="#E5E7EB" stroke-width="${size * 0.1}"/>
  <circle cx="${cx}" cy="${cy}" r="${r}"
    fill="none" stroke="${color}" stroke-width="${size * 0.1}"
    stroke-dasharray="${circumference}"
    stroke-dashoffset="${dashOffset}"
    stroke-linecap="round"
    transform="rotate(-90 ${cx} ${cy})"
    style="transition: stroke-dashoffset 1s cubic-bezier(0.4,0,0.2,1)"/>
  <text x="${cx}" y="${cy - 6}" text-anchor="middle" fill="#1F2937"
    font-size="${size * 0.17}px" font-weight="800" font-family="Inter,sans-serif">${score}</text>
  <text x="${cx}" y="${cy + 12}" text-anchor="middle" fill="#9CA3AF"
    font-size="${size * 0.09}px" font-weight="500" font-family="Inter,sans-serif">${label}</text>
</svg>`;
}

/* ============================================================
   AIC Metric Bars
   ============================================================ */
function createMetricBars(pi, ui, oi, topic) {
  const bars = [
    { label: 'PI', value: pi,    color: 'pi',    hex: '#3B82F6' },
    { label: 'UI', value: ui,    color: 'ui',    hex: '#F97316' },
    { label: 'OI', value: oi,    color: 'oi',    hex: '#10B981' },
    { label: 'TS', value: topic, color: 'topic', hex: '#8B5CF6' },
  ];

  return `
<div class="score-bar-group">
  ${bars.map(b => `
    <div class="score-bar-item">
      <span class="score-bar-label" style="color:${b.hex}">${b.label}</span>
      <div class="score-bar-track">
        <div class="score-bar-fill ${b.color}" style="width:${b.value}%"></div>
      </div>
      <span class="score-bar-value" style="color:${b.hex}">${b.value}</span>
    </div>
  `).join('')}
</div>`;
}

/* ============================================================
   Status helper
   ============================================================ */
function getStatusClass(score) {
  if (score >= 80) return { cls: 'status-excellent', text: 'Excellent' };
  if (score >= 65) return { cls: 'status-good',      text: 'Good' };
  if (score >= 50) return { cls: 'status-average',   text: 'Average' };
  return { cls: 'status-risk', text: 'Risk' };
}

function getStatusBadge(score) {
  const s = getStatusClass(score);
  return `<span class="status-badge ${s.cls}">${s.text}</span>`;
}

/* ============================================================
   Mobile sidebar toggle
   ============================================================ */
function initMobileToggle() {
  const toggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', e => {
      if (!sidebar.contains(e.target) && !toggle.contains(e.target))
        sidebar.classList.remove('open');
    });
  }
}

/* ============================================================
   Export
   ============================================================ */
window.AIC = {
  buildSidebar,
  buildHeader,
  createDonutChart,
  createMetricBars,
  getStatusBadge,
  getStatusClass,
  navigate,
  initRouter,
  icons,
};
