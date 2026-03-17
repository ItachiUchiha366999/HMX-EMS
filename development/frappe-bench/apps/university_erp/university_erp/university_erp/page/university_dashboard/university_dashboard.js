frappe.pages['university-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('University Dashboard'),
        single_column: true
    });

    new UniversityDashboard(page);
};

class UniversityDashboard {
    constructor(page) {
        this.page = page;
        this.make();
    }

    make() {
        this.$container = $('<div class="university-dashboard p-3"></div>').appendTo(this.page.body);

        // Add refresh button
        this.page.set_primary_action(__('Refresh'), () => this.load_data(), 'refresh');

        this.load_data();
    }

    load_data() {
        this.$container.html(`
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">${__('Loading...')}</span>
                </div>
                <p class="mt-2 text-muted">${__('Loading dashboard data...')}</p>
            </div>
        `);

        frappe.call({
            method: 'university_erp.university_erp.page.university_dashboard.university_dashboard.get_dashboard_data',
            callback: (r) => {
                if (r.message) {
                    this.render(r.message);
                }
            },
            error: () => {
                this.$container.html(`
                    <div class="alert alert-danger">
                        ${__('Error loading dashboard data. Please try again.')}
                    </div>
                `);
            }
        });
    }

    render(data) {
        this.$container.html(`
            <!-- Summary Cards Row 1 -->
            <div class="row mb-4">
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="dashboard-stat-card bg-primary text-white">
                        <div class="stat-icon">
                            <i class="fa fa-users"></i>
                        </div>
                        <div class="stat-content">
                            <h3 class="stat-number">${data.students.total || 0}</h3>
                            <p class="stat-label">${__('Total Students')}</p>
                            <small>${__('New this month')}: ${data.students.new_this_month || 0}</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="dashboard-stat-card bg-success text-white">
                        <div class="stat-icon">
                            <i class="fa fa-chalkboard-teacher"></i>
                        </div>
                        <div class="stat-content">
                            <h3 class="stat-number">${data.hr.faculty_count || 0}</h3>
                            <p class="stat-label">${__('Faculty Members')}</p>
                            <small>${__('Staff')}: ${data.hr.staff_count || 0}</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="dashboard-stat-card bg-info text-white">
                        <div class="stat-icon">
                            <i class="fa fa-rupee-sign"></i>
                        </div>
                        <div class="stat-content">
                            <h3 class="stat-number">${data.finance.collection_rate}%</h3>
                            <p class="stat-label">${__('Fee Collection Rate')}</p>
                            <small>${__('Outstanding')}: ₹${this.formatCurrency(data.finance.total_outstanding)}</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="dashboard-stat-card bg-warning text-white">
                        <div class="stat-icon">
                            <i class="fa fa-briefcase"></i>
                        </div>
                        <div class="stat-content">
                            <h3 class="stat-number">${data.placements.students_placed || 0}</h3>
                            <p class="stat-label">${__('Students Placed')}</p>
                            <small>${__('Avg Package')}: ₹${data.placements.avg_package || 0} LPA</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Summary Cards Row 2 -->
            <div class="row mb-4">
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="dashboard-stat-card bg-secondary text-white">
                        <div class="stat-icon">
                            <i class="fa fa-book"></i>
                        </div>
                        <div class="stat-content">
                            <h3 class="stat-number">${data.academics.active_courses || 0}</h3>
                            <p class="stat-label">${__('Active Courses')}</p>
                            <small>${__('Attendance')}: ${data.academics.avg_attendance}%</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="dashboard-stat-card bg-dark text-white">
                        <div class="stat-icon">
                            <i class="fa fa-building"></i>
                        </div>
                        <div class="stat-content">
                            <h3 class="stat-number">${data.hostel.occupancy_rate}%</h3>
                            <p class="stat-label">${__('Hostel Occupancy')}</p>
                            <small>${__('Available')}: ${data.hostel.available || 0} beds</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="dashboard-stat-card" style="background: #6f42c1; color: white;">
                        <div class="stat-icon">
                            <i class="fa fa-book-reader"></i>
                        </div>
                        <div class="stat-content">
                            <h3 class="stat-number">${data.library.books_issued || 0}</h3>
                            <p class="stat-label">${__('Books Issued')}</p>
                            <small>${__('Overdue')}: ${data.library.overdue_books || 0}</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="dashboard-stat-card" style="background: #fd7e14; color: white;">
                        <div class="stat-icon">
                            <i class="fa fa-user-graduate"></i>
                        </div>
                        <div class="stat-content">
                            <h3 class="stat-number">${data.admissions.total_applications || 0}</h3>
                            <p class="stat-label">${__('Applications')}</p>
                            <small>${__('Pending')}: ${data.admissions.pending || 0}</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts Row -->
            <div class="row mb-4">
                <div class="col-md-6 mb-3">
                    <div class="chart-container card">
                        <div class="card-header">
                            <h6 class="mb-0">${__('Fee Collection Trend')}</h6>
                        </div>
                        <div class="card-body">
                            <div id="fee-chart" style="height: 250px;"></div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="chart-container card">
                        <div class="card-header">
                            <h6 class="mb-0">${__('Students by Program')}</h6>
                        </div>
                        <div class="card-body">
                            <div id="program-chart" style="height: 250px;"></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-6 mb-3">
                    <div class="chart-container card">
                        <div class="card-header">
                            <h6 class="mb-0">${__('Faculty by Department')}</h6>
                        </div>
                        <div class="card-body">
                            <div id="dept-chart" style="height: 250px;"></div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="chart-container card">
                        <div class="card-header">
                            <h6 class="mb-0">${__('Admission Status')}</h6>
                        </div>
                        <div class="card-body">
                            <div id="admission-chart" style="height: 250px;"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">${__('Quick Actions')}</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-2 col-sm-4 col-6 mb-2 text-center">
                                    <a href="/app/student" class="btn btn-outline-primary btn-block">
                                        <i class="fa fa-users d-block mb-1"></i>
                                        ${__('Students')}
                                    </a>
                                </div>
                                <div class="col-md-2 col-sm-4 col-6 mb-2 text-center">
                                    <a href="/app/fees" class="btn btn-outline-success btn-block">
                                        <i class="fa fa-rupee-sign d-block mb-1"></i>
                                        ${__('Fees')}
                                    </a>
                                </div>
                                <div class="col-md-2 col-sm-4 col-6 mb-2 text-center">
                                    <a href="/app/teaching-assignment" class="btn btn-outline-info btn-block">
                                        <i class="fa fa-chalkboard d-block mb-1"></i>
                                        ${__('Assignments')}
                                    </a>
                                </div>
                                <div class="col-md-2 col-sm-4 col-6 mb-2 text-center">
                                    <a href="/app/placement-drive" class="btn btn-outline-warning btn-block">
                                        <i class="fa fa-briefcase d-block mb-1"></i>
                                        ${__('Placements')}
                                    </a>
                                </div>
                                <div class="col-md-2 col-sm-4 col-6 mb-2 text-center">
                                    <a href="/app/hostel-allocation" class="btn btn-outline-secondary btn-block">
                                        <i class="fa fa-building d-block mb-1"></i>
                                        ${__('Hostel')}
                                    </a>
                                </div>
                                <div class="col-md-2 col-sm-4 col-6 mb-2 text-center">
                                    <a href="/app/library-transaction" class="btn btn-outline-dark btn-block">
                                        <i class="fa fa-book d-block mb-1"></i>
                                        ${__('Library')}
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `);

        this.render_charts(data);
    }

