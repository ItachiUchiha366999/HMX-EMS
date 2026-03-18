<template>
  <div class="faculty-work">
    <h2 class="page-title">My Work</h2>

    <TabLayout
      :tabs="tabs"
      v-model="activeTab"
    >
      <template #leave>
        <div class="work-section">
          <h3 class="section-title">My Leave</h3>
          <LeaveBalanceCards @apply="showLeaveForm = true" />
          <LeaveApplyForm
            :show="showLeaveForm"
            :leave-types="leaveTypes"
            @close="showLeaveForm = false"
            @submitted="handleLeaveSubmitted"
          />
        </div>

        <div class="work-section">
          <h3 class="section-title">Recent Applications</h3>
          <DataTable
            :columns="leaveHistoryColumns"
            :data="leaveHistory"
            :total-rows="leaveHistoryTotal"
            :loading="leaveHistoryLoading"
            title="Leave History"
            @page-change="loadLeaveHistory"
          />
        </div>

        <div class="work-section">
          <h3 class="section-title">Student Leave Requests</h3>
          <StudentLeaveQueue />
        </div>
      </template>

      <template #workload>
        <WorkloadSummary />
      </template>

      <template #research>
        <ResearchPublications />
      </template>

      <template #obe>
        <ObeAttainment :courses="teachingCourses" />
      </template>
    </TabLayout>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import TabLayout from './TabLayout.vue'
import LeaveBalanceCards from './LeaveBalanceCards.vue'
import LeaveApplyForm from './LeaveApplyForm.vue'
import StudentLeaveQueue from './StudentLeaveQueue.vue'
import WorkloadSummary from './WorkloadSummary.vue'
import ResearchPublications from './ResearchPublications.vue'
import ObeAttainment from './ObeAttainment.vue'
import DataTable from '../shared/DataTable.vue'

const route = useRoute()
const { getLeaveBalance, getLeaveHistory: fetchLeaveHistory } = useFacultyApi()

const tabs = [
  { id: 'leave', label: 'Leave' },
  { id: 'workload', label: 'Workload' },
  { id: 'research', label: 'Research' },
  { id: 'obe', label: 'OBE' },
]

const activeTab = ref(route.query.tab || 'leave')
const showLeaveForm = ref(false)
const leaveTypes = ref([])
const teachingCourses = ref([])

// Leave history
const leaveHistory = ref([])
const leaveHistoryTotal = ref(0)
const leaveHistoryLoading = ref(true)

const leaveHistoryColumns = [
  { accessorKey: 'leave_type', header: 'Type' },
  { accessorKey: 'from_date', header: 'From' },
  { accessorKey: 'to_date', header: 'To' },
  { accessorKey: 'description', header: 'Reason' },
  { accessorKey: 'status', header: 'Status' },
]

async function loadLeaveHistory({ pageIndex = 0, pageSize = 10 } = {}) {
  leaveHistoryLoading.value = true
  try {
    const result = await fetchLeaveHistory({ start: pageIndex * pageSize, page_length: pageSize })
    leaveHistory.value = result.data || []
    leaveHistoryTotal.value = result.total_count || 0
  } catch (e) {
    // silently handle
  } finally {
    leaveHistoryLoading.value = false
  }
}

async function handleLeaveSubmitted() {
  showLeaveForm.value = false
  // Reload leave data
  await loadLeaveHistory()
}

onMounted(async () => {
  // Load leave types from balance data
  try {
    const balance = await getLeaveBalance()
    leaveTypes.value = balance.map(b => b.leave_type)
  } catch (e) {
    // silently handle
  }

  await loadLeaveHistory()
})
</script>

<style scoped>
.page-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.work-section {
  margin-bottom: var(--space-8);
}

.section-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}
</style>
