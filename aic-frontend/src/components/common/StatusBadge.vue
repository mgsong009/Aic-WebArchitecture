<script setup>
const props = defineProps({ score: { type: Number, default: null } })

function statusClass(score) {
  if (score === null || score === undefined) return 'status-pending'
  if (score >= 80) return 'status-excellent'
  if (score >= 65) return 'status-good'
  if (score >= 50) return 'status-average'
  return 'status-risk'
}

function statusText(score) {
  if (score === null || score === undefined) return '대기'
  if (score >= 80) return 'Excellent'
  if (score >= 65) return 'Good'
  if (score >= 50) return 'Average'
  return 'Risk'
}
</script>

<template>
  <span class="status-badge" :class="statusClass(score)">
    {{ statusText(score) }}
  </span>
</template>
