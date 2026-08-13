---
id: STORY-001
title: Migrate state.cash to a multi-currency wallet and bump the save format to v2
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-incremental-odyssey.md
branch: story/STORY-001-wallet-refactor
worktree_path: /Users/brent/idle-base-worktrees/STORY-001
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/1
is_architectural: true
approach_summary: >-
  Mechanical rename of the single `state.cash` number into
  `state.wallet = { caps, coins, cash }`, landed before any act work so later stories do not
  each special-case currency access. Touches `state/initialState.js`, all four modules under
  `state/actions/`, `engine/tickEngine.js` (`addRevenue`), `engine/prestige.js`
  (`resetForPrestige`), and the readers in `components/layout/HeaderStats.js`,
  `components/prestige/PrestigePanel.js`, `components/ticketing/*` and
  `components/common/Button.js`. Also bumps `CURRENT_VERSION` to 2 in
  `persistence/saveLoad.js`, intentionally wiping all v1 saves through the existing
  discard-on-mismatch path. No gameplay or balance change.
created: 2026-08-09
updated: 2026-08-10
---

# Migrate state.cash to a multi-currency wallet and bump the save format to v2

The odyssey uses three currencies across its six acts — bottle caps (Acts I–II), coins
(Acts III–IV), and cash (Acts V–VI) — but state currently exposes a single `state.cash`
number. This story is the mechanical refactor to `state.wallet = { caps, coins, cash }`,
done up front and on its own so that no later act story has to special-case currency
access or fight a rename mid-flight. It also bumps `CURRENT_VERSION` in
`persistence/saveLoad.js` to `2`, which is the intentional hard wipe of all existing
`idle-base-save-v1` saves described in PRD §3.4.

This is a pure refactor: no gameplay, balance, or UI behaviour changes. Cash accrues at
the same rate and every existing purchase works exactly as before.

## Acceptance Criteria

- [x] `state.wallet = { caps: 0, coins: 0, cash: <startingCash> }` exists in
      `createInitialState()`, and the top-level `state.cash` field is gone.
- [x] No reads of `state.cash` / `working.cash` remain anywhere in `src/` — verified by
      grep returning only `wallet.cash` accesses.
- [x] All currency writers are migrated: `engine/tickEngine.js` (`addRevenue`),
      `engine/prestige.js` (`resetForPrestige`), and every handler in
      `state/actions/economyActions.js`, `rosterActions.js`, `prestigeActions.js`.
- [x] All currency readers are migrated: `components/layout/HeaderStats.js`,
      `components/prestige/PrestigePanel.js`, `components/ticketing/*`, and
      `components/common/Button.js` (whose `cash` prop drives affordability).
- [x] `persistence/saveLoad.js` has `CURRENT_VERSION = 2`.
- [x] With a v1 save present in `localStorage`, loading the app discards it and starts a
      fresh game without throwing (the existing version-mismatch path already does this —
      confirm it still works rather than adding a migration).
- [x] Running `npm start`: cash accrues per second, stadium upgrades, powerup purchases,
      stat upgrades and perk purchases all still succeed and still gate on affordability.
- [x] `caps` and `coins` are present in state but unused by any mechanic in this story.

## Notes

- **Land this before STORY-002 and STORY-003.** Both touch `engine/tickEngine.js`;
  STORY-002 edits `runOffseasonTransition` and the `playoffTeams` read while this story
  edits `addRevenue` and the revenue line. Running them concurrently in separate
  worktrees will produce a merge conflict in the same file. This story is the base.
- `conventions.md`: CommonJS throughout (`require` / `module.exports`) — do **not**
  introduce `import`/`export` syntax even though Babel is configured for it. Plain
  `function foo() {}` declarations, single quotes, 2-space indent.
- `conventions.md`: state updates are immutable spreads (`{ ...state, wallet: {...} }`),
  no mutation and no immutability library.
- `conventions.md` / `package.json`: **there is no test framework, linter, or CI in this
  repo** — only `start` and `build` scripts. Acceptance is verified by running the app
  (`npm start`) and by diff review. Adding a test framework is explicitly out of scope
  per PRD §10.
- `key-files.md`: `state/initialState.js` defines the full state shape and is the anchor
  file for this change.
- PRD §4 specifies the wallet shape; PRD §3.4 specifies the save-wipe decision and the
  rationale for not writing a migration.
