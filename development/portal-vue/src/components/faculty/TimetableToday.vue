<template>
  <div class="timetable-today">
    <!-- Loading -->
    <template v-if="loading">
      <div v-for="n in 4" :key="n" class="timetable-skeleton">
        <SkeletonLoader height="64px" />
      </div>
    </template>

    <!-- Empty state -->
    <template v-else-if="!classes || classes.length === 0">
      <div class="timetable-empty">
        <span class="material-symbols-outlined timetable-empty-icon">event_busy</span>
        <h4 class="timetable-empty-title">No classes scheduled</h4>
        <p class="timetable-empty-body">You have no classes scheduled for today. Check back on a teaching day.</p>
      </div>
    </template>

    <!-- Class list -->
    <template v-else>
      <div
        v-for="cls in classes"
        :key="cls.name"
        :class="[
          'timetable-item',
          {
            'timetable-item--current': isCurrent(cls),
            'timetable-item--past': isPast(cls),
            'timetable-item--marked': cls.is_marked,
          },
        ]"
      >
        <div class="timetable-time">
          {{ formatTime(cls.start_time) }} - {{ formatTime(cls.end_time) }}
        </div>
        <div class="timetable-details">
          <div class="timetable-course">{{ cls.course_name }}</div>
          <div class="timetable-meta">{{ cls.section }}</div>
        </div>
        <div class="timetable-room">{{ cls.room }}</div>
        <div class="timetable-action">
          <template v-if="cls.is_marked">
            <span class="timetable-marked">
              <span class="material-symbols-outlined timetable-marked-icon">check_circle</span>
              Marked
            </span>
          </template>
          <template v-else>
            <button class="btn-primary btn-sm" @click="$emit('mark-attendance', cls)">
              Mark Attendance
            </button>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import SkeletonLoader from '../shared/SkeletonLoader.vue'

defineProps({
  classes: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['mark-attendance'])

function formatTime(timeStr) {
  if (!timeStr) return ''
  // Format "09:00:00" -> "09:00"
  return timeStr.substring(0, 5)
}

function isCurrent(cls) {
  const now = new Date()
  const [startH, startM] = (cls.start_time || '').split(':').map(Number)
  const [endH, endM] = (cls.end_time || '').split(':').map(Number)
  const currentMinutes = now.getHours() * 60 + now.getMinutes()
  const startMinutes = (startH || 0) * 60 + (startM || 0)
  const endMinutes = (endH || 0) * 60 + (endM || 0)
  return currentMinutes >= startMinutes && currentMinutes < endMinutes
}

function isPast(cls) {
  const now = new Date()
  const [endH, endM] = (cls.end_time || '').split(':').map(Number)
  const currentMinutes = now.getHours() * 60 + now.getMinutes()
  const endMinutes = (endH || 0) * 60 + (endM || 0)
  return currentMinutes >= endMinutes
}
</script>

<style scoped>
.timetable-today {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.timetable-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-default);
  border-left: 4px solid transparent;
  transition: background var(--transition-fast) var(--ease-in-out);
}

.timetable-item--current {
  border-left-color: var(--primary);
  background: var(--primary-tint);
}

.timetable-item--past {
  color: var(--gray-400);
}

.timetable-item--marked {
  background: var(--gray-50);
  opacity: 0.7;
}

.timetable-time {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: inherit;
  min-width: 100px;
}

.timetable-details {
  flex: 1;
}

.timetable-course {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: inherit;
}

.timetable-meta {
  font-size: var(--text-xs);
  color: var(--gray-500);
}

.timetable-room {
  font-size: var(--text-xs);
  color: var(--gray-500);
  min-width: 80px;
  text-align: right;
}

.timetable-action {
  min-width: 140px;
  text-align: right;
}

.timetable-marked {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-sm);
  color: var(--success);
}

.timetable-marked-icon {
  font-size: 18px;
}

.timetable-empty {
  text-align: center;
  padding: var(--space-12) var(--space-4);
}

.timetable-empty-icon {
  font-size: 48px;
  color: var(--text-muted);
}

.timetable-empty-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-top: var(--space-3);
}

.timetable-empty-body {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-top: var(--space-2);
}

.timetable-skeleton {
  margin-bottom: var(--space-2);
}

@media (max-width: 768px) {
  .timetable-item {
    flex-wrap: wrap;
  }

  .timetable-room {
    text-align: left;
    min-width: auto;
  }

  .timetable-action {
    width: 100%;
    text-align: left;
    margin-top: var(--space-2);
  }
}
</style>
