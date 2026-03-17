# Design System & Component Library

## Document Purpose

This document defines the design tokens, component specifications, and interaction patterns for the University ERP custom frontend. Use this as the foundation for creating consistent, accessible UI designs.

---

## 1. Design Principles

### Core Principles

| Principle | Description |
|-----------|-------------|
| **Clarity** | Information should be immediately understandable |
| **Efficiency** | Minimize clicks/taps to complete tasks |
| **Consistency** | Similar actions should look and behave the same |
| **Accessibility** | Usable by everyone, regardless of ability |
| **Mobile-First** | Design for mobile, then scale up |
| **Performance** | Fast load times, responsive interactions |

---

## 2. Color System

### Primary Colors

```
PRIMARY PALETTE (Trust, Education)
─────────────────────────────────────────────────────────────────

┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│  Primary    │  Primary    │  Primary    │  Primary    │  Primary    │
│  50         │  100        │  500        │  700        │  900        │
│             │             │  (Main)     │             │             │
│  #EEF2FF    │  #E0E7FF    │  #4F46E5    │  #4338CA    │  #312E81    │
│             │             │             │             │             │
│  Background │  Hover      │  Buttons    │  Hover      │  Text       │
│  Highlight  │  States     │  Links      │  Pressed    │  Headings   │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

### Semantic Colors

```
SUCCESS (Positive Actions, Completed States)
─────────────────────────────────────────────────────────────────

┌─────────────┬─────────────┬─────────────┐
│  Success    │  Success    │  Success    │
│  50         │  500        │  700        │
│             │  (Main)     │             │
│  #ECFDF5    │  #10B981    │  #047857    │
│  Background │  Icons      │  Text       │
└─────────────┴─────────────┴─────────────┘


WARNING (Attention Needed, Caution)
─────────────────────────────────────────────────────────────────

┌─────────────┬─────────────┬─────────────┐
│  Warning    │  Warning    │  Warning    │
│  50         │  500        │  700        │
│             │  (Main)     │             │
│  #FFFBEB    │  #F59E0B    │  #B45309    │
│  Background │  Icons      │  Text       │
└─────────────┴─────────────┴─────────────┘


ERROR (Errors, Destructive Actions)
─────────────────────────────────────────────────────────────────

┌─────────────┬─────────────┬─────────────┐
│  Error      │  Error      │  Error      │
│  50         │  500        │  700        │
│             │  (Main)     │             │
│  #FEF2F2    │  #EF4444    │  #B91C1C    │
│  Background │  Icons      │  Text       │
└─────────────┴─────────────┴─────────────┘


INFO (Informational, Neutral)
─────────────────────────────────────────────────────────────────

┌─────────────┬─────────────┬─────────────┐
│  Info       │  Info       │  Info       │
│  50         │  500        │  700        │
│             │  (Main)     │             │
│  #EFF6FF    │  #3B82F6    │  #1D4ED8    │
│  Background │  Icons      │  Text       │
└─────────────┴─────────────┴─────────────┘
```

### Neutral Colors

```
GRAY SCALE (Text, Borders, Backgrounds)
─────────────────────────────────────────────────────────────────

┌────────┬────────┬────────┬────────┬────────┬────────┬────────┬────────┐
│ Gray   │ Gray   │ Gray   │ Gray   │ Gray   │ Gray   │ Gray   │ Gray   │
│ 50     │ 100    │ 200    │ 300    │ 400    │ 500    │ 700    │ 900    │
│        │        │        │        │        │        │        │        │
│#F9FAFB │#F3F4F6 │#E5E7EB │#D1D5DB │#9CA3AF │#6B7280 │#374151 │#111827 │
│        │        │        │        │        │        │        │        │
│ Page   │ Card   │ Border │ Border │ Muted  │ Body   │ Heading│ Dark   │
│ BG     │ BG     │ Light  │ Normal │ Text   │ Text   │ Text   │ Text   │
└────────┴────────┴────────┴────────┴────────┴────────┴────────┴────────┘
```

### Module Accent Colors

```
MODULE IDENTIFICATION COLORS
─────────────────────────────────────────────────────────────────

