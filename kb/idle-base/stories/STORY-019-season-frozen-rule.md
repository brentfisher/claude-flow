---
id: STORY-019
title: Add the seasonFrozen rule so the baseball simulation can pause without being deleted
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

# Add the seasonFrozen rule so the baseball simulation can pause without being deleted

Act VII stops the baseball game. It must not *delete* it: `advance()` dereferences `state.season`
every iteration, and `AppShell` early-returns a pre-season shell when `!state.season` — so nulling
the slice takes the **whole app** down the Act I/II path, not just the tabs.

A resolved rule `seasonFrozen` lets an act suspend season progression while every slice stays
intact and valid. Small, self-contained, and needed by the Act VII shell story.

## Acceptance Criteria

- [ ] `seasonFrozen` is a resolvable rule read through `resolveRules(state)` / `computeModifiers`,
      not a bare `balanceConfig` read.
- [ ] When set, `advance()` skips season-phase progression, game resolution, playoff rounds and the
      `ticketing` income contributor.
- [ ] When set, `season`, `league`, `roster`, `stadium` and `powerups` remain in state **untouched**
      and valid — nothing is nulled, emptied or reshaped.
- [ ] When unset (every act today), behaviour is identical to current. Verify by driving `advance()`
      over a full simulated season before and after the change and deep-comparing.
- [ ] Verified on a scratch act with `rules: { seasonFrozen: true }`: the clock advances, non-ticket
      income accrues, and no game is ever resolved.
- [ ] `npm run build` passes.

## Notes

- PRD §3.5 and §11.1 story 0.5.
- `key-files.md`: `engine/modifiers.js` — "Never read `balanceConfig` directly for anything an act
  can override." `seasonFrozen` is act-overridable and must go through `resolveRules`.
- `engine/income.js` already owns the `phase !== 'offseason'` gate inside the `ticketing`
  contributor; the frozen gate belongs in the same place, for the same reason.
- `conventions.md`: `resolveRules` layers by spread so a legitimate `0`/`false` is distinguishable
  from "not overridden". Do not use `||` defaulting here.
