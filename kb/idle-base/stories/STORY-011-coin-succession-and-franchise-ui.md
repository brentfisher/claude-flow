---
id: STORY-011
title: Make coins the Act III currency and render the franchise UI at little-league scale
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

# Make coins the Act III currency and render the franchise UI at little-league scale

STORY-010 creates the season. This story makes the resulting screen correct: coins are the
currency the player earns and spends, the header shows coins rather than the cash the endgame
uses, `StandingsPanel` / `SeasonSchedulePanel` / `RosterPanel` read as a four-team little league
instead of a twelve-team pro franchise, and — critically — the Hustle button survives the
transition, because the moment a season exists `AppShell` stops rendering the lot entirely.

Every panel here already exists. The work is currency routing, absent-value handling for a
three-man roster, and copy that stops claiming there are playoffs when Act III declares
`playoffTeams: 0`.

## Acceptance Criteria

**Coins are the Act III currency**

- [ ] The header shows **coins** as the primary currency in Act III, with caps retired from the
      spendable display and cash not shown at all. Currently this is broken twice over:
      `HeaderStats.js:49-50` filters `CURRENCIES` by `unlocked.includes(c.id)`, but
      `getUnlockedFeatures()` returns *feature* ids (`'field'`, `'roster'`, `'concessions'`…) and
      never `'caps'` / `'coins'` / `'cash'` — so `unlockedCurrencies` is always empty and the code
      falls through to `held`. Combined with `wallet.cash` starting at `balanceConfig.startingCash`
      (`initialState.js:19`, `500`), **cash reads as the primary currency on Act III's first
      frame.**
- [ ] Settle the act→currency relationship in one place and document the choice: either acts
      declare their currency, or currency ids join the `unlocks` arrays, or `startingCash` is
      zeroed at init. Do not solve it three different ways across the components.
- [ ] `BUY_STAT_UPGRADE` spends **coins** in Act III. `rosterActions.js:18,24` reads and debits
      `state.wallet.cash` today. Route the cost to the act's currency rather than hardcoding a
      second branch per act.
- [ ] `UpgradeButton.js` displays the cost in the act's currency. It currently formats with
      `formatCash()` (a `$` prefix) and disables on `state.wallet.cash < cost` — both wrong in a
      coin act.
- [ ] `RosterPanel.js:13` says "Spend cash to upgrade individual stats." Copy follows the actual
      currency.
- [ ] Purchases are rejected rather than producing a negative balance
      (`openspec/.../specs/currency/spec.md`, "Currency balances never go negative").

**Hustle survives the act boundary (hard invariant)**

