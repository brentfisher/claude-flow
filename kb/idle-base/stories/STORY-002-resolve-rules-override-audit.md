---
id: STORY-002
title: Add resolveRules() and route every overridable balanceConfig read through it
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-incremental-odyssey.md
branch: story/STORY-002-resolve-rules
worktree_path: /Users/brent/idle-base-worktrees/STORY-002
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/2
is_architectural: true
approach_summary: >-
  Add `resolveRules(state)` to `engine/modifiers.js` implementing
  `balanceConfig <- act.rules <- era.rules`, then route every ad-hoc override read through it.
  Touches `engine/modifiers.js`, `engine/tickEngine.js` (line 119's direct
  `balanceConfig.playoffTeams` read and `runOffseasonTransition`'s hardcoded `secondsPerGame`)
  and `engine/prestige.js` lines 29-35. Must distinguish "not overridden" from "overridden to
  0", since the existing `||` fallback idiom treats a legitimate 0 as absent and
  `playoffTeams: 0` is a real Act III value. Collides with STORY-001 in `tickEngine.js` and
  `prestige.js` — branch from 001 rather than running concurrently.
created: 2026-08-09
updated: 2026-08-10
---

# Add resolveRules() and route every overridable balanceConfig read through it

Acts III–V reconfigure the existing season simulation to smaller scales (4 teams / 6 games
for Little League, up to 12 teams / 33 games for the big leagues) by declaring `rules` that
override `data/balanceConfig.js`. That mechanism does not currently work reliably: `era.rules`
is not processed by `computeModifiers()` at all — it is read ad-hoc by individual consumers —
and several `balanceConfig` fields are read **directly**, bypassing overrides entirely.

Two confirmed cases, both load-bearing for the act system:

- `engine/tickEngine.js:119` reads `balanceConfig.playoffTeams` directly, so Act III's
  `rules: { playoffTeams: 0 }` (a league with no playoffs) would silently do nothing.
- `runOffseasonTransition()` routes `gamesPerSeason` through `eraRules` but hardcodes
  `secondsPerGame: balanceConfig.secondsPerGame` (twice), so Acts III/IV/V's 25s/40s/50s
  pacing would apply on entry and then **silently revert to 60s at the first offseason
  transition**, destroying the pacing curve most of PRD §5 depends on.

This story introduces a single `resolveRules(state)` helper and converts every overridable
direct read to use it. It is a prerequisite for Acts III–V, not cleanup.

## Acceptance Criteria

- [ ] `engine/modifiers.js` exports `resolveRules(state)` returning a resolved rules object
      layered `balanceConfig ← act.rules ← era.rules` (era last / highest precedence, per
      PRD §3.3).
- [ ] `resolveRules` tolerates an absent `state.progression` slice (returns
      `balanceConfig ← era.rules`), so this story can land before STORY-004 creates
      `data/acts.js`.
- [ ] An audit of `src/engine/` has been performed for direct `balanceConfig.*` reads, and
      every field an act or era needs to override is routed through `resolveRules()`.
      `playoffTeams` and `secondsPerGame` are the two known cases; the diff should show
      whether any others were found.
- [ ] The existing ad-hoc `era.rules` reads are converted: `tickEngine.js:157`
      (`modifiers.era.rules`) and `prestige.js:29-35` (`leagueTeamCount`, `gamesPerSeason`,
      `tradeWindows`).
- [ ] Note the existing `||` fallback idiom (`era.rules.gamesPerSeason || balanceConfig...`)
      treats a legitimate `0` as absent. `resolveRules` must distinguish "not overridden"
      from "overridden to 0" — `playoffTeams: 0` is a real Act III value.
- [ ] **Regression check:** with no overrides present (era 0, no acts), every resolved value
      equals today's `balanceConfig` value, and a full season plays out identically —
      33 games, 4 playoff teams, 60s per game.
- [ ] **Override check:** temporarily setting `secondsPerGame` in era 0's `rules` changes game
      pacing *and survives an offseason transition into the next season*. (Revert the temporary
      edit before finishing; the point is to prove the override path works end to end.)
- [ ] Running `npm start`: a season completes, playoffs seed correctly, and the offseason
      transition produces a next season with the expected game count and pacing.

## Notes

- **Rebase on STORY-001.** Both stories rewrite `engine/tickEngine.js` — STORY-001 changes
  `addRevenue` and the revenue line, this story changes `runOffseasonTransition` and the
  `playoffTeams` read. Land STORY-001 first and branch from it to avoid a merge conflict.
- `conventions.md`: `src/engine/` must not import React or DOM APIs — `resolveRules` belongs
  in `engine/modifiers.js` alongside `computeModifiers`, keeping the composition logic in one
  place.
- `conventions.md`: the modifier composition chain is documented in `engine/modifiers.js` as
  `balanceConfig ← era ← perks ← powerups`. This story adds the *rules* axis, which is
  separate from the additive `modifierBonuses` axis — keep the two clearly distinguished in
  code and comments. PRD §3.3 specifies acts insert as `act ← era ← perks ← powerups` on the
  bonuses axis.
- `conventions.md`: comments in this codebase explain non-obvious invariants rather than
  restating code (see `engine/modifiers.js`, `engine/tickEngine.js`). The precedence order and
  the `0`-vs-absent subtlety both deserve a comment in that style.
- `conventions.md` / `package.json`: **no test framework, linter, or CI exists** — only
  `start` and `build`. Verify by running the app and by diff review. Adding a test framework
  is out of scope per PRD §10.
- PRD §3.3 is the specification for this story, including the worked `playoffTeams` and
  `secondsPerGame` examples.
