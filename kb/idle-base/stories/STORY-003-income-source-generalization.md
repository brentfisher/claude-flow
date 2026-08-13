---
id: STORY-003
title: Generalize tick income into an unlockable income-source list
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-incremental-odyssey.md
branch: story/STORY-003-income-sources
worktree_path: /Users/brent/idle-base-worktrees/STORY-003
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/3
is_architectural: true
approach_summary: >-
  New `engine/income.js` exporting `totalIncomePerSecond(state, modifiers)` that sums every
  unlocked contributor into a per-currency bundle; `advance()` calls it instead of
  `revenuePerSecond()`, and the offseason gate moves inside the ticketing contributor since
  suspension is a property of ticket sales rather than of income generally. Adds
  `engine/income.js` and touches `engine/tickEngine.js`; wraps `engine/economy.js` without
  modifying it. Income must stay rate-integrated rather than event-driven — an event per
  second would force ~28,800 iterations on an 8-hour offline return, hit
  `safetyCapIterations` (2,000), and silently discard roughly seven hours of the player's
  income. Depends on STORY-001's wallet for somewhere to credit the bundle.
created: 2026-08-09
updated: 2026-08-10
---

# Generalize tick income into an unlockable income-source list

`advance()` cannot produce Act I income as written. Its revenue line is gated on
`season.phase !== 'offseason'` and calls `revenuePerSecond()`, which reads
`state.stadium.capacity` and `state.stadium.ticketPrice`, while `attendanceFraction()` reads
`state.season.schedule` and `state.reputation`. In Act I there is no stadium and no schedule —
there are bottle caps being picked out of the dirt.

This story replaces the single hardcoded revenue call with `engine/income.js`, whose
`totalIncomePerSecond(state, modifiers)` sums the contributions of every currently unlocked
income source and returns a per-currency bundle. Each later act adds a contributor instead of
editing a conditional that every other act also touches — and because `engine/offlineProgress.js`
calls the same `advance()`, one implementation serves both live ticking and offline catch-up.

## Acceptance Criteria

- [x] New `src/engine/income.js` exports `totalIncomePerSecond(state, modifiers)` returning a
      per-currency bundle, e.g. `{ caps: 0.4, coins: 0, cash: 0 }`.
- [x] `advance()` calls `totalIncomePerSecond()` instead of `revenuePerSecond()` and credits
      each currency in the returned bundle via `addRevenue` (or its wallet-aware successor).
- [x] The `phase !== 'offseason'` gate is **moved inside the `ticketing` contributor** — it is a
      property of ticket sales, not of income in general. Bottle caps must not stop accruing
      during an offseason.
- [x] The `ticketing` contributor wraps the existing `revenuePerSecond()` **unchanged** and
      returns `0` when `state.stadium == null`, so `engine/economy.js` needs no edits.
- [x] Contributor scaffolding exists for the sources named in PRD §3.1 (`collectors`,
      `wallBallDues`, `concessions`, `sponsorships`, `ticketing`), each gated on its own unlock
      condition. Only `ticketing` needs a real implementation in this story; the rest may
      return zero until their act lands.
- [x] **Rate-integrated, not event-driven.** Early-act income must not register per-second
      events with `findNextEventClock()`. `advance()` is bounded by
      `balanceConfig.safetyCapIterations` (2,000) while `offlineCapSeconds` allows 8 hours
      (28,800s); a per-second event would hit the cap and silently discard ~7 hours of the
      player's income. `findNextEventClock()` returning `Infinity` with no discrete events
      pending is correct behaviour.
- [x] **Offline parity (required):** returning after N hours offline credits the same total as
      N hours of continuous live ticking, for a state with only rate-based sources. Verify at a
      duration long enough to exceed 2,000 seconds so the iteration cap would bite if the
      implementation were event-driven.
- [x] **Regression:** with a stadium present and a season running (current Act VI state), cash
      accrues at numerically the same rate as before this change.
- [~] Running `npm start`: the dev server and the production build both compile clean and
      serve (HTTP 200), and revenue accrual / offseason suspension are proven by direct
      engine calls. An interactive browser check was **not** run — eight sibling agents were
      sharing the developer's Chrome, and nothing in this diff imports React or DOM or is
      rendered by any component. See Verification.

## Verification (2026-08-09)

Throwaway `node` harness (deleted; the engine chain is pure CommonJS so it runs without
babel), against an event-free state — stadium + `phase: 'regular'` present so the real
`ticketing` contributor is under test, but `nextGameAtClock` pushed out of reach and no
powerups or camps pending, so nothing random fires and both runs are comparable:

