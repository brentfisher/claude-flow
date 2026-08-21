---
id: STORY-032
title: Add the win condition and the majors standings board
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: story/STORY-032-win-condition-majors-board
worktree_path: /Users/brent/idle-base-worktrees/STORY-032
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/36
is_architectural: true
approach_summary: >
  Every integration hook this story needs already exists and was left for it by name — the work is
  connecting them, not inventing them. `padTier5.reachesRung: 5` (data/actSevenSitesConfig.js)
  carries a comment saying engine/launch.js resolves a destination rung with no site as the win
  condition, and names STORY-032. `sites.js:overTheWallGrants()` already reads
  `milestones.overTheWall` and already gates the `majors` rung of the phase ladder, returning false
  through a defaulted lookup until something sets it — so the win condition is a milestone write at
  commit of the fifth burn, and `majors` then follows with no new phase machinery. The deterministic
  placement formula reads `aptitudeSummary()`/`solvedUnaided()` (puzzles.js), the contract board's
  `completedIds`, `overshootRatio` stored per launch record, and peak network Fuel/s. New
  `data/actSevenBoardConfig.js` for prose; the board panel REUSES components/league/StandingsPanel.js
  (89L) rather than introducing a second standings layout. Also owed by this story: §12's five-hour
  ceiling optimal-buyer run, deferred to it by STORY-028 and again by STORY-031.
created: 2026-08-13
updated: 2026-08-17
---

# Add the win condition and the majors standings board

Winning Act VII is committing the fifth burn — a *commit*, not an arrival, because the game's last
act should be the player's and not a timer's. What is on the other side is a standings table: the
exact component the player learned in Act III, with Earth as one row among other farm systems.

The last screen of the game is the first screen the game ever taught you, and you are in the
standings.

## Acceptance Criteria

- [ ] Committing the final launch sets `progression.milestones.overTheWall`. Act VII keeps
      `exit: null`.
- [ ] On arrival, `expedition.phase` becomes `majors`.
- [ ] New `data/actSevenBoardConfig.js` (prose) and a board panel that **reuses the standings
      layout** rather than introducing a new one.
- [ ] Earth's placement is **deterministic**, computed from the run — elapsed time, puzzles solved
      unaided vs. hinted vs. brute-forced, contracts completed, peak network Fuel/sec, overshoot
      ratios. **No dice.** A player who played well finishes higher, and the board says which line
      they earned.
- [ ] `majors` is a post-game state, not a new phase: the sites stay live, the click stays, and an
      endless ladder of scaling standing orders consumes Salvage and Fuel.
- [ ] Reaching `majors` does not break, reset or resurrect the frozen baseball league.
- [ ] No reset/replay axis is built (explicitly out of scope — see PRD §14).
- [ ] `npm run build` passes.

## Notes

- PRD §7.8 and §14 item 6.
- **Depends on STORY-028, STORY-031, STORY-029, STORY-030** (the placement formula reads puzzle and
  contract state).
- `conventions.md` pillar: reuse before invention. The board is the Act III standings component with
  different rows, not a new one.
- Prestige stays retired in Act VII (PRD §3.2 part 5); legacy points and perks remain in state and
  keep applying.
