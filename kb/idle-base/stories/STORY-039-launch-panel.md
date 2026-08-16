---
id: STORY-039
title: Build the Launch panel — the Fuel threshold, the overshoot decision and the commit surface
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: null
worktree_path: null
base_branch: null
pr_url: null
is_architectural: null
approach_summary: null
created: 2026-08-16
updated: 2026-08-16
---

# Build the Launch panel — the Fuel threshold, the overshoot decision and the commit surface

`launch` answers *can I go?* and is split from `sites` deliberately: **a launch is a committed
threshold spend that earns its own confirm surface**, the same way `CallUpModal` does (§6.4).

This panel carries the act's single most consequential player decision, and it is a decision the UI
creates rather than reports. §7.3's overshoot band gives every site a Fuel tank holding **1.6× the
threshold of the launch departing from it** — so a player may bank up to 60% over and spend the
surplus on a shorter transit and an arrival grant. **Committing dumps the entire tank, not the
threshold — there is no change.** That is what makes the extra 60% a decision instead of a rounding
error, and a panel that showed only "threshold met / not met" would delete it.

The tank floor is derived (`1.6 × departingThreshold`) rather than authored, so this panel must read
it from `fuelCapacityOnArrival` / the engine and never restate the multiplier — the derivation exists
specifically so the number cannot drift.

## Acceptance Criteria

**The threshold**

- [ ] `components/expedition/LaunchPanel.js` renders real content and no longer returns
      `<PlaceholderPanel />`.
- [ ] Current Fuel renders against the **departing** threshold for the site being launched from —
      not the arriving one. The tank you fill is the tank at the place you are standing.
- [ ] Before any Fuel tank exists, the panel says so honestly: Fuel's base capacity is 0, so Fuel
      cannot be banked at all and the threshold is unreachable until the first Bladder.
- [ ] The destination is the lowest unreached rung, read from the engine — the panel does not choose
      it.

**The overshoot decision**

- [ ] The band between threshold and tank ceiling renders as a **band**, not a binary, so the player
      can see they are banking surplus.
- [ ] What the surplus buys (shorter transit, arrival grant) is shown before commit, from the
      engine's own figures.
- [ ] The commit surface states plainly that committing **spends the whole tank**, not the
      threshold. This must be visible before the irreversible action, not after.
- [ ] Commit goes through a confirm surface, following `CallUpModal`'s precedent for a committed
      spend.

**In flight**

- [ ] A launch under way renders its remaining transit from the engine's clock, with no
      component-side timer and no `Date.now()`.
- [ ] The panel makes clear that a burn in progress is a burn in progress — a `resolved: false`
      record — and that reach is unaffected by resource starvation while it runs.

**Behaviour**

- [ ] Renders without throwing against a save with no `expedition` key, and against an Act VII save
      with no tank, no pad and no launch history.
- [ ] A refused commit (engine returns null) is a no-op.

**Verification**

- [ ] `npm run build` passes.
- [ ] Drive the launch engine under `node` across: no tank, tank below threshold, threshold met with
      no overshoot, and threshold met with surplus. Confirm the panel's displayed figures against
      the engine's.
- [ ] Any new CSS goes **inside STORY-034's `body.expedition` section**, above the mobile media
      query.

## Notes

- **PRD §6.4** (the `launch` row), **§7.3** (launch as an event, the overshoot band) and **§7.5**
  (the numbers and how to re-derive them).
- **BLOCKED on STORY-028**, which builds `engine/launch.js` — launch commit, transit, arrivals and
  the overshoot decision. This story renders that engine and must not implement any of it. If a
  figure this panel needs is not exported, that is a gap in 028 to raise, not arithmetic to add here.
- **Depends on STORY-034** for the palette and CSS section.
- `openspec/changes/act-seven-site-ladder/` is the merged change (PR #30) supplying this panel's
  inputs, and two of its decisions are ones this story **preserves**:
  - **Reach is a function of built pad tier alone, never of current satisfaction.** A starved network
    launches later, never shorter. The panel must never render reach as degraded by resources.
  - **The tank floor is derived, not authored** — read `departingThreshold` and the derived capacity
    from config/engine; restating `1.6` in a component recreates exactly the drift the derivation
    forecloses.
- `engine/sites.js` notes that `engine/launch.js` **must read its thresholds from
  `departingThreshold`** rather than restating them; the same rule binds this panel.
- STORY-028 also owes the **minutes-of-income measurement** for the site cost ladder, deferred from
  STORY-027 because no site can be reached without launches. That is 028's obligation, not this
  panel's — but if the costs move as a result, this panel's displayed figures must come from config
  so they move with them.
- `conventions.md`: render-only components, prose in `src/data/`, no `Date.now()` outside the tick.
