# Plugin-Based Modular Frontend Architecture

## Overview

This document explains the **plug-in/plug-out modular architecture** for the University ERP custom frontend.

### Core vs Optional Modules

The system has two types of modules:

**CORE MODULES (Always Present)**
- Student Portal
- Faculty Portal
- HR Module
- Accounts Module
- Admin Module

**OPTIONAL MODULES (Plug-in/Plug-out)**
- 🏠 **Hostel** - Room allocation, complaints, mess menu
- 🚌 **Transport** - Routes, bus tracking
- 📖 **Library** - Book search, borrowings, fines
- 💼 **Placement** - Job postings, applications, interviews

### What Plug-in/Plug-out Means

For optional modules (Hostel, Transport, Library, Placement):

1. **If client needs the module** → Include it in the build
2. **If client doesn't need it** → Simply don't include it - the module folder is removed entirely

This is NOT just hiding via configuration - the code is **physically not included** in the deployment.

---

## Architecture Concept

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           PLUGIN-BASED FRONTEND ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────────────────────────┘


                    CORE MODULES (Always Included)
                    ══════════════════════════════

┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   STUDENT     │ │   FACULTY     │ │     HR        │ │   ACCOUNTS    │ │    ADMIN      │
│   MODULE      │ │   MODULE      │ │   MODULE      │ │   MODULE      │ │   MODULE      │
│               │ │               │ │               │ │               │ │               │
│ • Dashboard   │ │ • Dashboard   │ │ • Dashboard   │ │ • Dashboard   │ │ • Users       │
│ • Academics   │ │ • Classes     │ │ • Employees   │ │ • Fees Mgmt   │ │ • Roles       │
│ • Fees        │ │ • Attendance  │ │ • Leave       │ │ • Payments    │ │ • Settings    │
│ • Exams       │ │ • Grades      │ │ • Payroll     │ │ • Reports     │ │ • Reports     │
│ • Timetable   │ │ • Students    │ │ • Reports     │ │               │ │               │
└───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘



                    OPTIONAL MODULES (Plug-in / Plug-out)
                    ══════════════════════════════════════

                    Include ONLY if client needs them

┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   🏠 HOSTEL   │ │ 🚌 TRANSPORT  │ │  📖 LIBRARY   │ │ 💼 PLACEMENT  │
│   (Optional)  │ │  (Optional)   │ │  (Optional)   │ │  (Optional)   │
│               │ │               │ │               │ │               │
│ • Room Alloc  │ │ • Routes      │ │ • Book Search │ │ • Job Posts   │
│ • Complaints  │ │ • Bus Track   │ │ • Borrowings  │ │ • Applications│
│ • Mess Menu   │ │ • Schedule    │ │ • Fines       │ │ • Interviews  │
│ • Fees        │ │ • Fees        │ │ • E-Resources │ │ • Companies   │
└───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘
       │                 │                 │                 │
       │                 │                 │                 │
       ▼                 ▼                 ▼                 ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                                                             │
   │   Client A: Include Hostel, Library                         │
   │   Client B: Include Hostel, Transport, Placement            │
   │   Client C: Include Library only                            │
   │   Client D: No optional modules                             │
   │                                                             │
   └─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