Student Module:    #4F46E5  (Indigo)
Faculty Module:    #7C3AED  (Purple)
HR Module:         #059669  (Emerald)
Accounts Module:   #2563EB  (Blue)
Admin Module:      #DC2626  (Red)
```

### Color Usage Guidelines

| Context | Color | Usage |
|---------|-------|-------|
| Primary Action | Primary 500 | Main buttons, links |
| Secondary Action | Gray 200 | Secondary buttons |
| Success State | Success 500 | Checkmarks, confirmations |
| Error State | Error 500 | Validation errors, alerts |
| Warning State | Warning 500 | Cautions, pending |
| Info State | Info 500 | Tips, information |
| Text Primary | Gray 900 | Headings |
| Text Secondary | Gray 700 | Body text |
| Text Muted | Gray 500 | Captions, hints |
| Background | Gray 50 | Page background |
| Surface | White | Cards, modals |
| Border | Gray 200 | Dividers, input borders |

---

## 3. Typography

### Font Family

```
PRIMARY FONT: Inter
─────────────────────────────────────────────────────────────────

Aa Bb Cc Dd Ee Ff Gg Hh Ii Jj Kk Ll Mm
Nn Oo Pp Qq Rr Ss Tt Uu Vv Ww Xx Yy Zz
0123456789

Usage: All UI text

Fallback Stack: 'Inter', -apple-system, BlinkMacSystemFont,
                'Segoe UI', Roboto, sans-serif


MONOSPACE FONT: JetBrains Mono (for code/numbers)
─────────────────────────────────────────────────────────────────

0123456789
₹45,000.00

Usage: Student IDs, amounts, codes
```

### Type Scale

```
TYPE SCALE
─────────────────────────────────────────────────────────────────

Display Large    │  48px / 3rem    │  Bold 700   │  Page Titles
Display          │  36px / 2.25rem │  Bold 700   │  Section Headers
Heading 1        │  30px / 1.875rem│  Semibold 600│  Page Headings
Heading 2        │  24px / 1.5rem  │  Semibold 600│  Card Headings
Heading 3        │  20px / 1.25rem │  Semibold 600│  Subsections
Heading 4        │  18px / 1.125rem│  Medium 500 │  Group Labels
Body Large       │  18px / 1.125rem│  Regular 400│  Emphasis Text
Body             │  16px / 1rem    │  Regular 400│  Default Text
Body Small       │  14px / 0.875rem│  Regular 400│  Secondary Text
Caption          │  12px / 0.75rem │  Regular 400│  Labels, Hints
```

### Line Heights

```
LINE HEIGHT
─────────────────────────────────────────────────────────────────

Tight:      1.25  │  Headings
Normal:     1.5   │  Body text
Relaxed:    1.75  │  Long-form content
```

### Typography Examples

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Dashboard                               <- Display (36px, Bold) │
│                                                                  │
│  Today's Schedule                        <- Heading 2 (24px)     │
│                                                                  │
│  You have 4 classes today. Your first    <- Body (16px)         │
│  class starts at 9:00 AM.                                       │
│                                                                  │
│  Data Structures                         <- Heading 4 (18px)     │
│  09:00 - 10:00 • Room 301               <- Caption (12px, Gray) │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Spacing System

### Spacing Scale

```
SPACING SCALE (Based on 4px grid)
─────────────────────────────────────────────────────────────────

0     │  0px        │  None
1     │  4px        │  Tiny (icons)
2     │  8px        │  Extra Small
3     │  12px       │  Small
4     │  16px       │  Default
5     │  20px       │  Medium-Small
6     │  24px       │  Medium
8     │  32px       │  Large
10    │  40px       │  Extra Large
12    │  48px       │  2x Large
16    │  64px       │  3x Large
20    │  80px       │  4x Large
```

### Component Spacing

```
COMPONENT SPACING GUIDELINES
─────────────────────────────────────────────────────────────────

Button Padding:
  - Small:    8px 16px  (py-2 px-4)
  - Medium:   12px 24px (py-3 px-6)
  - Large:    16px 32px (py-4 px-8)

