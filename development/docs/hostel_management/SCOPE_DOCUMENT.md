# Hostel Management System — Team Scope Document

> **Purpose:** A single buildable scope for the engineering team. Consolidates the existing spec (`HOSTEL_MANAGEMENT_SYSTEM.md`, `STUDENT_PORTAL_FRONTEND_SPEC.md`) and extends it with four new modules that were raised post-spec:
> 1. **Staff (Employee) Attendance** for hostel workers
> 2. **Biometric device integration** (shared by residents + staff)
> 3. **Public website enquiry / admission form**
> 4. **Walk-in mess billing** — single-meal purchases, non-resident guest billing, POS at the counter
>
> **Source of truth for unchanged areas:** `HOSTEL_MANAGEMENT_SYSTEM.md` + `STUDENT_PORTAL_FRONTEND_SPEC.md`. This doc only adds, it does not re-state.
>
> **Stack (unchanged):** Frappe 15 + ERPNext 15 · App `hostel_management` · Vue 3 portal · Razorpay · MariaDB/Redis.

---

## 0. How to read this doc

- **§1** Full DocType inventory (existing 22 + 10 new = 32). One table so the team can see everything at once.
- **§2** Staff attendance module — fields, workflows, portal surfaces.
- **§3** Biometric integration — device models, sync protocol, failure handling.
- **§4** Website enquiry form — public form → lead → admission pipeline.
- **§5** Walk-in mess billing — the money-at-the-counter problem: single meals, guests, non-residents.
- **§6** Cross-cutting concerns added by the new modules (permissions, notifications, reports).
- **§7** Delivery plan — phase sequencing, dependencies, test strategy.
- **§8** Open questions requiring business decisions before build.

---

## 1. Complete DocType Inventory

### 1.1 Already specified (22 DocTypes — see `HOSTEL_MANAGEMENT_SYSTEM.md §2`)

