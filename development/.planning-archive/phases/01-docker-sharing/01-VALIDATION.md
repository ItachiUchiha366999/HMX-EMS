---
phase: 1
slug: docker-sharing
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-17
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Shell scripts + Docker CLI (infrastructure phase, no app tests) |
| **Config file** | none — validation is via Docker commands and file checks |
| **Quick run command** | `docker compose -f docker-compose.prod.yml config --quiet` |
| **Full suite command** | `docker compose -f docker-compose.prod.yml up -d && docker compose -f docker-compose.prod.yml ps` |
| **Estimated runtime** | ~30 seconds (compose validation), ~120 seconds (full stack start) |

---

## Sampling Rate

- **After every task commit:** Run `docker compose -f docker-compose.prod.yml config --quiet`
- **After every plan wave:** Run full compose up + verify all services healthy
- **Before `/gsd:verify-work`:** Full stack must start and all services report healthy
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | DOCK-01 | manual | `docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"` | N/A | ⬜ pending |
| 01-01-02 | 01 | 1 | DOCK-02 | shell | `test ! -d frappe-bench/logs/*.log && echo "clean"` | N/A | ⬜ pending |
| 01-01-03 | 01 | 1 | DOCK-03 | shell | `grep -v "123\|RAZORPAY\|encryption_key" site_config.json` | N/A | ⬜ pending |
| 01-02-01 | 02 | 1 | DOCK-04 | shell | `docker images \| grep university-erp` | N/A | ⬜ pending |
| 01-02-02 | 02 | 1 | DOCK-05 | shell | `docker images \| grep university-erp-db` | N/A | ⬜ pending |
| 01-02-03 | 02 | 1 | DOCK-06 | shell | `docker manifest inspect ghcr.io/{org}/university-erp:latest` | N/A | ⬜ pending |
| 01-03-01 | 03 | 2 | DOCK-07 | shell | `docker compose -f docker-compose.prod.yml config --quiet` | ❌ W0 | ⬜ pending |
| 01-03-02 | 03 | 2 | DOCK-08 | manual | `test -f DEPLOYMENT.md && wc -l DEPLOYMENT.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `docker-compose.prod.yml` — production compose file (created in Plan 03)
- [ ] `DEPLOYMENT.md` — onboarding guide (created in Plan 03)
- [ ] `.env.example` — environment variable template (created in Plan 01)

*Infrastructure phase — no test framework installation needed. Validation is via Docker CLI commands and file existence checks.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GHCR push succeeds | DOCK-06 | Requires GitHub PAT authentication | Login to GHCR, push image, verify on github.com packages page |
| Receiving developer can start the stack | DOCK-07 | End-to-end requires a clean machine | Pull images on a separate machine/VM, run docker compose up, verify site loads |
| Onboarding guide is complete | DOCK-08 | Subjective completeness check | Follow guide step-by-step on clean setup, note any missing instructions |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