Card Padding:
  - Mobile:   16px
  - Desktop:  24px

Input Padding:
  - Horizontal: 12px
  - Vertical:   10px

List Item Spacing:
  - Between items: 8px
  - Within item:   12px

Section Spacing:
  - Mobile:   24px
  - Desktop:  32px

Page Margins:
  - Mobile:   16px
  - Desktop:  32px (or container max-width)
```

---

## 5. Grid System

### Responsive Grid

```
GRID CONFIGURATION
─────────────────────────────────────────────────────────────────

MOBILE (<640px):
  Columns: 4
  Gutter: 16px
  Margin: 16px

TABLET (640px - 1024px):
  Columns: 8
  Gutter: 24px
  Margin: 32px

DESKTOP (>1024px):
  Columns: 12
  Gutter: 24px
  Margin: 32px (or centered container)
  Max-width: 1280px
```

### Layout Patterns

```
SIDEBAR LAYOUT (Desktop Staff Modules)
─────────────────────────────────────────────────────────────────

┌──────────────────────────────────────────────────────────────┐
│  ┌──────────┐  ┌──────────────────────────────────────────┐  │
│  │          │  │                                          │  │
│  │ SIDEBAR  │  │              MAIN CONTENT                │  │
│  │  240px   │  │           (Remaining Width)              │  │
│  │  Fixed   │  │                                          │  │
│  │          │  │                                          │  │
│  └──────────┘  └──────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘


BOTTOM NAV LAYOUT (Mobile Student Module)
─────────────────────────────────────────────────────────────────

┌────────────────────────┐
│                        │
│     MAIN CONTENT       │
│     (Full Width)       │
│                        │
├────────────────────────┤
│    BOTTOM NAV BAR      │
│       56px Height      │
└────────────────────────┘
```

---

## 6. Components

### 6.1 Buttons

```
BUTTON VARIANTS
─────────────────────────────────────────────────────────────────

PRIMARY (Main actions)
┌─────────────────────────┐
│       Pay Now           │  Background: Primary 500
└─────────────────────────┘  Text: White
                             Hover: Primary 700
                             Active: Primary 800

SECONDARY (Alternative actions)
┌─────────────────────────┐
│       Cancel            │  Background: Gray 100
└─────────────────────────┘  Text: Gray 700
                             Border: Gray 300
                             Hover: Gray 200

OUTLINE (Less emphasis)
┌─────────────────────────┐
│       Learn More        │  Background: Transparent
└─────────────────────────┘  Text: Primary 500
                             Border: Primary 500
                             Hover: Primary 50 bg

GHOST (Minimal)
┌─────────────────────────┐
│       View All →        │  Background: Transparent
└─────────────────────────┘  Text: Primary 500
                             Hover: Primary 50 bg

DESTRUCTIVE (Delete/Remove)
┌─────────────────────────┐
│       Delete            │  Background: Error 500
└─────────────────────────┘  Text: White
                             Hover: Error 700


BUTTON SIZES
─────────────────────────────────────────────────────────────────

Small:    Height 32px, Text 14px, Padding 8px 12px
Medium:   Height 40px, Text 14px, Padding 10px 16px
Large:    Height 48px, Text 16px, Padding 12px 24px


BUTTON STATES
─────────────────────────────────────────────────────────────────

Default    │ Normal appearance
Hover      │ Darker background
Active     │ Even darker, slight scale down
Focus      │ Focus ring (2px offset, Primary color)
Disabled   │ Opacity 50%, cursor not-allowed
Loading    │ Spinner icon, text changes to "Loading..."
```

### 6.2 Form Inputs

```
TEXT INPUT
─────────────────────────────────────────────────────────────────

  Label *
  ┌─────────────────────────────────────────┐
  │ Placeholder text                        │
  └─────────────────────────────────────────┘
  Helper text or error message

STATES:

Default:
  Border: Gray 300
  Background: White

Focus:
  Border: Primary 500
  Ring: Primary 100 (2px)

Error:
  Border: Error 500
  Helper text: Error 500

