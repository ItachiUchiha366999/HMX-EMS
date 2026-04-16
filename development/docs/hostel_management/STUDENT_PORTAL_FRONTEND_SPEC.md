# Hostel Student Portal — Frontend Developer Specification

> **Audience:** Frontend engineer / designer building the resident-facing Student Portal.
> **Stack:** Vue 3 + Vite + Pinia + Vue Router + TailwindCSS. Axios (or `fetch`) for REST.
> **Backend:** Frappe 15 (the `hostel_management` Frappe app).
> **Auth:** Frappe session cookies (httpOnly). No JWT — rely on CSRF token for writes.
> **Deployment:** Mounted at `/hostel-portal/` (SPA served by Frappe Jinja loader, Vite assets hashed).

---

## 1. Purpose

The Student Portal is the **self-service** surface for a hostel resident. A resident can:

1. See a **dashboard** with allocation, balance, subscription status, today's menu.
2. View their **room, roommates, amenities, check-in date, rent**.
3. Browse **mess menu** (today, week), **subscribe to a mess plan**, **buy one-time meal coupons**, and **manage subscription** (pause, resume, cancel).
4. See all **invoices**, **pay online via Razorpay**, download **receipts**.
5. Raise and track **maintenance requests**.
6. View and update **profile**, guardian contact, ID proof, password.
7. See **visitor log** for their room.

The portal is **responsive (mobile-first)**: a resident must be able to do everything from a phone.

---

## 2. Information Architecture & Routes

```
/hostel-portal/                         → redirect to /dashboard (if logged in)
/hostel-portal/login                    → handled by Frappe; redirect here on 401
/hostel-portal/dashboard                → home / overview
/hostel-portal/room                     → room & allocation details
/hostel-portal/mess                     → mess landing (tabs: Menu | Subscription | Coupons)
  /hostel-portal/mess/menu              → today + week menu
  /hostel-portal/mess/subscription      → manage subscription
  /hostel-portal/mess/subscribe/:planId → subscribe flow
  /hostel-portal/mess/coupons           → buy one-time coupons
/hostel-portal/payments                 → invoices & payment history
  /hostel-portal/payments/:invoiceId    → invoice detail + Pay button
/hostel-portal/maintenance              → list of requests
  /hostel-portal/maintenance/new        → new request form
  /hostel-portal/maintenance/:id        → request detail
/hostel-portal/visitors                 → visitor log (read-only)
/hostel-portal/profile                  → profile + settings
  /hostel-portal/profile/password       → change password
/hostel-portal/notifications            → notification center
```

### 2.1 Navigation

**Desktop (sidebar):** Dashboard · My Room · Mess · Payments · Maintenance · Visitors · Profile · Logout
**Mobile (bottom tab bar):** Dashboard · Room · Mess · Pay · More (drawer)

Top bar: hostel logo (left), notification bell + avatar menu (right).

---

## 3. Authentication & Session

### 3.1 Login
- Portal is protected. If the SPA boots and the session check fails, redirect to `/login?redirect-to=/hostel-portal/dashboard`.
- Frappe handles login page. On success, user returns to the portal with a valid session cookie.

### 3.2 Session bootstrap
On app mount, call:
```
GET /api/method/hostel_management.api.portal.bootstrap
→ 200 { message: { user, resident, roles, settings, csrf_token } }
→ 401 → redirect to login
```
Store in Pinia `authStore`.

### 3.3 CSRF for writes
All POST/PUT/DELETE must send header:
```
X-Frappe-CSRF-Token: <csrf_token from bootstrap>
```

### 3.4 Logout
```
POST /api/method/logout
→ clear Pinia stores → router.push('/login')
```

---

## 4. REST API Contract

All endpoints live under `/api/method/hostel_management.api.*` and return the Frappe convention `{ "message": <payload> }`. Error shape: `{ "exc_type": "...", "exc": "...", "_server_messages": "..." }` with 4xx/5xx.

