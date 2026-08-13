---
id: STORY-012
title: Add concessions — the first passive coin income, shaped like ticketing
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-incremental-odyssey.md
branch: null
worktree_path: null
base_branch: null
pr_url: null
approach_summary: null
created: 2026-08-10
updated: 2026-08-10
---

# Add concessions — the first passive coin income, shaped like ticketing

A snack table behind the backstop. Mechanically this is the third contributor in
`engine/income.js` and the first one to pay coins, but its real job is rehearsal: it is
deliberately shaped like the ticketing economy so that when Act V switches on stadium
capacity, ticket pricing and attendance, the player is reading a familiar instrument at a larger
scale rather than meeting a new system.

Everything the contributor needs already exists. `advance()` already integrates a per-currency
bundle and `creditIncome()` already credits `wallet.coins` (`engine/tickEngine.js:66-80`), so
this story adds a contributor and a small purchase UI, and touches no tick-loop code at all.

## Acceptance Criteria

**The contributor**

- [ ] `engine/income.js` gains a real `concessions` contributor returning coins per second,
      summed into the `coins` slot of the bundle `totalIncomePerSecond()` returns. The bundle's
      shape and signature do not change.
- [ ] The contributor is gated on the `concessions` feature being unlocked —
      `getUnlockedFeatures(state.progression.act).includes('concessions')`, which Act III's
      `unlocks` array already declares (`data/acts.js:54`). It returns `0` before Act III and
      causes no error when `state.income.concessions` is absent from an older save.
- [ ] It is **not** suspended during an offseason. The `phase !== 'offseason'` gate belongs to
      ticketing alone — design.md Decision 1: "suspension is a property of ticket sales, not of
      income in general." A snack table sells during the offseason.
- [ ] Rates and costs live in a new `src/data/concessionsConfig.js`, not inline in the engine or
      a component.

**Proto-ticketing shape**

- [ ] The stand is a **level-based upgradeable** contributor whose cost curve mirrors
      `stadiumUpgradeCost()`'s geometric growth (`engine/economy.js:41-44`) and whose rate grows
      with level — the same instrument Act V hands the player at stadium scale. Do not build
      attendance modelling, ticket pricing or elasticity into it; PRD §5 calls it "mechanically a
      flat `coins/sec` contributor" and design.md's table calls it "proto-ticketing". Level-based
      and upgradeable satisfies both readings; a second attendance model does not.
- [ ] Upgrades are bought with coins, are rejected when unaffordable, and never take the balance
      below zero (currency spec, "Currency balances never go negative").
- [ ] Buying an upgrade visibly raises the coins/sec rate shown in the header immediately —
      `HeaderStats` reads `totalIncomePerSecond()` directly, so this should follow for free;
      verify it does (game-feedback spec, "Rate changes after a purchase").

**UI placement**

- [ ] The concessions stand renders as a section of the **Field** tab (`components/field/`),
      gated on the `concessions` unlock. It must **not** become a new `PANELS` key —
      `concessions` is a mechanic-level unlock inside an already-visible panel, per the header
      comment in `data/acts.js`, and adding a tab would drag in `AppShell.js`, which STORY-011
      owns.
- [ ] New action type appended to the end of the relevant block in `state/actionTypes.js`, with a
      new `state/actions/concessionsActions.js` module wired into `gameReducer.js`. Append only;
      do not reorder existing entries — STORY-013 appends to the same two files.

**Offline parity (required — this changes what `advance()` credits)**

- [ ] **Rate-integrated, never event-driven.** Concessions must register nothing with
      `findNextEventClock()`. `advance()` is bounded by `safetyCapIterations` (2,000) while
      `offlineCapSeconds` allows 8 hours (28,800s), so a per-second event would hit the cap and
      silently discard hours of income (design.md, Decision 1, "Constraint").
- [ ] **Offline parity check:** returning after N hours offline credits the same coin total as N
      hours of continuous live ticking, at a duration long enough that the iteration cap would
      bite if the implementation were event-driven. `engine/offlineProgress.js` calls the same
      `advance()`, so there is one code path — verify it, do not assume it.
- [ ] Note that in Act III the game *is* event-driven for a different reason (a 25s game clock),
      so an 8-hour return already runs ~1,152 iterations. Concessions must not add to that count.
- [ ] `applyOfflineProgress()`'s summary currently diffs only `wallet.cash`
      (`offlineProgress.js:14-16,23`), so a coin-only Act III return reports `revenueEarned: 0`.
      Either report the coin gain too or state in the PR that it is deliberately left for a later
      story — do not leave it silently wrong.

**Non-regression**

- [ ] Cash accrual in a stadium-and-season state (the Act VI configuration) is numerically
      unchanged. The `ticketing` contributor is not touched.
- [ ] Caps accrual in Acts I–II is unchanged, and no coins accrue before Act III.

## Notes

- **Depends on STORY-010** (Act III, coins, and the pre-created `income.concessions` slice) and
  reads the currency decision STORY-011 settles. It can be developed in parallel with STORY-011 —
  the file sets are disjoint apart from `FieldView.js`, noted below.
- **File ownership.** This story owns `engine/income.js`, `data/concessionsConfig.js` (new),
  `state/actions/concessionsActions.js` (new) and the concessions component(s) under
  `components/field/`. It must **not** open `state/initialState.js` (STORY-010 pre-creates
  `income.concessions`), `engine/tickEngine.js` (`creditIncome()` already handles coins — no
  change is needed and none should be made), `engine/progression.js`, `data/acts.js` or
  `components/layout/AppShell.js`.
- **Overlap to expect:** `components/field/FieldView.js` is also touched by STORY-011 (rendering
  a three-man roster). Coordinate or rebase; the two changes are in different regions of the file.
- design.md Decision 1 and PRD §3.1: income flows through a generalized contributor list so each
  act *adds a contributor* rather than editing a conditional every other act also touches. Do not
  branch by act inside `advance()`.
- `openspec/.../specs/income/spec.md`: "Adding a new income source MUST NOT require changing how
  existing sources are credited"; "Conditions that suspend one income source SHALL NOT suspend
  unrelated sources"; and offline credit must equal live credit for the same elapsed duration.
- STORY-003's PR notes record the scaffolding this story replaces: `income.js` currently has an
  `isUnlocked(state, feature)` helper that infers unlocks from state presence, with a TODO to
  become `getUnlockedFeatures(state.progression.act).includes(feature)` now that
  `engine/progression.js` exists. Make that swap — it is deliberately one function body.
- `conventions.md`: `src/engine/` is pure — no React or DOM imports. `src/data/` is config with no
  logic. Immutable spread updates only. CommonJS, plain `function` declarations, single quotes,
  2-space indent.
- **No test framework, linter or CI exists** — `package.json` has only `start` and `build`.
  Verification is by running the app plus diff review; the offline-parity check can be done with a
  throwaway `node` harness against the pure engine (STORY-003 did exactly this) or by editing
  `meta.lastSaveTimestamp` in a saved game. Adding a test framework is out of scope per PRD §10.
- PRD §3.1 (the contributor table), §5 (Act III, "Concessions") and design.md's income table
  specify this story.