Disabled:
  Background: Gray 100
  Text: Gray 400


SELECT DROPDOWN
─────────────────────────────────────────────────────────────────

  Department
  ┌─────────────────────────────────────┬───┐
  │ Select department...                │ ▼ │
  └─────────────────────────────────────┴───┘

  ┌─────────────────────────────────────────┐
  │ ○ Computer Science                      │
  │ ○ Electronics                           │
  │ ● Mechanical  ← Selected                │
  │ ○ Civil                                 │
  └─────────────────────────────────────────┘


CHECKBOX
─────────────────────────────────────────────────────────────────

  ☐ Unchecked     ☑ Checked     ▣ Indeterminate

  Size: 20px × 20px
  Border radius: 4px


RADIO BUTTON
─────────────────────────────────────────────────────────────────

  ○ Option A
  ● Option B (Selected)
  ○ Option C

  Size: 20px × 20px


TOGGLE SWITCH
─────────────────────────────────────────────────────────────────

  Off: ┌─────●───────┐
       └─────────────┘

  On:  ┌───────────●─┐
       └─────────────┘

  Width: 44px
  Height: 24px


DATE PICKER
─────────────────────────────────────────────────────────────────

  From Date
  ┌─────────────────────────────────┬─────┐
  │ 17 January 2026                 │ 📅  │
  └─────────────────────────────────┴─────┘

  Opens calendar dropdown on click
```

### 6.3 Cards

```
BASIC CARD
─────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────┐
  │                                         │
  │  Card Title                             │
  │                                         │
  │  Card content goes here with           │
  │  supporting text.                       │
  │                                         │
  │  [Action]                               │
  │                                         │
  └─────────────────────────────────────────┘

  Background: White
  Border: Gray 200 (1px)
  Border radius: 8px
  Shadow: 0 1px 3px rgba(0,0,0,0.1)
  Padding: 16px (mobile), 24px (desktop)


STAT CARD
─────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────┐
  │  📊 Total Students                      │
  │                                         │
  │  2,350                                  │
  │  +23 from last week                     │
  │                                         │
  └─────────────────────────────────────────┘


INTERACTIVE CARD (Clickable)
─────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────┐
  │  Data Structures                        │
  │  09:00 - 10:00 • Room 301              │
  │                                    →    │
  └─────────────────────────────────────────┘

  Hover: Shadow increases, subtle lift
  Active: Shadow decreases
```

### 6.4 Data Tables

```
DATA TABLE
─────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│  🔍 Search...    │ Filter ▼ │ Export ▼ │              1-10 of 50│
├─────────────────────────────────────────────────────────────────┤
│  □  │ Name ▲        │ Department    │ Status    │ Actions      │
│  ───┼───────────────┼───────────────┼───────────┼──────────────│
│  □  │ Rahul Sharma  │ CSE           │ ● Active  │ [⋮]          │
│  □  │ Priya Verma   │ ECE           │ ● Active  │ [⋮]          │
│  □  │ Amit Singh    │ Mechanical    │ ○ Inactive│ [⋮]          │
│  ───┼───────────────┼───────────────┼───────────┼──────────────│
│       (Hover row highlight)                                     │
├─────────────────────────────────────────────────────────────────┤
│  ◀ Prev │ 1 │ 2 │ 3 │ ... │ 5 │ Next ▶                        │
└─────────────────────────────────────────────────────────────────┘


TABLE FEATURES:
- Sortable columns (▲▼ indicator)
- Row selection (checkbox)
- Row hover highlight (Gray 50)
- Sticky header on scroll
- Responsive: Horizontal scroll or card view on mobile
- Pagination or infinite scroll
- Bulk actions toolbar when rows selected
```

### 6.5 Navigation

```
TOP HEADER
─────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│  ≡  │  [Logo] University ERP        │  🔔 (3)  │  👤 Name  ▼  │
└─────────────────────────────────────────────────────────────────┘

Height: 56px (mobile), 64px (desktop)
Background: White
Border-bottom: Gray 200


SIDEBAR NAVIGATION (Desktop)
─────────────────────────────────────────────────────────────────

