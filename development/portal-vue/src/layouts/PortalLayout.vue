<template>
  <div class="portal-shell">
    <Sidebar />
    <main class="portal-main">
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

.portal-main {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}
</style>
