---
id: STORY-010
title: Enter Act III — the season initializer, the Act II→III boundary, and the little-league title
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

# Enter Act III — the season initializer, the Act II→III boundary, and the little-league title

This is the moment the existing franchise simulation switches on. Everything before Act III runs
with `state.season == null`; entering Act III is what first calls `generateSeasonSchedule()` and
creates `state.league` / `state.season`, at a scale the player can read at a glance — 4 teams,
6 games, 25 seconds per game, no playoffs at all.

Almost nothing new is simulated here. `engine/schedule.js` and `engine/standings.js` already do
the work; Act III's `rules` in `data/acts.js` are already authored
(`{ leagueTeamCount: 4, gamesPerSeason: 6, secondsPerGame: 25, playoffTeams: 0 }`) and
`resolveRules()` already routes them. What is missing is the initializer that builds the content,
the boundary conversion that carries Act II's crew and Respect into the real roster and
reputation, and an exit condition — because with no playoffs the engine currently has no notion
of *winning* anything.

This is the architectural story of Phase 2. It is the only story in this batch that opens
`engine/tickEngine.js`, `state/initialState.js`, `engine/progression.js` or `data/acts.js`, and
it pre-creates the state slices that STORY-012 and STORY-013 fill in. Land it alone, before the
others branch.

## Acceptance Criteria

**The Act III initializer**

- [ ] `ACT_INITIALIZERS` in `engine/progression.js` gains an entry for Act III (index `2`) that
      creates the franchise content: `state.league` via `createLeagueTeams()`, `state.season`
      via `generateSeasonSchedule()` / `resetStandings()` / `buildTradeWindows()`, with
      `phase: 'regular'`, `seasonNumber: 1`, `scheduleIndex: 0`, `playoffs: null`.
- [ ] **The initializer produces a `season` and `league` with exactly the field set
      `runOffseasonTransition()` builds** at `engine/tickEngine.js:314-334` — diff against that
      function, do not enumerate from memory. Every omission fails silently rather than throwing:
      a missing `gamesPerSeason` makes `scheduleIndex >= season.gamesPerSeason`
      (`tickEngine.js:182`) permanently false, so the season never ends, the offseason never runs,
      `finishPosition` is never recorded and **Act III never exits** — which a playtester reads as
      "pacing feels long", not as a missing field. A missing `tradeWindows` crashes
      `tickEngine.js:145`. `league` must be `{ teams: [...] }`, not the bare array
      `createLeagueTeams()` returns (`tickEngine.js:30,48`). `offseasonSummaryPending` must be
      falsy or `AppShell.js:128` raises the recap modal on the act's first frame.
- [ ] Every scale value comes from `resolveRules(state)`, never from `balanceConfig` directly —
      `leagueTeamCount`, `gamesPerSeason`, `secondsPerGame`, `tradeWindows`. The AI team count
      is `leagueTeamCount - 1` (the player is `PLAYER_TEAM_ID`, see `engine/schedule.js:26`).
- [ ] `season.secondsPerGame` and `season.nextGameAtClock` are set from the resolved
      `secondsPerGame`, matching how `runOffseasonTransition()` builds a season
      (`engine/tickEngine.js:326-327`).
- [ ] A player entering Act III sees a 4-team standings table, a 6-game schedule, and a game
      resolving roughly every 25 seconds — a full season in about 2.5 minutes.
- [ ] **`engine/schedule.js` and `engine/standings.js` are verified, not modified.** PRD §5 lists
      both under "Files touched", but the existing code already handles this scale:
      `generateSeasonSchedule()` with 3 opponents computes `round(6/3) = 2` games each for exactly
      6 slots (`schedule.js:34-47`), and `pickAiPairingsForSlot()` pairs the 2 remaining AI teams
      each slot. If a change genuinely is needed, say why in the PR — no other Phase 2 story owns
      these files.
- [ ] **The no-playoffs path already works — do not add a guard.** `playoffFieldSize(0, n)`
      returns `0` (`tickEngine.js:40-44`), so `top` is empty, the player is not in it, and the
      season rolls straight to `'offseason'` (`tickEngine.js:188-197`). That clamp landed with
      STORY-002 and is a decided behaviour, not a gap.
- [ ] **Pacing survives the offseason.** Play through a full Act III season into the next one and
      confirm the second season is still 6 games at 25s. This is the exact regression
      `resolveRules()` exists to prevent (design.md, Decision 3) and it has never been exercised
      against a real `data/acts.js` — MERGE-NOTES.md "Untested seams" flags the 002 × 004 seam.

**The Act II→III boundary**

- [ ] Respect earned in Act II converts to `state.reputation`. Read the merged Act II code for
      the actual field names — do not guess. STORY-009 is still in flight (see Notes).
- [ ] Act II's crew are promoted onto `state.roster` as real players via
      `engine/playerFactory.js: createPlayer()`, not by hand-building objects.
