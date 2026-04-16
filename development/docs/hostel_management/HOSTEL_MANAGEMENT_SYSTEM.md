# Hostel Management System — Complete Specification

> **Product:** Standalone Hostel Management System extracted from the University ERP.
> **Platform:** Frappe Framework 15 + ERPNext 15 (single-tenant deployment per hostel).
> **App:** `hostel_management` (new Frappe app).
> **Scope:** Rooms, allocations, attendance, visitors, maintenance, mess (one-time + subscription), payments (Razorpay), public website, student portal.

---

## 1. System Overview

The Hostel Management System (HMS) is a standalone product that digitises every operational flow of a residential hostel:

- **Administration** — buildings, rooms, mess, staff (warden, admin)
- **Resident lifecycle** — admission, allocation, vacate, transfer
- **Daily operations** — attendance, visitor log, maintenance tickets
- **Mess management** — weekly menu, one-time coupons, recurring subscriptions
- **Billing & payments** — hostel invoices, Razorpay checkout, receipts, refunds
- **Public-facing web** — landing page, terms of service, login gateway
- **Student portal** — self-service payments, menu, room info, maintenance requests, subscription management

The system is extracted from an existing, battle-tested module inside `university_erp` but ships as a **fresh Frappe app** with only frappe + erpnext as dependencies. Education/HRMS are dropped.

