<template>
  <div class="timetable-grid-wrapper">
    <!-- Week navigation -->
    <div class="week-nav">
      <button class="btn-ghost btn-sm" @click="prevWeek">
        <span class="material-symbols-outlined">chevron_left</span>
        Previous
      </button>
      <span class="week-label">Week of {{ weekStart }}</span>
      <button class="btn-ghost btn-sm" @click="nextWeek">
        Next
        <span class="material-symbols-outlined">chevron_right</span>
      </button>
    </div>

    <!-- Loading state -->
    <template v-if="loading">
      <div class="grid-skeleton">
        <SkeletonLoader height="40px" />
        <SkeletonLoader v-for="n in 6" :key="n" height="64px" />
      </div>
    </template>

    <!-- Empty state -->
    <template v-else-if="!slots || slots.length === 0">
      <div class="grid-empty">
        <span class="material-symbols-outlined grid-empty-icon">event_busy</span>
        <h4 class="grid-empty-title">No classes scheduled</h4>
        <p class="grid-empty-body">You have no classes scheduled for today. Check back on a teaching day.</p>
      </div>
    </template>

    <!-- Desktop grid -->
    <template v-else>
      <div class="timetable-grid" v-if="!isMobile">
        <table class="grid-table">
          <thead>
            <tr>
              <th class="grid-time-header">Time</th>
              <th v-for="day in days" :key="day" class="grid-day-header">{{ day }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="time in timeSlots" :key="time">
              <td class="grid-time-cell">{{ time }}</td>
              <td
                v-for="day in days"
                :key="`${day}-${time}`"
                :class="[
                  'grid-slot-cell',
                  { 'grid-slot-cell--occupied': getSlot(day, time) },
                  { 'grid-slot-cell--current': isCurrentSlot(day, time) },
                ]"
                :aria-label="getSlotAriaLabel(day, time)"
              >
                <template v-if="getSlot(day, time)">
                  <div class="slot-course">{{ getSlot(day, time).course_name }}</div>
                  <div class="slot-room">{{ getSlot(day, time).room }}</div>
                </template>
                <div v-if="isCurrentSlot(day, time)" class="current-dot" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile: day-at-a-time -->
      <div class="timetable-mobile" v-else>
        <div class="day-selector">
          <button
            v-for="day in days"
            :key="day"
            :class="['day-pill', { 'day-pill--active': selectedDay === day }]"
            @click="selectedDay = day"
          >
            {{ day }}
          </button>
        </div>
        <div class="mobile-slots">
          <div
            v-for="slot in getDaySlots(selectedDay)"
            :key="`${slot.start_time}-${slot.course}`"
            class="mobile-slot"
          >
            <div class="mobile-slot-time">{{ formatTime(slot.start_time) }} - {{ formatTime(slot.end_time) }}</div>
            <div class="mobile-slot-course">{{ slot.course_name }}</div>
            <div class="mobile-slot-room">{{ slot.room }}</div>
          </div>
          <div v-if="getDaySlots(selectedDay).length === 0" class="mobile-no-slots">
            No classes on {{ selectedDay }}
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import SkeletonLoader from '../shared/SkeletonLoader.vue'

const { getWeeklyTimetable } = useFacultyApi()

const loading = ref(true)
const weekStart = ref('')
const days = ref(['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
const slots = ref([])
const selectedDay = ref('Mon')
const isMobile = ref(false)

const timeSlots = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']

function checkMobile() {
  isMobile.value = window.innerWidth < 768
}

onMounted(async () => {
  checkMobile()
  window.addEventListener('resize', checkMobile)

  // Set current day on mobile
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  selectedDay.value = dayNames[new Date().getDay()] || 'Mon'

  await fetchTimetable()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

async function fetchTimetable(start = null) {
  loading.value = true
  try {
    const result = await getWeeklyTimetable(start)
    if (result) {
      weekStart.value = result.week_start
      days.value = result.days || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
      slots.value = result.slots || []
    }
  } catch (e) {
    slots.value = []
  } finally {
    loading.value = false
  }
}

function prevWeek() {
  if (!weekStart.value) return
  const d = new Date(weekStart.value)
  d.setDate(d.getDate() - 7)
  fetchTimetable(d.toISOString().split('T')[0])
}

function nextWeek() {
  if (!weekStart.value) return
  const d = new Date(weekStart.value)
  d.setDate(d.getDate() + 7)
  fetchTimetable(d.toISOString().split('T')[0])
}

function getSlot(day, time) {
  return slots.value.find((s) => {
    const slotTime = s.start_time.substring(0, 5)
    return s.day === day && slotTime === time
  })
}

function getDaySlots(day) {
  return slots.value.filter((s) => s.day === day).sort((a, b) => a.start_time.localeCompare(b.start_time))
}

function isCurrentSlot(day, time) {
  const now = new Date()
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  const currentDay = dayNames[now.getDay()]
  if (currentDay !== day) return false

  const currentHour = String(now.getHours()).padStart(2, '0') + ':00'
  return currentHour === time
}

function getSlotAriaLabel(day, time) {
  const slot = getSlot(day, time)
  if (!slot) return `Empty slot ${day} ${time}`
  return `${slot.course_name} at ${time} in ${slot.room}`
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  return timeStr.substring(0, 5)
}
</script>

<style scoped>
.timetable-grid-wrapper {
  width: 100%;
}

.week-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.week-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.timetable-grid {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-default);
  overflow: auto;
}

.grid-table {
  width: 100%;
  border-collapse: collapse;
}

.grid-day-header {
  background: var(--gray-50);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  text-align: center;
  padding: var(--space-3);
  color: var(--text-secondary);
}

.grid-time-header {
  background: var(--gray-50);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  padding: var(--space-3);
  width: 80px;
  color: var(--text-secondary);
}

.grid-time-cell {
  background: var(--gray-50);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  padding: var(--space-3);
  width: 80px;
  color: var(--text-secondary);
}

.grid-slot-cell {
  padding: var(--space-3);
  min-height: 64px;
  border: 1px solid var(--border-subtle);
  vertical-align: top;
  position: relative;
}

.grid-slot-cell--occupied {
  background: var(--primary-tint);
  border-left: 3px solid var(--primary);
}

.grid-slot-cell--current {
  border-left: 3px solid var(--primary);
}

.slot-course {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.slot-room {
  font-size: var(--text-xs);
  color: var(--gray-500);
}

.current-dot {
  width: 8px;
  height: 8px;
  background: var(--primary);
  border-radius: 50%;
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}

/* Mobile day-at-a-time */
.day-selector {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
  overflow-x: auto;
}

.day-pill {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-full);
  border: 1px solid var(--border-default);
  background: var(--bg-card);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  cursor: pointer;
  white-space: nowrap;
}

.day-pill--active {
  background: var(--primary);
  color: var(--white);
  border-color: var(--primary);
}

.mobile-slot {
  padding: var(--space-3) var(--space-4);
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-2);
}

.mobile-slot-time {
  font-size: var(--text-xs);
  color: var(--gray-500);
}

.mobile-slot-course {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.mobile-slot-room {
  font-size: var(--text-xs);
  color: var(--gray-500);
}

.mobile-no-slots {
  text-align: center;
  padding: var(--space-8);
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.grid-empty {
  text-align: center;
  padding: var(--space-12) var(--space-4);
}

.grid-empty-icon {
  font-size: 48px;
  color: var(--text-muted);
}

.grid-empty-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-top: var(--space-3);
}

.grid-empty-body {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-top: var(--space-2);
}

.grid-skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
