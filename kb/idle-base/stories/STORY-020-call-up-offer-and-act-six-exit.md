---
id: STORY-020
title: Offer the call-up after the championship and give Act VI a player-gated exit
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: story/STORY-020-call-up-offer
worktree_path: /Users/brent/idle-base-worktrees/STORY-020
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/23
is_architectural: false
approach_summary: >
  Replace Act VI's `exit: null` in data/acts.js with `exit: { id: 'callUpAccepted' }` — the file's
  own comment at acts.js:44-50 already anticipates exactly this edit. No new predicate in
  engine/progression.js: isExitSatisfied already falls back to progression.milestones[id]. The
  offer rides inside the existing championship Modal in components/layout/AppShell.js (NOT PrestigePanel),
  gated on prestige.runStats.championships >= 1, with a second explicit one-way confirmation step
  before dispatching a single action that sets progression.milestones.callUpAccepted; declining is
  the existing Continue, and a later title re-offers. The act flips on the next tick via
  checkActTransition, never in the reducer. Prose goes in data/ (toastMessages.js / storyBeats.js).
created: 2026-08-13
updated: 2026-08-14
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