- [ ] Promoted crew are `isStarter: true`. `teamStrength()` filters on `isStarter` and returns
      `0` when no starters exist (`engine/strength.js:13-19`), which would feed a zero strength
      into `winProbability()`.
- [ ] Caps convert to coins at **10:1** (PRD §5 Act III) at the boundary. Caps are not deleted
      from `state.wallet` — the currency spec requires every currency the player has held to
      remain readable.
- [ ] Decide and document what happens to `income.collectors` at the boundary — see Notes; this
      is an open question the PRD does not answer, and the default (silently producing
      unspendable caps forever) is wrong.

**The title, and the exit out of Act III**

- [ ] `runOffseasonTransition()` records the player's **finishing position** in
      `season.lastOffseasonSummary`, computed from the pre-reset standings with
      `sortStandings()`. This must happen inside `runOffseasonTransition()` because
      `resolveGameSlot()` flips `phase` to `'offseason'` and the offseason branch fires in the
      *same* `advance()` iteration (`engine/tickEngine.js:186-197` then `386-388`), after which
      `resetStandings()` has erased the evidence.
- [ ] `finishPosition` is generic season machinery in `tickEngine.js`. The Act III-specific
      predicate `littleLeagueTitleWon` is registered in `EXIT_PREDICATES` in
      `engine/progression.js`, matching the convention documented at `progression.js:19-25`:
      `acts.js` names the condition, the engine owns evaluation.
- [ ] Finishing 1st in a 6-game season transitions the player to Act IV. Finishing lower rolls
      into another 6-game season and the act continues.
- [ ] **The title must not fire the Act VI payoff surfaces.** It must not increment
      `prestige.runStats.championships`, must not set `hasWonLeagueThisRun`, and must not raise
      AppShell's victory modal ("that's the win condition for the game!",
      `AppShell.js:110-126`) or the "🏆 Champions this run" header chip.
- [ ] An `act-3-intro` beat is added to `data/storyBeats.js` and shown on entry; feed messages for
      the season starting and the title being won go through `data/feedMessages.js`, not inline
      strings.

**Act III's rules (`data/acts.js`)**

- [ ] Act III declares `tradeWindows: []`. Without it, `buildTradeWindows(6, ...)` opens a window
      at game 3 and `resolveGameSlot()` calls `generateTradeCandidates()`
      (`tickEngine.js:149-157`), fabricating players that persist in the save with no UI to use
      them until Act IV. `[]` is safe through `.map()` and through AppShell's `.some()`.
- [ ] Act III declares a coin-scale `statUpgradeBaseCost`. `statUpgradeCost()` reads
      `modifiers.rules` (`engine/economy.js:35-36`) so the override applies; `balanceConfig`'s
      `150` is cash-scale, and Act III's coin range is ~500 to ~20,000 (PRD §5).

**State slices this story pre-creates (do not implement them here)**

