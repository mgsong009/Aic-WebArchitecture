<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const featuresSection = ref(null)

const features = [
  {
    key: 'PI',
    title: 'PI · Prompt Insight',
    desc: '질문의 깊이, 구체성, 비판성을 분석해 AI를 다루는 사고 과정을 보여줍니다.',
    color: 'var(--color-pi)',
  },
  {
    key: 'UI',
    title: 'UI · User Intervention',
    desc: 'AI 초안에 대한 학생의 수정, 선택, 재구성 개입 정도를 측정합니다.',
    color: 'var(--color-ui)',
  },
  {
    key: 'OI',
    title: 'OI · Originality Index',
    desc: '주제 안에서 드러나는 자기 관점과 독창적 사고의 흔적을 평가합니다.',
    color: 'var(--color-oi)',
  },
  {
    key: 'AIC',
    title: 'AIC · AI Collaboration Index',
    desc: 'PI, UI, OI를 종합해 AI 협업 역량을 하나의 지수로 제공합니다.',
    color: 'var(--color-aic)',
  },
  {
    key: 'TR',
    title: '성장 추이 분석',
    desc: '과제별 시계열 변화를 통해 학생의 AI 활용 역량 성장을 추적합니다.',
    color: 'var(--color-topic)',
  },
  {
    key: 'RK',
    title: '위험군 조기 감지',
    desc: 'AI 의존도가 높거나 개입이 낮은 학생을 찾아 교사의 우선 지도를 돕습니다.',
    color: 'var(--color-danger)',
  },
]

const stats = [
  { value: '4개', label: '핵심 평가 지표' },
  { value: '실시간', label: 'AI 협업 분석' },
  { value: '2가지', label: '사용자 역할' },
  { value: '10개+', label: '분석 화면' },
]

const navLinks = ['플랫폼 소개', '지표 체계', '사용 방법', '문의']

const roles = [
  {
    role: 'student',
    title: '학생',
    desc: '내 AIC 점수와 성장 추이를 확인하고 다음 과제의 개선 방향을 살펴봅니다.',
    items: ['PI/UI/OI 점수 확인', '과제별 성장 추이', '맞춤형 피드백 가이드', '반 평균 대비 위치'],
  },
  {
    role: 'teacher',
    title: '교사',
    desc: '반 전체 현황, 학생별 AIC 수준, 위험군을 한 화면에서 추적합니다.',
    items: ['반 전체 대시보드', '학생별 상세 분석', '위험 학생 탐지', '심화 데이터 시각화'],
  },
]

const homePath = computed(() => (auth.user?.role === 'teacher' ? '/teacher/dashboard' : '/student/dashboard'))

function goLogin(role) {
  if (auth.isAuthenticated) {
    router.push(homePath.value)
    return
  }
  router.push({ path: '/login', query: role ? { role } : undefined })
}

