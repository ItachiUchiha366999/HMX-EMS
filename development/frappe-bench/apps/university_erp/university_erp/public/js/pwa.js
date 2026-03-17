/**
 * University ERP PWA Registration and Push Notification Handler
 */

(function() {
    'use strict';

    const UniversityPWA = {
        init: function() {
            this.registerServiceWorker();
            this.setupPushNotifications();
            this.setupInstallPrompt();
        },

        registerServiceWorker: async function() {
            if (!('serviceWorker' in navigator)) {
                console.log('[PWA] Service workers not supported');
                return;
            }

            try {
                // Service worker scope must be under the script's directory
                // unless server sends Service-Worker-Allowed header
                const registration = await navigator.serviceWorker.register('/assets/university_erp/sw.js', {
                    scope: '/assets/university_erp/'
                });

                console.log('[PWA] Service worker registered:', registration.scope);

                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    console.log('[PWA] New service worker installing...');

                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            // New version available
                            this.showUpdateNotification();
                        }
                    });
                });

                // Handle controller change (new SW activated)
                navigator.serviceWorker.addEventListener('controllerchange', () => {
                    console.log('[PWA] Controller changed, reloading...');
                    window.location.reload();
                });

            } catch (error) {
                console.error('[PWA] Service worker registration failed:', error);
            }
        },

        setupPushNotifications: async function() {
            if (!('PushManager' in window)) {
                console.log('[PWA] Push notifications not supported');
                return;
            }

            try {
                const registration = await navigator.serviceWorker.ready;
                const subscription = await registration.pushManager.getSubscription();

                if (subscription) {
                    console.log('[PWA] Already subscribed to push');
                    this.syncSubscription(subscription);
                }
            } catch (error) {
                console.error('[PWA] Push setup failed:', error);
            }
        },

        subscribeToPush: async function() {
            if (!('PushManager' in window)) {
                frappe.msgprint('Push notifications are not supported in this browser');
                return false;
            }

            try {
                const permission = await Notification.requestPermission();
                if (permission !== 'granted') {
                    frappe.msgprint('Notification permission denied');
                    return false;
                }

                const registration = await navigator.serviceWorker.ready;

                // Get VAPID public key from server
                const response = await frappe.call({
                    method: 'university_erp.university_erp.notification_api.get_vapid_key',
                    async: true
                });

                if (!response.message) {
                    console.error('[PWA] VAPID key not configured');
                    return false;
                }

                const subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: this.urlBase64ToUint8Array(response.message)
                });

                // Send subscription to server
                await this.syncSubscription(subscription);

                frappe.show_alert({
                    message: 'Push notifications enabled',
                    indicator: 'green'
                });

                return true;

            } catch (error) {
                console.error('[PWA] Push subscription failed:', error);
                frappe.msgprint('Failed to enable push notifications');
                return false;
            }
        },

        unsubscribeFromPush: async function() {
            try {
                const registration = await navigator.serviceWorker.ready;
                const subscription = await registration.pushManager.getSubscription();

                if (subscription) {
                    await subscription.unsubscribe();

                    // Notify server
                    await frappe.call({
                        method: 'university_erp.university_erp.notification_api.unsubscribe_from_push',
                        args: { device_type: 'web' }
                    });

                    frappe.show_alert({
                        message: 'Push notifications disabled',
                        indicator: 'gray'
                    });
                }

            } catch (error) {
                console.error('[PWA] Unsubscribe failed:', error);
            }
        },

        syncSubscription: async function(subscription) {
            try {
                await frappe.call({
                    method: 'university_erp.university_erp.notification_api.subscribe_to_push',
                    args: {
                        push_token: JSON.stringify(subscription),
                        device_type: 'web'
                    }
                });
            } catch (error) {
                console.error('[PWA] Sync subscription failed:', error);
            }
        },

        setupInstallPrompt: function() {
            let deferredPrompt;

            window.addEventListener('beforeinstallprompt', (e) => {
                e.preventDefault();
                deferredPrompt = e;

                // Show install button
                this.showInstallButton(deferredPrompt);
            });

            window.addEventListener('appinstalled', () => {
                console.log('[PWA] App installed');
                deferredPrompt = null;
                this.hideInstallButton();
            });
        },

        showInstallButton: function(deferredPrompt) {
            // Create install button if not exists
            if (document.getElementById('pwa-install-btn')) return;

            const btn = document.createElement('button');
            btn.id = 'pwa-install-btn';
            btn.className = 'btn btn-primary btn-sm';
            btn.innerHTML = '<i class="fa fa-download"></i> Install App';
            btn.style.cssText = 'position: fixed; bottom: 80px; right: 20px; z-index: 9999;';

            btn.addEventListener('click', async () => {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log('[PWA] Install prompt outcome:', outcome);
                if (outcome === 'accepted') {
                    this.hideInstallButton();
                }
            });

            document.body.appendChild(btn);
        },

        hideInstallButton: function() {
            const btn = document.getElementById('pwa-install-btn');
            if (btn) btn.remove();
        },

        showUpdateNotification: function() {
            frappe.show_alert({
                message: 'A new version is available. <a href="#" onclick="window.location.reload()">Refresh</a> to update.',
                indicator: 'blue'
            }, 10);
        },

        urlBase64ToUint8Array: function(base64String) {
            const padding = '='.repeat((4 - base64String.length % 4) % 4);
            const base64 = (base64String + padding)
                .replace(/-/g, '+')
                .replace(/_/g, '/');

            const rawData = window.atob(base64);
            const outputArray = new Uint8Array(rawData.length);

            for (let i = 0; i < rawData.length; ++i) {
                outputArray[i] = rawData.charCodeAt(i);
            }
            return outputArray;
        },

        // Check if running as PWA
        isPWA: function() {
            return window.matchMedia('(display-mode: standalone)').matches ||
                   window.navigator.standalone === true;
        },

        // Add to home screen prompt
        showAddToHomeScreen: function() {
            if (this.isPWA()) return;

            // Check if already dismissed
            if (localStorage.getItem('pwa-dismissed')) return;

            const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
            const isAndroid = /Android/.test(navigator.userAgent);

            if (isIOS) {
                this.showIOSInstallPrompt();
            } else if (isAndroid && !window.matchMedia('(display-mode: standalone)').matches) {
                // Android install prompt is handled by beforeinstallprompt
            }
        },

        showIOSInstallPrompt: function() {
            const prompt = document.createElement('div');
            prompt.id = 'ios-install-prompt';
            prompt.innerHTML = `
                <div style="position: fixed; bottom: 0; left: 0; right: 0; background: #fff;
                            padding: 20px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); z-index: 9999;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <strong>Install University ERP</strong>
                            <p style="margin: 5px 0 0; font-size: 0.9em; color: #666;">
                                Tap <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 50 50'%3E%3Cpath d='M30.3 13.7L25 8.4l-5.3 5.3-1.4-1.4L25 5.6l6.7 6.7z'/%3E%3Cpath d='M24 7h2v21h-2z'/%3E%3Cpath d='M35 40H15c-1.7 0-3-1.3-3-3V19c0-1.7 1.3-3 3-3h7v2h-7c-.6 0-1 .4-1 1v18c0 .6.4 1 1 1h20c.6 0 1-.4 1-1V19c0-.6-.4-1-1-1h-7v-2h7c1.7 0 3 1.3 3 3v18c0 1.7-1.3 3-3 3z'/%3E%3C/svg%3E"
                                     style="width: 20px; height: 20px; vertical-align: middle;">
                                then "Add to Home Screen"
                            </p>
                        </div>
                        <button onclick="document.getElementById('ios-install-prompt').remove(); localStorage.setItem('pwa-dismissed', '1');"
                                style="background: none; border: none; font-size: 1.5em; cursor: pointer;">×</button>
                    </div>
                </div>
            `;
            document.body.appendChild(prompt);
        }
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => UniversityPWA.init());
    } else {
        UniversityPWA.init();
    }

    // Expose globally
    window.UniversityPWA = UniversityPWA;

})();
