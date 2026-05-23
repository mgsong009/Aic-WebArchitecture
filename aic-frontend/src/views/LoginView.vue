<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const role = ref('student')
const userId = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

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

function demoLogin(r) {
  role.value = r
  userId.value = r === 'student' ? 'student_001' : 'teacher_kim'
  password.value = 'password123'
  handleLogin()
}
</script>

<template>
  <div class="login-wrap">
    <!-- Left panel: brand -->
    <div class="login-left">
      <div class="login-brand">
        <div class="brand-logo">AIC</div>
        <div class="brand-name">Index Platform</div>
        <div class="brand-desc">AI 협업 능력을 정량적으로 측정하는 교육 분석 플랫폼</div>
      </div>
      <div class="metric-cards">
        <div class="metric-mini" v-for="m in metrics" :key="m.key" :style="{ borderColor: m.color }">
          <span class="metric-dot" :style="{ background: m.color }"></span>
          <div>
            <div class="metric-name">{{ m.key }}</div>
            <div class="metric-full">{{ m.full }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right panel: form -->
    <div class="login-right">
      <div class="login-form-wrap">
        <h2 class="form-title">로그인</h2>

        <!-- Role toggle -->
        <div class="role-toggle">
          <button :class="{ active: role === 'student' }" @click="role = 'student'">학생</button>
          <button :class="{ active: role === 'teacher' }" @click="role = 'teacher'">교사</button>
        </div>

        <div v-if="error" class="form-error">{{ error }}</div>

        <div class="form-group">
          <label>아이디 (학번/교번)</label>
          <input v-model="userId" type="text" placeholder="아이디를 입력하세요" @keyup.enter="handleLogin" />
        </div>
        <div class="form-group">
          <label>비밀번호</label>
          <input v-model="password" type="password" placeholder="비밀번호를 입력하세요" @keyup.enter="handleLogin" />
        </div>

        <button class="btn-login" :disabled="loading" @click="handleLogin">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>

        <div class="demo-btns">
          <button class="btn-demo" @click="demoLogin('student')">학생 데모</button>
          <button class="btn-demo" @click="demoLogin('teacher')">교사 데모</button>
        </div>

        <div class="back-link">
          <RouterLink to="/">← 홈으로</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data: () => ({
    metrics: [
      { key: 'PI', full: 'Prompt Insight', color: '#3B82F6' },
      { key: 'UI', full: 'User Intervention', color: '#F97316' },
      { key: 'OI', full: 'Originality Index', color: '#10B981' },
      { key: 'AIC', full: 'AI Collab Index', color: '#1E3A5F' },
    ],
  }),
}
</script>

<style scoped>
.login-wrap { display: flex; min-height: 100vh; background: var(--bg-primary); }

.login-left {
  width: 420px;
  background: var(--bg-sidebar);
  display: flex; flex-direction: column; justify-content: center;
  padding: 3rem 2.5rem; color: #fff;
}
.brand-logo { font-size: 3rem; font-weight: 900; letter-spacing: 0.2em; }
.brand-name { font-size: 1rem; opacity: 0.7; margin-bottom: 1rem; }
.brand-desc { font-size: 0.85rem; opacity: 0.6; line-height: 1.6; margin-bottom: 2rem; }

.metric-cards { display: flex; flex-direction: column; gap: 0.75rem; }
.metric-mini { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; background: rgba(255,255,255,0.07); border-radius: 8px; border-left: 3px solid; }
.metric-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.metric-name { font-weight: 700; font-size: 0.9rem; }
.metric-full { font-size: 0.75rem; opacity: 0.6; }

.login-right { flex: 1; background: var(--bg-primary); display: flex; align-items: center; justify-content: center; padding: var(--space-6); }
.login-form-wrap { background: var(--bg-surface); border: 1px solid var(--border-light); border-radius: var(--radius-xl); padding: 2.5rem; width: 400px; box-shadow: var(--shadow-lg); }
.form-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem; color: var(--text-primary); }

.role-toggle { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; background: var(--color-gray-100); padding: 4px; border-radius: var(--radius-md); }
.role-toggle button { flex: 1; padding: 0.5rem; border: none; background: transparent; border-radius: 6px; cursor: pointer; font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); transition: all 0.15s; }
.role-toggle button.active { background: var(--bg-surface); color: var(--color-aic); font-weight: 600; box-shadow: var(--shadow-xs); }

.form-error { background: #fee2e2; color: #dc2626; padding: 0.75rem; border-radius: 8px; font-size: 0.875rem; margin-bottom: 1rem; }

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); margin-bottom: 0.4rem; }
.form-group input {
  width: 100%; padding: 0.65rem 0.875rem;
  border: 1px solid var(--border-default); border-radius: var(--radius-md);
  font-size: 0.9rem; outline: none; box-sizing: border-box;
  transition: border-color 0.15s;
}
.form-group input:focus { border-color: var(--color-aic); }

.btn-login { width: 100%; padding: 0.75rem; background: var(--color-aic); color: #fff; border: 1px solid var(--color-aic); border-radius: var(--radius-md); font-size: 1rem; font-weight: 600; cursor: pointer; margin-top: 0.5rem; transition: opacity 0.15s; }
.btn-login:disabled { opacity: 0.7; }

.demo-btns { display: flex; gap: 0.5rem; margin-top: 1rem; }
.btn-demo { flex: 1; padding: 0.5rem; border: 1px solid var(--border-default); background: transparent; border-radius: var(--radius-md); cursor: pointer; font-size: 0.8rem; color: var(--text-secondary); transition: all 0.15s; font-weight: 600; }
.btn-demo:hover { border-color: var(--color-aic); color: var(--color-aic); }

.back-link { text-align: center; margin-top: 1.25rem; }
.back-link a { color: var(--text-secondary); font-size: 0.875rem; text-decoration: none; }
.back-link a:hover { color: var(--color-aic); }

@media (max-width: 760px) {
  .login-wrap {
    flex-direction: column;
  }

  .login-left {
    width: 100%;
    padding: var(--space-8) var(--space-5);
  }

  .login-right {
    width: 100%;
    padding: var(--space-5);
  }

  .login-form-wrap {
    width: 100%;
    max-width: 420px;
    padding: var(--space-6);
  }
}

@media (max-width: 420px) {
  .demo-btns {
    flex-direction: column;
  }
}
</style>
