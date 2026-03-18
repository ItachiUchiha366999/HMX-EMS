<template>
  <div class="research-publications">
    <template v-if="loading">
      <div class="pub-skeleton">
        <SkeletonLoader v-for="n in 3" :key="n" height="80px" />
      </div>
    </template>
    <template v-else-if="publications.length === 0">
      <div class="empty-state">
        <span class="material-symbols-outlined empty-state-icon">article</span>
        <p class="empty-state-heading">No publications found</p>
        <p class="empty-state-body">Research publications linked to your profile will appear here.</p>
      </div>
    </template>
    <template v-else>
      <!-- Count KPIs -->
      <div class="pub-kpi-grid">
        <KpiCard
          label="Journals"
          :value="byType.Journal || 0"
          status="info"
          icon="menu_book"
        />
        <KpiCard
          label="Conferences"
          :value="byType.Conference || 0"
          status="info"
          icon="groups"
        />
        <KpiCard
          label="Books"
          :value="byType.Book || 0"
          status="info"
          icon="auto_stories"
        />
      </div>

      <!-- Publication list -->
      <div class="pub-list">
        <div
          v-for="pub in publications"
          :key="pub.name"
          class="pub-item"
        >
          <div class="pub-item__header" @click="toggleExpand(pub.name)">
            <span :class="['pub-badge', `pub-badge--${(pub.type || '').toLowerCase()}`]">
              {{ pub.type }}
            </span>
            <div class="pub-item__info">
              <div class="pub-item__title">{{ pub.title }}</div>
              <div class="pub-item__meta">
                {{ pub.journal_conference }} {{ pub.publication_date ? `(${pub.publication_date.slice(0, 4)})` : '' }}
              </div>
            </div>
            <div class="pub-item__citations" v-if="pub.impact_factor">
              IF: {{ pub.impact_factor }}
            </div>
          </div>

          <!-- Expanded detail -->
          <div v-if="expandedName === pub.name" class="pub-item__detail">
            <div v-if="pub.doi_isbn" class="pub-detail-row">
              <span class="pub-detail-label">DOI/ISBN:</span>
              <a v-if="pub.doi_isbn.startsWith('10.')" :href="`https://doi.org/${pub.doi_isbn}`" target="_blank" class="pub-detail-link">{{ pub.doi_isbn }}</a>
              <span v-else>{{ pub.doi_isbn }}</span>
            </div>
            <div v-if="pub.scopus_indexed" class="pub-detail-row">
              <span class="pub-badge pub-badge--scopus">Scopus Indexed</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFacultyApi } from '../../composables/useFacultyApi.js'
import KpiCard from '../shared/KpiCard.vue'
import SkeletonLoader from '../shared/SkeletonLoader.vue'

const { getPublications } = useFacultyApi()
const publications = ref([])
const byType = ref({})
const loading = ref(true)
const expandedName = ref(null)

function toggleExpand(name) {
  expandedName.value = expandedName.value === name ? null : name
}

onMounted(async () => {
  try {
    const result = await getPublications()
    publications.value = result.publications || []
    byType.value = result.by_type || {}
  } catch (e) {
    // silently handle
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.pub-skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
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

.pub-kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.pub-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.pub-item {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.pub-item__header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4);
  cursor: pointer;
}

.pub-item__header:hover {
  background: var(--gray-50);
}

.pub-badge {
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  padding: 2px var(--space-2);
  font-weight: var(--font-semibold);
  white-space: nowrap;
  flex-shrink: 0;
}

.pub-badge--journal {
  background: var(--primary-light);
  color: var(--primary);
}

.pub-badge--conference {
  background: var(--info-light, #DBEAFE);
  color: var(--info, #3B82F6);
}

.pub-badge--book {
  background: var(--gray-100);
  color: var(--gray-600);
}

.pub-badge--scopus {
  background: var(--success-light);
  color: var(--success);
}

.pub-item__info {
  flex: 1;
}

.pub-item__title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.pub-item__meta {
  font-size: var(--text-xs);
  color: var(--gray-500);
  margin-top: 2px;
}

.pub-item__citations {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  white-space: nowrap;
}

.pub-item__detail {
  padding: var(--space-4);
  background: var(--gray-50);
  border-top: 1px solid var(--border-subtle, var(--gray-100));
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.pub-detail-row {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.pub-detail-label {
  font-weight: var(--font-semibold);
  margin-right: var(--space-1);
}

.pub-detail-link {
  color: var(--primary);
  text-decoration: none;
}

.pub-detail-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .pub-kpi-grid {
    grid-template-columns: 1fr;
  }
}
</style>
