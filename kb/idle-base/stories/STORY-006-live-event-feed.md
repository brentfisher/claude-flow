---
id: STORY-006
title: Add a live event feed that narrates what the simulation just did
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-incremental-odyssey.md
branch: story/STORY-006-event-feed
worktree_path: /Users/brent/idle-base-worktrees/STORY-006
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/6
is_architectural: true
approach_summary: >-
  Add a capped `state.feed` ring buffer (~50 entries) written by `engine/tickEngine.js` at the
  points where events already resolve — `resolveGameSlot`, `resolvePlayoffRound`,
  `runOffseasonTransition`, `expirePowerups`, `processCampCompletions` — and render it
  newest-first in a scrollable component visible without switching tabs. Touches
  `engine/tickEngine.js` and `state/initialState.js`, and adds a feed component. Because
  `advance()` resolves many events in one offline step, the same buffer doubles as the
  offline-progress summary, so the cap must keep an 8-hour catch-up bounded. Contends with
  every other engine story in `tickEngine.js`. Must also decide and document whether the feed
  persists to localStorage (PRD §11.4 leaves this open).
created: 2026-08-09
updated: 2026-08-10
---

# Add a live event feed that narrates what the simulation just did

The single highest-value item in the "make the game feel alive" work. `advance()` already knows
about every meaningful thing that happens — a game resolved with a score, a training camp
completed, a powerup expired, a player retired, a championship won — and currently throws all of
it away, updating silent totals instead. A player watching the screen cannot tell the game is
running.

This story adds `state.feed`, a capped ring buffer written by the tick engine and rendered as a
scrolling broadcast log. Because `advance()` resolves many events in a single offline step, the
same feed doubles as the offline-progress summary: returning after an hour shows exactly what
happened while away.

## Acceptance Criteria

- [ ] `state.feed` exists as a capped ring buffer (~50 entries) created in
      `createInitialState()`; the cap is enforced on write so the array cannot grow unbounded.
- [ ] Feed entries are appended by `engine/tickEngine.js` at each meaningful event, carrying at
      minimum a clock timestamp, a category, and a display string.
- [ ] The following existing events write entries: game resolved (with opponent and score),
      playoff round resolved, camp completed, powerup expired, player retired, rookie signed,
      championship won, season rolled over.
- [ ] A feed component renders the buffer newest-first in a scrollable container, visible
      alongside the active panel (placement is the implementer's call, but it must be visible
      without switching tabs).
- [ ] **Offline behaviour:** returning after a long absence shows the events that occurred
      during catch-up, in order, rather than a single summary line. Confirm the ring-buffer cap
      keeps this bounded — an 8-hour catch-up must not attempt to render thousands of entries.
- [ ] Feed writes are immutable (`{ ...state, feed: [...] }`) and do not mutate the existing
      array in place.
- [ ] Running `npm start`: within one minute of watching the field view, feed entries appear
      without interaction.

## Notes

- Independent of STORY-001/002/003 in principle, but **touches `engine/tickEngine.js`, which
  STORY-001, STORY-002, STORY-003 and STORY-004 all also touch.** This is the most contended
  file in Phase 1 — schedule it after the engine-level stories land, or expect to rebase.
- **Decide and document feed persistence.** PRD §11.4 leaves this open: saving `state.feed` to
  localStorage makes the offline summary richer but grows every save file. Pick one, implement
  it, and note the choice in the PR description. Recommended default: persist it, given the cap
  already bounds the size.
- `conventions.md`: **single simulation entry point** — feed writes belong inside `advance()`
  where the events already occur, not in a React effect observing state changes.
- `conventions.md`: `src/engine/` must not import React or DOM APIs. The writer is engine code;
  the renderer is a component.
- `conventions.md`: immutable spread updates only, no mutation.
- `conventions.md`: display strings are prose — follow the existing pattern of keeping authored
  text in `src/data/` rather than inline in engine code where practical.
- `conventions.md` / `package.json`: **no test framework, linter, or CI exists** — only `start`
  and `build`. Verify by running the app and by diff review. Adding a test framework is out of
  scope per PRD §10.
- `key-files.md`: `engine/tickEngine.js` is the largest source file and the place every one of
  these events already resolves — `resolveGameSlot`, `resolvePlayoffRound`,
  `runOffseasonTransition`, `expirePowerups`, `processCampCompletions`.
- PRD §7 item 2 specifies this story.
