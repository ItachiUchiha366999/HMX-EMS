frappe.pages['notification-center'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Notification Center',
        single_column: true
    });

    page.notification_center = new NotificationCenterPage(page);
};

frappe.pages['notification-center'].on_page_show = function(wrapper) {
    if (wrapper.page.notification_center) {
        wrapper.page.notification_center.refresh();
    }
};

class NotificationCenterPage {
    constructor(page) {
        this.page = page;
        this.current_page = 1;
        this.page_size = 20;
        this.category_filter = 'All';
        this.read_filter = 'all';
        this.selected = [];

        this.setup_page();
        this.make_filters();
        this.refresh();
    }

    setup_page() {
        this.page.set_primary_action(__('Mark All Read'), () => {
            this.mark_all_read();
        }, 'check');

        this.page.set_secondary_action(__('Refresh'), () => {
            this.refresh();
        }, 'refresh');

        this.page.add_menu_item(__('Delete Selected'), () => {
            this.delete_selected();
        });

        this.page.add_menu_item(__('Notification Settings'), () => {
            frappe.set_route('Form', 'Notification Preference');
        });

        this.$container = $('<div class="notification-center-container"></div>').appendTo(this.page.main);

        // Add styles
        if (!$('#notification-center-page-styles').length) {
            $('head').append(`
                <style id="notification-center-page-styles">
                    .notification-center-container {
                        max-width: 900px;
                        margin: 0 auto;
                        padding: 20px;
                    }

                    .notification-stats {
                        display: grid;
                        grid-template-columns: repeat(4, 1fr);
                        gap: 16px;
                        margin-bottom: 24px;
                    }

                    .stat-card {
                        background: var(--card-bg, white);
                        border-radius: 8px;
                        padding: 20px;
                        box-shadow: var(--card-shadow, 0 1px 3px rgba(0,0,0,0.1));
                        text-align: center;
                    }

                    .stat-card .stat-value {
                        font-size: 28px;
                        font-weight: 600;
                        color: var(--text-color);
                    }

                    .stat-card .stat-label {
                        font-size: 13px;
                        color: var(--text-muted);
                        margin-top: 4px;
                    }

                    .stat-card.unread .stat-value { color: #2563eb; }
                    .stat-card.total .stat-value { color: #059669; }

                    .notification-filters {
                        display: flex;
                        gap: 12px;
                        margin-bottom: 20px;
                        flex-wrap: wrap;
                    }

                    .notification-list-card {
                        background: var(--card-bg, white);
                        border-radius: 8px;
                        box-shadow: var(--card-shadow, 0 1px 3px rgba(0,0,0,0.1));
                        overflow: hidden;
                    }

                    .notification-list-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 16px 20px;
                        border-bottom: 1px solid var(--border-color, #e5e5e5);
                        background: var(--bg-color, #f9fafb);
                    }

                    .notification-list-header h4 {
                        margin: 0;
                        font-size: 16px;
                        font-weight: 600;
                    }

                    .select-all-wrapper {
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }

                    .notification-row {
                        display: flex;
                        align-items: flex-start;
                        padding: 16px 20px;
                        border-bottom: 1px solid var(--border-color, #f0f0f0);
                        cursor: pointer;
                        transition: background 0.2s;
                    }

                    .notification-row:hover {
                        background: var(--hover-color, #f5f5f5);
                    }

                    .notification-row.unread {
                        background: rgba(37, 99, 235, 0.04);
                    }

                    .notification-row.unread:hover {
                        background: rgba(37, 99, 235, 0.08);
                    }

                    .notification-checkbox {
                        margin-right: 12px;
                        margin-top: 4px;
                    }

                    .notification-icon-wrapper {
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 16px;
                        flex-shrink: 0;
                    }

                    .notification-icon-wrapper.info { background: #dbeafe; color: #2563eb; }
                    .notification-icon-wrapper.success { background: #d1fae5; color: #059669; }
                    .notification-icon-wrapper.warning { background: #fef3c7; color: #d97706; }
                    .notification-icon-wrapper.error { background: #fee2e2; color: #dc2626; }
                    .notification-icon-wrapper.announcement { background: #ede9fe; color: #7c3aed; }

                    .notification-body {
                        flex: 1;
                        min-width: 0;
                    }

                    .notification-title-row {
                        display: flex;
                        justify-content: space-between;
                        align-items: flex-start;
                        margin-bottom: 4px;
                    }

                    .notification-title {
                        font-weight: 500;
                        color: var(--text-color);
                        font-size: 14px;
                    }

                    .notification-row.unread .notification-title {
                        font-weight: 600;
                    }

                    .notification-meta {
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        flex-shrink: 0;
                    }

                    .notification-time {
                        font-size: 12px;
                        color: var(--text-muted);
                    }

                    .notification-category {
                        font-size: 11px;
                        padding: 2px 8px;
                        border-radius: 10px;
                        background: var(--bg-color, #f0f0f0);
                        color: var(--text-muted);
                    }

                    .notification-message {
                        font-size: 13px;
                        color: var(--text-muted);
                        line-height: 1.4;
                        display: -webkit-box;
                        -webkit-line-clamp: 2;
                        -webkit-box-orient: vertical;
                        overflow: hidden;
                    }

                    .notification-priority {
                        display: inline-block;
                        font-size: 10px;
                        padding: 2px 6px;
                        border-radius: 4px;
                        margin-left: 8px;
                    }

                    .notification-priority.high { background: #fef2f2; color: #dc2626; }
                    .notification-priority.urgent { background: #dc2626; color: white; }

                    .pagination-wrapper {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        gap: 8px;
                        padding: 20px;
                        border-top: 1px solid var(--border-color, #e5e5e5);
                    }

                    .pagination-info {
                        font-size: 13px;
                        color: var(--text-muted);
                        margin: 0 16px;
                    }

                    .empty-state {
                        text-align: center;
                        padding: 60px 20px;
                        color: var(--text-muted);
                    }

                    .empty-state svg {
                        width: 64px;
                        height: 64px;
                        margin-bottom: 16px;
                        opacity: 0.5;
                    }

                    @media (max-width: 768px) {
                        .notification-stats {
                            grid-template-columns: repeat(2, 1fr);
                        }

                        .notification-meta {
                            flex-direction: column;
                            align-items: flex-end;
                            gap: 4px;
                        }
                    }
                </style>
            `);
        }
    }

