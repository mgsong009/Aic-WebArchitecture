<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const initialRole = route.query.role === 'teacher' ? 'teacher' : 'student'
const role = ref(initialRole)
const userId = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const metrics = [
  { key: 'PI', full: 'Prompt Insight', desc: '질문의 깊이와 비판성', color: '#3B82F6' },
  { key: 'UI', full: 'User Intervention', desc: 'AI 초안 수정 개입 정도', color: '#F97316' },
  { key: 'OI', full: 'Originality Index', desc: '자기 관점과 독창성', color: '#10B981' },
  { key: 'AIC', full: '종합 협업 지수', desc: 'PI + UI + OI 가중 종합', color: '#60A5FA' },
]

const roleOptions = [
  { value: 'student', label: '학생', desc: 'Student' },
  { value: 'teacher', label: '교사', desc: 'Teacher' },
]

const roleHint = computed(() => (role.value === 'teacher' ? 'teacher_kim' : 'student_001'))

async function handleLogin() {
  if (!userId.value || !password.value) {
    error.value = '아이디와 비밀번호를 입력하세요.'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await auth.login(userId.value, password.value, role.value)
    router.push(role.value === 'teacher' ? '/teacher/dashboard' : '/student/dashboard')
  } catch (e) {
    error.value = '아이디, 비밀번호, 또는 역할이 올바르지 않습니다.'
  } finally {
    loading.value = false
  }
}

function selectRole(nextRole) {
  role.value = nextRole
  error.value = ''
}

function demoLogin(nextRole) {
  role.value = nextRole
  userId.value = nextRole === 'student' ? 'student_001' : 'teacher_kim'
  password.value = 'password123'
  handleLogin()
}
</script>

<template>
  <div class="login-root">
    <section class="login-left" aria-label="AIC Index 소개">
      <RouterLink class="ll-brand" to="/">
        <span class="ll-brand-icon">AIC</span>
        <span class="ll-brand-text">AIC <span>Index</span></span>
      </RouterLink>

      <div class="ll-content">
        <h1 class="ll-title">
          AI 협업 역량을<br />
          데이터로 읽다
        </h1>
        <p class="ll-subtitle">
          결과물보다 과정을 분석해 학생의 질문, 개입, 독창성을 평가합니다.
        </p>
        <div class="metric-cards">
          <div v-for="metric in metrics" :key="metric.key" class="metric-card-mini">
            <span class="metric-dot" :style="{ background: metric.color }"></span>
            <span class="metric-mini-label">{{ metric.key }} · {{ metric.full }}</span>
            <span class="metric-mini-desc">{{ metric.desc }}</span>
          </div>
        </div>
      </div>

      <div class="ll-footer">© 2025 AIC Index Platform</div>
    </section>

    <main class="login-right">
      <section class="login-form-card" aria-label="로그인 양식">
        <div class="lf-header">
          <h2 class="lf-title">환영합니다</h2>
          <p class="lf-subtitle">계속하려면 로그인하세요</p>
        </div>

        <div class="role-selector" role="tablist" aria-label="역할 선택">
          <button
            v-for="option in roleOptions"
            :key="option.value"
            class="role-option"
            :class="{ active: role === option.value }"
            type="button"
            role="tab"
            :aria-selected="role === option.value"
            @click="selectRole(option.value)"
          >
            <span class="role-option-label">{{ option.label }}</span>
            <span class="role-option-desc">{{ option.desc }}</span>
          </button>
        </div>

        <div v-if="error" class="form-error">{{ error }}</div>

        <div class="form-fields">
          <div class="field-group">
            <label class="field-label" for="login-id">아이디 (학번/교번)</label>
            <input
              id="login-id"
              v-model="userId"
              class="field-input"
              type="text"
              :placeholder="roleHint"
              autocomplete="username"
              @keyup.enter="handleLogin"
            />
          </div>
          <div class="field-group">
            <label class="field-label" for="login-password">비밀번호</label>
            <input
              id="login-password"
              v-model="password"
              class="field-input"
              type="password"
              placeholder="비밀번호를 입력하세요"
              autocomplete="current-password"
              @keyup.enter="handleLogin"
            />
          </div>
        </div>

        <button class="btn-login" type="button" :disabled="loading" @click="handleLogin">
          {{ loading ? '로그인 중...' : '로그인하기' }}
        </button>

        <div class="divider">
          <div class="divider-line"></div>
          <span class="divider-text">데모 빠른 접속</span>
          <div class="divider-line"></div>
        </div>

        <div class="demo-btns">
          <button class="demo-btn demo-student" type="button" :disabled="loading" @click="demoLogin('student')">
            학생 데모
          </button>
          <button class="demo-btn demo-teacher" type="button" :disabled="loading" @click="demoLogin('teacher')">
            교사 데모
          </button>
        </div>

        <div class="lf-footer">
          <RouterLink to="/">홈으로 돌아가기</RouterLink>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.login-root {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(360px, 1fr) minmax(420px, 1fr);
  background: #0b1526;
}

