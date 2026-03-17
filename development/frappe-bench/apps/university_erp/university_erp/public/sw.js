/**
 * University ERP Service Worker
 * Provides offline support, caching, and push notifications
 */

const CACHE_NAME = 'university-erp-v1';
const OFFLINE_URL = '/offline.html';

// URLs to cache on install
const CACHE_URLS = [
    '/',
    '/app',
    '/offline.html',
    '/assets/university_erp/css/university_erp.css',
    '/assets/university_erp/css/mobile.css',
    '/assets/university_erp/js/university_erp.js',
    '/assets/frappe/css/frappe-web.css',
    '/assets/frappe/js/frappe-web.min.js'
];

// Install event - cache essential resources
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker...');

    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Caching app shell');
                return cache.addAll(CACHE_URLS);
            })
            .then(() => {
                console.log('[SW] Service worker installed');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('[SW] Cache failed:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker...');

    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((name) => name !== CACHE_NAME)
                        .map((name) => {
                            console.log('[SW] Deleting old cache:', name);
                            return caches.delete(name);
                        })
                );
            })
            .then(() => {
                console.log('[SW] Service worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
    const request = event.request;

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Skip API calls and WebSocket connections
    if (request.url.includes('/api/') ||
        request.url.includes('/socket.io/') ||
        request.url.includes('frappe.call')) {
        return;
    }

    event.respondWith(
        caches.match(request)
            .then((cachedResponse) => {
                // Return cached response if available
                if (cachedResponse) {
                    // Fetch in background to update cache
                    fetchAndCache(request);
                    return cachedResponse;
                }

                // Fetch from network
                return fetchAndCache(request);
            })
            .catch(() => {
                // Return offline page for navigation requests
                if (request.mode === 'navigate') {
                    return caches.match(OFFLINE_URL);
                }
                return new Response('Offline', { status: 503 });
            })
    );
});

// Fetch and cache helper
function fetchAndCache(request) {
    return fetch(request)
        .then((response) => {
            // Don't cache non-successful responses
            if (!response || response.status !== 200) {
                return response;
            }

            // Don't cache responses with no-store
            if (response.headers.get('Cache-Control')?.includes('no-store')) {
                return response;
            }

            // Cache the response
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
                .then((cache) => {
                    cache.put(request, responseToCache);
                });

            return response;
        });
}

// Push notification event
self.addEventListener('push', (event) => {
    console.log('[SW] Push notification received');

    let data = {
        title: 'University ERP',
        body: 'You have a new notification',
        icon: '/assets/university_erp/icons/icon-192x192.png',
        badge: '/assets/university_erp/icons/badge-72x72.png',
        tag: 'university-erp-notification',
        data: {}
    };

    if (event.data) {
        try {
            const payload = event.data.json();
            data = {
                ...data,
                ...payload
            };
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body: data.body,
        icon: data.icon,
        badge: data.badge,
        tag: data.tag,
        data: data.data,
        vibrate: [100, 50, 100],
        actions: [
            {
                action: 'view',
                title: 'View'
            },
            {
                action: 'dismiss',
                title: 'Dismiss'
            }
        ],
        requireInteraction: true
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
    console.log('[SW] Notification clicked');

    event.notification.close();

    const action = event.action;
    const notificationData = event.notification.data || {};

    if (action === 'dismiss') {
        return;
    }

    // Determine URL to open
    let url = '/app';
    if (notificationData.url) {
        url = notificationData.url;
    } else if (notificationData.doctype && notificationData.docname) {
        url = `/app/${notificationData.doctype.toLowerCase().replace(/ /g, '-')}/${notificationData.docname}`;
    }

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clientList) => {
                // Check if there's already a window open
                for (const client of clientList) {
                    if (client.url.includes(self.location.origin) && 'focus' in client) {
                        client.navigate(url);
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

// Background sync event
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync:', event.tag);

    if (event.tag === 'sync-pending-actions') {
        event.waitUntil(syncPendingActions());
    }
});

// Sync pending actions when online
async function syncPendingActions() {
    try {
        // Get pending actions from IndexedDB
        const db = await openDatabase();
        const actions = await getPendingActions(db);

        for (const action of actions) {
            try {
                await fetch(action.url, {
                    method: action.method,
                    headers: action.headers,
                    body: action.body
                });
                await deleteAction(db, action.id);
            } catch (error) {
                console.error('[SW] Sync failed for action:', action.id, error);
            }
        }
    } catch (error) {
        console.error('[SW] Background sync failed:', error);
    }
}

// IndexedDB helpers
function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('university-erp-offline', 1);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('pending-actions')) {
                db.createObjectStore('pending-actions', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

function getPendingActions(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['pending-actions'], 'readonly');
        const store = transaction.objectStore('pending-actions');
        const request = store.getAll();

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

function deleteAction(db, id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['pending-actions'], 'readwrite');
        const store = transaction.objectStore('pending-actions');
        const request = store.delete(id);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve();
    });
}

// Periodic background sync (for supported browsers)
self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'check-notifications') {
        event.waitUntil(checkForNotifications());
    }
});

async function checkForNotifications() {
    try {
        const response = await fetch('/api/method/university_erp.university_erp.notification_api.get_unread_count');
        const data = await response.json();

        if (data.message && data.message.count > 0) {
            await self.registration.showNotification('University ERP', {
                body: `You have ${data.message.count} unread notifications`,
                icon: '/assets/university_erp/icons/icon-192x192.png',
                badge: '/assets/university_erp/icons/badge-72x72.png',
                tag: 'unread-notifications'
            });
        }
    } catch (error) {
        console.error('[SW] Notification check failed:', error);
    }
}
