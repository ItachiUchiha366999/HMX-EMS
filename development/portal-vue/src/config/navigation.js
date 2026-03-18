/**
 * Portal navigation configuration.
 * Each item:
 *   - path: Vue Router route path
 *   - label: Display name
 *   - icon: Material Symbols icon name (or any icon identifier)
 *   - roles: Frappe roles that grant access to this item
 *
 * Multi-role users see the UNION of all items their roles permit.
 * This file is the single source of truth for sidebar items AND route meta.
 */
export const navItems = [
  // Management
  {
    path: '/management',
    label: 'Management Dashboard',
    icon: 'dashboard',
    roles: ['University Admin', 'University VC', 'University Dean', 'University Registrar'],
  },
  // Faculty
  {
    path: '/faculty',
    label: 'Dashboard',
    icon: 'dashboard',
    roles: ['University Faculty', 'University HOD'],
  },
  {
    path: '/faculty/teaching',
    label: 'Teaching',
    icon: 'school',
    roles: ['University Faculty', 'University HOD'],
  },
  {
    path: '/faculty/work',
    label: 'My Work',
    icon: 'work',
    roles: ['University Faculty', 'University HOD'],
  },
  {
    path: '/faculty/notices',
    label: 'Notices',
    icon: 'campaign',
    roles: ['University Faculty', 'University HOD'],
  },
  // HOD
  {
    path: '/hod',
    label: 'Department Overview',
    icon: 'corporate_fare',
    roles: ['University HOD'],
  },
  // Student
  {
    path: '/student',
    label: 'My Dashboard',
    icon: 'home',
    roles: ['University Student'],
  },
  // Finance
  {
    path: '/finance',
    label: 'Finance',
    icon: 'account_balance',
    roles: ['University Finance', 'University Admin'],
  },
  // Admin
  {
    path: '/admin/health',
    label: 'System Health',
    icon: 'monitor_heart',
    roles: ['University Admin'],
  },
]