.login-left {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: clamp(var(--space-8), 5vw, 48px);
  background: linear-gradient(145deg, #0b1526, var(--color-aic));
  color: white;
}

.login-left::before {
  content: '';
  position: absolute;
  right: 0;
  bottom: 0;
  width: min(52vw, 440px);
  height: min(52vw, 440px);
  background:
    linear-gradient(90deg, rgba(59, 130, 246, 0.11) 1px, transparent 1px),
    linear-gradient(0deg, rgba(16, 185, 129, 0.09) 1px, transparent 1px);
  background-size: 32px 32px;
  opacity: 0.8;
  mask-image: linear-gradient(135deg, transparent 15%, black 78%);
}

.ll-brand {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  width: fit-content;
}

.ll-brand-icon {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--color-pi), var(--color-oi));
  font-size: var(--font-size-xs);
  font-weight: 800;
}

.ll-brand-text {
  font-size: var(--font-size-xl);
  font-weight: 800;
}

.ll-brand-text span {
  font-weight: 300;
  opacity: 0.72;
}

.ll-content {
  position: relative;
  z-index: 1;
  max-width: 520px;
}

.ll-title {
  font-size: clamp(34px, 5vw, 52px);
  line-height: 1.18;
  font-weight: 800;
  margin-bottom: var(--space-5);
}

.ll-subtitle {
  max-width: 420px;
  color: rgba(255, 255, 255, 0.58);
  font-size: var(--font-size-lg);
  line-height: 1.72;
  margin-bottom: var(--space-8);
}

.metric-cards {
  display: grid;
  gap: var(--space-3);
}

.metric-card-mini {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: var(--space-3);
  padding: 14px 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.05);
}

.metric-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
}

.metric-mini-label {
  color: rgba(255, 255, 255, 0.78);
  font-size: var(--font-size-sm);
  font-weight: 700;
}

.metric-mini-desc,
.ll-footer {
  color: rgba(255, 255, 255, 0.36);
  font-size: var(--font-size-xs);
}

.login-right {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(var(--space-6), 5vw, 48px);
  background: var(--bg-primary);
}

.login-form-card {
  width: 100%;
  max-width: 420px;
  padding: clamp(var(--space-6), 5vw, 44px);
  border: 1px solid var(--border-light);
  border-radius: 20px;
  background: white;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
}

.lf-header {
  margin-bottom: var(--space-6);
}

.lf-title {
  color: var(--text-primary);
  font-size: var(--font-size-3xl);
  font-weight: 800;
  line-height: 1.2;
}

.lf-subtitle {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  margin-top: var(--space-1);
}

.role-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-2);
  padding: 4px;
  border-radius: var(--radius-lg);
  background: var(--color-gray-100);
  margin-bottom: var(--space-6);
}

.role-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  transition: background var(--transition-fast), color var(--transition-fast), box-shadow var(--transition-fast);
}

.role-option.active {
  background: var(--bg-surface);
  color: var(--color-aic);
  box-shadow: var(--shadow-xs);
}

.role-option-label {
  font-size: var(--font-size-sm);
  font-weight: 800;
}

.role-option-desc {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.form-error {
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: #fee2e2;
  color: #b91c1c;
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-4);
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  color: var(--text-secondary);
  font-size: var(--font-size-xs);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.field-input {
  width: 100%;
  padding: 11px 14px;
  border: 1.5px solid var(--border-light);
  border-radius: var(--radius-md);
  background: white;
  color: var(--text-primary);
  font-size: var(--font-size-base);
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.field-input:focus {
  border-color: var(--color-pi);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.btn-login {
  width: 100%;
  min-height: 46px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--color-aic), var(--color-aic-light));
  color: white;
  font-size: var(--font-size-md);
  font-weight: 800;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), opacity var(--transition-fast);
  margin-bottom: var(--space-4);
}

.btn-login:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(30, 58, 95, 0.32);
}

.btn-login:disabled,
.demo-btn:disabled {
  opacity: 0.68;
  cursor: not-allowed;
}

.divider {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.divider-line {
  flex: 1;
  height: 1px;
  background: var(--border-light);
}

.divider-text {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
  font-weight: 700;
}

.demo-btns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
  margin-bottom: var(--space-5);
}

.demo-btn {
  min-height: 40px;
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  font-weight: 800;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.demo-student {
  background: var(--color-pi-pale);
  color: #1d4ed8;
}

.demo-teacher {
  background: var(--color-ui-pale);
  color: #c2410c;
}

.lf-footer {
  text-align: center;
}

.lf-footer a {
  color: var(--color-pi);
  font-size: var(--font-size-sm);
  font-weight: 700;
}

@media (max-width: 860px) {
  .login-root {
    grid-template-columns: 1fr;
  }

  .login-left {
    display: none;
  }

  .login-right {
    min-height: 100vh;
    padding: var(--space-5);
  }
}

@media (max-width: 420px) {
  .demo-btns {
    grid-template-columns: 1fr;
  }
}
</style>
