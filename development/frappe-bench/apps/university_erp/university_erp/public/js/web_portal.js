/**
 * University ERP - Web Portal JavaScript
 * Fixes and enhancements for default Frappe web portal
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        initDropdownFix();
        initLogoutFix();
    });

    /**
     * Fix navbar dropdown behavior
     * Ensures dropdown menus work properly on click
     */
    function initDropdownFix() {
        // Find all dropdown toggles in navbar
        var dropdowns = document.querySelectorAll('.navbar .dropdown-toggle, .navbar .nav-link[data-toggle="dropdown"], .navbar .nav-link[data-bs-toggle="dropdown"]');

        dropdowns.forEach(function(toggle) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                var parent = this.closest('.dropdown') || this.closest('.nav-item');
                var menu = parent ? parent.querySelector('.dropdown-menu') : null;

                if (!menu) return;

                // Close all other dropdowns first
                document.querySelectorAll('.navbar .dropdown-menu.show').forEach(function(m) {
                    if (m !== menu) {
                        m.classList.remove('show');
                        var p = m.closest('.dropdown') || m.closest('.nav-item');
                        if (p) p.classList.remove('show');
                    }
                });

                // Toggle current dropdown
                menu.classList.toggle('show');
                if (parent) parent.classList.toggle('show');
            });
        });

        // Also handle avatar clicks that might not have proper attributes
        var avatarLinks = document.querySelectorAll('.navbar .avatar-medium, .navbar .avatar-frame, .navbar [class*="avatar"]');
        avatarLinks.forEach(function(avatar) {
            var parent = avatar.closest('.dropdown') || avatar.closest('.nav-item');
            if (parent && parent.querySelector('.dropdown-menu')) {
                avatar.style.cursor = 'pointer';
                avatar.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();

                    var menu = parent.querySelector('.dropdown-menu');

                    // Close all other dropdowns
                    document.querySelectorAll('.navbar .dropdown-menu.show').forEach(function(m) {
                        if (m !== menu) {
                            m.classList.remove('show');
                            var p = m.closest('.dropdown') || m.closest('.nav-item');
                            if (p) p.classList.remove('show');
                        }
                    });

                    // Toggle
                    menu.classList.toggle('show');
                    parent.classList.toggle('show');
                });
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dropdown') && !e.target.closest('.nav-item.dropdown')) {
                document.querySelectorAll('.navbar .dropdown-menu.show').forEach(function(menu) {
                    menu.classList.remove('show');
                    var parent = menu.closest('.dropdown') || menu.closest('.nav-item');
                    if (parent) parent.classList.remove('show');
                });
            }
        });

        // Close dropdown on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.navbar .dropdown-menu.show').forEach(function(menu) {
                    menu.classList.remove('show');
                    var parent = menu.closest('.dropdown') || menu.closest('.nav-item');
                    if (parent) parent.classList.remove('show');
                });
            }
        });
    }

    /**
     * Ensure logout functionality works
     */
    function initLogoutFix() {
        // Add logout link if not present in dropdown
        var dropdownMenus = document.querySelectorAll('.navbar .dropdown-menu');

        dropdownMenus.forEach(function(menu) {
            var hasLogout = menu.querySelector('[href*="logout"], [href*="web_logout"]');

            if (!hasLogout) {
                // Check if this looks like a user menu
                var hasProfileLinks = menu.querySelector('[href*="me"], [href*="profile"], [href*="account"]');

                if (hasProfileLinks) {
                    // Add logout link
                    var divider = document.createElement('div');
                    divider.className = 'dropdown-divider';

                    var logoutLink = document.createElement('a');
                    logoutLink.className = 'dropdown-item';
                    logoutLink.href = '/?cmd=web_logout';
                    logoutLink.innerHTML = '<i class="fa fa-sign-out"></i> Logout';

                    menu.appendChild(divider);
                    menu.appendChild(logoutLink);
                }
            }
        });

        // Also add a visible logout option if user is logged in but can't access menu
        if (frappe && frappe.session && frappe.session.user && frappe.session.user !== 'Guest') {
            addEmergencyLogout();
        }
    }

    /**
     * Add emergency logout link if dropdown doesn't work
     */
    function addEmergencyLogout() {
        // Check if there's already a working logout mechanism
        var existingLogout = document.querySelector('.navbar [href*="logout"], .navbar [href*="web_logout"]');
        if (existingLogout) return;

        // Find navbar actions area or create logout button
        var navbar = document.querySelector('.navbar-nav.ml-auto, .navbar-nav.ms-auto, .navbar .navbar-right');

        if (navbar) {
            var logoutItem = document.createElement('li');
            logoutItem.className = 'nav-item d-none d-md-block';
            logoutItem.innerHTML = '<a class="nav-link" href="/?cmd=web_logout" title="Logout"><i class="fa fa-sign-out"></i></a>';
            navbar.appendChild(logoutItem);
        }
    }

    // Also run on frappe.ready if available
    if (typeof frappe !== 'undefined' && frappe.ready) {
        frappe.ready(function() {
            initDropdownFix();
            initLogoutFix();
        });
    }

})();
