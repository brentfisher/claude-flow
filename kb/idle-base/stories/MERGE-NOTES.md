# Merge notes — Phase 1 (nine parallel branches)

All nine stories branched from `master` @ `7981c96` concurrently, so several implement the same
shared primitives independently. Agents were instructed to match canonical shapes exactly and
isolate scaffolding into separate commits, so conflicts should be **textual, not semantic** —
but several resolve *silently wrong* if you take one side wholesale. Read this before merging.

**Recommended order: 001 → 002 → 004 → 003 → 005 → 006 → 007 → 008 → 009.**
(004 before 003 because 003's income refactor supersedes a line 004 edits — see hazard 2.)

## Authoritative owner per shared artifact

Everything else is scaffolding: take the owner's version, delete the duplicate.

| Artifact | Owner | Also created (scaffolding) by |
|---|---|---|
| `state.wallet`, `CURRENT_VERSION` bump | STORY-001 | 003 (`04117b0`), 005 (`2cbe745`) |
| `resolveRules()` | STORY-002 | — |
| `engine/income.js` | STORY-003 | 008, 009 |
| `data/acts.js`, `engine/progression.js`, `state.progression` | STORY-004 | 005 (`2cbe745`), 008, 009 |
| `state.feed` | STORY-006 | — |
| `state.clicker`, `data/storyBeats.js` | STORY-008 | 009 |
| `engine/wallBall.js` | STORY-009 | — |

## Silent-failure hazards

These do not produce a conflict marker you can eyeball — a wrong resolution compiles and runs.

### 1. `state/initialState.js` — 001 vs 004 (CRITICAL)
STORY-001 migrates `cash` → `wallet`. STORY-004 makes `stadium`/`league`/`season` null and
`roster`/`powerups`/`runStats` present-and-empty. **Taking either side wholesale silently
restores the other's removed behaviour with no error anywhere** — take 001's and you get the
eager 12-team league back, killing the entire progression premise. Both changes must survive.
Flagged independently by the STORY-004 agent.

### 2. `engine/tickEngine.js` revenue line — 003 supersedes 004
- STORY-004 (line ~224): `if (working.stadium && working.season && ...phase !== 'offseason')` wrapping `revenuePerSecond()`
- STORY-003 (line ~242): replaced that whole block with `creditIncome(working, totalIncomePerSecond(...), step)`

**Keep STORY-003's version.** Its `ticketing` contributor already returns 0 when
`stadium == null` / `season == null` / offseason, so 004's guard is redundant. Keeping 004's
line instead compiles fine and silently means caps and coins never accrue — Act I would have
no income at all.

### 3. Save version literal exists in TWO places
`persistence/saveLoad.js: CURRENT_VERSION` **and** `state/initialState.js: meta.version`.
Bumping only the first makes every fresh game write a save that `loadGame()` immediately
discards — **progress wipes on every reload**. Found independently by the STORY-001 and
STORY-005 agents; both bumped both. Verify the merged result has `2` in both places.
Post-merge cleanup: dedupe into one exported constant (deliberately deferred to avoid a
conflict in a file three branches were editing).

### 4. `data/acts.js` unlock content
STORY-004 authored the real six acts. STORY-005's stub is explicitly filler with arbitrary
unlock ordering. **Replace 005's wholesale with 004's** — do not merge them.

### 5. Act 0 renders an empty screen until 008 lands
STORY-004 unlocks `field` at Act III, so at Act 0 STORY-005's filtered `PANELS` is empty and
the `PANELS[activeTab] || FieldView` fallback renders an empty Home Field. This is correct
per-story behaviour but broken in combination. Needs STORY-008's `lot` panel plus a STORY-005
fallback to a *derived* unlocked tab. **Expect a blank first screen between merging 004/005 and
merging 008 — that is this, not a regression.**

### 6. `data/acts.js` must not require `engine/*`
STORY-002 resolves the act layer through an expression-built require (`../data/${...}`), which
pulls every `src/data` file into `modifiers.js`'s dependency graph. If `acts.js` ever requires
`engine/progression.js` (which requires `modifiers.js`), that closes a cycle.
**Verified clean:** STORY-004's `acts.js` has no requires at all. Keep it that way.

### 7. `state.feed` does NOT bump the save version — by design
STORY-006 persists the feed (whole state is serialised, so it costs no code; a full 50-entry
buffer measures ~5.7 KB, bounded by the cap). It deliberately left `CURRENT_VERSION` alone —
STORY-001 owns that — and instead guards with `state.feed || []` in `engine/feed.js` and
`EventFeed.js`, verified against a real pre-existing v1 save. **Keep those guards** even after
001's bump lands; they cost nothing and they are what let 006 merge in any order.

Storage order is oldest-first; the component reverses for display, so the trim always drops the
oldest entry.

## Verification caveat — cross-agent browser contamination

The STORY-006 agent disclosed that, before realising ports 8080/8104 belonged to STORY-004's
dev server, it wrote a stale `lastSaveTimestamp` into `localStorage` on those origins,
fast-forwarding ~45 minutes of game time there. No source files, git state or branches were
affected.

STORY-004's reported browser observations (fresh Act-0 game, 579-byte save, header correctly
omitting the Capacity and Season chips) are *inconsistent* with a fast-forwarded save, so its
verification most likely stands. But if anything on that branch looks unexpectedly advanced —
e.g. a "fresh" game showing Season 11 and $203K cash — that is the contamination, not a bug on
the branch. **Re-verify STORY-004's fresh-game behaviour after merge rather than trusting the
in-flight browser run.**

## Untested seams

- **002 × 004**: STORY-002's act-rules layer has only ever run against a *missing* `data/acts.js`
  (its absent-file degradation path). It has never been exercised with a real acts file. Acts
  III–V's `rules` are authored but inert until both land. Verify pacing overrides actually apply
  — and that they survive an offseason transition, which is the bug 002 exists to fix.
- **004's exit predicates are stubs.** `EXIT_PREDICATES` / `ACT_INITIALIZERS` are near-empty
  registration points; 004 proved the transition cascade using injected clock thresholds.
  STORY-008/009 must register the real predicates or no act ever exits.
- **001**: `executeTradeAction` / `TradeDeadlinePanel` never exercised (needs a mid-season state
  the agent couldn't reach). Same two-line pattern as four verified purchases, but untested.

## Bonus fixes riding along in STORY-002

Two pre-existing shipped bugs, found outside its brief and verified against `master`:
- `economy.js:34` read `balanceConfig.statUpgradeCostGrowth` directly, so the **Analytics era's
  `statUpgradeCostGrowth: 1.15` override had never applied** — the era's whole premise.
- `tradeDeadline.js:17` hardcoded `retireAtSeasonsRange`, so traded players ignored the shorter
  careers eras 3–4 declare while drafted rookies honored them.

Plus a latent softlock: a non-power-of-2 `playoffTeams` (now authorable) strands the season in
the playoffs phase forever — confirmed by simulation at `playoffTeams: 6`. 002 clamps the field
down to a power of 2 and to the league size. Act authors should still choose powers of 2
deliberately rather than lean on the clamp.
