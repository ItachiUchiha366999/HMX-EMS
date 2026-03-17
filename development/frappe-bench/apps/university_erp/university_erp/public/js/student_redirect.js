// Auto-redirect students to portal - fallback client-side redirect
// Primary redirect is handled server-side in on_session_creation hook
(function() {
    'use strict';

    var DEBUG = false; // Set to true for console logging

    function log() {
        if (DEBUG) console.log.apply(console, ['[Student Redirect]'].concat(Array.prototype.slice.call(arguments)));
    }

    // Clear last_visited from localStorage on login page to prevent
    // redirecting students to admin pages after admin logout
    if (window.location.pathname === '/login' || window.location.pathname === '/') {
        try {
            var lastVisited = localStorage.getItem('last_visited');
            if (lastVisited && (lastVisited.startsWith('/app') || lastVisited.startsWith('/desk'))) {
                localStorage.removeItem('last_visited');
                log('Cleared last_visited:', lastVisited);
            }
        } catch(e) {}
    }

    log('Script loaded on path:', window.location.pathname);

    // Function to check if user has Student role
    function hasStudentRole() {
        // Never redirect Administrator or System Manager
        if (window.frappe && frappe.session && frappe.session.user) {
            var username = frappe.session.user;
            if (username === 'Administrator' || username === 'administrator' || username === 'Guest') {
                log('User is', username, '- not redirecting');
                return false;
            }
        }

        // Check multiple ways to get user roles
        var roles = null;
        if (window.frappe && frappe.boot && frappe.boot.user && frappe.boot.user.roles) {
            roles = frappe.boot.user.roles;
        } else if (window.frappe && frappe.user_roles) {
            roles = frappe.user_roles;
        }

        if (roles) {
            log('Found roles:', roles);

            // Don't redirect if user has System Manager role
            if (roles.includes('System Manager')) {
                log('User has System Manager role - not redirecting');
                return false;
            }

            return roles.includes('Student');
        }

        log('No roles found');
        return false;
    }

    // Function to check if we're on a desk page that should redirect
    function shouldRedirect() {
        var currentPath = window.location.pathname;
        return currentPath === '/app' ||
               currentPath === '/app/' ||
               currentPath === '/desk' ||
               currentPath === '/app/home';
    }

    // Function to perform redirect
    function redirectStudent() {
        if (!shouldRedirect()) {
            log('Not on a redirect path, skipping');
            return false;
        }

        if (hasStudentRole()) {
            log('Student role detected - REDIRECTING to /student_portal');
            window.location.replace('/student_portal');
            return true;
        }
        return false;
    }

    // Watch for "Not Permitted" error and redirect immediately
    function watchForPermissionError() {
        // Check if there's a permission error message on the page
        var checkError = function() {
            var errorMsg = document.querySelector('.msgprint, .page-card .indicator-pill, [data-page-container] .msgprint');
            var pageContent = document.body ? document.body.textContent : '';

            if ((errorMsg && errorMsg.textContent.toLowerCase().includes('not permitted')) ||
                pageContent.includes('Not permitted') ||
                pageContent.includes('Insufficient Permission')) {

                if (hasStudentRole()) {
                    log('Permission error detected, redirecting student');
                    window.location.replace('/student_portal');
                    return true;
                }
            }
            return false;
        };

        // Check immediately
        if (checkError()) return;

        // Also watch for dynamic content
        if (typeof MutationObserver !== 'undefined') {
            var observer = new MutationObserver(function(mutations) {
                if (checkError()) {
                    observer.disconnect();
                }
            });

            // Start observing after a short delay to let page load
            setTimeout(function() {
                if (document.body) {
                    observer.observe(document.body, { childList: true, subtree: true });
                    // Stop watching after 5 seconds
                    setTimeout(function() { observer.disconnect(); }, 5000);
                }
            }, 100);
        }
    }

    // Wait for frappe to be ready before checking
    function waitForFrappe() {
        log('Waiting for frappe...');

        // If frappe.boot is already available, redirect immediately
        if (window.frappe && frappe.boot && frappe.boot.user) {
            log('frappe.boot already available');
            redirectStudent();
            return;
        }

        // Otherwise, wait for frappe.ready
        if (window.frappe && typeof frappe.ready === 'function') {
            log('Using frappe.ready()');
            frappe.ready(function() {
                redirectStudent();
            });
        } else {
            // Frappe not ready yet, poll for it
            log('Polling for frappe.boot...');
            var attempts = 0;
            var checkInterval = setInterval(function() {
                attempts++;
                if (window.frappe && frappe.boot && frappe.boot.user) {
                    log('frappe.boot available after', attempts, 'attempts');
                    clearInterval(checkInterval);
                    redirectStudent();
                } else if (attempts > 30) {
                    clearInterval(checkInterval);
                    log('Timeout waiting for frappe.boot');
                }
            }, 100);
        }
    }

    // Start the process
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            waitForFrappe();
            watchForPermissionError();
        });
    } else {
        waitForFrappe();
        watchForPermissionError();
    }
})();
