# Phase 21: Custom Vue/React Frontend + PWA

## Overview

This phase implements a **custom frontend** using Vue.js or React (framework choice deferred) with Progressive Web App (PWA) features. The frontend is a **separate multi-page application** that communicates with the Frappe backend via REST API. This replaces the cluttered Frappe Desk UI with a clean, modern interface for regular users while keeping Desk available for system administrators.

**Duration:** 6 Weeks
**Priority:** Medium
**Dependencies:** Phase 13 (Portals), Phase 15 (Notifications)
**Status:** In Progress

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              SEPARATE FRONTEND PROJECT                       │
│              (Vue.js or React + Vite)                        │
├─────────────────────────────────────────────────────────────┤
│  /login          → Login page                               │
│  /dashboard      → Role-based dashboard                     │
│  /academic       → Academic module pages                    │
│  /students       → Student management pages                 │
│  /finance        → Fee & payment pages                      │
│  /hr             → HR & faculty pages                       │
│  /exams          → Examination pages                        │
│  /placement      → Placement pages                          │
│  /analytics      → Reports & dashboards                     │
│                                                              │
│  + PWA Features: Offline, Installable, Push Notifications   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ REST API (fetch/axios)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRAPPE BACKEND                             │
│   • All DocTypes (Phases 1-20)                              │
│   • Unified REST API endpoints                              │
│   • Authentication & Session management                      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              FRAPPE DESK (Admin Only)                        │
│              URL: /app                                       │
│   • System configuration, DocType management                 │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Backend API Layer | In Progress | Unified API endpoints |
| User Device Token DocType | Pending | For push notifications |
| Push Notification Service | Pending | FCM integration |
| Frontend Documentation | Pending | Setup guides |
| Frontend Project | Pending | Separate Vue/React project |

## Gap Analysis Reference

From IMPLEMENTATION_GAP_ANALYSIS.md:
- Mobile Application: 0% (Missing) → Custom Frontend approach
- PWA Enhancement: 20% (Basic service worker) → Full PWA implementation
- Offline Functionality: 0% (Missing) → Service Worker + IndexedDB
- Native App Framework: 0% (Missing) → PWA instead (installable)
- Biometric Authentication: 0% (Missing) → Future consideration
- Mobile Push Notifications: 0% (Missing) → FCM integration

---

## 1. PWA Enhancement

### 1.1 Enhanced Service Worker

```javascript
// university_erp/public/js/pwa/service-worker.js

const CACHE_VERSION = 'v2.0.0';
const STATIC_CACHE = `university-erp-static-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `university-erp-dynamic-${CACHE_VERSION}`;
const API_CACHE = `university-erp-api-${CACHE_VERSION}`;

// Static assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/student-portal',
    '/student-portal/dashboard',
    '/student-portal/attendance',
    '/student-portal/timetable',
    '/student-portal/fees',
    '/assets/university_erp/css/student-portal.css',
    '/assets/university_erp/js/student-portal.bundle.js',
    '/assets/university_erp/images/logo.png',
    '/assets/university_erp/images/icons/icon-192x192.png',
    '/assets/university_erp/images/icons/icon-512x512.png',
    '/offline.html'
];

// API endpoints to cache
const API_ROUTES = [
    '/api/method/university_erp.api.student.get_dashboard_data',
    '/api/method/university_erp.api.student.get_timetable',
    '/api/method/university_erp.api.student.get_attendance_summary'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('[ServiceWorker] Installing...');

    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('[ServiceWorker] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
    console.log('[ServiceWorker] Activating...');

    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => {
                        return name.startsWith('university-erp-') &&
                               name !== STATIC_CACHE &&
                               name !== DYNAMIC_CACHE &&
                               name !== API_CACHE;
                    })
                    .map((name) => {
                        console.log('[ServiceWorker] Deleting old cache:', name);
                        return caches.delete(name);
                    })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache with network fallback
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Handle API requests
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleApiRequest(request));
        return;
    }

    // Handle static assets
    if (isStaticAsset(url.pathname)) {
        event.respondWith(handleStaticRequest(request));
        return;
    }

    // Handle page navigation
    if (request.mode === 'navigate') {
        event.respondWith(handleNavigationRequest(request));
        return;
    }

    // Default: Network first, cache fallback
    event.respondWith(handleDynamicRequest(request));
});

// Handle API requests - Network first, cache fallback
async function handleApiRequest(request) {
    const cache = await caches.open(API_CACHE);

    try {
        const response = await fetch(request);

        if (response.ok) {
            // Clone and cache successful responses
            cache.put(request, response.clone());
        }

        return response;
    } catch (error) {
        console.log('[ServiceWorker] API request failed, trying cache');
        const cachedResponse = await cache.match(request);

        if (cachedResponse) {
            // Add offline indicator to response
            const data = await cachedResponse.json();
            data._offline = true;
            data._cached_at = cachedResponse.headers.get('date');

            return new Response(JSON.stringify(data), {
                headers: { 'Content-Type': 'application/json' }
            });
        }

        throw error;
    }
}

// Handle static requests - Cache first
async function handleStaticRequest(request) {
    const cache = await caches.open(STATIC_CACHE);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
        return cachedResponse;
    }

    try {
        const response = await fetch(request);
        cache.put(request, response.clone());
        return response;
    } catch (error) {
        console.log('[ServiceWorker] Static request failed');
        throw error;
    }
}

// Handle navigation requests
async function handleNavigationRequest(request) {
    try {
        const response = await fetch(request);

        // Cache successful page responses
        if (response.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, response.clone());
        }

        return response;
    } catch (error) {
        console.log('[ServiceWorker] Navigation failed, trying cache');

        // Try to serve cached page
        const cache = await caches.open(DYNAMIC_CACHE);
        const cachedResponse = await cache.match(request);

        if (cachedResponse) {
            return cachedResponse;
        }

        // Serve offline page
        return caches.match('/offline.html');
    }
}

// Handle dynamic requests - Network first
async function handleDynamicRequest(request) {
    const cache = await caches.open(DYNAMIC_CACHE);

    try {
        const response = await fetch(request);
        cache.put(request, response.clone());
        return response;
    } catch (error) {
        const cachedResponse = await cache.match(request);
        return cachedResponse || new Response('Offline', { status: 503 });
    }
}

