export const referenceStudents = [
  { id: 1, name: '강태양', user_id_str: 'STU001', aic: 88, pi: 85, ui: 90, oi: 88, topic: 91, submission_count: 5, assignment: 'A5', color: '#3B82F6' },
  { id: 2, name: '윤서연', user_id_str: 'STU002', aic: 84, pi: 82, ui: 86, oi: 84, topic: 88, submission_count: 5, assignment: 'A5', color: '#10B981' },
  { id: 3, name: '이수현', user_id_str: 'STU003', aic: 81, pi: 78, ui: 83, oi: 82, topic: 85, submission_count: 5, assignment: 'A5', color: '#8B5CF6' },
  { id: 4, name: '한승희', user_id_str: 'STU004', aic: 78, pi: 75, ui: 80, oi: 79, topic: 82, submission_count: 5, assignment: 'A5', color: '#F97316' },
  { id: 5, name: '조민준', user_id_str: 'STU005', aic: 76, pi: 74, ui: 77, oi: 77, topic: 80, submission_count: 5, assignment: 'A5', color: '#EF4444' },
  { id: 6, name: '김민준', user_id_str: 'STU006', aic: 71, pi: 72, ui: 68, oi: 75, topic: 83, submission_count: 5, assignment: 'A5', color: '#1E3A5F' },
  { id: 7, name: '박서준', user_id_str: 'STU007', aic: 70, pi: 68, ui: 72, oi: 70, topic: 74, submission_count: 5, assignment: 'A5', color: '#6B7280' },
  { id: 8, name: '최다은', user_id_str: 'STU008', aic: 68, pi: 65, ui: 70, oi: 69, topic: 72, submission_count: 5, assignment: 'A5', color: '#3B82F6' },
  { id: 9, name: '김지아', user_id_str: 'STU009', aic: 67, pi: 64, ui: 69, oi: 68, topic: 71, submission_count: 5, assignment: 'A5', color: '#10B981' },
  { id: 10, name: '이하은', user_id_str: 'STU010', aic: 65, pi: 63, ui: 67, oi: 65, topic: 70, submission_count: 5, assignment: 'A5', color: '#F97316' },
  { id: 11, name: '박민재', user_id_str: 'STU011', aic: 63, pi: 60, ui: 65, oi: 64, topic: 68, submission_count: 4, assignment: 'A5', color: '#8B5CF6' },
  { id: 12, name: '오지우', user_id_str: 'STU012', aic: 61, pi: 59, ui: 63, oi: 61, topic: 65, submission_count: 4, assignment: 'A5', color: '#6B7280' },
  { id: 13, name: '장서윤', user_id_str: 'STU013', aic: 58, pi: 55, ui: 60, oi: 59, topic: 62, submission_count: 4, assignment: 'A4', color: '#EF4444' },
  { id: 14, name: '신유진', user_id_str: 'STU014', aic: 56, pi: 53, ui: 58, oi: 57, topic: 60, submission_count: 4, assignment: 'A4', color: '#3B82F6' },
  { id: 15, name: '황지현', user_id_str: 'STU015', aic: 54, pi: 51, ui: 56, oi: 55, topic: 58, submission_count: 4, assignment: 'A4', color: '#10B981' },
  { id: 16, name: '정승호', user_id_str: 'STU016', aic: 49, pi: 55, ui: 42, oi: 49, topic: 53, submission_count: 5, assignment: 'A5', color: '#F97316', risk_types: ['UI Low'] },
  { id: 17, name: '최민서', user_id_str: 'STU017', aic: 47, pi: 50, ui: 44, oi: 46, topic: 51, submission_count: 5, assignment: 'A5', color: '#8B5CF6', risk_types: ['UI Low'] },
  { id: 18, name: '이현우', user_id_str: 'STU018', aic: 44, pi: 38, ui: 48, oi: 46, topic: 49, submission_count: 5, assignment: 'A5', color: '#EF4444', risk_types: ['PI Low'] },
  { id: 19, name: '박지수', user_id_str: 'STU019', aic: 38, pi: 32, ui: 40, oi: 41, topic: 42, submission_count: 5, assignment: 'A5', color: '#6B7280', risk_types: ['All Low'] },
]

