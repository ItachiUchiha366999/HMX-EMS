<template>
  <div class="toast-container" v-if="toasts.length">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast-item"
        :class="`toast-item--${toast.type}`"
        role="status"
        aria-live="polite"
      >
        <span class="material-symbols-outlined toast-icon">
          {{ toast.type === 'error' ? 'error' : 'check_circle' }}
        </span>
        <span class="toast-message">{{ toast.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToast } from '@/composables/useToast.js'

const { toasts } = useToast()
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 16px;
  right: 16px;
  z-index: var(--z-tooltip);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.toast-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  font-size: var(--text-sm);
  min-width: 240px;
  max-width: 360px;
}

.toast-item--success {
  background: var(--success-light);
  color: var(--success-dark);
}

.toast-item--error {
  background: var(--error-light);
  color: var(--error-dark);
}

.toast-item--warning {
  background: var(--warning-light);
  color: var(--warning-dark);
}

.toast-item--info {
  background: var(--info-light);
  color: var(--info-dark);
}

.toast-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.toast-message {
  flex: 1;
}

.toast-enter-active {
  transition: all var(--transition-base) var(--ease-in-out);
}

.toast-leave-active {
  transition: all var(--transition-base) var(--ease-in-out);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
