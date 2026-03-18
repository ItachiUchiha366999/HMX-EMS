<template>
  <div class="performance-analytics">
    <!-- Back button -->
    <button class="btn-ghost btn-sm back-to-students" @click="$emit('back')">
      <span class="material-symbols-outlined">arrow_back</span>
      Back to Students
    </button>

    <h2 class="performance-analytics__title">Course Performance Analytics</h2>

    <!-- Loading -->
    <template v-if="loading">
      <div class="performance-analytics__grid">
        <SkeletonLoader height="240px" />
        <SkeletonLoader height="240px" />
        <SkeletonLoader height="240px" />
        <SkeletonLoader height="240px" />
      </div>
    </template>

    <!-- Charts -->
    <template v-else-if="analytics">
      <div class="performance-analytics__grid">
        <!-- Grade Distribution -->
        <ChartWrapper
          type="bar"
          title="Grade Distribution"
          :series="gradeDistSeries"
          :categories="analytics.grade_distribution.labels"
          :height="240"
        />

        <!-- Attendance Correlation -->
        <ChartWrapper
          type="bar"
          title="Attendance vs Grade Correlation"
          :series="attendanceCorrSeries"
          :categories="analytics.attendance_correlation.labels"
          :height="240"
        />

        <!-- Assessment Trend -->
        <ChartWrapper
          type="line"
          title="Assessment Trend"
          :series="analytics.assessment_trend.series"
          :categories="analytics.assessment_trend.labels"
          :height="240"
        />

        <!-- Batch Comparison -->
        <ChartWrapper
          type="bar"
          title="Batch Comparison"
          :series="batchComparisonSeries"
          :categories="['Average Score', 'Pass Rate (%)']"
          :height="240"
        />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import ChartWrapper from '../shared/ChartWrapper.vue'
import SkeletonLoader from '../shared/SkeletonLoader.vue'

const props = defineProps({
  course: { type: String, required: true },
})

const emit = defineEmits(['back'])

const { getPerformanceAnalytics } = useFacultyApi()

const loading = ref(true)
const analytics = ref(null)

const gradeDistSeries = computed(() => {
  if (!analytics.value?.grade_distribution) return []
  return [{ name: 'Students', data: analytics.value.grade_distribution.data }]
})

const attendanceCorrSeries = computed(() => {
  if (!analytics.value?.attendance_correlation) return []
  return [{ name: 'Average Grade', data: analytics.value.attendance_correlation.data }]
})

const batchComparisonSeries = computed(() => {
  if (!analytics.value?.batch_comparison) return []
  const { current, previous } = analytics.value.batch_comparison
  return [
    { name: 'Current Batch', data: [current.average, current.pass_rate] },
    { name: 'Previous Batch', data: [previous.average, previous.pass_rate] },
  ]
})

onMounted(async () => {
  try {
    const result = await getPerformanceAnalytics(props.course)
    if (result) {
      analytics.value = result
    }
  } catch (e) {
    // Error state
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.performance-analytics {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.back-to-students {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  align-self: flex-start;
}

.performance-analytics__title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.performance-analytics__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

@media (max-width: 1023px) {
  .performance-analytics__grid {
    grid-template-columns: 1fr;
  }
}
</style>
