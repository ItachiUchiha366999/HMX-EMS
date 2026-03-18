<template>
  <div class="card data-table">
    <!-- Header bar -->
    <div class="data-table__header">
      <div class="data-table__header-left">
        <div v-if="searchable" class="data-table__search-wrapper">
          <span class="material-symbols-outlined data-table__search-icon">search</span>
          <input
            type="text"
            class="form-input data-table__search"
            placeholder="Search..."
            :value="searchValue"
            @input="handleSearchInput"
          />
        </div>
        <span class="data-table__count">
          Showing {{ showingStart }}-{{ showingEnd }} of {{ totalRows }}
        </span>
      </div>
      <div class="data-table__header-right">
        <button
          class="btn-icon btn-secondary btn-sm"
          aria-label="Export to PDF"
          @click="handleExportPdf"
        >
          <span class="material-symbols-outlined">picture_as_pdf</span>
        </button>
        <button
          class="btn-icon btn-secondary btn-sm"
          aria-label="Export to Excel"
          @click="handleExportExcel"
        >
          <span class="material-symbols-outlined">table_view</span>
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="table-wrapper">
      <table class="table">
        <thead>
          <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
            <th
              v-for="header in headerGroup.headers"
              :key="header.id"
              :class="{
                'data-table__th--sortable': header.column.columnDef.sortable,
                'data-table__th--sorted': header.column.getIsSorted(),
              }"
              :aria-sort="
                header.column.getIsSorted() === 'asc' ? 'ascending' :
                header.column.getIsSorted() === 'desc' ? 'descending' :
                header.column.columnDef.sortable ? 'none' : undefined
              "
              @click="header.column.columnDef.sortable ? handleSort(header.column) : undefined"
            >
              <div class="data-table__th-content">
                <FlexRender
                  :render="header.column.columnDef.header"
                  :props="header.getContext()"
                />
                <span
                  v-if="header.column.columnDef.sortable"
                  class="material-symbols-outlined data-table__sort-icon"
                  :class="{
                    'data-table__sort-icon--active': header.column.getIsSorted(),
                  }"
                >
                  {{ header.column.getIsSorted() === 'desc' ? 'arrow_downward' : 'arrow_upward' }}
                </span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody v-if="loading">
          <tr v-for="n in 5" :key="'skeleton-' + n">
            <td v-for="col in allColumns" :key="'skel-' + n + '-' + col.id">
              <SkeletonLoader width="80%" height="16px" />
            </td>
          </tr>
        </tbody>
        <tbody v-else-if="data.length === 0">
          <tr>
            <td :colspan="allColumns.length" class="data-table__empty">
              <div class="data-table__empty-content">
                <span class="material-symbols-outlined data-table__empty-icon">table_chart</span>
                <p class="data-table__empty-heading">No records found</p>
                <p class="data-table__empty-body">Try adjusting your filters or search terms.</p>
              </div>
            </td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr
            v-for="row in table.getRowModel().rows"
            :key="row.id"
            :class="{
              'data-table__row--selected': row.getIsSelected(),
            }"
          >
            <td v-for="cell in row.getVisibleCells()" :key="cell.id">
              <FlexRender
                :render="cell.column.columnDef.cell"
                :props="cell.getContext()"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="pageCount > 1" class="data-table__pagination">
      <span class="data-table__pagination-info">
        Showing {{ showingStart }}-{{ showingEnd }} of {{ totalRows }}
      </span>
      <div class="data-table__pagination-buttons">
        <button
          class="btn-secondary btn-sm"
          :disabled="!table.getCanPreviousPage()"
          aria-label="Previous page"
          @click="handlePageChange(currentPageIndex - 1)"
        >
          <span class="material-symbols-outlined">navigate_before</span>
        </button>
        <button
          v-for="page in visiblePages"
          :key="page"
          :class="page - 1 === currentPageIndex ? 'btn-primary btn-sm' : 'btn-secondary btn-sm'"
          @click="handlePageChange(page - 1)"
        >
          {{ page }}
        </button>
        <button
          class="btn-secondary btn-sm"
          :disabled="!table.getCanNextPage()"
          aria-label="Next page"
          @click="handlePageChange(currentPageIndex + 1)"
        >
          <span class="material-symbols-outlined">navigate_next</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, h } from 'vue'
import {
  useVueTable,
  getCoreRowModel,
  getSortedRowModel,
  FlexRender,
} from '@tanstack/vue-table'
import SkeletonLoader from './SkeletonLoader.vue'
import { useExportPdf } from '../../composables/useExportPdf.js'
import { useExportExcel } from '../../composables/useExportExcel.js'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
  },
  data: {
    type: Array,
    required: true,
  },
  totalRows: {
    type: Number,
    default: 0,
  },
  pageSize: {
    type: Number,
    default: 20,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  selectable: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '',
  },
  searchable: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['page-change', 'sort-change', 'selection-change', 'search-change'])

