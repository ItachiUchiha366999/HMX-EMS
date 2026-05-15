# New DocTypes & Features — Companion to HOSTEL_MANAGEMENT_SYSTEM.md

> **Purpose.** This file lists **only the DocTypes and features added by `SCOPE_DOCUMENT.md`** that are **not** in `HOSTEL_MANAGEMENT_SYSTEM.md`. Developers can read this file in isolation to know exactly what's new.
>
> **Source of truth for behaviour:** `SCOPE_DOCUMENT.md` (cross-referenced by section).
> **Source of truth for everything else:** `HOSTEL_MANAGEMENT_SYSTEM.md` (DocTypes 1–22).
>
> Numbering continues from the existing inventory. Existing DocType **#18 Mess Meal Coupon** is **removed and replaced** — see §0 below.
>
> **Count:** 11 new DocTypes (#23–#33), 1 removed (#18). Net inventory: **32 DocTypes**.

---

## 0. Removed DocType

### ~~#18 Mess Meal Coupon~~ — DO NOT BUILD

The original spec defined a per-meal, resident-only coupon. The simplified cafeteria model (SCOPE_DOCUMENT.md §5) replaces this with:
- **Mess Coupon Book (#30)** — prepaid bundle, open to residents + public.
- **Mess Single Meal Sale (#31)** — one-off pay-at-counter, open to residents + public.

If the team has already scaffolded Mess Meal Coupon, delete the DocType and any controller code. Any documentation referencing it should be updated.

---

## 1. New Modules at a Glance

| Module | New DocTypes | Section |
|--------|-------------|---------|
| **Staff** (hostel workers — warden, cooks, guards, cleaners) | #23, #24, #25 | §2 |
| **Biometric** (devices + raw punch log) | #26, #27 | §3 |
| **Admissions** (website enquiry pipeline) | #28, #29 | §4 |
| **Cafeteria** (coupon books + single meal sales + POS) | #30, #31, #32, #33 | §5 |

---

## 2. Staff Module

> Scope: `SCOPE_DOCUMENT.md §2`.
>
> Problem solved: hostel workers (warden, mess incharge, cooks, cleaners, guards) need attendance tracking across shifts that cross midnight; monthly payable-hours output for wage computation; late/absent visibility for managers.

### #23 Hostel Staff

**Type:** Master · **Submittable:** No · **Module:** Staff

Staff profile linked to a Frappe User (and optionally an ERPNext Employee if payroll is in scope).

**Fields**

| Field | Type | Notes |
|-------|------|-------|
| `full_name` | Data | Required |
| `user` | Link (User) | Unique, required |
| `employee` | Link (Employee) | Optional — only if pushing to ERPNext Payroll |
| `staff_code` | Data | Unique, auto-generated |
| `role_tag` | Select | Warden / Assistant Warden / Mess Incharge / Cook / Cleaner / Security / Maintenance / Other |
| `primary_building` | Link (Hostel Building) | Optional |
| `primary_mess` | Link (Hostel Mess) | Optional — required for mess roles |
| `default_shift` | Link (Hostel Staff Shift) | The shift most rows are stamped with |
| `biometric_user_id` | Data | Unique across Staff + Resident (no overlap) |
| `mobile` | Data | — |
| `emergency_contact` | Data | Name + phone |
| `photo` | Attach Image | — |
| `id_proof_type`, `id_proof_number` | Data | — |
| `joined_on` | Date | — |
| `status` | Select | Active / On Leave / Suspended / Separated |
| `separated_on` | Date | Required if status=Separated |
| `hourly_rate` *or* `monthly_salary` | Currency | For wage-hour reports; not ERPNext Payroll |

**Controller behaviour**
- Validate `biometric_user_id` is unique across Hostel Staff AND Hostel Resident.
- When `status` changes to Suspended/Separated, disable the linked User and revoke active sessions.
- When reactivated, re-enable User.

---

### #24 Hostel Staff Shift

**Type:** Master · **Submittable:** No · **Module:** Staff

Shift template. Supports shifts that cross midnight (e.g. 22:00 → 06:00 for night guards).

**Fields**

| Field | Type | Notes |
|-------|------|-------|
| `shift_name` | Data | e.g. "Morning Cook 04:00–12:00" |
| `start_time`, `end_time` | Time | May cross midnight |
| `grace_minutes` | Int | Default 10; no late flag within grace |
| `break_minutes` | Int | Default 0 |
| `applicable_weekdays` | Check × 7 | Mon–Sun multi-check |
| `expected_hours` | Float | Computed read-only |
| `status` | Select | Active / Inactive |

**Controller behaviour**
- `expected_hours = (end − start + 24 if end < start) − break_minutes/60`.

---

### #25 Hostel Staff Attendance

**Type:** Txn · **Submittable:** No · **Module:** Staff

One row per staff × date. **Not** submittable — it's mutated throughout the day as punches arrive.

**Fields**

| Field | Type | Notes |
|-------|------|-------|
| `staff` | Link (Hostel Staff) | Required |
| `attendance_date` | Date | Required; unique with `staff` |
| `shift` | Link (Hostel Staff Shift) | Defaults from `staff.default_shift` |
| `check_in_time` | Datetime | First In punch of the day |
| `check_out_time` | Datetime | Last Out punch of the day |
| `source` | Select | Biometric / Manual / Mobile / Warden-Entered |
| `biometric_events` | Table (read-only list of Link to #27) | Audit of every punch that fed this row |
| `status` | Select | Present / Absent / Half-Day / On Leave / Holiday / Weekly Off |
| `late_by_minutes` | Int | Computed |
| `early_exit_minutes` | Int | Computed |
| `hours_worked` | Float | Computed: check_out − check_in − break |
| `overtime_hours` | Float | Computed: max(0, hours_worked − shift.expected_hours) |
| `approved_by` | Link (User) | Required for source=Manual |
| `approved_on` | Datetime | — |
| `auto_closed` | Check | Set if scheduler stamped check_out = shift.end_time |
| `remarks` | Small Text | — |

**Controller behaviour**
- **First-in / last-out rule:** the first biometric In event of the day sets `check_in_time`; the last Out event updates `check_out_time`. Everything in between is appended to `biometric_events` for audit but does NOT overwrite the first/last.
- Manual edits to `check_in_time` / `check_out_time` are allowed only if `approved_by` is set; field-level change log is retained.
- Compute `late_by_minutes`, `early_exit_minutes`, `hours_worked`, `overtime_hours` on save.

**Schedulers**
- `daily close_open_attendance` — rows with check_in but no check_out get check_out = shift.end_time + `auto_closed=1`.
- `daily generate_absent_rows` — creates `status=Absent` rows at 23:59 for active staff with no punch that day (respects holiday calendar and any approved leave).

**Reports**
- Staff Attendance Summary (days present/absent/late, hours, OT).
- Today's Roster.
- Late Arrivals.
- Wage Hour Export (CSV — staff × month × hours × rate).

---

## 3. Biometric Module

> Scope: `SCOPE_DOCUMENT.md §3`.
>
> Problem solved: unified ingestion for any biometric device vendor (ZKTeco / eSSL / Hikvision / Mantra), feeding both staff and resident attendance from the same raw punch log.

### #26 Hostel Biometric Device

**Type:** Master · **Submittable:** No · **Module:** Biometric

Device registry. One row per physical reader.

**Fields**

| Field | Type | Notes |
|-------|------|-------|
| `device_name` | Data | Human label |
| `device_code` | Data | Unique; used in ingestion URL |
| `vendor` | Select | ZKTeco / eSSL / Hikvision / Mantra / Other |
| `device_model`, `serial_number` | Data | — |
| `location_type` | Select | Gate / Mess Counter / Office / Block Entry |
| `building` | Link (Hostel Building) | Optional |
| `mess` | Link (Hostel Mess) | Optional |
| `ip_address`, `port` | Data | For pull-mode vendors |
| `auth_token` | Password | Bearer token for push-mode ingestion |
| `direction_policy` | Select | In Only / Out Only / Bidirectional |
| `last_heartbeat_at`, `last_sync_at` | Datetime | — |
| `status` | Select | Online / Offline / Disabled |
| `notes` | Small Text | — |

**Controller behaviour**
- `auth_token` auto-generated on create; rotatable from desk.
- `hourly ping_devices` scheduler updates heartbeat + status.

---

### #27 Hostel Biometric Event

**Type:** Txn · **Submittable:** No · **Module:** Biometric

**Raw punch log. One row per punch.** This is the source-of-truth for all biometric processing; downstream attendance DocTypes reference these rows for audit.

**Fields**

| Field | Type | Notes |
|-------|------|-------|
| `device` | Link (Hostel Biometric Device) | Required |
| `biometric_user_id` | Data | The ID enrolled on the device |
| `event_timestamp` | Datetime | Device-local time |
| `direction` | Select | In / Out / Unknown |
| `raw_payload` | Long Text | JSON from the device; for debugging |
| `matched_to` | Dynamic Link | → Hostel Staff OR Hostel Resident; null if unmatched |
| `processing_status` | Select | Pending / Matched / Unmatched / Error |
| `processing_error` | Small Text | — |
| `processed_at` | Datetime | — |

**Indexes**
- `(device, event_timestamp)` — dedupe and device-history queries
- `(biometric_user_id)` — user history lookups
- `(processing_status)` — worker picks up Pending

**Dedupe rule**
- Unique constraint `(device, biometric_user_id, event_timestamp)` — idempotent ingestion; replays of the same batch don't create duplicates.

### Ingestion endpoints

**A. Device push (real-time, preferred)**
```
POST /api/method/hostel_management.api.biometric.ingest
Headers: Authorization: Bearer <device.auth_token>
Body: {
  "device_code": "GATE-01",
  "events": [{ "user_id": "1024", "timestamp": "2026-04-19T08:14:33", "direction": "In", "payload": {...} }]
}
→ 200 { accepted: N, duplicates: M }
```

**B. Scheduled pull (every 5 min)**
```
hostel_management.biometric.adapters.zkteco.pull_all_devices  (or vendor-specific)
→ Connect to each Online device → get_attendance() → diff since last_sync_at → write events → update last_sync_at
```

### Processing pipeline

For each row with `processing_status = Pending`:
1. **Resolve** `biometric_user_id`:
   - Match `Hostel Staff.biometric_user_id` → staff attendance target.
   - Else match `Hostel Resident.biometric_user_id` → resident attendance / mess target.
   - Else `processing_status = Unmatched` → admin digest.
2. **Determine direction** if Unknown:
   - Use `device.direction_policy` if set.
   - Else toggle based on user's last event (In ↔ Out).
3. **Route** based on matched entity + device location:
   - Staff hit → upsert Hostel Staff Attendance (first-in / last-out rule).
   - Resident hit at Gate → upsert Hostel Attendance (#8 — existing).
   - Resident hit at Mess Counter → create Mess Attendance (#19) — but ONLY if an active Mess Subscription or valid Mess Coupon Book exists; otherwise logged, no attendance row.
4. Stamp `processed_at` + flip `processing_status` to Matched / Error.

**Schedulers**
- `every_5_minutes adapters.pull_all_devices` — pull-mode ingestion.
- `every_5_minutes processing.process_pending_events` — drain the Pending queue.
- `daily processing.send_unmatched_digest` — email unmatched events to Biometric Admin.

### Failure modes handled

| Failure | Handling |
|---------|----------|
| Device offline | Heartbeat miss > 10 min → status=Offline → alert admin; events buffered on device, synced on reconnect |
| Unmatched user_id | Stored with `processing_status=Unmatched`; daily digest |
| Duplicate punch | Unique constraint idempotent on replay |
| Clock drift | Admin-configurable per-device offset |
| Mess scan with no active pass | Event processed, no Mess Attendance; counter display shows "No active pass"; counter can upsell a Single Meal Sale |

### Enrolment flow

- Admin enrols fingerprint/face on the device using vendor software with a chosen numeric ID.
- Admin pastes that ID into `Hostel Staff.biometric_user_id` or `Hostel Resident.biometric_user_id`.
- Self-serve kiosk enrolment is **out of scope for v1**.

---

## 4. Admissions Module

> Scope: `SCOPE_DOCUMENT.md §4`.
>
> Problem solved: structured pipeline for prospective residents who submit an enquiry on the public website — replacing WhatsApp / phone tag.

### #28 Hostel Enquiry

**Type:** Txn · **Submittable:** No · **Module:** Admissions

Public-form submission. Moves through a pipeline from `New` to `Converted` (or `Rejected`/`Dropped`).

**Fields (grouped)**

**Prospect**
- `full_name` (required), `email`, `mobile` (required), `gender`, `date_of_birth`
- `city`, `state`, `pincode`

**Academic (optional)**
- `institution_name`, `course`, `year_of_study`

**Guardian**
- `guardian_name`, `guardian_mobile`, `guardian_relationship`

**Preferences**
- `preferred_building` (Link, optional)
- `preferred_room_type` (Select: Single / Double / Triple / Dormitory / Any)
- `preferred_start_date` (Date), `duration_months` (Int)
- `wants_mess` (Check)
- `preferred_mess_plan` (Link Mess Subscription Plan, optional)
- `special_requirements` (Small Text)

**Provenance**
- `source` (Select: Website / Walk-in / Referral / Instagram / Google Ads / Other)
- `referred_by` (Data)
- `utm_source`, `utm_medium`, `utm_campaign` (Data)

**Pipeline**
- `status` (Select: New / Contacted / Visit Scheduled / Offer Sent / Converted / Rejected / Dropped)
- `assigned_to` (Link User — role Admissions)
- `visit_scheduled_on` (Datetime), `offer_sent_on` (Date)
- `converted_to_resident` (Link Hostel Resident — set on conversion)
- `rejected_reason`, `dropped_reason` (Small Text)
- `consent_to_contact` (Check, required true)

**Child table**
- `notes` → `Hostel Enquiry Note` (#29)

**Controller behaviour**
- Auto-assigns `assigned_to` via round-robin across users with role `Admissions`.
- On `status = Converted`: prompts admin to create Hostel Resident + Allocation + Frappe User (one-click action button).
- Rate-limit on public-endpoint submissions: max 3 per IP / hour.

### Public endpoint

```
POST /api/method/hostel_management.api.enquiry.submit
Body: { prospect fields..., captcha_token }
Server steps:
  1. Verify hCaptcha / Cloudflare Turnstile.
  2. Reject if honeypot field is non-empty.
  3. Rate-limit check.
  4. Create Hostel Enquiry (status=New).
  5. Send confirmation email (+ optional SMS) to prospect.
  6. Notify admissions assignee via Hostel Notification Log.
→ 200 { enquiry_id, next_step: "We'll call you within 24 hours" }
```

### Admin surfaces
- Kanban view grouped by `status`.
- Filters: assigned_to, preferred_building, source, date range.
- Detail page with action buttons: Schedule Visit · Send Offer · Convert to Resident.

### Schedulers
- `daily enquiry.remind_unassigned` — email admin if any enquiry unassigned > 24h.

### Reports
- Enquiry Funnel (New → Contacted → Visit → Offer → Converted; drop-off % + time-in-stage).
- Enquiry Source Attribution (conversions by source / utm_campaign).

---

### #29 Hostel Enquiry Note

**Type:** Child Table · **Parent:** Hostel Enquiry · **Module:** Admissions

Follow-up log inside an enquiry.

**Fields**

| Field | Type | Notes |
|-------|------|-------|
| `noted_on` | Datetime | Defaults to now |
| `noted_by` | Link (User) | Defaults to session user |
| `note` | Small Text | Required |
| `note_type` | Select | Call / Email / WhatsApp / Visit / Other |

---

## 5. Cafeteria Module

> Scope: `SCOPE_DOCUMENT.md §5`.
>
> Problem solved: sell meals to residents **and** the general public through two simple flows — a prepaid coupon book, or a single meal at the counter. Uniform pricing; no buyer tiers; no KYC; no host-resident linkage.

### #30 Mess Coupon Book

**Type:** Txn · **Submittable:** Yes · **Module:** Cafeteria

A prepaid wallet of meal credits. One book = one QR = N meals.

**Fields**

| Field | Type | Notes |
|-------|------|-------|
| `book_number` | Data | Unique, auto: `MCB-2026-00042` |
| `mess` | Link (Hostel Mess) | Required |
| `book_type` | Link (Mess Coupon Book Type — #33) | Required; determines bundle |
| `holder_type` | Select | Resident / Public |
| `resident` | Link (Hostel Resident) | Required if holder_type=Resident |
| `holder_name`, `holder_mobile` | Data | Required if holder_type=Public; auto-copied from resident otherwise |
| `meals_total` | Int | Denormalised from book_type at purchase |
| `meals_remaining` | Int | Starts at meals_total; decrements per redemption |
| `meal_constraints` | Small Text / JSON | Which meals are allowed: e.g. `["Lunch"]` or all four |
| `unit_price` | Currency | Computed: book_price ÷ meals_total |
| `book_price` | Currency | — |
| `payment_method` | Select | Cash / UPI / Card / Razorpay |
| `payment_reference` | Data | UPI ref / last-4 / Razorpay payment_id |
| `pos_session` | Link (Mess POS Session — #32) | Only set if sold at counter |
| `purchased_on` | Date | — |
| `valid_until` | Date | Defaults to purchased_on + book_type.validity_days |
| `qr_code` | Attach / Data | Generated on submit |
| `status` | Select | Active / Exhausted / Expired / Refunded / Cancelled |
| `hostel_invoice` | Link (Hostel Invoice) | Only for Razorpay online purchases or GST-bill requests |
| `notes` | Small Text | — |

**Controller behaviour**
- On submit (payment confirmed): `status = Active`, `meals_remaining = meals_total`, QR generated.
- Redemption: scanning the QR at the counter → validate `status=Active`, `meals_remaining > 0`, `valid_until >= today`, and `meal_type ∈ meal_constraints` → decrement → write Mess Attendance (#19) with `source = Coupon Book` → if now 0, flip to `Exhausted`.
- Group redemption: a single book can redeem N meals in one operation ("2 lunches from this book") — each redemption writes its own Mess Attendance row.
- Refund / cancellation rules: business decision (see `SCOPE_DOCUMENT.md §8.Q12`); default = forfeit on expiry.

**Schedulers**
- `daily cafeteria.coupon_book.expire_books` — flip Active books past `valid_until` to Expired.
- `daily cafeteria.coupon_book.send_expiry_reminders` — SMS 7 days before expiry if `meals_remaining > 0`.

---

### #31 Mess Single Meal Sale

**Type:** Txn · **Submittable:** Yes · **Module:** Cafeteria

One walk-in transaction. One row = one meal sold, paid right now.

**Fields**

| Field | Type | Notes |
|-------|------|-------|
| `sale_number` | Data | Unique, auto: `MSM-20260419-0123` |
| `mess` | Link | Required |
| `meal_date` | Date | Defaults to today |
| `meal_type` | Select | Breakfast / Lunch / Snacks / Dinner |
| `buyer_name` | Data | Optional |
| `buyer_mobile` | Data | Optional — captured only if buyer wants an SMS receipt |
| `quantity` | Int | Default 1 |
| `unit_price`, `total_amount` | Currency | total = unit × qty |
| `payment_method` | Select | Cash / UPI / Card / Razorpay |
| `payment_reference` | Data | **Optional** — see UPI capture modes below |
| `pos_session` | Link (#32) | Auto — the open session at the counter |
| `token_number` | Int | Per-session sequential — "Token 47" |
| `qr_code` | Data / Attach | Optional — only if the mess uses scan-on-entry |
| `status` | Select | Paid / Refunded / Cancelled |
| `hostel_invoice` | Link | Only created if buyer asked for a GST bill or total ≥ threshold |
| `sold_by` | Link (User) | Counter staff |
| `sold_at` | Datetime | — |

**Controller behaviour**
- On submit: `status = Paid`; write Mess Attendance (#19) row with `source = Single Meal`.
- Void within the same session: `status = Refunded`; remove attendance row; return cash via POS Session.
- The row is final on submit — no half-state. No "Unpaid → Paid" workflow.

### UPI capture modes (configurable per mess)

To keep peak-hour counter speed, `payment_reference` is **optional**. The mess chooses a capture mode via `Hostel Mess.upi_capture_mode`:

| Mode | At the counter | Reconciliation |
|------|---------------|----------------|
| `amount-only` (default) | Pick UPI, type amount, submit — no ref | Session close: bank UPI total vs sales UPI total |
| `last-3-digits` | Type last 3 digits of the UPI ref | Fuzzy match on amount + last-3 + timestamp window |
| `psp-qr` | Dynamic Razorpay / PhonePe QR per sale; webhook auto-confirms | Fully automatic, per-sale |
| `bank-import` | Amount only at counter; overnight job matches bank statement | Next-morning per-sale match |

The counter UI adapts to the mode — only `psp-qr` requires a customer-facing screen; the other three run on any tablet.

---

### #32 Mess POS Session

**Type:** Txn · **Submittable:** Yes · **Module:** Cafeteria

Daily counter shift cash-up. Aggregates both Mess Coupon Book sales and Mess Single Meal Sales for the shift.

**Fields**

| Field | Type | Notes |
|-------|------|-------|
| `session_number` | Data | Unique, auto |
| `mess` | Link | Required |
| `session_date` | Date | — |
| `meal_type` | Select | Optional — a session can span multiple meals |
| `shift` | Data | Free text ("Morning", "Evening") |
| `opened_by` | Link (User) | — |
| `opened_at` | Datetime | — |
| `opening_float` | Currency | Cash in drawer at start |
| `closed_by` | Link (User) | — |
| `closed_at` | Datetime | — |
| `closing_cash_counted` | Currency | What's actually in the drawer at end |
| `total_cash`, `total_upi`, `total_card`, `total_razorpay` | Currency | Computed from linked sales |
| `total_coupon_book_sales` | Currency | Computed |
| `total_single_meal_sales` | Currency | Computed |
| `total_refunds` | Currency | Computed |
| `gross_sales`, `net_sales` | Currency | Computed |
| `cash_variance` | Currency | = closing_cash_counted − opening_float − total_cash |
| `status` | Select | Open / Closed / Reconciled / Disputed |
| `notes` | Small Text | — |

**Controller behaviour**
- Only one session can have `status=Open` per mess at a time.
- All Mess Coupon Book (#30) and Mess Single Meal Sale (#31) rows submitted while a session is Open auto-link to that session.
- On submit (close): compute variance → if ≠ 0 → `status = Disputed` + notify admin.
- On submit with variance = 0 → `status = Closed` → create **one consolidated ERPNext Payment Entry per payment method**, referencing this session. This keeps the accountant's books clean (not one entry per sale).
- Coupon redemptions do NOT touch the session — no money moves at redemption time.

**Schedulers**
- `daily cafeteria.pos.auto_close_stale_sessions` — sessions left Open > 24h get force-closed with `status=Disputed`.

---

### #33 Mess Coupon Book Type

**Type:** Master · **Submittable:** No · **Module:** Cafeteria

Configurable bundle templates. Pre-seeded by admin; resident portal + counter both pick from this list when selling a book.

**Fields**

| Field | Type | Notes |
|-------|------|-------|
| `type_code` | Data | Unique: `LUNCH-10`, `MIXED-20` |
| `display_name` | Data | "10 Lunches Pack" |
| `meals_total` | Int | — |
| `applicable_meals` | Multi-check | Breakfast / Lunch / Snacks / Dinner |
| `price` | Currency | Total bundle price |
| `validity_days` | Int | Default 90 |
| `is_active` | Check | — |

**Controller behaviour**
- Price changes on a type apply only to **new** books. Existing books are immutable — their price was locked at purchase.

---

## 6. Cross-cutting additions

### 6.1 New roles

| Role | Scope |
|------|-------|
| **Admissions** | R/W Hostel Enquiry + notes, convert to Resident. Read-only on residents/rooms. |
| **Mess Counter Staff** | Open/close POS Session, sell Coupon Books + Single Meals, scan QR. No access to menus/subscriptions admin. |
| **Biometric Admin** | Configure devices, view raw events, resolve unmatched events. |

Add these to the role permission table in `HOSTEL_MANAGEMENT_SYSTEM.md §6` alongside all new DocTypes.

### 6.2 New notifications (Hostel Notification Log triggers)

| Event | Channel | Recipient |
|-------|---------|-----------|
| New enquiry submitted | Email + desk | Admissions assignee + admin |
| Enquiry unassigned > 24h | Email | Admin |
| Biometric device offline > 10 min | Email + SMS | Biometric Admin |
| Unmatched biometric event daily digest | Email | Biometric Admin |
| Staff late arrival | Email | Building warden |
| Staff absent without leave | Email | Warden + admin |
| POS session closed with variance | Email | Admin |
| Coupon book expiring in 7 days with unused meals | SMS + email | Holder |
| Coupon book expired with unused meals | Internal | Mess incharge (refund/goodwill review) |

### 6.3 Scheduler additions (`hooks.py`)

```python
"every_5_minutes": [
  "hostel_management.biometric.adapters.pull_all_devices",
  "hostel_management.biometric.processing.process_pending_events",
],
"hourly": [
  "hostel_management.biometric.devices.ping_devices",
],
"daily": [
  "hostel_management.staff.attendance.generate_absent_rows",
  "hostel_management.staff.attendance.close_open_attendance",
  "hostel_management.enquiry.remind_unassigned",
  "hostel_management.cafeteria.pos.auto_close_stale_sessions",
  "hostel_management.cafeteria.coupon_book.expire_books",
  "hostel_management.cafeteria.coupon_book.send_expiry_reminders",
  "hostel_management.biometric.processing.send_unmatched_digest",
],
```

### 6.4 Mess Attendance (#19) — enum update

`Mess Attendance.source` becomes:
- `Subscription` (existing — from active Mess Subscription)
- `Coupon Book` (new — from Mess Coupon Book redemption; replaces old "Coupon" value)
- `Single Meal` (new — from Mess Single Meal Sale)

`Mess Attendance.coupon_book` and `Mess Attendance.single_meal_sale` link fields (mutually exclusive, nullable) replace the old `meal_coupon` link.

### 6.5 Hostel Mess (#4) — new fields

- `breakfast_price`, `lunch_price`, `snacks_price`, `dinner_price` — single price tier for all buyers.
- `upi_capture_mode` — `amount-only` / `last-3-digits` / `psp-qr` / `bank-import` (default `amount-only`).
- `gst_number`, `gst_rate`, `sac_hsn_code` — for invoices when threshold hit.
- `gst_invoice_threshold` — default ₹1000.
- `food_safety_license_number` — printed on bill footer.

### 6.6 Hostel Resident (#13) — new field

- `biometric_user_id` — unique across Staff + Resident. Enrolment is admin-entered after device-side enrolment.

### 6.7 New reports

**Staff**
- Staff Attendance Summary
- Today's Roster
- Late Arrivals
- Wage Hour Export

**Admissions**
- Enquiry Funnel
- Enquiry Source Attribution

**Cafeteria**
- Single Meal Sales (by date / meal / payment method)
- Coupon Book Sales (by type, by holder type)
- Coupon Book Redemption Rate
- Daily Cafeteria Revenue
- POS Cash Reconciliation
- Outstanding Coupon Liability
- Expired Books with Unused Meals

**Biometric**
- Biometric Device Health

---

## 7. DocType dependency graph (new modules only)

```
Hostel Biometric Device ──┐
                          ├──► Hostel Biometric Event ──► Hostel Staff Attendance
Hostel Staff ─────────────┤                         │
                          │                         ├──► Hostel Attendance (#8 existing)
Hostel Resident (#13) ────┘                         └──► Mess Attendance (#19)

Hostel Enquiry ──(convert)──► Hostel Resident ──► Hostel Allocation
     │
     └──► Hostel Enquiry Note (child)

Mess Coupon Book Type ──► Mess Coupon Book ──┐
                              ▲              ├──► Mess Attendance (redemption)
                              │              │
Mess POS Session ─────────────┤              │
       │                      │              │
       └──► Mess Single Meal Sale ───────────┤
                              │              │
                              └──► Hostel Invoice (Razorpay + GST-bill requests)
```

---

## 8. File layout (app structure)

Suggested placement inside `apps/hostel_management/hostel_management/`:

```
hostel_management/
├── staff/
│   ├── doctype/
│   │   ├── hostel_staff/
│   │   ├── hostel_staff_shift/
│   │   └── hostel_staff_attendance/
│   └── attendance.py                 # close_open_attendance, generate_absent_rows
├── biometric/
│   ├── doctype/
│   │   ├── hostel_biometric_device/
│   │   └── hostel_biometric_event/
│   ├── adapters/
│   │   ├── __init__.py               # pull_all_devices dispatcher
│   │   ├── zkteco.py
│   │   └── hikvision.py
│   ├── processing.py                 # process_pending_events, send_unmatched_digest
│   └── devices.py                    # ping_devices
├── admissions/
│   ├── doctype/
│   │   ├── hostel_enquiry/
│   │   └── hostel_enquiry_note/
│   └── enquiry.py                    # submit, remind_unassigned, convert_to_resident
├── cafeteria/
│   ├── doctype/
│   │   ├── mess_coupon_book/
│   │   ├── mess_coupon_book_type/
│   │   ├── mess_single_meal_sale/
│   │   └── mess_pos_session/
│   ├── coupon_book.py                # expire_books, send_expiry_reminders, redeem
│   └── pos.py                        # auto_close_stale_sessions, consolidated payment entry
└── api/
    ├── biometric.py                  # ingest endpoint
    └── enquiry.py                    # public submit endpoint
```

---

## 9. Build order (suggested)

Follows `SCOPE_DOCUMENT.md §7.1`:

1. **Admissions (#28, #29)** — independent, unblocks marketing.
2. **Staff (#23, #24, #25)** — independent, admin-facing; no SPA.
3. **Biometric (#26, #27)** — depends on Staff + Resident (ID fields).
4. **Cafeteria (#30, #31, #32, #33)** — depends on existing Mess module; new counter Vue app at `/mess-pos/`.

Add-on effort estimate: ~17 backend days + ~9 frontend days = **~5 person-weeks** incremental. See `SCOPE_DOCUMENT.md §7.4`.

---

## 10. Open questions the team still needs answered

See `SCOPE_DOCUMENT.md §8`. The most load-bearing ones:

- **Q1** Biometric vendor (affects which adapter we build first).
- **Q11** Cafeteria compliance (FSSAI / GST / municipal licence readiness before serving public).
- **Q12** Coupon book expiry refund policy (forfeit / pro-rata / goodwill credit).
- **Q13** UPI capture mode for single meal sales (`amount-only` / `last-3-digits` / `psp-qr` / `bank-import`).

---

## 11. What this document is NOT

- Not a plan or roadmap — see `SCOPE_DOCUMENT.md §7`.
- Not the portal / API spec for the existing modules — see `HOSTEL_MANAGEMENT_SYSTEM.md` and `STUDENT_PORTAL_FRONTEND_SPEC.md`.
- Not user-facing documentation — internal engineering reference.

If anything here conflicts with `SCOPE_DOCUMENT.md`, **SCOPE_DOCUMENT.md wins**. This file is a developer-oriented extract, not a replacement.
