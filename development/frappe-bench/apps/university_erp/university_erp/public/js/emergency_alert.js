// Emergency Alert UI Component
// Handles real-time emergency alerts and acknowledgment

frappe.provide('university_erp.emergency');

university_erp.emergency = {
    active_alerts: [],
    audio: null,

    init: function() {
        // Listen for emergency alerts
        frappe.realtime.on('emergency_alert', function(data) {
            university_erp.emergency.show_alert(data);
        });

        // Listen for emergency resolved
        frappe.realtime.on('emergency_resolved', function(data) {
            university_erp.emergency.show_resolved(data);
        });

        // Listen for emergency cancelled
        frappe.realtime.on('emergency_cancelled', function(data) {
            university_erp.emergency.dismiss_alert(data.alert_id);
        });

        // Check for active alerts on page load
        this.check_active_alerts();
    },

    check_active_alerts: function() {
        frappe.call({
            method: 'university_erp.university_erp.doctype.emergency_alert.emergency_alert.get_active_alerts',
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    r.message.forEach(function(alert) {
                        university_erp.emergency.show_persistent_banner(alert);
                    });
                }
            }
        });
    },

    show_alert: function(data) {
        var self = this;

        // Play audio if enabled
        if (data.play_audio) {
            this.play_alert_sound();
        }

        // Create overlay for critical alerts
        if (data.severity === 'Critical') {
            this.show_fullscreen_alert(data);
        } else {
            this.show_modal_alert(data);
        }

        // Add to active alerts
        this.active_alerts.push(data.alert_id);

        // Show persistent banner
        this.show_persistent_banner(data);
    },

    show_fullscreen_alert: function(data) {
        var self = this;

        var overlay = $(`
            <div class="emergency-overlay" id="emergency-overlay-${data.alert_id}">
                <div class="emergency-content">
                    <div class="emergency-icon">
                        <i class="fa fa-exclamation-triangle fa-4x"></i>
                    </div>
                    <h1 class="emergency-title">EMERGENCY ALERT</h1>
                    <h2 class="emergency-type">${data.alert_type}</h2>
                    <h3>${data.title}</h3>
                    <p class="emergency-message">${data.message}</p>
                    ${data.instructions ? `<div class="emergency-instructions">
                        <h4>Safety Instructions:</h4>
                        <p>${data.instructions}</p>
                    </div>` : ''}
                    <div class="emergency-contacts">
                        <h4>Emergency Contacts:</h4>
                        <div class="contact-list">
                            <a href="tel:100" class="emergency-contact-btn">
                                <i class="fa fa-phone"></i> Police: 100
                            </a>
                            <a href="tel:101" class="emergency-contact-btn">
                                <i class="fa fa-fire-extinguisher"></i> Fire: 101
                            </a>
                            <a href="tel:102" class="emergency-contact-btn">
                                <i class="fa fa-ambulance"></i> Ambulance: 102
                            </a>
                            <a href="#" class="emergency-contact-btn campus-security" onclick="university_erp.emergency.call_campus_security()">
                                <i class="fa fa-shield"></i> Campus Security
                            </a>
                        </div>
                    </div>
                    <div class="emergency-actions">
                        <button class="btn btn-primary btn-lg acknowledge-btn" data-alert="${data.alert_id}">
                            <i class="fa fa-check"></i> I Acknowledge
                        </button>
                    </div>
                </div>
            </div>
        `);

        overlay.find('.acknowledge-btn').on('click', function() {
            self.acknowledge_alert(data.alert_id);
        });

        $('body').append(overlay);

        // Add CSS if not already added
        if (!$('#emergency-alert-styles').length) {
            this.add_styles();
        }
    },

    show_modal_alert: function(data) {
        var self = this;

        var severity_color = {
            'Critical': '#dc2626',
            'High': '#ea580c',
            'Medium': '#ca8a04',
            'Low': '#65a30d'
        };

        var d = new frappe.ui.Dialog({
            title: `<span style="color: ${severity_color[data.severity] || '#dc2626'}">
                <i class="fa fa-exclamation-triangle"></i> EMERGENCY: ${data.alert_type}
            </span>`,
            fields: [
                {
                    fieldtype: 'HTML',
                    options: `
                        <div class="emergency-modal-content">
                            <h4>${data.title}</h4>
                            <p>${data.message}</p>
                            ${data.instructions ? `
                                <div class="alert alert-warning">
                                    <strong>Safety Instructions:</strong><br>
                                    ${data.instructions}
                                </div>
                            ` : ''}
                        </div>
                    `
                }
            ],
            primary_action_label: 'Acknowledge',
            primary_action: function() {
                self.acknowledge_alert(data.alert_id);
                d.hide();
            },
            secondary_action_label: 'View Details',
            secondary_action: function() {
                frappe.set_route('Form', 'Emergency Alert', data.alert_id);
                d.hide();
            }
        });

        d.show();
        d.$wrapper.find('.modal-header').css('background-color', severity_color[data.severity] || '#dc2626');
        d.$wrapper.find('.modal-title').css('color', 'white');
    },

    show_persistent_banner: function(data) {
        // Remove existing banner for this alert
        $(`#emergency-banner-${data.alert_id || data.name}`).remove();

        var alert_id = data.alert_id || data.name;
        var severity_color = {
            'Critical': '#dc2626',
            'High': '#ea580c',
            'Medium': '#ca8a04',
            'Low': '#65a30d'
        };

        var banner = $(`
            <div class="emergency-banner" id="emergency-banner-${alert_id}"
                 style="background-color: ${severity_color[data.severity] || '#dc2626'}">
                <div class="emergency-banner-content">
                    <i class="fa fa-exclamation-triangle"></i>
                    <span class="emergency-banner-text">
                        <strong>EMERGENCY:</strong> ${data.title}
                    </span>
                    ${!data.acknowledged ? `
                        <button class="btn btn-sm btn-light acknowledge-banner-btn" data-alert="${alert_id}">
                            Acknowledge
                        </button>
                    ` : ''}
                    <button class="btn btn-sm btn-link view-details-btn" data-alert="${alert_id}">
                        <i class="fa fa-external-link"></i>
                    </button>
                    <button class="btn btn-sm btn-link dismiss-banner-btn" data-alert="${alert_id}"
                            title="Dismiss" style="color:white;font-size:16px;line-height:1;padding:0 4px;">
                        &times;
                    </button>
                </div>
            </div>
        `);

        banner.find('.acknowledge-banner-btn').on('click', function() {
            university_erp.emergency.acknowledge_alert($(this).data('alert'));
        });

        banner.find('.view-details-btn').on('click', function() {
            frappe.set_route('Form', 'Emergency Alert', $(this).data('alert'));
        });

        banner.find('.dismiss-banner-btn').on('click', function() {
            university_erp.emergency.dismiss_alert($(this).data('alert'));
        });

        $('body').prepend(banner);

        // Add banner styles
        if (!$('#emergency-banner-styles').length) {
            $('head').append(`
                <style id="emergency-banner-styles">
                    .emergency-banner {
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        z-index: 10000;
                        padding: 10px 20px;
                        color: white;
                        animation: banner-pulse 2s infinite;
                    }
                    .emergency-banner-content {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 15px;
                    }
                    .emergency-banner-text {
                        flex: 1;
                        text-align: center;
                    }
                    @keyframes banner-pulse {
                        0%, 100% { opacity: 1; }
                        50% { opacity: 0.8; }
                    }
                </style>
            `);
        }
    },

    show_resolved: function(data) {
        // Remove overlay
        $(`#emergency-overlay-${data.alert_id}`).fadeOut(function() {
            $(this).remove();
        });

        // Update banner
        $(`#emergency-banner-${data.alert_id}`).css('background-color', '#22c55e')
            .find('.emergency-banner-text').html(`
                <strong>ALL CLEAR:</strong> ${data.all_clear_message || 'Emergency has been resolved.'}
            `);

        // Remove banner after 30 seconds
        setTimeout(function() {
            $(`#emergency-banner-${data.alert_id}`).fadeOut(function() {
                $(this).remove();
            });
        }, 30000);

        // Show notification
        frappe.show_alert({
            message: `Emergency resolved: ${data.all_clear_message || 'All Clear'}`,
            indicator: 'green'
        }, 10);
    },

    dismiss_alert: function(alert_id) {
        $(`#emergency-overlay-${alert_id}`).fadeOut(function() {
            $(this).remove();
        });
        $(`#emergency-banner-${alert_id}`).fadeOut(function() {
            $(this).remove();
        });

        // Remove from active alerts
        var idx = this.active_alerts.indexOf(alert_id);
        if (idx > -1) {
            this.active_alerts.splice(idx, 1);
        }
    },

    acknowledge_alert: function(alert_id) {
        var self = this;

        // Try to get location
        var location = null;
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                location = `${position.coords.latitude},${position.coords.longitude}`;
            });
        }

        frappe.call({
            method: 'university_erp.university_erp.doctype.emergency_alert.emergency_alert.acknowledge',
            args: {
                alert_name: alert_id,
                location: location,
                status: 'Safe'
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    // Remove fullscreen overlay
                    $(`#emergency-overlay-${alert_id}`).fadeOut(function() {
                        $(this).remove();
                    });

                    // Update banner to show acknowledged
                    $(`#emergency-banner-${alert_id}`).find('.acknowledge-banner-btn').remove();

                    frappe.show_alert({
                        message: 'Alert acknowledged. Stay safe!',
                        indicator: 'green'
                    }, 5);
                }
            }
        });
    },

    play_alert_sound: function() {
        if (!this.audio) {
            // Create audio element with a simple beep
            this.audio = new Audio('data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU...');
        }
        this.audio.play().catch(function() {
            // Audio autoplay might be blocked
            console.log('Emergency audio blocked by browser');
        });
    },

    call_campus_security: function() {
        // Fetch campus security number from settings
        frappe.call({
            method: 'university_erp.university_erp.doctype.emergency_alert.emergency_alert.get_emergency_contacts',
            callback: function(r) {
                if (r.message && r.message.campus_security) {
                    window.location.href = 'tel:' + r.message.campus_security;
                } else {
                    frappe.msgprint({
                        title: __('Campus Security'),
                        message: __('Campus security number not configured. Please contact administration.'),
                        indicator: 'orange'
                    });
                }
            }
        });
    },

    show_emergency_contacts_modal: function() {
        var self = this;

        frappe.call({
            method: 'university_erp.university_erp.doctype.emergency_alert.emergency_alert.get_emergency_contacts',
            callback: function(r) {
                var contacts = r.message || {};

                var d = new frappe.ui.Dialog({
                    title: __('Emergency Contacts'),
                    fields: [
                        {
                            fieldtype: 'HTML',
                            options: `
                                <div class="emergency-contacts-modal">
                                    <div class="contact-grid">
                                        <div class="contact-card">
                                            <div class="contact-icon" style="background: #dc2626;">
                                                <i class="fa fa-phone"></i>
                                            </div>
                                            <div class="contact-info">
                                                <strong>Police</strong>
                                                <a href="tel:100">100</a>
                                            </div>
                                        </div>
                                        <div class="contact-card">
                                            <div class="contact-icon" style="background: #ea580c;">
                                                <i class="fa fa-fire-extinguisher"></i>
                                            </div>
                                            <div class="contact-info">
                                                <strong>Fire</strong>
                                                <a href="tel:101">101</a>
                                            </div>
                                        </div>
                                        <div class="contact-card">
                                            <div class="contact-icon" style="background: #059669;">
                                                <i class="fa fa-ambulance"></i>
                                            </div>
                                            <div class="contact-info">
                                                <strong>Ambulance</strong>
                                                <a href="tel:102">102</a>
                                            </div>
                                        </div>
                                        <div class="contact-card">
                                            <div class="contact-icon" style="background: #2563eb;">
                                                <i class="fa fa-shield"></i>
                                            </div>
                                            <div class="contact-info">
                                                <strong>Campus Security</strong>
                                                <a href="tel:${contacts.campus_security || ''}">${contacts.campus_security || 'Not configured'}</a>
                                            </div>
                                        </div>
                                        ${contacts.control_room ? `
                                        <div class="contact-card">
                                            <div class="contact-icon" style="background: #7c3aed;">
                                                <i class="fa fa-building"></i>
                                            </div>
                                            <div class="contact-info">
                                                <strong>Control Room</strong>
                                                <a href="tel:${contacts.control_room}">${contacts.control_room}</a>
                                            </div>
                                        </div>
                                        ` : ''}
                                        ${contacts.medical_center ? `
                                        <div class="contact-card">
                                            <div class="contact-icon" style="background: #dc2626;">
                                                <i class="fa fa-medkit"></i>
                                            </div>
                                            <div class="contact-info">
                                                <strong>Medical Center</strong>
                                                <a href="tel:${contacts.medical_center}">${contacts.medical_center}</a>
                                            </div>
                                        </div>
                                        ` : ''}
                                    </div>
                                </div>
                                <style>
                                    .emergency-contacts-modal .contact-grid {
                                        display: grid;
                                        grid-template-columns: repeat(2, 1fr);
                                        gap: 16px;
                                        padding: 10px;
                                    }
                                    .emergency-contacts-modal .contact-card {
                                        display: flex;
                                        align-items: center;
                                        gap: 12px;
                                        padding: 12px;
                                        background: var(--bg-color, #f9fafb);
                                        border-radius: 8px;
                                    }
                                    .emergency-contacts-modal .contact-icon {
                                        width: 40px;
                                        height: 40px;
                                        border-radius: 50%;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        color: white;
                                    }
                                    .emergency-contacts-modal .contact-info strong {
                                        display: block;
                                        font-size: 13px;
                                        color: var(--text-muted);
                                    }
                                    .emergency-contacts-modal .contact-info a {
                                        font-size: 16px;
                                        font-weight: 600;
                                        color: var(--text-color);
                                    }
                                </style>
                            `
                        }
                    ]
                });

                d.show();
            }
        });
    },

    add_styles: function() {
        $('head').append(`
            <style id="emergency-alert-styles">
                .emergency-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(220, 38, 38, 0.95);
                    z-index: 100000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    animation: emergency-pulse 1s infinite;
                }

                @keyframes emergency-pulse {
                    0%, 100% { background: rgba(220, 38, 38, 0.95); }
                    50% { background: rgba(185, 28, 28, 0.95); }
                }

                .emergency-content {
                    text-align: center;
                    color: white;
                    max-width: 600px;
                    padding: 40px;
                }

                .emergency-icon {
                    margin-bottom: 20px;
                    animation: icon-shake 0.5s infinite;
                }

                @keyframes icon-shake {
                    0%, 100% { transform: translateX(0); }
                    25% { transform: translateX(-5px); }
                    75% { transform: translateX(5px); }
                }

                .emergency-title {
                    font-size: 36px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                }

                .emergency-type {
                    font-size: 24px;
                    margin-bottom: 20px;
                    background: rgba(0,0,0,0.2);
                    padding: 5px 20px;
                    border-radius: 4px;
                    display: inline-block;
                }

                .emergency-message {
                    font-size: 18px;
                    line-height: 1.6;
                    margin-bottom: 20px;
                }

                .emergency-instructions {
                    background: rgba(0,0,0,0.2);
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    text-align: left;
                }

                .emergency-instructions h4 {
                    margin-bottom: 10px;
                }

                .emergency-actions {
                    margin-top: 30px;
                }

                .emergency-actions .btn {
                    padding: 15px 40px;
                    font-size: 18px;
                }

                .emergency-modal-content h4 {
                    color: #dc2626;
                    margin-bottom: 15px;
                }

                .emergency-contacts {
                    background: rgba(0,0,0,0.3);
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }

                .emergency-contacts h4 {
                    margin-bottom: 15px;
                    font-size: 16px;
                }

                .emergency-contacts .contact-list {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 10px;
                }

                .emergency-contact-btn {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 12px 16px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 6px;
                    color: white;
                    text-decoration: none;
                    font-size: 14px;
                    transition: background 0.2s;
                }

                .emergency-contact-btn:hover {
                    background: rgba(255,255,255,0.3);
                    color: white;
                    text-decoration: none;
                }

                .emergency-contact-btn i {
                    font-size: 18px;
                }

                @media (max-width: 480px) {
                    .emergency-contacts .contact-list {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        `);
    }
};

// Initialize on page ready
$(document).ready(function() {
    university_erp.emergency.init();
});
