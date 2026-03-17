/**
 * University ERP Portal Utilities
 * Mobile-friendly utilities for all portals
 */

// MobilePortal class for handling mobile-specific features
class MobilePortal {
    constructor() {
        this.isTouch = 'ontouchstart' in window;
        this.pullToRefresh = null;
        this.longPressTimer = null;
    }

    static init() {
        const portal = new MobilePortal();
        portal.initPullToRefresh();
        portal.initSwipeNavigation();
        portal.initLongPress();
        portal.registerServiceWorker();
        return portal;
    }

    // Pull to Refresh
    initPullToRefresh() {
        if (!this.isTouch) return;

        let startY = 0;
        let pulling = false;

        const container = document.querySelector('.portal-container');
        if (!container) return;

        container.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].pageY;
                pulling = true;
            }
        });

        container.addEventListener('touchmove', (e) => {
            if (!pulling) return;

            const currentY = e.touches[0].pageY;
            const pullDistance = currentY - startY;

            if (pullDistance > 50 && window.scrollY === 0) {
                container.classList.add('pulling');
            }
        });

        container.addEventListener('touchend', (e) => {
            if (container.classList.contains('pulling')) {
                container.classList.remove('pulling');
                container.classList.add('refreshing');

                // Trigger refresh
                setTimeout(() => {
                    location.reload();
                }, 500);
            }
            pulling = false;
        });
    }

    // Swipe Navigation
    initSwipeNavigation() {
        if (!this.isTouch) return;

        let startX = 0;
        let startY = 0;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;

            const diffX = startX - endX;
            const diffY = startY - endY;

            // Check if horizontal swipe is greater than vertical
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 100) {
                if (diffX > 0) {
                    // Swipe left - can be used for navigation
                    this.onSwipeLeft();
                } else {
                    // Swipe right - go back
                    this.onSwipeRight();
                }
            }
        });
    }

    onSwipeLeft() {
        // Override in specific portals if needed
    }

    onSwipeRight() {
        // Go back on swipe right
        if (window.history.length > 1) {
            const backLink = document.querySelector('.back-link');
            if (backLink) {
                window.location.href = backLink.href;
            }
        }
    }

    // Long Press Handler
    initLongPress() {
        const longPressItems = document.querySelectorAll('[data-long-press]');

        longPressItems.forEach(item => {
            item.addEventListener('touchstart', (e) => {
                this.longPressTimer = setTimeout(() => {
                    const action = item.dataset.longPress;
                    this.handleLongPress(item, action);
                }, 500);
            });

            item.addEventListener('touchend', () => {
                clearTimeout(this.longPressTimer);
            });

            item.addEventListener('touchmove', () => {
                clearTimeout(this.longPressTimer);
            });
        });
    }

    handleLongPress(element, action) {
        // Trigger haptic feedback if available
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }

        // Show context menu or perform action
        const event = new CustomEvent('longpress', {
            detail: { element, action }
        });
        document.dispatchEvent(event);
    }

    // Service Worker Registration
    registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/assets/university_erp/js/sw.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration.scope);
                })
                .catch(error => {
                    console.log('Service Worker registration failed:', error);
                });
        }
    }
}

// Bottom Sheet Modal
class BottomSheet {
    constructor(options = {}) {
        this.title = options.title || '';
        this.content = options.content || '';
        this.actions = options.actions || [];
        this.sheet = null;
    }

    show() {
        this.sheet = document.createElement('div');
        this.sheet.className = 'bottom-sheet';
        this.sheet.innerHTML = `
            <div class="bottom-sheet-overlay"></div>
            <div class="bottom-sheet-content">
                <div class="bottom-sheet-handle"></div>
                ${this.title ? `<div class="bottom-sheet-title">${this.title}</div>` : ''}
                <div class="bottom-sheet-body">${this.content}</div>
                ${this.actions.length > 0 ? `
                    <div class="bottom-sheet-actions">
                        ${this.actions.map(action => `
                            <button class="btn ${action.class || 'btn-default'}" data-action="${action.id}">
                                ${action.label}
                            </button>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;

        document.body.appendChild(this.sheet);

        // Animate in
        requestAnimationFrame(() => {
            this.sheet.classList.add('active');
        });

        // Bind events
        this.sheet.querySelector('.bottom-sheet-overlay').addEventListener('click', () => this.hide());

        this.actions.forEach(action => {
            const btn = this.sheet.querySelector(`[data-action="${action.id}"]`);
            if (btn && action.handler) {
                btn.addEventListener('click', () => {
                    action.handler();
                    if (!action.keepOpen) this.hide();
                });
            }
        });

        return this;
    }

    hide() {
        if (this.sheet) {
            this.sheet.classList.remove('active');
            setTimeout(() => {
                this.sheet.remove();
            }, 300);
        }
    }
}

// Floating Action Button
class FloatingActionButton {
    constructor(options = {}) {
        this.icon = options.icon || '+';
        this.actions = options.actions || [];
        this.fab = null;
    }

    create() {
        this.fab = document.createElement('div');
        this.fab.className = 'fab-container';
        this.fab.innerHTML = `
            <div class="fab-menu">
                ${this.actions.map(action => `
                    <button class="fab-action" data-action="${action.id}" title="${action.label}">
                        <svg class="icon"><use href="#icon-${action.icon}"></use></svg>
                    </button>
                `).join('')}
            </div>
            <button class="fab-main">
                <span class="fab-icon">${this.icon}</span>
            </button>
        `;

        document.body.appendChild(this.fab);

        // Bind events
        this.fab.querySelector('.fab-main').addEventListener('click', () => {
            this.fab.classList.toggle('active');
        });

        this.actions.forEach(action => {
            const btn = this.fab.querySelector(`[data-action="${action.id}"]`);
            if (btn && action.handler) {
                btn.addEventListener('click', () => {
                    action.handler();
                    this.fab.classList.remove('active');
                });
            }
        });

        return this;
    }
}

// Toast Notifications
class Toast {
    static show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `portal-toast toast-${type}`;
        toast.textContent = message;

        document.body.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    static success(message) {
        this.show(message, 'success');
    }

    static error(message) {
        this.show(message, 'error');
    }

    static warning(message) {
        this.show(message, 'warning');
    }
}

// Export for global access
window.MobilePortal = MobilePortal;
window.BottomSheet = BottomSheet;
window.FloatingActionButton = FloatingActionButton;
window.Toast = Toast;

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.portal-container')) {
        MobilePortal.init();
    }
});