export const referenceDashboard = {
  cls: { code: 'CS101', name: '컴퓨터과학 개론', student_count: 28, assignment_count: 5 },
  class_avg: { aic: 66.3, pi: 64.5, ui: 69.2, oi: 62.8, topic: 73.4 },
  risk_count: 4,
  excellent_count: 3,
  analyzed_count: 25,
  trend: [
    { label: 'A1', aic: 58, pi: 56, ui: 60, oi: 57, top: 70, bottom: 44 },
    { label: 'A2', aic: 61, pi: 59, ui: 63, oi: 60, top: 73, bottom: 46 },
    { label: 'A3', aic: 62, pi: 60, ui: 64, oi: 61, top: 74, bottom: 47 },
    { label: 'A4', aic: 64, pi: 62, ui: 67, oi: 63, top: 76, bottom: 48 },
    { label: 'A5', aic: 66, pi: 64.5, ui: 69.2, oi: 62.8, top: 78, bottom: 50 },
  ],
  aic_distribution: [1, 3, 6, 10, 5, 3, 0],
  top_students: referenceStudents.slice(0, 5),
  risk_students: referenceStudents.slice(-4).reverse(),
}

export const referenceActivities = [
  { name: '김민준', text: 'Assignment #5 제출', time: '2h ago', color: 'var(--color-oi)' },
  { name: '이수현', text: '분석 완료', time: '3h ago', color: 'var(--color-pi)' },
  { name: '박지수', text: '위험군 탐지됨', time: '4h ago', color: 'var(--color-danger)' },
  { name: '한승희', text: '피드백 읽음', time: '5h ago', color: 'var(--color-ui)' },
  { name: '정승호', text: '재제출 완료', time: '6h ago', color: 'var(--color-topic)' },
]

export const referenceAssignments = [
  { label: 'A1', title: 'AI 개요 리뷰', aic: 58.2, pi: 56.1, ui: 61.3, oi: 57.0, deviation: 14.2, riskRate: 22, difficulty: '보통', min: 32, q1: 42, median: 58, q3: 72, max: 84 },
  { label: 'A2', title: '알고리즘 분석', aic: 61.4, pi: 59.2, ui: 64.8, oi: 60.3, deviation: 13.1, riskRate: 18, difficulty: '쉬움', min: 36, q1: 45, median: 62, q3: 76, max: 86 },
  { label: 'A3', title: '데이터 분석 보고서', aic: 60.2, pi: 58.0, ui: 62.5, oi: 60.1, deviation: 15.8, riskRate: 28, difficulty: '어려움', min: 30, q1: 38, median: 60, q3: 78, max: 88 },
  { label: 'A4', title: '딥러닝 설계 보고서', aic: 64.1, pi: 62.0, ui: 67.3, oi: 63.0, deviation: 12.4, riskRate: 15, difficulty: '보통', min: 41, q1: 48, median: 65, q3: 80, max: 90 },
  { label: 'A5', title: '생성형 AI 윤리 에세이', aic: 66.3, pi: 64.5, ui: 69.2, oi: 62.8, deviation: 12.8, riskRate: 14, difficulty: '쉬움', min: 44, q1: 50, median: 67, q3: 82, max: 91 },
]

export const referenceAdvancedInsights = {
  clusters: [
    { label: '고역량', count: 7, color: '#10B981', points: [{ x: 0.8, y: 0.9 }, { x: 0.7, y: 0.85 }, { x: 0.9, y: 0.8 }, { x: 0.75, y: 0.95 }, { x: 0.85, y: 0.78 }, { x: 0.6, y: 0.88 }, { x: 0.92, y: 0.72 }] },
    { label: '중상위', count: 10, color: '#3B82F6', points: [{ x: 0.3, y: 0.5 }, { x: 0.4, y: 0.6 }, { x: 0.35, y: 0.55 }, { x: 0.5, y: 0.45 }, { x: 0.45, y: 0.65 }, { x: 0.2, y: 0.58 }, { x: 0.55, y: 0.42 }, { x: 0.28, y: 0.62 }, { x: 0.48, y: 0.38 }, { x: 0.38, y: 0.7 }] },
    { label: '성장형', count: 7, color: '#F97316', points: [{ x: -0.2, y: 0.1 }, { x: -0.1, y: 0.2 }, { x: 0.0, y: 0.0 }, { x: -0.3, y: 0.15 }, { x: -0.15, y: -0.1 }, { x: 0.1, y: -0.05 }, { x: -0.25, y: 0.25 }] },
    { label: '위험군', count: 4, color: '#EF4444', points: [{ x: -0.7, y: -0.6 }, { x: -0.8, y: -0.5 }, { x: -0.65, y: -0.75 }, { x: -0.75, y: -0.55 }] },
  ],
  strategies: [
    { key: 'expert', title: 'Expert', desc: '질문도 좋고 수정도 많음', count: 7, tone: 'blue' },
    { key: 'thinker', title: 'Thinker', desc: '질문은 좋지만 수정 적음', count: 6, tone: 'yellow' },
    { key: 'editor', title: 'Editor', desc: '질문은 약하나 수정 많음', count: 11, tone: 'orange' },
    { key: 'passive', title: 'Passive', desc: '질문도 약하고 수정도 적음', count: 4, tone: 'red' },
  ],
  effortSamples: [{ x: 3, y: 42 }, { x: 5, y: 48 }, { x: 7, y: 58 }, { x: 8, y: 61 }, { x: 10, y: 69 }, { x: 12, y: 73 }, { x: 15, y: 81 }, { x: 17, y: 86 }],
  topicOiSamples: [{ x: 52, y: 41 }, { x: 58, y: 46 }, { x: 62, y: 55 }, { x: 70, y: 61 }, { x: 76, y: 70 }, { x: 82, y: 75 }, { x: 88, y: 84 }],
  similarityBands: [
    { label: '유형 A', value: 38 },
    { label: '유형 B', value: 52 },
    { label: '유형 C', value: 64 },
    { label: '유형 D', value: 81 },
    { label: '유형 E', value: 89 },
  ],
  correlation: {
    pi_ui: 0.68,
    pi_oi: 0.54,
    pi_topic: 0.48,
    pi_aic: 0.82,
    ui_oi: 0.61,
    ui_topic: 0.42,
    ui_aic: 0.88,
    oi_topic: 0.72,
    oi_aic: 0.79,
    topic_aic: 0.63,
  },
}

