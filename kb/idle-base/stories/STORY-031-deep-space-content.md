---
id: STORY-031
title: Add Ceres, the Warning Track, and pad tiers 4-5
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: null
worktree_path: null
base_branch: null
pr_url: null
is_architectural: null
approach_summary: null
created: 2026-08-13
updated: 2026-08-13
---

# Add Ceres, the Warning Track, and pad tiers 4-5

The `deepSpace` content on top of the site and launch engines: a site that produces Provisions at
scale, a site that produces **nothing at all**, and the two pad tiers that reach past them.

The Warning Track producing nothing is the design, not an oversight. It is the act's thesis as a
mechanic: the last site is a pure sink, and the whole network exists to hold one pad open long
enough to swing. A player arriving there watches every rate in the header go down and has to build
anyway.

## Acceptance Criteria

- [ ] Ceres and the Warning Track added to `data/actSevenSitesConfig.js` with their upkeep factors.
- [ ] Pad tiers 4 and 5 added, with costs, build windows and upkeep.
- [ ] The Warning Track produces **nothing** and is deliberately cheap to establish and expensive to
      sustain — that inversion is the site's character and must survive retuning.
- [ ] The network can actually sustain the top pad's upkeep at the point it becomes buildable.
      **Verify by simulation**; if it cannot, scale the upkeep table down rather than raising
      generator ceilings, because the point is that the Track is expensive, not impossible.
- [ ] The final threshold is sized against the **post-Track** Fuel rate, not the pre-Track rate —
      arriving lowers net Fuel/sec, and sizing against the higher number makes the last fill run
      long at exactly the beat that must not drag.
- [ ] The `deepSpace` beats each have an identified flat point with a relieving unlock within ~5
      minutes, **except the final fill**, which is deliberately flat and must be commented as
      intentional so a later reviewer does not "fix" it.
- [ ] Measured: no interval longer than ~2 minutes in which the player has no affordable purchase
      and no pending event (again excepting the final beat).
- [ ] `npm run build` passes.

## Notes

- PRD §7.1, §7.2, §7.6 (the `deepSpace` beat table and the dead-air metric).
- **Depends on STORY-027, STORY-028.**
- Ledger **R2**'s note that within-phase interpolation runs hot: §7's costs are ~15–25% more
  generous than intended. If simulation confirms, spend the recovered minutes on the arrival beat
  rather than raising thresholds.
