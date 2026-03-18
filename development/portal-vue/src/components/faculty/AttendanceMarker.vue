<template>
  <div class="attendance-marker">
    <!-- Header -->
    <div class="attendance-header">
      <h2 class="attendance-title">{{ classInfo.course_name }}</h2>
      <div class="attendance-meta">
        {{ classInfo.section }} | {{ classInfo.schedule_date }} | {{ students.length }} students
      </div>
      <a class="mark-another-link" @click.prevent="showDatePicker = !showDatePicker">
        Mark for Another Date
      </a>
    </div>

    <!-- Already marked banner -->
    <div v-if="classInfo.is_marked" class="already-marked-banner">
      <span class="material-symbols-outlined">info</span>
      Attendance has already been submitted for this class.
    </div>

    <!-- Loading state -->
    <template v-if="loadingStudents">
      <div class="skeleton-row" v-for="n in 10" :key="n">
        <SkeletonLoader height="48px" />
      </div>
    </template>

    <!-- Student list -->
    <template v-else-if="students.length > 0">
      <!-- Select All -->
      <div class="select-all-row">
        <input
          type="checkbox"
          class="select-all-checkbox"
          :checked="allPresent"
          :disabled="classInfo.is_marked"
          @change="toggleAll($event.target.checked)"
        />
        <span class="select-all-label">
          Select All Present ({{ presentCount }}/{{ students.length }})
        </span>
      </div>

      <!-- Student rows -->
      <div
        v-for="(student, index) in students"
        :key="student.student"
        :class="[
          'student-row',
          {
            'student-row--absent': !attendance[index],
            'student-row--disabled': classInfo.is_marked,
          },
        ]"
      >
        <input
          type="checkbox"
          class="student-checkbox"
          :checked="attendance[index]"
          :disabled="classInfo.is_marked"
          :aria-label="`Mark ${student.student_name} as present`"
          @change="toggleStudent(index, $event.target.checked)"
        />
        <div class="student-avatar">
          <img
            v-if="student.image"
            :src="student.image"
            :alt="student.student_name"
            class="student-avatar-img"
          />
          <span v-else class="student-avatar-initials">
            {{ getInitials(student.student_name) }}
          </span>
        </div>
        <div class="student-info">
          <span class="student-name">{{ student.student_name }}</span>
          <span class="student-roll">{{ student.roll_no }}</span>
        </div>
      </div>

      <!-- Submission bar -->
      <div v-if="!classInfo.is_marked" class="submission-bar">
        <div class="attendance-summary">
          {{ presentCount }} Present, {{ absentCount }} Absent ({{ percentage }}%)
        </div>
        <button
          class="btn-primary submit-attendance-btn"
          :disabled="submitting"
          @click="handleSubmit"
        >
          {{ submitting ? 'Submitting...' : 'Submit Attendance' }}
        </button>
      </div>
    </template>

    <!-- Error state -->
    <div v-if="submitError" class="error-state">
      <p>Attendance submission failed. Please check your connection and try again.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import { useToast } from '../../composables/useToast.js'
import SkeletonLoader from '../shared/SkeletonLoader.vue'

const props = defineProps({
  classInfo: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['attendance-submitted'])

const { getStudentsForAttendance, submitAttendance } = useFacultyApi()
const { show: showToast } = useToast()

const students = ref([])
const attendance = ref([]) // boolean array: true = present
const loadingStudents = ref(true)
const submitting = ref(false)
const submitError = ref(false)
const showDatePicker = ref(false)

const presentCount = computed(() => attendance.value.filter(Boolean).length)
const absentCount = computed(() => attendance.value.length - presentCount.value)
const allPresent = computed(() => attendance.value.length > 0 && attendance.value.every(Boolean))
const percentage = computed(() => {
  if (attendance.value.length === 0) return 0
  return Math.round((presentCount.value / attendance.value.length) * 100)
})

onMounted(async () => {
  try {
    const result = await getStudentsForAttendance(props.classInfo.name)
    if (result) {
      students.value = result
      // All present by default
      attendance.value = new Array(result.length).fill(true)
    }
  } catch (e) {
    // Error handling
  } finally {
    loadingStudents.value = false
  }
})

function toggleStudent(index, checked) {
  attendance.value[index] = checked
  // Force reactivity
  attendance.value = [...attendance.value]
}

function toggleAll(checked) {
  attendance.value = new Array(students.value.length).fill(checked)
}

function getInitials(name) {
  if (!name) return '?'
  return name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .substring(0, 2)
    .toUpperCase()
}

async function handleSubmit() {
  submitting.value = true
  submitError.value = false

  const attendanceData = students.value.map((student, index) => ({
    student: student.student,
    status: attendance.value[index] ? 'Present' : 'Absent',
  }))

  try {
    const result = await submitAttendance(props.classInfo.name, attendanceData)
    if (result) {
      showToast(`${result.present} Present, ${result.absent} Absent (${result.percentage}%)`, 'success')
      emit('attendance-submitted', result)
    }
  } catch (e) {
    submitError.value = true
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.attendance-header {
  padding: var(--space-4);
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
}

.attendance-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.attendance-meta {
  font-size: var(--text-sm);
  color: var(--gray-500);
  margin-top: var(--space-1);
}

.mark-another-link {
  display: inline-block;
  margin-top: var(--space-2);
  font-size: var(--text-sm);
  color: var(--primary);
  cursor: pointer;
  text-decoration: none;
}

.mark-another-link:hover {
  text-decoration: underline;
}

.already-marked-banner {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: var(--info-light);
  border-left: 3px solid var(--info);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.already-marked-banner .material-symbols-outlined {
  color: var(--info);
  font-size: 20px;
}

.select-all-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.select-all-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.student-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-top: none;
  transition: background var(--transition-fast) var(--ease-in-out);
}

.student-row:last-child {
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}

.student-row--absent {
  background: var(--error-tint);
}

.student-row--disabled {
  background: var(--gray-100);
  opacity: 0.7;
}

.student-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.student-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.student-avatar-initials {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: var(--primary-light);
  color: var(--primary);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.student-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex: 1;
}

.student-name {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.student-roll {
  font-size: var(--text-sm);
  color: var(--gray-500);
}

.submission-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-top: none;
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  margin-top: var(--space-4);
  position: sticky;
  bottom: 0;
}

.attendance-summary {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.skeleton-row {
  margin-bottom: var(--space-2);
}

.error-state {
  padding: var(--space-4);
  color: var(--error);
  font-size: var(--text-sm);
}

@media (max-width: 767px) {
  .submission-bar {
    position: sticky;
    bottom: 0;
    border-radius: 0;
    border-left: none;
    border-right: none;
    border-bottom: none;
    box-shadow: var(--shadow-lg);
  }

  .student-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0;
  }
}
</style>
