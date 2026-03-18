<template>
  <div :class="['stat-card', `kpi-card--${status}`]" :style="borderStyle">
    <template v-if="loading">
      <SkeletonLoader height="120px" />
    </template>
    <template v-else>
      <div :class="['stat-icon', statusIconClass]">
        <span class="material-symbols-outlined">{{ icon }}</span>
      </div>
      <div class="stat-content">
        <div class="stat-label">{{ label }}</div>
        <div class="stat-value kpi-value">{{ value }}</div>
        <div :class="['stat-change', trendClass]">
          <span class="material-symbols-outlined kpi-trend-icon">{{ trendIcon }}</span>
          {{ trendText }}
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SkeletonLoader from './SkeletonLoader.vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: '' },
  trend: { type: Number, default: 0 },
  status: { type: String, default: 'info', validator: v => ['good', 'warning', 'critical', 'info'].includes(v) },
  icon: { type: String, default: 'analytics' },
  loading: { type: Boolean, default: false },
})

const statusColorMap = {
  good: 'var(--success)',
  warning: 'var(--warning)',
  critical: 'var(--error)',
  info: 'var(--info)',
}

const statusIconClassMap = {
  good: 'success',
  warning: 'warning',
  critical: 'error',
  info: 'info',
}

const borderStyle = computed(() => ({
  borderLeft: `3px solid ${statusColorMap[props.status] || statusColorMap.info}`,
}))

const statusIconClass = computed(() => statusIconClassMap[props.status] || 'info')

const trendIcon = computed(() => {
  if (props.trend > 0) return 'trending_up'
  if (props.trend < 0) return 'trending_down'
  return 'trending_flat'
})

const trendText = computed(() => {
  if (props.trend > 0) return `+${props.trend}%`
  if (props.trend < 0) return `${props.trend}%`
  return '0%'
})

const trendClass = computed(() => {
  if (props.trend > 0) return 'kpi-trend--positive'
  if (props.trend < 0) return 'kpi-trend--negative'
  return 'kpi-trend--flat'
})
</script>

<style scoped>
.stat-card {
  transition: box-shadow var(--transition-base) var(--ease-in-out);
  background: var(--bg-card);
  border-color: var(--border-default);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
}

.kpi-value {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.stat-label {
  color: var(--text-secondary);
}

.kpi-trend-icon {
  font-size: 16px;
}

.kpi-trend--positive {
  color: var(--success);
}

.kpi-trend--negative {
  color: var(--error);
}

.kpi-trend--flat {
  color: var(--text-muted);
}
</style>
