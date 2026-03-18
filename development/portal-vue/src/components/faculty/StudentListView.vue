<template>
  <div class="student-list-view">
    <!-- Header -->
    <div class="student-list-view__header">
      <div class="student-list-view__header-left">
        <input
          type="text"
          class="form-input student-list-view__search"
          placeholder="Search students..."
          v-model="searchQuery"
          @input="debouncedSearch"
        />
        <span class="student-list-view__count">
          Showing {{ showingStart }}-{{ showingEnd }} of {{ totalCount }}
        </span>
      </div>
      <div class="student-list-view__header-right">
        <button class="btn-ghost btn-sm" @click="$emit('view-analytics')">
          <span class="material-symbols-outlined">analytics</span>
          View Analytics
        </button>
      </div>
    </div>

    <!-- Loading -->
    <template v-if="loading">
      <div class="student-list-view__skeleton">
        <SkeletonLoader v-for="n in 5" :key="n" height="48px" />
      </div>
    </template>

    <!-- Student table -->
    <template v-else>
      <div class="student-list-view__table">
        <table class="table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Roll No</th>
              <th>Enrollment</th>
              <th>Attendance</th>
              <th>Grade</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="student in students" :key="student.student">
              <tr>
                <!-- Avatar + Name -->
                <td>
                  <div class="student-list-view__name-cell">
                    <div class="student-list-view__avatar" :title="student.student_name">
                      <img v-if="student.image" :src="student.image" :alt="student.student_name" />
                      <span v-else class="student-list-view__initials">{{ getInitials(student.student_name) }}</span>
                    </div>
                    <span class="student-list-view__name">{{ student.student_name }}</span>
                  </div>
                </td>
                <!-- Roll -->
                <td class="student-list-view__secondary">{{ student.roll_no }}</td>
                <!-- Enrollment -->
                <td class="student-list-view__secondary">{{ student.enrollment_no }}</td>
                <!-- Attendance % -->
                <td>
                  <span
                    :class="[
                      'student-list-view__attendance',
                      attendanceClass(student.attendance_percentage),
                    ]"
                  >
                    {{ student.attendance_percentage }}%
                  </span>
                </td>
                <!-- Grade -->
                <td class="student-list-view__grade">{{ student.current_grade }}</td>
                <!-- Expand -->
                <td>
                  <button
                    class="btn-icon btn-ghost btn-sm student-expand-btn"
                    :aria-label="`Expand details for ${student.student_name}`"
                    @click="toggleExpand(student.student)"
                  >
                    <span class="material-symbols-outlined">
                      {{ expandedStudent === student.student ? 'expand_less' : 'expand_more' }}
                    </span>
                  </button>
                </td>
              </tr>
              <!-- Expanded detail row -->
              <tr v-if="expandedStudent === student.student">
                <td colspan="6" class="student-list-view__expanded-cell">
                  <StudentDetailPanel
                    :student="student.student"
                    :course="course"
                  />
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalCount > pageSize" class="student-list-view__pagination">
        <span class="student-list-view__pagination-info">
          Showing {{ showingStart }}-{{ showingEnd }} of {{ totalCount }}
        </span>
        <div class="student-list-view__pagination-buttons">
          <button
            class="btn-secondary btn-sm"
            :disabled="currentPage === 0"
            @click="changePage(currentPage - 1)"
          >
            <span class="material-symbols-outlined">navigate_before</span>
          </button>
          <button
            class="btn-secondary btn-sm"
            :disabled="(currentPage + 1) * pageSize >= totalCount"
            @click="changePage(currentPage + 1)"
          >
            <span class="material-symbols-outlined">navigate_next</span>
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import StudentDetailPanel from './StudentDetailPanel.vue'
import SkeletonLoader from '../shared/SkeletonLoader.vue'

const props = defineProps({
  course: { type: String, required: true },
})

const emit = defineEmits(['view-analytics'])

const { getStudentList } = useFacultyApi()

const loading = ref(true)
const students = ref([])
const totalCount = ref(0)
const currentPage = ref(0)
const pageSize = 20
const searchQuery = ref('')
const expandedStudent = ref(null)
let searchTimeout = null

const showingStart = computed(() => {
  if (totalCount.value === 0) return 0
  return currentPage.value * pageSize + 1
})

const showingEnd = computed(() => {
  const end = (currentPage.value + 1) * pageSize
  return Math.min(end, totalCount.value)
})

function getInitials(name) {
  if (!name) return '?'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

function attendanceClass(percentage) {
  if (percentage >= 75) return 'attendance--success'
  if (percentage >= 60) return 'attendance--warning'
  return 'attendance--error'
}

function toggleExpand(studentId) {
  expandedStudent.value = expandedStudent.value === studentId ? null : studentId
}

function debouncedSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 0
    fetchStudents()
  }, 300)
}

function changePage(page) {
  currentPage.value = page
  fetchStudents()
}

async function fetchStudents() {
  loading.value = true
  try {
    const result = await getStudentList({
      course: props.course,
      search: searchQuery.value || undefined,
      start: currentPage.value * pageSize,
      page_length: pageSize,
    })
    if (result) {
      students.value = result.data || []
      totalCount.value = result.total_count || 0
    }
  } catch (e) {
    // Error state
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStudents()
})
</script>

<style scoped>
.student-list-view__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
}

.student-list-view__header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex: 1;
}

.student-list-view__search {
  min-width: 200px;
  max-width: 300px;
}

.student-list-view__count {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  white-space: nowrap;
}

.student-list-view__skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.student-list-view__table {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-default);
  overflow: hidden;
}

.student-list-view__table .table {
  width: 100%;
  border-collapse: collapse;
}

.student-list-view__table th {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--gray-500);
  text-transform: uppercase;
  text-align: left;
  padding: var(--space-3);
  background: var(--gray-50);
  border-bottom: 1px solid var(--border-default);
}

.student-list-view__table td {
  padding: var(--space-3);
  font-size: var(--text-sm);
  border-bottom: 1px solid var(--border-subtle, var(--gray-100));
  vertical-align: middle;
}

.student-list-view__name-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.student-list-view__avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-light, #EEF2FF);
}

.student-list-view__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.student-list-view__initials {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--primary);
}

.student-list-view__name {
  font-weight: var(--font-semibold);
}

.student-list-view__secondary {
  color: var(--gray-500);
}

.student-list-view__attendance {
  font-weight: var(--font-semibold);
}

.attendance--success {
  color: var(--success);
}

.attendance--warning {
  color: var(--warning);
}

.attendance--error {
  color: var(--error);
}

.student-list-view__grade {
  font-weight: var(--font-semibold);
}

.student-list-view__expanded-cell {
  padding: 0 !important;
}

.student-list-view__pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
}

.student-list-view__pagination-info {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.student-list-view__pagination-buttons {
  display: flex;
  gap: var(--space-1);
}
</style>
