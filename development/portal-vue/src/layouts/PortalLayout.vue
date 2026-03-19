<template>
  <div class="portal-shell">
    <a href="#main-content" class="skip-to-content">Skip to main content</a>
    <Sidebar />
    <main id="main-content" class="portal-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import Sidebar from '../components/Sidebar.vue'
</script>

<style scoped>
.portal-shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
  font-family: var(--font-family);
  background: var(--bg-surface);
}

.skip-to-content {
  position: absolute;
  top: -100%;
  left: 0;
  z-index: 9999;
  padding: 0.75rem 1.5rem;
  background: var(--primary, #4F46E5);
  color: #FFFFFF;
  text-decoration: none;
  font-weight: var(--font-semibold, 600);
  border-radius: 0 0 var(--radius-md, 6px) 0;
}

.skip-to-content:focus {
  top: 0;
}

.portal-main {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}
</style>
