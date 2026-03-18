<template>
  <div class="grade-grid-wrapper">
    <!-- Loading state -->
    <template v-if="loading">
      <div class="grade-grid-skeleton">
        <SkeletonLoader height="32px" />
        <SkeletonLoader v-for="n in 8" :key="n" height="40px" />
      </div>
    </template>

    <!-- Empty state -->
    <template v-else-if="!students.length">
      <div class="grade-grid-empty">
        <span class="material-symbols-outlined grade-grid-empty__icon">edit_note</span>
        <p class="grade-grid-empty__heading">No courses to grade</p>
        <p class="grade-grid-empty__body">You have no active courses requiring grade entry this semester.</p>
      </div>
    </template>

    <!-- Grade grid -->
    <template v-else>
      <!-- Submitted banner -->
      <div v-if="isSubmitted" class="grade-grid-banner grade-grid-banner--locked">
        <span class="material-symbols-outlined">lock</span>
        Grades have been submitted and are now locked for editing.
      </div>

      <div
        class="grade-grid"
        role="grid"
        aria-label="Grade entry grid"
      >
        <!-- Header row -->
        <div class="grade-grid__row grade-grid__header" role="row">
          <div class="grade-grid__cell grade-grid__cell--frozen grade-grid__cell--header" role="columnheader">
            Student
          </div>
          <div
            v-for="assessment in assessments"
            :key="assessment.name"
            class="grade-grid__cell grade-grid__cell--header"
            role="columnheader"
          >
            {{ assessment.name }}
          </div>
          <div class="grade-grid__cell grade-grid__cell--header grade-grid__cell--grade" role="columnheader">
            Grade
          </div>
          <div class="grade-grid__cell grade-grid__cell--header grade-grid__cell--status" role="columnheader">
            Status
          </div>
        </div>

        <!-- Data rows -->
        <div
          v-for="(student, rowIndex) in students"
          :key="student.student"
          class="grade-grid__row"
          :class="{ 'grade-grid__row--at-risk': isAtRisk(student) }"
          role="row"
        >
          <!-- Frozen student name column -->
          <div class="grade-grid__cell grade-grid__cell--frozen grade-grid__cell--name" role="gridcell">
            {{ student.student_name }}
          </div>

          <!-- Editable mark cells -->
          <div
            v-for="(assessment, colIndex) in assessments"
            :key="`${student.student}-${assessment.name}`"
            class="grade-grid__cell grade-grid__cell--editable"
            role="gridcell"
            :aria-label="`${assessment.name} for ${student.student_name}`"
          >
            <input
              v-if="!isSubmitted"
              :ref="el => setCellRef(rowIndex, colIndex, el)"
              type="text"
              class="grade-grid__input"
              :value="getCellValue(student, assessment.name)"
              @input="handleCellInput($event, student, assessment.name)"
              @keydown.tab.prevent="moveFocus(rowIndex, colIndex, 'tab')"
              @keydown.enter.prevent="moveFocus(rowIndex, colIndex, 'enter')"
            />
            <span v-else class="grade-grid__value-readonly">
              {{ getCellValue(student, assessment.name) }}
            </span>

            <!-- Save status indicator -->
            <span
              v-if="getCellState(student.student, assessment.name) === 'saved'"
              class="grade-grid__save-indicator"
              role="status"
              aria-live="polite"
            >
              <span class="material-symbols-outlined grade-grid__check-icon">check</span>
              <span class="sr-only">Saved</span>
            </span>
            <span
              v-if="getCellState(student.student, assessment.name) === 'error'"
              class="grade-grid__save-indicator grade-grid__save-indicator--error"
              role="status"
              aria-live="polite"
            >
              <span class="material-symbols-outlined grade-grid__error-icon">error</span>
            </span>
          </div>

          <!-- Computed grade (read-only) -->
          <div class="grade-grid__cell grade-grid__cell--grade" role="gridcell">
            {{ getComputedGrade(student) }}
          </div>

          <!-- Status badge -->
          <div class="grade-grid__cell grade-grid__cell--status" role="gridcell">
            <span
              v-if="isSubmitted"
              class="grade-grid__badge grade-grid__badge--submitted"
            >Submitted</span>
            <span v-else class="grade-grid__badge grade-grid__badge--draft">Draft</span>
          </div>
        </div>
      </div>

      <!-- Submit bar -->
      <div class="grade-grid__submit-bar">
        <span v-if="lastSaveTime" class="grade-grid__autosave-text">
          Auto-saved {{ lastSaveTime }}
        </span>
        <button
          class="btn-primary"
          :disabled="isSubmitted"
          @click="handleSubmitGrades"
        >
          Submit Grades
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, shallowRef, shallowReactive, onMounted, onUnmounted } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import { useToast } from '../../composables/useToast.js'
import SkeletonLoader from '../shared/SkeletonLoader.vue'

