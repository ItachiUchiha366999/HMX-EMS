<template>
  <div class="tab-layout">
    <div class="tab-bar" role="tablist">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        role="tab"
        :aria-selected="modelValue === tab.id"
        :aria-controls="`tabpanel-${tab.id}`"
        :class="['tab-item', { 'tab-item--active': modelValue === tab.id }]"
        @click="$emit('update:modelValue', tab.id)"
      >
        {{ tab.label }}
      </button>
    </div>
    <div
      :id="`tabpanel-${modelValue}`"
      class="tab-content"
      role="tabpanel"
      :aria-labelledby="`tab-${modelValue}`"
    >
      <slot :name="modelValue" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  tabs: {
    type: Array,
    required: true,
    // Each tab: { id: string, label: string }
  },
  modelValue: {
    type: String,
    required: true,
  },
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.tab-bar {
  display: flex;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-default);
  padding: 0 var(--space-4);
  overflow-x: auto;
}

.tab-item {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  font-weight: var(--font-normal);
  color: var(--text-secondary);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition-fast) var(--ease-in-out);
}

.tab-item:hover:not(.tab-item--active) {
  color: var(--text-primary);
  background: var(--gray-100);
}

.tab-item--active {
  font-weight: var(--font-semibold);
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.tab-content {
  padding-top: var(--space-4);
}
</style>