    make_filters() {
        // Category filter and read/unread filter are added to page filters
        this.page.add_field({
            fieldname: 'category',
            label: __('Category'),
            fieldtype: 'Select',
            options: [
                'All',
                'General',
                'Academic',
                'Fee',
                'Examination',
                'Library',
                'Hostel',
                'Placement',
                'Emergency'
            ],
            default: 'All',
            change: () => {
                this.category_filter = this.page.fields_dict.category.get_value();
                this.current_page = 1;
                this.load_notifications();
            }
        });

        this.page.add_field({
            fieldname: 'read_status',
            label: __('Status'),
            fieldtype: 'Select',
            options: [
                {label: 'All', value: 'all'},
                {label: 'Unread', value: 'unread'},
                {label: 'Read', value: 'read'}
            ],
            default: 'all',
            change: () => {
                this.read_filter = this.page.fields_dict.read_status.get_value();
                this.current_page = 1;
                this.load_notifications();
            }
        });
    }

    refresh() {
        this.load_stats();
        this.load_notifications();
    }

    load_stats() {
        frappe.call({
            method: 'university_erp.university_erp.page.notification_center.notification_center.get_notification_stats',
            callback: (r) => {
                if (r.message) {
                    this.render_stats(r.message);
                }
            }
        });
    }

    render_stats(stats) {
        let stats_html = `
            <div class="notification-stats">
                <div class="stat-card unread">
                    <div class="stat-value">${stats.unread}</div>
                    <div class="stat-label">Unread</div>
                </div>
                <div class="stat-card total">
                    <div class="stat-value">${stats.total}</div>
                    <div class="stat-label">Total</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.read}</div>
                    <div class="stat-label">Read</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${Object.keys(stats.categories || {}).length}</div>
                    <div class="stat-label">Categories</div>
                </div>
            </div>
        `;

        this.$container.find('.notification-stats').remove();
        this.$container.prepend(stats_html);
    }

    load_notifications() {
        frappe.call({
            method: 'university_erp.university_erp.page.notification_center.notification_center.get_notifications_paginated',
            args: {
                page: this.current_page,
                page_size: this.page_size,
                category: this.category_filter,
                read_status: this.read_filter
            },
            callback: (r) => {
                if (r.message) {
                    this.render_notifications(r.message);
                }
            }
        });
    }

    render_notifications(data) {
        this.$container.find('.notification-list-card').remove();

        if (!data.notifications || data.notifications.length === 0) {
            let empty_html = `
                <div class="notification-list-card">
                    <div class="empty-state">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                        </svg>
                        <h4>${__('No notifications')}</h4>
                        <p>${__('You\'re all caught up!')}</p>
                    </div>
                </div>
            `;
            this.$container.append(empty_html);
            return;
        }

        let list_html = `
            <div class="notification-list-card">
                <div class="notification-list-header">
                    <h4>${__('Notifications')}</h4>
                    <div class="select-all-wrapper">
                        <input type="checkbox" id="select-all-notifications" />
                        <label for="select-all-notifications">${__('Select All')}</label>
                    </div>
                </div>
                <div class="notification-list">
                    ${data.notifications.map(n => this.render_notification_row(n)).join('')}
                </div>
                ${this.render_pagination(data)}
            </div>
        `;

        this.$container.append(list_html);
        this.bind_notification_events();
    }