university-erp-frontend/
│
├── src/
│   │
│   ├── core/                       # Core framework (always present)
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── store/
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── auth.js
│   │   ├── layouts/
│   │   └── components/
│   │
│   ├── modules/
│   │   │
│   │   ├── student/                # ✓ CORE - Always included
│   │   │   ├── index.js
│   │   │   ├── routes.js
│   │   │   └── views/
│   │   │       ├── Dashboard.vue
│   │   │       ├── Academics.vue
│   │   │       ├── Fees.vue
│   │   │       └── Exams.vue
│   │   │
│   │   ├── faculty/                # ✓ CORE - Always included
│   │   │   ├── index.js
│   │   │   ├── routes.js
│   │   │   └── views/
│   │   │
│   │   ├── hr/                     # ✓ CORE - Always included
│   │   │   └── ...
│   │   │
│   │   ├── accounts/               # ✓ CORE - Always included
│   │   │   └── ...
│   │   │
│   │   ├── admin/                  # ✓ CORE - Always included
│   │   │   └── ...
│   │   │
│   │   └── optional/               # ⚡ OPTIONAL - Remove if not needed
│   │       │
│   │       ├── hostel/             # 🏠 Delete folder if not needed
│   │       │   ├── index.js
│   │       │   ├── routes.js
│   │       │   └── views/
│   │       │       ├── RoomAllocation.vue
│   │       │       ├── Complaints.vue
│   │       │       └── MessMenu.vue
│   │       │
│   │       ├── transport/          # 🚌 Delete folder if not needed
│   │       │   ├── index.js
│   │       │   ├── routes.js
│   │       │   └── views/
│   │       │       ├── Routes.vue
│   │       │       └── BusTracking.vue
│   │       │
│   │       ├── library/            # 📖 Delete folder if not needed
│   │       │   ├── index.js
│   │       │   ├── routes.js
│   │       │   └── views/
│   │       │       ├── BookSearch.vue
│   │       │       ├── MyBorrowings.vue
│   │       │       └── Fines.vue
│   │       │
│   │       └── placement/          # 💼 Delete folder if not needed
│   │           ├── index.js
│   │           ├── routes.js
│   │           └── views/
│   │               ├── JobPostings.vue
│   │               ├── Applications.vue
│   │               └── Interviews.vue
│   │
│   └── shared/                     # Shared components
│       ├── components/
│       └── utils/
│
├── modules.config.js               # Configure which optional modules to include
└── package.json
```

---

## How to Remove Optional Modules

### Simple Process - Just Delete the Folder

If a client doesn't need Hostel module:

```bash
# Simply delete the hostel folder
rm -rf src/modules/optional/hostel/
```

That's it! The system automatically:
1. Won't include hostel routes
2. Won't show hostel in navigation
3. Won't include hostel code in the build

### Configuration File (modules.config.js)

```javascript
// modules.config.js - Defines which optional modules exist

export default {
  // Core modules (always present, cannot be disabled)
  core: ['student', 'faculty', 'hr', 'accounts', 'admin'],

  // Optional modules - set to true if the folder exists
  // Set to false or remove if client doesn't need it
  optional: {
    hostel: true,       // Include hostel module
    transport: false,   // Don't include transport (folder removed)
    library: true,      // Include library module
    placement: true     // Include placement module
  }
}
```

### Client-Specific Deployments

```
CLIENT A: Large University (All modules)
────────────────────────────────────────
optional/
├── hostel/      ✓ Included
├── transport/   ✓ Included
├── library/     ✓ Included
└── placement/   ✓ Included


CLIENT B: Small College (No hostel/transport)
────────────────────────────────────────
optional/
├── library/     ✓ Included
└── placement/   ✓ Included
(hostel and transport folders deleted)


CLIENT C: Training Institute (No optional modules)
────────────────────────────────────────
optional/
(empty - all folders deleted)
```

### What Happens When Module is Removed?

1. **Navigation** - Menu items for that module won't appear
2. **Routes** - URLs like `/student/hostel` won't exist
3. **Build Size** - Code not included = smaller bundle
4. **No Errors** - System gracefully handles missing modules

---

## Module Manifest

Each module has a `manifest.json` that defines its capabilities:

```json
// @university-erp/student/src/manifest.json
{
  "id": "student",
  "name": "Student Portal",
  "version": "1.0.0",
  "description": "Student-facing portal for academics, fees, and more",

  "icon": "graduation-cap",
  "color": "#4F46E5",

  "requiredRoles": ["Student"],
  "optionalRoles": ["Guardian"],

  "requiredBackendApps": [
    "education",
    "university_erp"
  ],

  "navigation": {
    "position": 1,
    "showInSidebar": true,
    "label": "Student Portal"
  },

  "routes": [
    {
      "path": "/student",
      "name": "student-dashboard",
      "label": "Dashboard",
      "icon": "home"
    },
    {
      "path": "/student/academics",
      "name": "student-academics",
      "label": "Academics",
      "icon": "book"
    },
    {
      "path": "/student/fees",
      "name": "student-fees",
      "label": "Fees",
      "icon": "credit-card"
    }
  ],

  "permissions": {
    "view_attendance": true,
    "view_grades": true,
    "view_fees": true,
    "pay_fees": true,
    "download_documents": true
  },

  "dependencies": [
    "@university-erp/core",
    "@university-erp/shared"
  ]
}
```

---

## Configuration-Based Module Loading

### modules.config.js

```javascript
// Core configuration file that controls which modules are enabled

