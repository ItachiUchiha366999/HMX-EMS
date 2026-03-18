<template>
  <div class="lms-course-list">
    <template v-if="loading">
      <SkeletonLoader v-for="n in 2" :key="n" height="100px" />
    </template>
    <template v-else-if="!available">
      <div class="empty-state">
        <span class="material-symbols-outlined empty-state-icon">school</span>
        <p class="empty-state-heading">No LMS courses</p>
        <p class="empty-state-body">LMS courses assigned to you will appear here.</p>
      </div>
    </template>
    <template v-else-if="courses.length === 0">
      <div class="empty-state">
        <span class="material-symbols-outlined empty-state-icon">school</span>
        <p class="empty-state-heading">No LMS courses</p>
        <p class="empty-state-body">LMS courses assigned to you will appear here.</p>
      </div>
    </template>
    <template v-else>
      <div class="lms-courses">
        <div
          v-for="course in courses"
          :key="course.name"
          class="lms-course-card"
        >
          <div class="lms-course-card__name">{{ course.title }}</div>
          <div class="lms-course-card__stats">
            {{ course.lesson_count }} lessons | {{ course.assignment_count }} assignments | {{ course.quiz_count }} quizzes
          </div>
          <button class="btn-primary btn-sm" @click="$emit('manage-course', course.name)">
            Manage Content
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import SkeletonLoader from '../shared/SkeletonLoader.vue'

defineEmits(['manage-course'])

const { getLmsCourses } = useFacultyApi()
const courses = ref([])
const available = ref(true)
const loading = ref(true)

onMounted(async () => {
  try {
    const result = await getLmsCourses()
    available.value = result.available !== false
    courses.value = result.courses || []
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

.lms-courses {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.lms-course-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
}

.lms-course-card__name {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.lms-course-card__stats {
  font-size: var(--text-sm);
  color: var(--gray-500);
  margin-bottom: var(--space-3);
}
</style>