### 1.1 High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                        PUBLIC WEB                                   │
│     Landing (/) ── ToS (/terms-of-service) ── Login (/login)       │
└────────────────────────────┬───────────────────────────────────────┘
                             │  after login
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                   STUDENT PORTAL (Vue 3 SPA)                        │
│   Dashboard · Room · Mess · Payments · Maintenance · Profile        │
└────────────────────────────┬───────────────────────────────────────┘
                             │  REST / RPC (frappe.call)
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                  FRAPPE BACKEND — hostel_management app             │
│                                                                     │
│  ┌──────────────┐  ┌────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Hostel Core  │  │  Mess      │  │  Payments    │  │ Portal API│ │
│  │ (Building,   │  │ (Menu,     │  │ (Invoice,    │  │ (/api/    │ │
│  │  Room,       │  │  Subscript-│  │  Razorpay    │  │  method/  │ │
│  │  Allocation, │  │  ion, Meal │  │  Webhook,    │  │  hostel_  │ │
│  │  Attendance, │  │  Coupon)   │  │  Payment     │  │  manage-  │ │
│  │  Visitor)    │  │            │  │  Entry)      │  │  ment…)   │ │
│  └──────────────┘  └────────────┘  └──────────────┘  └───────────┘ │
│                                                                     │
│       Scheduler: generate_due_invoices · mark_past_due ·            │
│                  auto_checkout_visitors · renew_subscriptions       │
└────────────────────────────┬───────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                MariaDB + Redis + Razorpay (external)                │
└────────────────────────────────────────────────────────────────────┘
```

### 1.2 Personas

| Persona | Role | Capabilities |
|---------|------|--------------|
| **Hostel Admin** | Full-access owner/manager | All CRUD, settings, reports |
| **Warden** | Daily operations staff | Allocations, attendance, visitors, maintenance, no settings |
| **Mess Incharge** | Mess manager | Menu, subscriptions, meal coupons, mess attendance |
| **Hostel Resident** | Student/resident | Self-service portal: view room, pay, subscribe, raise tickets |

---

## 2. Module Inventory & DocTypes

### 2.1 Core Hostel DocTypes (carried over from `university_hostel`)

| # | DocType | Type | Submittable | Purpose |
|---|---------|------|:-----------:|---------|
| 1 | **Hostel Building** | Master | No | Building metadata, facilities, occupancy rollup |
| 2 | **Hostel Room** | Master | No | Rooms, bed capacity, amenities, rent |
| 3 | **Hostel Room Occupant** | Child Table | — | Current residents inside a room |
| 4 | **Hostel Mess** | Master | No | Mess profile, meal timings |
| 5 | **Mess Menu** | Master | No | Weekly menu (Draft/Published/Archived) |
| 6 | **Mess Menu Item** | Child Table | — | Day × meal × items |
| 7 | **Hostel Allocation** | Txn | Yes | Resident → Room assignment |
| 8 | **Hostel Attendance** | Txn | No | Per-resident daily presence |
| 9 | **Hostel Bulk Attendance** | Txn | Yes | Batch attendance per building/date/slot |
| 10 | **Hostel Attendance Record** | Child Table | — | Rows inside Bulk Attendance |
| 11 | **Hostel Visitor** | Txn | No | Visitor check-in/out |
| 12 | **Hostel Maintenance Request** | Txn | Yes | Priority-based repair tickets |

### 2.2 New DocTypes (added for the standalone product)

| # | DocType | Type | Submittable | Purpose |
|---|---------|------|:-----------:|---------|
| 13 | **Hostel Resident** | Master | No | Replaces Education Student — resident profile linked to Frappe User |
| 14 | **Hostel Invoice** | Txn | Yes | Hostel-specific invoice (rent, deposit, mess coupon, subscription period) |
| 15 | **Mess Subscription Plan** | Master | No | Billing interval + meal inclusions |
| 16 | **Mess Subscription** | Txn | Yes | Active recurring subscription for a resident |
| 17 | **Mess Subscription Invoice History** | Child Table | — | Per-period invoice log inside a subscription |
| 18 | **Mess Meal Coupon** | Txn | No | One-time paid meal entry |
| 19 | **Mess Attendance** | Txn | No | Daily meal consumption log |
| 20 | **Security Deposit Refund** | Txn | Yes | Refund on vacate |
| 21 | **Hostel Payment Settings** | Single | No | Razorpay keys, webhook secret, enabled flag |
| 22 | **Hostel Notification Log** | Txn | No | Outgoing SMS/email audit trail |

### 2.3 DocType Details (fields, controllers, key behaviour)

#### 2.3.1 Hostel Building
- `building_name`, `building_code` (unique), `hostel_type` (Boys/Girls/Co-Ed), `status`
- `warden`, `assistant_warden` (Link User/Employee), `contact_number`
- `total_floors`, `total_rooms` (ro), `total_capacity` (ro), `occupied` (ro), `available` (ro), `occupancy_rate` (ro)
- Facilities checks: `has_wifi`, `has_laundry`, `has_mess`, `has_common_room`, `has_gym`, `has_parking`
- Fee defaults: `annual_fee`, `security_deposit`, `mess_fee_monthly`
- Address: `address`, `city`, `state`, `latitude`, `longitude`
- **Controller:** validates warden employment and gender match; `update_stats()` rolls up room occupancy
- **Whitelist methods:** `get_building_stats`, `get_buildings_for_gender`, `recalculate_all_building_stats`

#### 2.3.2 Hostel Room
- `hostel_building`, `room_number`, `floor`, `room_type` (Single/Double/Triple/Dormitory), `capacity`
- `occupied_beds` (ro), `available_beds` (ro), `status` (Available/Partial/Full/Maintenance)
- Child table `occupants` → Hostel Room Occupant
- Pricing: `rent_per_month`, `rent_per_semester`, `security_deposit`
- Amenities: `has_attached_bathroom`, `has_ac`, `has_balcony`, `has_study_table`, `has_wardrobe`, `has_hot_water`
- Maintenance: `furniture_condition`, `last_maintenance_date`, `next_maintenance_due`
- **Controller:** auto-names `{building}-{room_number}`, enforces room_type vs capacity, rolls occupancy to building
- **Whitelist methods:** `get_available_rooms`, `get_room_occupants`, `set_maintenance_status`

#### 2.3.3 Hostel Resident (NEW)
- `full_name`, `user` (Link User, unique, required), `email`, `mobile`
- `gender`, `date_of_birth`, `photo`, `status` (Active/Vacated/Blacklisted)
- Guardian: `guardian_name`, `guardian_mobile`, `guardian_relationship`
- KYC: `id_proof_type` (Aadhar/PAN/DL/Passport), `id_proof_number`, `id_proof_attachment`
- Academic (optional): `institution_name`, `course`, `year`
- Emergency: `emergency_contact_name`, `emergency_contact_mobile`
- Address: `permanent_address`, `city`, `state`, `pincode`
- `enrolled_on`, `vacated_on`, `remarks`
- **Controller:** ensures unique User mapping, enables/disables User based on status
- **Whitelist methods:** `get_current_resident(user)` — portal-side identity resolver

#### 2.3.4 Hostel Allocation
- `resident` (Link Hostel Resident — replaces Student), `from_date`, `to_date`, `duration_months`
- `hostel_building`, `room`, `bed_number`, `room_type` (ro), `floor` (ro), `rent_per_month` (ro)
- Fee: `generate_invoice` (check), `total_rent`, `security_deposit`, `mess_charges`, `total_amount`, `hostel_invoice` (Link)
- `status` (Active/Vacated/Transferred/Cancelled), `remarks`
- **Controller:** validates room availability and gender, on submit adds to room occupants + creates Hostel Invoice if `generate_invoice=1`, on cancel removes occupant and updates stats
- **Whitelist methods:** `get_available_rooms`, `vacate_room`, `transfer_room`

#### 2.3.5 Hostel Attendance / Bulk Attendance
- Individual: resident, date, status (Present/Absent/Leave/Late), in_time, out_time, late_entry, early_exit
- Bulk: building, attendance_date, attendance_type (Morning/Evening/Night), summary counters, child table `attendance_records`
- **Controller:** prevents duplicates, curfew flag (in_time > 22:00), bulk submit creates individual rows

#### 2.3.6 Hostel Visitor
- visitor_name, visitor_mobile, relationship, id_type, id_number, photo
- student (now `resident`), building (ro), room (ro)
- visit_date, check_in_time, expected_checkout_time, check_out_time, duration (ro), purpose, status
- **Scheduler:** `auto_checkout_visitors` at day end

#### 2.3.7 Hostel Maintenance Request
- request_date, building, room, requested_by (resident), request_type, priority, subject, description, attachments
- assigned_to (Employee/User), assigned_on, expected_completion, actual_completion
- resolution_remarks, cost_incurred, status
- **Controller:** notifies admin on Urgent; closes when `actual_completion` set

#### 2.3.8 Hostel Mess
- `mess_name` (unique), `mess_type` (Veg/Non-Veg/Both), `capacity`, `current_subscribers` (ro)
- `mess_incharge` (User), `monthly_charge`, `daily_rate` (ro = monthly/30)
- Meal timings, `status` (Active/Inactive/Closed)
- Child table `menu` → quick weekly preview (also covered by dedicated Mess Menu docs)
- Contact: `contact_number`, `email`

#### 2.3.9 Mess Menu + Mess Menu Item
- Menu: `mess`, `week_start_date` (must be Monday), `week_end_date` (ro), `status` (Draft/Published/Archived), child table `menu_items`, `special_notes`, `prepared_by`, `approved_by`
- Menu Item: `day` (Mon–Sun), `meal_type` (Breakfast/Lunch/Snacks/Dinner), `menu_items` (text), `special_item` (check)
- **Controller:** warns when publishing incomplete menus; whitelist `get_today_menu`, `get_week_menu`

#### 2.3.10 Hostel Invoice (NEW)
- `resident`, `invoice_date`, `due_date`, `invoice_type` (Rent/Deposit/Mess Coupon/Mess Subscription/Maintenance/Other)
- Line items (child table): description, quantity, rate, amount, tax_rate, tax_amount
- `subtotal`, `tax_total`, `discount`, `grand_total`, `paid_amount`, `balance`
- `status` (Draft/Unpaid/Partially Paid/Paid/Overdue/Cancelled/Refunded)
- Source links: `allocation`, `meal_coupon`, `subscription`, `subscription_period_start`, `subscription_period_end`
- Razorpay: `razorpay_order_id`, `razorpay_payment_id`, `payment_entry`
- **Controller:** calculates totals; on submit sends email with payment link; on cancel reverses

#### 2.3.11 Mess Subscription Plan (NEW)
- `plan_name`, `mess`, `status` (Active/Inactive)
- `billing_interval` (Monthly/Quarterly/Half-Yearly/Annual), `billing_interval_count` (default 1)
- `cost`, `currency` (default INR)
- Meal inclusions: `includes_breakfast`, `includes_lunch`, `includes_snacks`, `includes_dinner`
- `grace_period_days` (default 5), `allow_pause`, `allow_auto_renew` (default true)
- `applicable_from`, `applicable_to`, `description`
- **Controller:** computes `days_per_cycle` utility

#### 2.3.12 Mess Subscription (NEW)
- `resident`, `plan`, `mess`
- `start_date`, `end_date`, `billing_day` (day-of-month), `billing_day_computed` (ro)
- `status` (Trial/Active/Paused/Past Due/Cancelled/Completed)
- `auto_renew` (default from plan), `paused_on`, `paused_until`, `cancelled_on`, `cancellation_reason`
- `current_period_start`, `current_period_end`, `next_invoice_date`, `last_invoice_date`
- Child table `invoice_history` → Mess Subscription Invoice History
- **Controller:** on submit computes first `current_period_*` and `next_invoice_date`, creates first (pro-rata) invoice; on cancel optionally issues refund via Razorpay Refund API
- **Whitelist methods:** `pause`, `resume`, `cancel(refund_policy)`, `renew`

#### 2.3.13 Mess Subscription Invoice History (child)
- `period_start`, `period_end`, `hostel_invoice` (Link), `amount`, `status`, `generated_on`, `paid_on`

#### 2.3.14 Mess Meal Coupon (NEW)
- `resident`, `mess`, `meal_type` (Breakfast/Lunch/Snacks/Dinner), `meal_date`
- `amount`, `hostel_invoice`, `status` (Unpaid/Paid/Consumed/Expired/Cancelled)
- `qr_code` (ro — generated after payment), `consumed_at`, `consumed_by`
- **Controller:** on payment success generates QR; on expiry (meal_date < today and not consumed) status=Expired

#### 2.3.15 Mess Attendance (NEW)
- `resident`, `mess`, `meal_date`, `meal_type`, `source` (Subscription/Coupon/Walk-in), `reference` (subscription/coupon link)
- Logged by scanning QR at the counter

#### 2.3.16 Security Deposit Refund (NEW)
- `allocation`, `resident`, `original_deposit`, `deductions` (child: description, amount), `refund_amount`, `refund_mode` (Bank Transfer/Razorpay Refund), `status` (Pending/Processed/Failed)

#### 2.3.17 Hostel Payment Settings (Single)
- `enabled`, `razorpay_key_id`, `razorpay_key_secret` (password), `razorpay_webhook_secret` (password)
- `currency`, `company_name`, `company_logo`, `support_email`, `support_phone`
- `terms_url`, `privacy_url`

---

## 3. Business Workflows

### 3.1 Resident Admission & Allocation

```
Admin creates Hostel Resident → Frappe User auto-provisioned → welcome email
  → Admin creates Hostel Allocation (select building, room, bed, dates)
  → On submit: occupant added to room, building stats updated, Hostel Invoice
    generated (rent × duration + security deposit + optional mess charges)
  → Invoice emailed to resident with Razorpay pay link
  → Resident pays → webhook marks invoice Paid, Payment Entry created
