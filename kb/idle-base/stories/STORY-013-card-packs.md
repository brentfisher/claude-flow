---
id: STORY-013
title: Add card packs — the first randomness mechanic, with variance in quality and never in loss
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-incremental-odyssey.md
branch: null
worktree_path: null
base_branch: null
pr_url: null
is_architectural: null
approach_summary: null
created: 2026-08-10
updated: 2026-08-10
---

# Add card packs — the first randomness mechanic, with variance in quality and never in loss

Act III's identified flat point is the third repeated six-game season with no new lever, and card
packs are the unlock scheduled to land there (PRD §5, Act III). Coins buy a pack; a pack yields a
player. The pack is the game's first randomness mechanic and deliberately the gentlest of the
four: **a pack always yields a usable player — the variance is in quality, never in total loss.**
Wall-ball wagers, scouting and the Bookie escalate from here (PRD §6.4), so this one establishes
the pattern with no downside to teach.

It is also what makes Act III's exit reachable: a three-man promoted crew is not expected to
finish first in the standings, and packs are how the roster gets good enough to win the title.

## Acceptance Criteria

**The mechanic**

- [ ] New `src/engine/cardPacks.js` opens a pack and returns exactly one player, created via
      `engine/playerFactory.js: createPlayer(position, { qualityMult, ... })`. Reuse before
      invention — do not write a parallel player generator or a second stat model.
- [ ] A pack **always** yields a usable player. There is no dud outcome, no empty pack, no
      refund case, and no path where coins are spent and nothing is received.
- [ ] Variance is expressed entirely through `qualityMult` (and optionally position), drawn from
      a rarity table in a new `src/data/cardPacksConfig.js`. Costs, rarity weights and quality
      ranges are config, not inline in the engine or a component.
- [ ] Packs cost coins, are rejected when unaffordable, and can never take the balance below zero
      (`openspec/.../specs/currency/spec.md`, "Currency balances never go negative"; PRD §6.4).
- [ ] Pack randomness goes through the existing `src/utils/randomUtils.js` helpers rather than
      raw `Math.random()` scattered through the engine.
- [ ] An absent `state.cardPacks` is tolerated. STORY-010 adds the slice to
      `createInitialState()`, but that does not retrofit a save written before it — a player who
      reached Act III on 010/011/012 has a valid v2 save with no `cardPacks` key. Read it
      defensively rather than bumping the save version.

**Roster integration**

- [ ] A pulled player lands on `state.roster` immediately and is visible in `RosterPanel`.
- [ ] Whether the player arrives as a starter or on the bench is decided deliberately and
      documented: `teamStrength()` averages **starters only** (`engine/strength.js:13-19`), so a
      bench arrival changes nothing about the team until the player is promoted, and Act III has
      no lineup-management UI. Do not leave this to chance — a pull that visibly does nothing
      reads as a broken mechanic.
- [ ] Roster growth is bounded. Act III's roster starts at ~3 promoted crew; state a cap or an
      explicit "no cap in Act III" decision in the PR, and confirm the panels and `FieldView`
      still render as the roster grows past nine.
- [ ] Opening a pack writes a feed entry through `data/feedMessages.js` (a pull is exactly the
      kind of event PRD §7 wants narrated) — no inline strings in components.

**UI placement**

- [ ] The pack shop is a component under a new `components/cardPacks/` directory, rendered as a
      child of `RosterPanel` and gated on the `cardPacks` unlock, which Act III's `unlocks` array
      already declares (`data/acts.js:54`). It must **not** become a new `PANELS` key — adding a
      tab drags in `AppShell.js`, which STORY-011 owns, and `cardPacks` is a mechanic-level unlock
      inside an already-visible panel per the header comment in `data/acts.js`.
- [ ] The change to `RosterPanel.js` is a require plus a single gated render. Keep it to two
      lines; STORY-011 owns the rest of that file.
- [ ] The pull is legible — the player sees what they got, with enough of a reveal that the
      variance registers. Any prose lives in `data/storyBeats.js` or `data/feedMessages.js`, not
      in the component (PRD §6.3).
- [ ] New action type appended to the end of the relevant block in `state/actionTypes.js`, with a
      new `state/actions/cardPackActions.js` module wired into `gameReducer.js`. Append only; do
      not reorder existing entries — STORY-012 appends to the same two files.

**Pacing**

- [ ] Packs are priced so they become the interesting decision around the third Act III season
      (PRD §5's identified flat point), and so that a run of pulls plausibly lifts a three-man
      crew to a standings title within the act's 15–20 minute target. This is coupled to the crew
      quality STORY-010 sets — tune against it and say what you assumed in the PR. PRD §11.1
      flags all act durations as playtest-dependent.

**Non-regression**

- [ ] `advance()` is not modified. Packs are a player-initiated purchase resolved in a reducer
      action, not a tick event, so there is nothing for offline catch-up to replay and no
      `findNextEventClock()` entry to register.
- [ ] Players added by a pack behave like any other roster member through the existing systems —
      `playerOverall()`, `teamStrength()`, `updatePeakRating()` and eventually retirement — with
      no special-casing. `acquiredVia` is the existing field for provenance
      (`playerFactory.js:26,39`).

## Notes

- **Depends on STORY-010** (Act III, coins, a roster) and **STORY-011** (`RosterPanel` in its
  Act III form, and the coins-spending decision). Land it last in this batch — it is the only
  story that edits a file another Phase 2 story owns, and it edits it in two lines.
- **File ownership.** This story owns `engine/cardPacks.js` (new), `data/cardPacksConfig.js`
  (new), `components/cardPacks/` (new) and `state/actions/cardPackActions.js` (new), plus the
  two-line insertion in `RosterPanel.js`. It must **not** open `state/initialState.js`
  (STORY-010 pre-creates the `cardPacks` slice), `engine/tickEngine.js`, `engine/progression.js`,
  `engine/income.js` (STORY-012's), `data/acts.js` or `components/layout/AppShell.js`.
- PRD §6.4 orders the four randomness mechanics deliberately: **card packs (no downside, variance
  only)** → wall-ball wagers (small bounded loss) → scouting (bounded loss plus opportunity cost)
  → the Bookie (real, painful, bounded loss). This story is the first rung and must stay
  downside-free; adding a bust outcome here would collapse the escalation and duplicate Act V's
  scouting mechanic (PRD §5, Act V, "Scouting").
- design.md Decision 6: the anti-softlock guarantee is mechanical, not a balance target. No
  mechanic may reduce a currency below zero. PRD §6.4 asks that this be recorded in
  `conventions.md` as a hard project invariant once implemented — STORY-009 may have already done
  so; check before duplicating the note.
- `conventions.md`: reuse before invention — `createPlayer()` already takes a `qualityMult`
  option and is already used this way by `engine/retirement.js` for rookies and
  `engine/tradeDeadline.js` for trade candidates. `src/engine/` is pure, no React or DOM imports.
  Costs and odds belong in `src/data/`. Feature-scoped component directories. Immutable spread
  updates only. CommonJS, plain `function` declarations, single quotes, 2-space indent.
- **No test framework, linter or CI exists** — `package.json` has only `start` and `build`.
  Verification is by running the app plus diff review; the "always yields a usable player"
  guarantee is best checked by opening many packs in a throwaway `node` harness against the pure
  engine and asserting no null, no undefined stats and no negative balance. Adding a test
  framework is out of scope per PRD §10.
- PRD §5 (Act III, "Card packs"), §6.4 (risk without soft-lock) and §8 (Phase 2) specify this
  story.
