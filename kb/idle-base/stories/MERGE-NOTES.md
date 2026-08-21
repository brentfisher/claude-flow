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


---

# Merge notes — Phase 2 (four parallel branches, 2026-08-14)

STORY-020 (#23), STORY-022 (#24), STORY-024 (#25) and STORY-023 (#26) all branched from
`master` @ `ea38953`. Conflicts were measured with `git merge-tree`, not guessed:

| pair | conflicts | files |
|---|---|---|
| 020 vs 022 | 2 | `AppShell.js`, `data/storyBeats.js` |
| 022 vs 023 | 1 | `styles/global.css` |
| every other pair | **0** | — |

**Recommended order: #23 -> #26 -> #25 (any order among those three) -> #24 last.**

Every conflict involves STORY-022 (#24), so merging it last means resolving all three in one
rebase instead of spreading them across the queue.

## The three conflicts, and how to resolve each

**1. `data/storyBeats.js` — 020 and 022 both append an Act VII section.**
Both anchored on the same end-of-array text. **Take both**, as two separate labelled sections:
`// --- Act VII: the call-up ---` (the `act-7-offer` beat) and
`// --- Act VII: the teardown ---` (the `act-7-teardown` beat). Neither supersedes the other;
they are different beats with different `kind` values. Dropping either silently removes a
feature — the offer would have no prose, or the teardown would render nothing.

**2. `AppShell.js` — adjacent edits, not competing ones.**
020 changes `{showVictory && (` to `{showVictory && !confirmingCallUp && (` and adds the
call-up modals; 022 inserts `<TeardownOverlay />` plus its comment on the lines just above.
They also touch neighbouring lines in the require block. **Take both**; there is no semantic
overlap. Check afterwards that `<TeardownOverlay />` still appears in BOTH render branches —
the pre-season shell and the full shell — because AppShell early-returns and an overlay
mounted only in the full shell is missing for a whole class of saves.

**3. `styles/global.css` — 022 and 023 both add a feature section.**
Both are placed immediately above the file's trailing `@media (max-width: 640px)` block.
**Take both, and keep them above that block.** `global.css` ends inside the mobile media
query, so any rule that lands after it is silently scoped to `max-width: 640px`. Resolving
this one by appending to the end of the file would produce a build that passes, a diff that
looks right, and a teardown overlay plus a set of resource chips that are unstyled on desktop.

## No semantic hazards

Unlike Phase 1, no two branches implement the same primitive:

- **024 did not change `colonyRates`'s signature or return shape.** It adds a `salvage` key
  *additively*, so 023's `listResources` wrapper — built against the pre-024 shape — merges
  clean and stays correct. This was the one silent-divergence risk in the batch and it did
  not materialise.
- 020 owns Act VI's `exit` in `acts.js`; 024 owns Act VII's `rules`. Separate hunks.
- 023 owns `HeaderStats.js`; nothing else touches it.
- 024 owns `income.js`, `clicker.js` and `actSevenConfig.js`; nothing else touches them.

## Follow-up owed after all four land

- `act-7-offer` and `act-7-teardown` prose is **serviceable, not final**. STORY-033 owns the
  Act VII narrative and should rewrite the wording; the beat ids and object shapes are meant
  to survive that.
- **STORY-025 must re-measure the Salvage bands.** #25's tuning comment measures a
  deliberately partial ladder (no storage rungs, no scrubbers bought) and runs ~27% hot at
  the `aftermath` exit. Ledger R8 says later stories recompute against the measurement — this
  measurement has a known, stated bias.


---

# Merge notes — Phase 3 (stacked branches, 2026-08-15)

Four PRs open, and **two of them are stacked on other PRs rather than on `master`.** That is the
thing to get right; the rest is ordinary.

```
master
 ├── #24  STORY-022  teardown overlay        (on master, MERGEABLE)
 │    └── #29  STORY-033  narrative          (stacked on #24 — rewrites the act-7-teardown beat #24 adds)
 └── #27  STORY-025  full module ladder      (on master)
      └── #28  STORY-026  generation powerups (stacked on #27 — registers the keys 025's ladder makes meaningful)
```

**Merge order: #24 → #29 → #27 → #28.**

A stacked PR's diff includes its base's commits, so #29 and #28 will look larger than they are
until their base lands. After the base merges, GitHub usually retargets the child automatically; if
it does not, rebase the child onto `master` and force-push.

**Do not rebase a stacked branch onto `master` before its base merges** — it drops the base story's
work, and in #28's case that is silent: the powerups would still build, register their keys, and do
nothing, because the ladder that makes them meaningful would be gone.

## Why each stack exists

- **#29 on #24** — STORY-033 rewrites `act-7-teardown`, a beat that only exists on #24. Off
  `master` there would be nothing to rewrite and the narrative story would have to invent the beat,
  which is how two versions of one beat end up in the file.
- **#28 on #27** — STORY-026 registers `OUTPUT_MULTIPLIER_KEYS` in `BONUS_KEYS`. Those keys are
  read by the tier-2 modules STORY-025 adds; on `master` alone the powerups would be measurable
  against an empty ladder, which is exactly the unmeasured-balance-change the house rules forbid.

## Still building

STORY-027 (sites, stacked on #27) and STORY-029 (puzzles, on `master`) are with agents. **027's
branch depends on #27 for the same reason #28 does** — it populates the `slice.sites` term that
`colonyCapacity()` currently sums over an empty list.

## Follow-ups this phase created

- **A naming-convention violation, flagged not fixed.** `data/actSevenNamingConfig.js` (#29)
  publishes §10.5's one prohibition: no Act VII name may be a word the sport does not already own.
  `reactor`, `hydroponicsBay` and `solarWing` in `actSevenModulesConfig.js` fail it. Left alone
  because those rows are load-bearing in three open PRs; worth a renaming pass once the stack
  lands.
- **STORY-029 must re-measure the phase bands.** #27's tuning block records `lifeSupport` earning
  2.6x its §5.3 budget under an optimal buyer. §8's hint ladder is the act's elastic sink (ledger
  R6) and is where that surplus is supposed to go, so its pricing is the first thing to check
  against the measurement rather than against §5.3's table.


---

# Merge notes — Phase 4 (2026-08-16)

Two PRs, **both on `master`, neither stacked**, and `git merge-tree` measures **zero conflicts**
for each against current `master` and against each other. This is the easy phase; the thing to get
right is not the merge, it is what STORY-028 inherits.

```
master
 ├── #30  STORY-027  site ladder, pads, phase writer   (on master, clean)
 └── #31  STORY-029  artifact puzzles, hints, shop     (on master, clean)
```

**Merge order does not matter.** They touch disjoint files: 027 owns `engine/sites.js`,
`data/actSevenSitesConfig.js` and the site half of `engine/colony.js`; 029 owns `engine/puzzles.js`
and `data/actSevenPuzzlesConfig.js`. Both add a contributor to `engine/tickEngine.js`'s list, but at
different call sites, and the merge is textual either way.

Note 027 was cut on `story/STORY-025-module-ladder`. #27 merged first, so 025's commits are already
reachable from `master` — `master..HEAD` is exactly 027's own commits, and no rebase was needed. The
Phase 3 warning about rebasing stacked branches early does not apply here; it was already satisfied.

## What was finished during pickup, not by the original agents

Both branches were left mid-bookkeeping. The code was complete on each; the paperwork was not.

**STORY-027 shipped an empty `MEASURED` block.** The config header stakes a load-bearing empirical
claim — "R2's cost ladder, re-derived against the measurement" — and pointed at a block reading
"Filled in by the simulation run" that contained nothing. That is worse than no block: it is a
citation to evidence that does not exist.

It has been replaced with what is actually verifiable on that branch, plus a stated deferral. See
below for why the deferral is the correct answer rather than an excuse.

**STORY-027's OpenSpec change directory was a bare scaffold** — a README and a schema line, no
proposal, design, specs or tasks, while every other Act VII story carries all four. Written and
committed separately from the measurement commit.

## THE ONE THING STORY-028 MUST NOT MISS

**027's cost ladder is unmeasured, and it cannot be measured until 028 exists.**

Every purchase `data/actSevenSitesConfig.js` prices — all four colonize costs, all four pad tiers —
happens in `lunar` or later. A site is reached only by a launch. `engine/launch.js` is STORY-028. So
on 027's branch `listOffers()` correctly returns **zero rows for the whole of `aftermath` and
`lifeSupport`**, which is every phase that branch can reach. Verified, not assumed.

A minutes-of-income run there would have to synthesise the arrival times it was trying to price
against, which is inventing the input and reporting it as a result. So it was not done, and the
config says so in place of promising numbers.

**028 is the first branch on which this ladder can be played at all, so 028 owes the measurement**
(ledger R8). The costs currently stand on §7.5's minutes-of-income *intent* recomputed against
STORY-025's measurement (`lifeSupport` earning 2.6x its §5.3 budget) — a re-derivation, not a
simulation. Check the four colonize costs (3.3 / 6.0 / 8.0 / 6.0 min) and the four pad tiers
(5 / 8 / 10 / 12 min) against what the economy actually pays once transits land.

Hold the Warning Track's inversion through any retune: **6.0 minutes to establish against a 6.0
`upkeepFactor` to sustain**. §7.5 asks explicitly that cheap-to-establish/ruinous-to-sustain survive
retuning, and it currently does.

## What 027 verified, so 028 need not re-derive it

- **Ledger R1's tank floor holds at all five sites** — `1.6 x departingThreshold`, derived rather
  than authored: 1,200→1,920, 4,200→6,720, 13,500→21,600, 21,000→33,600, 42,000→67,200. **028 must
  read its thresholds from `departingThreshold` rather than restating them** — two copies is exactly
  the drift the derivation forecloses.
- **One pad tier per rung**, no gaps. The top pad reaches rung 5, past the end of the ladder, which
  is §7.1's "beyond the wall is not a site" — 028's transit code needs to handle a reach with no
  destination record.
- **Home Plate's Fuel grant is withheld until a tank is owned.** 0 capacity at act start, 2,320 on
  the first 400-unit Bladder (its 400 plus Home Plate's 1,920 together). This is R1's pacing control:
  ungate it and L1's threshold is crossed roughly a third of a phase early, stealing that time from
  `lunar`.
- `markSiteReached()` is **exported for 028** and is the single writer of `reached`. Use it rather
  than writing site records from `engine/launch.js`, so records keep one author.
- `deepSpace` turns on launch **commit**, not arrival, and reads the launch **log** — a record with
  `resolved: false` is a burn under way. The predicate turns on the record *existing*, which is what
  keeps it monotone across resolution. It runs against an empty list today; 028 is what fills it.

## 029's obligation, discharged

Phase 3 left STORY-029 owing a re-measurement of the phase bands against 025's surplus. It did that,
and it discharged ledger R9 by measurement rather than assertion — 30 runs, seeded rng, mashing
`attemptBruteForce()` against a synthetic clock rather than computing wall time arithmetically.

Shipped counts measure **1.096 median / 1.104 worst** against R9's 1.3 ceiling, and **1.199 / 1.215**
on an adversarial upper bound that counts every graded-phase bypass minute as fully blocking.

Worth knowing before anyone reconciles against §8.7's table: **the first attempt is free**, so wall
times are (n−1) cooldowns, not n. §8.7 quotes n × cooldown, making every row there ~one cooldown
pessimistic. That is a difference in the table, not a drift in the code.

## Still outstanding

The naming-convention violation flagged in Phase 3 is **still open** — `reactor`, `hydroponicsBay`
and `solarWing` in `actSevenModulesConfig.js` fail `data/actSevenNamingConfig.js`'s prohibition. It
was left alone in Phase 3 because those rows were load-bearing in three open PRs. Two of those have
merged; the rename is worth doing once #30 and #31 land.

Everything 027 adds passes that rule — Home Plate, the On-Deck Circle, the bases, the Warning Track,
and the Sandlot / Mound / Long Toss / Cutoff / Swing pads are all terms the sport already owns.

---

## Queued follow-ups — approved 2026-08-20, to run AFTER the panel wave

Both were gated on work that has now merged, and both were deliberately kept out of the
037/038 wave because they touch files those agents are editing. Serialize them behind it.

1. **The naming-convention rename.** `reactor`, `hydroponicsBay` and `solarWing` in
   `data/actSevenModulesConfig.js` violate `data/actSevenNamingConfig.js`'s prohibition. The
   "Still outstanding" section above gated this on "#30 and #31 land" — **both have merged**, so
   the gate is discharged and the rename is live work. It touches merged module config that the
   Fab panel (#37) now renders, so re-check the panel after renaming.

2. **Re-measure D-5's dead-air interval.** STORY-031 carried forward a worst interval of
   **3.32 min against a ~2 min target**, diagnosed to §5's 1.14 growth exponent on a uniformly-
   levelled portfolio rather than to anything §7 authors. Per §7.6's remedy ("a cheaper Salvage
   sink, never a smaller threshold") nothing was retuned, and the note said the fix belongs to
   the §6/§8/§9 content stories and D-5 should be re-measured once they land. **029, 030 and 031
   have all merged**, so that obligation is now live.

   Anything that lengthens a fill must also re-run §12's five-hour ceiling: STORY-032 measured
   the act won at **291.8 min = 4.86h against a 5.00h ceiling — a 2.7% margin**, and that buyer
   is a limit rather than a person, so a real player already exceeds five hours.

---

## #39 vs #40 (STORY-037 Sites, STORY-038 Artifacts) — MEASURED, not predicted

Both branched from `master` @ `0cba1d2`. A real test merge was run on 2026-08-20 and the resolution
below was **built and verified**, not reasoned about. Three files are touched by both:

| File | Result |
|---|---|
| `data/actSevenPanels.js` | **auto-merges.** Different `blurb` rows, line-local. |
| `state/gameReducer.js` | conflicts; **blind take-both is correct and builds.** |
| `styles/global.css` | conflicts; **blind take-both BREAKS THE BUILD.** See below. |

### `global.css` — do not resolve this line-by-line

Both stories insert a section header comment at the same anchor, so **the `=======` marker lands
in the middle of a rule.** Deleting the three marker lines and keeping both sides splices 037's
`.v7-site-status` body into 038's header comment and yields:

```
SyntaxError (3520:1) Unclosed block
```

That one failed loudly. The same class of splice landing between two complete rules would produce
*valid CSS with a mangled selector* and no error at all — which is the silent version of this
hazard, and the reason this note exists.

**Resolve by taking each section as a WHOLE UNIT, in story order, both above the final media query.**
Reconstruct rather than hand-edit: `master`'s final `@media (max-width: 640px)` is at line **3421**;
037 contributes the **208** lines above it from its branch, 038 contributes **477**. Merged file is
`master[:3421] + block037 + block038 + master[3421:]` = **4,134 lines with the media query at 4,106**
and both panels' rules above it. 208 + 477 matches both branches' diff stats exactly, which is the
check that the reconstruction dropped nothing.

Verified after resolving: `npm run build` compiles with 3 warnings (the pre-existing bundle-size
ones) and 0 errors; `.v7-site` and `.v7-artifact` rules both sit above 4,106.

### `gameReducer.js`

Two independent hunks — the `require` line and the `case` arms. Take both sides of both. Verify
`BUY_SITE_BUILD` and all five `puzzleActions.*` arms survive; a missing arm fails at first dispatch,
not at build.

> **Merge order note:** whichever lands second owns this resolution. The measurements above are
> against `master` @ `0cba1d2`; if anything else touches `global.css` first, re-derive the line
> numbers rather than trusting these.

### An inconsistency the wave introduced — worth a decision

037 registered its action in `state/actionTypes.js` (house convention, all 18 sibling modules).
038 declared its five ids as constants **on `puzzleActions.js` itself**, with an argued comment
(dispatcher and reducer import from one file, so they cannot drift). Both are defensible; having
**both in one codebase is not**. This came from the kickoff prompt asking agents to keep action
types in their own module to minimise conflict — the instruction was wrong, not the agents.
Normalising to `actionTypes.js` is the smaller change and matches everything else.
