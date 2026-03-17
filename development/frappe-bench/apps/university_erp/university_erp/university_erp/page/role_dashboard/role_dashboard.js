frappe.pages['role-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('My Dashboard'),
        single_column: true
    });

    new RoleDashboard(page);
};

class RoleDashboard {
    constructor(page) {
        this.page = page;
        this.make();
    }

    make() {
        this.$container = $('<div class="role-dashboard p-3"></div>').appendTo(this.page.body);
        this.page.set_primary_action(__('Refresh'), () => this.load_data(), 'refresh');
        this.load_data();
    }

    load_data() {
        this.$container.html(`
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2 text-muted">${__('Loading your dashboard...')}</p>
            </div>
        `);

        frappe.call({
            method: 'university_erp.university_erp.page.role_dashboard.role_dashboard.get_role_dashboard_data',
            callback: (r) => {
                if (r.message) {
                    this.render(r.message);
                }
            }
        });
    }

    render(data) {
        if (data.error) {
            this.$container.html(`<div class="alert alert-warning">${data.error}</div>`);
            return;
        }

        switch (data.type) {
            case 'student':
                this.render_student_dashboard(data);
                break;
            case 'faculty':
                this.render_faculty_dashboard(data);
                break;
            case 'admin':
                this.render_admin_dashboard(data);
                break;
            case 'hr':
                this.render_hr_dashboard(data);
                break;
            case 'finance':
                this.render_finance_dashboard(data);
                break;
            default:
                this.render_default_dashboard(data);
        }
    }

