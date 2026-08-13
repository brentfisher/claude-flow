---
id: STORY-004
title: Add the progression engine, act config, and pre-Act-VI state shape
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-incremental-odyssey.md
branch: story/STORY-004-progression-engine
worktree_path: /Users/brent/idle-base-worktrees/STORY-004
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/4
is_architectural: true
approach_summary: >-
  Add `data/acts.js` (mirroring the `data/eras.js` shape, extrapolation-safe like
  `getEraConfig`) and `engine/progression.js` with a derived `getUnlockedFeatures`,
  `checkActTransition` and `enterAct`; restructure `initialState.js` so player-visible content
  (`stadium`, `league`, `season`, `playoffs`) is null while tick-loop collections (`roster`,
  `powerups`, `runStats`) are present-and-empty. Touches `state/initialState.js`,
  `engine/tickEngine.js` (one `season == null` guard at the phase block plus the transition
  call) and `engine/prestige.js` (reset to the Act VI floor, zero `runStats` on entry).
  Unlocks are derived from the act index rather than stored, so retuning takes effect on
  existing saves with no migration. Rewrites the same `initialState.js` as STORY-001.
created: 2026-08-09
updated: 2026-08-10
---

# Add the progression engine, act config, and pre-Act-VI state shape

This is the framework the entire odyssey hangs off: a declarative act config, an engine that
knows which act the player is in and when they advance, and a state shape that can honestly
represent "the stadium does not exist yet."

`createInitialState()` currently builds everything eagerly — a 15-man professional roster, a
12-team league, a full schedule, standings and trade windows — so a fresh game starts with the
whole game already constructed. Under the odyssey, act transitions become the initializer
boundary: entering Act III is what calls `generateSeasonSchedule()` for the first time.

## Acceptance Criteria

**Act config**
- [ ] New `src/data/acts.js` defines the six acts from PRD §5, mirroring the shape of
      `data/eras.js`: `{ id, name, description, entry, exit, rules, modifierBonuses, unlocks }`.
- [ ] `getActConfig(actIndex)` mirrors `getEraConfig` and is safe past the authored range.
- [ ] Act VI declares `rules: {}` so it defers entirely to the era config, preserving today's
      prestige-era behaviour.

**Progression engine**
- [ ] New `src/engine/progression.js` exports `getActConfig`, `getUnlockedFeatures(actIndex)`,
      `checkActTransition(state)`, and `enterAct(state, actIndex)`.
- [ ] `getUnlockedFeatures` returns the **cumulative union** of `unlocks` arrays for acts
      `0..actIndex` and is **derived, never stored** — retuning which act unlocks a feature
      must take effect on an existing save with no migration.
- [ ] `enterAct` runs that act's initializers (creating the content it owns) and records
      `progression.actEnteredAtClock`.
- [ ] `checkActTransition(state)` is called from `advance()` once per loop iteration, after the
      existing phase handling.
- [ ] **Offline parity (required):** a player who closes the tab in one act and returns after
      enough elapsed time to satisfy the exit condition arrives in the next act, with the
      transition having fired during catch-up — not stuck at the boundary. PRD §6.1 asserts
      this; it must actually be exercised.

**State shape (PRD §3.2 carve-out)**
- [ ] `state.progression = { act, actEnteredAtClock, milestones, seenTabs, storyBeatsSeen }`
      is created in `createInitialState()`.
- [ ] **Player-visible content is `null` until its act creates it:** `stadium`, `league`,
      `season`, `playoffs`.
- [ ] **Tick-loop collection slices are present-and-empty from t=0:** `roster: []`,
      `powerups: { active: [], purchasedPermanentIds: [] }`, `prestige.runStats` zeroed.
      Iterating an empty array is free; guarding every call site is not.
- [ ] `advance()` gets **one** guard at the top of the phase-handling block for `season == null`
      — not a check per line. The loop must not throw with a null season, and the following
      existing calls must remain safe: `expirePowerups`, `processCampCompletions`,
      `updatePeakRating`, `addRevenue`, `findNextEventClock`, and the three
      `season.phase === ...` branches.
- [ ] A fresh game (Act 0) runs `advance()` for several minutes with no season, no stadium and
      an empty roster without throwing.

**Prestige**
- [ ] `resetForPrestige()` sets `progression.act` to the Act VI index and leaves all Act I–V
      unlock flags on, so prestige never replays the odyssey (PRD §3.3).
- [ ] Entering Act VI zeroes `prestige.runStats`, so Acts III–V revenue does not inflate the
      first legacy-point payout (PRD §3.3).

## Notes

- Depends on **STORY-002** for `resolveRules()` if act `rules` are to take effect. STORY-002 is
  written to tolerate an absent `progression` slice, so the two can land in either order — but
  act rules are inert until both are in.
- Touches `state/initialState.js`, which **STORY-001 also rewrites**. Land STORY-001 first.
- Also touches `engine/tickEngine.js` (the `checkActTransition` call and the season guard) —
  coordinate with STORY-002 and STORY-003, which touch the same file.
- `conventions.md`: config/tuning data lives in `src/data/*.js` with no logic; simulation logic
  lives in `src/engine/` with no React/DOM imports. `acts.js` is data, `progression.js` is
  engine — keep the split clean.
- `conventions.md`: `data/eras.js` is the model to imitate. It already implements "declarative
  stage with `rules` overriding balanceConfig plus additive `modifierBonuses`," including
  extrapolation past authored content. Do not invent a parallel config system.
- `conventions.md`: comments explain non-obvious invariants rather than restating code — the
  derived-not-stored unlock decision and the content-vs-collections state split both warrant one.
- `conventions.md` / `package.json`: **no test framework, linter, or CI exists** — only `start`
  and `build`. Verify by running the app and by diff review. Adding a test framework is out of
  scope per PRD §10.
- `key-files.md`: `state/initialState.js` defines the full state shape; any new top-level field
  must be added there or new games start without it.
- PRD §3.2, §3.3, §4 and §6.1 together specify this story.
