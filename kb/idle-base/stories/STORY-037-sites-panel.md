---
id: STORY-037
title: Build the Sites panel — the colony ladder, its upkeep, and what a pad costs to keep
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: null
worktree_path: null
base_branch: null
pr_url: null
is_architectural: true
approach_summary: >
  Replace `SitesPanel`'s placeholder, rendering the ladder from `sites.listSites()` and purchasable rows from `sites.listOffers()` — kept as two sources, since `engine/sites.js` documents that computing either from the other loses information. Leads every row with upkeep, because §7.2's design is that expanding is a decision rather than a purchase. Adds `state/actions/sitesActions.js`, an action type and reducer wiring. Must read honestly in today's pre-STORY-028 state, where no site is reachable and the offer list is correctly empty.
created: 2026-08-16
updated: 2026-08-16
---

# Build the Sites panel — the colony ladder, its upkeep, and what a pad costs to keep

The `sites` tab answers *where am I?*, against `launch`'s *can I go?* — §6.4 splits them for that
reason and defends the split as a tab-budget decision. `SitesPanel` renders a placeholder today.

`engine/sites.js` (STORY-027, merged as PR #30) already exports exactly what this panel needs, and
one of its exports exists **only** for this story: `listSites(state)` is documented in the source as
"Every site, resolved, in ladder order — for §6's Sites panel," and is deliberately distinct from
`listOffers()`. The comment states why, and it is the design constraint of this story:

> this is "where am I", including sites with a build already running and sites finished with, while
> `listOffers()` is "what can I buy right now". **A panel needs both and computing either from the
> other loses information the player is looking at.**

So the panel renders the ladder from `listSites()` and the purchasable rows from `listOffers()`. It
must not derive one from the other.

The single most important thing this panel communicates is **upkeep**. §7.2's design is that
expanding must be a **decision** and not a purchase, and what makes it one is the permanent draw on
the shared pool. The engine already leads its effect strings with the upkeep for exactly this
reason — the Warning Track is deliberately cheap to establish (6.0 minutes of income) and ruinous
to sustain (a 6.0 `upkeepFactor`), and a player who cannot see that before buying has not been given
the decision the section is built around.

**Note the ladder is inert until STORY-028 lands.** A site is reached only by a launch, so until
`engine/launch.js` exists `listOffers()` correctly returns zero rows and only Home Plate is
colonized. That is not a bug and this story must not "fix" it — build the panel so it reads
honestly in that state, and so it comes alive unchanged when launches arrive.

## Acceptance Criteria

**The ladder**

- [ ] `components/expedition/SitesPanel.js` renders real content and no longer returns
      `<PlaceholderPanel />`.
- [ ] The ladder renders from `sites.listSites(state)` in rung order, showing every site's `name`,
      `where`, `rung`, and its `reached` / `colonized` / `launchPadTier` state.
- [ ] An unreached site is legible as a **destination**, not as an error or an empty row.
- [ ] A site with a build in progress shows its `buildingId` and `readyAtClock` as a pending build —
      "one build per site at a time" is a rule the player should be able to see.
- [ ] `reachesRung` renders for a site with a pad, sourced from `siteReach()` and never recomputed
      from the tier in the component.

**Upkeep, which is the point**

- [ ] Each colonized site shows its **upkeep**, with pad upkeep scaled by that site's
      `upkeepFactor` — read from the engine's resolved values, never multiplied in the component.
- [ ] Home Plate's site production (a flat 2.0 O2/s, the only free atmosphere in the game) renders
      as production and is visibly distinct from upkeep.
- [ ] A purchasable row leads with its upkeep before what it unlocks, matching the effect strings
      `engine/sites.js` already assembles.

**The shop half**

- [ ] Purchasable rows come from `sites.listOffers(state)` and render verbatim — the panel resolves
      no cost and no affordability.
- [ ] Purchase dispatches through a `state/actions/` module reaching `sites.purchase(state, offerId)`;
      a refused purchase is a no-op.
- [ ] Exactly one pad tier is offered per rung; the panel does not invent a tier list of its own.

**The pre-STORY-028 state, which is today**

- [ ] With no launches possible, the panel renders Home Plate colonized, the four sites above it
      unreached, and **no purchasable rows**, without reading as broken.
- [ ] Renders without throwing against a save with **no `expedition` key**, and against a
      pre-Act-VII save where `resolvedSites()` returns `[]`.

**Verification**

- [ ] `npm run build` passes.
- [ ] Drive under `node` against three states: fresh Act VII (only Home Plate), a state where
      `markSiteReached(state, 'onDeck')` has been applied (colonize offer appears), and one with a
      pad built (reach becomes 2). Confirm the panel's rows against the engine's return values.
- [ ] Any new CSS goes **inside STORY-034's `body.expedition` section**, above the mobile media
      query.

## Notes

- **PRD §6.4** (the `sites` row), **§7.1** (the ladder), **§7.2** (pads, tiers, upkeep, reach) and
  **§7.4** (one resource pool, not per-site — the panel must not imply per-site stocks).
- **Depends on STORY-034** for the palette and CSS section. Independent of STORY-035 and STORY-036 —
  all three can run in parallel behind 034.
- **Not blocked by STORY-028, but inert without it.** Build for both states; do not stub launches.
- `openspec/changes/act-seven-site-ladder/design.md` is the change this story renders, and three of
  its decisions are ones this story **preserves**:
  - **Decision 1** — the record stores six fields and everything else is resolved from config on
    read. The panel must read resolved values and denormalize nothing.
  - **Decision 9** — the shop row leads with the upkeep. That ordering is a design decision, not a
    formatting choice; keep it.
  - The **reach-from-pad-tier-alone** invariant (proposal, "the sharpest rule in §7.2"): reach must
    never appear to depend on satisfaction. A starved network launches later, never shorter — do not
    render reach as conditional on resources.
- `engine/sites.js:90-93` is the authority on the `listSites()` / `listOffers()` split; read that
  comment before designing the layout.
- `conventions.md`: render-only components, prose in `src/data/`. Site names, `where` strings and
  descriptions are authored in `data/actSevenSitesConfig.js` — render them, do not restate them.
- Every name on this ladder passes `data/actSevenNamingConfig.js` (Home Plate, the On-Deck Circle,
  the bases, the Warning Track, and the Sandlot / Mound / Long Toss / Cutoff / Swing pads), so the
  open naming violation elsewhere does not touch this panel.