function scrollToFeatures() {
  featuresSection.value?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <div class="landing-root">
    <nav class="landing-nav">
      <button class="nav-brand" type="button" @click="goLogin()">
        <span class="nav-brand-icon">AIC</span>
        <span class="nav-brand-text">AIC <span>Index</span></span>
      </button>
      <div class="nav-links">
        <button v-for="link in navLinks" :key="link" type="button" @click="scrollToFeatures">{{ link }}</button>
      </div>
      <div class="nav-cta">
        <button class="btn-outline-white" type="button" @click="goLogin()">로그인</button>
        <button class="btn-white" type="button" @click="goLogin()">시작하기</button>
      </div>
    </nav>

    <main>
      <section class="hero animate-fade-in">
        <div class="hero-tag">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
            <polyline points="22,12 18,12 15,21 9,3 6,12 2,12" />
          </svg>
          생성형 AI 시대의 새로운 학습 평가 패러다임
        </div>
        <div class="index-pills">
          <span class="index-pill pill-pi">PI · Prompt Insight</span>
          <span class="index-pill pill-ui">UI · User Intervention</span>
          <span class="index-pill pill-oi">OI · Originality Index</span>
          <span class="index-pill pill-aic">AIC · AI Collaboration Index</span>
        </div>
        <h1 class="hero-title">
          AI와의 협업 과정을<br />
          <span class="gradient-text">정량적으로 평가</span>하다
        </h1>
        <p class="hero-subtitle">
          결과물이 아닌 과정을 분석합니다. 학생의 노력, AI 개입, 독창성을 AIC Index로 시각화하여 교사와 학생 모두에게 의미 있는 피드백을 제공합니다.
        </p>
        <div class="hero-cta">
          <button class="btn-hero-primary" type="button" @click="goLogin()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
              <polyline points="10,17 15,12 10,7" />
              <line x1="15" y1="12" x2="3" y2="12" />
            </svg>
            로그인하여 시작하기
          </button>
          <button class="btn-hero-secondary" type="button" @click="scrollToFeatures">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12,8 12,12 14,14" />
            </svg>
            지표 설명 보기
          </button>
        </div>
        <div class="hero-stats">
          <div v-for="stat in stats" :key="stat.label" class="stat-item">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </section>

      <section id="features" ref="featuresSection" class="features">
        <div class="section-label">플랫폼 기능</div>
        <h2 class="section-title">4가지 핵심 지표로 학습 과정을 분석</h2>
        <div class="features-grid stagger">
          <article v-for="feature in features" :key="feature.title" class="feature-card animate-fade-in-up">
            <div class="feature-icon" :style="{ color: feature.color, background: `${feature.color}18` }">
              {{ feature.key }}
            </div>
            <h3 class="feature-title" :style="{ color: feature.color }">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.desc }}</p>
          </article>
        </div>
      </section>

      <section class="roles-section">
        <div class="section-label">역할 선택</div>
        <h2 class="section-title">누구로 시작하시나요?</h2>
        <div class="roles-grid">
          <article
            v-for="roleCard in roles"
            :key="roleCard.role"
            class="role-card"
            :class="roleCard.role"
            @click="goLogin(roleCard.role)"
          >
            <div class="role-mark">{{ roleCard.role === 'student' ? 'S' : 'T' }}</div>
            <h3 class="role-title">{{ roleCard.title }} <span>({{ roleCard.role === 'student' ? 'Student' : 'Teacher' }})</span></h3>
            <p class="role-desc">{{ roleCard.desc }}</p>
            <div class="role-features">
              <div v-for="item in roleCard.items" :key="item" class="role-feature-item">
                <span class="role-feature-dot"></span>{{ item }}
              </div>
            </div>
            <button class="role-cta" :class="roleCard.role" type="button">
              {{ roleCard.title }}로 입장 →
            </button>
          </article>
        </div>
      </section>
    </main>

    <footer class="landing-footer">
      <div>© 2025 AIC Index Platform. AI Collaboration Assessment System.</div>
      <div>PI · UI · OI · TopicScore · AIC</div>
    </footer>
  </div>
</template>

<style scoped>
.landing-root {
  min-height: 100vh;
  background:
    linear-gradient(90deg, rgba(59, 130, 246, 0.08) 1px, transparent 1px),
    linear-gradient(0deg, rgba(16, 185, 129, 0.06) 1px, transparent 1px),
    linear-gradient(145deg, rgba(30, 58, 95, 0.62), rgba(11, 21, 38, 0.98)),
    #0b1526;
  background-size: 44px 44px, 44px 44px, auto, auto;
  color: white;
  overflow-x: hidden;
}

.landing-nav {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-5);
  padding: var(--space-5) clamp(var(--space-5), 5vw, 60px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.nav-brand {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  color: white;
}

.nav-brand-icon {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--color-pi), var(--color-oi));
  font-size: var(--font-size-xs);
  font-weight: 800;
}

.nav-brand-text {
  font-size: var(--font-size-lg);
  font-weight: 800;
}

.nav-brand-text span {
  font-weight: 300;
  opacity: 0.7;
}

.nav-links,
.nav-cta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.nav-links button {
  color: rgba(255, 255, 255, 0.62);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.nav-links button:hover {
  color: white;
}

.btn-outline-white,
.btn-white,
.btn-hero-primary,
.btn-hero-secondary,
.role-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  border-radius: var(--radius-md);
  font-weight: 700;
  transition: transform var(--transition-fast), background var(--transition-fast), box-shadow var(--transition-fast);
}

.btn-outline-white {
  padding: var(--space-2) var(--space-4);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.8);
}

.btn-white {
  padding: var(--space-2) var(--space-4);
  background: white;
  color: var(--color-aic);
}

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: clamp(64px, 9vw, 108px) var(--space-5) 72px;
}

.hero-tag {
  padding: 5px 14px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: var(--radius-full);
  background: rgba(59, 130, 246, 0.15);
  color: var(--color-pi-light);
  font-size: var(--font-size-xs);
  font-weight: 700;
  margin-bottom: var(--space-6);
}

.index-pills {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
}

