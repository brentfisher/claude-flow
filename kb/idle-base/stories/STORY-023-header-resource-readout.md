---
id: STORY-023
title: Rework HeaderStats for a frozen league and add the resource readout
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

# Rework HeaderStats for a frozen league and add the resource readout

In Act VII the record, the season chip and the era pill are meaningless — the league is frozen. And
four consumables with capacity ceilings need a readout a currency chip cannot give: amount against
capacity, the sign of the net rate, and a warning before a resource bottoms out.

Header space is already contested on a 390px screen, so this is a swap, not an addition.

## Acceptance Criteria

- [ ] Season/record, reputation, capacity and champions chips are suppressed when
      `resolveRules(state).seasonFrozen` is set.
- [ ] The era pill's slot is reused for a phase pill.
- [ ] New `ResourceChips` renders amount/capacity, the net-rate sign, and a warning state, fed by a
      `listResources(state)` in the shop-contract idiom.
- [ ] **`listResources` is a thin presentation wrapper over `colonyRates(state, modifiers)`** and
      performs no second solve. The header must never compute a rate the engine did not hand it —
      divergence means the header lies about when a resource bottoms out.
- [ ] Salvage appears as an ordinary currency chip via `data/currencies.js`, with no hardcoded
      currency name in the component.
- [ ] Contrast ratios for all new colour pairs are **computed and recorded**, not asserted — chips
      render at ~0.78rem on a phone, which is normal-size text for contrast purposes.
- [ ] Readable at 390px wide without horizontal scroll.
- [ ] `npm run build` passes.

## Notes

- PRD §6.6 and ledger **R5** (one solve, one boundary helper).
- **Depends on STORY-018** (`colonyRates`) and **STORY-019** (`seasonFrozen`).
- `key-files.md`: `HeaderStats.js` has 8 changes and "space here is contested on a 390px screen."
- `data/eras.js`'s pill comment is the house standard for reasoning about colour and contrast —
  every authored bg/ink pair there clears 4.7:1 and says why.
- `conventions.md`: components decide nothing about rules, costs, odds or availability.
