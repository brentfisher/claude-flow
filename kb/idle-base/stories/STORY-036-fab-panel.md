---
id: STORY-036
title: Build the Fab panel — the module shop, and the first place Act VII's Salvage can be spent
status: pr-opened
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: story/STORY-036-fab-panel
worktree_path: /Users/brent/idle-base-worktrees/STORY-036
base_branch: story/STORY-036-fab-panel
pr_url: https://github.com/brentfisher/idle-base/pull/37
is_architectural: true
approach_summary: >
  Replace `FabPanel`'s placeholder with the module shop, rendering `actSevenModules.listOffers()` verbatim. This is Act VII's first purchase surface, so it creates the act's first action module — `state/actions/fabActions.js` plus a new action type and a require in `gameReducer.js`. Renders the two gate kinds distinctly (the `requires` spend gate shows what is still needed; `requiresSiteCapability` fails closed and is absent) and storage grants without a `/s` suffix. The story that makes Act VII playable.
created: 2026-08-16
updated: 2026-08-17
---

# Build the Fab panel — the module shop, and the first place Act VII's Salvage can be spent

**This is the story that makes Act VII a game rather than a clicker with no sink.** Right now a
player entering Act VII can earn Salvage from the shell-level click and has literally nowhere to
spend it: `FabPanel` renders "This panel is not built yet."

Behind that placeholder sits the most heavily specified and most thoroughly measured system in the
act. `engine/actSevenModules.js` exports `listOffers(state)` and `purchase(state, offerId)` in the
house shop contract, with **cost, ownership and affordability already resolved** so the panel
renders rows verbatim and recomputes nothing. `data/actSevenModulesConfig.js` carries the full
ladder — producers, the Power↔Provisions↔Oxygen interlock, nine storage rows — and two measurement
blocks recording what it actually pays.

The scope is the shop and only the shop. Two gate kinds already exist in the engine and must be
rendered faithfully rather than flattened: `requires` (a **spend** gate — quantities of other
modules) and `requiresSiteCapability` (a **colonization** gate). They fail differently on purpose,
and the difference is a design decision this panel must not erase.

## Acceptance Criteria

**The shop**

- [x] `components/expedition/FabPanel.js` renders real content and no longer returns
      `<PlaceholderPanel />`.
- [x] Rows come from `actSevenModules.listOffers(state)` and are rendered **verbatim** — the panel
      recomputes no cost, no affordability and no ownership.
- [x] Purchase dispatches through a `state/actions/` module reaching
      `actSevenModules.purchase(state, offerId)`; the component calls no engine mutator directly.
- [x] An unaffordable row is visibly unaffordable but still shown; an **unavailable** row is
      **omitted entirely**, matching every other shop in this game ("the reveal is the reward").
- [x] Owned counts render for repeatable rows.
- [x] A refused purchase (engine returns null) is a **no-op** — no error surface, no thrown
      exception.

**The two gates, kept distinct**

- [x] A row withheld by the **spend** gate (`requires`) communicates what is still needed, since it
      is a target the player can work toward.
- [x] A row withheld by the **colonization** gate (`requiresSiteCapability`) fails **closed** and is
      simply absent until a qualifying site is colonized — do not preview it. Revealing Solar Wing
      and Ice Harvester early would offer the cheapest Power in the act from minute one and delete
      the `lunar` phase's central beat.

**Storage rows read as storage**

- [x] A storage row renders its grant **without** a `/s` suffix — "+250 max power", never
      "+250 power/s". Storage grants capacity and never a rate; this exact wording is called out in
      the module-ladder change's tasks.
- [x] The first Fuel Bladder is legible as what it is: Fuel's base capacity is 0, so what it buys is
      **Fuel existing at all**, not 400 units of headroom.

**Behaviour under real states**

- [x] With zero Salvage and nothing owned, the panel renders the tier-1 rows as unaffordable rather
      than empty.
