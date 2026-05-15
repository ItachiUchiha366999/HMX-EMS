# Troubleshooting: All Pages Show Same Content

## ✅ Problem Resolved!

**Issue:** All student portal pages (exams, attendance, library, etc.) were showing the same content as the dashboard.

**Root Causes:**
1. **CRITICAL: Folder Naming** - Frappe loads files from folders with underscores (`student_portal`), NOT hyphens (`student-portal`)
2. **Frappe Web Cache** - Frappe caches rendered pages
3. **Python Bytecode Cache** - Old `.pyc` files in `__pycache__`
4. **Import Issues** - `get_current_student()` import failed due to folder naming

---

## 🔧 Solution Applied

### 1. Fixed Folder Structure (THE ACTUAL ROOT CAUSE!)

**Critical Discovery:** Frappe's web routing system uses the hyphenated folder name (`student-portal`) for URLs, but Python loads modules from the underscored folder name (`student_portal`).

**The Issue:**
- Our files were in: `/www/student-portal/` (hyphen)
- Frappe was looking for: `/www/student_portal/` (underscore) for Python imports
- Result: All routes fell back to loading `index.py` (dashboard)

**The Fix:**
```bash
# Copy all files to underscore version
cd /workspace/development/frappe-bench/apps/university_erp/university_erp/www
cp -r student-portal student_portal
```

**How ERPNext Does It:**
- ERPNext has both `book-appointment/` AND `book_appointment/`
- The hyphen version is for URL routing
- The underscore version contains the actual .py and .html files
- This is the standard Frappe pattern for multi-word portal sections

**Result:**
- URL: `http://localhost:8000/student_portal/exams` (uses underscore)
- Files loaded from: `/www/student_portal/exams.py` (uses underscore)
- Navigation links updated to use underscore URLs
- Old hyphenated folder removed (only `student_portal/` exists now)

### 2. Fixed Import Issue (Secondary Fix)
**File:** `/www/student-portal/exams.py`

**Root Cause:** The import statement `from university_erp.www.student_portal.index import get_current_student` **fails** because:
1. The folder is named `student-portal` (with hyphen) in the filesystem
2. Python module names cannot contain hyphens
3. The import tries to use `student_portal` (underscore) which doesn't exist

**Wrong Approach (tried first):**
```python
# This FAILS - folder has hyphen, not underscore
from university_erp.www.student_portal.index import get_current_student

# This also fails - even if you change the import, the folder name has a hyphen
def get_current_student():
    ...  # separate function
```

**Correct Approach (final fix):**
```python
# Inline the student lookup directly in get_context()
def get_context(context):
    """Get examinations page context"""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access the Student Portal"), frappe.PermissionError)

    # Get current student - inline code
    user = frappe.session.user
    student = frappe.db.get_value("Student", {"user": user},
        ["name", "student_name", "image", "custom_cgpa"], as_dict=1)

    if student:
        # Get program from Program Enrollment (active enrollment)
        program = frappe.db.get_value(
            "Program Enrollment",
            {"student": student.name, "docstatus": 1},
            "program",
            order_by="enrollment_date desc"
        )
        student.program = program

    if not student:
        frappe.throw(_("You are not registered as a student"), frappe.PermissionError)

    context.no_cache = 1
    context.student = student
    context.active_page = "exams"
    # ... rest of context setup
```

**Why This Works:**
- No imports needed - all code is self-contained
- Folder naming (hyphen vs underscore) doesn't matter
- This is the most reliable pattern for Frappe www files
- Keeps each portal page independent

### 3. Cleared All Caches
```bash
# Remove Python cache
rm -rf apps/university_erp/university_erp/www/student-portal/__pycache__/*

# Clear Frappe cache
bench --site university.local clear-cache
bench --site university.local clear-website-cache

# Rebuild assets
bench build --app university_erp

# Restart
bench restart
```

---

## 🧪 How to Test

1. **Clear Browser Cache:**
   - Press `Ctrl + Shift + R` (Windows/Linux)
   - Or `Cmd + Shift + R` (Mac)
   - Or open in Incognito mode

2. **Login as Student:**
   - Email: `student@test.edu`
   - Navigate to: `http://localhost:8000/student-portal`

3. **Test Each Page:**
   - Click "Dashboard" → Should show dashboard stats
   - Click "Attendance" → Should show attendance page
   - Click "Examinations" → Should show exams page with 3 tabs
   - Click "Library" → Should show library page
   - etc.