    render_student_dashboard(data) {
        this.$container.html(`
            <div class="row mb-4">
                <div class="col-12">
                    <h4>${__('Welcome')}, ${data.student_name}</h4>
                    <p class="text-muted">${data.program || ''}</p>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-primary text-white">
                        <i class="fa fa-chart-line"></i>
                        <h3>${data.cgpa || 'N/A'}</h3>
                        <p>${__('CGPA')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-success text-white">
                        <i class="fa fa-calendar-check"></i>
                        <h3>${data.attendance_rate}%</h3>
                        <p>${__('Attendance')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-danger text-white">
                        <i class="fa fa-rupee-sign"></i>
                        <h3>₹${this.formatNumber(data.pending_fees)}</h3>
                        <p>${__('Pending Fees')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-info text-white">
                        <i class="fa fa-book"></i>
                        <h3>${data.books_borrowed}</h3>
                        <p>${__('Books Borrowed')}</p>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-header"><h6>${__('My Courses')}</h6></div>
                        <div class="card-body">
                            ${data.enrollments.length ? data.enrollments.map(e => `
                                <div class="d-flex justify-content-between border-bottom py-2">
                                    <span>${e.course_name || e.course}</span>
                                </div>
                            `).join('') : `<p class="text-muted">${__('No courses enrolled')}</p>`}
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-header"><h6>${__('Recent Results')}</h6></div>
                        <div class="card-body">
                            ${data.latest_results.length ? data.latest_results.map(r => `
                                <div class="d-flex justify-content-between border-bottom py-2">
                                    <span>${r.course_name || r.course}</span>
                                    <span class="badge bg-primary">${r.grade || 'N/A'}</span>
                                </div>
                            `).join('') : `<p class="text-muted">${__('No results available')}</p>`}
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mt-3">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header"><h6>${__('Quick Actions')}</h6></div>
                        <div class="card-body">
                            <a href="/app/fees?student=${data.student_name}" class="btn btn-outline-primary me-2 mb-2">${__('View Fees')}</a>
                            <a href="/placement" class="btn btn-outline-success me-2 mb-2">${__('Placement Portal')}</a>
                            <a href="/library" class="btn btn-outline-info me-2 mb-2">${__('Library')}</a>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    render_faculty_dashboard(data) {
        this.$container.html(`
            <div class="row mb-4">
                <div class="col-12">
                    <h4>${__('Welcome')}, ${data.employee_name}</h4>
                    <p class="text-muted">${data.department || ''}</p>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-primary text-white">
                        <i class="fa fa-book"></i>
                        <h3>${data.assignments.length}</h3>
                        <p>${__('Assigned Courses')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-success text-white">
                        <i class="fa fa-clock"></i>
                        <h3>${data.total_hours}</h3>
                        <p>${__('Weekly Hours')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-warning text-white">
                        <i class="fa fa-star"></i>
                        <h3>${data.avg_feedback}/5</h3>
                        <p>${__('Avg Feedback')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-info text-white">
                        <i class="fa fa-calendar"></i>
                        <h3>${data.pending_leaves}</h3>
                        <p>${__('Pending Leaves')}</p>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-header"><h6>${__("Today's Schedule")}</h6></div>
                        <div class="card-body">
                            ${data.today_schedule.length ? data.today_schedule.map(s => `
                                <div class="d-flex justify-content-between border-bottom py-2">
                                    <span>${s.course_name}</span>
                                    <span class="text-muted">${s.start_time} - ${s.end_time}</span>
                                </div>
                            `).join('') : `<p class="text-muted">${__('No classes today')}</p>`}
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-header"><h6>${__('Leave Balance')}</h6></div>
                        <div class="card-body">
                            ${data.leave_balance.length ? data.leave_balance.map(l => `
                                <div class="d-flex justify-content-between border-bottom py-2">
                                    <span>${l.leave_type}</span>
                                    <span>${l.total_leaves_allocated - l.total_leaves_taken} / ${l.total_leaves_allocated}</span>
                                </div>
                            `).join('') : `<p class="text-muted">${__('No leave allocation')}</p>`}
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    render_admin_dashboard(data) {
        this.$container.html(`
            <div class="row mb-4">
                <div class="col-12">
                    <h4>${__('Academic Administration Dashboard')}</h4>
                    <p class="text-muted">${__('Current Term')}: ${data.active_term || 'N/A'}</p>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-2 col-sm-6 mb-3">
                    <div class="stat-card bg-primary text-white">
                        <h3>${data.total_students}</h3>
                        <p>${__('Students')}</p>
                    </div>
                </div>
                <div class="col-md-2 col-sm-6 mb-3">
                    <div class="stat-card bg-success text-white">
                        <h3>${data.total_programs}</h3>
                        <p>${__('Programs')}</p>
                    </div>
                </div>
                <div class="col-md-2 col-sm-6 mb-3">
                    <div class="stat-card bg-info text-white">
                        <h3>${data.total_courses}</h3>
                        <p>${__('Courses')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-warning text-white">
                        <h3>${data.pending_applications}</h3>
                        <p>${__('Pending Applications')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-secondary text-white">
                        <h3>${data.recent_enrollments}</h3>
                        <p>${__('New Enrollments')}</p>
                    </div>
                </div>
            </div>
        `);
    }

    render_hr_dashboard(data) {
        this.$container.html(`
            <div class="row mb-4">
                <div class="col-12"><h4>${__('HR Dashboard')}</h4></div>
            </div>
            <div class="row mb-4">
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-primary text-white">
                        <h3>${data.total_employees}</h3>
                        <p>${__('Employees')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-warning text-white">
                        <h3>${data.pending_leaves}</h3>
                        <p>${__('Pending Leaves')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-success text-white">
                        <h3>${data.attendance_today}</h3>
                        <p>${__('Present Today')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-info text-white">
                        <h3>${data.recent_hires}</h3>
                        <p>${__('New Hires')}</p>
                    </div>
                </div>
            </div>
        `);
    }

    render_finance_dashboard(data) {
        this.$container.html(`
            <div class="row mb-4">
                <div class="col-12"><h4>${__('Finance Dashboard')}</h4></div>
            </div>
            <div class="row mb-4">
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-primary text-white">
                        <h3>₹${this.formatNumber(data.total_generated)}</h3>
                        <p>${__('Generated')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-success text-white">
                        <h3>₹${this.formatNumber(data.total_collected)}</h3>
                        <p>${__('Collected')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-danger text-white">
                        <h3>₹${this.formatNumber(data.total_outstanding)}</h3>
                        <p>${__('Outstanding')}</p>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card bg-info text-white">
                        <h3>${data.collection_rate}%</h3>
                        <p>${__('Collection Rate')}</p>
                    </div>
                </div>
            </div>
        `);
    }

    render_default_dashboard(data) {
        this.$container.html(`
            <div class="text-center py-5">
                <h3>${data.welcome_message}</h3>
                <div class="mt-4">
                    ${data.quick_links.map(l => `
                        <a href="${l.link}" class="btn btn-outline-primary m-2">${l.label}</a>
                    `).join('')}
                </div>
            </div>
        `);
    }

    formatNumber(value) {
        if (!value) return '0';
        if (value >= 10000000) return (value / 10000000).toFixed(1) + ' Cr';
        if (value >= 100000) return (value / 100000).toFixed(1) + ' L';
        if (value >= 1000) return (value / 1000).toFixed(1) + ' K';
        return value.toFixed(0);
    }
}