// Check if URL is a static asset
function isStaticAsset(pathname) {
    return pathname.match(/\.(js|css|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot)$/);
}

// Background sync for offline form submissions
self.addEventListener('sync', (event) => {
    console.log('[ServiceWorker] Sync event:', event.tag);

    if (event.tag === 'sync-forms') {
        event.waitUntil(syncOfflineForms());
    }

    if (event.tag === 'sync-attendance') {
        event.waitUntil(syncAttendanceData());
    }
});

// Sync offline form submissions
async function syncOfflineForms() {
    const db = await openIndexedDB();
    const forms = await getOfflineForms(db);

    for (const form of forms) {
        try {
            const response = await fetch(form.url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(form.data)
            });

            if (response.ok) {
                await deleteOfflineForm(db, form.id);

                // Notify the client
                self.clients.matchAll().then((clients) => {
                    clients.forEach((client) => {
                        client.postMessage({
                            type: 'FORM_SYNCED',
                            formId: form.id
                        });
                    });
                });
            }
        } catch (error) {
            console.error('[ServiceWorker] Form sync failed:', error);
        }
    }
}

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('[ServiceWorker] Push received');

    let data = {};
    if (event.data) {
        data = event.data.json();
    }

    const options = {
        body: data.body || 'New notification from University ERP',
        icon: '/assets/university_erp/images/icons/icon-192x192.png',
        badge: '/assets/university_erp/images/icons/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            url: data.url || '/student-portal/notifications',
            timestamp: Date.now()
        },
        actions: data.actions || [
            { action: 'view', title: 'View' },
            { action: 'dismiss', title: 'Dismiss' }
        ],
        tag: data.tag || 'default',
        renotify: true
    };

    event.waitUntil(
        self.registration.showNotification(data.title || 'University ERP', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('[ServiceWorker] Notification clicked:', event.action);

    event.notification.close();

    if (event.action === 'dismiss') {
        return;
    }

    const url = event.notification.data.url;

    event.waitUntil(
        clients.matchAll({ type: 'window' }).then((windowClients) => {
            // Check if there's already a window open
            for (const client of windowClients) {
                if (client.url === url && 'focus' in client) {
                    return client.focus();
                }
            }

            // Open new window
            if (clients.openWindow) {
                return clients.openWindow(url);
            }
        })
    );
});

// IndexedDB helpers
function openIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('UniversityERPOffline', 1);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;

            if (!db.objectStoreNames.contains('offlineForms')) {
                db.createObjectStore('offlineForms', { keyPath: 'id', autoIncrement: true });
            }

            if (!db.objectStoreNames.contains('offlineAttendance')) {
                db.createObjectStore('offlineAttendance', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

function getOfflineForms(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['offlineForms'], 'readonly');
        const store = transaction.objectStore('offlineForms');
        const request = store.getAll();

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

function deleteOfflineForm(db, id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['offlineForms'], 'readwrite');
        const store = transaction.objectStore('offlineForms');
        const request = store.delete(id);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve();
    });
}
```

### 1.2 Web App Manifest

```json
{
  "name": "University ERP - Student Portal",
  "short_name": "UniERP",
  "description": "Complete university management system for students",
  "start_url": "/student-portal/dashboard",
  "display": "standalone",
  "orientation": "portrait-primary",
  "background_color": "#ffffff",
  "theme_color": "#1a73e8",
  "scope": "/",
  "icons": [
    {
      "src": "/assets/university_erp/images/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/assets/university_erp/images/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/assets/university_erp/images/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/assets/university_erp/images/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/assets/university_erp/images/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/assets/university_erp/images/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/assets/university_erp/images/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/assets/university_erp/images/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable any"
    }
  ],
  "screenshots": [
    {
      "src": "/assets/university_erp/images/screenshots/dashboard.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide",
      "label": "Student Dashboard"
    },
    {
      "src": "/assets/university_erp/images/screenshots/mobile-dashboard.png",
      "sizes": "750x1334",
      "type": "image/png",
      "form_factor": "narrow",
      "label": "Mobile Dashboard"
    }
  ],
  "shortcuts": [
    {
      "name": "View Timetable",
      "short_name": "Timetable",
      "description": "View your class timetable",
      "url": "/student-portal/timetable",
      "icons": [{ "src": "/assets/university_erp/images/icons/timetable.png", "sizes": "96x96" }]
    },
    {
      "name": "Check Attendance",
      "short_name": "Attendance",
      "description": "Check your attendance",
      "url": "/student-portal/attendance",
      "icons": [{ "src": "/assets/university_erp/images/icons/attendance.png", "sizes": "96x96" }]
    },
    {
      "name": "View Results",
      "short_name": "Results",
      "description": "View exam results",
      "url": "/student-portal/results",
      "icons": [{ "src": "/assets/university_erp/images/icons/results.png", "sizes": "96x96" }]
    },
    {
      "name": "Pay Fees",
      "short_name": "Fees",
      "description": "Pay pending fees",
      "url": "/student-portal/fees",
      "icons": [{ "src": "/assets/university_erp/images/icons/fees.png", "sizes": "96x96" }]
    }
  ],
  "categories": ["education", "productivity"],
  "prefer_related_applications": false,
  "related_applications": [
    {
      "platform": "play",
      "url": "https://play.google.com/store/apps/details?id=com.university.erp",
      "id": "com.university.erp"
    },
    {
      "platform": "itunes",
      "url": "https://apps.apple.com/app/university-erp/id123456789"
    }
  ],
  "share_target": {
    "action": "/student-portal/share",
    "method": "POST",
    "enctype": "multipart/form-data",
    "params": {
      "title": "title",
      "text": "text",
      "url": "url",
      "files": [
        {
          "name": "files",
          "accept": ["image/*", "application/pdf"]
        }
      ]
    }
  }
}
```

### 1.3 PWA Installation Manager

```javascript
// university_erp/public/js/pwa/install-manager.js

class PWAInstallManager {
    constructor() {
        this.deferredPrompt = null;
        this.isInstalled = false;
        this.installButton = null;

        this.init();
    }

