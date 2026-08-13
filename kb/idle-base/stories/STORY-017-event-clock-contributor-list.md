---
id: STORY-017
title: Refactor findNextEventClock into a contributor list
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

# Refactor findNextEventClock into a contributor list

`engine/tickEngine.js:117-132 findNextEventClock(working)` is a twelve-line function that hardcodes
four candidate sources (next game, playoff round, powerup expiry, camp completion). **Four separate
Act VII stories need to add candidates to it** — colony resource boundaries, launch arrivals and
site builds, puzzle cooldowns, and contract windows. Four stories editing one twelve-line function
is the highest-collision seam in the whole Act VII plan.

This story converts it to a registration list, in the shape `engine/income.js` already uses for
income contributors, so each later story appends one registration instead of editing shared control
flow. The same argument was made for income in the odyssey PRD's Decision 3.1 and was right there.

## Acceptance Criteria

- [ ] `findNextEventClock` iterates a module-level contributor list; each contributor is a pure
      `(state) => clock | Infinity`.
- [ ] The four existing candidate sources become four registered contributors with no behaviour
      change.
- [ ] `findNextEventClock` returns identical values to the current implementation across a fixture
      sweep covering: no season, regular-season, playoffs, active powerups, and in-progress camps.
      Verify under `node`.
- [ ] Contributors tolerate absent state slices (a contributor for a slice that does not exist
      returns `Infinity`, never throws).
- [ ] A comment records why the list exists — that it is a shared seam with several pending
      consumers — so the next contributor is appended rather than inlined.
- [ ] `npm run build` passes.

## Notes

- PRD ledger **R5** ("One solve, one boundary helper, one `findNextEventClock` refactor") mandates
  this as a Phase 0 story explicitly.
- `key-files.md` flags `tickEngine.js` as "the most likely file for two parallel changes to
  collide in." This story exists to defuse that.
- `engine/income.js` is the shape to copy — `module-map.md` calls it "where a new passive income
  source plugs in", and the same ergonomics are wanted here.
- Blocks STORY-018, STORY-027, STORY-028, STORY-029, STORY-030. Land it before any of them.