const DEBOUNCE_MS = 500
const SAVED_DISPLAY_MS = 1500

const props = defineProps({
  course: { type: String, required: true },
  assessmentPlan: { type: String, required: true },
})

const { getStudentsForGrading, saveDraftGrade, submitGrades, getGradeAnalytics } = useFacultyApi()
const { show: showToast } = useToast()

const emit = defineEmits(['analytics-updated'])

// State
const loading = ref(true)
const students = shallowRef([])
const assessments = shallowRef([])
const isSubmitted = ref(false)
const lastSaveTime = ref(null)

// Cell state tracking: key = `${student}-${assessment}`, value = 'idle'|'saving'|'saved'|'error'
const cellStates = shallowReactive(new Map())

// Cell ref registry for keyboard navigation
const cellRefs = {}

// Debounce timers per cell
const debounceTimers = {}
// Saved timeout timers per cell
const savedTimers = {}

function setCellRef(rowIndex, colIndex, el) {
  if (!cellRefs[rowIndex]) cellRefs[rowIndex] = {}
  cellRefs[rowIndex][colIndex] = el
}

function moveFocus(rowIndex, colIndex, direction) {
  let nextRow = rowIndex
  let nextCol = colIndex

  if (direction === 'tab') {
    nextCol = colIndex + 1
    if (nextCol >= assessments.value.length) {
      nextCol = 0
      nextRow = rowIndex + 1
    }
  } else if (direction === 'enter') {
    nextRow = rowIndex + 1
  }

  if (cellRefs[nextRow] && cellRefs[nextRow][nextCol]) {
    cellRefs[nextRow][nextCol].focus()
  }
}

function getCellValue(student, assessmentName) {
  const grade = student.grades.find(g => g.assessment_name === assessmentName)
  return grade?.marks != null ? String(grade.marks) : ''
}

function getCellState(studentId, assessmentName) {
  return cellStates.get(`${studentId}-${assessmentName}`) || 'idle'
}

function getComputedGrade(student) {
  // Use the latest grade from the grades array
  const validGrades = student.grades.filter(g => g.grade)
  if (!validGrades.length) return '-'
  // Return the first non-null grade as representative
  return validGrades[0]?.grade || '-'
}

function isAtRisk(student) {
  const totalMarks = student.grades.reduce((sum, g) => sum + (g.marks || 0), 0)
  const maxTotal = assessments.value.length * (assessments.value[0]?.max_marks || 100)
  const percentage = maxTotal > 0 ? (totalMarks / maxTotal) * 100 : 0
  return percentage < 40
}

function handleCellInput(event, student, assessmentName) {
  const value = event.target.value
  const cellKey = `${student.student}-${assessmentName}`

  // Update local data
  const updatedStudents = [...students.value]
  const studentData = updatedStudents.find(s => s.student === student.student)
  if (studentData) {
    const grade = studentData.grades.find(g => g.assessment_name === assessmentName)
    if (grade) {
      grade.marks = value ? parseFloat(value) : null
    }
    students.value = updatedStudents
  }

  // Set saving state
  cellStates.set(cellKey, 'saving')

  // Clear existing timer
  if (debounceTimers[cellKey]) {
    clearTimeout(debounceTimers[cellKey])
  }

  // Debounced save
  debounceTimers[cellKey] = setTimeout(async () => {
    try {
      const result = await saveDraftGrade({
        student: student.student,
        course: props.course,
        assessment_plan: props.assessmentPlan,
        assessment_name: assessmentName,
        marks: value,
      })

      cellStates.set(cellKey, 'saved')
      lastSaveTime.value = new Date().toLocaleTimeString()

      // Update grade from server response
      if (result?.grade && studentData) {
        const gradeEntry = studentData.grades.find(g => g.assessment_name === assessmentName)
        if (gradeEntry) {
          gradeEntry.grade = result.grade
        }
      }

      // Emit analytics update
      emit('analytics-updated')

      // Reset saved indicator after delay
      if (savedTimers[cellKey]) clearTimeout(savedTimers[cellKey])
      savedTimers[cellKey] = setTimeout(() => {
        cellStates.set(cellKey, 'idle')
      }, SAVED_DISPLAY_MS)
    } catch (e) {
      cellStates.set(cellKey, 'error')
    }
  }, DEBOUNCE_MS)
}

