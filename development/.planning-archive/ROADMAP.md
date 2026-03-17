# Roadmap: University ERP — Developer Sharing & Handoff

## Overview

This milestone has one job: package the complete working University ERP environment and hand it off to another developer via two channels. **Docker images on GHCR** deliver the running environment (database, config, demo data). **Git repo** delivers source code with all planning docs, hooks.py changes, and dashboard specs. The two phases are independent — they can run in parallel since they deliver through separate channels.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Docker Sharing** - Audit, clean, commit, and push the full running environment (bench + MariaDB) to GHCR with a compose file and onboarding guide
- [ ] **Phase 2: Planning Artifacts & Handoff** - Finalize all planning docs, update hooks.py, document per-module dashboard specs, and package everything for the receiving developer

## Phase Details

### Phase 1: Docker Sharing
**Goal**: The receiving developer can pull two GHCR images, run `docker compose up`, and have the complete working University ERP environment running locally — code, database, demo data, and config intact
**Depends on**: Nothing (first phase)
**Requirements**: DOCK-01, DOCK-02, DOCK-03, DOCK-04, DOCK-05, DOCK-06, DOCK-07, DOCK-08
**Success Criteria** (what must be TRUE):
  1. `docker ps` and `docker inspect` output is documented — service names, container names, and volume bindings are known and recorded
  2. Both committed images (bench + MariaDB) exist on GHCR under the correct repository and tag
  3. `docker-compose.share.yml` references the GHCR images and starts successfully with `docker compose up`
  4. The onboarding guide covers pull instructions, credential setup, first-start checklist, and project structure so a new developer needs no verbal walkthrough
  5. No real credentials (encryption_key, Razorpay/PayU keys, MariaDB password) exist in the committed images — all replaced with sandbox/placeholder values
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md — Audit container architecture, pre-build cleanup, secrets scrub, .env.example (DOCK-01, DOCK-02, DOCK-03)
- [ ] 01-02-PLAN.md — Update Containerfile, build production image, push to GHCR (DOCK-04, DOCK-05, DOCK-06)
- [ ] 01-03-PLAN.md — Write docker-compose.prod.yml and developer onboarding guide DEPLOYMENT.md (DOCK-07, DOCK-08)

### Phase 2: Planning Artifacts & Handoff
**Goal**: Every planning artifact the receiving developer needs exists in the repo — project context, requirements with REQ-IDs, a phased roadmap for dashboard development, hooks.py updated to export fixtures, and per-module dashboard specs for all 21 modules
**Depends on**: Nothing (independent — delivered via Git repo, not Docker image)
**Requirements**: PLAN-01, PLAN-02, PLAN-03, PLAN-04, PLAN-05, PLAN-06, DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06
**Success Criteria** (what must be TRUE):
  1. PROJECT.md, REQUIREMENTS.md, and ROADMAP.md are complete and accurate — a developer reading them cold understands scope, constraints, and next steps without asking questions
  2. hooks.py includes Dashboard, Number Card, and Dashboard Chart in the fixtures list so `bench export-fixtures` captures dashboard artifacts from day one
  3. Per-module dashboard specs exist for all 21 modules — each spec names specific KPIs, chart types, and data sources the receiving developer will build
  4. Research artifacts (.planning/research/) and codebase map (.planning/codebase/) are present and current, providing stack patterns, architecture guidance, and pitfall mitigations
  5. The fixture export workflow (hooks.py pattern + bench export-fixtures command + fixture JSON location) is documented as a developer guide so the receiving developer doesn't hit the "dashboards lost on reinstall" pitfall
**Plans**: TBD

Plans:
- [ ] 02-01: Finalize PROJECT.md, REQUIREMENTS.md, research artifacts, and codebase map (PLAN-01, PLAN-02, PLAN-04, PLAN-05)
- [ ] 02-02: Update hooks.py for fixture export and document the fixture workflow (PLAN-06, DASH-06)
- [ ] 02-03: Write per-module dashboard specs for all 21 modules and finalize ROADMAP.md for dashboard phases (PLAN-03, DASH-01, DASH-02, DASH-03, DASH-04, DASH-05)

## Progress

**Execution Order:**
Phases are independent and can run in parallel (Docker via GHCR, code via Git repo)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Docker Sharing | 0/3 | Not started | - |
| 2. Planning Artifacts & Handoff | 0/3 | Not started | - |
