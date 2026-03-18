<template>
  <div v-if="show" class="lms-content-form-overlay" @click.self="$emit('close')">
    <div class="lms-content-form-panel">
      <div class="lms-form-header">
        <h3 class="lms-form-title">{{ editData ? 'Edit' : 'Add' }} {{ contentType }}</h3>
        <button class="btn-icon btn-ghost" aria-label="Close" @click="$emit('close')">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <form class="lms-form-body" @submit.prevent="handleSubmit">
        <!-- Title (all types) -->
        <div class="form-group">
          <label class="form-label" for="content-title">Title</label>
          <input
            id="content-title"
            v-model="form.title"
            type="text"
            class="form-input"
            required
          />
        </div>

        <!-- Lesson-specific fields -->
        <template v-if="contentType === 'Lesson'">
          <div class="form-group">
            <label class="form-label" for="content-body">Content</label>
            <textarea
              id="content-body"
              v-model="form.content"
              class="form-input"
              rows="6"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label" for="content-order">Order</label>
            <input
              id="content-order"
              v-model.number="form.idx"
              type="number"
              class="form-input"
              min="1"
            />
          </div>
        </template>

        <!-- Assignment-specific fields -->
        <template v-if="contentType === 'Assignment'">
          <div class="form-group">
            <label class="form-label" for="due-date">Due Date</label>
            <input
              id="due-date"
              v-model="form.due_date"
              type="date"
              class="form-input"
              required
            />
          </div>
          <div class="form-group">
            <label class="form-label" for="instructions">Instructions</label>
            <textarea
              id="instructions"
              v-model="form.instructions"
              class="form-input"
              rows="4"
            />
          </div>
          <div class="form-group">
            <label class="form-label" for="max-score">Max Score</label>
            <input
              id="max-score"
              v-model.number="form.max_score"
              type="number"
              class="form-input"
              min="0"
            />
          </div>
        </template>

        <!-- Quiz-specific fields -->
        <template v-if="contentType === 'Quiz'">
          <div class="form-group">
            <label class="form-label" for="duration">Duration (minutes)</label>
            <input
              id="duration"
              v-model.number="form.duration"
              type="number"
              class="form-input"
              min="1"
            />
          </div>
          <div class="form-group">
            <label class="form-label" for="quiz-instructions">Instructions</label>
            <textarea
              id="quiz-instructions"
              v-model="form.instructions"
              class="form-input"
              rows="4"
            />
          </div>
        </template>

        <div v-if="errorMsg" class="lms-form-error">{{ errorMsg }}</div>

        <div class="lms-form-actions">
          <button type="submit" class="btn-primary" :disabled="submitting">
            Save Content
          </button>
          <button type="button" class="btn-ghost" @click="$emit('close')">
            Discard
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'

const props = defineProps({
  show: { type: Boolean, default: false },
  contentType: { type: String, default: 'Lesson' },
  editData: { type: Object, default: null },
  course: { type: String, default: '' },
})

const emit = defineEmits(['close', 'saved'])

const { saveLmsContent } = useFacultyApi()
const submitting = ref(false)
const errorMsg = ref('')

const form = reactive({
  title: '',
  content: '',
  idx: 1,
  due_date: '',
  instructions: '',
  max_score: 100,
  duration: 30,
})

watch(() => props.editData, (val) => {
  if (val) {
    Object.assign(form, val)
  } else {
    form.title = ''
    form.content = ''
    form.idx = 1
    form.due_date = ''
    form.instructions = ''
    form.max_score = 100
    form.duration = 30
  }
}, { immediate: true })

async function handleSubmit() {
  submitting.value = true
  errorMsg.value = ''

  try {
    await saveLmsContent({
      doctype: `LMS ${props.contentType}`,
      name: props.editData?.name || undefined,
      course: props.course,
      ...form,
    })
    emit('saved')
    emit('close')
  } catch (e) {
    errorMsg.value = 'Content could not be saved. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.lms-content-form-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 100;
  display: flex;
  justify-content: flex-end;
}

.lms-content-form-panel {
  width: 480px;
  max-width: 100%;
  height: 100%;
  background: var(--bg-card);
  border-left: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  transition: transform var(--transition-slow) var(--ease-in-out);
}

.lms-form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-default);
}

.lms-form-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.lms-form-body {
  padding: var(--space-4);
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.lms-form-error {
  font-size: var(--text-sm);
  color: var(--error);
  padding: var(--space-2);
  background: var(--error-light);
  border-radius: var(--radius-lg);
}

.lms-form-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: auto;
  padding-top: var(--space-4);
}
</style>
