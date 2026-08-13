---
id: STORY-014
title: Extract PRESTIGE_ACT_INDEX so prestige stops depending on being the last act
status: in-progress
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: story/STORY-014-prestige-act-index
worktree_path: /Users/brent/idle-base-worktrees/STORY-014
base_branch: master
pr_url: null
is_architectural: true
approach_summary: >-
  Add `PRESTIGE_ACT_INDEX` to `data/acts.js` alongside `FINAL_ACT_INDEX`, with a comment
  distinguishing the two meanings that happen to coincide today; point `resetForPrestige()` at it;
  rewrite the now-stale `checkActTransition` loop comment to state the invariant that actually
  holds (the last transition is player-gated). Verified byte-identical by driving
  `resetForPrestige()` under node against a fixture before and after. Touches `data/acts.js`,
  `engine/prestige.js`, `engine/progression.js`.
created: 2026-08-13
updated: 2026-08-13
---

# Extract PRESTIGE_ACT_INDEX so prestige stops depending on being the last act

`engine/prestige.js:73` ends `resetForPrestige()` with `enterAct({ ... }, FINAL_ACT_INDEX)`. Today
`FINAL_ACT_INDEX` is 5 and Act VI is both the last act and the prestige floor, so one constant
correctly serves two unrelated meanings. The moment `data/acts.js` grows a seventh entry,
`FINAL_ACT_INDEX` becomes 6 and **every prestige teleports the player into Act VII**, skipping the
crossing entirely.

This is a latent bug, not a refactor, and it must land before any story appends to `ACTS`. It
carries no Act VII content and is independently shippable today.

It also does not overturn OpenSpec Decision 4 — it *protects* it. Decision 4 says prestige returns
the player to the Act VI index; this story is what keeps that true once Act VI stops being last.

## Acceptance Criteria

- [ ] `data/acts.js` exports `PRESTIGE_ACT_INDEX` alongside `FINAL_ACT_INDEX`, with a comment
      stating the two mean different things and why they happen to be equal today.
- [ ] `engine/prestige.js: resetForPrestige()` calls `enterAct(..., PRESTIGE_ACT_INDEX)`.
- [ ] `FINAL_ACT_INDEX` keeps its literal meaning (`ACTS.length - 1`) and is no longer read by
      `prestige.js`.
- [ ] `engine/progression.js: checkActTransition()`'s loop comment is rewritten. It currently
      justifies itself with "Act VI declares no exit, so this can never run past the final act" —
      both halves stop being true under Act VII. The new comment must state the invariant that
      actually holds: **the last transition is player-gated**.
- [ ] **Behaviour is byte-identical to today.** Verify by driving `resetForPrestige()` under `node`
      against a fixture state before and after the change and deep-comparing the results.
- [ ] `npm run build` passes.

## Notes

- `key-files.md` names `engine/progression.js` as the owner of act transitions and
  `src/data/acts.js` as the file to read first. Both are touched here.
- `openspec/changes/odyssey-progression-architecture/design.md` **Decision 4** ("Prestige resets to
  the final-act floor") is the decision this story preserves. Do not change prestige's *semantics*;
  change only which named constant expresses them.
- PRD `docs/PRD-act-seven-farm-team.md` §3.2 (parts 1 and 4) and §11.1 story 0.1.
- `conventions.md`: comments record decisions and measurements, not restatements. The rewritten
  `checkActTransition` comment is the deliverable here, not incidental.