```

### 3.2 Daily Attendance

```
Warden opens Bulk Attendance form → picks building + date + slot
  → System loads active residents → warden marks each → Submit
  → Individual Hostel Attendance records created per resident
  → Absent residents trigger notification (email/SMS to guardian)
```

### 3.3 Visitor Check-in

```
Guard opens Hostel Visitor → captures visitor ID + photo + resident
  → System validates resident is currently allocated
  → Status=Checked In; scheduled auto-checkout at 22:00 if no manual checkout
  → Checkout: computes duration, status=Checked Out
```

### 3.4 Maintenance Request

```
Resident portal → raise request (type, priority, description)
  → Warden dashboard shows open tickets
  → Warden assigns to staff → status=In Progress → completes → status=Completed
  → Urgent tickets push notification to admin
```

### 3.5 One-Time Mess Coupon Purchase

```
Resident portal → Mess → Buy Coupon → pick date + meal
  → Hostel Invoice created (single line, mess daily rate)
  → Razorpay Order created, checkout shown
  → User pays → webhook verifies signature → invoice Paid + coupon Paid + QR generated
  → QR displayed in portal, scanned at mess counter → coupon Consumed + Mess Attendance row
```

### 3.6 Mess Subscription Lifecycle (Custom Engine)

**Subscribe:**
```
Resident portal → Subscribe → pick plan (Monthly ₹3000, meals included)
  → Mess Subscription created (Draft)
  → Pro-rata amount for current partial cycle computed
  → First Hostel Invoice generated → Razorpay checkout
  → On payment: subscription submitted, status=Active,
    current_period_start/end set, next_invoice_date = period_end + 1