    init() {
        // Check if already installed
        if (window.matchMedia('(display-mode: standalone)').matches) {
            this.isInstalled = true;
            console.log('PWA is already installed');
            return;
        }

        // Listen for beforeinstallprompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallPromotion();
        });

        // Listen for app installed
        window.addEventListener('appinstalled', () => {
            this.isInstalled = true;
            this.hideInstallPromotion();
            this.trackInstallation();
        });

        // Create install button
        this.createInstallButton();
    }

    createInstallButton() {
        // Create floating install button
        this.installButton = document.createElement('div');
        this.installButton.id = 'pwa-install-prompt';
        this.installButton.className = 'pwa-install-prompt hidden';
        this.installButton.innerHTML = `
            <div class="pwa-install-content">
                <img src="/assets/university_erp/images/icons/icon-72x72.png" alt="App Icon">
                <div class="pwa-install-text">
                    <strong>Install University ERP</strong>
                    <span>Add to home screen for quick access</span>
                </div>
                <div class="pwa-install-actions">
                    <button class="btn btn-primary btn-sm pwa-install-btn">Install</button>
                    <button class="btn btn-link btn-sm pwa-dismiss-btn">Not now</button>
                </div>
            </div>
        `;

        document.body.appendChild(this.installButton);

        // Add event listeners
        this.installButton.querySelector('.pwa-install-btn').addEventListener('click', () => {
            this.promptInstall();
        });

        this.installButton.querySelector('.pwa-dismiss-btn').addEventListener('click', () => {
            this.hideInstallPromotion();
            this.setDismissed();
        });
    }

    showInstallPromotion() {
        // Check if user dismissed recently
        if (this.wasDismissedRecently()) {
            return;
        }

        if (this.installButton) {
            this.installButton.classList.remove('hidden');
            setTimeout(() => {
                this.installButton.classList.add('visible');
            }, 100);
        }
    }

    hideInstallPromotion() {
        if (this.installButton) {
            this.installButton.classList.remove('visible');
            setTimeout(() => {
                this.installButton.classList.add('hidden');
            }, 300);
        }
    }

    async promptInstall() {
        if (!this.deferredPrompt) {
            console.log('No deferred prompt available');
            return;
        }

        // Show the install prompt
        this.deferredPrompt.prompt();

        // Wait for user choice
        const { outcome } = await this.deferredPrompt.userChoice;
        console.log(`User response: ${outcome}`);

        // Clear the deferred prompt
        this.deferredPrompt = null;
        this.hideInstallPromotion();

        // Track the outcome
        this.trackInstallPromptOutcome(outcome);
    }

    wasDismissedRecently() {
        const dismissed = localStorage.getItem('pwa_install_dismissed');
        if (!dismissed) return false;

        const dismissedDate = new Date(parseInt(dismissed));
        const daysSinceDismissed = (Date.now() - dismissedDate) / (1000 * 60 * 60 * 24);

        return daysSinceDismissed < 7; // Don't show for 7 days after dismiss
    }

    setDismissed() {
        localStorage.setItem('pwa_install_dismissed', Date.now().toString());
    }

    trackInstallation() {
        // Track installation analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', 'pwa_installed', {
                'event_category': 'PWA',
                'event_label': 'App Installed'
            });
        }

        // Send to server
        fetch('/api/method/university_erp.api.analytics.track_pwa_install', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event: 'installed' })
        }).catch(console.error);
    }

    trackInstallPromptOutcome(outcome) {
        fetch('/api/method/university_erp.api.analytics.track_pwa_install', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event: 'prompt_outcome', outcome })
        }).catch(console.error);
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.pwaInstallManager = new PWAInstallManager();
});
```

---

## 2. Offline Functionality

### 2.1 Offline Data Manager

```javascript
// university_erp/public/js/pwa/offline-manager.js

class OfflineDataManager {
    constructor() {
        this.dbName = 'UniversityERPOffline';
        this.dbVersion = 2;
        this.db = null;

        this.stores = {
            userData: 'userData',
            timetable: 'timetable',
            attendance: 'attendance',
            notifications: 'notifications',
            assignments: 'assignments',
            pendingSync: 'pendingSync'
        };

        this.init();
    }

    async init() {
        this.db = await this.openDatabase();

        // Listen for online/offline events
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());

