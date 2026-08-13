---
id: STORY-009
title: Build Act II — Off the Wall (wall-ball subgame, bounded wagers, the first crew)
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-incremental-odyssey.md
branch: story/009-act-two-rebuild
worktree_path: /Users/brent/idle-base-worktrees/STORY-009
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/10
is_architectural: true
approach_summary: >-
  Add `engine/wallBall.js` resolving challenges as a staked strength check that reuses
  `gameSim.js: winProbability()` rather than introducing a second probability model, with three
  risk approaches (Safe/Normal/Showboat). Add crew recruitment via
  `playerFactory.js: createPlayer()` with a simplified-player option, plus a Respect counter
  that converts to `state.reputation` at the Act III boundary. Adds `components/wallBall/` and
  touches `state/actionTypes.js` and the action modules. Must enforce the bounded-loss
  invariant — 25% stake cap, no balance below zero, Hustle never removed — which PRD §6.4
  designates a hard project invariant to be recorded in conventions once implemented. Depends
  on STORY-008.
created: 2026-08-09
updated: 2026-08-10
---

# Build Act II — Off the Wall (wall-ball subgame, bounded wagers, the first crew)

A brick wall, a chalk strike zone, and every kid on the block wanting a piece of you. Act II is
the only fully new subgame in the odyssey — Acts III–VI are the existing season simulation at
four different scales — so it carries the job of proving the game is more than a clicker.

It introduces the first real risk mechanic (wagering caps on a rally) and the first
roster-shaped mechanic (recruiting a crew), three acts before the full `RosterPanel` appears.

## Acceptance Criteria

**Wall Ball subgame**
- [x] New `src/engine/wallBall.js` resolves a challenge as a **strength check, not a twitch
      mini-game**: the player stakes caps, picks an approach, and the outcome resolves.
- [x] It reuses `engine/gameSim.js: winProbability()` with kit quality as the player's strength
      rather than implementing a second probability model.
- [x] Three approaches with increasing variance and payout: **Safe / Normal / Showboat**.
      Showboat is roughly a 35% loss rate at ~3x payout — a genuinely bad decision when taken
      greedily at a low balance.
- [x] New `src/components/wallBall/` renders the challenge, the stake selector, and the result.

**Bounded risk (PRD §6.4 — hard invariant)**
- [x] A single stake is capped at **25% of current caps**.
- [x] A loss can never reduce caps below the cost of one Hustle click, and no mechanic may take
      a currency below zero.
- [x] The Hustle (click) action from Act I remains available throughout Act II — this is the
      mechanical anti-softlock guarantee, not a nicety.
- [x] Any sequence of maximally bad wagers leaves the game recoverable in bounded time.

**Crew and Respect**
- [x] Winning challenges attracts crew members — stripped-down players created via
      `engine/playerFactory.js: createPlayer()` with a simplified-player option (name, one
      position, one visible stat), rather than a parallel entity type.
- [x] **Respect** accrues from wins, is displayed, and converts to `state.reputation` at the Act
      III boundary.
- [x] A small `wallBallDues` caps trickle feeds the income contributor scaffolded in STORY-003.

**Exit**
- [x] Act II's exit predicate is **5 wall-ball wins AND 3 crew members**, after which the player
      transitions to Act III.
- [x] **Pacing check:** the act runs roughly 8–12 minutes, with crew recruitment landing near
      the identified flat point (~6–8 rally attempts).

## Notes

- **Depends on STORY-008** (Act I must exist and be completable), and transitively on
  STORY-001/003/004.
- `conventions.md`: `src/engine/` is pure and must not import React or DOM APIs — `wallBall.js`
  is engine, its panel is a component.
- `conventions.md`: reuse before invention. `gameSim.js` already implements Elo-style
  `winProbability(strengthA, strengthB)`; `playerFactory.js` already implements `createPlayer`
  with a `qualityMult` option. Extend these rather than writing parallel implementations.
- `conventions.md`: feature-scoped component directories; costs/odds/config in `src/data/`.
- `conventions.md`: action-type constants in `state/actionTypes.js`; pure
  `(state, action) => newState` handlers under `state/actions/`.
- `conventions.md` / `package.json`: **no test framework, linter, or CI exists** — only `start`
  and `build`. Verify by running the app and by diff review; the bounded-loss invariant should
  be exercised by deliberately losing repeatedly at a low balance. Adding a test framework is
  out of scope per PRD §10.
- Once the bounded-loss invariant is implemented, PRD §6.4 asks that it be recorded in
  `conventions.md` as a hard project invariant: no mechanic may reduce a currency below zero,
  and no mechanic may remove the Hustle action.
- PRD §5 (Act II) and §6.4 specify this story. PRD §11.3 flags Act II as the place to invest if
  playtesting shows it is the weakest act — if the resolved check reads as flat, this is the
  story to deepen rather than a later act.