### Conventions
- **Base URL**: same origin (SPA served by Frappe) — no CORS.
- **Auth**: session cookie automatically sent; include `X-Frappe-CSRF-Token` for writes.
- **Dates**: ISO-8601 `YYYY-MM-DD` or `YYYY-MM-DDTHH:mm:ss`.
- **Currency amounts**: always numbers in INR (no string formatting).
- **Pagination**: `?limit_start=0&limit_page_length=20`.

### 4.1 Portal Identity
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/method/hostel_management.api.portal.bootstrap` | Session, resident profile, settings, CSRF token |
| GET | `/api/method/hostel_management.api.portal.dashboard` | Home-screen aggregate |

**`bootstrap` response example**
```json
{
  "message": {
    "user": "aarav.sharma@example.com",
    "resident": {
      "name": "HR-2026-00017",
      "full_name": "Aarav Sharma",
      "email": "aarav.sharma@example.com",
      "mobile": "+91-98XXXXXX01",
      "photo": "/files/residents/aarav.jpg",
      "status": "Active"
    },
    "roles": ["Hostel Resident"],
    "settings": {
      "razorpay_key_id": "rzp_test_XXXX",
      "currency": "INR",
      "company_name": "Acme Hostel",
      "company_logo": "/files/logo.png",
      "support_email": "help@acmehostel.in",
      "support_phone": "+91-98XXXXXX77"
    },
    "csrf_token": "…"
  }
}
```

**`dashboard` response example**
```json
{
  "message": {
    "allocation": {
      "name": "HA-2026-00042",
      "building": "A Block",
      "room": "A-204",
      "bed_number": 2,
      "from_date": "2026-01-10",
      "to_date": "2026-12-31",
      "rent_per_month": 8500,
      "status": "Active"
    },
    "balance_due": 12500,
    "next_due_date": "2026-05-01",
    "subscription": {
      "name": "MS-2026-00011",
      "plan": "Monthly Veg",
      "status": "Active",
      "current_period_end": "2026-04-30",
      "next_invoice_date": "2026-05-01",
      "auto_renew": true
    },
    "today_menu": {
      "mess": "Main Mess",
      "meals": [
        {"meal_type": "Breakfast", "items": "Idli, Sambar, Chutney"},
        {"meal_type": "Lunch", "items": "Rice, Dal, Paneer, Roti, Salad"},
        {"meal_type": "Snacks", "items": "Samosa, Tea"},
        {"meal_type": "Dinner", "items": "Rice, Rajma, Roti, Kheer"}
      ]
    },
    "recent_payments": [
      {"invoice": "HINV-2026-00031", "amount": 8500, "date": "2026-04-01", "status": "Paid"}
    ],
    "open_maintenance_count": 1,
    "unread_notifications": 3
  }
}
```

### 4.2 Room
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/method/hostel_management.api.portal.my_room` | Allocation + room details + roommates |

**Response**
```json
{
  "message": {
    "allocation": { ... },
    "room": {
      "room_number": "A-204", "floor": 2, "room_type": "Double",
      "amenities": {
        "attached_bathroom": true, "ac": true, "balcony": false,
        "study_table": true, "wardrobe": true, "hot_water": true
      },
      "rent_per_month": 8500, "security_deposit": 15000
    },
    "building": {
      "name": "A Block", "hostel_type": "Boys", "warden": "Mr. Rao",
      "address": "…", "contact_number": "+91-80XXXXXX"
    },
    "roommates": [
      {"full_name": "Rohit Verma", "bed_number": 1, "photo": "/files/residents/rohit.jpg"}
    ]
  }
}
```

### 4.3 Mess
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `…portal.mess_today` | Today's menu for resident's mess |
| GET | `…portal.mess_week?start_date=YYYY-MM-DD` | 7-day menu |
| GET | `…portal.mess_plans` | Available subscription plans |
| GET | `…portal.my_subscription` | Current subscription (or null) |
| POST | `…portal.subscribe_mess` | Start a subscription (returns invoice+order for payment) |
| POST | `…portal.pause_subscription` | Pause |
| POST | `…portal.resume_subscription` | Resume |
| POST | `…portal.cancel_subscription` | Cancel (body: `{refund_policy: "prorata"|"none"}`) |
| POST | `…portal.buy_meal_coupon` | Purchase one-time coupon |
| GET | `…portal.my_coupons?status=Paid` | List coupons |