        // Initial sync if online
        if (navigator.onLine) {
            this.syncData();
        }
    }

    openDatabase() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create object stores
                Object.values(this.stores).forEach(storeName => {
                    if (!db.objectStoreNames.contains(storeName)) {
                        const store = db.createObjectStore(storeName, {
                            keyPath: 'id',
                            autoIncrement: true
                        });

                        // Add indexes
                        if (storeName === 'timetable') {
                            store.createIndex('date', 'date', { unique: false });
                            store.createIndex('day', 'day', { unique: false });
                        }

                        if (storeName === 'pendingSync') {
                            store.createIndex('type', 'type', { unique: false });
                            store.createIndex('timestamp', 'timestamp', { unique: false });
                        }
                    }
                });
            };
        });
    }

    // Save data to IndexedDB
    async saveData(storeName, data) {
        const transaction = this.db.transaction([storeName], 'readwrite');
        const store = transaction.objectStore(storeName);

        if (Array.isArray(data)) {
            // Clear existing and add new
            await this.clearStore(storeName);
            data.forEach(item => store.add(item));
        } else {
            store.put(data);
        }

        return new Promise((resolve, reject) => {
            transaction.oncomplete = () => resolve();
            transaction.onerror = () => reject(transaction.error);
        });
    }

    // Get data from IndexedDB
    async getData(storeName, key = null) {
        const transaction = this.db.transaction([storeName], 'readonly');
        const store = transaction.objectStore(storeName);

        return new Promise((resolve, reject) => {
            let request;

            if (key) {
                request = store.get(key);
            } else {
                request = store.getAll();
            }

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // Clear a store
    async clearStore(storeName) {
        const transaction = this.db.transaction([storeName], 'readwrite');
        const store = transaction.objectStore(storeName);

        return new Promise((resolve, reject) => {
            const request = store.clear();
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    // Queue action for sync when online
    async queueForSync(type, data, url) {
        await this.saveData(this.stores.pendingSync, {
            type,
            data,
            url,
            timestamp: Date.now()
        });

        // Register for background sync if available
        if ('serviceWorker' in navigator && 'sync' in window.registration) {
            await navigator.serviceWorker.ready;
            await registration.sync.register('sync-forms');
        }
    }

    // Sync cached data with server
    async syncData() {
        console.log('[OfflineManager] Starting data sync...');

        try {
            // Sync pending actions first
            await this.syncPendingActions();

            // Fetch fresh data
            await this.fetchAndCacheData();

            console.log('[OfflineManager] Sync completed');
        } catch (error) {
            console.error('[OfflineManager] Sync failed:', error);
        }
    }

    // Sync pending actions
    async syncPendingActions() {
        const pendingItems = await this.getData(this.stores.pendingSync);

        for (const item of pendingItems) {
            try {
                const response = await fetch(item.url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Frappe-CSRF-Token': frappe.csrf_token
                    },
                    body: JSON.stringify(item.data)
                });

                if (response.ok) {
                    // Remove from pending
                    await this.deleteItem(this.stores.pendingSync, item.id);

                    // Notify UI
                    this.dispatchEvent('sync-success', item);
                }
            } catch (error) {
                console.error('[OfflineManager] Failed to sync item:', error);
            }
        }
    }

    // Fetch and cache essential data
    async fetchAndCacheData() {
        const endpoints = [
            { url: '/api/method/university_erp.api.student.get_profile', store: 'userData' },
            { url: '/api/method/university_erp.api.student.get_timetable', store: 'timetable' },
            { url: '/api/method/university_erp.api.student.get_attendance_summary', store: 'attendance' }
        ];

        for (const endpoint of endpoints) {
            try {
                const response = await fetch(endpoint.url);
                if (response.ok) {
                    const data = await response.json();
                    await this.saveData(endpoint.store, data.message);
                }
            } catch (error) {
                console.log(`[OfflineManager] Could not fetch ${endpoint.store}`);
            }
        }
    }

    // Delete item from store
    async deleteItem(storeName, id) {
        const transaction = this.db.transaction([storeName], 'readwrite');
        const store = transaction.objectStore(storeName);

        return new Promise((resolve, reject) => {
            const request = store.delete(id);
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    // Handle going online
    handleOnline() {
        console.log('[OfflineManager] Online - starting sync');
        this.dispatchEvent('online');
        this.syncData();
    }

    // Handle going offline
    handleOffline() {
        console.log('[OfflineManager] Offline');
        this.dispatchEvent('offline');
        this.showOfflineNotification();
    }

    // Show offline notification
    showOfflineNotification() {
        const notification = document.createElement('div');
        notification.className = 'offline-notification';
        notification.innerHTML = `
            <i class="fa fa-wifi-slash"></i>
            <span>You're offline. Some features may be limited.</span>
        `;
        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add('visible'), 100);

        // Remove when back online
        const removeNotification = () => {
            notification.classList.remove('visible');
            setTimeout(() => notification.remove(), 300);
            window.removeEventListener('online', removeNotification);
        };

        window.addEventListener('online', removeNotification);
    }

    // Dispatch custom events
    dispatchEvent(eventName, detail = null) {
        window.dispatchEvent(new CustomEvent(`offline-manager:${eventName}`, { detail }));
    }

    // Get offline status
    isOffline() {
        return !navigator.onLine;
    }
}

// Initialize
window.offlineManager = new OfflineDataManager();
```

---

## 3. Native Mobile App Framework

### 3.1 React Native App Structure

```javascript
// mobile-app/src/App.js

import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import messaging from '@react-native-firebase/messaging';
import { store, persistor } from './store';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Screens
import LoginScreen from './screens/LoginScreen';
import DashboardScreen from './screens/DashboardScreen';
import TimetableScreen from './screens/TimetableScreen';
import AttendanceScreen from './screens/AttendanceScreen';
import ResultsScreen from './screens/ResultsScreen';
import ProfileScreen from './screens/ProfileScreen';
import NotificationsScreen from './screens/NotificationsScreen';
import FeesScreen from './screens/FeesScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Tab Navigator
function MainTabs() {
    return (
        <Tab.Navigator
            screenOptions={({ route }) => ({
                tabBarIcon: ({ focused, color, size }) => {
                    let iconName;

                    switch (route.name) {
                        case 'Dashboard':
                            iconName = 'view-dashboard';
                            break;
                        case 'Timetable':
                            iconName = 'calendar-clock';
                            break;
                        case 'Attendance':
                            iconName = 'clipboard-check';
                            break;
                        case 'Results':
                            iconName = 'chart-line';
                            break;
                        case 'Profile':
                            iconName = 'account';
                            break;
                    }

                    return <Icon name={iconName} size={size} color={color} />;
                },
                tabBarActiveTintColor: '#1a73e8',
                tabBarInactiveTintColor: 'gray',
            })}
        >
            <Tab.Screen name="Dashboard" component={DashboardScreen} />
            <Tab.Screen name="Timetable" component={TimetableScreen} />
            <Tab.Screen name="Attendance" component={AttendanceScreen} />
            <Tab.Screen name="Results" component={ResultsScreen} />
            <Tab.Screen name="Profile" component={ProfileScreen} />
        </Tab.Navigator>
    );
}

// Auth Stack
function AuthStack() {
    return (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
            <Stack.Screen name="Login" component={LoginScreen} />
        </Stack.Navigator>
    );
}

// Main Stack
function MainStack() {
    return (
        <Stack.Navigator>
            <Stack.Screen
                name="Main"
                component={MainTabs}
                options={{ headerShown: false }}
            />
            <Stack.Screen
                name="Notifications"
                component={NotificationsScreen}
                options={{ title: 'Notifications' }}
            />
            <Stack.Screen
                name="Fees"
                component={FeesScreen}
                options={{ title: 'Fee Payment' }}
            />
        </Stack.Navigator>
    );
}

// Root Navigator
function RootNavigator() {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return <SplashScreen />;
    }

    return isAuthenticated ? <MainStack /> : <AuthStack />;
}

// Main App Component
export default function App() {
    const [fcmToken, setFcmToken] = useState(null);

    useEffect(() => {
        // Request FCM permission
        requestFCMPermission();

        // Handle foreground messages
        const unsubscribe = messaging().onMessage(async remoteMessage => {
            console.log('FCM Message:', remoteMessage);
            // Show in-app notification
        });

        return unsubscribe;
    }, []);

    async function requestFCMPermission() {
        const authStatus = await messaging().requestPermission();
        const enabled =
            authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
            authStatus === messaging.AuthorizationStatus.PROVISIONAL;

        if (enabled) {
            const token = await messaging().getToken();
            setFcmToken(token);
            // Send token to server
        }
    }

    return (
        <Provider store={store}>
            <PersistGate loading={null} persistor={persistor}>
                <AuthProvider>
                    <NavigationContainer>
                        <RootNavigator />
                    </NavigationContainer>
                </AuthProvider>
            </PersistGate>
        </Provider>
    );
}
```

### 3.2 API Service

```javascript
// mobile-app/src/services/api.js

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

const API_BASE_URL = 'https://university.example.com';

class APIService {
    constructor() {
        this.client = axios.create({
            baseURL: API_BASE_URL,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Request interceptor
        this.client.interceptors.request.use(
            async (config) => {
                const token = await AsyncStorage.getItem('auth_token');
                if (token) {
                    config.headers.Authorization = `token ${token}`;
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        // Response interceptor
        this.client.interceptors.response.use(
            (response) => response,
            async (error) => {
                if (error.response?.status === 401) {
                    await this.handleUnauthorized();
                }
                return Promise.reject(error);
            }
        );
    }

    async handleUnauthorized() {
        await AsyncStorage.removeItem('auth_token');
        // Redirect to login
    }

    // Check network status
    async isOnline() {
        const state = await NetInfo.fetch();
        return state.isConnected;
    }

    // Generic API call with offline support
    async request(method, endpoint, data = null, options = {}) {
        const online = await this.isOnline();

        if (!online && options.offlineCache) {
            // Return cached data
            const cached = await AsyncStorage.getItem(`cache_${endpoint}`);
            if (cached) {
                return JSON.parse(cached);
            }
            throw new Error('No network connection and no cached data');
        }

        try {
            const response = await this.client.request({
                method,
                url: endpoint,
                data,
            });

            // Cache successful GET responses
            if (method === 'GET' && options.cache) {
                await AsyncStorage.setItem(
                    `cache_${endpoint}`,
                    JSON.stringify(response.data)
                );
            }

            return response.data;
        } catch (error) {
            // Queue for later if offline
            if (!online && options.queueOffline) {
                await this.queueRequest(method, endpoint, data);
                return { queued: true };
            }
            throw error;
        }
    }

    // Queue request for later sync
    async queueRequest(method, endpoint, data) {
        const queue = JSON.parse(await AsyncStorage.getItem('request_queue') || '[]');
        queue.push({
            method,
            endpoint,
            data,
            timestamp: Date.now(),
        });
        await AsyncStorage.setItem('request_queue', JSON.stringify(queue));
    }

    // Sync queued requests
    async syncQueue() {
        const queue = JSON.parse(await AsyncStorage.getItem('request_queue') || '[]');

        for (const item of queue) {
            try {
                await this.client.request({
                    method: item.method,
                    url: item.endpoint,
                    data: item.data,
                });
            } catch (error) {
                console.error('Sync failed for:', item.endpoint);
            }
        }

        await AsyncStorage.removeItem('request_queue');
    }

    // Authentication
    async login(email, password) {
        const response = await this.client.post('/api/method/frappe.auth.get_logged_user', {
            usr: email,
            pwd: password,
        });

        if (response.data.message) {
            await AsyncStorage.setItem('auth_token', response.data.message);
        }

        return response.data;
    }

    async logout() {
        await this.client.get('/api/method/frappe.auth.logout');
        await AsyncStorage.removeItem('auth_token');
    }

    // Student API endpoints
    async getDashboard() {
        return this.request('GET', '/api/method/university_erp.api.student.get_dashboard_data', null, {
            cache: true,
            offlineCache: true,
        });
    }

    async getTimetable(date = null) {
        return this.request('GET', '/api/method/university_erp.api.student.get_timetable', { date }, {
            cache: true,
            offlineCache: true,
        });
    }

    async getAttendance() {
        return this.request('GET', '/api/method/university_erp.api.student.get_attendance_summary', null, {
            cache: true,
            offlineCache: true,
        });
    }

    async getResults() {
        return this.request('GET', '/api/method/university_erp.api.student.get_results', null, {
            cache: true,
        });
    }

    async getFees() {
        return this.request('GET', '/api/method/university_erp.api.student.get_pending_fees');
    }

    async getNotifications() {
        return this.request('GET', '/api/method/university_erp.api.student.get_notifications', null, {
            cache: true,
        });
    }

    async markNotificationRead(notificationId) {
        return this.request('POST', '/api/method/university_erp.api.student.mark_notification_read', {
            notification_id: notificationId,
        }, {
            queueOffline: true,
        });
    }

    async submitFeedback(feedbackId, answers) {
        return this.request('POST', '/api/method/university_erp.api.feedback.submit_response', {
            feedback_form: feedbackId,
            answers,
        }, {
            queueOffline: true,
        });
    }

    // Register device for push notifications
    async registerDevice(token, platform) {
        return this.request('POST', '/api/method/university_erp.api.notifications.register_device', {
            token,
            platform,
        });
    }
}

export default new APIService();
```

### 3.3 Biometric Authentication

```javascript
// mobile-app/src/services/biometric.js

import ReactNativeBiometrics, { BiometryTypes } from 'react-native-biometrics';
import AsyncStorage from '@react-native-async-storage/async-storage';

const rnBiometrics = new ReactNativeBiometrics();

class BiometricService {
    constructor() {
        this.isAvailable = false;
        this.biometryType = null;
    }

    async checkAvailability() {
        try {
            const { available, biometryType } = await rnBiometrics.isSensorAvailable();
            this.isAvailable = available;
            this.biometryType = biometryType;

            return {
                available,
                type: biometryType,
                typeName: this.getBiometryTypeName(biometryType),
            };
        } catch (error) {
            console.error('Biometric check failed:', error);
            return { available: false };
        }
    }

    getBiometryTypeName(type) {
        switch (type) {
            case BiometryTypes.FaceID:
                return 'Face ID';
            case BiometryTypes.TouchID:
                return 'Touch ID';
            case BiometryTypes.Biometrics:
                return 'Biometrics';
            default:
                return 'Unknown';
        }
    }

    async enableBiometric(userId) {
        if (!this.isAvailable) {
            throw new Error('Biometric authentication not available');
        }

        try {
            // Generate keys
            const { publicKey } = await rnBiometrics.createKeys();

            // Store public key on server for verification
            await this.registerPublicKey(userId, publicKey);

            // Mark biometric as enabled
            await AsyncStorage.setItem('biometric_enabled', 'true');
            await AsyncStorage.setItem('biometric_user', userId);

            return true;
        } catch (error) {
            console.error('Enable biometric failed:', error);
            throw error;
        }
    }

    async disableBiometric() {
        try {
            await rnBiometrics.deleteKeys();
            await AsyncStorage.removeItem('biometric_enabled');
            await AsyncStorage.removeItem('biometric_user');
            return true;
        } catch (error) {
            console.error('Disable biometric failed:', error);
            throw error;
        }
    }

    async isBiometricEnabled() {
        const enabled = await AsyncStorage.getItem('biometric_enabled');
        return enabled === 'true';
    }

    async authenticateWithBiometric(promptMessage = 'Authenticate to continue') {
        if (!this.isAvailable) {
            throw new Error('Biometric authentication not available');
        }

        const enabled = await this.isBiometricEnabled();
        if (!enabled) {
            throw new Error('Biometric authentication not enabled');
        }

        try {
            const { success, signature } = await rnBiometrics.createSignature({
                promptMessage,
                payload: `${Date.now()}`,
            });

            if (success) {
                // Verify signature on server
                const userId = await AsyncStorage.getItem('biometric_user');
                const verified = await this.verifySignature(userId, signature);

                if (verified) {
                    return { success: true, userId };
                }
            }

            return { success: false };
        } catch (error) {
            console.error('Biometric auth failed:', error);
            throw error;
        }
    }

    async simplePrompt(promptMessage = 'Confirm your identity') {
        try {
            const { success } = await rnBiometrics.simplePrompt({
                promptMessage,
            });
            return success;
        } catch (error) {
            console.error('Simple prompt failed:', error);
            return false;
        }
    }

    async registerPublicKey(userId, publicKey) {
        // Call server API to register public key
        const response = await fetch('/api/method/university_erp.api.auth.register_biometric', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, public_key: publicKey }),
        });

        return response.ok;
    }

    async verifySignature(userId, signature) {
        // Call server API to verify signature
        const response = await fetch('/api/method/university_erp.api.auth.verify_biometric', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, signature }),
        });

        return response.ok;
    }
}

export default new BiometricService();
```

---

## 4. Mobile Push Notifications

### 4.1 Push Notification Service

```python
# university_erp/university_erp/mobile/push_notifications.py

import frappe
from frappe import _
import firebase_admin
from firebase_admin import credentials, messaging
import json

class MobilePushService:
    """
    Mobile push notification service using Firebase Cloud Messaging
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not MobilePushService._initialized:
            self._initialize_firebase()
            MobilePushService._initialized = True

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Get credentials from settings
            cred_path = frappe.db.get_single_value(
                "Push Notification Settings",
                "firebase_credentials_path"
            )

            if cred_path:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
        except Exception as e:
            frappe.log_error(f"Firebase initialization failed: {e}", "Push Notifications")

    def send_to_device(self, token: str, title: str, body: str,
                      data: dict = None, image: str = None) -> bool:
        """
        Send notification to a single device

        Args:
            token: FCM device token
            title: Notification title
            body: Notification body
            data: Additional data payload
            image: Image URL for rich notification
        """
        try:
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image
            )

            android_config = messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='notification_icon',
                    color='#1a73e8',
                    sound='default',
                    click_action='OPEN_APP'
                )
            )

            apns_config = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        badge=1,
                        sound='default',
                        mutable_content=True
                    )
                )
            )

            message = messaging.Message(
                notification=notification,
                data=data or {},
                token=token,
                android=android_config,
                apns=apns_config
            )

            response = messaging.send(message)
            return True

        except Exception as e:
            frappe.log_error(f"Push notification failed: {e}", "Push Notifications")
            return False

    def send_to_topic(self, topic: str, title: str, body: str,
                     data: dict = None) -> bool:
        """
        Send notification to a topic (group of devices)
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                topic=topic
            )

            response = messaging.send(message)
            return True

        except Exception as e:
            frappe.log_error(f"Topic notification failed: {e}", "Push Notifications")
            return False

    def send_to_multiple_devices(self, tokens: list, title: str, body: str,
                                data: dict = None) -> dict:
        """
        Send notification to multiple devices
        """
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )

            response = messaging.send_multicast(message)

            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": [
                    {"success": r.success, "message_id": r.message_id if r.success else None}
                    for r in response.responses
                ]
            }

        except Exception as e:
            frappe.log_error(f"Multicast notification failed: {e}", "Push Notifications")
            return {"success_count": 0, "failure_count": len(tokens)}

    def subscribe_to_topic(self, tokens: list, topic: str) -> bool:
        """Subscribe devices to a topic"""
        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            return response.success_count > 0
        except Exception as e:
            frappe.log_error(f"Topic subscription failed: {e}", "Push Notifications")
            return False

    def unsubscribe_from_topic(self, tokens: list, topic: str) -> bool:
        """Unsubscribe devices from a topic"""
        try:
            response = messaging.unsubscribe_from_topic(tokens, topic)
            return response.success_count > 0
        except Exception as e:
            frappe.log_error(f"Topic unsubscription failed: {e}", "Push Notifications")
            return False


