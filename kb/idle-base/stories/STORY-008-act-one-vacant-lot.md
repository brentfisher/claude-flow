---
id: STORY-008
title: Build Act I — The Vacant Lot (clicker, collectors, starter kit) and the narrative layer
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-incremental-odyssey.md
branch: story/STORY-008-act-one
worktree_path: /Users/brent/idle-base-worktrees/STORY-008
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/8 (closed; landed directly as af3c385)
is_architectural: true
approach_summary: >-
  Build the opening clicker act: a click action plus `state.clicker`, collector tiers feeding
  STORY-003's `collectors` contributor, the Starter Kit purchases, and Act I's exit predicate;
  plus the narrative layer (`data/storyBeats.js` and act-intro cards reusing
  `components/common/Modal.js`). Adds `state/actions/clickerActions.js`, a
  `components/lot/` directory and data config; touches `state/actionTypes.js` and
  `state/gameReducer.js`. Act I income must be rate-integrated so offline catch-up is not
  truncated by `safetyCapIterations`. Clicking is never removed — from Act II it persists as
  Hustle, which is the anti-softlock guarantee. Integration story for the whole Phase 1 spine;
  depends on 001, 003 and 004.
created: 2026-08-09
updated: 2026-08-10
---

# Build Act I — The Vacant Lot (clicker, collectors, starter kit) and the narrative layer

The first three to five minutes of the game, and the moment the odyssey either works or doesn't.
The player is nine years old behind a hardware store, clicking to pick bottle caps out of the
dirt. One button, one currency, no tabs. Within about 25 clicks they can afford a Kid Brother who
collects for them, and the game quietly becomes an idle game.

This story also carries the narrative layer, since Act I is its first consumer: act-intro story
cards and the authored prose that frames each act.

## Acceptance Criteria

**The clicker**
- [ ] A single prominent *Search the lot* button yields `clicker.perClick` caps (base `1`) per
      click, dispatching a new action type via `state/actions/clickerActions.js`.
- [ ] `state.clicker = { totalClicks, perClick }` is tracked.
- [ ] A fresh game shows this button and nothing else — no tabs, no stats the player has not
      earned.

**Purchases (PRD §5 Act I table)**
- [ ] Kid Brother (collector tier 1) — **25 caps**, +0.2 caps/sec
- [ ] Sharper Eyes (click upgrade) — **60 caps**, +1 cap/click
- [ ] Wagon (collector tier 2) — **120 caps**, +0.8 caps/sec
- [ ] Glove **40**, Ball **25**, Bat **75** — the Starter Kit items
- [ ] Costs and rates live in `src/data/` as config, not inline in components or engine code.

**Income and exit**
- [ ] Collectors feed the `collectors` contributor added by STORY-003; caps accrue while idle
      and while the tab is closed.
- [ ] Act I income is **rate-integrated**, registering no per-second events with
      `findNextEventClock()` (see STORY-003 — an event-driven implementation silently loses
      ~7 hours of an 8-hour offline return to the iteration cap).
- [ ] Owning all three Starter Kit items satisfies Act I's exit predicate and transitions the
      player to Act II.
- [ ] **Pacing check:** the first automation is affordable within ~25 clicks / ~45 seconds, and
      the act completes in roughly 3–5 minutes of active play (PRD §9 criterion 2).

**Narrative layer**
- [ ] `src/data/storyBeats.js` holds all authored act prose — no prose strings in components.
- [ ] Entering an act shows a full-screen story card reusing
      `components/common/Modal.js` with the act title, prose, and the new objective.
- [ ] Dismissing a beat records it in `progression.storyBeatsSeen` so it does not reappear on
      reload.
- [ ] Intra-act beats (first collector, first Starter Kit item) surface as feed entries rather
      than modals, if STORY-006 has landed; otherwise this may be deferred.

**Hustle**
- [ ] Clicking is **never removed** — from Act II onward it persists as *Hustle*, a manual
      action whose absolute value scales per act. This is the anti-softlock guarantee of PRD
      §6.4; the click action must not be gated off when Act I ends.

## Notes

- **Depends on STORY-003** (the `collectors` income contributor), **STORY-004** (progression
  engine, `data/acts.js`, and the pre-Act-VI state shape that lets a game exist with no season),
  and **STORY-001** (`wallet.caps`). This is the integration story for the whole Phase 1 spine —
  land it last among the framework stories.
- Benefits from **STORY-005** (tab reveal) and **STORY-007** (floating gains on the click
  button), but does not strictly require them.
- `conventions.md`: new simulation logic belongs in `src/engine/`, never inlined into a reducer
  action or a component. Costs and rates belong in `src/data/`.
- `conventions.md`: components are feature-directory-scoped — a new `src/components/lot/`
  directory is the right home, matching `field/`, `roster/`, etc.
- `conventions.md`: action-type constants go in `state/actionTypes.js`; one action module per
  domain under `state/actions/`, each exporting pure `(state, action) => newState` functions.
- `conventions.md`: CommonJS, plain `function` declarations, single quotes, 2-space indent.
- `conventions.md` / `package.json`: **no test framework, linter, or CI exists** — only `start`
  and `build`. Verify by running the app and by diff review; the pacing check is a manual
  playtest. Adding a test framework is out of scope per PRD §10.
- PRD §5 (Act I), §6.3 (narrative layer) and §6.4 (anti-softlock) specify this story. The
  numbers in the purchase table are first-pass estimates flagged for playtesting in PRD §11.1 —
  tune them if the act reads as too slow or too fast, and say so in the PR.
