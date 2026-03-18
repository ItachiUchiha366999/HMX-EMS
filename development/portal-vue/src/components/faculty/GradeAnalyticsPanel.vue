<template>
  <div class="grade-analytics-panel">
    <!-- Loading state -->
    <template v-if="loading">
      <SkeletonLoader height="240px" />
      <SkeletonLoader height="16px" width="60%" />
      <SkeletonLoader height="16px" width="40%" />
      <SkeletonLoader height="16px" width="50%" />
    </template>

    <template v-else-if="analytics">
      <!-- Grade distribution chart -->
      <ChartWrapper
        type="bar"
        :title="'Grade Distribution'"
        :series="chartSeries"
        :categories="chartCategories"
        :height="200"
      />

      <!-- KPI summary -->
      <div class="grade-analytics-panel__kpis">
        <div class="grade-analytics-panel__kpi">
          <span class="grade-analytics-panel__kpi-label">Class Average</span>
          <span class="grade-analytics-panel__kpi-value">{{ analytics.average }}</span>
        </div>
        <div class="grade-analytics-panel__kpi-row">
          <div class="grade-analytics-panel__kpi grade-analytics-panel__kpi--pass">
            <span class="grade-analytics-panel__kpi-label">Pass</span>
            <span class="grade-analytics-panel__kpi-value grade-analytics-panel__kpi-value--success">{{ analytics.pass_count }}</span>
          </div>
          <div class="grade-analytics-panel__kpi grade-analytics-panel__kpi--fail">
            <span class="grade-analytics-panel__kpi-label">Fail</span>
            <span class="grade-analytics-panel__kpi-value grade-analytics-panel__kpi-value--error">{{ analytics.fail_count }}</span>
          </div>
        </div>
        <div class="grade-analytics-panel__kpi grade-analytics-panel__kpi--at-risk">
          <span class="grade-analytics-panel__kpi-label">At-risk</span>
          <span class="grade-analytics-panel__kpi-value grade-analytics-panel__kpi-value--error grade-analytics-panel__kpi-value--bold">{{ analytics.at_risk_count }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ChartWrapper from '../shared/ChartWrapper.vue'
import SkeletonLoader from '../shared/SkeletonLoader.vue'

const props = defineProps({
  analytics: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

const chartCategories = computed(() => {
  if (!props.analytics?.distribution) return []
  return Object.keys(props.analytics.distribution)
})

const chartSeries = computed(() => {
  if (!props.analytics?.distribution) return []
  return [{ name: 'Students', data: Object.values(props.analytics.distribution) }]
})
</script>

<style scoped>
.grade-analytics-panel {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.grade-analytics-panel__kpis {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.grade-analytics-panel__kpi {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.grade-analytics-panel__kpi-row {
  display: flex;
  gap: var(--space-4);
}

.grade-analytics-panel__kpi-row .grade-analytics-panel__kpi {
  flex: 1;
}

.grade-analytics-panel__kpi-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.grade-analytics-panel__kpi-value {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
}

.grade-analytics-panel__kpi-value--success {
  color: var(--success);
}

.grade-analytics-panel__kpi-value--error {
  color: var(--error);
}

.grade-analytics-panel__kpi-value--bold {
  font-weight: var(--font-semibold);
}

@media (max-width: 1023px) {
  .grade-analytics-panel {
    width: 100%;
  }
}
</style>