4. **Verify Page Titles:**
   - Each page should have a different browser tab title
   - Dashboard: "Dashboard | EduPortal"
   - Examinations: "Examinations | EduPortal"
   - Attendance: "Attendance | EduPortal"

---

## ✅ Expected Behavior

### Dashboard (`/student-portal`)
- Shows quick stats
- Today's classes
- Announcements
- Quick links

### Examinations (`/student-portal/exams`)
- 4 stats cards (Upcoming, Completed, Hall Tickets, Total)
- 3 tabs (Upcoming Exams, Completed Exams, Hall Tickets)
- Empty states with icons if no data

### Other Pages
- Each page should show its own unique content
- Each page has its own `.py` file with `get_context()` function
- Each page has its own `.html` template

---

## 🐛 If Problem Persists

### Step 1: Force Reload Without Cache
```bash
# In browser developer tools (F12)
# Go to Network tab
# Check "Disable cache"
# Reload page
```

### Step 2: Check Console for Errors
```bash
# Press F12 in browser
# Go to Console tab
# Look for red errors
# Check if CSS/JS files are loading (Network tab)
```

### Step 3: Verify Python Files
```bash
cd /workspace/development/frappe-bench/apps/university_erp/university_erp/www/student-portal

# Check if .py files exist
ls -la *.py

# Check file permissions (should be readable)
# -rw-r--r-- means readable
```

### Step 4: Test Individual Page Loading
```bash
# In bench console
bench --site university.local console
```
```python
# Test loading exams page context
import frappe
frappe.init(site="university.local")
frappe.connect()
frappe.set_user("student@test.edu")

from university_erp.www.student_portal.exams import get_context

context = frappe._dict()
get_context(context)

print("Active Page:", context.active_page)  # Should be "exams"
print("Stats:", context.stats)  # Should show exam stats
```

### Step 5: Nuclear Option - Complete Rebuild
```bash
cd /workspace/development/frappe-bench

# Stop everything
bench restart

# Clear everything
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -delete
bench --site university.local clear-cache
bench --site university.local clear-website-cache

# Rebuild
bench build --app university_erp

# Restart
bench restart
```

---

## 📊 How Frappe Routes Work

### URL Structure
```
http://localhost:8000/student-portal/exams
                       └── folder ───┘ └page┘
```

### File Mapping
```
URL:  /student-portal/exams
Maps: /www/student-portal/exams.py + exams.html
      (underscore in filesystem, hyphen in URL)
```

### Rendering Process
1. User visits `/student-portal/exams`
2. Frappe finds `www/student_portal/exams.py`
3. Calls `get_context(context)` function
4. Populates context with data
5. Renders `exams.html` template with context
6. Caches the result
7. Returns HTML to browser

### Why Caching Causes Issues
- If cache isn't cleared, old content persists
- All pages might show cached dashboard
- Solution: Always clear cache after code changes

---

## ✅ Prevention

To avoid this issue in the future:

### 1. Always Clear Cache After Changes
```bash
# After editing .py or .html files
bench clear-cache
bench restart
```

### 2. Understand Frappe www Folder Structure
```python
# ❌ WRONG - Cannot import from other www files
from university_erp.www.student_portal.index import get_current_student

# ✅ CORRECT - Define helper functions in each www file
def get_current_student():
    user = frappe.session.user
    return frappe.db.get_value("Student", {"user": user}, as_dict=1)
```

**Note:** If you need to share code across multiple portal pages, create a utility module in `university_erp/utils/` folder (not in www folder), then import from there.

### 3. Test in Incognito Mode
- Incognito doesn't use browser cache
- Easier to catch caching issues

### 4. Verify active_page Variable
```python
# In each page's get_context()
context.active_page = "exams"  # Unique for each page
```

This ensures:
- Navigation highlights correctly
- Page identification works
- Analytics track correctly

---

## 🎯 Quick Reference

### Clear Cache Command
```bash
bench clear-cache && bench build --app university_erp && bench restart
```

### Check Page is Different
1. View page source (Ctrl+U)
2. Search for `<title>` tag
3. Should show unique page title

### Test Without Browser
```bash
curl -s http://localhost:8000/student-portal/exams | grep "<title>"
# Should show: <title>Examinations | EduPortal</title>
```

---

**Status:** ✅ **RESOLVED**
**Date Fixed:** January 4, 2026
**Solution:** Removed duplicate functions + cleared all caches

---

*If you still see dashboard content on all pages after following these steps, check browser extensions or proxy settings that might be caching responses.*