**`mess_week` response**
```json
{
  "message": {
    "mess": "Main Mess",
    "week_start_date": "2026-04-13",
    "days": [
      {"day":"Monday","date":"2026-04-13","meals":[{"meal_type":"Breakfast","items":"…","special":false}, ...]},
      ...
    ]
  }
}
```

**`mess_plans` response**
```json
{
  "message": [
    {"name":"MSP-Monthly-Veg","plan_name":"Monthly Veg","billing_interval":"Monthly",
     "cost":3000,"currency":"INR","meals":["Breakfast","Lunch","Snacks","Dinner"],
     "grace_period_days":5,"allow_pause":true,"allow_auto_renew":true},
    {"name":"MSP-Quarterly-Veg","plan_name":"Quarterly Veg","billing_interval":"Quarterly",
     "cost":8500,"currency":"INR","meals":["Breakfast","Lunch","Dinner"], ...}
  ]
}
```

**`subscribe_mess` request / response**
```
POST body: { "plan": "MSP-Monthly-Veg", "start_date": "2026-04-15", "auto_renew": true }
→ 200 { message: {
    "subscription": "MS-2026-00033",
    "invoice": "HINV-2026-00088",
    "razorpay_order": {
      "order_id": "order_XYZ",
      "amount": 150000,         // paise
      "currency": "INR",
      "key_id": "rzp_test_…",
      "prefill": {"name":"…","email":"…","contact":"…"}
    }
} }
```

**`buy_meal_coupon` request / response**
```
POST body: { "meal_date": "2026-04-14", "meal_type": "Lunch", "mess": "Main Mess" }
→ 200 { message: { "coupon": "MMC-…", "invoice": "HINV-…",
                   "razorpay_order": {...same shape as above} } }
```

**`my_subscription` response**
```json
{
  "message": {
    "name":"MS-2026-00011","plan_name":"Monthly Veg","mess":"Main Mess",
    "status":"Active","start_date":"2026-03-15","end_date":"2026-09-14",
    "current_period_start":"2026-04-15","current_period_end":"2026-05-14",
    "next_invoice_date":"2026-05-15","last_invoice_date":"2026-04-15",
    "auto_renew":true,"paused_on":null,
    "invoice_history":[
      {"period_start":"2026-03-15","period_end":"2026-04-14",
       "invoice":"HINV-2026-00061","amount":3000,"status":"Paid","paid_on":"2026-03-15"}
    ],
    "upcoming_invoice_amount":3000
  }
}
```

### 4.4 Payments
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `…portal.my_invoices?status=Unpaid&limit_page_length=20` | Invoice list |
| GET | `…portal.invoice_detail?name=HINV-…` | Single invoice |
| POST | `…api.payments.create_razorpay_order` | Returns order for an existing invoice |
| POST | `…api.payments.verify_payment` | Verify handler response |
| GET | `…portal.receipt_url?invoice=HINV-…` | Signed PDF URL |

**`my_invoices` response**
```json
{
  "message": {
    "total_count": 12,
    "invoices": [
      {"name":"HINV-2026-00088","invoice_date":"2026-04-13","due_date":"2026-04-20",
       "invoice_type":"Mess Subscription","grand_total":3000,"paid_amount":0,
       "balance":3000,"status":"Unpaid"},
      ...
    ]
  }
}
```

**`create_razorpay_order`**
```
POST body: { "invoice": "HINV-2026-00088" }
→ 200 { message: { "order_id":"order_XYZ","amount":300000,"currency":"INR",
                   "key_id":"rzp_test_…","prefill":{...} } }
```

**`verify_payment`**
```
POST body: {
  "razorpay_order_id": "order_XYZ",
  "razorpay_payment_id": "pay_ABC",
  "razorpay_signature":  "..."
}
→ 200 { message: { "status":"success","invoice":"HINV-2026-00088",
                   "invoice_status":"Paid","receipt_url":"/api/method/…" } }
→ 400 { exc: "InvalidSignatureError" }
```

