---
id: STORY-029
title: Add the artifact puzzles, the hint ladder and the instrument shop
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: story/STORY-029-puzzles-instruments
worktree_path: /Users/brent/idle-base-worktrees/STORY-029
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/31
is_architectural: true
approach_summary: null
created: 2026-08-13
updated: 2026-08-16
---

# Add the artifact puzzles, the hint ladder and the instrument shop

Nine artifacts that must be *understood*, not merely afforded — each a piece of orbital mechanics
dressed as alien hardware, and each solvable from the baseball metaphor the player already has.

The design rule: **the goal may be unclear; the feedback never is.** The failure mode this story
must avoid is a moon-logic adventure-game puzzle.

## Acceptance Criteria

- [ ] New `data/actSevenPuzzlesConfig.js` (all prose and answers) and `engine/puzzles.js` (pure).
- [ ] `engine/puzzles.js` exports `listPuzzles(state)` in the shop-contract shape,
      `checkAnswer(puzzleId, input)`, `buyHint(state, puzzleId)`, `solvedUnaided(state, id)`, and a
      brute-force attempt path with an `...AtClock` cooldown.
- [ ] Answer validation tolerates input formatting — case, whitespace, synonyms, numeric tolerance.
- [ ] Wrong answers give **graded feedback**: a `near[]` table distinguishing "close" from "wrong
      track". No bare rejection.
- [ ] **Three ways past every puzzle**: solve it, buy the hint ladder, or brute-force on cooldown.
      No puzzle gates the only path forward.
- [ ] Hint and instrument prices are **generated from STORY-024's measured Salvage bands** by the
      documented formula, not pinned to constants. The derived column is regenerate-don't-edit.
- [ ] **The brute-force multiplier is measured and ≤ 1.3×** (ledger R9). At 1.5× the act breaches
      the 5-hour ceiling. `attemptsToBypass` comes down until the measured ratio clears. A ratio
      asserted rather than measured does not discharge this.
- [ ] Puzzle state lives in `expedition.puzzles` and `progression.milestones`; the cooldown
      registers on STORY-017's contributor list.
- [ ] `npm run build` passes.

## Notes

- PRD §8 in full; ledger **R6**, **R8** (recompute `R(phase)`) and **R9** (the 1.3× ceiling).
- **Depends on STORY-024** (bands), **STORY-017**, **STORY-021** (the `artifacts` tab).
- `conventions.md`: player-facing prose lives in `src/data/`; a string literal in a component is a
  bug. The puzzle prompts are prose.
- `openspec/.../design.md` **Decision 6** — the anti-softlock guarantee is structural. The
  brute-force path is this story's form of it.
- §8's hint ladder is the act's **elastic sink**: no pacing table depends on it, so it is the right
  place to absorb a rebalance.
