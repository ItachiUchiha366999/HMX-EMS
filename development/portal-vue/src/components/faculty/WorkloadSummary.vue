<template>
  <div class="workload-summary">
    <template v-if="loading">
      <div class="workload-kpi-grid">
        <SkeletonLoader v-for="n in 4" :key="n" height="120px" />
      </div>
      <SkeletonLoader height="240px" />
    </template>
    <template v-else-if="isEmpty">
      <div class="empty-state">
        <span class="material-symbols-outlined empty-state-icon">work</span>
        <p class="empty-state-heading">No workload data</p>
        <p class="empty-state-body">Teaching assignments for this semester have not been published yet.</p>
      </div>
    </template>
    <template v-else>
      <!-- KPI Cards -->
      <div class="workload-kpi-grid">
        <div class="workload-kpi-card">
          <KpiCard
            label="Hours/Week"
            :value="personal.hours_per_week"
            :status="hoursStatus"
            icon="schedule"
          />
          <div class="dept-avg">Dept avg: {{ deptAvg.hours_per_week }}</div>
        </div>
        <div class="workload-kpi-card">
          <KpiCard
            label="Courses"
            :value="personal.total_courses"
            status="info"
            icon="class"
          />
          <div class="dept-avg">Dept avg: {{ deptAvg.total_courses }}</div>
        </div>
        <div class="workload-kpi-card">
          <KpiCard
            label="Credits"
            :value="personal.total_credits"
            status="info"
            icon="star"
          />
          <div class="dept-avg">Dept avg: {{ deptAvg.total_credits }}</div>
        </div>
        <div class="workload-kpi-card">
          <KpiCard
            label="Students"
            :value="personal.total_students"
            status="info"
            icon="people"
          />
          <div class="dept-avg">Dept avg: {{ deptAvg.total_students }}</div>
        </div>
      </div>

      <!-- Weekly Heatmap -->
      <ChartWrapper
        type="heatmap"
        :series="heatmapSeries"
        :categories="heatmapDays"
        :height="240"
        title="Weekly Teaching Heatmap"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import KpiCard from '../shared/KpiCard.vue'
import ChartWrapper from '../shared/ChartWrapper.vue'
import SkeletonLoader from '../shared/SkeletonLoader.vue'

const { getWorkloadSummary } = useFacultyApi()

const loading = ref(true)
const personal = ref({ hours_per_week: 0, total_courses: 0, total_credits: 0, total_students: 0 })
const deptAvg = ref({ hours_per_week: 0, total_courses: 0, total_credits: 0, total_students: 0 })
const heatmapData = ref([])

const isEmpty = computed(() =>
  personal.value.hours_per_week === 0 &&
  personal.value.total_courses === 0 &&
  heatmapData.value.length === 0
)

const hoursStatus = computed(() => {
  if (personal.value.hours_per_week > deptAvg.value.hours_per_week * 1.1) {
    return 'warning'
  }
  return 'good'
})

const heatmapDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

const heatmapSeries = computed(() => {
  // Build timeslot x day grid
  const timeSlots = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']

  return timeSlots.map(slot => ({
    name: slot,
    data: heatmapDays.map(day => {
      const occupied = heatmapData.value.find(
        h => h.day === day && h.timeslot === slot && h.occupied
      )
      return occupied ? 100 : 0
    }),
  })).reverse()
})

onMounted(async () => {
  try {
    const result = await getWorkloadSummary()
    personal.value = result.personal || personal.value
    deptAvg.value = result.department_avg || deptAvg.value
    heatmapData.value = result.heatmap || []
  } catch (e) {
    // silently handle
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-12);
  gap: var(--space-2);
}

.empty-state-icon {
  font-size: 48px;
  color: var(--gray-300);
}

.empty-state-heading {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.empty-state-body {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.workload-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.workload-kpi-card {
  position: relative;
}

.dept-avg {
  font-size: var(--text-xs);
  color: var(--gray-500);
  margin-top: var(--space-1);
  padding-left: var(--space-2);
}

@media (max-width: 1023px) {
  .workload-kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .workload-kpi-grid {
    grid-template-columns: 1fr;
  }
}
</style>