# API Endpoints

@frappe.whitelist()
def register_device(token: str, platform: str):
    """
    Register device for push notifications

    Args:
        token: FCM device token
        platform: 'android' or 'ios'
    """
    user = frappe.session.user

    # Check if token already exists
    existing = frappe.db.get_value("User Device Token", {
        "user": user,
        "token": token
    })

    if existing:
        # Update last seen
        frappe.db.set_value("User Device Token", existing, "last_seen", frappe.utils.now())
        return {"status": "updated"}

    # Create new token record
    doc = frappe.get_doc({
        "doctype": "User Device Token",
        "user": user,
        "token": token,
        "platform": platform,
        "is_active": 1
    })
    doc.insert(ignore_permissions=True)

    # Subscribe to user's topics
    push_service = MobilePushService()

    # Subscribe to general topic
    push_service.subscribe_to_topic([token], "all_users")

    # Subscribe to role-based topics
    roles = frappe.get_roles(user)
    for role in roles:
        topic = role.lower().replace(" ", "_")
        push_service.subscribe_to_topic([token], topic)

    # Subscribe to department topic if applicable
    student = frappe.db.get_value("Student", {"user": user}, "department")
    if student:
        push_service.subscribe_to_topic([token], f"dept_{student}")

    return {"status": "registered"}