### 4.5 Maintenance
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `…portal.maintenance_list?status=Open` | List own requests |
| POST | `…portal.maintenance_create` | New request |
| GET | `…portal.maintenance_detail?name=MR-…` | Detail |
| POST | `…portal.maintenance_cancel` | Cancel own request (if Open) |

**`maintenance_create`**
```
POST multipart form:
  subject, description, request_type (Electrical|Plumbing|Furniture|Cleaning|AC|Internet|Other),
  priority (Low|Medium|High|Urgent), attachment (file optional)
→ 201 { message: { name: "MR-2026-00012", status: "Open" } }
```

### 4.6 Visitors
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `…portal.my_visitors?from_date=…&to_date=…` | Visitor log for resident |

### 4.7 Profile
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `…portal.profile` | Full profile |
| POST | `…portal.profile_update` | Update mobile, guardian, emergency contact |
| POST | `…portal.change_password` | Password change |
| POST | `…portal.upload_photo` | Multipart photo upload |

### 4.8 Notifications
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `…portal.notifications?unread_only=1&limit=20` | List |
| POST | `…portal.mark_notification_read` | Body: `{name}` or `{all:true}` |

---

## 5. Screen-by-Screen Design Brief

### 5.1 Dashboard
**Goal:** One-glance status; reduce follow-up questions to warden.

Sections (top to bottom on mobile, grid on desktop):

1. **Welcome header** — "Hi Aarav" + resident photo + building/room chip.
2. **Balance card** — outstanding amount (₹12,500), next due date, "Pay Now" CTA (primary).
3. **Subscription card** — plan name, status badge, current period, "Manage" link.
4. **Today's Menu card** — 4 meal rows with items. "See Week" link.
5. **Quick actions row** — Raise Ticket · Buy Coupon · Profile.
6. **Recent payments list** (last 3).
7. **Notifications preview** (last 3 unread).

Empty states for each card (no allocation, no subscription, no balance).

### 5.2 My Room
- Hero image (room photo placeholder) + room number + status.
- Two-column: left — room details (floor, type, rent, deposit); right — amenities as icon grid.
- Roommates strip — avatars with name + bed number.
- Building card — name, warden name + phone (tap-to-call), address, hostel type.

### 5.3 Mess
Tabbed screen: **Menu | Subscription | Coupons**.

**Menu tab:**
- Today big card (meal timeline: Breakfast → Lunch → Snacks → Dinner).
- Weekly table (day rows × meal columns). Highlight today. "Previous week" / "Next week" paginator.
- Special items get a star badge.

**Subscription tab:**
- If none → empty state with "Subscribe Now" → goes to plans picker.
- If active → card with plan, status, period, next invoice amount & date.
  - Invoice history table (period, amount, status, receipt link).
  - Actions: **Pause** (modal: pause until date), **Resume**, **Cancel** (modal: refund policy radio).
  - Toggle: Auto-renew.
- Plans picker → grid of plan cards (cost, interval, included meals, feature list). Click → subscribe flow.

**Subscribe flow:**
1. Plan summary + start date picker (default today).
2. Show pro-rata calculation: "First period ₹1,200 for 12 days, then ₹3,000/month."
3. Confirm → `subscribe_mess` → Razorpay checkout (see §6).
4. Success screen with period dates and "Go to Dashboard".

**Coupons tab:**
- Date picker + meal selector + price preview → Buy.
- Active coupons list with **QR code** (tap to enlarge for scanning at counter).
- Past coupons (consumed/expired) under collapsed section.

### 5.4 Payments
- Filter chips: All · Unpaid · Paid · Overdue · Refunded.
- Invoice list: number, date, type, amount, status badge, "Pay" button (if Unpaid).
- Invoice detail page: line items, totals, status timeline, "Pay Now" primary CTA, "Download Receipt" (when Paid).

### 5.5 Maintenance
- List with status chips (Open, In Progress, Completed, Cancelled).
- FAB "+ New Request" → form: subject, type (select), priority (segmented), description (textarea), attachment.
- Detail: status timeline, resolution remarks, cost (if any), cancel button if still Open.

### 5.6 Visitors
Read-only table: date, visitor name, relationship, check-in, check-out, status. Date-range filter.

