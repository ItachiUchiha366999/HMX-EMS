<template>
  <div class="obe-attainment">
    <template v-if="loading">
      <SkeletonLoader height="240px" />
    </template>
    <template v-else-if="matrixData.cos.length === 0">
      <div class="empty-state">
        <span class="material-symbols-outlined empty-state-icon">grid_on</span>
        <p class="empty-state-heading">No attainment data</p>
        <p class="empty-state-body">CO/PO attainment data for your courses will appear once assessments are mapped.</p>
      </div>
    </template>
    <template v-else>
      <!-- Course selector -->
      <div v-if="courses.length > 1" class="course-selector">
        <select v-model="selectedCourse" class="form-select" @change="loadMatrix">
          <option v-for="c in courses" :key="c.name" :value="c.name">
            {{ c.course_name || c.name }}
          </option>
        </select>
      </div>

      <!-- Drill-down view -->
      <template v-if="drillDownData">
        <button class="btn-ghost btn-sm back-btn" @click="closeDrillDown">
          <span class="material-symbols-outlined">arrow_back</span>
          Back to Matrix
        </button>

        <h4 class="drill-title">Student Attainment: {{ drillDownData.co }}</h4>
        <div class="drill-table">
          <div class="drill-table__header">
            <div class="drill-table__cell drill-table__cell--name">Student</div>
            <div class="drill-table__cell drill-table__cell--value">Attainment</div>
          </div>
          <div
            v-for="stu in drillDownData.students"
            :key="stu.student"
            class="drill-table__row"
          >
            <div class="drill-table__cell drill-table__cell--name">{{ stu.student_name }}</div>
            <div class="drill-table__cell drill-table__cell--value">{{ stu.attainment_value }}</div>
          </div>
        </div>
      </template>

      <!-- Heatmap view -->
      <template v-else>
        <ChartWrapper
          type="heatmap"
          :series="heatmapSeries"
          :categories="matrixData.pos"
          :height="240"
          title="CO-PO Attainment"
        />
        <!-- CO rows for click interaction -->
        <div class="co-rows">
          <div
            v-for="(co, idx) in matrixData.cos"
            :key="co"
            class="co-row"
            @click="handleCoDrillDown(co)"
          >
            <span class="co-row__label">{{ co }}</span>
            <span class="co-row__hint">Click to view student details</span>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import ChartWrapper from '../shared/ChartWrapper.vue'
import SkeletonLoader from '../shared/SkeletonLoader.vue'

const props = defineProps({
  courses: { type: Array, default: () => [] },
})

const { getCopoMatrix, getCopoStudentDetail } = useFacultyApi()

const loading = ref(true)
const selectedCourse = ref('')
const matrixData = ref({ cos: [], pos: [], matrix: [] })
const drillDownData = ref(null)

const heatmapSeries = computed(() => {
  if (!matrixData.value.cos.length) return []
  return matrixData.value.cos.map((co, idx) => ({
    name: co,
    data: matrixData.value.matrix[idx] || [],
  })).reverse() // ApexCharts heatmap renders bottom-up
})

async function loadMatrix() {
  if (!selectedCourse.value) return
  loading.value = true
  drillDownData.value = null
  try {
    matrixData.value = await getCopoMatrix(selectedCourse.value)
  } catch (e) {
    matrixData.value = { cos: [], pos: [], matrix: [] }
  } finally {
    loading.value = false
  }
}

async function handleCoDrillDown(co) {
  try {
    const result = await getCopoStudentDetail(selectedCourse.value, co)
    drillDownData.value = result
  } catch (e) {
    // silently handle
  }
}

function closeDrillDown() {
  drillDownData.value = null
}

onMounted(async () => {
  if (props.courses.length > 0) {
    selectedCourse.value = props.courses[0].name
    await loadMatrix()
  } else {
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

.course-selector {
  margin-bottom: var(--space-4);
  max-width: 300px;
}

.co-rows {
  margin-top: var(--space-4);
}

.co-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--border-subtle, var(--gray-100));
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-1);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.co-row:hover {
  background: var(--gray-50);
}

.co-row__label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.co-row__hint {
  font-size: var(--text-xs);
  color: var(--gray-400);
}

.back-btn {
  margin-bottom: var(--space-3);
}

.drill-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-3) 0;
}

.drill-table {
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.drill-table__header {
  display: flex;
  background: var(--gray-50);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
}

.drill-table__row {
  display: flex;
  padding: var(--space-2) var(--space-3);
  border-top: 1px solid var(--border-subtle, var(--gray-100));
  font-size: var(--text-sm);
}

.drill-table__cell--name {
  flex: 2;
}

.drill-table__cell--value {
  flex: 1;
  text-align: right;
  font-weight: var(--font-semibold);
}
</style>
