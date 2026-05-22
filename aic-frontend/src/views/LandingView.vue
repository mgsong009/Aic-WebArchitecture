<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

function goLogin() { router.push('/login') }

if (auth.isAuthenticated) {
  router.push(auth.user?.role === 'teacher' ? '/teacher/dashboard' : '/student/dashboard')
}
</script>

<template>
  <div class="landing">
    <nav class="landing-nav">
      <span class="brand">AIC Index Platform</span>
      <button class="btn-primary" @click="goLogin">로그인</button>
    </nav>

    <section class="hero">
      <div class="hero-pills">
        <span class="pill pi">PI</span>
        <span class="pill ui">UI</span>
        <span class="pill oi">OI</span>
        <span class="pill aic">AIC</span>
      </div>
      <h1>AI 협업 능력을<br /><em>정량적으로 평가하다</em></h1>
      <p class="hero-sub">Prompt Insight · User Intervention · Originality Index</p>
      <button class="btn-hero" @click="goLogin">시작하기</button>
    </section>

    <section class="features">
      <div class="feature-card" v-for="f in features" :key="f.title">
        <div class="feature-icon">{{ f.icon }}</div>
        <h3>{{ f.title }}</h3>
        <p>{{ f.desc }}</p>
      </div>
    </section>

    <section class="role-select">
      <div class="role-card" @click="goLogin">
        <span class="role-icon">🧑‍🎓</span>
        <h3>학생</h3>
        <p>내 AI 협업 점수와 성장 추이를 확인하세요</p>
      </div>
      <div class="role-card" @click="goLogin">
        <span class="role-icon">👩‍🏫</span>
        <h3>교사</h3>
        <p>반 전체 현황을 모니터링하고 피드백을 제공하세요</p>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  data: () => ({
    features: [
      { icon: '🔍', title: 'PI · Prompt Insight', desc: '학생의 질문 깊이, 비판적 사고, 복잡도를 분석합니다.' },
      { icon: '✏️', title: 'UI · User Intervention', desc: 'AI 초안에 대한 학생의 개입 정도를 측정합니다.' },
      { icon: '💡', title: 'OI · Originality Index', desc: '최종 제출물에서 독창적인 관점을 평가합니다.' },
      { icon: '📊', title: 'AIC · 종합 지수', desc: '세 지표를 종합한 AI 협업 능력 지수입니다.' },
      { icon: '📈', title: '성장 추이 분석', desc: '과제별 성장 패턴을 시각화합니다.' },
      { icon: '⚠️', title: '위험군 조기 감지', desc: '도움이 필요한 학생을 자동으로 식별합니다.' },
    ],
  }),
}
</script>

<style scoped>
.landing { min-height: 100vh; background: linear-gradient(135deg, #f0f4f8, #e8f0fe); }
.landing-nav { display: flex; justify-content: space-between; align-items: center; padding: 1rem 3rem; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.brand { font-weight: 800; font-size: 1.125rem; color: var(--color-aic); }
.btn-primary { padding: 0.5rem 1.25rem; background: var(--color-aic); color: #fff; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
.hero { text-align: center; padding: 5rem 2rem 3rem; }
.hero-pills { display: flex; gap: 0.5rem; justify-content: center; margin-bottom: 1.5rem; }
.pill { padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 700; font-size: 0.875rem; color: #fff; }
.pill.pi { background: var(--color-pi); }
.pill.ui { background: var(--color-ui); }
.pill.oi { background: var(--color-oi); }
.pill.aic { background: var(--color-aic); }
.hero h1 { font-size: 2.5rem; font-weight: 800; color: var(--text-primary); line-height: 1.2; }
.hero h1 em { color: var(--color-aic); font-style: normal; }
.hero-sub { color: var(--text-secondary); margin: 1rem 0 2rem; }
.btn-hero { padding: 0.75rem 2rem; background: var(--color-aic); color: #fff; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; font-weight: 600; }
.features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; max-width: 900px; margin: 0 auto; padding: 2rem; }
.feature-card { background: #fff; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.feature-icon { font-size: 1.5rem; margin-bottom: 0.75rem; }
.feature-card h3 { font-size: 0.9rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem; }
.feature-card p { font-size: 0.8rem; color: var(--text-secondary); line-height: 1.5; }
.role-select { display: flex; gap: 2rem; justify-content: center; padding: 2rem; }
.role-card { background: #fff; border-radius: 16px; padding: 2rem; text-align: center; cursor: pointer; box-shadow: 0 4px 16px rgba(0,0,0,0.08); transition: transform 0.2s; min-width: 220px; }
.role-card:hover { transform: translateY(-4px); }
.role-icon { font-size: 2rem; display: block; margin-bottom: 1rem; }
.role-card h3 { font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem; }
.role-card p { font-size: 0.85rem; color: var(--text-secondary); }
</style>
