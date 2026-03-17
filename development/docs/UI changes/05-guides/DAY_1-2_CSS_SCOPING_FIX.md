# Day 1-2: CSS Scoping Fix - Detailed Task List

## 🎯 Goal
Fix CSS scoping issue where portal styles are affecting ERPNext desk UI

**Duration:** 1-2 days
**Priority:** CRITICAL
**Status:** ⬜ Not Started

---

## 📋 Task Checklist

### Phase 4 - Section 1: CSS Scoping Fix

#### Task 1: Audit Current CSS Setup
- [ ] **1.1** Check `hooks.py` for `web_include_css` entries
  - File: `/frappe-bench/apps/university_erp/university_erp/hooks.py`
  - Look for portal CSS files being included globally
  - Document current entries

- [ ] **1.2** Check `app_include_css` entries (these are OK for desk)
  - These should remain for desk UI customizations
  - Document current entries

- [ ] **1.3** List all portal CSS files
  - [ ] `/public/css/theme/variables.css`
  - [ ] `/public/css/theme/portal.css`
  - [ ] `/public/css/theme/base.css` (if exists)
  - [ ] `/public/css/theme/components.css` (if exists)
  - [ ] Any other portal-specific CSS files

- [ ] **1.4** Test current issue
  - [ ] Login to ERPNext desk
  - [ ] Navigate to any DocType list/form
  - [ ] Document what styles are broken
  - [ ] Take screenshots of issues

**Output:** Document with current setup and issues

---

#### Task 2: Update portal_base.html with CSS Links
- [ ] **2.1** Open `/templates/includes/portal_base.html`
  - File: `/frappe-bench/apps/university_erp/university_erp/templates/includes/portal_base.html`

- [ ] **2.2** Add CSS links in `<head>` section
  ```html
  <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{% block title %}Dashboard{% endblock %} | Student Portal</title>

      <!-- Fonts -->
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

      <!-- Icons -->
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

      <!-- SCOPED PORTAL CSS - Only loads on portal pages -->
      <link rel="stylesheet" href="/assets/university_erp/css/theme/variables.css">
      <link rel="stylesheet" href="/assets/university_erp/css/theme/portal.css">

      {% block head %}{% endblock %}
  </head>
  ```

- [ ] **2.3** Add wrapper class to `<body>`
  ```html
  <body class="student-portal-body">
      <!-- rest of template -->
  </body>
  ```

- [ ] **2.4** Save file

**Output:** Updated `portal_base.html`

---

#### Task 3: Update hooks.py
- [ ] **3.1** Open `hooks.py`
  - File: `/frappe-bench/apps/university_erp/university_erp/hooks.py`

- [ ] **3.2** Find `web_include_css` section

- [ ] **3.3** Remove portal CSS entries
  - Remove `/assets/university_erp/css/theme/variables.css`
  - Remove `/assets/university_erp/css/theme/portal.css`
  - Remove any other portal-specific CSS

- [ ] **3.4** Keep only desk-specific CSS (if any)
  ```python
  # CORRECT - Portal CSS removed
  app_include_css = [
      "/assets/university_erp/css/university_erp.css",  # Desk only
  ]

  # Portal CSS removed - loaded via portal_base.html instead
  web_include_css = [
      # Empty or only non-portal CSS
  ]
  ```

- [ ] **3.5** Save file

**Output:** Updated `hooks.py`

---

#### Task 4: Prefix CSS Selectors (Additional Safety)
- [ ] **4.1** Open `/public/css/theme/portal.css`

- [ ] **4.2** Add wrapper to beginning of file
  ```css
  /**
   * EduPortal - Portal Styles
   * Scoped to .student-portal-body to prevent conflicts with desk UI
   */

  /* All styles wrapped in .student-portal-body */
  ```

- [ ] **4.3** Wrap critical selectors
  - Option A: Manually prefix key selectors
    ```css
    /* BEFORE */
    .card { ... }
    .btn-primary { ... }

    /* AFTER */
    .student-portal-body .card { ... }
    .student-portal-body .btn-primary { ... }
    ```

  - Option B: Use CSS nesting (if supported)
    ```css
    .student-portal-body {
        .card { ... }
        .btn-primary { ... }
    }
    ```

- [ ] **4.4** Focus on high-risk selectors first
  - [ ] `.card`
  - [ ] `.btn-primary`, `.btn-secondary`
  - [ ] `.form-control`
  - [ ] `.modal`
  - [ ] `.table`, `.data-table`
  - [ ] Common utility classes

- [ ] **4.5** Save file

**Output:** Updated `portal.css` with scoped selectors

---

#### Task 5: Build and Deploy
- [ ] **5.1** Clear cache
  ```bash
  cd /workspace/development/frappe-bench
  bench clear-cache
  ```

- [ ] **5.2** Build assets
  ```bash
  bench build --app university_erp
  ```

- [ ] **5.3** Restart server
  ```bash
  bench restart
  ```

- [ ] **5.4** Clear browser cache
  - Press Ctrl+Shift+R (or Cmd+Shift+R on Mac)
  - Or open DevTools > Application > Clear storage

**Output:** Deployed changes

---

#### Task 6: Test Portal Pages
- [ ] **6.1** Login as student user

- [ ] **6.2** Test each portal page loads correctly
  - [ ] `/student-portal` - Dashboard
  - [ ] `/student-portal/profile` - Profile
  - [ ] `/student-portal/attendance` - Attendance
  - [ ] `/student-portal/academics` - Academics
  - [ ] `/student-portal/assignments` - Assignments
  - [ ] `/student-portal/results` - Results
  - [ ] `/student-portal/fees` - Fees
  - [ ] `/student-portal/library` - Library
  - [ ] `/student-portal/timetable` - Timetable
  - [ ] `/student-portal/notifications` - Notifications
  - [ ] `/student-portal/certificates` - Certificates
  - [ ] `/student-portal/grievances` - Grievances