### 5.7 Profile
- Photo + name + residence info.
- Edit sections: Contact (mobile, email read-only), Guardian, Emergency Contact, Permanent Address.
- ID proof — display uploaded (no edit here; warden handles).
- Actions: Change Password · Logout · View Terms of Service · Contact Support.

### 5.8 Notifications
- List ordered by date desc. Read vs unread visual. "Mark all read".

---

## 6. Razorpay Checkout Integration (Client-side)

Include the SDK:
```html
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>
```

Unified helper:
```ts
// src/lib/razorpay.ts
export async function startRazorpayCheckout(order, invoice, onSuccess, onFailure) {
  const rzp = new window.Razorpay({
    key: order.key_id,
    order_id: order.order_id,
    amount: order.amount,             // paise
    currency: order.currency,
    name: settings.company_name,
    description: `Invoice ${invoice}`,
    image: settings.company_logo,
    prefill: order.prefill,
    notes: { invoice },
    theme: { color: "#2563eb" },
    handler: async (resp) => {
      try {
        const verify = await api.post(
          "hostel_management.api.payments.verify_payment",
          resp
        );
        onSuccess(verify);
      } catch (e) { onFailure(e); }
    },
    modal: { ondismiss: () => onFailure(new Error("dismissed")) }
  });
  rzp.on("payment.failed", onFailure);
  rzp.open();
}
```

Usage (Pay button):
```ts
const order = await api.post("hostel_management.api.payments.create_razorpay_order", { invoice });
await startRazorpayCheckout(order, invoice,
  (res) => { toast.success("Payment successful"); router.push(`/payments/${invoice}`); },
  (err) => { toast.error("Payment failed"); console.error(err); }
);
```

> **Source of truth** for invoice status is the server webhook. After `verify_payment` returns success, you can optimistically show Paid; if you re-enter the screen later, refetch from backend.

---

## 7. State Management (Pinia)

```
stores/
  auth.ts          user, resident, roles, settings, csrfToken, isReady
  dashboard.ts     cached dashboard payload (TTL 60s)
  room.ts          my_room payload
  mess.ts          todayMenu, weekMenu (cache key by weekStart), plans, subscription, coupons
  payments.ts      invoices (paginated), invoiceDetail cache, receiptUrls
  maintenance.ts   myRequests (paginated), detailById
  notifications.ts items, unreadCount
```

Each store exposes: `fetch*`, `refresh`, and mutations. Use `storeToRefs` for reactive reads. Clear on logout.

---

## 8. Component Library

**Atoms:** Button (primary/ghost/danger/link), Input, Select, Textarea, Checkbox, Radio, Switch, Badge, Avatar, Skeleton, Spinner, Icon (heroicons or lucide).

**Molecules:** StatusChip, CurrencyAmount, DateChip, EmptyState, FileUpload, Toast, Modal, Drawer, Tabs.

**Organisms:** AppShell (sidebar + topbar + main), MobileTabBar, InvoiceCard, SubscriptionCard, MenuDayCard, MaintenanceCard, RoommateStrip.

---

## 9. Design System

### 9.1 Tokens
| Token | Value |
|-------|-------|
| Primary | `#2563eb` (blue-600) |
| Primary hover | `#1d4ed8` |
| Success | `#16a34a` |
| Warning | `#d97706` |
| Danger | `#dc2626` |
| Surface | `#ffffff` / dark `#0f172a` |
| Muted | `#64748b` |
| Border | `#e2e8f0` / dark `#1f2937` |
| Radius | 8px (sm), 12px (md), 16px (lg) |
| Shadow | `0 1px 2px rgba(0,0,0,.05)` / elevated `0 8px 24px rgba(0,0,0,.08)` |
| Font | Inter, system-ui, sans-serif |
| Font sizes | 12 / 14 / 16 / 18 / 20 / 24 / 30 / 36 |
| Spacing scale | 4, 8, 12, 16, 20, 24, 32, 40, 48 |

Dark mode: support via `prefers-color-scheme` + user override toggle in Profile.

### 9.2 Status Colour Map

| Status | Colour |
|--------|--------|
| Paid / Active / Completed | Success |
| Unpaid / Open / Trial | Primary |
| Partially Paid / In Progress / Paused | Warning |
| Overdue / Past Due / Cancelled / Expired | Danger |
| Refunded | Muted |

