---
id: STORY-038
title: Build the Artifacts panel — the puzzle surface, the graded feedback and the hint ladder
status: pr-opened
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: story/STORY-038-artifacts-panel
worktree_path: /Users/brent/idle-base-worktrees/STORY-038
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/40
is_architectural: true
approach_summary: >
  Replace `ArtifactsPanel`'s placeholder with the puzzle surface: rows from `puzzles.listPuzzles()`, the graded `near[]` feedback that is the whole point of §8.1, the hint ladder priced from `hintCost()`, the brute-force path with its cooldown read from the engine, and the instrument shop. Adds `state/actions/puzzleActions.js` with several action types and reducer wiring. No component-side timer and no `Date.now()` — the cooldown boundary is already on the tick contributor list.
created: 2026-08-16
updated: 2026-08-20
---

# Build the Artifacts panel — the puzzle surface, the graded feedback and the hint ladder

`artifacts` is separate from `ops` because **a puzzle is read, not monitored** (§6.4). The engine
behind it is STORY-029 — nine artifacts, the hint ladder, the instrument shop and the brute-force
governors — and it is the one Act VII system whose entire value is in its presentation.

§8's binding rule is **"the goal may be unclear; the FEEDBACK never is"** (§8.1), and the failure
mode it exists to prevent is a moon-logic adventure-game puzzle. That rule is discharged in the UI
or not at all: `engine/puzzles.js` already returns graded feedback through a `near[]` table that
distinguishes "close" from "wrong track", and a panel that rendered a bare "incorrect" would throw
away the story's whole point while still passing every engine check.

The other thing this panel must make visible is the **anti-softlock guarantee** (Decision 3.6): a
puzzle never gates the only path forward. There are always three ways past — solve it, buy the hint
ladder, or brute-force on a cooldown. All three must be discoverable *from the panel*, because a
guarantee the player cannot see does not reassure anyone.

## Acceptance Criteria

**The surface**

- [ ] `components/expedition/ArtifactsPanel.js` renders real content and no longer returns
      `<PlaceholderPanel />`.
- [ ] Rows come from `puzzles.listPuzzles(state)`; the panel resolves no availability and no price.
- [ ] Answer submission dispatches through a `state/actions/` module reaching
      `puzzles.submitAnswer(...)`. The component never calls an engine mutator directly.
- [ ] The prompt, the instrument readout and every other player-facing string render from
      `data/actSevenPuzzlesConfig.js` — no string literal in the component.

**Feedback, which is the story**

- [ ] A wrong answer renders the **graded** feedback the engine returns, distinguishing "close" from
      "wrong track" via `FEEDBACK_CODES` / the `near[]` table. A bare rejection fails this story.
- [ ] Answer input tolerance (case, whitespace, synonyms, numeric tolerance) is left to
      `checkAnswer` — the panel must not pre-normalize, or the two will drift.

**All three paths visible**

- [ ] The **hint ladder** renders with its prices from `hintCost()`, and buying dispatches to
      `buyHint`.
- [ ] The **brute-force** path is visible with its cooldown, driven by `attemptCooldownRemaining()`
      / `attemptCooldownSeconds()`, and the button's enabled state derives from the engine.
- [ ] A solved puzzle reads as solved, and `solvedUnaided` is distinguished where the engine
      distinguishes it.
- [ ] The **instrument shop** (`listInstruments` / `buyInstrument`) renders in the house shop
      contract shape.

**Behaviour**

- [ ] Renders without throwing against a save with **no `expedition.puzzles`** key.
- [ ] A cooldown that expires while the tab is open updates without a manual refresh — the engine
      already registers `nextPuzzleCooldownClock` on the event-clock contributor list precisely so
      the boundary lands; the panel must not poll on its own timer.
- [ ] No component-side timer or `Date.now()` — read the clock from state.

**Verification**

- [ ] `npm run build` passes.
- [ ] Drive `listPuzzles` / `submitAnswer` / `buyHint` / `attemptBruteForce` under `node` and
      confirm the panel renders the engine's returned feedback codes rather than its own.
- [ ] Any new CSS goes **inside STORY-034's `body.expedition` section**, above the mobile media
      query.

## Notes

- **PRD §8** in full — especially **§8.1** (the feedback rule), **§8.2** (how the game says "close"
  versus "wrong track") and **§8.7** (anti-soft-lock).
- **BLOCKED until STORY-029 merges.** That work is open as **PR #31**, currently MERGEABLE/CLEAN
  after a `tickEngine.js` merge resolution. **Base this story on `master` once #31 lands — do not
  stack on the branch.**
- **Depends on STORY-034** for the palette and the CSS section.
- `openspec/changes/act-seven-artifact-puzzles/design.md` **Decision 6** (the anti-softlock guarantee
  is structural) is the decision this story **preserves** — the brute-force path is the act's form of
  it, and hiding it in the UI would revoke a structural guarantee at the presentation layer.
- The engine's config records that the **first attempt is free**, so displayed wall times are (n−1)
  cooldowns rather than n, and §8.7's published table is ~one cooldown pessimistic as a result. If
  this panel shows any time estimate, take it from the engine, not from §8.7.
- `conventions.md`: components are render-only and decide nothing about availability; prose lives in
  `src/data/`. The puzzle prompts are prose and are already authored.
- **Storm-safety, do not break it.** `engine/puzzles.js` notes that nothing in `advance()` writes
  `expedition.puzzles`, so an eight-hour catch-up cannot advance an attempt count or resolve a
  puzzle. The panel must not introduce a write that happens on tick.
