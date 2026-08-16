---
id: STORY-036
title: Build the Fab panel — the module shop, and the first place Act VII's Salvage can be spent
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: null
worktree_path: null
base_branch: null
pr_url: null
is_architectural: null
approach_summary: null
created: 2026-08-16
updated: 2026-08-16
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

- [ ] `components/expedition/FabPanel.js` renders real content and no longer returns
      `<PlaceholderPanel />`.
- [ ] Rows come from `actSevenModules.listOffers(state)` and are rendered **verbatim** — the panel
      recomputes no cost, no affordability and no ownership.
- [ ] Purchase dispatches through a `state/actions/` module reaching
      `actSevenModules.purchase(state, offerId)`; the component calls no engine mutator directly.
- [ ] An unaffordable row is visibly unaffordable but still shown; an **unavailable** row is
      **omitted entirely**, matching every other shop in this game ("the reveal is the reward").
- [ ] Owned counts render for repeatable rows.
- [ ] A refused purchase (engine returns null) is a **no-op** — no error surface, no thrown
      exception.

**The two gates, kept distinct**

- [ ] A row withheld by the **spend** gate (`requires`) communicates what is still needed, since it
      is a target the player can work toward.
- [ ] A row withheld by the **colonization** gate (`requiresSiteCapability`) fails **closed** and is
      simply absent until a qualifying site is colonized — do not preview it. Revealing Solar Wing
      and Ice Harvester early would offer the cheapest Power in the act from minute one and delete
      the `lunar` phase's central beat.

**Storage rows read as storage**

- [ ] A storage row renders its grant **without** a `/s` suffix — "+250 max power", never
      "+250 power/s". Storage grants capacity and never a rate; this exact wording is called out in
      the module-ladder change's tasks.
- [ ] The first Fuel Bladder is legible as what it is: Fuel's base capacity is 0, so what it buys is
      **Fuel existing at all**, not 400 units of headroom.

**Behaviour under real states**

- [ ] With zero Salvage and nothing owned, the panel renders the tier-1 rows as unaffordable rather
      than empty.
- [ ] Renders without throwing against a save with **no `expedition` key**.
- [ ] Buying a module the same tick it becomes affordable does not double-apply — verify against the
      engine, which owns the debit.

**Verification**

- [ ] `npm run build` passes.
- [ ] Drive `listOffers()` / `purchase()` under `node` across `aftermath` and `lifeSupport` states —
      including one where the spend gate is unmet and one where it is met — and confirm the panel
      renders exactly the rows the engine returns.
- [ ] Any new CSS goes **inside STORY-034's `body.expedition` section**, above the mobile media
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
