<template>
  <div class="student-detail-panel">
    <!-- Loading -->
    <template v-if="loading">
      <div class="student-detail-panel__loading">
        <SkeletonLoader height="160px" />
        <SkeletonLoader height="160px" />
        <SkeletonLoader height="160px" />
      </div>
    </template>

    <template v-else-if="detail">
      <div class="student-detail-panel__sections">
        <!-- Attendance history chart -->
        <div class="student-detail-panel__section">
          <ChartWrapper
            type="line"
            title="Attendance History"
            :series="attendanceSeries"
            :categories="attendanceCategories"
            :height="160"
          />
        </div>

        <!-- Assessment marks table -->
        <div class="student-detail-panel__section">
          <h4 class="student-detail-panel__section-title">Assessment Marks</h4>
          <table class="student-detail-panel__marks-table">
            <thead>
              <tr>
                <th>Assessment</th>
                <th>Marks</th>
                <th>Grade</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="mark in detail.assessment_marks" :key="mark.assessment_name">
                <td>{{ mark.assessment_name }}</td>
                <td>{{ mark.marks }} / {{ mark.max_marks }}</td>
                <td>{{ mark.grade || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Grade trend -->
        <div class="student-detail-panel__section">
          <ChartWrapper
            type="line"
            title="Grade Trend"
            :series="trendSeries"
            :categories="trendCategories"
            :height="160"
          />
        </div>
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
  student: { type: String, required: true },
  course: { type: String, required: true },
})

const { getStudentDetail } = useFacultyApi()

const loading = ref(true)
const detail = ref(null)

const attendanceCategories = computed(() => {
  if (!detail.value?.attendance_history) return []
  return detail.value.attendance_history.map(a => a.date).reverse()
})

const attendanceSeries = computed(() => {
  if (!detail.value?.attendance_history) return []
  return [{
    name: 'Attendance',
    data: detail.value.attendance_history.map(a => a.status === 'Present' ? 1 : 0).reverse(),
  }]
})

const trendCategories = computed(() => {
  if (!detail.value?.grade_trend) return []
  return detail.value.grade_trend.map(t => t.assessment_name)
})

const trendSeries = computed(() => {
  if (!detail.value?.grade_trend) return []
  return [{
    name: 'Marks %',
    data: detail.value.grade_trend.map(t => t.marks_percentage),
  }]
})

onMounted(async () => {
  try {
    const result = await getStudentDetail(props.student, props.course)
    if (result) {
      detail.value = result
    }
  } catch (e) {
    // handled by empty state
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.student-detail-panel {
  background: var(--gray-50);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
}

.student-detail-panel__loading {
  display: flex;
  gap: var(--space-4);
}

.student-detail-panel__sections {
  display: flex;
  gap: var(--space-4);
}

.student-detail-panel__section {
  flex: 1;
  min-width: 0;
}

.student-detail-panel__section-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
}

.student-detail-panel__marks-table {
  width: 100%;
  font-size: var(--text-sm);
  border-collapse: collapse;
}

.student-detail-panel__marks-table th {
  text-align: left;
  font-weight: var(--font-semibold);
  color: var(--gray-500);
  font-size: var(--text-xs);
  text-transform: uppercase;
  padding: var(--space-1) var(--space-2);
  border-bottom: 1px solid var(--border-subtle, var(--gray-200));
}

.student-detail-panel__marks-table td {
  padding: var(--space-1) var(--space-2);
  border-bottom: 1px solid var(--border-subtle, var(--gray-100));
}

@media (max-width: 767px) {
  .student-detail-panel__sections {
    flex-direction: column;
  }

  .student-detail-panel__loading {
    flex-direction: column;
  }
}
</style>