┌─────────────────┐
│  [Logo]         │
│                 │
│  ─────────────  │
│                 │
│  📊 Dashboard   │  <- Active: Primary bg, Primary text
│                 │
│  📚 Classes     │  <- Normal: Gray 700 text
│    ├ Schedule   │  <- Submenu: Indented, smaller
│    └ Materials  │
│                 │
│  📋 Attendance  │  <- Hover: Gray 100 bg
│                 │
│  ─────────────  │  <- Divider
│                 │
│  ⚙️ Settings    │
│  🚪 Logout      │
│                 │
└─────────────────┘

Width: 240px (expanded), 64px (collapsed)
Item height: 44px
Padding: 12px 16px


BOTTOM NAVIGATION (Mobile)
─────────────────────────────────────────────────────────────────

┌───────────────────────────────────────────────────────────────┐
│                                                               │
│   🏠        📚         💰         📝         ≡               │
│  Home    Academic     Fees      Exams      More              │
│   ▲                                                           │
│ Active                                                        │
│                                                               │
└───────────────────────────────────────────────────────────────┘

Height: 56px + safe area
Background: White
Border-top: Gray 200
Active: Primary color icon + text
Inactive: Gray 500 icon + text


BREADCRUMBS
─────────────────────────────────────────────────────────────────

Home  /  Academics  /  Attendance  /  Details

Separator: / or >
Current page: Gray 900 (not clickable)
Previous pages: Primary 500 (clickable)
```

### 6.6 Modals & Dialogs

```
MODAL
─────────────────────────────────────────────────────────────────

  ┌────────────────────────────────────────────────┐
  │                                                │
  │  ┌────────────────────────────────────────┐   │
  │  │  Modal Title                      [X]  │   │
  │  ├────────────────────────────────────────┤   │
  │  │                                        │   │
  │  │  Modal content goes here. This can    │   │
  │  │  include forms, information, or       │   │
  │  │  confirmation messages.               │   │
  │  │                                        │   │
  │  ├────────────────────────────────────────┤   │
  │  │              [Cancel]  [Confirm]       │   │
  │  └────────────────────────────────────────┘   │
  │                                                │
  └────────────────────────────────────────────────┘

  Overlay: Black, 50% opacity
  Modal: White background
  Border radius: 12px
  Shadow: Large
  Max-width: 480px (small), 640px (medium), 800px (large)
  Mobile: Full-screen or bottom sheet


CONFIRMATION DIALOG
─────────────────────────────────────────────────────────────────

  ┌────────────────────────────────────────┐
  │                                        │
  │  ⚠️  Are you sure?                     │
  │                                        │
  │  This action cannot be undone.         │
  │                                        │
  │         [Cancel]  [Delete]             │
  │                                        │
  └────────────────────────────────────────┘


BOTTOM SHEET (Mobile)
─────────────────────────────────────────────────────────────────

  ┌────────────────────────────────────────┐
  │                                        │
  │            (Overlay area)              │
  │                                        │
  │                                        │
  │ ─────────────────────────────────────  │
  │  ────────                              │  <- Drag handle
  │                                        │
  │  Sheet Title                           │
  │                                        │
  │  Content goes here                     │
  │                                        │
  │  [Action Button]                       │
  │                                        │
  └────────────────────────────────────────┘

  Slides up from bottom
  Swipe down to dismiss
  Border radius: 16px (top corners)
```

### 6.7 Feedback Components

```
TOAST NOTIFICATION
─────────────────────────────────────────────────────────────────

  ┌──────────────────────────────────────────────┐
  │  ✓  Payment successful                   [X] │
  └──────────────────────────────────────────────┘

  Position: Top-right (desktop), Top-center (mobile)
  Auto-dismiss: 5 seconds
  Types: Success (green), Error (red), Warning (yellow), Info (blue)


ALERT BANNER
─────────────────────────────────────────────────────────────────

  ┌──────────────────────────────────────────────────────────────┐
  │  ⚠️  Your session will expire in 5 minutes. [Extend Session] │
  └──────────────────────────────────────────────────────────────┘

  Full width
  Dismissible or persistent
  Background: Semantic color (light variant)