- **Regression, exact:** `totalIncomePerSecond(state, m).cash === revenuePerSecond(state, m)`
  → `12 === 12`, strict equality.
- **Offline parity, cash:** `advance(s, 3600)` = 43,200 vs 3,600 × `advance(s, 1)` = 43,200;
  `advance(s, 28800)` = 345,600 vs 28,800 × `advance(s, 1)` = 345,600. Relative error 0.
- **Real offline path:** `applyOfflineProgress` with `lastSaveTimestamp = now - 28,800,000`
  reported `elapsedSeconds: 28800`, `revenueEarned: 345,600` — identical to 28,800 live
  one-second ticks. 28,800 seconds in one pass is itself the proof the path is not
  event-driven; under a per-second event the 2,000-iteration cap would have capped it.
- **Wallet parity, caps:** with `collectors` temporarily stubbed to 0.4/s, one 28,800s step
  credited 11,520.0 caps vs 11,519.999999993905 over 28,800 one-second steps (rel. err
  5.3e-13 — float accumulation only), and caps accrued while `phase === 'offseason'` with
  cash correctly suspended at 0.
- **Offseason gate:** `totalIncomePerSecond(offseasonState, m)` → `{caps:0,coins:0,cash:0}`.
  Checked by direct call, since `advance()` flips an offseason back to `regular` within the
  same iteration.
- **No stadium / no season:** returns a zeroed bundle without throwing.
- `npx webpack --mode production` and `npx webpack serve --mode development` both compile
  clean and the dev server serves `bundle.js` (HTTP 200).

## Scaffolding owned by other stories

- `state.wallet = { caps: 0, coins: 0, cash: 0 }` added to `createInitialState()` in its own
  commit (`04117b0`) — **STORY-001 owns this field.** `state.cash` deliberately remains
  canonical for cash (`offlineProgress.js` diffs `next.cash`, `resetForPrestige()` resets it),
  so `wallet.cash` stays 0 until STORY-001 unifies them. `creditIncome()` defaults a missing
  wallet, so pre-existing saves (save `version` unchanged at 1) keep loading.
- `isUnlocked(state, feature)` in `income.js` infers unlocks from state presence, with a TODO
  to become `getUnlockedFeatures(state.progression.act).includes(feature)` when **STORY-004**
  lands `engine/progression.js`. It is deliberately one function, so that merge is a
  single-body swap. `engine/progression.js` is **not** required from `income.js` — webpack
  fails the build on an unresolved request even inside a `try/catch`.
- `state.income` is read defensively and was **not** added to `initialState.js`.

## Still blocking Act I — not this story

`totalIncomePerSecond()` is safe with `stadium: null` / `season: null`, but **`advance()`
itself is not yet**: `findNextEventClock()` reads `working.season.phase` unguarded, as do
three branches in the loop body. The `season: null` guard is Decision 2's ("one guard at the
top of the phase-handling block") and belongs to the sibling story that owns it — it was
deliberately not touched here to keep the `tickEngine.js` diff surgical.

`components/ticketing/RevenueTicker.js` still calls `revenuePerSecond()` directly for its
display, so it shows a nonzero rate during an offseason even though nothing is credited.
That is pre-existing behavior, unchanged by this story; a wallet-aware ticker belongs with
the UI work.

## Notes

- **Depends on STORY-001** (wallet). The per-currency bundle this story returns has nowhere to
  be credited until `state.wallet` exists. Branch from STORY-001.
- Also touches `engine/tickEngine.js`, so coordinate with STORY-002 — if both are in flight,
  land STORY-002 first or expect to rebase.
- `conventions.md`: **single simulation entry point.** `engine/tickEngine.js: advance()` is
  called identically by the live 1s tick and by `engine/offlineProgress.js`. Do not add a second
  timer or a separate offline income path — anything not folded into `advance()` will silently
  fail to apply during catch-up.
- `conventions.md`: `src/engine/` is pure and must not import React or DOM APIs.
- `conventions.md`: immutable spread updates only.
- `conventions.md` / `package.json`: **no test framework, linter, or CI exists** — only `start`
  and `build`. Verify by running the app and by diff review; the offline-parity check can be
  done with a temporary manual harness or by manipulating `meta.lastSaveTimestamp` in a saved
  game. Adding a test framework is out of scope per PRD §10.
- `key-files.md`: `engine/tickEngine.js` is the largest and most load-bearing source file
  (245 lines) — keep the diff surgical.
- PRD §3.1 is the specification for this story, including the contributor table and the
  rationale for a source list over act-branching.