@frappe.whitelist()
def unregister_device(token: str):
    """Unregister device from push notifications"""
    user = frappe.session.user

    frappe.db.set_value("User Device Token", {
        "user": user,
        "token": token
    }, "is_active", 0)

    return {"status": "unregistered"}


def send_notification_to_user(user: str, title: str, body: str,
                             data: dict = None, notification_type: str = None):
    """
    Send push notification to a user's devices

    Args:
        user: User ID
        title: Notification title
        body: Notification body
        data: Additional data
        notification_type: Type for categorization
    """
    # Get user's active device tokens
    tokens = frappe.get_all("User Device Token",
        filters={"user": user, "is_active": 1},
        pluck="token"
    )

    if not tokens:
        return

    push_service = MobilePushService()

    # Add notification type to data
    if data is None:
        data = {}
    if notification_type:
        data["type"] = notification_type

    # Send to all devices
    push_service.send_to_multiple_devices(tokens, title, body, data)


def send_bulk_notification(users: list, title: str, body: str,
                          data: dict = None):
    """Send notification to multiple users"""
    all_tokens = []

    for user in users:
        tokens = frappe.get_all("User Device Token",
            filters={"user": user, "is_active": 1},
            pluck="token"
        )
        all_tokens.extend(tokens)

    if not all_tokens:
        return

    push_service = MobilePushService()

    # Send in batches of 500 (FCM limit)
    batch_size = 500
    for i in range(0, len(all_tokens), batch_size):
        batch = all_tokens[i:i + batch_size]
        push_service.send_to_multiple_devices(batch, title, body, data)