const { exportToPdf } = useExportPdf()
const { exportToExcel } = useExportExcel()

// State
const sorting = ref([])
const rowSelection = ref({})
const currentPageIndex = ref(0)
const searchValue = ref('')
let searchTimeout = null

// Computed
const pageCount = computed(() => Math.ceil(props.totalRows / props.pageSize))

const showingStart = computed(() => {
  if (props.totalRows === 0) return 0
  return currentPageIndex.value * props.pageSize + 1
})

const showingEnd = computed(() => {
  const end = (currentPageIndex.value + 1) * props.pageSize
  return Math.min(end, props.totalRows)
})

const visiblePages = computed(() => {
  const pages = []
  for (let i = 1; i <= pageCount.value; i++) {
    pages.push(i)
  }
  return pages
})

// Build column definitions
const allColumns = computed(() => {
  const cols = []

  if (props.selectable) {
    cols.push({
      id: 'select',
      header: ({ table }) => h('input', {
        type: 'checkbox',
        checked: table.getIsAllRowsSelected(),
        onChange: table.getToggleAllRowsSelectedHandler(),
      }),
      cell: ({ row }) => h('input', {
        type: 'checkbox',
        checked: row.getIsSelected(),
        onChange: row.getToggleSelectedHandler(),
      }),
      enableSorting: false,
    })
  }

  props.columns.forEach(col => {
    cols.push({
      accessorKey: col.accessorKey,
      header: col.header,
      sortable: col.sortable || false,
      enableSorting: col.sortable || false,
    })
  })

  return cols
})

// Table instance
const table = useVueTable({
  get data() { return props.data },
  get columns() { return allColumns.value },
  state: {
    get sorting() { return sorting.value },
    get rowSelection() { return rowSelection.value },
    get pagination() {
      return {
        pageIndex: currentPageIndex.value,
        pageSize: props.pageSize,
      }
    },
  },
  manualPagination: true,
  manualSorting: true,
  get pageCount() { return pageCount.value },
  onSortingChange: updater => {
    sorting.value = typeof updater === 'function' ? updater(sorting.value) : updater
    if (sorting.value.length > 0) {
      emit('sort-change', { id: sorting.value[0].id, desc: sorting.value[0].desc })
    }
  },
  onRowSelectionChange: updater => {
    rowSelection.value = typeof updater === 'function' ? updater(rowSelection.value) : updater
    const selectedRows = table.getSelectedRowModel().rows.map(r => r.original)
    emit('selection-change', selectedRows)
  },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  enableRowSelection: props.selectable,
})

// Handlers
function handleSort(column) {
  column.toggleSorting()
}

function handlePageChange(pageIndex) {
  currentPageIndex.value = pageIndex
  emit('page-change', { pageIndex, pageSize: props.pageSize })
}

function handleSearchInput(event) {
  searchValue.value = event.target.value
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    emit('search-change', searchValue.value)
  }, 300)
}

function handleExportPdf() {
  exportToPdf({
    title: props.title || 'Export',
    columns: props.columns,
    rows: props.data,
  })
}

function handleExportExcel() {
  exportToExcel({
    title: props.title || 'Export',
    columns: props.columns,
    rows: props.data,
  })
}
</script>

<style scoped>
.data-table {
  overflow: hidden;
}

.data-table__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  gap: var(--space-3);
  flex-wrap: wrap;
}

.data-table__header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex: 1;
}

.data-table__header-right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.data-table__search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.data-table__search-icon {
  position: absolute;
  left: var(--space-2);
  font-size: 18px;
  color: var(--text-muted, var(--gray-400));
  pointer-events: none;
}

.data-table__search {
  padding-left: var(--space-8, 2rem);
  min-width: 200px;
}

.data-table__count {
  font-size: var(--text-sm);
  color: var(--text-secondary, var(--gray-500));
  white-space: nowrap;
}

.data-table__th-content {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.data-table__th--sortable {
  cursor: pointer;
  user-select: none;
}

.data-table__sort-icon {
  font-size: 12px;
  color: var(--gray-300);
  transition: color 0.15s;
}

.data-table__sort-icon--active {
  color: var(--primary, #4F46E5);
}

.data-table__row--selected {
  background: var(--primary-light, rgba(79, 70, 229, 0.05));
}

.data-table__empty {
  text-align: center;
  padding: var(--space-8) var(--space-4);
}

.data-table__empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}

.data-table__empty-icon {
  font-size: 48px;
  color: var(--gray-300);
}

.data-table__empty-heading {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary, var(--gray-700));
  margin: 0;
}

.data-table__empty-body {
  font-size: var(--text-sm);
  color: var(--text-secondary, var(--gray-500));
  margin: 0;
}

.data-table__pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--border-subtle, var(--gray-100));
}

.data-table__pagination-info {
  font-size: var(--text-sm);
  color: var(--text-secondary, var(--gray-500));
}

.data-table__pagination-buttons {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}
</style>
