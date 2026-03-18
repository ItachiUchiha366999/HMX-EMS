<template>
  <div class="faculty-teaching">
    <h1 class="page-title">Teaching</h1>

    <TabLayout :tabs="teachingTabs" v-model="activeTab">
      <template #timetable>
        <TimetableGrid />
      </template>

      <template #attendance>
        <!-- Attendance: class selection or marking mode -->
        <template v-if="selectedClass">
          <button class="btn-ghost btn-sm back-btn" @click="selectedClass = null">
            <span class="material-symbols-outlined">arrow_back</span>
            Back to classes
          </button>
          <AttendanceMarker
            :classInfo="selectedClass"
            @attendance-submitted="handleAttendanceSubmitted"
          />
        </template>
        <template v-else>
          <TimetableToday
            :classes="todayClasses"
            :loading="loadingClasses"
            @mark-attendance="selectClass"
          />
        </template>
      </template>

      <template #grades>
        <div class="grades-layout">
          <FacultyGradeGrid
            v-if="selectedCourse"
            :course="selectedCourse"
            :assessmentPlan="selectedAssessmentPlan"
            @analytics-updated="refreshGradeAnalytics"
          />
          <GradeAnalyticsPanel
            v-if="selectedCourse"
            :analytics="gradeAnalytics"
            :loading="loadingAnalytics"
          />
        </div>
        <div v-if="!selectedCourse" class="placeholder-content">
          <span class="material-symbols-outlined placeholder-icon">edit_note</span>
          <p>Select a course to begin grading</p>
        </div>
      </template>

      <template #students>
        <template v-if="showAnalyticsView">
          <PerformanceAnalytics
            :course="selectedCourse"
            @back="showAnalyticsView = false"
          />
        </template>
        <template v-else>
          <StudentListView
            v-if="selectedCourse"
            :course="selectedCourse"
            @view-analytics="showAnalyticsView = true"
          />
          <div v-else class="placeholder-content">
            <span class="material-symbols-outlined placeholder-icon">group</span>
            <p>Select a course to view students</p>
          </div>
        </template>
      </template>
    </TabLayout>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import TabLayout from './TabLayout.vue'
import TimetableGrid from './TimetableGrid.vue'
import TimetableToday from './TimetableToday.vue'
import AttendanceMarker from './AttendanceMarker.vue'
import FacultyGradeGrid from './FacultyGradeGrid.vue'
import GradeAnalyticsPanel from './GradeAnalyticsPanel.vue'
import StudentListView from './StudentListView.vue'
import PerformanceAnalytics from './PerformanceAnalytics.vue'

const route = useRoute()
const { getTodayClasses, getGradeAnalytics } = useFacultyApi()

const activeTab = ref(route.query.tab || 'timetable')
const todayClasses = ref([])
const loadingClasses = ref(true)
const selectedClass = ref(null)

// Shared course state across tabs
const selectedCourse = ref('')
const selectedAssessmentPlan = ref('')
const showAnalyticsView = ref(false)

// Grade analytics for side panel
const gradeAnalytics = ref(null)
const loadingAnalytics = ref(false)

async function refreshGradeAnalytics() {
  if (!selectedCourse.value || !selectedAssessmentPlan.value) return
  loadingAnalytics.value = true
  try {
    const result = await getGradeAnalytics(selectedCourse.value, selectedAssessmentPlan.value)
    if (result) gradeAnalytics.value = result
  } catch (e) {
    // ignore
  } finally {
    loadingAnalytics.value = false
  }
}

const teachingTabs = [
  { id: 'timetable', label: 'Timetable' },
  { id: 'attendance', label: 'Attendance' },
  { id: 'grades', label: 'Grades' },
  { id: 'students', label: 'Students' },
]

onMounted(async () => {
  try {
    const result = await getTodayClasses()
    if (result) {
      todayClasses.value = result
    }

    // If a class param was passed, select it
    if (route.query.class) {
      const cls = todayClasses.value.find((c) => c.name === route.query.class)
      if (cls) {
        selectedClass.value = cls
        activeTab.value = 'attendance'
      }
    }
  } catch (e) {
    // Error handled by loading state
  } finally {
    loadingClasses.value = false
  }
})

function selectClass(cls) {
  selectedClass.value = cls
}

function handleAttendanceSubmitted() {
  selectedClass.value = null
  // Refresh today's classes to update is_marked status
  getTodayClasses().then((result) => {
    if (result) todayClasses.value = result
  })
}
</script>

<style scoped>
.page-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  margin-bottom: var(--space-4);
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  color: var(--text-muted);
  text-align: center;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: var(--space-2);
}

.placeholder-content p {
  font-size: var(--text-sm);
}

.grades-layout {
  display: flex;
  gap: var(--space-4);
}

.grades-layout > :first-child {
  flex: 1;
  min-width: 0;
}

@media (max-width: 1023px) {
  .grades-layout {
    flex-direction: column;
  }
}
</style>
