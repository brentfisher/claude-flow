---
id: STORY-025
title: Build the full module ladder, the Power/Provisions interlock and storage
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: null
pr_url: null
approach_summary: null
created: 2026-08-13
updated: 2026-08-13
---

# Build the full module ladder, the Power/Provisions interlock and storage

The act's actual game: **Power buys Provisions and Provisions buy Power**. Reactors need staffing,
scrubbers need power, and the interesting decision is a net-rate balance, not an accumulation curve.
This story lands the full ladder on top of STORY-018's already-proven integration path.

Storage is capacity-only and carries the ledger **R1** fix: Fuel capacity has **two** sources.

## Acceptance Criteria

- [ ] Full module ladder in `data/actSevenModulesConfig.js`: generators, scrubbers, hydroponics,
      staffing consumers, and the Salvage ladder's upper tiers. Each declares production **and**
      consumption.
- [ ] Storage modules add capacity only, no rate.
- [ ] **`resources.fuel.capacity = Σ sites[].fuelCapacityOnArrival + Σ owned storage modules`** —
      both terms derived, never stored. The site term defaults to 0 until STORY-027 lands, so this
      story is shippable alone.
- [ ] The satisfaction factor is implemented per PRD §5.6 and **converges** — verify the fixed point
      terminates in a bounded number of passes and record the measured bound in a comment.
- [ ] A colony starved of any resource **throttles and recovers**; nothing is destroyed, no module
      is removed, and adding one generator always restores it.
- [ ] Each phase's affordability is checked against §5.3's budget: the phase's integrated Salvage
      versus the sum of what the player must buy, with slack stated. **Measure the integral, not the
      quotient** — income ramps while the player builds, so `threshold ÷ rate` under-reports by
      5–15%.
- [ ] Tuning comments record runs (the `data/acts.js` Act III/IV comment blocks are the template).
- [ ] `npm run build` passes.

## Notes

- PRD §5.4, §5.5, §5.6, and ledger **R1**.
- **Depends on STORY-018** and **STORY-024**.
- The `lifeSupport` flat point and its relieving unlock (the graph inverting) is the design payload
  of this story — PRD §5.10.
- **Pacing control, not an economy number:** the first Fuel tank must not be affordable before
  ~minute 35 of `lifeSupport`, or the first launch threshold is crossed a third of a phase early and
  steals time from `lunar` (PRD §7.5).
- `conventions.md`: `data/` comments carry measured results; a band without a run behind it is not
  done.
