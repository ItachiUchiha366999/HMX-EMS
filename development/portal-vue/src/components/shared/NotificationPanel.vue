<template>
  <div class="card notification-panel">
    <div class="notification-header">
      <h3 class="notification-title">Notifications</h3>
      <button v-if="items.length > 0" class="btn-ghost btn-sm" @click="$emit('mark-all-read')">
        Mark all read
      </button>
    </div>

    <!-- Loading state -->
    <template v-if="loading">
      <div v-for="n in 3" :key="n" class="notification-skeleton">
        <SkeletonLoader circle height="40px" />
        <div class="notification-skeleton-text">
          <SkeletonLoader height="14px" width="60%" />
          <SkeletonLoader height="12px" width="80%" />
        </div>
      </div>
    </template>

    <!-- Empty state -->
    <template v-else-if="items.length === 0">
      <div class="notification-empty">
        <span class="material-symbols-outlined notification-empty-icon">notifications_none</span>
        <h4 class="notification-empty-title">All caught up</h4>
        <p class="notification-empty-body">No new notifications to show.</p>
      </div>
    </template>

    <!-- Items -->
    <template v-else>
      <div class="notification-list">
        <div
          v-for="item in visibleItems"
          :key="item.id"
          :class="['notification-item', { 'notification-item--unread': !item.read }]"
        >
          <div :class="['stat-icon', categoryIconClass(item.category)]">
            <span class="material-symbols-outlined">{{ categoryIcon(item.category) }}</span>
          </div>
          <div class="notification-content">
            <div class="notification-item-title">{{ item.title }}</div>
            <div class="notification-item-body">{{ item.body }}</div>
            <div class="notification-item-timestamp">{{ item.timestamp }}</div>
          </div>
          <div v-if="!item.read" class="notification-unread-dot" />
          <button class="btn-icon btn-ghost btn-sm notification-dismiss" @click="$emit('dismiss', item.id)">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
      </div>
      <div class="notification-footer">
        <a class="notification-view-all" @click.prevent="$emit('view-all')">View all notifications</a>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SkeletonLoader from './SkeletonLoader.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

defineEmits(['dismiss', 'mark-all-read', 'view-all'])

const visibleItems = computed(() => props.items.slice(0, 5))

function categoryIconClass(category) {
  const map = {
    assignment: 'primary',
    grade: 'warning',
    deadline: 'error',
    schedule: 'info',
  }
  return map[category] || 'primary'
}

function categoryIcon(category) {
  const map = {
    assignment: 'assignment',
    grade: 'grade',
    deadline: 'schedule',
    schedule: 'event',
  }
  return map[category] || 'notifications'
}
</script>

<style scoped>
.notification-panel {
  background: var(--bg-card);
  border-color: var(--border-default);
}

.notification-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.notification-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.notification-list {
  display: flex;
  flex-direction: column;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--border-subtle);
  position: relative;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-item-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.notification-item-body {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-top: var(--space-1);
}

.notification-item-timestamp {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--space-1);
}

.notification-unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  flex-shrink: 0;
  margin-top: var(--space-2);
}

.notification-dismiss {
  flex-shrink: 0;
}

.notification-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-12) var(--space-6);
  text-align: center;
}

.notification-empty-icon {
  font-size: 48px;
  color: var(--gray-300);
  margin-bottom: var(--space-4);
}

.notification-empty-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
}

.notification-empty-body {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.notification-footer {
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-subtle);
  text-align: center;
}

.notification-view-all {
  font-size: var(--text-sm);
  color: var(--primary);
  cursor: pointer;
  text-decoration: none;
}

.notification-view-all:hover {
  text-decoration: underline;
}

.notification-skeleton {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-3) 0;
}

.notification-skeleton-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
