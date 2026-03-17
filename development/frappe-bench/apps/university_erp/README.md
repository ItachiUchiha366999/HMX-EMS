# University ERP

Comprehensive University Management System built on Frappe Framework.

## Overview

University ERP is a specialized application that extends Frappe Education with comprehensive university-specific features including:

- **Academics**: CBCS-based program and course management
- **Admissions**: Merit-based admission process with entrance exam integration
- **Student Information System**: Complete student lifecycle management
- **Examinations**: 10-point grading system with SGPA/CGPA calculation
- **University Finance**: Fee management with scholarships and penalties
- **University HR**: Faculty management, workload tracking, performance evaluation, payroll integration
- **Extended Modules**: Hostel, Transport, Library, Placement

## Architecture

This app uses a hybrid architecture:
- Extends Frappe Education DocTypes (Student, Program, Course, etc.) via override classes
- Integrates with ERPNext for finance (GL entries, payments)
- Integrates with Frappe HRMS for employee management
- Adds university-specific DocTypes and workflows

## Dependencies

- Frappe Framework v15+
- ERPNext v15+
- Frappe HRMS v15+
- Frappe Education v15+

## Installation

```bash
# Get the app
bench get-app university_erp

# Install on site
bench --site [your-site] install-app university_erp
```

## License

MIT
