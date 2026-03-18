<template>
  <div class="lms-content-manager">
    <template v-if="loading">
      <SkeletonLoader height="300px" />
    </template>
    <template v-else>
      <!-- Lessons -->
      <div class="content-section">
        <div class="content-section__header">
          <h4 class="content-section__title">Lessons</h4>
          <button class="btn-ghost btn-sm" @click="openForm('Lesson')">
            <span class="material-symbols-outlined btn-icon-prefix">add</span>
            Add Lesson
          </button>
        </div>
        <div v-for="item in content.lessons" :key="item.name" class="content-item">
          <span class="content-item__title">{{ item.title }}</span>
          <span class="content-badge content-badge--lesson">Lesson</span>
          <button class="btn-ghost btn-sm" @click="openForm('Lesson', item)">Edit</button>
          <button class="btn-ghost btn-sm btn-delete" @click="confirmDelete('LMS Lesson', item)">Delete</button>
        </div>
      </div>

      <!-- Assignments -->
      <div class="content-section">
        <div class="content-section__header">
          <h4 class="content-section__title">Assignments</h4>
          <button class="btn-ghost btn-sm" @click="openForm('Assignment')">
            <span class="material-symbols-outlined btn-icon-prefix">add</span>
            Add Assignment
          </button>
        </div>
        <div v-for="item in content.assignments" :key="item.name" class="content-item">
          <span class="content-item__title">{{ item.title }}</span>
          <span class="content-badge content-badge--assignment">Assignment</span>
          <button class="btn-ghost btn-sm" @click="openForm('Assignment', item)">Edit</button>
          <button class="btn-ghost btn-sm btn-delete" @click="confirmDelete('LMS Assignment', item)">Delete</button>
        </div>
      </div>

      <!-- Quizzes -->
      <div class="content-section">
        <div class="content-section__header">
          <h4 class="content-section__title">Quizzes</h4>
          <button class="btn-ghost btn-sm" @click="openForm('Quiz')">
            <span class="material-symbols-outlined btn-icon-prefix">add</span>
            Add Quiz
          </button>
        </div>
        <div v-for="item in content.quizzes" :key="item.name" class="content-item">
          <span class="content-item__title">{{ item.title }}</span>
          <span class="content-badge content-badge--quiz">Quiz</span>
          <button class="btn-ghost btn-sm" @click="openForm('Quiz', item)">Edit</button>
          <button class="btn-ghost btn-sm btn-delete" @click="confirmDelete('LMS Quiz', item)">Delete</button>
        </div>
      </div>

      <!-- Delete confirmation modal -->
      <div v-if="deleteTarget" class="delete-modal-overlay" @click.self="cancelDelete">
        <div class="delete-modal">
          <p class="delete-modal__title">Delete {{ deleteTarget.title }}?</p>
          <p class="delete-modal__body">This action cannot be undone.</p>
          <div class="delete-modal__actions">
            <button class="btn-ghost" @click="cancelDelete">Keep Content</button>
            <button class="btn-sm btn-delete-confirm" @click="handleDelete">Delete</button>
          </div>
        </div>
      </div>

      <!-- Content form slide-over -->
      <LmsContentForm
        :show="showForm"
        :content-type="formContentType"
        :edit-data="formEditData"
        :course="course"
        @close="closeForm"
        @saved="handleSaved"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import SkeletonLoader from '../shared/SkeletonLoader.vue'
import LmsContentForm from './LmsContentForm.vue'

const props = defineProps({
  course: { type: String, required: true },
})

const { getLmsCourseContent, deleteLmsContent } = useFacultyApi()
const loading = ref(true)
const content = reactive({ lessons: [], assignments: [], quizzes: [] })

// Form state
const showForm = ref(false)
const formContentType = ref('Lesson')
const formEditData = ref(null)

// Delete state
const deleteTarget = ref(null)
const deleteDoctype = ref('')

function openForm(type, editData = null) {
  formContentType.value = type
  formEditData.value = editData
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  formEditData.value = null
}

function confirmDelete(doctype, item) {
  deleteDoctype.value = doctype
  deleteTarget.value = item
}

function cancelDelete() {
  deleteTarget.value = null
}

async function handleDelete() {
  if (deleteTarget.value) {
    await deleteLmsContent(deleteDoctype.value, deleteTarget.value.name)
    await loadContent()
    deleteTarget.value = null
  }
}

async function handleSaved() {
  await loadContent()
}

async function loadContent() {
  try {
    const result = await getLmsCourseContent(props.course)
    content.lessons = result.lessons || []
    content.assignments = result.assignments || []
    content.quizzes = result.quizzes || []
  } catch (e) {
    // silently handle
  }
}

onMounted(async () => {
  await loadContent()
  loading.value = false
})
</script>

<style scoped>
.content-section {
  margin-bottom: var(--space-6);
}

.content-section__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.content-section__title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.btn-icon-prefix {
  font-size: 16px;
  margin-right: var(--space-1);
}

.content-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  border: 1px solid var(--border-subtle, var(--gray-100));
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-2);
}

.content-item__title {
  flex: 1;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.content-badge {
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  padding: 2px var(--space-2);
  font-weight: var(--font-semibold);
}

.content-badge--lesson {
  background: var(--primary-light);
  color: var(--primary);
}

.content-badge--assignment {
  background: var(--warning-light, #FEF3C7);
  color: var(--warning-dark, #92400E);
}

.content-badge--quiz {
  background: var(--info-light, #DBEAFE);
  color: var(--info, #3B82F6);
}

.btn-delete {
  color: var(--error);
}

.delete-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-modal {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  max-width: 400px;
  width: 100%;
  box-shadow: var(--shadow-lg);
}

.delete-modal__title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
}

.delete-modal__body {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0 0 var(--space-4) 0;
}

.delete-modal__actions {
  display: flex;
  gap: var(--space-2);
  justify-content: flex-end;
}

.btn-delete-confirm {
  background: var(--error);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  padding: var(--space-1) var(--space-3);
  cursor: pointer;
}
</style>