LOADING STATES
─────────────────────────────────────────────────────────────────

Spinner:
  ○─○    (Rotating)
  Size: 16px (inline), 24px (button), 48px (page)

Skeleton:
  ░░░░░░░░░░░░░░░░░░░░░░  (Animated shimmer)

Progress Bar:
  ████████████░░░░░░░░░░  75%


EMPTY STATE
─────────────────────────────────────────────────────────────────

  ┌────────────────────────────────────────┐
  │                                        │
  │            📭                          │
  │                                        │
  │     No notifications yet               │
  │                                        │
  │  You'll see notifications here when   │
  │  there's activity on your account.    │
  │                                        │
  │           [Learn More]                 │
  │                                        │
  └────────────────────────────────────────┘
```

### 6.8 Status Indicators

```
STATUS BADGES
─────────────────────────────────────────────────────────────────

  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │ ● Active │     │ ○ Pending│     │ ✓ Done   │
  └──────────┘     └──────────┘     └──────────┘
    Green            Yellow           Blue

  ┌──────────┐     ┌──────────┐
  │ ✗ Failed │     │ ◐ Draft  │
  └──────────┘     └──────────┘
    Red              Gray


PROGRESS INDICATORS
─────────────────────────────────────────────────────────────────

Linear:
  ████████████░░░░░░░░  60%

Circular:
      ╭───╮
     ╱  76% ╲
    │       │
     ╲     ╱
      ╰───╯


ATTENDANCE INDICATOR
─────────────────────────────────────────────────────────────────

  ███████████████░░░  76%  ⚠️

  Green: ≥75%
  Yellow: 70-74%
  Red: <70%
```

---

## 7. Animation & Motion

### Timing Functions

```
EASING CURVES
─────────────────────────────────────────────────────────────────

Ease Out:     cubic-bezier(0, 0, 0.2, 1)    │  Elements entering
Ease In:      cubic-bezier(0.4, 0, 1, 1)    │  Elements exiting
Ease In-Out:  cubic-bezier(0.4, 0, 0.2, 1)  │  Moving elements
```

### Duration

```
ANIMATION DURATION
─────────────────────────────────────────────────────────────────

Instant:     0ms         │  Immediate feedback
Fast:        150ms       │  Hover states, button press
Normal:      250ms       │  Transitions, toggle
Slow:        350ms       │  Modal open/close
Complex:     500ms       │  Page transitions
```

### Common Animations

```
ENTER ANIMATIONS
─────────────────────────────────────────────────────────────────

Fade In:        opacity 0 → 1
Slide Up:       translateY(8px) → 0, opacity 0 → 1
Scale In:       scale(0.95) → 1, opacity 0 → 1
Slide In Right: translateX(100%) → 0


EXIT ANIMATIONS
─────────────────────────────────────────────────────────────────

Fade Out:       opacity 1 → 0
Slide Down:     translateY(0) → 8px, opacity 1 → 0
Scale Out:      scale(1) → 0.95, opacity 1 → 0


INTERACTION FEEDBACK
─────────────────────────────────────────────────────────────────

Button Press:   scale(0.98)
Hover Lift:     translateY(-2px), shadow increase
Card Tap:       scale(0.99), quick
```

---

## 8. Iconography

### Icon Set

Recommended: **Heroicons** (MIT License)
Alternative: **Lucide Icons**, **Phosphor Icons**

### Icon Sizes

```
ICON SIZES
─────────────────────────────────────────────────────────────────

Extra Small:   16px   │  Inline with text
Small:         20px   │  Buttons, inputs
Medium:        24px   │  Navigation, cards
Large:         32px   │  Feature icons
Extra Large:   48px   │  Empty states, illustrations
```

### Common Icons

```
NAVIGATION
─────────────────────────────────────────────────────────────────
🏠 Home       📊 Dashboard   👤 Profile     ⚙️ Settings
📚 Academic   📋 Attendance  📝 Grades      💰 Fees
🔔 Bell       ≡ Menu        ← Back         → Forward
X Close       ▼ Chevron     ⋮ More         🔍 Search


