# ✅ Auto-Redirect Fix Complete

## Root Cause Analysis

The student login was redirecting to `/app/erpnext-settings` instead of `/student_portal` due to **three critical issues**:

### 1. **User Type Issue** ❌→✅ FIXED
- **Problem:** Student user was set as "System User" instead of "Website User"
- **Impact:** Frappe's `auth.py` redirects System Users to desk, Website Users to portal
- **Fix:** Changed user type via SQL:
  ```sql
  UPDATE tabUser SET user_type = 'Website User' WHERE name = 'student@test.edu'
  ```
- **Verification:** ✅ `user_type: Website User`

### 2. **Cached `role_home_page` Hook** ❌→✅ FIXED
- **Problem:** Old bytecode cache kept `role_home_page = {'Student': 'student_portal'}` active
- **Impact:** Frappe tried to find a Workspace named "student_portal" (doesn't exist)
- **Fix:**
  - Removed all Python bytecode cache files
  - Ran `bench clear-cache`
  - Commented out `role_home_page` in hooks.py
- **Verification:** ✅ `role_home_page hooks: []` (empty)

### 3. **Return Value Format** ❌→✅ FIXED
- **Problem:** Function returned `/student_portal` but Frappe adds `/` automatically
- **Impact:** Could result in `//student_portal` redirect
- **Fix:** Changed return value from `"/student_portal"` to `"student_portal"` (no leading slash)
- **Code:**
  ```python
  def get_website_user_home_page(user):
      if "Student" in roles:
          return "student_portal"  # No leading slash
  ```
- **Verification:** ✅ `get_home_page()` returns `student_portal`, final redirect: `/student_portal`

---

## Fixes Applied

### File: [utils.py:267-294](/workspace/development/frappe-bench/apps/university_erp/university_erp/utils.py#L267-L294)

```python
def get_website_user_home_page(user):
    """
    Get home page for website user based on role.

    Returns:
        str: URL path to redirect to (WITHOUT leading slash - Frappe adds it)
    """
    try:
        if frappe.db.exists("User", user):
            roles = frappe.get_roles(user)
            if "Student" in roles:
                # Return path without leading slash - Frappe's auth.py adds "/" + get_home_page()
                return "student_portal"
    except Exception as e:
        frappe.log_error(f"Error in get_website_user_home_page: {str(e)}", "Student Redirect")

    return None
```

### File: [hooks.py](/workspace/development/frappe-bench/apps/university_erp/university_erp/hooks.py)

```python
# Role-based Home Pages (COMMENTED OUT - causes Workspace lookup)
# role_home_page = {
# 	"Student": "student_portal",  # This looks for a Workspace, not a portal page
# }

# Website User Home Page (ACTIVE - correct for portal redirect)
get_website_user_home_page = "university_erp.utils.get_website_user_home_page"
```

### Database Update

```sql
UPDATE tabUser SET user_type = 'Website User' WHERE name = 'student@test.edu';
```

### Cache Clearing

```bash
# Clear Python bytecode cache
find apps/university_erp -name "*.pyc" -delete
find apps/university_erp -name "__pycache__" -type d -delete

# Clear Frappe caches
bench clear-cache
bench clear-website-cache

# Restart
bench restart
```

---

## Testing & Verification

### Console Test Results ✅

```python
# User configuration
user_type: Website User
default_workspace: None
roles: ['Student', 'All', 'Guest']

# Redirect logic
get_default_path(): None
get_home_page(): student_portal
Final redirect URL: /student_portal  ✅
```

### How to Test

#### Option 1: Fresh Login (Recommended)

1. **Clear browser data:**
   - Press `Ctrl+Shift+Delete` (Windows/Linux) or `Cmd+Shift+Delete` (Mac)
   - Select "Cookies and other site data"
   - Clear for `localhost:18000`

2. **Or use Incognito/Private window:**
   - `Ctrl+Shift+N` (Chrome) or `Ctrl+Shift+P` (Firefox)

3. **Navigate to:** `http://localhost:18000/login`

4. **Login with:**
   - Email: `student@test.edu`
   - Password: [your password]

5. **Expected result:**
   - ✅ Automatically redirected to `/student_portal`
   - ✅ See Student Portal Dashboard
   - ✅ No manual navigation needed

#### Option 2: Force Logout First

1. **If already logged in, logout completely:**
   ```
   http://localhost:18000/api/method/logout
   ```

2. **Or click logout from desk and clear cookies**

3. **Then follow steps 3-5 from Option 1**

---

## Why the Fix Works

### Frappe's Login Flow (from `frappe/auth.py`)

```python
def set_user_info(self, resume=False):
    if self.info.user_type == "Website User":
        frappe.local.response["message"] = "No App"
        frappe.local.response["home_page"] = get_default_path() or "/" + get_home_page()
    else:  # System User
        frappe.local.response["message"] = "Logged In"
        # Redirects to desk/workspace
```

**Before Fix:**
- `user_type = "System User"` → Redirected to desk
- `role_home_page` tried to find Workspace → Failed, used default

**After Fix:**
- `user_type = "Website User"` → Uses `get_home_page()` ✅
- `get_home_page()` calls our hook → Returns `"student_portal"` ✅
- Frappe constructs: `"/" + "student_portal"` = `"/student_portal"` ✅

---

## Fallback: JavaScript Redirect

As a safety net, [student_redirect.js](/workspace/development/frappe-bench/apps/university_erp/university_erp/public/js/student_redirect.js) provides client-side redirect if server-side fails:

```javascript
// Redirects from /app, /app/, /desk, /app/home to /student_portal
if (hasStudentRole() && shouldRedirect()) {
    window.location.replace('/student_portal');
}
```

This catches edge cases where the server redirect doesn't fire.

---

## Troubleshooting

### Issue: Still redirecting to `/app/erpnext-settings`

**Cause:** Browser cached the old session/redirect

**Solution:**
1. Clear browser cookies for `localhost:18000`
2. Use Incognito mode
3. Hard refresh: `Ctrl+Shift+R`
4. Or visit: `http://localhost:18000/api/method/logout` then login again

### Issue: "403 Forbidden" on `/app/erpnext-settings`

**Expected behavior!** This means:
- ✅ Student user (Website User) cannot access desk pages
- ✅ Redirect should happen before reaching this page
- ✅ If you see this, clear cookies and login fresh

### Issue: JavaScript redirect not working

**Check console logs:**
- Should see: `[Student Redirect] ✅ Student role detected - REDIRECTING to /student_portal`
- If not, check `frappe.boot.user.roles` includes 'Student'

---

## Summary

| Component | Before | After |
|-----------|--------|-------|
| **User Type** | System User ❌ | Website User ✅ |
| **role_home_page hook** | Active (cached) ❌ | Commented out ✅ |
| **Return value** | `/student_portal` ❌ | `student_portal` ✅ |
| **Cache** | Stale bytecode ❌ | Cleared ✅ |
| **Login redirect** | `/app/erpnext-settings` ❌ | `/student_portal` ✅ |

---

## Files Modified

1. ✅ [utils.py:267-294](/workspace/development/frappe-bench/apps/university_erp/university_erp/utils.py#L267-L294) - Fixed return value
2. ✅ [hooks.py](/workspace/development/frappe-bench/apps/university_erp/university_erp/hooks.py) - Commented out `role_home_page`
3. ✅ Database - Updated user type to Website User
4. ✅ Cache - Cleared all Python and Frappe caches

---

**Status:** ✅ **COMPLETE**

**Test:** Logout and login as `student@test.edu` - you will be automatically redirected to `/student_portal`

**Date Fixed:** January 4, 2026

---

*Note: If the issue persists after clearing cookies, restart the bench with `bench restart` to ensure all changes are loaded.*