export default {
  // Application identity
  app: {
    name: "University ERP",
    logo: "/assets/logo.png",
    favicon: "/assets/favicon.ico"
  },

  // Enabled modules (plug-in/plug-out here)
  modules: {
    // Core modules (always enabled)
    core: { enabled: true },

    // User-facing modules (enable/disable as needed)
    student: {
      enabled: true,
      config: {
        showFees: true,
        showExams: true,
        showPlacement: true,
        showLibrary: true,
        showHostel: true,
        showTransport: false  // Disabled for this deployment
      }
    },

    faculty: {
      enabled: true,
      config: {
        showResearch: true,
        showMentoring: true
      }
    },

    hr: {
      enabled: true,
      config: {
        showRecruitment: false,  // Not needed for small institutions
        showTraining: true
      }
    },

    accounts: {
      enabled: true,
      config: {
        showBudgeting: true,
        showAssets: false
      }
    },

    admin: {
      enabled: true
    },

    // Optional modules
    hostel: { enabled: true },
    transport: { enabled: false },  // Disabled
    library: { enabled: true },
    placement: { enabled: true }
  },

  // Role-to-module mapping (which roles see which modules)
  roleModuleAccess: {
    "System Manager": ["admin", "hr", "accounts", "student", "faculty"],
    "HR Manager": ["hr"],
    "HR User": ["hr"],
    "Accounts Manager": ["accounts"],
    "Accounts User": ["accounts"],
    "Academic Admin": ["admin", "faculty", "student"],
    "Instructor": ["faculty"],
    "Student": ["student"],
    "Guardian": ["student"]  // Limited access
  }
}
```

---

## How Module Loading Works

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              MODULE LOADING FLOW                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘


  USER LOGIN                    CORE SHELL                    BACKEND
      │                             │                            │
      │  1. Login Request           │                            │
      │  ───────────────────────────┼──────────────────────────> │
      │                             │                            │
      │  2. Auth Response           │                            │
      │  (user data + roles)        │                            │
      │  <──────────────────────────┼─────────────────────────── │
      │                             │                            │
      │                             │                            │
      │     ┌───────────────────────┴───────────────────────┐   │
      │     │                                               │   │
      │     │  3. MODULE LOADER                             │   │
      │     │                                               │   │
      │     │  a) Read modules.config.js                    │   │
      │     │  b) Get user's roles from auth                │   │
      │     │  c) Filter enabled modules                    │   │
      │     │  d) Filter by role access                     │   │
      │     │  e) Check backend app dependencies            │   │
      │     │  f) Load qualifying modules dynamically       │   │
      │     │                                               │   │
      │     └───────────────────────┬───────────────────────┘   │
      │                             │                            │
      │                             │                            │
      │  4. Example: Student logs in                            │
      │     Roles: ["Student"]                                  │
      │                             │                            │
      │     Modules loaded:                                     │
      │     ✓ @university-erp/student                           │
      │     ✗ @university-erp/faculty (no access)               │
      │     ✗ @university-erp/hr (no access)                    │
      │     ✗ @university-erp/accounts (no access)              │
      │     ✗ @university-erp/admin (no access)                 │
      │                             │                            │
      │                             │                            │
      │  5. Navigation built dynamically                        │
      │     Only shows Student Portal menu                      │
      │                             │                            │
      │  <──────────────────────────│                            │
      │                             │                            │


  DIFFERENT USER (HR Manager):
  ────────────────────────────

      │  Login as HR Manager        │                            │
      │     Roles: ["HR Manager"]   │                            │
      │                             │                            │
      │     Modules loaded:                                     │
      │     ✓ @university-erp/hr                                │
      │     ✗ Others (no access)                                │
      │                             │                            │
      │     Navigation shows only HR menu                       │
      │                             │                            │


  MULTI-ROLE USER (Department Head):
  ───────────────────────────────────

      │  Login as Dept Head         │                            │
      │     Roles: ["Instructor",   │                            │
      │             "HR User"]      │                            │
      │                             │                            │
      │     Modules loaded:                                     │
      │     ✓ @university-erp/faculty                           │
      │     ✓ @university-erp/hr                                │
      │                             │                            │
      │     Navigation shows both                               │
      │     Faculty & HR menus                                  │
      │                             │                            │
```