| # | DocType | Module | Notes |
|---|---------|--------|-------|
| 1 | Hostel Building | Core | — |
| 2 | Hostel Room | Core | — |
| 3 | Hostel Room Occupant | Core (child) | — |
| 4 | Hostel Mess | Mess | — |
| 5 | Mess Menu | Mess | — |
| 6 | Mess Menu Item | Mess (child) | — |
| 7 | Hostel Allocation | Core | Submittable |
| 8 | Hostel Attendance | Core | Resident attendance |
| 9 | Hostel Bulk Attendance | Core | Submittable |
| 10 | Hostel Attendance Record | Core (child) | — |
| 11 | Hostel Visitor | Core | — |
| 12 | Hostel Maintenance Request | Ops | Submittable |
| 13 | Hostel Resident | Core | — |
| 14 | Hostel Invoice | Billing | Submittable |
| 15 | Mess Subscription Plan | Mess | — |
| 16 | Mess Subscription | Mess | Submittable |
| 17 | Mess Subscription Invoice History | Mess (child) | — |
| 18 | ~~Mess Meal Coupon~~ | ~~Mess~~ | **REMOVED** — superseded by Mess Coupon Book (#30). Drop from build list. |
| 19 | Mess Attendance | Mess | Entry log; `source` enum updated — see §5.12 |
| 20 | Security Deposit Refund | Billing | Submittable |
| 21 | Hostel Payment Settings | Settings (Single) | — |
| 22 | Hostel Notification Log | Ops | — |

### 1.2 New DocTypes added by this scope (10)

| # | DocType | Module | Submittable | Purpose |
|---|---------|--------|:-----------:|---------|
| 23 | **Hostel Staff** | Staff | No | Staff profile (warden, mess incharge, cook, cleaner, guard). Wraps Frappe User/Employee with hostel-specific metadata. |
| 24 | **Hostel Staff Shift** | Staff | No | Shift template (Morning 06–14, Evening 14–22, Night 22–06, Full-Day) with expected hours. |
| 25 | **Hostel Staff Attendance** | Staff | No | One row per staff member per day: check-in, check-out, shift, source (biometric/manual), late/early flags, hours worked. |
| 26 | **Hostel Biometric Device** | Biometric | No | Device registry — model, location (gate/mess/office), IP, serial, last-seen heartbeat. |
| 27 | **Hostel Biometric Event** | Biometric | No | Raw punch log — `device`, `biometric_user_id`, `timestamp`, `direction` (In/Out), `raw_payload`. Feeds staff attendance + resident in/out. |
| 28 | **Hostel Enquiry** | Admissions | No | Public form submission — prospective resident + guardian + preferences. Status pipeline: New → Contacted → Visit Scheduled → Offer Sent → Converted/Rejected/Dropped. |
| 29 | **Hostel Enquiry Note** | Admissions (child) | — | Follow-up log inside an enquiry. |
| 30 | **Mess Coupon Book** | Mess | Yes | Prepaid bundle of N meals with QR. Holder can be a resident or any member of the public. Decrements on each redemption. (See §5.3.) |
| 31 | **Mess Single Meal Sale** | Mess | Yes | One-off meal sold at the counter — cash/UPI/card. Open to anyone, no identity required. (See §5.5.) |
| 32 | **Mess POS Session** | Mess | Yes | Counter shift cash-up — opens with float, aggregates all coupon-book sales + single-meal sales for the shift, closes with reconciled total. (See §5.6.) |
| 33 | **Mess Coupon Book Type** | Mess (master) | No | Configurable bundle templates — "10 Lunches @ ₹800", "20 Mixed Meals @ ₹1500", validity days, applicable meal types. (See §5.4.) |

> **Mess Meal Coupon (#18) is removed.** It was resident-only and per-meal; both flows are now covered better by Mess Coupon Book (residents + public, bundle-based) and Mess Single Meal Sale (residents + public, pay-per-meal). The team should not implement #18.

**Total DocTypes:** 32 (22 from existing spec − 1 removed + 11 new = 32).

---

## 2. Staff Attendance Module

### 2.1 Problem

Wardens, mess incharges, cooks, cleaners, guards work across shifts. The hostel needs to:
- Know who is on-site right now (liability, emergencies).
- Compute monthly payable hours (wages).
- Track late arrivals, early departures, absences.
- Honour multiple shift patterns (some staff do split shifts; guards do nights; cooks have 4am starts).

### 2.2 DocType: Hostel Staff (#23)

Fields:
- `full_name`, `user` (Link User, unique), `employee` (Link ERPNext Employee — optional; for payroll)
- `staff_code` (unique, auto), `role_tag` (Warden / Assistant Warden / Mess Incharge / Cook / Cleaner / Security / Maintenance / Other)
- `primary_building` (Link Hostel Building), `primary_mess` (Link Hostel Mess, if applicable)
- `default_shift` (Link Hostel Staff Shift)
- `biometric_user_id` (string, unique; maps to the ID enrolled on the device)
- `mobile`, `emergency_contact`, `photo`, `id_proof_type`, `id_proof_number`
- `joined_on`, `status` (Active / On Leave / Suspended / Separated), `separated_on`
- `hourly_rate` or `monthly_salary` (for wage-hour reports; not payroll — that's ERPNext)

Controller:
- Ensures `biometric_user_id` is globally unique across Hostel Staff + Hostel Resident (biometric IDs don't overlap).
- Enables/disables linked User when status toggles.

### 2.3 DocType: Hostel Staff Shift (#24)

Masters for shift patterns:
- `shift_name` (e.g. "Morning Cook 04:00–12:00")
- `start_time`, `end_time` (supports crossing midnight — e.g. 22:00 → 06:00)
- `grace_minutes` (default 10 — no late flag within grace)
- `break_minutes` (default 0)
- `applicable_weekdays` (multi-check Mon–Sun)
- `expected_hours` (computed read-only)
- `status` (Active / Inactive)

### 2.4 DocType: Hostel Staff Attendance (#25)

One row per staff × date. Not submittable (mutated throughout the day as punches come in).

Fields:
- `staff` (Link Hostel Staff), `attendance_date`, `shift` (Link Hostel Staff Shift)
- `check_in_time`, `check_out_time` (datetime)
- `source` (Biometric / Manual / Mobile / Warden-Entered)
- `biometric_events` (read-only list of Link Hostel Biometric Event for audit)
- `status` (Present / Absent / Half-Day / On Leave / Holiday / Weekly Off)
- `late_by_minutes`, `early_exit_minutes` (computed)
- `hours_worked` (computed: check_out − check_in − breaks)
- `overtime_hours` (computed: max(0, hours_worked − expected))
- `approved_by` (Link User), `approved_on`, `remarks`

Behaviour:
- First biometric "In" event for the date creates the row and sets `check_in_time`.
- Last biometric "Out" event updates `check_out_time`. Any In/Out in between is appended to `biometric_events` for audit but doesn't overwrite first-in/last-out.
- Manual correction allowed only if `source = Biometric` **and** `approved_by` is set → audit-logged.
- End-of-day scheduler `close_open_attendance` stamps check_out = shift.end_time for rows with only a check-in (and flags `auto_closed = 1`).
- Daily scheduler `generate_absent_rows` creates `Absent` rows at 23:59 for active staff with no punch that day (respecting holiday calendar + approved leave).

### 2.5 Workflows

**Routine day (biometric):**
```
Staff punches at gate device
  → Biometric Event created (device, biometric_user_id, timestamp, direction=In)
  → Background worker maps biometric_user_id → Hostel Staff
  → Hostel Staff Attendance row for today: set check_in_time if empty
  → Append event to biometric_events
  → End of shift → punch Out → update check_out_time + compute hours
```

**Manual entry (device down, mobile staff):**
```
Warden → Hostel Staff Attendance list → New
  → Select staff, date, shift, check_in, check_out → Save
  → source = Manual; requires role "Hostel Admin" or "Warden"
  → Audit: field-level change log retained
```

**Leave:**
- Phase 1: simple `status = On Leave` with remarks (warden toggles).
- Phase 2: link to ERPNext Leave Application if `employee` is set (optional, out of scope for v1).

### 2.6 Reports

- **Staff Attendance Summary** — date range, per staff: days present, days absent, late count, total hours, OT hours.
- **Today's Roster** — who is scheduled, who has checked in, who is still missing.
- **Late Arrivals** — filter by building, threshold minutes, date range.
- **Wage Hour Export** — CSV for payroll (staff × month × hours × rate).

### 2.7 Portal / UI surfaces

**Admin back-office (Frappe desk):**
- Hostel Staff list view with status + shift + building filters.
- Hostel Staff Attendance calendar view (month grid per staff).
- "Today's Roster" dashboard card.

**Staff self-service (future, v2):** small PWA or a staff tab inside the existing portal so staff see their own attendance + monthly summary. **Not in v1** — v1 is admin-only because staff headcount is small.

---

## 3. Biometric Integration

### 3.1 Device strategy

Decision required from the team (see §8.Q1) on vendor. This scope assumes one of:
- **ZKTeco / eSSL** (most common in Indian hostels) — pull via their SDK or cloud push over HTTP.
- **Mantra MFS100** (fingerprint USB sensor, browser-attached) — for POS-style punch at a web kiosk.
- **Hikvision / Matrix** (face recognition) — richer logs, ONVIF/HTTP push.

Architecture is **device-agnostic**: one well-defined ingestion endpoint; per-vendor adapter on the outside.

### 3.2 DocType: Hostel Biometric Device (#26)

- `device_name`, `device_code` (unique), `vendor` (ZKTeco / eSSL / Hikvision / Mantra / Other)
- `device_model`, `serial_number`
- `location_type` (Gate / Mess Counter / Office / Block Entry), `building` (Link, optional), `mess` (Link, optional)
- `ip_address`, `port`, `auth_token` (password), `direction_policy` (In Only / Out Only / Bidirectional — for single-direction gate readers)
- `last_heartbeat_at`, `last_sync_at`, `status` (Online / Offline / Disabled), `notes`
- **Controller:** scheduled `ping_devices` updates heartbeat + status.

### 3.3 DocType: Hostel Biometric Event (#27)

Raw log. One row per punch.
- `device` (Link), `biometric_user_id` (string), `event_timestamp` (datetime)
- `direction` (In / Out / Unknown)
- `raw_payload` (long text — JSON from the device for debugging)
- `matched_to` (Link to Hostel Staff OR Hostel Resident — dynamic link; null if unmatched)
- `processing_status` (Pending / Matched / Unmatched / Error), `processing_error`, `processed_at`
- **Indexes:** `(device, event_timestamp)`, `(biometric_user_id)`, `(processing_status)`

Why a raw log + processed target (Staff Attendance / Mess Attendance / Hostel Attendance) rather than writing directly? — Idempotency on replay, debugging, and so the same punch can trigger multiple downstream effects (e.g. a resident's mess entry punch also records them as present for the day).

### 3.4 Ingestion endpoints

Two modes supported:

**A. Device push (preferred, real-time):**
```
POST /api/method/hostel_management.api.biometric.ingest
Auth: per-device bearer token (stored on Hostel Biometric Device.auth_token)
Body: { device_code, events: [{ user_id, timestamp, direction, payload }] }
→ Creates Hostel Biometric Event rows (dedupes on device+user+timestamp)
→ Enqueues processing job
→ 200 { accepted: N, duplicates: M }
```

**B. Scheduled pull (ZKTeco-style SDK):**
```
Worker: hostel_management.biometric.adapters.zkteco.pull_all_devices (every 5 min)
  → For each online device: connect → get_attendance() → diff against last_sync_at
  → Write Hostel Biometric Event rows → update last_sync_at
```

### 3.5 Processing pipeline

```
For each Pending event:
  1. Resolve biometric_user_id:
     - Match Hostel Staff.biometric_user_id → target = staff attendance flow
     - Else match Hostel Resident.biometric_user_id → target = resident attendance / mess
     - Else processing_status = Unmatched (warden alerted via Notification Log)
  2. Determine direction if Unknown:
     - Use device.direction_policy if set
     - Else infer from last event for that user (toggle In/Out)
  3. Route:
     - Staff hit → upsert Hostel Staff Attendance row (first-in / last-out rule §2.4)
     - Resident hit at gate → upsert Hostel Attendance row (present = any in-event that day)
     - Resident hit at mess counter → create Mess Attendance row (validated against active subscription or meal coupon; rejected+logged if neither)
  4. Mark event processed_at / Matched.
```

### 3.6 Failure modes handled

| Failure | Handling |
|---------|----------|
| Device offline | Heartbeat miss > 10 min → status=Offline → alert admin; events buffered on device, synced on reconnect |
| Unmatched user_id | Event stored with `processing_status=Unmatched`; daily digest to admin |
| Duplicate punch | Unique constraint `(device, user_id, timestamp)` — idempotent ingestion |
| Clock drift between devices | `event_timestamp` uses device-local time; admin-configurable offset per device |
| Mess scan with no subscription/coupon | Event processed, Mess Attendance **not** created; counter staff see "No active pass" on the device display; counter can upsell a Mess Guest Pass (§5) |

### 3.7 Enrolment flow

- Admin → Hostel Staff or Hostel Resident → sets `biometric_user_id` (unique).
- On-device enrolment is a manual one-off step (device vendor's own software) — the hostel admin enrols the fingerprint/face with a chosen numeric ID, then pastes that ID into the DocType.
- Self-serve enrolment at a kiosk is **out of scope for v1**.

---

## 4. Website Enquiry Form

### 4.1 Purpose

Public-facing admission intake. Replaces WhatsApp/phone tag with a structured lead pipeline. Lives on the marketing site at `/enquire` (alongside the existing landing `/` and `/terms-of-service`).

### 4.2 DocType: Hostel Enquiry (#28)

Fields (grouped):

**Prospect**
- `full_name`, `email`, `mobile` (required), `gender`, `date_of_birth`
- `city`, `state`, `pincode`

**Academic context (optional — most hostels serve students)**
- `institution_name`, `course`, `year_of_study`

**Guardian**
- `guardian_name`, `guardian_mobile`, `guardian_relationship`

**Preferences**
- `preferred_building` (Link, optional), `preferred_room_type` (Single/Double/Triple/Dormitory/Any)
- `preferred_start_date`, `duration_months`
- `wants_mess` (check), `preferred_mess_plan` (Link Mess Subscription Plan, optional)
- `special_requirements` (text — dietary, accessibility, etc.)

**Provenance**
- `source` (Website / Walk-in / Referral / Instagram / Google Ads / Other)
- `referred_by` (free text)
- `utm_source`, `utm_medium`, `utm_campaign`

**Pipeline**
- `status` (New / Contacted / Visit Scheduled / Offer Sent / Converted / Rejected / Dropped)
- `assigned_to` (Link User — admin or admissions staff)
- `visit_scheduled_on` (datetime), `offer_sent_on` (date)
- `converted_to_resident` (Link Hostel Resident, on conversion)
- `rejected_reason` / `dropped_reason`
- `consent_to_contact` (check, required true — stored for compliance)

**Child table**
- `notes` → Hostel Enquiry Note child (date, by, note)

Controller:
- Auto-assigns `assigned_to` via round-robin across users with role "Admissions" (configurable in Hostel Payment Settings or a dedicated setting).
- On `status = Converted`, prompts admin to create Hostel Resident + Allocation (one-click).
- Rate-limit: max 3 submissions per IP per hour on the public endpoint.

### 4.3 Public form

Route: `/enquire` (Jinja page, no auth). Submits to:
```
POST /api/method/hostel_management.api.enquiry.submit
Body: { form fields above, captcha_token }
→ Verifies hCaptcha or Cloudflare Turnstile token
→ Creates Hostel Enquiry (status=New)
→ Sends confirmation email to prospect (+ SMS optional)
→ Sends admin notification via Hostel Notification Log
→ 200 { enquiry_id, next_step: "We'll call you within 24 hours" }
```

Security:
- CAPTCHA mandatory.
- IP-based rate limiting.
- Honeypot hidden field (bot filter).
- No auth required, but the endpoint cannot set sensitive fields — whitelisted input only.

### 4.4 Admin pipeline view

In Frappe desk:
- Kanban view on Hostel Enquiry grouped by `status`.
- Filters: assigned_to, preferred_building, source, date range.
- Detail view: full form, notes thread, "Schedule Visit" / "Send Offer" / "Convert to Resident" action buttons.

### 4.5 Conversion flow

`Converted` button:
1. Creates a Hostel Resident pre-filled from enquiry (name, contact, guardian, ID proof placeholder).
2. Creates a Frappe User + sends invitation (welcome email with password setup link).
3. Opens a draft Hostel Allocation pre-filled with preferred building/room-type/start-date.
4. Writes back `converted_to_resident` on the enquiry.

### 4.6 Metrics

- **Enquiry Funnel Report** — New → Contacted → Visit → Offer → Converted, with drop-off % and time-in-stage.
- **Source Attribution** — conversions split by source / utm_campaign.

---

## 5. Cafeteria — Coupons & Single Meals (simplified model)

### 5.1 Two flows, anyone can buy

The cafeteria sells meals to **two kinds of buyers** — residents and the general public — but the business model treats them **identically**: same price, same flow. The only rule that matters is "did you pay for this meal?" Identity is incidental, not gating.

There are exactly **two ways to pay**:

| Flow | What it is | Who buys | Settles via |
|------|-----------|----------|-------------|
| **1. Coupon Book** | Prepaid bundle of meals (e.g. "10 lunches for ₹800"). Buyer holds a wallet of remaining meals; redeems one per visit. | Residents (via portal) **and** public (at counter or online). | One upfront payment when the book is bought. |
| **2. Single Meal Sale** | One meal, paid right now at the counter (or via UPI QR on the wall). Walk in, pay, eat, leave. | Anyone — residents who didn't subscribe + public walk-ins. | Per-transaction cash / UPI / card. |

That's it. No buyer-tier pricing, no host-resident logic, no KYC tiers, no capacity caps, no separate "guest pass" entity. If you've paid (via either flow), you eat. If you haven't, you don't.

### 5.2 The two DocTypes (replaces #30/#31/#32 from the earlier draft)

| # | DocType | Submittable | Purpose |
|---|---------|:-----------:|---------|
| 30 | **Mess Coupon Book** | Yes | A prepaid bundle: holder, meals_total, meals_remaining, price paid, expiry. Issued on payment. Decrements as redeemed. |
| 31 | **Mess Single Meal Sale** | Yes | One walk-in transaction: meal, amount, payment method, payment reference. Submitted = paid. |
| 32 | **Mess POS Session** | Yes | Daily counter cash-up — opening float, all coupon-book sales + single-meal sales for the shift, closing cash count, variance. (Same as before, just consumes the simpler upstream DocTypes.) |

Note: the existing **Mess Meal Coupon (#18)** from the original spec is **subsumed by Mess Coupon Book** — that earlier doctype was per-meal and resident-only. Removing it; the team should delete it from the build list. Total DocType count stays at 32.

### 5.3 DocType: Mess Coupon Book (#30)

A book is a wallet of meal credits.

Fields:
- `book_number` (auto, unique — `MCB-2026-00042`)
- `mess` (Link Hostel Mess), `book_type` (Link to a master `Mess Coupon Book Type` — defines bundle: e.g. "10 Lunches", "20 Mixed Meals", "5 Dinners")
- `holder_type` (Resident / Public)
- `resident` (Link Hostel Resident — required if holder_type=Resident)
- `holder_name`, `holder_mobile` (required if holder_type=Public; auto-filled from resident otherwise)
- `meals_total` (int — denormalised from book_type)
- `meals_remaining` (int — starts at meals_total, decrements on redemption)
- `meal_constraints` (long text or JSON — which meal types this book covers; e.g. `["Lunch"]` or `["Breakfast","Lunch","Snacks","Dinner"]`)
- `unit_price` (computed: book_price ÷ meals_total — used to record revenue per meal as it's consumed)
- `book_price`, `payment_method`, `payment_reference`, `pos_session` (the session it was sold in, if at counter)
- `purchased_on`, `valid_until` (default 90 days from purchase, configurable on book type)
- `qr_code` (ro — printed/displayed; this is what gets scanned at every meal redemption)
- `status` (Active / Exhausted / Expired / Refunded / Cancelled)
- `hostel_invoice` (Link — for online purchases via Razorpay)
- `notes`

Behaviour:
- On submit (= "book is paid for"): `meals_remaining = meals_total`, `status = Active`, QR generated.
- Each redemption: scan QR at the counter → `meals_remaining -= 1` → write a Mess Attendance row → if `meals_remaining = 0` → `status = Exhausted`.
- On `valid_until` reached with `meals_remaining > 0` → daily scheduler flips `status = Expired`. (Refund policy on expiry is a business call — **Q12** in §8.)
- One book can serve a group: a holder can redeem two meals back-to-back at the counter (e.g. "I'm buying lunch for myself and a friend") — the counter UI lets you choose `Redeem N` from a single book in one tap. Each redemption writes its own Mess Attendance row.

### 5.4 DocType: Mess Coupon Book Type (master, simple — counts as new DocType #33; bumping inventory)

Defines the bundles offered. Pre-seeded by admin; resident portal + counter both pick from this list.

Fields:
- `type_code` (e.g. `LUNCH-10`, `MIXED-20`)
- `display_name` (e.g. "10 Lunches Pack")
- `meals_total`, `applicable_meals` (multi-select: Breakfast/Lunch/Snacks/Dinner)
- `price`
- `validity_days` (default 90)
- `is_active`

This master makes pricing changes painless — admin updates the master, every new book uses the new price; existing books are immutable (price was fixed at purchase).

### 5.5 DocType: Mess Single Meal Sale (#31)

The simplest possible transaction: one row = one meal sold.

Fields:
- `sale_number` (auto, unique short — `MSM-20260419-0123`)
- `mess`, `meal_date`, `meal_type` (Breakfast / Lunch / Snacks / Dinner)
- `buyer_name` (optional — only captured if buyer asks for a receipt or pays by UPI which gives us a name)
- `buyer_mobile` (optional)
- `quantity` (int, default 1 — supports "2 lunches please")
- `unit_price`, `total_amount`
- `payment_method` (Cash / UPI / Card / Razorpay)
- `payment_reference` (UPI transaction ID, last-4 of card, Razorpay payment_id)
- `pos_session` (Link — auto-filled to the open session at the counter)
- `token_number` (per-session sequential — what gets shouted: "Token 47")
- `qr_code` (optional — only generated if the mess uses scan-on-entry; for small messes the token + paper receipt is enough)
- `status` (Paid / Refunded / Cancelled)
- `hostel_invoice` (Link — only created if the buyer asks for a GST bill)
- `sold_by` (Link User), `sold_at`

Behaviour:
- On submit, status=Paid, the sale is final, payment is in. Mess Attendance row is written immediately (`source = Single Meal`).
- Refund: counter staff can void within the same POS session with reason → status=Refunded, attendance row deleted, cash returned.

### 5.6 DocType: Mess POS Session (#32)

Same structure as the original §5.4 — opening float, transactions, closing cash, variance — but it now aggregates **two** child transaction sources instead of one:

- All Mess Coupon Book sales submitted during the session (bookings of new books).
- All Mess Single Meal Sale rows submitted during the session.

Both contribute to the session's cash/UPI/card totals. Coupon **redemptions** (using an already-paid book) don't touch the session — no money changes hands at redemption time.

### 5.7 How each scenario is paid for

Re-reading the original four scenarios through the simplified model:

| Original scenario | How it's billed now |
|-------------------|---------------------|
| A. Resident wants one-off meal, no subscription | Single Meal Sale at counter, OR resident bought a Coupon Book earlier and redeems one. |
| B. Resident's friend visits | Single Meal Sale at counter. (Resident can pay, or friend can pay — system doesn't care.) |
| C. Parent / alumni visiting | Single Meal Sale at counter. |
| D. Stranger off the street | Single Meal Sale at counter. |

All four collapse to the same flow. **The only field that differs is whether `buyer_mobile` is captured** — and that's optional, only collected if the buyer wants a receipt.

### 5.8 Tracking single-meal payments — the answer to your question

This is the critical part. Three layers of tracking, each serving a different need:

**Layer 1 — Per-transaction (the receipt):**
Every single meal sold creates a Mess Single Meal Sale row, immediately on payment. The row has:
- the **payment method** (Cash / UPI / Card / Razorpay) and a **payment reference** (UPI ref, card last-4, Razorpay payment_id) — so you can always trace any sale back to a bank-side transaction
- a **token number** (visible to the buyer) and a **sale number** (visible internally)
- a **timestamp + counter staff who issued it**

For UPI specifically: the counter has a **static UPI QR code** (one per mess, printed on a board). Buyer scans, pays, shows the "Paid ₹120 to ABC Mess" screen → counter staff key in the UPI ref into the Sale row → submit. For higher trust, a dynamic-QR PSP integration (Razorpay QR, PhonePe Smart QR) auto-creates a Razorpay Payment row whose webhook posts back to the server and **the sale is created automatically** when the webhook fires — no manual entry. (Recommended where the volume justifies it.)

**Layer 2 — Per-shift (the cash drawer):**
At end of shift, the Mess POS Session closes. The session's auto-totals show:
- Total cash sales (sum of cash-method sales in the session)
- Total UPI sales (with all UPI references listed for cross-check)
- Total card sales
- Total Razorpay sales (auto-reconciled from gateway)
- Closing cash counted by incharge
- **Variance** (cash counted − opening float − cash sales) — this is the daily proof that no cash was lost or stolen.

A non-zero variance flags the session as Disputed and pages the admin. So even though individual single-meal sales are tiny, **the shift-level cash-up is the audit gate**.

**Layer 3 — Daily ledger (the books):**
On POS Session submit, the system creates **one consolidated ERPNext Payment Entry per payment method**:
- "Cash receipts — Lunch shift 19 Apr — ₹4,520" (one entry, references session)
- "UPI receipts — Lunch shift 19 Apr — ₹6,830" (one entry)
- "Card receipts — Lunch shift 19 Apr — ₹1,200" (one entry)

This keeps the accountant's books clean: instead of 200 individual ₹100 entries cluttering the journal, there are 3–4 lines per shift. Drill-down to the session always shows the full transaction list.

Together: **every rupee is traceable** (Layer 1), **every shift balances** (Layer 2), **every day posts to the books cleanly** (Layer 3).

### 5.9 Pricing — single tier

Hostel Mess gets one price column per meal — no resident vs guest vs public split:

- `breakfast_price`, `lunch_price`, `snacks_price`, `dinner_price`

That's the price for everyone. The mess incharge picks the price based on cost-plus-margin, and it applies whether the buyer is a resident, a friend, or a stranger. Coupon Book Types layer their own bundle pricing on top (a "10 Lunches" book at ₹800 effectively prices each meal at ₹80 vs single-meal price of ₹100 — that's the customer's incentive to commit upfront).

If the team later wants discounted rates for residents (likely), it's a small future change: add a `resident_discount_pct` field on Hostel Mess. **Out of scope for v1** — keep it simple.

### 5.10 Counter UI (replaces §5.6 from earlier draft)

Route: `/mess-pos/`. Single-screen, three-button layout optimised for speed at peak:

```
┌─────────────────────────────────────────────────┐
│  [BREAKFAST] [LUNCH ●]  [SNACKS] [DINNER]       │  ← meal selector
├─────────────────────────────────────────────────┤
│                                                 │
│   ┌───────────────┐      ┌───────────────┐      │
│   │  SCAN COUPON  │      │  SELL MEAL    │      │  ← two big buttons
│   │     BOOK      │      │  (₹100)       │      │
│   └───────────────┘      └───────────────┘      │
│                                                 │
│   Today: 47 sold · ₹4,700 · Session #12 OPEN   │  ← live status
└─────────────────────────────────────────────────┘
```

**SCAN COUPON BOOK** path:
1. USB scanner reads QR → fetch book → check active + has remaining + meal allowed → "Aarav Sharma · 7 lunches left" → tap **Redeem** → −1 → Mess Attendance written → done. (~3 seconds.)

**SELL MEAL** path:
1. Tap → modal shows Quantity + payment method (big buttons: Cash · UPI · Card).
2. Pick method → for UPI, optional field for transaction ref (or skip if using Razorpay-QR auto-confirm).
3. Submit → token number prints/displays → done. (~5 seconds for cash, ~10 for UPI manual ref.)

Both paths default to the currently-selected meal type — no extra clicks needed at peak rush.

A "More" menu has: open/close session, view today's sales list, refund/void.

### 5.11 Resident portal additions

In the existing portal's Mess tab, replace the old "Coupons" sub-tab with **"Coupon Books"**:
- List of book types with prices and per-meal effective rate ("₹80/lunch — save ₹20").
- Buy → Razorpay → on success, a Mess Coupon Book is issued and the QR is displayed in the portal (resident can screenshot it or print).
- Active books shown with `meals_remaining` and `valid_until` countdown.
- Past books shown collapsed.

Public buyers do **not** get a portal — they buy at the counter (cash/UPI) or, optionally, via a public `/cafeteria/buy-coupon-book` page on the website that runs Razorpay and emails the QR. The public page is **post-v1** unless the business specifically wants it.

### 5.12 Mess Attendance — unified entry log

`Mess Attendance.source` enum collapses to:
- `Subscription` — from an active Mess Subscription
- `Coupon Book` — from a Mess Coupon Book redemption (replaces old "Coupon" source)
- `Single Meal` — from a Mess Single Meal Sale

The mess incharge sees one "who ate today" table; filter chips break it down by source.

### 5.13 What we're explicitly NOT building (vs the earlier draft)

To stay simple, the following — present in the earlier §5.12 — are **dropped**:

- ❌ Buyer tiers (Resident / Named Guest / Public Walk-in) and 3-tier pricing
- ❌ KYC policy levels (None / Mobile-only / Strict)
- ❌ `host_resident` linkage and host-guest frequency reports
- ❌ Per-meal capacity caps for public walk-ins (`max_walk_in_seats_*`)
- ❌ "Charge to Room" credit billing
- ❌ Cafeteria Mode kill-switch (it's just always on, because there's no operational difference)

If any of these become important later, the data model accommodates them (add fields, don't restructure). But shipping without them removes a lot of UI complexity and business decisions.

### 5.14 Reports

- **Single Meal Sales** — date range, split by meal, payment method.
- **Coupon Book Sales** — books sold, by type, by holder type (resident vs public).
- **Coupon Book Redemption Rate** — meals redeemed / meals sold per book type. Identifies bundles that go unused (signals expiry-refund risk).
- **Daily Cafeteria Revenue** — single meals + coupon books, by mess, by day.
- **POS Cash Reconciliation** — daily variance.
- **Outstanding Coupon Liability** — sum of (`meals_remaining × unit_price`) across all active books — this is money you owe the customers as future meals.
- **Expired Books with Unused Meals** — surface for refund / goodwill credit decisions.

### 5.15 Compliance — kept (lighter)

If the cafeteria sells to the public regularly:
- Mess Single Meal Sale auto-generates a Hostel Invoice with GST breakdown when total ≥ `gst_invoice_threshold` (default ₹1000), or when buyer ticks "I need a GST bill" at the counter.
- FSSAI licence number printed on every receipt.
- Below-threshold sales just get a token paper slip (no Hostel Invoice row needed — the Mess Single Meal Sale row itself is the audit record).

The full compliance checklist (FSSAI, GST registration, municipal permit, insurance, fire/hygiene) from the earlier draft remains the hostel admin's responsibility — see §8.Q11.

---

## 6. Cross-cutting Concerns

### 6.1 New roles

| Role | Added for | Scope |
|------|-----------|-------|
| **Admissions** | §4 | Read/write Hostel Enquiry, convert to Resident. Read-only on residents/rooms. |
| **Mess Counter Staff** | §5 | Open/close POS Session, create Mess Guest Pass, scan QR. No access to menu/subscription admin. |
| **Biometric Admin** | §3 | Configure devices, view raw events, resolve unmatched events. |

Update role permission table in §6 of the existing spec to include these three + all new DocTypes.

### 6.2 Notifications additions

| Event | Channel | Recipient |
|-------|---------|-----------|
| New enquiry submitted | Email + desk notification | Admissions assignee + admin |
| Enquiry unassigned > 24h | Email | Admin |
| Biometric device offline > 10 min | Email + SMS | Biometric Admin |
| Unmatched biometric event daily digest | Email | Biometric Admin |
| Staff late arrival | Email | Building warden (their manager) |
| Staff absent without leave | Email | Warden + admin |
| POS session closed with variance | Email | Admin |
| Coupon book expiring in 7 days with unused meals | SMS + email | Holder (resident or public mobile) |
| Coupon book expired with unused meals | Internal | Mess incharge (for refund/goodwill review per §8.Q12) |

### 6.3 Scheduler additions (append to `hooks.py`)

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
  "hostel_management.mess.pos.auto_close_stale_sessions",
  "hostel_management.biometric.processing.send_unmatched_digest",
  "hostel_management.cafeteria.coupon_book.expire_books",
  "hostel_management.cafeteria.coupon_book.send_expiry_reminders",
],
```

### 6.4 Reports consolidated (added to §10 of existing spec)

- Staff Attendance Summary
- Today's Roster
- Late Arrivals
- Wage Hour Export
- Enquiry Funnel
- Enquiry Source Attribution
- Single Meal Sales (by date / meal / payment method)
- Coupon Book Sales (by type, by holder type)
- Coupon Book Redemption Rate (per book type)
- Daily Cafeteria Revenue (single meals + coupon books)
- POS Cash Reconciliation
- Outstanding Coupon Liability (sum of meals_remaining × unit_price across active books)
- Expired Books with Unused Meals
- Biometric Device Health

---

## 7. Delivery Plan

### 7.1 Phase sequencing (builds on the existing roadmap in §12)

Existing phases 0–9 remain. New phases slot in as follows:

| Phase | Name | Depends on | Deliverable |
|-------|------|-----------|-------------|
| 2.5 | **Website Enquiry module** | Phase 2 (Hostel Resident exists) | DocTypes #28–29, public form, admin kanban, conversion flow |
| 6.5 | **Staff module + admin UI** | Phase 1 (scaffold), Phase 7 (roles) | DocTypes #23–25, staff list/calendar views, attendance reports |
| 6.6 | **Biometric integration** | Phase 6.5 + Phase 2 | DocTypes #26–27, ingestion endpoint, first vendor adapter (pick one per §8.Q1), processing pipeline |
| 6.7 | **Cafeteria POS** | Phase 3 (mess engine) | DocTypes #30–33, counter Vue app (scan-coupon + sell-single-meal), POS reconciliation, ERPNext Payment Entry posting, optional thermal printer + UPI dynamic-QR |

So the updated full sequence is:
`0 → 1 → 2 → 2.5 → 3 → 4 → 5 → 6 → 6.5 → 6.6 → 6.7 → 7 → 8 → 9`.

### 7.2 Parallelism

After Phase 1 (scaffold), three streams can run in parallel with separate owners:

- **Stream A (Core + Mess):** Phases 2 → 3 → 4 → 6 → 6.7
- **Stream B (Admissions):** Phase 2.5 (can start in parallel with 3 once Resident DocType lands)
- **Stream C (Staff + Biometric):** Phase 6.5 → 6.6 (can start any time after Phase 1)

Public website (Phase 5) and portal (Phase 6) can proceed independently once their API contracts are stubbed.

### 7.3 Testing strategy for new modules

**Staff Attendance:**
- Unit: shift calculation with midnight crossover, late/early computation, absent row generation.
- Integration: biometric event → attendance row upsert end-to-end; manual correction audit log.

**Biometric:**
- Device adapter contract tests (mock device push + SDK pull).
- Idempotency: replay same batch → no duplicates.
- Processing: matched/unmatched/direction-inference cases covered.
- Load test: 1000 events/minute (peak mess rush simulation).

**Enquiry:**
- Unit: CAPTCHA bypass rejected, rate limit triggers.
- E2E: public form submit → admin sees lead → convert → resident + user created.

**Cafeteria POS (Coupon Books + Single Meal Sales):**
- Unit: coupon-book decrement, expiry transition, variance calculation, single-meal price computation, refund/void.
- E2E (Playwright, on counter app):
  - Sell single meal (cash) → token displayed → Mess Attendance written.
  - Sell single meal (UPI with manual ref) → submitted → counted in session totals.
  - Buy coupon book at counter → QR generated → scan QR → redeem 1 → meals_remaining decrements → Mess Attendance written.
  - Redeem until exhausted → status flips to Exhausted → next scan shows "no meals left".
  - Open session → sell N → close session → variance = 0 → Payment Entries created in ERPNext.
- Hardware: printer/scanner in staging; UPI dynamic-QR webhook flow (if used).

### 7.4 Estimated effort (rough — team to refine)

| Phase | Backend days | Frontend days | Notes |
|-------|:---:|:---:|-------|
| 2.5 Enquiry | 3 | 2 | Single public form + kanban |
| 6.5 Staff | 4 | 2 | Desk-only admin UI; no SPA |
| 6.6 Biometric | 6 | 1 | One vendor adapter; events UI is desk list |
| 6.7 Cafeteria POS | 4 | 4 | Simpler than the original 3-tier model — two flows, one price column |
| **Total add-on** | **17** | **9** | **~5 person-weeks incremental** |

---

## 8. Open Questions (decide before build)

These items need product / business decisions. Flag them at the team kickoff:

**Q1. Biometric vendor.** Which device are we standardising on? The adapter layer supports any, but we only build one in v1. Recommendation: ZKTeco (widest distribution, Python SDK mature, cheapest hardware).

**Q2. Enrolment responsibility.** Who enrols a new resident's fingerprint — the resident at a kiosk, or the warden? Affects whether we need a kiosk app in v1 (answer: assume warden for v1).

**Q3. Staff payroll integration.** Do we push wage-hours to ERPNext Payroll, or does the hostel export CSV to their accountant? Affects whether Phase 6.5 depends on ERPNext HRMS.

**Q4. ~~Charge-to-room ceiling.~~** **Not applicable** in simplified model — cafeteria is pay-at-counter only. (Skip.)

**Q5. ~~Guest pricing differential.~~** **Not applicable** in simplified model — single price per meal for everyone. If a resident discount is wanted later, add `resident_discount_pct` to Hostel Mess as a future change. (Skip for v1.)

**Q6. Captcha provider.** hCaptcha (free) or Cloudflare Turnstile (if already on Cloudflare)?

**Q7. Thermal printer.** Are we buying printers for mess counters, or is on-screen QR acceptable? (On-screen is cheaper + greener.)

**Q8. Multi-hostel tenancy.** The existing spec says "single-tenant per hostel". Does the enquiry form serve just one hostel, or is there a chain where one form routes to multiple? Affects the `preferred_building` field design.

**Q9. Data retention.** How long do we keep raw Hostel Biometric Event rows? These grow fast (5000 events/day at a 200-resident hostel). Suggest: 90 days hot, archive to cold storage beyond.

**Q10. Guest data privacy.** Guest name + mobile is PII. Do we need explicit consent at the counter, and a retention policy? Affects the counter UI (tick-box) and a scheduler purge job.

**Q11. Cafeteria compliance readiness.** The simplified model treats public sales as just "another single-meal sale", but the licences below remain the hostel admin's responsibility before serving the public commercially:
  - FSSAI food-service licence covers commercial sale to the public (not just residents).
  - GST registration if annual cafeteria turnover crosses the services threshold.
  - Local municipal / shop-and-establishment licence permits public food service at the address.
  - Hostel insurance covers third-party food liability.
  - Fire + hygiene inspections current.

  Software can't ship enforcement of these — they're paperwork. Confirm before go-live.

**Q12. Coupon book expiry refund policy.** When a Mess Coupon Book expires with `meals_remaining > 0`:
  - (a) Forfeit (no refund) — simplest, fairest to the business.
  - (b) Pro-rata cash refund — at the unit_price recorded on the book.
  - (c) Goodwill credit — auto-issue a new short-validity book worth the remaining meals.

  Recommendation: **(a) Forfeit**, with a 7-day pre-expiry SMS reminder so customers can come use them. Easy to revisit if customers complain.

**Q13. UPI flow at the counter.** Two options for collecting UPI payments:
  - (a) Static QR poster on the wall + counter staff manually keys in the UPI ref. Cheap, slower, error-prone.
  - (b) Razorpay QR / PhonePe Smart QR (dynamic per-transaction, webhook auto-creates the sale). Costs PSP fees, faster, no manual entry, harder to fraud.

  Recommendation: start with (a) at low volume, switch to (b) once daily UPI volume justifies the PSP fee.

---

## 9. Appendix — DocType dependency graph (new modules)

```
Hostel Biometric Device ──┐
                          ├──► Hostel Biometric Event ──► Hostel Staff Attendance
Hostel Staff ─────────────┤                         │
                          │                         ├──► Hostel Attendance (resident)
Hostel Resident ──────────┘                         └──► Mess Attendance

Hostel Enquiry ──(convert)──► Hostel Resident ──► Hostel Allocation
     │
     └──► Hostel Enquiry Note (child)

Mess Coupon Book Type ──► Mess Coupon Book ──┐
                              ▲              ├──► Mess Attendance (on each redemption, decrements meals_remaining)
                              │              │
Mess POS Session ─────────────┤              │
       │                      │              │
       └──► Mess Single Meal Sale ───────────┤
                              │              │
                              └──► Hostel Invoice (Razorpay payments + GST-bill requests)
```

The session aggregates both Mess Coupon Book purchases and Mess Single Meal Sales for cash-up. Coupon redemptions don't touch the session (no money moves at redemption time — money was collected when the book was sold).

---

## 10. Sign-off checklist

Before the team starts Phase 2.5, confirm:

- [ ] Product owner has answered Q1–Q13 in §8 (Q4, Q5 marked N/A in simplified model).
- [ ] Biometric device procured + network access confirmed for staging.
- [ ] Razorpay test keys already in `Hostel Payment Settings` (prerequisite, existing).
- [ ] Role matrix in existing spec §6 updated with Admissions / Mess Counter Staff / Biometric Admin.
- [ ] Mess counter hardware decided (scanner mandatory; thermal printer optional; tablet form-factor).
- [ ] Cafeteria compliance (§8.Q11) signed off by ops before serving the public commercially.
- [ ] Coupon Book Type catalogue seeded (e.g. "10 Lunches @ ₹800", "20 Mixed @ ₹1500").
- [ ] Coupon expiry refund policy decided (§8.Q12).
- [ ] UPI collection mode decided (static QR vs PSP dynamic QR — §8.Q13).