```

**Recurring billing (daily scheduler `generate_due_invoices`):**
```
FOR each Mess Subscription WHERE status=Active AND next_invoice_date <= today:
    advance current_period_start/end by billing_interval
    create Hostel Invoice(amount = plan.cost)
    append Mess Subscription Invoice History row
    update last_invoice_date = today
    update next_invoice_date = new_period_end + 1
    email resident with payment link
```

**Past due (daily `mark_past_due`):**
```
FOR each active subscription with unpaid invoice older than grace_period_days:
    status = Past Due
    send reminder to resident + admin
```

**Auto-cancel (weekly `auto_cancel_past_due`):**
```
FOR each Past Due subscription older than policy threshold (e.g. 14 days):
    status = Cancelled
    cancel upcoming invoices
```

**Pause / Resume:**
```
pause(from_date): status=Paused, paused_on=from_date, halt next_invoice_date
resume(on_date): status=Active, recompute next_invoice_date from on_date
```

**Cancel:**
```
cancel(effective_date, refund_policy):
    status=Cancelled; cancelled_on=effective_date
    if refund_policy=prorata: compute unused days × daily rate → trigger Razorpay Refund
```

**Renew:**
```
renew(): if auto_renew and end_date approaching:
    extend end_date by billing_interval
    continue generating invoices
