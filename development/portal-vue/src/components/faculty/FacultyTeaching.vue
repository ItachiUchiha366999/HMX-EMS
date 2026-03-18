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
        <div class="placeholder-content">
          <span class="material-symbols-outlined placeholder-icon">edit_note</span>
          <p>Grade entry coming soon</p>
        </div>
      </template>

      <template #students>
        <div class="placeholder-content">
          <span class="material-symbols-outlined placeholder-icon">group</span>
          <p>Student list coming soon</p>
        </div>
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

const route = useRoute()
const { getTodayClasses } = useFacultyApi()

const activeTab = ref(route.query.tab || 'timetable')
const todayClasses = ref([])
const loadingClasses = ref(true)
const selectedClass = ref(null)

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
</style>
