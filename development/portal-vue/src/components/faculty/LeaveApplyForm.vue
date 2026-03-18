<template>
  <div v-if="show" class="leave-form-overlay" @click.self="$emit('close')">
    <div class="leave-form-panel">
      <div class="leave-form-header">
        <h3 class="leave-form-title">Apply for Leave</h3>
        <button class="btn-icon btn-ghost" aria-label="Close" @click="$emit('close')">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <form class="leave-form-body" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label" for="leave-type">Leave Type</label>
          <select
            id="leave-type"
            v-model="form.leave_type"
            class="form-select"
            required
          >
            <option value="" disabled>Select leave type</option>
            <option
              v-for="lt in leaveTypes"
              :key="lt"
              :value="lt"
            >
              {{ lt }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label" for="from-date">From Date</label>
          <input
            id="from-date"
            v-model="form.from_date"
            type="date"
            class="form-input"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="to-date">To Date</label>
          <input
            id="to-date"
            v-model="form.to_date"
            type="date"
            class="form-input"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="reason">Reason</label>
          <textarea
            id="reason"
            v-model="form.reason"
            class="form-input leave-form-textarea"
            rows="3"
            required
          />
        </div>

        <div v-if="errorMsg" class="leave-form-error">{{ errorMsg }}</div>

        <div class="leave-form-actions">
          <button type="submit" class="btn-primary" :disabled="submitting">
            Submit Leave Request
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
import { ref, reactive } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'

const props = defineProps({
  show: { type: Boolean, default: false },
  leaveTypes: { type: Array, default: () => [] },
})

const emit = defineEmits(['close', 'submitted'])

const { applyLeave } = useFacultyApi()
const submitting = ref(false)
const errorMsg = ref('')

const form = reactive({
  leave_type: '',
  from_date: '',
  to_date: '',
  reason: '',
})

async function handleSubmit() {
  submitting.value = true
  errorMsg.value = ''

  try {
    await applyLeave({
      leave_type: form.leave_type,
      from_date: form.from_date,
      to_date: form.to_date,
      reason: form.reason,
    })
    emit('submitted')
    emit('close')
    // Reset form
    form.leave_type = ''
    form.from_date = ''
    form.to_date = ''
    form.reason = ''
  } catch (e) {
    errorMsg.value = 'Leave request could not be submitted. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.leave-form-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 100;
  display: flex;
  justify-content: flex-end;
}

.leave-form-panel {
  width: 320px;
  max-width: 100%;
  height: 100%;
  background: var(--bg-card);
  border-left: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  transform: translateX(0);
  transition: transform var(--transition-slow) var(--ease-in-out);
}

.leave-form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-default);
}

.leave-form-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.leave-form-body {
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

.leave-form-textarea {
  resize: vertical;
}

.leave-form-error {
  font-size: var(--text-sm);
  color: var(--error);
  padding: var(--space-2);
  background: var(--error-light);
  border-radius: var(--radius-lg);
}

.leave-form-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: auto;
  padding-top: var(--space-4);
}
</style>
