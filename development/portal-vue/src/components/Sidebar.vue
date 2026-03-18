<template>
  <aside class="portal-sidebar">
    <div class="sidebar-header">
      <span class="sidebar-logo">EduPortal</span>
    </div>

    <div class="sidebar-user">
      <img
        v-if="session.user_image"
        :src="session.user_image"
        class="user-avatar"
        alt="User"
      />
      <div v-else class="user-avatar user-avatar--placeholder">
        {{ initials }}
      </div>
      <div class="user-info">
        <span class="user-name">{{ session.full_name || session.logged_user }}</span>
      </div>
    </div>

    <nav class="sidebar-nav">
      <RouterLink
        v-for="item in visibleItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        active-class="nav-item--active"
      >
        <span class="nav-icon material-symbols-outlined">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <a href="/logout" class="nav-item nav-item--logout">
        <span class="nav-icon material-symbols-outlined">logout</span>
        <span class="nav-label">Sign out</span>
      </a>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useSessionStore } from '../stores/session.js'
import { navItems } from '../config/navigation.js'

const session = useSessionStore()

// Show only items where the user holds at least one of the required roles
const visibleItems = computed(() =>
  navItems.filter((item) =>
    item.roles.some((role) => session.roles.includes(role))
  )
)

const initials = computed(() => {
  const name = session.full_name || session.logged_user || '?'
  return name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('')
})
</script>

<style scoped>
.portal-sidebar {
  width: 240px;
  min-width: 240px;
  background: #0f172a;
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #1e293b;
}

.sidebar-logo {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
}

.sidebar-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #1e293b;
}

.user-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  object-fit: cover;
}

.user-avatar--placeholder {
  background: #334155;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
}

.user-name {
  font-size: 0.85rem;
  font-weight: 500;
  color: #f1f5f9;
}

.sidebar-nav {
  flex: 1;
  padding: 0.5rem 0;
}

.sidebar-footer {
  padding: 0.5rem 0;
  border-top: 1px solid #1e293b;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 1.5rem;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.875rem;
  transition: background 0.15s, color 0.15s;
  border-radius: 0;
}

.nav-item:hover {
  background: #1e293b;
  color: #f1f5f9;
}

.nav-item--active {
  background: #1e3a8a;
  color: #fff;
}

.nav-item--logout {
  color: #64748b;
}

.nav-item--logout:hover {
  background: #1e293b;
  color: #f87171;
}

.nav-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}
</style>