export const referenceStudentDetail = {
  student: referenceStudents.find((student) => student.user_id_str === 'STU006'),
  latest_metrics: { aic: 71, pi: 72, ui: 68, oi: 75, topic: 83 },
  class_avg: referenceDashboard.class_avg,
  weak_metrics: ['UI'],
  rank: 7,
  total_students: 28,
  trend: [
    { label: 'A1', aic: 54, pi: 52, ui: 58, oi: 51 },
    { label: 'A2', aic: 63, pi: 60, ui: 65, oi: 64 },
    { label: 'A3', aic: 59, pi: 55, ui: 58, oi: 63 },
    { label: 'A4', aic: 66, pi: 68, ui: 70, oi: 60 },
    { label: 'A5', aic: 71, pi: 72, ui: 68, oi: 75 },
  ],
  assignments: [
    { id: 5, title: '생성형 AI 윤리 에세이', label: 'A5', submitted_at: '2025.03.18', aic: 71, pi: 72, ui: 68, oi: 75 },
    { id: 4, title: '딥러닝 모델 설계 보고서', label: 'A4', submitted_at: '2025.03.05', aic: 66, pi: 68, ui: 70, oi: 60 },
    { id: 3, title: '데이터 분석 보고서', label: 'A3', submitted_at: '2025.02.20', aic: 59, pi: 55, ui: 58, oi: 63 },
    { id: 2, title: '알고리즘 활용 분석', label: 'A2', submitted_at: '2025.02.05', aic: 63, pi: 60, ui: 65, oi: 64 },
    { id: 1, title: 'AI 개요 리뷰', label: 'A1', submitted_at: '2025.01.22', aic: 54, pi: 52, ui: 58, oi: 51 },
  ],
  teacher_feedback: {
    content: '독창적인 개인 경험 서술이 매우 인상적이었습니다. 다음 과제에서는 UI 지표 향상을 위해 AI 초안의 논리 구조를 더 적극적으로 재배치해 보세요.',
  },
  previous_feedback: [
    { assignment: 'Assignment #5', date: '2025.03.20', body: '독창적인 개인 경험 서술이 매우 인상적이었습니다. 다음에는 UI 지표 향상을 위해 AI 초안의 논리 구조를 더 적극적으로 재배치해 보세요.' },
    { assignment: 'Assignment #4', date: '2025.03.06', body: '딥러닝 개념 서술이 명확해졌습니다. PI 점수가 크게 올랐군요. 계속 이 방향으로 발전하세요.' },
    { assignment: 'Assignment #3', date: '2025.02.21', body: '이번 과제는 AI 초안을 거의 수정 없이 제출한 것 같습니다. 다음에는 자신의 목소리를 더 담아보세요.' },
  ],
}

export function scoreTone(score) {
  if (score == null) return 'pending'
  if (score >= 80) return 'excellent'
  if (score >= 65) return 'good'
  if (score >= 50) return 'average'
  return 'risk'
}

export function scoreColor(score) {
  const tone = scoreTone(score)
  return {
    excellent: 'var(--color-oi)',
    good: 'var(--color-pi)',
    average: 'var(--color-ui)',
    risk: 'var(--color-danger)',
    pending: 'var(--text-muted)',
  }[tone]
}
