# Product Requirements Document (PRD)

> **Project Name:** _[e.g., AITG Machine Monitoring Platform — OEE Dashboard v2]_
> **Document Owner:** _[Your Name, Role]_
> **Stakeholders:** _[Product, Engineering, Client POC, QA]_
> **Version:** 1.0
> **Date Created:** _[DD-MMM-YYYY]_
> **Last Updated:** _[DD-MMM-YYYY]_
> **Status:** ☐ Draft  ☐ In Review  ☐ Approved  ☐ In Development  ☐ Released

---

## 1. Executive Summary
_2–4 sentences. What is being built, for whom, and why now._

> Example: We are building a real-time OEE analytics module for the AITG platform to give CNC shop-floor managers visibility into machine downtime causes. This addresses recurring complaints about manual Excel-based tracking and supports the Q3 client expansion plan.

---

## 2. Problem Statement
- **Current pain point:** _What's broken or missing today?_
- **Who feels it:** _Which user/role/persona?_
- **Cost of inaction:** _Lost revenue, churn, manual hours, compliance risk, etc._

---

## 3. Goals & Success Metrics

| # | Goal | Metric | Target | Measurement Method |
|---|------|--------|--------|--------------------|
| 1 | _e.g., Reduce manual reporting time_ | Hours/week per supervisor | < 1 hr (from 6 hrs) | Time audit pre/post launch |
| 2 | _e.g., Increase machine utilization visibility_ | % machines reporting OEE live | ≥ 95% | Platform telemetry |
| 3 | | | | |

**Non-goals** _(explicitly out of scope, to avoid scope creep)_:
- _e.g., Predictive maintenance ML models — deferred to Phase 2_
- _e.g., Mobile-native app — web-responsive only for v1_

---

## 4. Target Users / Personas

| Persona | Role | Key Need |
|---------|------|----------|
| _Plant Supervisor_ | Operations | Real-time alerts on downtime |
| _Shop-floor Operator_ | Execution | Quick status entry, no typing |
| _Plant Manager_ | Leadership | Weekly OEE trends per line |

---

## 5. Scope

**In Scope (v1):**
- _Feature A_
- _Feature B_
- _Feature C_

**Out of Scope (this release):**
- _Feature X — planned for v1.1_
- _Feature Y — needs separate discovery_

---

## 6. Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-01 | _User can filter machines by line and shift_ | P0 (Must) | Filters persist across page reloads; load < 2s for 200 machines |
| FR-02 | _Alarm triggers SMS + in-app notification_ | P0 | SMS dispatch within 30s of trigger event |
| FR-03 | | P1 (Should) | |
| FR-04 | | P2 (Nice) | |

> **Priority legend:** P0 = launch blocker · P1 = important · P2 = nice-to-have

---

## 7. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Performance | _Page load < 2s on 4G; dashboard refresh ≤ 5s_ |
| Scalability | _Support 500 concurrent users, 5,000 machines_ |
| Security | _Role-based access control; audit logs retained 1 year_ |
| Availability | _99.5% uptime during business hours_ |
| Compatibility | _Chrome, Edge, Safari (latest 2 versions)_ |
| Localization | _English + Hindi (Phase 1)_ |

---

## 8. User Stories / Use Cases

**Story 1:** As a _plant supervisor_, I want to _see live downtime reasons per machine_, so that _I can intervene before a shift's OEE drops below target_.

**Story 2:** As a _[role]_, I want to _[capability]_, so that _[outcome]_.

---

## 9. Technical Considerations
- **Architecture:** _High-level approach — e.g., Angular frontend, .NET Core API, SignalR for real-time push, Azure SQL backend_
- **Integrations / APIs:** _List third-party dependencies (e.g., MapMyIndia, WhatsApp Business, payment gateway)_
- **Data model changes:** _New tables / schema migrations_
- **Open technical questions:** _Anything still under investigation_

---

## 10. Dependencies & Assumptions
- **Dependencies:** _Other teams, vendors, infrastructure (e.g., "Requires Azure tenant provisioning by IT")_
- **Assumptions:** _e.g., "Client will provide test machines by [date]"_

---

## 11. Timeline & Milestones

| Phase | Deliverable | Owner | Start | **Deadline** | Status |
|-------|-------------|-------|-------|--------------|--------|
| Discovery | Requirements sign-off | PM | _DD-MMM_ | **_DD-MMM_** | ☐ |
| Design | UX wireframes + design review | Design Lead | | **** | ☐ |
| Build (Sprint 1) | Backend APIs + auth | Backend Lead | | **** | ☐ |
| Build (Sprint 2) | Frontend integration | Frontend Lead | | **** | ☐ |
| QA | Test cycle + UAT fixes | QA Lead | | **** | ☐ |
| Pilot / Soft launch | Limited rollout | PM | | **** | ☐ |
| GA Release | Full release + comms | PM | | **** | ☐ |

> Update the Status column with: ☐ Not started · 🟡 In progress · ✅ Done · 🔴 Blocked

---

## 12. Risks & Mitigation

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|------|------------|--------|------------|-------|
| 1 | _Third-party API SLA breach_ | Medium | High | _Add fallback queue + retry logic_ | _Lead Dev_ |
| 2 | _Client delays UAT feedback_ | High | Medium | _Weekly checkpoint + written sign-off gates_ | _PM_ |
| 3 | | | | | |

---

## 13. Open Questions
- [ ] _Question 1 — owner, due date_
- [ ] _Question 2_

---

## 14. Approval / Sign-off

| Role | Name | Decision | Date |
|------|------|----------|------|
| Product Owner | | ☐ Approved ☐ Changes Requested | |
| Engineering Lead | | ☐ Approved ☐ Changes Requested | |
| Client / Sponsor | | ☐ Approved ☐ Changes Requested | |

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | _DD-MMM-YYYY_ | _Name_ | Initial draft |
