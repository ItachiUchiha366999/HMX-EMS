<template>
  <div class="faculty-dashboard">
    <h1 class="page-title">Faculty Dashboard</h1>

    <!-- Loading state -->
    <template v-if="loading">
      <div class="kpi-grid">
        <SkeletonLoader v-for="n in 4" :key="n" height="120px" />
      </div>
      <div class="skeleton-rows">
        <SkeletonLoader v-for="n in 6" :key="n" height="48px" />
      </div>
    </template>

    <!-- Error state -->
    <template v-else-if="error">
      <div class="error-state">
        <span class="material-symbols-outlined error-icon">error_outline</span>
        <p>Unable to load data. Please refresh the page or try again later.</p>
      </div>
    </template>

    <!-- Dashboard content -->
    <template v-else>
      <TabLayout
        :tabs="dashboardTabs"
        v-model="activeTab"
      >
        <template #pending>
          <!-- KPI cards -->
          <div class="kpi-grid">
            <KpiCard
              label="Classes Today"
              :value="data.pending_tasks.classes_today"
              icon="calendar_today"
              status="info"
              @click="navigateTo('/faculty/teaching?tab=timetable')"
            />
            <KpiCard
              label="Unmarked Attendance"
              :value="data.pending_tasks.unmarked_attendance"
              icon="fact_check"
              :status="data.pending_tasks.unmarked_attendance > 0 ? 'warning' : 'good'"
              @click="navigateTo('/faculty/teaching?tab=attendance')"
            />
            <KpiCard
              label="Pending Grades"
              :value="data.pending_tasks.pending_grades"
              icon="edit_note"
              :status="data.pending_tasks.pending_grades > 0 ? 'warning' : 'good'"
              @click="navigateTo('/faculty/teaching?tab=grades')"
            />
            <KpiCard
              label="Pending Leave"
              :value="data.pending_tasks.pending_leave_requests"
              icon="pending_actions"
              status="info"
              @click="navigateTo('/faculty/work?tab=leave')"
            />
          </div>

          <!-- Today's Classes -->
          <div class="section">
            <h2 class="section-title">Today's Classes</h2>
            <TimetableToday
              :classes="data.today_classes"
              :loading="false"
              @mark-attendance="handleMarkAttendance"
            />
          </div>
        </template>

        <template #overview>
          <!-- Charts placeholder -->
          <div class="overview-charts">
            <div class="chart-placeholder">
              <span class="material-symbols-outlined">show_chart</span>
              <p>Weekly attendance trend chart will appear here when data is available.</p>
            </div>
            <div class="chart-placeholder">
              <span class="material-symbols-outlined">bar_chart</span>
              <p>Grade distribution chart will appear here when data is available.</p>
            </div>
          </div>

          <!-- Recent announcements -->
          <div class="section" v-if="data.announcements && data.announcements.length > 0">
            <h2 class="section-title">Recent Announcements</h2>
            <div
              v-for="notice in data.announcements"
              :key="notice.name"
              class="announcement-card"
            >
              <div class="announcement-header">
                <span :class="['announcement-badge', `announcement-badge--${(notice.category || '').toLowerCase()}`]">
                  {{ notice.category }}
                </span>
                <span class="announcement-date">{{ notice.posting_date }}</span>
              </div>
              <h3 class="announcement-title">{{ notice.title }}</h3>
              <p class="announcement-content">{{ notice.content }}</p>
            </div>
          </div>
        </template>
      </TabLayout>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import KpiCard from '../shared/KpiCard.vue'
import SkeletonLoader from '../shared/SkeletonLoader.vue'
import TabLayout from './TabLayout.vue'
import TimetableToday from './TimetableToday.vue'

const router = useRouter()
const { getDashboard } = useFacultyApi()

const loading = ref(true)
const error = ref(null)
const activeTab = ref('pending')
const data = ref({
  today_classes: [],
  pending_tasks: { classes_today: 0, unmarked_attendance: 0, pending_grades: 0, pending_leave_requests: 0 },
  announcements: [],
})

const dashboardTabs = [
  { id: 'pending', label: 'Pending Tasks' },
  { id: 'overview', label: 'Overview' },
]

onMounted(async () => {
  try {
    const result = await getDashboard()
    if (result) {
      data.value = result
    }
  } catch (e) {
    error.value = e.message || 'Failed to load dashboard'
  } finally {
    loading.value = false
  }
})

function navigateTo(path) {
  router.push(path)
}

function handleMarkAttendance(cls) {
  router.push(`/faculty/teaching?tab=attendance&class=${cls.name}`)
}
</script>

<style scoped>
.page-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.section {
  margin-top: var(--space-6);
}

.section-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-3);
}

.skeleton-rows {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-top: var(--space-6);
}

.error-state {
  text-align: center;
  padding: var(--space-12);
  color: var(--text-secondary);
}

.error-icon {
  font-size: 48px;
  color: var(--error);
}

.overview-charts {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  background: var(--bg-card);
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-xl);
  color: var(--text-muted);
  text-align: center;
}

.chart-placeholder .material-symbols-outlined {
  font-size: 32px;
  margin-bottom: var(--space-2);
}

.chart-placeholder p {
  font-size: var(--text-sm);
}

.announcement-card {
  padding: var(--space-4);
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-3);
}

.announcement-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.announcement-badge {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.announcement-badge--academic {
  background: var(--primary-light);
  color: var(--primary);
}

.announcement-badge--administrative {
  background: var(--gray-100);
  color: var(--gray-500);
}

.announcement-badge--emergency {
  background: var(--error-light);
  color: var(--error);
}

.announcement-date {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.announcement-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.announcement-content {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

@media (max-width: 1023px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 767px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .overview-charts {
    grid-template-columns: 1fr;
  }
}
</style>
