---
id: STORY-020
title: Offer the call-up after the championship and give Act VI a player-gated exit
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

# Offer the call-up after the championship and give Act VI a player-gated exit

Act VI declares `exit: null` and is documented as terminal. Act VII sits after it, but crossing must
be the **player's** choice, not a cutscene that takes the franchise game away from someone who wants
to keep managing it. The championship remains the win condition; Act VII is what is on the other
side of it.

The offer reuses the existing victory-acknowledgement path rather than inventing a parallel one, and
adds **no new stored state** beyond one milestone.

## Acceptance Criteria

- [ ] Act VI gains `exit: { id: 'callUpAccepted' }` in `data/acts.js`.
- [ ] `isExitSatisfied` needs **no new predicate** — it already falls back to reading
      `progression.milestones[id]` (`progression.js:56-61`). Confirm this and do not add one.
- [ ] The offer is surfaced only when `prestige.runStats.championships >= 1`, inside the existing
      championship `Modal`, plus a re-offer path so declining is never permanent.
- [ ] Declining is the existing "Continue" action. Winning another title re-offers.
- [ ] Accepting requires an **explicit confirmation** that states the crossing is one-way, and
      dispatches a single action setting `progression.milestones.callUpAccepted`.
- [ ] The act flips on the next tick via `checkActTransition`, **not** inside the reducer.
- [ ] A player who never accepts sees Act VI behave exactly as today, prestige included, forever.
- [ ] All player-facing prose lives in `data/` (story beats / toast messages), not in the component.
- [ ] `npm run build` passes.

## Notes

- PRD §3.2 (parts 2 and 3) and §6.1.
- **Depends on STORY-014** — appending Act VII to `ACTS` without the `PRESTIGE_ACT_INDEX` fix makes
  every prestige teleport into Act VII.
- `conventions.md`: "Player-facing prose lives in `src/data/` — a string literal in a component is
  a bug." The confirmation copy is prose.
- `key-files.md`: `AppShell.js` early-returns a pre-season shell when `state.season` is absent, so
  every hook must sit above that return.
- The beat ids (`act-7-offer`) are owned by the narrative story (STORY-033); this story references
  them and does not author them.