---

## Implementation Code Examples

### 1. Module Loader Service

```javascript
// @university-erp/core/src/services/moduleLoader.js

import modulesConfig from '../config/modules.config.js';

class ModuleLoader {
  constructor() {
    this.loadedModules = new Map();
    this.moduleRegistry = new Map();
  }

  /**
   * Register available modules
   */
  registerModules() {
    // Dynamic imports for each module
    this.moduleRegistry.set('student', () => import('@university-erp/student'));
    this.moduleRegistry.set('faculty', () => import('@university-erp/faculty'));
    this.moduleRegistry.set('hr', () => import('@university-erp/hr'));
    this.moduleRegistry.set('accounts', () => import('@university-erp/accounts'));
    this.moduleRegistry.set('admin', () => import('@university-erp/admin'));
    this.moduleRegistry.set('hostel', () => import('@university-erp/hostel'));
    this.moduleRegistry.set('library', () => import('@university-erp/library'));
    this.moduleRegistry.set('placement', () => import('@university-erp/placement'));
  }

  /**
   * Get modules accessible by user based on roles
   */
  getAccessibleModules(userRoles) {
    const accessibleModules = [];

    for (const [moduleId, moduleConfig] of Object.entries(modulesConfig.modules)) {
      // Skip if module is disabled
      if (!moduleConfig.enabled) continue;

      // Check if user has access based on roles
      const hasAccess = userRoles.some(role => {
        const allowedModules = modulesConfig.roleModuleAccess[role] || [];
        return allowedModules.includes(moduleId);
      });

      if (hasAccess) {
        accessibleModules.push({
          id: moduleId,
          config: moduleConfig.config || {}
        });
      }
    }

    return accessibleModules;
  }

  /**
   * Load modules dynamically
   */
  async loadModules(userRoles) {
    const accessibleModules = this.getAccessibleModules(userRoles);
    const loadedModules = [];

    for (const moduleInfo of accessibleModules) {
      try {
        const moduleImport = this.moduleRegistry.get(moduleInfo.id);
        if (moduleImport) {
          const module = await moduleImport();

          // Initialize module with config
          if (module.default.init) {
            await module.default.init(moduleInfo.config);
          }

          loadedModules.push({
            id: moduleInfo.id,
            module: module.default,
            manifest: module.default.manifest,
            routes: module.default.routes,
            store: module.default.store
          });

          this.loadedModules.set(moduleInfo.id, module.default);
        }
      } catch (error) {
        console.error(`Failed to load module: ${moduleInfo.id}`, error);
      }
    }

    return loadedModules;
  }

  /**
   * Get navigation items from loaded modules
   */
  getNavigationItems() {
    const navItems = [];

    for (const [id, module] of this.loadedModules) {
      if (module.manifest.navigation.showInSidebar) {
        navItems.push({
          id,
          label: module.manifest.navigation.label,
          icon: module.manifest.icon,
          position: module.manifest.navigation.position,
          routes: module.manifest.routes
        });
      }
    }

    // Sort by position
    return navItems.sort((a, b) => a.position - b.position);
  }
}

export default new ModuleLoader();
```

### 2. Module Entry Point

```javascript
// @university-erp/student/src/index.js

import manifest from './manifest.json';
import routes from './routes';
import store from './store';

export default {
  manifest,
  routes,
  store,

  /**
   * Initialize module with configuration
   */
  async init(config) {
    // Apply module-specific configuration
    this.config = config;

    // Filter routes based on config
    if (!config.showFees) {
      this.routes = this.routes.filter(r => !r.path.includes('fees'));
    }
    if (!config.showExams) {
      this.routes = this.routes.filter(r => !r.path.includes('exams'));
    }
    // ... etc

    return this;
  },

  /**
   * Cleanup when module is unloaded
   */
  destroy() {
    // Cleanup module resources
  }
};
```

### 3. Dynamic Router

