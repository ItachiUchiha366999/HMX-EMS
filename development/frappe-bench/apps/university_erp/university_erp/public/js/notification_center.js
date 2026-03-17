// University ERP Notification Center
// Handles in-app notifications with real-time updates

frappe.provide('university_erp.notifications');

university_erp.notifications = {
    unread_count: 0,
    notifications: [],
    is_open: false,
    poll_interval: null,

    init: function() {
        var self = this;

        // Wait for page to be ready
        if (!frappe.boot || !frappe.boot.user || frappe.boot.user.name === 'Guest') {
            return;
        }

        // Setup notification bell in navbar
        this.setup_notification_bell();

        // Setup real-time listeners
        this.setup_realtime_listeners();

        // Initial fetch of notifications
        this.fetch_unread_count();

        // Setup polling fallback (every 60 seconds)
        this.poll_interval = setInterval(function() {
            self.fetch_unread_count();
        }, 60000);
    },

    setup_notification_bell: function() {
        var self = this;

        // Check if bell already exists
        if ($('#university-notification-bell').length) {
            return;
        }

        // Create notification bell HTML
        var bell_html = `
            <li class="nav-item dropdown" id="university-notification-bell">
                <a class="nav-link notification-bell-icon" href="#" role="button"
                   data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    <svg class="icon icon-md" style="stroke: currentColor;">
                        <use href="#icon-notification"></use>
                    </svg>
                    <span class="notification-badge" style="display: none;">0</span>
                </a>
                <div class="dropdown-menu dropdown-menu-right notification-dropdown">
                    <div class="notification-header">
                        <span class="notification-title">Notifications</span>
                        <a href="#" class="mark-all-read">Mark all read</a>
                    </div>
                    <div class="notification-list">
                        <div class="notification-loading">
                            <span class="text-muted">Loading...</span>
                        </div>
                    </div>
                    <div class="notification-footer">
                        <a href="/app/user-notification" class="view-all-link">View All Notifications</a>
                    </div>
                </div>
            </li>
        `;

        // Insert bell after search or at beginning of navbar
        var $navbar = $('.navbar-nav.ml-auto, .navbar-nav.ms-auto').first();
        if ($navbar.length) {
            $navbar.prepend(bell_html);
        } else {
            // Fallback: append to navbar
            $('.navbar-collapse .navbar-nav').first().append(bell_html);
        }

        // Add styles
        this.add_styles();

        // Bind events
        this.bind_events();
    },

    add_styles: function() {
        if ($('#notification-center-styles').length) {
            return;
        }

        $('head').append(`
            <style id="notification-center-styles">
                #university-notification-bell {
                    position: relative;
                }

                .notification-bell-icon {
                    position: relative;
                    padding: 8px 12px;
                    cursor: pointer;
                }

                .notification-badge {
                    position: absolute;
                    top: 2px;
                    right: 2px;
                    background: #e53935;
                    color: white;
                    border-radius: 10px;
                    padding: 2px 6px;
                    font-size: 10px;
                    font-weight: bold;
                    min-width: 18px;
                    text-align: center;
                    line-height: 1.2;
                }

                .notification-dropdown {
                    width: 360px;
                    max-height: 480px;
                    padding: 0;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                }

                .notification-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px 16px;
                    border-bottom: 1px solid var(--border-color, #e0e0e0);
                    background: var(--bg-color, #f8f9fa);
                }

                .notification-title {
                    font-weight: 600;
                    font-size: 14px;
                }

                .mark-all-read {
                    font-size: 12px;
                    color: var(--primary-color, #2490ef);
                }

                .notification-list {
                    max-height: 360px;
                    overflow-y: auto;
                }

                .notification-item {
                    display: flex;
                    padding: 12px 16px;
                    border-bottom: 1px solid var(--border-color, #f0f0f0);
                    cursor: pointer;
                    transition: background 0.2s;
                }

                .notification-item:hover {
                    background: var(--hover-color, #f5f5f5);
                }

                .notification-item.unread {
                    background: rgba(36, 144, 239, 0.05);
                }

                .notification-item.unread:hover {
                    background: rgba(36, 144, 239, 0.1);
                }

                .notification-icon {
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 12px;
                    flex-shrink: 0;
                }

                .notification-icon.info { background: #e3f2fd; color: #1976d2; }
                .notification-icon.success { background: #e8f5e9; color: #388e3c; }
                .notification-icon.warning { background: #fff3e0; color: #f57c00; }
                .notification-icon.error { background: #ffebee; color: #d32f2f; }
                .notification-icon.announcement { background: #ede7f6; color: #7b1fa2; }

                .notification-content {
                    flex: 1;
                    min-width: 0;
                }

                .notification-content-title {
                    font-size: 13px;
                    font-weight: 500;
                    margin-bottom: 4px;
                    line-height: 1.3;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                }

                .notification-content-message {
                    font-size: 12px;
                    color: var(--text-muted, #6c757d);
                    display: -webkit-box;
                    -webkit-line-clamp: 1;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                }

                .notification-time {
                    font-size: 11px;
                    color: var(--text-muted, #999);
                    margin-top: 4px;
                }

                .notification-footer {
                    padding: 12px 16px;
                    border-top: 1px solid var(--border-color, #e0e0e0);
                    text-align: center;
                    background: var(--bg-color, #f8f9fa);
                }

                .view-all-link {
                    font-size: 13px;
                    font-weight: 500;
                }

                .notification-empty {
                    padding: 40px 20px;
                    text-align: center;
                    color: var(--text-muted, #999);
                }

                .notification-empty-icon {
                    font-size: 48px;
                    margin-bottom: 12px;
                    opacity: 0.5;
                }

                .notification-loading {
                    padding: 20px;
                    text-align: center;
                }

                /* Animation for new notification */
                @keyframes notification-pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.2); }
                    100% { transform: scale(1); }
                }

                .notification-badge.pulse {
                    animation: notification-pulse 0.5s ease-in-out;
                }
            </style>
        `);
    },

    bind_events: function() {
        var self = this;

        // On dropdown open
        $(document).on('show.bs.dropdown', '#university-notification-bell', function() {
            self.is_open = true;
            self.fetch_notifications();
        });

        $(document).on('hide.bs.dropdown', '#university-notification-bell', function() {
            self.is_open = false;
        });

        // Mark all as read
        $(document).on('click', '.mark-all-read', function(e) {
            e.preventDefault();
            e.stopPropagation();
            self.mark_all_read();
        });

        // Click on notification item
        $(document).on('click', '.notification-item', function(e) {
            var $item = $(this);
            var notification_name = $item.data('name');
            var link = $item.data('link');

            // Mark as read
            if ($item.hasClass('unread')) {
                self.mark_as_read(notification_name);
            }

            // Navigate to link
            if (link) {
                frappe.set_route(link);
            }
        });
    },

    setup_realtime_listeners: function() {
        var self = this;

        // Listen for new notifications
        frappe.realtime.on('university_notification', function(data) {
            self.on_new_notification(data);
        });

        // Listen for notification read
        frappe.realtime.on('notification_read', function(data) {
            if (data.user === frappe.session.user) {
                self.fetch_unread_count();
            }
        });
    },

    fetch_unread_count: function() {
        var self = this;

        frappe.call({
            method: 'university_erp.university_erp.notification_center.get_unread_count',
            async: true,
            callback: function(r) {
                if (r.message !== undefined) {
                    self.update_badge(r.message);
                }
            }
        });
    },

    fetch_notifications: function() {
        var self = this;
        var $list = $('.notification-list');

        $list.html('<div class="notification-loading"><span class="text-muted">Loading...</span></div>');

        frappe.call({
            method: 'university_erp.university_erp.notification_center.get_notifications',
            args: {
                limit: 10
            },
            callback: function(r) {
                if (r.message) {
                    self.notifications = r.message;
                    self.render_notifications();
                }
            }
        });
    },

    render_notifications: function() {
        var self = this;
        var $list = $('.notification-list');

        if (!this.notifications || this.notifications.length === 0) {
            $list.html(`
                <div class="notification-empty">
                    <div class="notification-empty-icon">
                        <svg class="icon icon-lg">
                            <use href="#icon-notification"></use>
                        </svg>
                    </div>
                    <p>No notifications yet</p>
                </div>
            `);
            return;
        }

        var html = '';
        this.notifications.forEach(function(n) {
            var icon_class = self.get_icon_class(n.notification_type);
            var icon = self.get_icon(n.notification_type);
            var time_ago = frappe.datetime.prettyDate(n.creation);

            html += `
                <div class="notification-item ${n.read ? '' : 'unread'}"
                     data-name="${n.name}"
                     data-link="${n.link || ''}">
                    <div class="notification-icon ${icon_class}">
                        <i class="fa ${icon}"></i>
                    </div>
                    <div class="notification-content">
                        <div class="notification-content-title">${frappe.utils.escape_html(n.title)}</div>
                        ${n.message ? `<div class="notification-content-message">${frappe.utils.escape_html(n.message)}</div>` : ''}
                        <div class="notification-time">${time_ago}</div>
                    </div>
                </div>
            `;
        });

        $list.html(html);
    },

    get_icon_class: function(type) {
        var classes = {
            'info': 'info',
            'success': 'success',
            'warning': 'warning',
            'error': 'error',
            'announcement': 'announcement'
        };
        return classes[type] || 'info';
    },

    get_icon: function(type) {
        var icons = {
            'info': 'fa-info-circle',
            'success': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'error': 'fa-times-circle',
            'announcement': 'fa-bullhorn'
        };
        return icons[type] || 'fa-bell';
    },

    update_badge: function(count) {
        var $badge = $('.notification-badge');
        this.unread_count = count;

        if (count > 0) {
            $badge.text(count > 99 ? '99+' : count).show();
        } else {
            $badge.hide();
        }
    },

    on_new_notification: function(data) {
        var self = this;

        // Update badge with animation
        this.unread_count++;
        var $badge = $('.notification-badge');
        $badge.text(this.unread_count > 99 ? '99+' : this.unread_count).show();
        $badge.addClass('pulse');
        setTimeout(function() {
            $badge.removeClass('pulse');
        }, 500);

        // Show toast notification
        if (data.title) {
            frappe.show_alert({
                message: data.title,
                indicator: this.get_indicator_color(data.notification_type)
            }, 7);
        }

        // Play sound if enabled
        this.play_notification_sound();

        // Refresh list if dropdown is open
        if (this.is_open) {
            this.fetch_notifications();
        }
    },

    get_indicator_color: function(type) {
        var colors = {
            'info': 'blue',
            'success': 'green',
            'warning': 'orange',
            'error': 'red',
            'announcement': 'purple'
        };
        return colors[type] || 'blue';
    },

    mark_as_read: function(notification_name) {
        var self = this;

        frappe.call({
            method: 'university_erp.university_erp.notification_center.mark_notification_read',
            args: {
                notification_name: notification_name
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    // Update UI
                    $(`.notification-item[data-name="${notification_name}"]`).removeClass('unread');
                    self.unread_count = Math.max(0, self.unread_count - 1);
                    self.update_badge(self.unread_count);
                }
            }
        });
    },

    mark_all_read: function() {
        var self = this;

        frappe.call({
            method: 'university_erp.university_erp.notification_center.mark_all_notifications_read',
            callback: function(r) {
                if (r.message && r.message.success) {
                    // Update UI
                    $('.notification-item').removeClass('unread');
                    self.unread_count = 0;
                    self.update_badge(0);

                    frappe.show_alert({
                        message: 'All notifications marked as read',
                        indicator: 'green'
                    }, 3);
                }
            }
        });
    },

    play_notification_sound: function() {
        // Check if user has enabled notification sounds (could be a preference)
        try {
            var audio = new Audio('/assets/frappe/sounds/chat-notification.mp3');
            audio.volume = 0.5;
            audio.play().catch(function() {
                // Autoplay blocked, ignore
            });
        } catch (e) {
            // Audio not supported
        }
    }
};

// Initialize on document ready
$(document).ready(function() {
    // Small delay to ensure frappe is fully loaded
    setTimeout(function() {
        university_erp.notifications.init();
    }, 1000);
});