- [ ] The manual income action remains available and remains **payable** in Act III.
      `AppShell.js:72-79` renders `LotPanel` only when `!state.season`; past that point the shell
      renders `HeaderStats` / `TabNav` / `ActivePanel` / `EventFeed` and there is no click button
      anywhere in the tree. This breaks PRD §6.4, design.md Decision 6.1 ("the manual click action
      exists in every act and is never removed") and the currency spec's "A manual income action is
      always available" requirement, all at once.
- [ ] `components/lot/SearchLotButton.js` already exists as its own component, separate from
      `LotPanel` — render that rather than restructuring the lot. `LotPanel` also renders
      `LotShop`'s collector and starter-kit offers, and those must **not** reappear in Act III.
- [ ] The click pays in the act's currency, scaled to the act — PRD §5 Act I: "from Act II onward
      it is reframed as *Hustle* — a manual action whose absolute value scales with the act but
      whose relative value steadily declines." This is a `clickerActions.js` change, not just a
      placement change.
- [ ] Verify the anti-softlock guarantee holds in Act III: from a zero coin balance, Hustle alone
      returns the player to a playable balance in bounded time.

**The franchise panels at four-team scale**

- [ ] `StandingsPanel.js:22` hardcodes "Top {4} make the playoffs". In Act III `playoffTeams` is
      `0` and the champion is simply the standings leader — read the resolved value through
      `resolveRules()` / `modifiers.rules` and say something true, including the no-postseason
      case.
- [ ] The standings table renders 4 rows and the schedule 6 games without layout breakage or
      empty-state weirdness (`SeasonSchedulePanel.js` slices ±5 games around `scheduleIndex`,
      which is most of a 6-game season).
- [ ] `RosterPanel` renders a three-man roster without a broken "Bench" section — the promoted
      crew are all starters, so bench is empty.
- [ ] `FieldView` renders with six of the nine fielding positions unfilled. `PlayerIcon` receives
      `player={undefined}` for those (`FieldView.js:27-30`); `createStartingRoster()` has always
      filled every slot so this path has probably never executed. Verify it does not crash and
      reads as a deliberately sparse sandlot team.
- [ ] Team strength displays a real number, not `NaN` or `0.0`, for a three-starter roster.

**Tab reveal**

- [ ] Entering Act III reveals exactly the tabs Act III unlocks — `field`, `roster`, `league` —
      each carrying the NEW badge until visited, through the existing gate at
      `AppShell.js:44-47` and `TabNav.js:23-34`. `ticketing`, `playoffs`, `camp`, `trade` and
      `prestige` are **not rendered at all**, not greyed out (design.md Decision 5; the
      progression spec's "Locked content is absent, not merely hidden").
- [ ] `statUpgrades` and `concessions` / `cardPacks` are mechanic-level unlock ids, not tab ids —
      they gate features inside already-visible panels (see the header comment in `data/acts.js`).

## Notes

- **Depends on STORY-010.** There is no season, no coins and no roster to render until 010's
  initializer lands. Branch from 010, not from `master`.
- **File ownership.** This story owns `components/layout/AppShell.js`,
  `components/layout/HeaderStats.js`, `components/layout/TabNav.js`, `components/league/*`,
  `components/roster/*`, `components/field/FieldView.js`, `state/actions/rosterActions.js` and
  `state/actions/clickerActions.js`. It must **not** open `state/initialState.js`,
  `engine/tickEngine.js`, `engine/progression.js`, `data/acts.js` (STORY-010's) or
  `engine/income.js` (STORY-012's).
- **Overlap to expect:** STORY-010 deletes the crashing static Cash chip at
  `HeaderStats.js:121-124` so that its own work is verifiable at all. If you rebase and see it
  gone, that is 010, not a mistake. `FieldView.js` is also touched by STORY-012 (the concessions
  stand) — coordinate, or land whichever is ready first and rebase the other.
- `openspec/changes/odyssey-progression-architecture/specs/currency/spec.md`: currencies succeed
  one another; the retired currency stops being displayed as a spendable balance but stays
  readable in state; only currencies relevant to the current act are displayed, including not
  showing a not-yet-introduced currency at zero.
- `openspec/.../specs/game-feedback/spec.md`: every currency the player can earn shows its
  per-second rate beside its balance, and the rate updates immediately after a purchase that
  changes it. `HeaderStats` already does this via `totalIncomePerSecond()` — keep it working for
  coins.
- design.md Decision 5: unlocks are derived on read from the act index, never stored. Do not add
  a persisted unlock flag for anything here.
- `conventions.md`: feature-scoped component directories; components render, engines compute;
  action-type constants in `state/actionTypes.js`; one pure `(state, action) => newState` module
  per domain under `state/actions/`. CommonJS, plain `function` declarations, single quotes,
  2-space indent.
- **No test framework, linter or CI exists** — `package.json` has only `start` and `build`.
  Verification is by running the app plus diff review. Adding a test framework is out of scope
  per PRD §10.
- This story does not touch `advance()` or income, so no offline-parity check is required — but
  it must not introduce a second place where currency is credited. All accrual stays in
  `creditIncome()` (`engine/tickEngine.js:66-80`).
- PRD §4 (currency progression), §5 (Act III), §6.2 (progressive UI reveal) and §6.4
  (anti-softlock) specify this story.
