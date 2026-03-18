<template>
  <div class="faculty-notices">
    <h1 class="page-title">Announcements</h1>

    <!-- Category filter -->
    <div class="notice-filters">
      <button
        :class="['notice-filter-btn', { 'notice-filter-btn--active': !selectedCategory }]"
        @click="filterByCategory(null)"
      >
        All
      </button>
      <button
        v-for="cat in categories"
        :key="cat"
        :class="['notice-filter-btn', { 'notice-filter-btn--active': selectedCategory === cat }]"
        @click="filterByCategory(cat)"
      >
        {{ cat }}
      </button>
    </div>

    <!-- Loading state -->
    <template v-if="loading">
      <div class="notice-skeleton" v-for="n in 5" :key="n">
        <SkeletonLoader height="80px" />
      </div>
    </template>

    <!-- Empty state -->
    <template v-else-if="notices.length === 0">
      <div class="notice-empty">
        <span class="material-symbols-outlined notice-empty-icon">campaign</span>
        <h4 class="notice-empty-title">No announcements</h4>
        <p class="notice-empty-body">There are no announcements to display. Check back later.</p>
      </div>
    </template>

    <!-- Notice list -->
    <template v-else>
      <div class="notice-list">
        <div
          v-for="notice in notices"
          :key="notice.name"
          :class="[
            'notice-card',
            { 'notice-card--emergency': (notice.category || '').toLowerCase() === 'emergency' },
          ]"
        >
          <div class="notice-card-header">
            <span :class="['notice-badge', `notice-badge--${(notice.category || '').toLowerCase()}`]">
              <span v-if="(notice.category || '').toLowerCase() === 'emergency'" class="material-symbols-outlined notice-warning-icon">warning</span>
              {{ notice.category }}
            </span>
            <span class="notice-date">{{ notice.posting_date }}</span>
          </div>
          <h3 class="notice-title">{{ notice.title }}</h3>
          <p class="notice-content">{{ notice.content }}</p>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalCount > pageLength" class="notice-pagination">
        <span class="notice-pagination-info">
          Showing {{ start + 1 }}-{{ Math.min(start + pageLength, totalCount) }} of {{ totalCount }}
        </span>
        <div class="notice-pagination-buttons">
          <button
            class="btn-ghost btn-sm"
            :disabled="start === 0"
            @click="prevPage"
          >
            Previous
          </button>
          <button
            class="btn-ghost btn-sm"
            :disabled="start + pageLength >= totalCount"
            @click="nextPage"
          >
            Next
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

const { getAnnouncements } = useFacultyApi()

const loading = ref(true)
const notices = ref([])
const totalCount = ref(0)
const selectedCategory = ref(null)
const start = ref(0)
const pageLength = 20

const categories = ['Academic', 'Administrative', 'Emergency']

async function fetchNotices() {
  loading.value = true
  try {
    const params = { start: start.value, page_length: pageLength }
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    const result = await getAnnouncements(params)
    if (result) {
      notices.value = result.data || []
      totalCount.value = result.total_count || 0
    }
  } catch (e) {
    notices.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

function filterByCategory(category) {
  selectedCategory.value = category
  start.value = 0
  fetchNotices()
}

function prevPage() {
  start.value = Math.max(0, start.value - pageLength)
  fetchNotices()
}

function nextPage() {
  start.value += pageLength
  fetchNotices()
}

onMounted(fetchNotices)
</script>

<style scoped>
.page-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.notice-filters {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
}

.notice-filter-btn {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  background: var(--bg-card);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast) var(--ease-in-out);
}

.notice-filter-btn:hover {
  background: var(--gray-100);
  color: var(--text-primary);
}

.notice-filter-btn--active {
  background: var(--primary);
  color: var(--white);
  border-color: var(--primary);
}

.notice-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.notice-card {
  padding: var(--space-4);
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  border-left: 3px solid transparent;
}

.notice-card--emergency {
  background: var(--error-tint);
  border-left-color: var(--error);
}

.notice-card-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.notice-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.notice-badge--academic {
  background: var(--primary-light);
  color: var(--primary);
}

.notice-badge--administrative {
  background: var(--gray-100);
  color: var(--gray-500);
}

.notice-badge--emergency {
  background: var(--error-light);
  color: var(--error);
}

.notice-warning-icon {
  font-size: 14px;
}

.notice-date {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.notice-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.notice-content {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.notice-empty {
  text-align: center;
  padding: var(--space-12) var(--space-4);
}

.notice-empty-icon {
  font-size: 48px;
  color: var(--text-muted);
}

.notice-empty-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-top: var(--space-3);
}

.notice-empty-body {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-top: var(--space-2);
}

.notice-skeleton {
  margin-bottom: var(--space-3);
}

.notice-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-default);
}

.notice-pagination-info {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.notice-pagination-buttons {
  display: flex;
  gap: var(--space-2);
}
</style>