- [ ] `createInitialState()` gains `income.concessions` (STORY-012's) and a `cardPacks` slice
      (STORY-013's), zeroed/empty. Those stories must never open `state/initialState.js` —
      MERGE-NOTES.md hazard #1 is exactly this file being edited by two branches and resolving
      silently wrong.

**Unblocking the franchise UI (a deletion, carried here so this story is verifiable)**

- [ ] Delete the static Cash chip at `components/layout/HeaderStats.js:121-124`. It calls
      `formatCash(...)`, which is **not imported** — line 7 destructures only
      `{ formatNumber, formatDuration }`. This is an unconditional `ReferenceError` in the JSX,
      and it has never executed because `AppShell.js:72` early-returns to `LotPanel` whenever
      `!state.season`. The first frame Act III creates a season, the app white-screens. The
      `shownCurrencies` loop at lines 106-119 already renders cash, so the chip is a duplicate as
      well as a crash. **Delete only — do not restructure HeaderStats; STORY-011 owns that file.**

**Offline parity (required — this story changes `advance()`)**

- [ ] Act transitions still fire during offline catch-up. `checkActTransition()` is called inside
      the `advance()` loop (`tickEngine.js:394`); confirm a player who leaves mid-Act-III and
      returns arrives having actually crossed the boundary, with the transition's feed entries
      present.
- [ ] **Iteration-budget check.** Once a season exists, `findNextEventClock()` is finite again and
      `advance()` returns to event-driven stepping. An 8-hour return at `secondsPerGame: 25` is
      ~28,800 / 25 ≈ **1,152 iterations** against `safetyCapIterations: 2000`. It fits, but Act
      III is the tightest pacing in the game — verify an 8-hour offline return is not truncated,
      and record the headroom in the PR. Tuning `secondsPerGame` below ~15s would silently start
      discarding offline time.
- [ ] A long offline return resolves many complete seasons (≈192 in 8 hours), so the Act III→IV
      transition firing during catch-up is a routine case, not a theoretical one. Verify it.

**Non-regression**

- [ ] Acts I and II are unchanged: a fresh game still opens on the lot with no season, no league
      and no tabs.
- [ ] After Act III exits, the game does not crash. Act IV has no initializer until Phase 3, so
      the player lands in Act IV with the 4-team league still in place. Verify no crash and no
      white screen; fixing the scale is Phase 3's job, explicitly out of scope here.

## Notes

- **Depends on STORY-009 (Act II), which is still in flight.** `story/009-act-two-rebuild` is at
  `af3c385` — no work is committed yet, so the shapes of `state.crew` and Respect are unknown.
  The contract this story needs is: a crew collection of `createPlayer()`-shaped objects, and a
  numeric Respect total. **Read the merged Act II source for the real field names rather than
  guessing** — a wrong guess compiles and silently promotes nothing.
- **Open question for the human — collectors at the boundary.** PRD §4 says the old currency
  converts at a documented rate and is retired from the header but never deleted from state. It
  says nothing about `income.collectors`, which keep producing caps forever. Leaving it as-is
  silently deletes the player's Act I/II income the moment coins become primary. Pick one:
  retire the collectors, convert their rate into a coin contributor, or keep paying caps and
  accept they are unspendable. Say which in the PR.
- **Open question for the human — Act III pacing.** A 6-game season is ~2.5 minutes but PRD §5
  targets 15–20 minutes for the act, with the flat point at "the 3rd repeated 6-game season" and
  card packs as the scheduled relief. That only works if a 3-man promoted crew usually *cannot*
  finish 1st against `randInt(35, 65)` AI teams (`engine/schedule.js:12`), and card packs are
  what make the title reachable. Crew quality (this story) and pack quality (STORY-013) must be
  tuned against each other. PRD §11.1 already flags act durations as playtest-dependent.
- design.md Decision 2: player-visible content (`stadium`, `league`, `season`, `playoffs`) is
  `null` until its act creates it; tick-loop collections (`roster`, `powerups`,
  `prestige.runStats`) are present-and-empty from t=0. Each act's story owns *creating* its own
  content fields — that is this story's core job.
- design.md Decision 3 and PRD §3.3: `balanceConfig ← act.rules ← era.rules`, resolved through
  `resolveRules()`. Never read an overridable `balanceConfig` field directly. Two more misses
  from the STORY-002 audit are still live at `state/actions/rosterActions.js:14,20`
  (`balanceConfig.statCap`, `balanceConfig.statUpgradeAmount`) — not needed for Act III, but
  worth knowing the audit was not exhaustive.
- design.md Decision 6 / PRD §6.4: no mechanic may reduce a currency below zero, and the manual
  income action can never be removed. The caps→coins conversion must not produce a negative or a
  NaN balance. (Keeping the Hustle button reachable in Act III is STORY-011's.)
- `conventions.md`: `src/engine/` is pure — no React or DOM imports. `src/data/` is config with
  no logic. Immutable spread updates only. CommonJS, plain `function` declarations, single
  quotes, 2-space indent.
- MERGE-NOTES.md hazard #6: `data/acts.js` must not `require()` anything from `engine/` —
  `modifiers.js` resolves it through an expression-built require and a cycle would close.
  `acts.js` currently has no requires at all. Keep it that way.
- `key-files.md`: `engine/tickEngine.js` is the largest and most load-bearing file in the repo,
  and the three files this story owns (`tickEngine.js`, `initialState.js`, and `HeaderStats.js`
  by way of `AppShell.js`) are exactly the ones the previous batch's parallel branches corrupted.
  Keep every diff surgical and say in the PR what you touched in each.
- **No test framework, linter or CI exists** in this repo — `package.json` has only `start` and
  `build`. Verification is by running the app plus diff review; the offline-parity and
  iteration-budget checks can be done with a throwaway `node` harness against the pure engine, or
  by editing `meta.lastSaveTimestamp` in a saved game. Adding a test framework is out of scope
  per PRD §10.
- PRD §5 (Act III), §3.2, §3.3 and §8 (Phase 2) specify this story.

## DECIDED — retired currencies stop generating (owner's call, 2026-08-10)

The open question was what happens to `income.collectors` (and `wallBallDues`) when caps stop
being spendable at the Act II→III boundary. **Resolved: retire the currency and stop generating
it.** If an income source produces a currency that is no longer spendable in the current act,
remove the source — do not leave it accruing a dead balance the player can see but never use.

- At the caps→coins boundary, convert the caps balance per PRD §4 and **deactivate the caps
  contributors** (`collectors`, `wallBallDues`) rather than letting them run forever.
- **Currency sharing across acts is explicitly fine.** Acts that share a currency need no
  retirement step between them — this rule applies only where a currency actually stops being
  spendable.
- The Hustle keeps paying, in whatever currency the current act uses (see STORY-011). Retiring
  caps must not retire the manual income action — that would break the hard invariant in
  `conventions.md`.

Apply the same rule at every later boundary where a currency is retired.