### 9.3 Accessibility
- WCAG AA contrast for all text on backgrounds.
- All interactive elements keyboard reachable; visible focus ring.
- Forms: label every input; `aria-invalid` on errors; inline error text with `role="alert"`.
- Modals trap focus; Esc to close.
- Currency spoken correctly (use `<span aria-label="three thousand rupees">₹3,000</span>` where needed).

### 9.4 Responsive Breakpoints
- Mobile: < 640px (base)
- Tablet: 640–1024px
- Desktop: > 1024px (sidebar appears)

---

## 10. Error Handling & UX States

Every screen has four states: **loading, empty, success, error**.

- **Loading:** skeleton placeholders matching final layout (no spinners on full screen except initial bootstrap).
- **Empty:** friendly illustration + one-sentence cause + primary action ("No subscription yet — Browse plans").
- **Error:** inline banner with retry; 401 triggers silent session refresh → if still 401, redirect to login; 403 shows "You don't have access"; 500 shows "Something went wrong" with support email.
- Network offline: toast + queue non-critical retries.

Payment errors to surface clearly:
- Signature mismatch → "Payment verification failed. If money was debited, it will be refunded within 7 days."
- Modal dismissed → silent, allow retry.
- `payment.failed` → show reason + retry CTA.

---

## 11. Performance

- Route-level code splitting (dynamic `import()` per page).
- Prefetch Dashboard on login.
- Cache menu by week (stale-while-revalidate, TTL 10 min).
- Image lazy-load; compressed thumbnails for photos.
- Bundle target: < 200KB gz first paint; < 60KB per route chunk.
- Lighthouse target: Performance ≥ 90 mobile; Accessibility ≥ 95.

---

## 12. Testing

- **Unit (Vitest):** stores, utilities (currency, date, proRata).
- **Component (Vue Testing Library):** forms (validation), cards (status rendering).
- **E2E (Playwright):**
  - Login → Dashboard
  - View menu week
  - Subscribe to plan → Razorpay test mode → success → dashboard shows Active
  - Buy coupon → pay → QR visible
  - Raise maintenance → appears in list → cancel
  - Pay overdue invoice → status Paid
- Use Razorpay's test keys + test card `4111 1111 1111 1111`.

---

## 13. Project Setup

```
hostel-portal-spa/
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/index.ts
│   ├── stores/
│   ├── views/
│   │   ├── Dashboard.vue
│   │   ├── Room.vue
│   │   ├── mess/{Menu,Subscription,Subscribe,Coupons}.vue
│   │   ├── payments/{List,Detail}.vue
│   │   ├── maintenance/{List,New,Detail}.vue
│   │   ├── Visitors.vue
│   │   ├── profile/{Index,Password}.vue
│   │   └── Notifications.vue
│   ├── components/{atoms,molecules,organisms}
│   ├── lib/
│   │   ├── api.ts          // axios + CSRF + 401 redirect
│   │   ├── razorpay.ts
│   │   ├── format.ts       // currency, date
│   │   └── guards.ts       // route guards
│   └── styles/tailwind.css
└── public/
```

Vite build output should write to `frappe-bench/apps/hostel_management/hostel_management/public/hostel-portal-spa/` so Frappe's Jinja loader at `www/hostel-portal/index.html` can read the `manifest.json`.

### 13.1 API client sketch
```ts
// src/lib/api.ts
import axios from "axios";
import { useAuth } from "@/stores/auth";
const client = axios.create({ baseURL: "/api/method/", withCredentials: true });
client.interceptors.request.use((cfg) => {
  const { csrfToken } = useAuth();
  if (csrfToken) cfg.headers["X-Frappe-CSRF-Token"] = csrfToken;
  return cfg;
});
client.interceptors.response.use(
  (r) => r.data?.message ?? r.data,
  (err) => {
    if (err.response?.status === 401) location.href = `/login?redirect-to=${location.pathname}`;
    return Promise.reject(err);
  }
);
export const api = {
  get: (m, params) => client.get(m, { params }),
  post: (m, body) => client.post(m, body),
  upload: (m, form) => client.post(m, form, { headers: {"Content-Type":"multipart/form-data"} })
};
```