```

---

## 5. Mobile-Optimized Components

### 5.1 Mobile Dashboard Component

```javascript
// mobile-app/src/screens/DashboardScreen.js

import React, { useEffect, useState, useCallback } from 'react';
import {
    View,
    ScrollView,
    RefreshControl,
    StyleSheet,
    Dimensions,
} from 'react-native';
import { Card, Text, Avatar, Badge, ProgressBar } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import api from '../services/api';
import { useOffline } from '../hooks/useOffline';

const { width } = Dimensions.get('window');

export default function DashboardScreen() {
    const navigation = useNavigation();
    const { isOffline, cachedData, saveToCache } = useOffline('dashboard');

    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [data, setData] = useState(cachedData);

    useEffect(() => {
        loadDashboard();
    }, []);

    const loadDashboard = async () => {
        try {
            const response = await api.getDashboard();
            setData(response.message);
            saveToCache(response.message);
        } catch (error) {
            console.error('Dashboard load failed:', error);
            // Use cached data if available
            if (cachedData) {
                setData(cachedData);
            }
        } finally {
            setLoading(false);
        }
    };

    const onRefresh = useCallback(async () => {
        setRefreshing(true);
        await loadDashboard();
        setRefreshing(false);
    }, []);

    if (loading && !data) {
        return <LoadingScreen />;
    }

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }
        >
            {isOffline && <OfflineBanner />}

            {/* Profile Summary */}
            <ProfileCard profile={data?.profile} />

            {/* Quick Stats */}
            <View style={styles.statsRow}>
                <StatCard
                    icon="clipboard-check"
                    label="Attendance"
                    value={`${data?.attendance?.percentage || 0}%`}
                    color="#4caf50"
                    onPress={() => navigation.navigate('Attendance')}
                />
                <StatCard
                    icon="chart-line"
                    label="CGPA"
                    value={data?.cgpa?.toFixed(2) || '0.00'}
                    color="#2196f3"
                    onPress={() => navigation.navigate('Results')}
                />
            </View>

            {/* Today's Schedule */}
            <Card style={styles.card}>
                <Card.Title
                    title="Today's Classes"
                    left={(props) => <Icon name="calendar-today" size={24} color="#1a73e8" />}
                    right={() => (
                        <Text
                            style={styles.viewAll}
                            onPress={() => navigation.navigate('Timetable')}
                        >
                            View All
                        </Text>
                    )}
                />
                <Card.Content>
                    {data?.today_classes?.length > 0 ? (
                        data.today_classes.map((cls, index) => (
                            <ClassItem key={index} classData={cls} />
                        ))
                    ) : (
                        <Text style={styles.emptyText}>No classes today</Text>
                    )}
                </Card.Content>
            </Card>

            {/* Pending Fees */}
            {data?.pending_fees > 0 && (
                <Card style={[styles.card, styles.feeCard]}>
                    <Card.Content>
                        <View style={styles.feeRow}>
                            <View>
                                <Text style={styles.feeLabel}>Pending Fees</Text>
                                <Text style={styles.feeAmount}>
                                    ₹{data.pending_fees.toLocaleString()}
                                </Text>
                            </View>
                            <Button
                                mode="contained"
                                onPress={() => navigation.navigate('Fees')}
                            >
                                Pay Now
                            </Button>
                        </View>
                    </Card.Content>
                </Card>
            )}

            {/* Recent Notifications */}
            <Card style={styles.card}>
                <Card.Title
                    title="Notifications"
                    left={(props) => <Icon name="bell" size={24} color="#ff9800" />}
                    right={() => (
                        <Badge visible={data?.unread_notifications > 0}>
                            {data?.unread_notifications}
                        </Badge>
                    )}
                />
                <Card.Content>
                    {data?.notifications?.slice(0, 3).map((notif, index) => (
                        <NotificationItem key={index} notification={notif} />
                    ))}
                </Card.Content>
            </Card>

            {/* Quick Actions */}
            <View style={styles.quickActions}>
                <QuickActionButton
                    icon="file-document"
                    label="Assignments"
                    onPress={() => navigation.navigate('Assignments')}
                />
                <QuickActionButton
                    icon="book-open"
                    label="Library"
                    onPress={() => navigation.navigate('Library')}
                />
                <QuickActionButton
                    icon="certificate"
                    label="Certificates"
                    onPress={() => navigation.navigate('Certificates')}
                />
                <QuickActionButton
                    icon="help-circle"
                    label="Support"
                    onPress={() => navigation.navigate('Support')}
                />
            </View>
        </ScrollView>
    );
}