ACTIONS
─────────────────────────────────────────────────────────────────
+ Add         ✎ Edit        🗑 Delete      👁 View
📄 Document   📥 Download   📤 Upload      🖨 Print
✓ Check       ✗ Cross       ⚠ Warning      ℹ Info


STATUS
─────────────────────────────────────────────────────────────────
● Active      ○ Inactive    ◐ Pending      ✓ Success
✗ Error       ⚠ Warning     🔄 Loading     🔒 Locked
```

---

## 9. Accessibility (A11y)

### Color Contrast

| Text Type | Minimum Ratio |
|-----------|---------------|
| Normal Text | 4.5:1 |
| Large Text (18px+) | 3:1 |
| UI Components | 3:1 |

### Focus States

```
FOCUS INDICATOR
─────────────────────────────────────────────────────────────────

All interactive elements must have visible focus:

┌─────────────────────────┐
│       Button            │  <- 2px ring, Primary color
│                         │     2px offset
└─────────────────────────┘

Focus should be visible with keyboard navigation
Never remove focus outline entirely
```

### Touch Targets

```
MINIMUM TOUCH TARGETS
─────────────────────────────────────────────────────────────────

Minimum: 44px × 44px

Small buttons/icons can have visual size < 44px
but clickable area must be ≥ 44px
```

### ARIA Labels

```
ARIA GUIDELINES
─────────────────────────────────────────────────────────────────

• All images: alt text or aria-hidden
• Icon buttons: aria-label
• Form inputs: associated labels
• Dynamic content: aria-live regions
• Modals: aria-modal, focus trap
• Navigation: aria-current for active item
• Expandable: aria-expanded
• Loading: aria-busy
```

---

## 10. Responsive Design

### Breakpoints

```
BREAKPOINTS
─────────────────────────────────────────────────────────────────

Mobile S:     320px
Mobile M:     375px
Mobile L:     425px
Tablet:       768px
Laptop:       1024px
Desktop:      1280px
Desktop L:    1440px
```

### Design Approach

```
MOBILE-FIRST
─────────────────────────────────────────────────────────────────

Start with mobile design, then add complexity for larger screens:

1. Design for 375px width first
2. Add tablet adjustments at 768px
3. Add desktop layout at 1024px

Benefits:
• Forces content prioritization
• Better performance (smaller CSS)
• Natural progressive enhancement
```

---

## 11. Design Tokens (CSS Variables)

```css
/* COLORS */
--color-primary-50: #EEF2FF;
--color-primary-500: #4F46E5;
--color-primary-700: #4338CA;

--color-success-500: #10B981;
--color-warning-500: #F59E0B;
--color-error-500: #EF4444;

--color-gray-50: #F9FAFB;
--color-gray-500: #6B7280;
--color-gray-900: #111827;

/* TYPOGRAPHY */
--font-family: 'Inter', sans-serif;
--font-size-xs: 0.75rem;
--font-size-sm: 0.875rem;
--font-size-base: 1rem;
--font-size-lg: 1.125rem;
--font-size-xl: 1.25rem;
--font-size-2xl: 1.5rem;

/* SPACING */
--spacing-1: 0.25rem;
--spacing-2: 0.5rem;
--spacing-4: 1rem;
--spacing-6: 1.5rem;
--spacing-8: 2rem;

/* BORDER RADIUS */
--radius-sm: 0.25rem;
--radius-md: 0.5rem;
--radius-lg: 0.75rem;
--radius-full: 9999px;

/* SHADOWS */
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
--shadow-md: 0 4px 6px rgba(0,0,0,0.1);
--shadow-lg: 0 10px 15px rgba(0,0,0,0.1);

/* TRANSITIONS */
--transition-fast: 150ms ease-out;
--transition-normal: 250ms ease-out;
--transition-slow: 350ms ease-out;
```

---

**Document Version**: 1.0
**Created**: 2026-01-17
**Audience**: UI/UX Designers, Frontend Developers
