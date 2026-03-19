<template>
  <div class="card filter-bar">
    <div class="filter-bar__toggle" v-if="isMobile">
      <button class="btn-ghost btn-sm" @click="showFilters = !showFilters">
        <span class="material-symbols-outlined">filter_list</span>
        Filters
      </button>
    </div>

    <div class="filter-bar__content" v-show="!isMobile || showFilters">
      <div class="filter-item">
        <label class="filter-label" for="filter-date-from">Date From</label>
        <input id="filter-date-from" type="date" class="form-input" v-model="dateFrom" />
      </div>

      <div class="filter-item">
        <label class="filter-label" for="filter-date-to">Date To</label>
        <input id="filter-date-to" type="date" class="form-input" v-model="dateTo" />
      </div>

      <div class="filter-item">
        <label class="filter-label" for="filter-academic-year">Academic Year</label>
        <select id="filter-academic-year" class="form-select" v-model="academicYear">
          <option value="">All Years</option>
          <option v-for="year in academicYears" :key="year" :value="year">{{ year }}</option>
        </select>
      </div>

      <div class="filter-item">
        <label class="filter-label" for="filter-department">Department</label>
        <select id="filter-department" class="form-select" v-model="department">
          <option value="">All Departments</option>
          <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
        </select>
      </div>

      <div class="filter-item">
        <label class="filter-label" for="filter-program">Program</label>
        <select id="filter-program" class="form-select" v-model="program">
          <option value="">All Programs</option>
          <option v-for="prog in programs" :key="prog" :value="prog">{{ prog }}</option>
        </select>
      </div>

      <div class="filter-actions">
        <button class="btn-primary btn-sm" @click="applyFilters">Apply Filters</button>
        <button class="btn-ghost btn-sm" @click="clearFilters">Clear Filters</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  academicYears: { type: Array, default: () => [] },
  departments: { type: Array, default: () => [] },
  programs: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['filter-change'])

const dateFrom = ref('')
const dateTo = ref('')
const academicYear = ref('')
const department = ref('')
const program = ref('')
const showFilters = ref(false)
const isMobile = ref(false)

function getFilterState() {
  return {
    dateFrom: dateFrom.value,
    dateTo: dateTo.value,
    academicYear: academicYear.value,
    department: department.value,
    program: program.value,
  }
}

function applyFilters() {
  emit('filter-change', getFilterState())
}

function clearFilters() {
  dateFrom.value = ''
  dateTo.value = ''
  academicYear.value = ''
  department.value = ''
  program.value = ''
  emit('filter-change', getFilterState())
}
</script>

<style scoped>
.filter-bar {
  background: var(--bg-card);
  border-color: var(--border-default);
}

.filter-bar__content {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: flex-end;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 140px;
}

.filter-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.filter-actions {
  display: flex;
  gap: var(--space-2);
  align-items: flex-end;
  margin-left: auto;
}

@media (max-width: 767px) {
  .filter-bar__content {
    flex-direction: column;
  }

  .filter-item {
    width: 100%;
  }

  .filter-actions {
    margin-left: 0;
    width: 100%;
  }
}
</style>