```

### 3.7 Vacate & Refund

```
Warden → Hostel Allocation → vacate_room(date, remarks)
  → Status=Vacated; occupant removed from room; room stats updated
  → Security Deposit Refund created (draft) with deductions list
  → Admin approves → Razorpay Refund API call → status=Processed
```

---

## 4. Payment Integration (Razorpay)

### 4.1 Configuration
- `Hostel Payment Settings` holds `key_id`, `key_secret`, `webhook_secret`
- Razorpay dashboard webhook URL: `https://<site>/api/method/hostel_management.payments.webhooks.razorpay.handle_webhook`
- Events subscribed: `payment.captured`, `payment.failed`, `order.paid`, `refund.created`, `refund.processed`

### 4.2 Order Creation
```
POST /api/method/hostel_management.api.payments.create_razorpay_order
body: { invoice: "HINV-2026-00042" }
→ validates permission (resident owns invoice)
→ creates Razorpay Order via razorpay.Client.order.create({amount, currency})
→ stores order_id on invoice
→ returns { order_id, amount, currency, key_id, prefill:{name,email,contact} }
```

### 4.3 Client Checkout
```js
const rzp = new Razorpay({
  key: <key_id>, order_id: <order_id>, amount, currency,
  handler: (resp) => frappe.call("verify_payment", resp),
  prefill: {...}
});
rzp.open();
```

### 4.4 Signature Verification
```
POST /api/method/hostel_management.api.payments.verify_payment
body: { razorpay_order_id, razorpay_payment_id, razorpay_signature }
→ HMAC-SHA256(order_id + "|" + payment_id, key_secret) == signature
→ if ok: mark Hostel Invoice Paid, create Payment Entry, update downstream
    (subscription period, coupon QR, allocation fee)
→ returns { status: "success", invoice_status: "Paid", receipt_url }
```

### 4.5 Webhook (server-to-server source of truth)
```
POST /api/method/hostel_management.payments.webhooks.razorpay.handle_webhook
→ header X-Razorpay-Signature verified via HMAC(body, webhook_secret)
→ on payment.captured: idempotent mark-as-paid (no-op if already Paid)
→ on refund.processed: create/update Security Deposit Refund or subscription refund row
```

### 4.6 Refunds
- `razorpay.Client.payment.refund(payment_id, {amount})`
- Refund status logged in Hostel Invoice + Security Deposit Refund

---

## 5. Scheduler Jobs (`hooks.py`)

```python
scheduler_events = {
  "hourly": [
    "hostel_management.mess.billing.auto_expire_coupons",
  ],
  "daily": [
    "hostel_management.mess.billing.generate_due_invoices",
    "hostel_management.mess.billing.mark_past_due",
    "hostel_management.hostel.visitor.auto_checkout_visitors",
    "hostel_management.hostel.allocation.remind_upcoming_rent",
  ],
  "weekly": [
    "hostel_management.mess.billing.auto_cancel_past_due",
  ],
}
```

---

## 6. Roles & Permissions

| Role | Buildings | Rooms | Allocations | Attendance | Visitors | Maintenance | Mess | Invoices | Settings |
|------|:---------:|:-----:|:-----------:|:----------:|:--------:|:-----------:|:----:|:--------:|:--------:|
| Hostel Admin | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD | R/W |
| Warden | R | CRUD | CRUD | CRUD | CRUD | CRUD | R | R | — |
| Mess Incharge | R | R | R | — | — | — | CRUD | R (mess only) | — |
| Hostel Resident | — | R (own) | R (own) | R (own) | R (own) | C + R own | R (menu) | R (own) + Pay | — |

Permissions enforced via DocType role permissions + `has_permission` hooks for resident scoping.

---

## 7. Public Website