// Sub-components
const ProfileCard = ({ profile }) => (
    <Card style={styles.profileCard}>
        <Card.Content style={styles.profileContent}>
            <Avatar.Image
                size={60}
                source={{ uri: profile?.image || 'https://via.placeholder.com/60' }}
            />
            <View style={styles.profileInfo}>
                <Text style={styles.profileName}>{profile?.student_name}</Text>
                <Text style={styles.profileDetails}>
                    {profile?.program} | {profile?.roll_number}
                </Text>
                <Text style={styles.profileSemester}>
                    Semester {profile?.current_semester}
                </Text>
            </View>
        </Card.Content>
    </Card>
);

const StatCard = ({ icon, label, value, color, onPress }) => (
    <Card style={styles.statCard} onPress={onPress}>
        <Card.Content style={styles.statContent}>
            <Icon name={icon} size={28} color={color} />
            <Text style={[styles.statValue, { color }]}>{value}</Text>
            <Text style={styles.statLabel}>{label}</Text>
        </Card.Content>
    </Card>
);

const ClassItem = ({ classData }) => (
    <View style={styles.classItem}>
        <View style={styles.classTime}>
            <Text style={styles.timeText}>{classData.start_time}</Text>
            <Text style={styles.timeSeparator}>-</Text>
            <Text style={styles.timeText}>{classData.end_time}</Text>
        </View>
        <View style={styles.classInfo}>
            <Text style={styles.className}>{classData.course_name}</Text>
            <Text style={styles.classDetails}>
                {classData.instructor} • {classData.room}
            </Text>
        </View>
    </View>
);

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    card: {
        margin: 16,
        marginBottom: 8,
        borderRadius: 12,
    },
    profileCard: {
        margin: 16,
        borderRadius: 12,
        backgroundColor: '#1a73e8',
    },
    profileContent: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    profileInfo: {
        marginLeft: 16,
    },
    profileName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#fff',
    },
    profileDetails: {
        fontSize: 14,
        color: 'rgba(255,255,255,0.8)',
    },
    profileSemester: {
        fontSize: 12,
        color: 'rgba(255,255,255,0.7)',
        marginTop: 4,
    },
    statsRow: {
        flexDirection: 'row',
        paddingHorizontal: 12,
    },
    statCard: {
        flex: 1,
        marginHorizontal: 4,
        borderRadius: 12,
    },
    statContent: {
        alignItems: 'center',
        paddingVertical: 16,
    },
    statValue: {
        fontSize: 24,
        fontWeight: 'bold',
        marginTop: 8,
    },
    statLabel: {
        fontSize: 12,
        color: '#666',
    },
    classItem: {
        flexDirection: 'row',
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
    },
    classTime: {
        width: 70,
        alignItems: 'center',
    },
    timeText: {
        fontSize: 12,
        color: '#666',
    },
    classInfo: {
        flex: 1,
        marginLeft: 16,
    },
    className: {
        fontSize: 14,
        fontWeight: '600',
    },
    classDetails: {
        fontSize: 12,
        color: '#666',
        marginTop: 2,
    },
    quickActions: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        padding: 16,
    },
    viewAll: {
        color: '#1a73e8',
        marginRight: 16,
    },
    feeCard: {
        backgroundColor: '#fff3e0',
    },
    feeRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    feeLabel: {
        fontSize: 14,
        color: '#666',
    },
    feeAmount: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#f57c00',
    },
    emptyText: {
        textAlign: 'center',
        color: '#999',
        paddingVertical: 16,
    },
});
```

---

## 6. Implementation Checklist

### Week 1: PWA Enhancement
- [ ] Implement enhanced service worker
- [ ] Add offline page support
- [ ] Create web app manifest
- [ ] Implement install promotion
- [ ] Add background sync
- [ ] Create PWA analytics

### Week 2: Offline Functionality
- [ ] Implement IndexedDB storage
- [ ] Create offline data manager
- [ ] Add request queuing
- [ ] Build sync mechanism
- [ ] Add offline indicators
- [ ] Test offline scenarios

### Week 3: Mobile App Setup
- [ ] Set up React Native project
- [ ] Configure navigation
- [ ] Implement API service
- [ ] Add state management
- [ ] Create auth flow
- [ ] Set up biometric auth

### Week 4: Mobile Screens
- [ ] Build Dashboard screen
- [ ] Create Timetable screen
- [ ] Build Attendance screen
- [ ] Create Results screen
- [ ] Build Profile screen
- [ ] Add Notifications screen

### Week 5: Push Notifications
- [ ] Set up Firebase Cloud Messaging
- [ ] Create push notification service
- [ ] Implement device registration
- [ ] Add topic subscriptions
- [ ] Build notification handlers
- [ ] Test notification delivery

### Week 6: Testing & Deployment
- [ ] Test PWA installation
- [ ] Test offline functionality
- [ ] Test push notifications
- [ ] Performance optimization
- [ ] App store preparation
- [ ] Documentation

---

## 7. Platform Support Matrix

| Feature | PWA | Android | iOS |
|---------|-----|---------|-----|
| Offline Access | ✅ | ✅ | ✅ |
| Push Notifications | ✅ | ✅ | ✅ |
| Biometric Auth | ❌ | ✅ | ✅ |
| Camera Access | ✅ | ✅ | ✅ |
| File Upload | ✅ | ✅ | ✅ |
| Background Sync | ✅ | ✅ | ⚠️ |
| Home Screen Install | ✅ | ✅ | ⚠️ |
| App Store Distribution | ❌ | ✅ | ✅ |
