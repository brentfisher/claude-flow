---
id: STORY-030
title: Add the contract board and the fuel side quests
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

# Add the contract board and the fuel side quests

Small bounded objectives that pay fixed Fuel lumps toward the next launch threshold. They exist to
give the player something to *do* during phases that would otherwise be watching a bar fill, and to
give the designer a lever to shorten a phase for an engaged player without shortening it for
everyone.

Twelve contracts across five kinds, so the board is not one side quest with twelve names.

## Acceptance Criteria

- [ ] New `engine/contracts.js` (pure) and its config + prose in `data/`.
- [ ] Shop-contract shape: offers with progress/claimability resolved, plus `accept`, `claim`,
      `abandon`, `refreshBoard`, `advanceContracts`, `contractUpkeepPerSecond`, and
      `nextContractEventClock` registered on STORY-017's list.
- [ ] Board randomness is **seeded from state**, not a bare `Math.random()`; `rng` enters as a
      defaulted parameter.
- [ ] **Only unaccepted offers expire.** An accepted contract never expires; a lapse returns as a
      makeup offer at the same payout. Nothing is ever debited or lost.
- [ ] **`claim()` returns `null` when the payout would exceed `fuel.capacity`** rather than silently
      destroying the overflow. Claiming is a player action, never an auto-credit.
- [ ] `contractUpkeepPerSecond(state)` is summed into the consumer side **before**
      `nextColonyThresholdClock` solves — otherwise an expedition contract can push a resource
      through zero inside a step.
- [ ] Payouts resolve as a percentage of **the threshold of the launch currently being filled**
      (5% / 7.5% / 11%), never a hardcoded absolute, and total no more than 40% of any threshold.
- [ ] Sustain/window progress resolves correctly across an 8-hour offline `advance()`.
- [ ] `npm run build` passes.

## Notes

- PRD §9 and ledger **R3** (per-launch resolution) and **R5** (upkeep ordering).
- **Depends on STORY-028** (thresholds), **STORY-018**, **STORY-017**.
- `conventions.md`: engines take `rng` as a defaulted parameter — `engine/wallBall.js` and
  `engine/bookie.js` are the templates.
- `key-files.md`: `engine/bookie.js` widened two shared contracts when it added props; watch for the
  same pattern here.
