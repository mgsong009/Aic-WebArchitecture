<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api'
import AppLayout from '@/components/layout/AppLayout.vue'

const route = useRoute()
const router = useRouter()
const assignmentId = Number(route.params.assignmentId)
const loading = ref(true)
const feedback = ref(null)

onMounted(async () => {
  try {
    const { data } = await api.get(`/student/feedback/${assignmentId}`)
    feedback.value = data
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AppLayout title="피드백" subtitle="교사 코멘트와 자동 가이드">
    <div v-if="loading" class="card">불러오는 중...</div>
    <div v-else-if="feedback" class="grid">
      <div class="card">
        <h3>교사 피드백</h3>
        <p v-if="feedback.teacher_feedback?.content" class="body">
          {{ feedback.teacher_feedback.content }}
        </p>
        <p v-else class="empty">등록된 교사 피드백이 없습니다.</p>
        <div v-if="feedback.teacher_feedback?.created_at" class="date">
          작성일: {{ feedback.teacher_feedback.created_at }}
        </div>
      </div>

      <div class="card">
        <h3>강점</h3>
        <ul>
          <li v-for="(s, i) in feedback.auto_guide.strengths" :key="`s-${i}`">{{ s }}</li>
          <li v-if="!feedback.auto_guide.strengths.length">강점 항목이 아직 없습니다.</li>
        </ul>
      </div>

      <div class="card">
        <h3>개선 포인트</h3>
        <ul>
          <li v-for="(s, i) in feedback.auto_guide.improvements" :key="`i-${i}`">{{ s }}</li>
          <li v-if="!feedback.auto_guide.improvements.length">개선 포인트가 아직 없습니다.</li>
        </ul>
      </div>

      <div class="card">
        <h3>실행 팁</h3>
        <ul>
          <li v-for="(s, i) in feedback.auto_guide.tips" :key="`t-${i}`">{{ s }}</li>
          <li v-if="!feedback.auto_guide.tips.length">실행 팁이 아직 없습니다.</li>
        </ul>
      </div>
    </div>
    <div class="actions">
      <button class="btn-secondary" @click="router.push(`/student/assignments/${assignmentId}`)">
        과제 상세로 돌아가기
      </button>
    </div>
  </AppLayout>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 1.2rem;
  box-shadow: var(--shadow-sm);
}

h3 {
  margin-bottom: 0.75rem;
}

.body {
  line-height: 1.65;
  font-size: var(--text-sm);
  white-space: pre-wrap;
}

.empty {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.date {
  margin-top: 0.8rem;
  color: var(--text-secondary);
  font-size: var(--text-xs);
}

ul {
  margin: 0;
  padding-left: 1rem;
}

li {
  margin-bottom: 0.35rem;
  font-size: var(--text-sm);
  line-height: 1.55;
}

.actions {
  margin-top: 1rem;
}

.btn-secondary {
  border: 1px solid #cbd5e1;
  background: #fff;
  color: var(--text-primary);
  border-radius: 8px;
  padding: 0.55rem 0.8rem;
  cursor: pointer;
}

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
