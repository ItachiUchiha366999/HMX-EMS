/**
 * University ERP - Main Application JavaScript
 * Core client-side functionality for the desk interface
 */

(function() {
    'use strict';

    // Initialize when frappe is ready
    if (typeof frappe !== 'undefined') {
        frappe.provide('university_erp');

        // University ERP namespace
        university_erp = {
            version: '1.0.0',

            /**
             * Initialize University ERP customizations
             */
            init: function() {
                this.setup_desk_customizations();
                this.setup_quick_actions();
            },

            /**
             * Setup desk UI customizations
             */
            setup_desk_customizations: function() {
                // Add university branding class to body
                if (document.body) {
                    document.body.classList.add('university-erp');
                }

                // Custom page title for university pages
                this.update_page_titles();
            },

            /**
             * Update page titles for university modules
             */
            update_page_titles: function() {
                var university_modules = [
                    'University Academics',
                    'University Finance',
                    'Faculty Management',
                    'University Hostel',
                    'University Transport',
                    'University Library',
                    'University Placement'
                ];

                // Check if current module is a university module
                var route = frappe.get_route ? frappe.get_route() : null;
                if (route && route[0] === 'Workspaces') {
                    var workspace = route[1];
                    if (workspace && university_modules.includes(workspace)) {
                        // Add custom styling for university workspaces
                        setTimeout(function() {
                            var header = document.querySelector('.page-head .page-title');
                            if (header) {
                                header.style.color = '#6366f1';
                            }
                        }, 100);
                    }
                }
            },

            /**
             * Setup quick actions for common operations
             */
            setup_quick_actions: function() {
                // Add keyboard shortcuts
                if (frappe.ui && frappe.ui.keys) {
                    // Ctrl+Shift+S for quick student search
                    frappe.ui.keys.add_shortcut({
                        shortcut: 'ctrl+shift+s',
                        action: function() {
                            frappe.set_route('List', 'Student');
                        },
                        description: 'Go to Student List',
                        page: '*'
                    });

                    // Ctrl+Shift+F for quick fee search
                    frappe.ui.keys.add_shortcut({
                        shortcut: 'ctrl+shift+f',
                        action: function() {
                            frappe.set_route('List', 'Fees');
                        },
                        description: 'Go to Fees List',
                        page: '*'
                    });
                }
            },

            /**
             * Show notification with university branding
             */
            notify: function(message, type) {
                type = type || 'green';
                frappe.show_alert({
                    message: message,
                    indicator: type
                }, 5);
            },

            /**
             * Format student enrollment number
             */
            format_enrollment: function(enrollment_number) {
                if (!enrollment_number) return '';
                // Format: YYYY-DEPT-XXXX
                return enrollment_number.toUpperCase();
            },

            /**
             * Calculate CGPA from grades
             */
            calculate_cgpa: function(grades) {
                if (!grades || !grades.length) return 0;

                var total_points = 0;
                var total_credits = 0;

                grades.forEach(function(grade) {
                    total_points += (grade.grade_point || 0) * (grade.credits || 0);
                    total_credits += grade.credits || 0;
                });

                return total_credits > 0 ? (total_points / total_credits).toFixed(2) : 0;
            }
        };

        // Initialize on page load - check if jQuery is available
        if (typeof $ !== 'undefined') {
            $(document).ready(function() {
                university_erp.init();
            });
        } else if (typeof frappe !== 'undefined' && frappe.ready) {
            // Fallback to frappe.ready if jQuery not available yet
            frappe.ready(function() {
                university_erp.init();
            });
        }

        // Also initialize on route change
        if (frappe.router && frappe.router.on) {
            frappe.router.on('change', function() {
                university_erp.update_page_titles();
            });
        }
    }

})();
