---
id: STORY-027
title: Add the site ladder, colonization, launch pads and the phase writer
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: null
pr_url: null
approach_summary: null
created: 2026-08-13
updated: 2026-08-13
---

# Add the site ladder, colonization, launch pads and the phase writer

The act's spine and the user's core mechanic: to launch further you must colonize the Moon, and a
colony is what lets you build the places you launch from. Five rungs, strictly ordered — you cannot
skip second base, and the fiction and the gating are the same sentence.

## Acceptance Criteria

- [ ] New `engine/sites.js` (pure) and `data/actSevenSitesConfig.js` with the five-rung ladder.
- [ ] Site record shape: `{ id, reached, colonized, launchPadTier, buildingId, readyAtClock }`.
- [ ] **One build per site at a time** (`buildingId`), so colonization and pad builds collapse into
      a single `readyAtClock` contributor.
- [ ] Shop contract: `listOffers(state)`, `purchase(state, offerId)`, `resolveBuilds(state)`,
      `nextBuildClock(state)`. `resolveBuilds` is **idempotent** — a completed build clears
      `buildingId`, so a replayed step is a no-op.
- [ ] `nextBuildClock` registers on STORY-017's contributor list.
- [ ] Pad tiers gate reach. **Reach is a function of built pad tier alone, never of current
      satisfaction** — a starved network launches later, never shorter. A pad whose reach degrades
      under starvation is destruction with extra steps, and could happen while the player is asleep.
- [ ] Each site carries `upkeepFactor` (a plain config scalar — deliberately **not** `Mult`-suffixed,
      since it is not a `BONUS_KEYS` member) multiplying pad upkeep only.
- [ ] Each site carries `fuelCapacityOnArrival`, feeding STORY-025's two-source capacity sum.
- [ ] **`engine/sites.js` is the single writer of `expedition.phase`**, recomputed from a pure
      predicate ladder every `advance()` and written only when it differs, so an old or hand-edited
      save self-heals.
- [ ] Salvage costs are **recomputed from STORY-024's measured bands**, holding the minutes-of-income
      intent — not copied from the PRD's estimate-derived table.
- [ ] `npm run build` passes.

## Notes

- PRD §7.1, §7.2, §7.4, §7.7, and ledger **R2** and **R4**.
- **Depends on STORY-017, STORY-025.**
- **Ledger R2 is a reconciliation, not a measurement.** Its cost table was computed from §5's
  *unsimulated* estimates. Recompute against STORY-024's actual measured bands or you inherit the
  error the ledger was written to correct.
- Resources are **one global pool**, not per-site — this keeps `nextColonyThresholdClock` a
  closed-form solve over four scalars rather than four × N.
