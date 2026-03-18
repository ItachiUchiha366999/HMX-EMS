import { ref, onMounted, onUnmounted } from 'vue'

function resolveColors() {
  const style = getComputedStyle(document.documentElement)
  return {
    primary: style.getPropertyValue('--primary').trim() || '#4F46E5',
    success: style.getPropertyValue('--success').trim() || '#10B981',
    warning: style.getPropertyValue('--warning').trim() || '#F59E0B',
    error: style.getPropertyValue('--error').trim() || '#EF4444',
    info: style.getPropertyValue('--info').trim() || '#3B82F6',
    secondary: style.getPropertyValue('--secondary').trim() || '#9333EA',
    textPrimary: style.getPropertyValue('--text-primary').trim() || '#0F172A',
    textSecondary: style.getPropertyValue('--text-secondary').trim() || '#64748B',
    bgCard: style.getPropertyValue('--bg-card').trim() || '#FFFFFF',
  }
}

export function useThemeColors() {
  const colors = ref(resolveColors())
  let observer

  onMounted(() => {
    observer = new MutationObserver(() => {
      colors.value = resolveColors()
    })
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme'],
    })
  })

  onUnmounted(() => observer?.disconnect())

  return { colors }
}
