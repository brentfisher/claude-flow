---
id: STORY-031
title: Add Ceres, the Warning Track, and pad tiers 4-5
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: story/STORY-031-deep-space-content
worktree_path: /Users/brent/idle-base-worktrees/STORY-031
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/35
is_architectural: true
approach_summary: >
  NOTE ON is_architectural: the checklist answer is false (no new module — config extension over
  rung-agnostic engines). Overridden to true by the user at the 2026-08-16 kickoff gate so this
  story records an OpenSpec change: it must durably record WHY the upkeep table was scaled down
  rather than generator ceilings raised, and why the final fill is deliberately flat, where a later
  reviewer will look for it. Matches how STORY-027 recorded its deferred measurement and STORY-029
  discharged ledger R9 by measurement.
  Pure config extension over engines that already exist and are rung-agnostic: two site rows
  (Ceres, the Warning Track) plus pad tiers 4-5 appended to `data/actSevenSitesConfig.js`, and the
  final threshold re-sized in `data/actSevenLaunchConfig.js`. No new engine module —
  sites.js/launch.js already read tiers and reach from config via getPadTier/padTierForRung. The
  work is mostly MEASUREMENT: drive the colony and launch engines headlessly under `node` to prove
  the network sustains the top pad's upkeep at the moment it becomes buildable, size the last
  threshold against the POST-Track Fuel rate, and check the dead-air metric (no ~2min interval with
  no affordable purchase and no pending event) — excepting the final fill, which is deliberately
  flat and must be commented as intentional.
created: 2026-08-13
updated: 2026-08-17
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
- [ ] **ADDED 2026-08-17 at the kickoff gate — fix `actualDraw()` to charge site upkeep.**
      `siteUpkeepPerSecond()` is summed into `demand` but never into `actualDraw`
      (`engine/colony.js`), so a colonized site raises ration pressure without drawing a unit.
      Measured by STORY-030: 10 RTGs + On-Deck + a tier-2 pad reports `demand.power 3.8` but
      `net.power 30.0` (= `gross`). PRD §5.7's own trace disagrees with the code. This is folded in
      here rather than done separately because **AC #4 is meaningless without it** — an upkeep
      ladder measured against a colony that never pays site upkeep is measured against a fiction.
      Re-measure §7.5's affordability tables against the corrected draw and record the delta.
- [ ] `npm run build` passes.

## Notes

- PRD §7.1, §7.2, §7.6 (the `deepSpace` beat table and the dead-air metric).
- **Depends on STORY-027, STORY-028.**
- Ledger **R2**'s note that within-phase interpolation runs hot: §7's costs are ~15–25% more
  generous than intended. If simulation confirms, spend the recovered minutes on the arrival beat
  rather than raising thresholds.
- **EXPECTED MERGE CONFLICT with PR #34 (STORY-030), in `actualDraw()` — resolve by taking BOTH
  terms.** #34 widened the signature to `actualDraw(owned, drawMult, throttles, contractDraw)` and
  appended a contract-draw loop. This story adds a site-upkeep term to the same function. Neither
  supersedes the other; both consumers are real. This is the same class of conflict MERGE-NOTES
  records for the `tickEngine.js` event-clock contributors (029 vs 027), resolved the same way.
  Match #34's shape: the site term is multiplied by `drawMult` and is **not** load-followed — a site
  is not a module and has no `loadFollowOf`, exactly as it is treated in `demandAtFullOutput()`.
