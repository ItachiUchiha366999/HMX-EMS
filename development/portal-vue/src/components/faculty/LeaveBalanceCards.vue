<template>
  <div class="leave-balance-cards">
    <template v-if="loading">
      <div class="leave-balance-grid">
        <SkeletonLoader v-for="n in 3" :key="n" height="100px" />
      </div>
    </template>
    <template v-else>
      <div class="leave-balance-grid">
        <div
          v-for="leave in balances"
          :key="leave.leave_type"
          class="leave-card"
        >
          <div class="leave-card__label">{{ leave.leave_type }}</div>
          <div class="leave-card__value">{{ leave.used }} / {{ leave.total }}</div>
          <div class="leave-progress">
            <div
              :class="['leave-progress-fill', progressColorClass(leave)]"
              :style="{ width: progressWidth(leave) + '%' }"
            />
          </div>
        </div>
      </div>
      <button class="btn-primary leave-apply-btn" @click="$emit('apply')">
        Apply for Leave
      </button>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import SkeletonLoader from '../shared/SkeletonLoader.vue'

defineEmits(['apply'])

const { getLeaveBalance } = useFacultyApi()
const balances = ref([])
const loading = ref(true)

function progressWidth(leave) {
  if (!leave.total || leave.total === 0) return 0
  return Math.min((leave.used / leave.total) * 100, 100)
}

function progressColorClass(leave) {
  const pct = leave.total > 0 ? (leave.used / leave.total) * 100 : 0
  if (pct > 90) return 'leave-progress-fill--error'
  if (pct >= 75) return 'leave-progress-fill--warning'
  return 'leave-progress-fill--success'
}

onMounted(async () => {
  try {
    balances.value = await getLeaveBalance()
  } catch (e) {
    // silently handle
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.leave-balance-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.leave-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
}

.leave-card__label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-bottom: var(--space-1);
}

.leave-card__value {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.leave-progress {
  height: 4px;
  background: var(--gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.leave-progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-base) var(--ease-in-out);
}

.leave-progress-fill--success {
  background: var(--success);
}

.leave-progress-fill--warning {
  background: var(--warning);
}

.leave-progress-fill--error {
  background: var(--error);
}

.leave-apply-btn {
  margin-top: var(--space-2);
}

@media (max-width: 768px) {
  .leave-balance-grid {
    grid-template-columns: 1fr;
  }
}
</style>