---

## 14. Security Checklist

- [ ] Never store Razorpay `key_secret` in the frontend; only `key_id` is exposed.
- [ ] Every write includes `X-Frappe-CSRF-Token`.
- [ ] Session cookies are httpOnly; don't read them via JS.
- [ ] Invoice/subscription actions are authorised server-side against `frappe.session.user` → Hostel Resident mapping.
- [ ] Razorpay handler response is treated as a **claim**; actual status confirmed by webhook.
- [ ] File uploads (photo, maintenance attachment) are size/type validated client-side AND server-side.
- [ ] Avoid logging PII or tokens to analytics.
- [ ] Content Security Policy allows only `checkout.razorpay.com` for scripts; self for the rest.

---

## 15. Delivery Milestones

| M | Scope | Acceptance |
|---|-------|------------|
| M1 | Shell + Auth + Dashboard + My Room | Boot SPA, load real dashboard data, view room |
| M2 | Mess Menu + Coupons | View today/week menu; buy coupon end-to-end with Razorpay test |
| M3 | Mess Subscription | Subscribe, pause, resume, cancel; invoice history visible |
| M4 | Payments + Receipts | Pay any invoice; download receipt PDF |
| M5 | Maintenance + Visitors | Raise/cancel tickets; view visitor log |
| M6 | Profile + Notifications + Dark Mode | Full polish; a11y audit; Lighthouse ≥ 90 |

---

## 16. Appendix

### 16.1 Sample TypeScript Types
```ts
export type Status =
  | "Draft" | "Unpaid" | "Partially Paid" | "Paid" | "Overdue" | "Cancelled"
  | "Refunded" | "Active" | "Paused" | "Past Due" | "Completed" | "Trial"
  | "Open" | "In Progress" | "Expired" | "Consumed" | "Vacated" | "Transferred";

export interface Invoice {
  name: string;
  invoice_date: string;
  due_date: string;
  invoice_type: "Rent" | "Deposit" | "Mess Coupon" | "Mess Subscription" | "Maintenance" | "Other";
  grand_total: number;
  paid_amount: number;
  balance: number;
  status: Status;
}

export interface Subscription {
  name: string;
  plan_name: string;
  mess: string;
  status: Status;
  start_date: string;
  end_date: string;
  current_period_start: string;
  current_period_end: string;
  next_invoice_date: string | null;
  last_invoice_date: string | null;
  auto_renew: boolean;
  invoice_history: Array<{
    period_start: string; period_end: string; invoice: string;
    amount: number; status: Status; paid_on: string | null;
  }>;
  upcoming_invoice_amount: number;
}

export interface MenuDay {
  day: "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday" | "Saturday" | "Sunday";
  date: string;
  meals: Array<{ meal_type: "Breakfast"|"Lunch"|"Snacks"|"Dinner"; items: string; special: boolean }>;
}
```

### 16.2 cURL smoke tests
```bash
# Bootstrap
curl -b cookie.txt 'https://hostel.local/api/method/hostel_management.api.portal.bootstrap'

# Dashboard
curl -b cookie.txt 'https://hostel.local/api/method/hostel_management.api.portal.dashboard'

# Subscribe
curl -b cookie.txt -H "X-Frappe-CSRF-Token: …" -H "Content-Type: application/json" \
  -d '{"plan":"MSP-Monthly-Veg","start_date":"2026-04-15","auto_renew":true}' \
  'https://hostel.local/api/method/hostel_management.api.portal.subscribe_mess'

# Create Razorpay order
curl -b cookie.txt -H "X-Frappe-CSRF-Token: …" -H "Content-Type: application/json" \
  -d '{"invoice":"HINV-2026-00088"}' \
  'https://hostel.local/api/method/hostel_management.api.payments.create_razorpay_order'
```

### 16.3 Related Docs
- Product & backend spec: `HOSTEL_MANAGEMENT_SYSTEM.md` (same folder)
- Execution plan: `/home/frappe/.claude/plans/radiant-juggling-graham.md`