- [x] Renders without throwing against a save with **no `expedition` key**.
- [x] Buying a module the same tick it becomes affordable does not double-apply — verify against the
      engine, which owns the debit.

**Verification**

- [x] `npm run build` passes.
- [x] Drive `listOffers()` / `purchase()` under `node` across `aftermath` and `lifeSupport` states —
      including one where the spend gate is unmet and one where it is met — and confirm the panel
      renders exactly the rows the engine returns.
- [x] Any new CSS goes **inside STORY-034's `body.expedition` section**, above the mobile media
      query.

## Notes

- **PRD §6.4** (the `fab` row: "Fabrication shop — generators, scrubbers, farms, tanks. The Salvage
  sink."), **§5.3** (the affordability budget) and **§5.4** (the module ladder).
- **Depends on STORY-034** for the palette and the CSS section, and on the shared shop-row treatment
  it defines. STORY-035 (Ops) is independent of this story — they can run in parallel.
- `engine/actSevenModules.js` is the **reference implementation of the house shop contract**, and
  `engine/sites.js:153-157` describes emitting rows "exactly as engine/actSevenModules.js emits
  them." A panel written against this contract should generalize to the Sites panel (STORY-037);
  coordinate the shared row markup through STORY-034's primitives rather than duplicating it.
- `openspec/changes/act-seven-full-module-ladder/` (merged, PR #27) is the change that owns this
  ladder. Its **"The two site-gated rows fail closed, unlike the phase gate"** decision is the one
  this story **preserves** — an unrecognized *phase* is corruption one tick from self-repair, so
  revealing everything is safe there, but a missing *site* is the accurate statement that nothing
  has been colonized. Do not render the two site-gated rows before their site exists.
- Its **"Capacity is derived, never stored"** decision is likewise **preserved**: render
  `colonyCapacity()`'s value, never a stored ceiling.
- `openspec/changes/act-seven-aftermath-economy/` (merged, PR #25) owns the tier-1 rows and the
  Salvage faucet this panel spends.
- `conventions.md`: components are render-only; player-facing prose lives in `src/data/`. Module
  names and descriptions are already authored in `data/actSevenModulesConfig.js` — read them, do not
  restate them in JSX.
- **Naming caveat, do not fix here.** `reactor`, `hydroponicsBay` and `solarWing` violate
  `data/actSevenNamingConfig.js`'s prohibition (no Act VII name may be a word the sport does not
  already own). It is a known open item deferred since Phase 3 and is **out of scope** — surfacing
  those names in the UI does not make renaming this story's job.

## Implementation note

- **The engine gained one export.** `listOffers()` filters `requires`-gated rows out entirely, so
  the spend-gate AC ("communicates what is still needed") was unreachable without either
  recomputing ownership in the component — the exact bug `conventions.md` names — or an engine
  addition. `engine/actSevenModules.js` now also exports **`listGoals(state)`**: the rows the spend
  gate is holding, each prerequisite resolved into the required module's own label and progress
  toward it. A separate list rather than a flag on `listOffers()`, because `listOffers()` means
  "rows that can be acted on" and the tuning record's greedy-buyer harness drives straight off it.
  The two lists are asserted disjoint on every fixture; goal rows carry no `affordable` field and
  no button.
- `data/actSevenModulesConfig.js` gained one field, `firstNote`, on `fuelBladder` only — the
  sentence that makes the first Bladder legible as "Fuel existing at all". Authored in `data/`
  beside the zero it explains; the engine decides whether it applies (`count === 0`).
- New files: `data/actSevenFabConfig.js` (copy only), `state/actions/fabActions.js`.
  `BUY_MODULE` added to `actionTypes.js` and wired in `gameReducer.js`.
- Verified under `node`: 60 engine assertions and 43 render assertions through `react-dom/server`.
  Recorded in full in the VERIFIED block at the foot of `components/expedition/FabPanel.js`.