- [ ] **6.3** Verify CSS is applied
  - [ ] Check sidebar styling
  - [ ] Check card styles
  - [ ] Check button colors
  - [ ] Check typography (Inter font)
  - [ ] Check colors match design system

- [ ] **6.4** Test responsive design
  - [ ] Desktop (> 1024px)
  - [ ] Tablet (768px - 1024px)
  - [ ] Mobile (< 768px)

- [ ] **6.5** Check browser console for errors
  - Open DevTools (F12)
  - Look for CSS loading errors
  - Look for JavaScript errors

**Output:** Confirmed portal styling works

---

#### Task 7: Test ERPNext Desk UI
- [ ] **7.1** Login as admin/desk user

- [ ] **7.2** Navigate to key desk pages
  - [ ] Desk home
  - [ ] Student List
  - [ ] Student Form
  - [ ] Course List
  - [ ] Any custom DocType
  - [ ] Settings pages
  - [ ] Reports

- [ ] **7.3** Verify desk styling is UNCHANGED
  - [ ] Cards look normal
  - [ ] Forms look normal
  - [ ] Lists look normal
  - [ ] Buttons have correct ERPNext style
  - [ ] No custom colors bleeding in
  - [ ] Sidebar normal
  - [ ] Navbar normal

- [ ] **7.4** Check specific elements
  - [ ] DocType cards on desk home
  - [ ] Form controls (input, select, etc.)
  - [ ] Action buttons (Save, Submit, Cancel)
  - [ ] Sidebar menu
  - [ ] Search bar
  - [ ] Filters

- [ ] **7.5** Compare with fresh ERPNext instance (if available)
  - Take screenshots
  - Compare side-by-side

**Output:** Confirmed desk UI unaffected

---

#### Task 8: Cross-Browser Testing
- [ ] **8.1** Test in Chrome/Chromium
  - [ ] Portal pages
  - [ ] Desk pages

- [ ] **8.2** Test in Firefox
  - [ ] Portal pages
  - [ ] Desk pages

- [ ] **8.3** Test in Safari (if Mac available)
  - [ ] Portal pages
  - [ ] Desk pages

- [ ] **8.4** Test in mobile browsers
  - [ ] Chrome mobile
  - [ ] Safari mobile

**Output:** Cross-browser compatibility confirmed

---

#### Task 9: Performance Check
- [ ] **9.1** Check CSS file sizes
  ```bash
  ls -lh /workspace/development/frappe-bench/apps/university_erp/university_erp/public/css/theme/
  ```

- [ ] **9.2** Check page load times
  - Open DevTools > Network tab
  - Reload portal page
  - Check total load time (should be < 2s)
  - Check CSS load time

- [ ] **9.3** Verify CSS caching
  - Reload page
  - Check if CSS loaded from cache (304 status)

**Output:** Performance metrics documented

---

#### Task 10: Documentation & Cleanup
- [ ] **10.1** Update PHASE_4_CSS_NAVIGATION_POLISH.md
  - Mark "CSS Scoping Fix" section as complete
  - Add any notes or deviations from plan

- [ ] **10.2** Update MASTER_CHECKLIST.md
  - Mark CSS scoping tasks as complete

- [ ] **10.3** Document the fix
  - Create notes on what was changed
  - Why it works
  - Any gotchas for future developers

- [ ] **10.4** Commit changes
  ```bash
  git add .
  git commit -m "fix: Scope portal CSS to prevent conflicts with desk UI

  - Updated portal_base.html to include CSS links
  - Removed portal CSS from hooks.py web_include_css
  - Added .student-portal-body wrapper class
  - Prefixed critical CSS selectors
  - Tested portal and desk UI - no conflicts
  "
  ```

**Output:** Changes committed and documented

---

## ✅ Completion Criteria

- [ ] Portal CSS loads only on portal pages
- [ ] ERPNext desk UI completely unaffected
- [ ] All 13 existing portal pages styled correctly
- [ ] No console errors
- [ ] Mobile responsive working
- [ ] Cross-browser compatible
- [ ] Performance acceptable (< 2s load)
- [ ] Changes committed to git

---

## 🚨 Rollback Plan

If issues occur:

1. **Revert hooks.py**
   ```bash
   git checkout hooks.py
   ```

2. **Revert portal_base.html**
   ```bash
   git checkout templates/includes/portal_base.html
   ```

3. **Clear cache and rebuild**
   ```bash
   bench clear-cache
   bench build --app university_erp
   bench restart
   ```

---

## 📝 Notes & Issues

### Issues Encountered
- Document any issues here as you work

### Solutions Applied
- Document solutions here

### Deviations from Plan
- Note any changes to the approach

---

## 🔄 Status Updates

**Day 1 Morning:**
- [ ] Tasks 1-3 complete

**Day 1 Afternoon:**
- [ ] Tasks 4-5 complete

**Day 1 Evening:**
- [ ] Tasks 6-7 complete

**Day 2 Morning:**
- [ ] Tasks 8-9 complete

**Day 2 Afternoon:**
- [ ] Task 10 complete
- [ ] Ready for Phase 1

---

## ⏭️ Next Steps

Once this task list is 100% complete:
- [ ] Update this file status to ✅ Complete
- [ ] Move to Phase 1 task list
- [ ] Start Day 3-14: Examinations & Placements implementation

---

*Last Updated: [Current Date]*
*Status: ⬜ Not Started | ⏳ In Progress | ✅ Complete*