```javascript
// @university-erp/core/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router';
import moduleLoader from '../services/moduleLoader';

// Base routes (always available)
const baseRoutes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('../views/ForgotPassword.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'home',
    redirect: '/dashboard'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes: baseRoutes
});

/**
 * Add routes from loaded modules
 */
export async function initializeRoutes(userRoles) {
  const loadedModules = await moduleLoader.loadModules(userRoles);

  for (const { routes, id } of loadedModules) {
    for (const route of routes) {
      // Add module prefix to route name
      const fullRoute = {
        ...route,
        name: `${id}-${route.name}`,
        meta: {
          ...route.meta,
          module: id,
          requiresAuth: true
        }
      };

      router.addRoute(fullRoute);
    }
  }

  // Add catch-all 404 route
  router.addRoute({
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFound.vue')
  });
}

export default router;
```

---

## Deployment Scenarios

### Scenario 1: Full University Deployment

```javascript
// All modules enabled
modules: {
  student: { enabled: true },
  faculty: { enabled: true },
  hr: { enabled: true },
  accounts: { enabled: true },
  admin: { enabled: true },
  hostel: { enabled: true },
  transport: { enabled: true },
  library: { enabled: true },
  placement: { enabled: true }
}
```

### Scenario 2: Small College (No Hostel/Transport)

```javascript
// Only core modules
modules: {
  student: { enabled: true },
  faculty: { enabled: true },
  hr: { enabled: true },
  accounts: { enabled: true },
  admin: { enabled: true },
  hostel: { enabled: false },
  transport: { enabled: false },
  library: { enabled: true },
  placement: { enabled: false }
}
```

### Scenario 3: HR-Only Deployment (Corporate Training Institute)

```javascript
// Only HR and Accounts
modules: {
  student: { enabled: false },
  faculty: { enabled: false },
  hr: { enabled: true },
  accounts: { enabled: true },
  admin: { enabled: true },
  hostel: { enabled: false },
  transport: { enabled: false },
  library: { enabled: false },
  placement: { enabled: false }
}
```

### Scenario 4: Student Portal Only (Parent Facing)

```javascript
// Only student module with limited features
modules: {
  student: {
    enabled: true,
    config: {
      showFees: true,
      showExams: true,
      showAttendance: true,
      showPlacement: false,
      showLibrary: false,
      showHostel: false
    }
  },
  faculty: { enabled: false },
  hr: { enabled: false },
  accounts: { enabled: false },
  admin: { enabled: false }
}
```

---

## Build & Deployment

### Monorepo Structure with npm Workspaces

```json
// Root package.json
{
  "name": "university-erp-frontend",
  "private": true,
  "workspaces": [
    "packages/*"
  ],
  "scripts": {
    "build": "npm run build --workspaces",
    "build:core": "npm run build -w @university-erp/core",
    "build:student": "npm run build -w @university-erp/student",
    "build:faculty": "npm run build -w @university-erp/faculty",
    "build:hr": "npm run build -w @university-erp/hr",
    "build:accounts": "npm run build -w @university-erp/accounts",
    "dev": "npm run dev -w @university-erp/core"
  }
}
```

### Build Output

```
dist/
├── core/
│   ├── index.html
│   └── assets/
├── modules/
│   ├── student/
│   │   └── student.bundle.js
│   ├── faculty/
│   │   └── faculty.bundle.js
│   ├── hr/
│   │   └── hr.bundle.js
│   └── accounts/
│       └── accounts.bundle.js
└── shared/
    └── shared.bundle.js
```

---

## Summary

The plugin-based architecture provides:

| Feature | Benefit |
|---------|---------|
| **Module Independence** | Each module is a separate package that can be enabled/disabled |
| **Role-Based Loading** | Users only see modules they have access to |
| **Configuration-Driven** | Change `modules.config.js` to enable/disable features |
| **Lazy Loading** | Modules load on-demand, improving initial load time |
| **Independent Updates** | Update one module without affecting others |
| **Multi-Tenant Support** | Different configurations for different institutions |
| **Feature Flags** | Enable/disable specific features within modules |

---

**Next Document**: [02_PROJECT_OVERVIEW.md](./02_PROJECT_OVERVIEW.md) - Project overview for UI/UX team