### 7.1 Landing (`/`)
- Hero with product tagline
- Feature grid: Allocation, Mess, Maintenance, Payments, Reports
- Pricing tiers (optional; marketing copy)
- CTA: "Resident Login" → `/login?redirect-to=/hostel-portal/`
- Footer: Terms of Service, Privacy, Contact

### 7.2 Terms of Service (`/terms-of-service`)
- Static Jinja page, legal text, version + last-updated stamp
- Linked from landing footer and portal profile

### 7.3 Login
- Reuses Frappe's built-in `/login`
- `hooks.py` sets `website_user_home_page = "hostel-portal"` for residents
- Redirect rule: if `frappe.session.user` has role "Hostel Resident" → `/hostel-portal/`

---

## 8. Student Portal

Full specification in **`STUDENT_PORTAL_FRONTEND_SPEC.md`**.

Summary:
- Vue 3 + Vite SPA served at `/hostel-portal/`
- Consumes REST endpoints under `/api/method/hostel_management.api.*`
- Sections: Dashboard, My Room, Mess (menu, subscription, coupons), Payments, Maintenance, Profile

---

## 9. Notifications

| Event | Channel | Recipient | Template |
|-------|---------|-----------|----------|
| Allocation confirmed | Email + SMS | Resident, Guardian | `allocation_confirmed` |
| Invoice generated | Email | Resident | `invoice_new` |
| Payment received | Email | Resident | `payment_receipt` |
| Subscription past due | Email + SMS | Resident | `subscription_past_due` |
| Subscription cancelled | Email | Resident, Admin | `subscription_cancelled` |
| Visitor checked in | SMS | Resident | `visitor_checkin` |
| Maintenance urgent | Email + SMS | Admin, Warden | `maintenance_urgent` |
| Attendance marked absent | Email | Guardian | `attendance_absent` |

---

## 10. Reports

- **Hostel Occupancy** — building-wise occupancy %, available beds
- **Hostel Attendance Report** — date-range attendance by building
- **Outstanding Invoices** — unpaid invoices by age bucket
- **Mess Subscription Report** — active / past-due / cancelled counts
- **Revenue Report** — monthly collections by category
- **Maintenance Summary** — open tickets by priority/type

---

## 11. Deployment

### 11.1 Prerequisites
- Frappe Framework 15
- ERPNext 15
- MariaDB 10.6+, Redis 6+, Node 18+, Python 3.10+
- Razorpay merchant account

### 11.2 Install
```bash
bench get-app hostel_management <git-url>
bench new-site hostel.local
bench --site hostel.local install-app erpnext
bench --site hostel.local install-app hostel_management
bench --site hostel.local migrate
bench --site hostel.local set-config developer_mode 0
bench setup production <user>
```

### 11.3 First-run Setup
1. Log in as Administrator
2. Open **Hostel Payment Settings** → enter Razorpay credentials
3. Create Hostel Building → Rooms → Mess → Mess Menu
4. Create first Hostel Resident + User; allocate; verify invoice + payment
5. Configure Razorpay webhook in dashboard pointing to webhook URL

### 11.4 Operations Runbook
- **Daily:** verify `generate_due_invoices` ran; review failed webhooks log
- **Weekly:** review past-due subscriptions; mess menu publish
- **Monthly:** close books; reconcile payments; backup site

---

## 12. Roadmap

**Phase 0 — Docs** (this file)
**Phase 1 — App scaffold + port DocTypes**
**Phase 2 — Hostel Resident + decouple from Student**
**Phase 3 — Custom mess subscription engine + invoices**
**Phase 4 — Razorpay integration**
**Phase 5 — Public landing + ToS**
**Phase 6 — Student portal (Vue SPA)**
**Phase 7 — Roles, permissions, fixtures**
**Phase 8 — Testing**
**Phase 9 — Production deploy**

See `/home/frappe/.claude/plans/radiant-juggling-graham.md` for the authoritative execution plan.

---

## 13. File Reference

| What | Where |
|------|-------|
| Existing hostel source (to copy) | `frappe-bench/apps/university_erp/university_erp/university_hostel/` |
| Razorpay webhook pattern | `frappe-bench/apps/university_erp/university_erp/university_payments/webhooks/razorpay_webhook.py` |
| Portal SPA pattern | `frappe-bench/apps/university_erp/university_erp/www/student_portal/` |
| Pay-fees template | `frappe-bench/apps/university_erp/university_erp/www/pay-fees/` |
| New app target | `frappe-bench/apps/hostel_management/` (to be created) |
