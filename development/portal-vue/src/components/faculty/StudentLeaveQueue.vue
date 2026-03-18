<template>
  <div class="student-leave-queue">
    <template v-if="loading">
      <SkeletonLoader height="300px" />
    </template>
    <template v-else-if="requests.length === 0">
      <div class="empty-state">
        <span class="material-symbols-outlined empty-state-icon">pending_actions</span>
        <p class="empty-state-heading">No pending requests</p>
        <p class="empty-state-body">There are no student leave requests awaiting your approval.</p>
      </div>
    </template>
    <template v-else>
      <!-- Bulk approve bar -->
      <div v-if="selectedNames.length > 0" class="bulk-bar">
        <button class="btn-primary btn-sm btn-approve-selected" @click="handleBulkApprove">
          Approve Selected ({{ selectedNames.length }})
        </button>
      </div>

      <!-- Request list -->
      <div class="leave-table">
        <div class="leave-table__header">
          <div class="leave-table__cell leave-table__cell--check">
            <input
              type="checkbox"
              :checked="allSelected"
              @change="toggleSelectAll"
              aria-label="Select all"
            />
          </div>
          <div class="leave-table__cell leave-table__cell--name">Student Name</div>
          <div class="leave-table__cell leave-table__cell--roll">Roll No</div>
          <div class="leave-table__cell leave-table__cell--date">From</div>
          <div class="leave-table__cell leave-table__cell--date">To</div>
          <div class="leave-table__cell leave-table__cell--reason">Reason</div>
          <div class="leave-table__cell leave-table__cell--actions">Actions</div>
        </div>

        <div
          v-for="req in requests"
          :key="req.name"
          class="leave-table__row-group"
        >
          <div class="leave-table__row">
            <div class="leave-table__cell leave-table__cell--check">
              <input
                type="checkbox"
                class="student-leave-checkbox"
                :checked="selectedNames.includes(req.name)"
                @change="toggleSelect(req.name)"
                :aria-label="`Select ${req.student_name}`"
              />
            </div>
            <div class="leave-table__cell leave-table__cell--name">{{ req.student_name }}</div>
            <div class="leave-table__cell leave-table__cell--roll">{{ req.roll_no }}</div>
            <div class="leave-table__cell leave-table__cell--date">{{ req.from_date }}</div>
            <div class="leave-table__cell leave-table__cell--date">{{ req.to_date }}</div>
            <div class="leave-table__cell leave-table__cell--reason">{{ req.reason }}</div>
            <div class="leave-table__cell leave-table__cell--actions">
              <button
                class="btn-sm btn-approve"
                @click="handleApprove(req.name)"
                :aria-label="`Approve leave for ${req.student_name}`"
              >
                Approve
              </button>
              <button
                class="btn-sm btn-ghost btn-reject"
                @click="showRejectInput(req.name)"
                :aria-label="`Reject leave for ${req.student_name}`"
              >
                Reject
              </button>
            </div>
          </div>

          <!-- Inline reject reason -->
          <div v-if="rejectingName === req.name" class="leave-table__reject-row">
            <input
              v-model="rejectReason"
              type="text"
              class="form-input reject-reason-input"
              placeholder="Enter rejection reason..."
            />
            <button
              class="btn-sm btn-confirm-reject"
              @click="handleReject(req.name)"
            >
              Confirm Reject
            </button>
            <button
              class="btn-sm btn-ghost"
              @click="cancelReject"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import SkeletonLoader from '../shared/SkeletonLoader.vue'

const { getStudentLeaveRequests, approveStudentLeave, rejectStudentLeave } = useFacultyApi()

const requests = ref([])
const loading = ref(true)
const selectedNames = ref([])
const rejectingName = ref(null)
const rejectReason = ref('')

const allSelected = computed(() =>
  requests.value.length > 0 && selectedNames.value.length === requests.value.length
)

function toggleSelectAll() {
  if (allSelected.value) {
    selectedNames.value = []
  } else {
    selectedNames.value = requests.value.map(r => r.name)
  }
}

function toggleSelect(name) {
  const idx = selectedNames.value.indexOf(name)
  if (idx >= 0) {
    selectedNames.value.splice(idx, 1)
  } else {
    selectedNames.value.push(name)
  }
}

function showRejectInput(name) {
  rejectingName.value = name
  rejectReason.value = ''
}

function cancelReject() {
  rejectingName.value = null
  rejectReason.value = ''
}

async function handleApprove(name) {
  await approveStudentLeave(name)
  requests.value = requests.value.filter(r => r.name !== name)
  selectedNames.value = selectedNames.value.filter(n => n !== name)
}

async function handleReject(name) {
  await rejectStudentLeave(name, rejectReason.value)
  requests.value = requests.value.filter(r => r.name !== name)
  rejectingName.value = null
  rejectReason.value = ''
}

async function handleBulkApprove() {
  const toApprove = [...selectedNames.value]
  for (const name of toApprove) {
    await approveStudentLeave(name)
  }
  requests.value = requests.value.filter(r => !toApprove.includes(r.name))
  selectedNames.value = []
}

onMounted(async () => {
  try {
    const result = await getStudentLeaveRequests()
    requests.value = result.data || []
  } catch (e) {
    // silently handle
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.student-leave-queue {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

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

.bulk-bar {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-default);
  background: var(--gray-50);
}

.leave-table__header {
  display: flex;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--gray-50);
  border-bottom: 1px solid var(--border-default);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
}

.leave-table__row {
  display: flex;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle, var(--gray-100));
  font-size: var(--text-sm);
}

.leave-table__row:hover {
  background: var(--gray-50);
}

.leave-table__cell {
  padding: 0 var(--space-2);
}

.leave-table__cell--check {
  width: 40px;
  flex-shrink: 0;
}

.leave-table__cell--name {
  flex: 2;
  font-weight: var(--font-semibold);
}

.leave-table__cell--roll {
  flex: 1;
  color: var(--text-secondary);
}

.leave-table__cell--date {
  flex: 1;
}

.leave-table__cell--reason {
  flex: 2;
  color: var(--text-secondary);
}

.leave-table__cell--actions {
  flex: 2;
  display: flex;
  gap: var(--space-2);
  justify-content: flex-end;
}

.btn-approve {
  background: var(--success);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  padding: var(--space-1) var(--space-3);
  cursor: pointer;
  font-size: var(--text-xs);
}

.btn-reject {
  color: var(--error);
  font-size: var(--text-xs);
}

.leave-table__reject-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  padding-left: calc(40px + var(--space-4));
  background: var(--gray-50);
  border-bottom: 1px solid var(--border-subtle, var(--gray-100));
}

.reject-reason-input {
  flex: 1;
  font-size: var(--text-sm);
}

.btn-confirm-reject {
  background: var(--error);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  padding: var(--space-1) var(--space-3);
  cursor: pointer;
  font-size: var(--text-xs);
  white-space: nowrap;
}
</style>