    render_charts(data) {
        // Fee Collection Trend
        if (data.finance.monthly_trend && data.finance.monthly_trend.length) {
            new frappe.Chart("#fee-chart", {
                data: {
                    labels: data.finance.monthly_trend.map(d => d.month),
                    datasets: [{
                        name: __("Collected"),
                        values: data.finance.monthly_trend.map(d => d.collected || 0)
                    }]
                },
                type: 'line',
                colors: ['#5e64ff'],
                lineOptions: {
                    regionFill: 1
                },
                axisOptions: {
                    xIsSeries: true
                }
            });
        } else {
            $('#fee-chart').html(`<p class="text-muted text-center py-5">${__('No fee data available')}</p>`);
        }

        // Students by Program
        if (data.students.by_program && data.students.by_program.length) {
            new frappe.Chart("#program-chart", {
                data: {
                    labels: data.students.by_program.map(d => (d.program || 'Unknown').substring(0, 20)),
                    datasets: [{
                        name: __("Students"),
                        values: data.students.by_program.map(d => d.count)
                    }]
                },
                type: 'bar',
                colors: ['#28a745'],
                barOptions: {
                    spaceRatio: 0.3
                }
            });
        } else {
            $('#program-chart').html(`<p class="text-muted text-center py-5">${__('No program data available')}</p>`);
        }

        // Faculty by Department
        if (data.hr.by_department && data.hr.by_department.length) {
            new frappe.Chart("#dept-chart", {
                data: {
                    labels: data.hr.by_department.map(d => (d.department || 'N/A').substring(0, 15)),
                    datasets: [{
                        name: __("Faculty"),
                        values: data.hr.by_department.map(d => d.count)
                    }]
                },
                type: 'pie',
                colors: ['#5e64ff', '#28a745', '#ffc107', '#dc3545', '#17a2b8', '#6c757d', '#fd7e14', '#6f42c1']
            });
        } else {
            $('#dept-chart').html(`<p class="text-muted text-center py-5">${__('No department data available')}</p>`);
        }

        // Admission Status
        if (data.admissions.total_applications > 0) {
            new frappe.Chart("#admission-chart", {
                data: {
                    labels: [__('Pending'), __('Approved'), __('Admitted'), __('Rejected')],
                    datasets: [{
                        name: __("Applications"),
                        values: [
                            data.admissions.pending || 0,
                            data.admissions.approved || 0,
                            data.admissions.admitted || 0,
                            data.admissions.rejected || 0
                        ]
                    }]
                },
                type: 'donut',
                colors: ['#ffc107', '#28a745', '#5e64ff', '#dc3545']
            });
        } else {
            $('#admission-chart').html(`<p class="text-muted text-center py-5">${__('No admission data available')}</p>`);
        }
    }

    formatCurrency(value) {
        if (!value) return '0';
        if (value >= 10000000) {
            return (value / 10000000).toFixed(2) + ' Cr';
        } else if (value >= 100000) {
            return (value / 100000).toFixed(2) + ' L';
        } else if (value >= 1000) {
            return (value / 1000).toFixed(2) + ' K';
        }
        return value.toFixed(2);
    }
}