.index-pill {
  padding: 6px 12px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 700;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.pill-pi { color: #93c5fd; }
.pill-ui { color: #fdba74; }
.pill-oi { color: #6ee7b7; }
.pill-aic { color: #bfdbfe; }

.hero-title {
  max-width: 820px;
  color: white;
  font-size: clamp(36px, 6vw, 64px);
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -0.5px;
  margin-bottom: var(--space-5);
}

.gradient-text {
  background: linear-gradient(90deg, #60a5fa, #34d399, #a78bfa);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  max-width: 620px;
  color: rgba(255, 255, 255, 0.62);
  font-size: var(--font-size-lg);
  line-height: 1.75;
  margin-bottom: var(--space-10);
}

.hero-cta {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-3);
  margin-bottom: var(--space-12);
}

.btn-hero-primary,
.btn-hero-secondary {
  min-height: 46px;
  padding: 0 var(--space-8);
}

.btn-hero-primary {
  background: var(--color-pi);
  color: white;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.36);
}

.btn-hero-secondary {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: white;
}

.btn-hero-primary:hover,
.role-card:hover {
  transform: translateY(-2px);
}

.hero-stats {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-8);
  padding: var(--space-5) var(--space-8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-xl);
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
}

.stat-value {
  color: white;
  font-size: var(--font-size-2xl);
  font-weight: 800;
}

.stat-label {
  color: rgba(255, 255, 255, 0.42);
  font-size: var(--font-size-xs);
  margin-top: var(--space-1);
}

.features,
.roles-section {
  padding: 80px clamp(var(--space-5), 5vw, 60px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.section-label {
  text-align: center;
  color: var(--color-pi-light);
  font-size: var(--font-size-xs);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: var(--space-3);
}

.section-title {
  text-align: center;
  color: white;
  font-size: var(--font-size-4xl);
  line-height: 1.25;
  margin-bottom: var(--space-12);
}

.features-grid,
.roles-grid {
  display: grid;
  gap: var(--space-5);
  max-width: 1100px;
  margin: 0 auto;
}

.features-grid {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.feature-card,
.role-card {
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-xl);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.16);
}

.feature-card {
  padding: 28px;
  transition: transform var(--transition-base), background var(--transition-base), border-color var(--transition-base);
}

.feature-card:hover {
  background: rgba(255, 255, 255, 0.07);
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.feature-icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  font-weight: 800;
  margin-bottom: var(--space-4);
}

.feature-title,
.role-title {
  font-size: var(--font-size-lg);
  margin-bottom: var(--space-3);
}

.role-title span {
  color: rgba(255, 255, 255, 0.58);
  font-weight: 600;
}

.feature-desc,
.role-desc,
.role-feature-item {
  color: rgba(255, 255, 255, 0.58);
  font-size: var(--font-size-sm);
  line-height: 1.65;
}

.roles-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.role-card {
  position: relative;
  overflow: hidden;
  padding: var(--space-8);
  cursor: pointer;
  transition: transform var(--transition-base), border-color var(--transition-base), box-shadow var(--transition-base);
}

.role-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
}

.role-card.student::before {
  background: linear-gradient(90deg, var(--color-pi), var(--color-oi));
}

.role-card.teacher::before {
  background: linear-gradient(90deg, var(--color-ui), var(--color-topic));
}

.role-card:hover {
  border-color: rgba(255, 255, 255, 0.18);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28);
}

.role-mark {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.08);
  color: white;
  font-weight: 800;
  margin-bottom: var(--space-4);
}

.role-features {
  display: grid;
  gap: var(--space-2);
  margin: var(--space-5) 0 var(--space-6);
}

.role-feature-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.role-feature-dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  background: var(--color-oi);
}

.role-cta {
  min-height: 40px;
  width: 100%;
}

.role-cta.student {
  background: var(--color-pi-pale);
  color: var(--color-pi);
}

.role-cta.teacher {
  background: var(--color-ui-pale);
  color: var(--color-ui);
}

.landing-footer {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-6) clamp(var(--space-5), 5vw, 60px);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.34);
  font-size: var(--font-size-xs);
}

@media (max-width: 768px) {
  .landing-nav {
    padding: var(--space-4) var(--space-5);
  }

  .nav-links,
  .btn-outline-white {
    display: none;
  }

  .hero {
    padding-top: var(--space-12);
  }

  .hero-stats {
    gap: var(--space-5);
    width: 100%;
  }

  .features,
  .roles-section {
    padding: 60px var(--space-5);
  }

  .section-title {
    font-size: var(--font-size-3xl);
  }

  .roles-grid {
    grid-template-columns: 1fr;
  }

  .landing-footer {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .hero-cta,
  .btn-hero-primary,
  .btn-hero-secondary {
    width: 100%;
  }
}
</style>
