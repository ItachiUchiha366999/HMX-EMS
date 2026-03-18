<template>
  <div class="report-viewer">
    <!-- Header -->
    <h3 class="report-viewer__heading">{{ reportName }}</h3>

    <!-- Error state -->
    <div v-if="reportError" class="alert-error report-viewer__error">
      Report failed to load. Check your filters and try again.
    </div>

    <!-- Filter section -->
    <div v-if="filterDefs.length > 0" class="report-viewer__filters">
      <div
        v-for="filter in filterDefs"
        :key="filter.fieldname"
        class="filter-item"
      >
        <label class="form-label report-viewer__filter-label">{{ filter.label }}</label>

        <!-- Select -->
        <select
          v-if="filter.fieldtype === 'Select'"
          class="form-select"
          v-model="filterValues[filter.fieldname]"
        >
          <option value="">Select...</option>
          <option
            v-for="opt in getSelectOptions(filter)"
            :key="opt"
            :value="opt"
          >
            {{ opt }}
          </option>
        </select>

        <!-- Date -->
        <input
          v-else-if="filter.fieldtype === 'Date'"
          type="date"
          class="form-input"
          v-model="filterValues[filter.fieldname]"
        />

        <!-- Check -->
        <input
          v-else-if="filter.fieldtype === 'Check'"
          type="checkbox"
          v-model="filterValues[filter.fieldname]"
        />

        <!-- Link / Data / Small Text / default -->
        <input
          v-else
          type="text"
          class="form-input"
          :placeholder="filter.fieldtype === 'Link' ? 'Select ' + (filter.options || '') : ''"
          v-model="filterValues[filter.fieldname]"
        />
      </div>

      <div class="filter-item report-viewer__run-wrapper">
        <button class="btn-primary btn-sm" @click="handleRunReport">
          Run Report
        </button>
      </div>
    </div>

    <!-- No filters: just show Run Report -->
    <div v-else class="report-viewer__filters">
      <button class="btn-primary btn-sm" @click="handleRunReport">
        Run Report
      </button>
    </div>

    <!-- Results -->
    <DataTable
      v-if="reportColumns.length > 0 || loading"
      :columns="reportColumns"
      :data="reportRows"
      :totalRows="reportRows.length"
      :loading="loading"
      :title="reportName"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useReportRunner } from '../../composables/useReportRunner.js'
import DataTable from './DataTable.vue'

const props = defineProps({
  reportName: {
    type: String,
    required: true,
  },
  defaultFilters: {
    type: Object,
    default: () => ({}),
  },
})

const {
  loadReportMeta,
  runReport,
  columns: rawColumns,
  rows: rawRows,
  filters: filterDefs,
  loading,
  error: reportError,
} = useReportRunner()

const filterValues = reactive({ ...props.defaultFilters })

// Map report columns to DataTable-compatible format
const reportColumns = computed(() => {
  return rawColumns.value.map(col => ({
    accessorKey: col.accessorKey,
    header: col.header,
    sortable: true,
  }))
})

const reportRows = computed(() => rawRows.value)

function getSelectOptions(filter) {
  if (!filter.options) return []
  if (typeof filter.options === 'string') {
    return filter.options.split('\n').filter(Boolean)
  }
  return Array.isArray(filter.options) ? filter.options : []
}

async function handleRunReport() {
  try {
    // Collect current filter values
    const activeFilters = {}
    for (const key in filterValues) {
      if (filterValues[key] !== '' && filterValues[key] !== null && filterValues[key] !== undefined) {
        activeFilters[key] = filterValues[key]
      }
    }
    await runReport(props.reportName, activeFilters)
  } catch (e) {
    // Error is already set in reportError by useReportRunner
  }
}

onMounted(async () => {
  try {
    await loadReportMeta(props.reportName)
    // Initialize filter values from loaded filter definitions
    filterDefs.value.forEach(f => {
      if (!(f.fieldname in filterValues)) {
        filterValues[f.fieldname] = f.default || ''
      }
    })
  } catch (e) {
    // Error handled by useReportRunner
  }
})
</script>

<style scoped>
.report-viewer__heading {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary, var(--gray-700));
  margin: 0 0 var(--space-3) 0;
}

.report-viewer__error {
  margin-bottom: var(--space-3);
}

.report-viewer__filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: flex-end;
  margin-bottom: var(--space-4);
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.report-viewer__filter-label {
  font-size: var(--text-xs);
  color: var(--text-secondary, var(--gray-500));
}

.report-viewer__run-wrapper {
  justify-content: flex-end;
}
</style>
