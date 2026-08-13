---
id: STORY-024
title: Add the Act VII click, Salvage income, and the aftermath tier-1 modules
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: null
worktree_path: null
base_branch: null
pr_url: null
is_architectural: null
approach_summary: null
created: 2026-08-13
updated: 2026-08-13
---

# Add the Act VII click, Salvage income, and the aftermath tier-1 modules

The first playable Act VII loop: a click that pays Salvage, a passive Salvage ladder that is itself
a Power and Provisions *consumer*, and the tier-1 modules that make the `aftermath` phase a real
economy rather than a bar.

Salvage is manufactured, not free — that is what stops the act degenerating into "buy drones, buy
everything."

## Acceptance Criteria

- [ ] Act VII's click keys (`clickCurrency: 'salvage'`, label, flat value, cooldown) live in
      `data/acts.js` `rules` and are read by `engine/clicker.js`, which already reads these keys off
      `act.rules` directly.
- [ ] New `data/actSevenModulesConfig.js` holds the tier-1 ladder with
      `cost(n) = baseCost × growth^n`, matching the `stadiumUpgradeCostGrowth` shape.
- [ ] Module purchase goes through a shop-contract engine: `listOffers(state)` returns
      presentation-ready rows with cost/ownership/affordability already resolved, and
      `purchase(state, id)` returns new state or `null` for refused.
- [ ] A `salvage` contributor is added to `engine/income.js`, gated on its own unlock.
- [ ] Every module declares its **own consumption**; the Salvage ladder draws Power and Provisions.
- [ ] **No magic numbers in the engine or components** — every rate, cost and growth exponent lives
      in `data/`.
- [ ] Measured under `node` and recorded in a tuning comment: seconds of pure clicking to the first
      automation (target 90–130s), and click share of Salvage income after minute 10 (target < 5%).
- [ ] The identified flat point for `aftermath` has a relieving unlock landing within ~5 minutes
      of it.
- [ ] `npm run build` passes.

## Notes

- PRD §5.2, §5.4 (tier-1 rows), §5.10, and ledger **R8** — §5.2's income table is authoritative and
  §7's and §8's numbers derive from it, so **publish the measured Salvage bands in a comment** in
  `actSevenModulesConfig.js`. Later stories recompute against the measurement, not the estimate.
- **Depends on STORY-016** (salvage + slice), **STORY-018** (colony rates), **STORY-021** (config).
- `conventions.md`: "A number inline in an engine or component is a bug. It belongs in a
  `*Config.js`." And: `data/` comments carry measured simulation results — that IS the design record.
- `engine/concessions.js` + `data/concessionsConfig.js` is named in `key-files.md` as "the most
  elaborate shop and the model to copy."