    render_notification_row(n) {
        let icon_class = this.get_icon_class(n.notification_type);
        let icon = this.get_icon(n.notification_type);
        let time_ago = frappe.datetime.prettyDate(n.creation);

        let priority_badge = '';
        if (n.priority === 'High') {
            priority_badge = '<span class="notification-priority high">High</span>';
        } else if (n.priority === 'Urgent') {
            priority_badge = '<span class="notification-priority urgent">Urgent</span>';
        }

        return `
            <div class="notification-row ${n.read ? '' : 'unread'}" data-name="${n.name}" data-link="${n.link || ''}">
                <input type="checkbox" class="notification-checkbox" data-name="${n.name}" />
                <div class="notification-icon-wrapper ${icon_class}">
                    <i class="fa ${icon}"></i>
                </div>
                <div class="notification-body">
                    <div class="notification-title-row">
                        <span class="notification-title">
                            ${frappe.utils.escape_html(n.title)}
                            ${priority_badge}
                        </span>
                        <div class="notification-meta">
                            <span class="notification-category">${n.category || 'General'}</span>
                            <span class="notification-time">${time_ago}</span>
                        </div>
                    </div>
                    ${n.message ? `<div class="notification-message">${frappe.utils.escape_html(n.message)}</div>` : ''}
                </div>
            </div>
        `;
    }

    render_pagination(data) {
        if (data.total_pages <= 1) return '';

        return `
            <div class="pagination-wrapper">
                <button class="btn btn-default btn-sm" ${data.page <= 1 ? 'disabled' : ''} data-action="prev">
                    <i class="fa fa-chevron-left"></i> ${__('Previous')}
                </button>
                <span class="pagination-info">
                    ${__('Page')} ${data.page} ${__('of')} ${data.total_pages}
                </span>
                <button class="btn btn-default btn-sm" ${data.page >= data.total_pages ? 'disabled' : ''} data-action="next">
                    ${__('Next')} <i class="fa fa-chevron-right"></i>
                </button>
            </div>
        `;
    }

    bind_notification_events() {
        let self = this;

        // Click on notification row
        this.$container.find('.notification-row').on('click', function(e) {
            if ($(e.target).is('input[type="checkbox"]')) return;

            let $row = $(this);
            let name = $row.data('name');
            let link = $row.data('link');

            // Mark as read
            if ($row.hasClass('unread')) {
                self.mark_as_read([name]);
                $row.removeClass('unread');
            }

            // Navigate if link
            if (link) {
                frappe.set_route(link);
            }
        });

        // Checkbox change
        this.$container.find('.notification-checkbox').on('change', function(e) {
            e.stopPropagation();
            self.update_selection();
        });

        // Select all
        this.$container.find('#select-all-notifications').on('change', function() {
            let checked = $(this).is(':checked');
            self.$container.find('.notification-checkbox').prop('checked', checked);
            self.update_selection();
        });

        // Pagination
        this.$container.find('.pagination-wrapper button').on('click', function() {
            let action = $(this).data('action');
            if (action === 'prev' && self.current_page > 1) {
                self.current_page--;
                self.load_notifications();
            } else if (action === 'next') {
                self.current_page++;
                self.load_notifications();
            }
        });
    }

    update_selection() {
        this.selected = [];
        this.$container.find('.notification-checkbox:checked').each((i, el) => {
            this.selected.push($(el).data('name'));
        });
    }

    get_icon_class(type) {
        let classes = {
            'info': 'info',
            'success': 'success',
            'warning': 'warning',
            'error': 'error',
            'announcement': 'announcement'
        };
        return classes[type] || 'info';
    }

    get_icon(type) {
        let icons = {
            'info': 'fa-info-circle',
            'success': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'error': 'fa-times-circle',
            'announcement': 'fa-bullhorn'
        };
        return icons[type] || 'fa-bell';
    }

    mark_as_read(names) {
        frappe.call({
            method: 'university_erp.university_erp.page.notification_center.notification_center.bulk_mark_read',
            args: { notification_names: names },
            callback: (r) => {
                if (r.message && r.message.success) {
                    this.load_stats();
                }
            }
        });
    }

    mark_all_read() {
        frappe.call({
            method: 'university_erp.university_erp.notification_center.mark_all_notifications_read',
            callback: (r) => {
                if (r.message && r.message.success) {
                    frappe.show_alert({
                        message: __('All notifications marked as read'),
                        indicator: 'green'
                    });
                    this.refresh();
                }
            }
        });
    }

    delete_selected() {
        if (this.selected.length === 0) {
            frappe.msgprint(__('Please select notifications to delete'));
            return;
        }

        frappe.confirm(
            __('Are you sure you want to delete {0} notification(s)?', [this.selected.length]),
            () => {
                frappe.call({
                    method: 'university_erp.university_erp.page.notification_center.notification_center.bulk_delete',
                    args: { notification_names: this.selected },
                    callback: (r) => {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: __('Deleted {0} notification(s)', [r.message.deleted]),
                                indicator: 'green'
                            });
                            this.selected = [];
                            this.refresh();
                        }
                    }
                });
            }
        );
    }
}