async function handleSubmitGrades() {
  try {
    await submitGrades(props.course, props.assessmentPlan)
    isSubmitted.value = true
    showToast('Grades submitted successfully', 'success')
  } catch (e) {
    showToast('Grade submission failed. Please try again.', 'error')
  }
}

onMounted(async () => {
  try {
    const result = await getStudentsForGrading(props.course, props.assessmentPlan)
    if (result) {
      students.value = result.students || []
      assessments.value = result.assessments || []
    }
  } catch (e) {
    // Error handled by empty state
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  // Clean up timers
  Object.values(debounceTimers).forEach(clearTimeout)
  Object.values(savedTimers).forEach(clearTimeout)
})
</script>

<style scoped>
.grade-grid-wrapper {
  width: 100%;
}

.grade-grid-skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-4);
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-default);
}

.grade-grid-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  text-align: center;
}

.grade-grid-empty__icon {
  font-size: 48px;
  color: var(--gray-300);
  margin-bottom: var(--space-2);
}

.grade-grid-empty__heading {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1) 0;
}

.grade-grid-empty__body {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.grade-grid-banner {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-3);
}

.grade-grid-banner--locked {
  background: var(--info-light, #DBEAFE);
  color: var(--info, #3B82F6);
  border-left: 3px solid var(--info, #3B82F6);
}

.grade-grid-banner--locked .material-symbols-outlined {
  font-size: 18px;
}

.grade-grid {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-default);
  overflow-x: auto;
}

.grade-grid__row {
  display: flex;
  border-bottom: 1px solid var(--border-subtle, var(--gray-100));
}

.grade-grid__row:last-child {
  border-bottom: none;
}

.grade-grid__row--at-risk {
  background: var(--error-tint, var(--error-light, #FEE2E2));
  border-left: 3px solid var(--error);
}

.grade-grid__header {
  background: var(--gray-50);
}

.grade-grid__cell {
  min-width: 80px;
  padding: var(--space-2);
  font-size: var(--text-sm);
  display: flex;
  align-items: center;
  position: relative;
}

.grade-grid__cell--header {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--gray-500);
  text-transform: uppercase;
  min-height: 36px;
}

.grade-grid__cell--frozen {
  position: sticky;
  left: 0;
  z-index: 1;
  background: var(--bg-card);
  min-width: 180px;
}

.grade-grid__row--at-risk .grade-grid__cell--frozen {
  background: var(--error-tint, var(--error-light, #FEE2E2));
}

.grade-grid__header .grade-grid__cell--frozen {
  background: var(--gray-50);
}

.grade-grid__cell--name {
  font-weight: var(--font-semibold);
}

.grade-grid__cell--editable {
  position: relative;
}

.grade-grid__cell--grade {
  background: var(--gray-50);
  font-weight: var(--font-semibold);
  min-width: 70px;
}

.grade-grid__cell--status {
  min-width: 90px;
}

.grade-grid__input {
  width: 100%;
  min-width: 60px;
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-sm);
  font-weight: var(--font-normal);
  border: 1px solid var(--border-subtle, var(--gray-200));
  border-radius: var(--radius-md, 4px);
  background: transparent;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.grade-grid__input:focus {
  border: 2px solid var(--primary);
  box-shadow: 0 0 0 3px var(--primary-tint, var(--primary-light, rgba(79, 70, 229, 0.15)));
}

.grade-grid__value-readonly {
  color: var(--text-secondary);
  background: var(--gray-100);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md, 4px);
  width: 100%;
  text-align: center;
}

.grade-grid__save-indicator {
  position: absolute;
  right: var(--space-1);
  top: 50%;
  transform: translateY(-50%);
  animation: fadeIn 200ms ease-in;
}

.grade-grid__check-icon {
  font-size: 12px;
  color: var(--success);
}

.grade-grid__error-icon {
  font-size: 12px;
  color: var(--error);
}

.grade-grid__badge {
  padding: 2px 8px;
  border-radius: var(--radius-full, 9999px);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.grade-grid__badge--draft {
  background: var(--warning-light, #FEF3C7);
  color: var(--warning-dark, #92400E);
}

.grade-grid__badge--submitted {
  background: var(--success-light, #D1FAE5);
  color: var(--success-dark, #065F46);
}

.grade-grid__submit-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-4);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-card);
  border-top: 1px solid var(--border-default);
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
}

.grade-grid__autosave-text {
  font-size: var(--text-xs);
  color: var(--gray-400);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
