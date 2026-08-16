---
id: STORY-018
title: Add the colony consumption path and nextColonyThresholdClock
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: story/STORY-018-colony-consumption
worktree_path: /Users/brent/idle-base-worktrees/STORY-018
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/22
is_architectural: true
approach_summary: >-
  New pure `engine/colony.js` exporting `colonyRates`/`integrateColony`/
  `nextColonyThresholdClock`/`spendResource` plus the early phase predicates, clamping every
  resource to `[0, capacity]` and throttling dependents via a satisfaction factor rather than
  failing. Ships with zero modules defined so `advance()` is provably unchanged, then proves
  offline safety on a synthetic over-committed colony across an 8h delta. BLOCKED: needs STORY-016
  (the slice) and STORY-017 (the contributor list) merged first.
created: 2026-08-13
updated: 2026-08-14
---

# Add the colony consumption path and nextColonyThresholdClock

The entire income model is monotonic and additive: `totalIncomePerSecond()` returns a per-currency
bundle that is always ≥ 0, integrated over a step. Power, Oxygen and Provisions are **consumed**,
which breaks two assumptions at once:

1. `advance()` is the same code path for the live 1s tick and an 8-hour offline return. A colony
   with a negative net rate integrated across 8 hours in one step goes arbitrarily negative.
2. `findNextEventClock()` returns `Infinity` when nothing is pending, so `advance()` takes the whole
   remaining span as one step (`tickEngine.js:447`). A resource crossing zero or its cap *inside* a
   step means the rate applied to the rest of that step was wrong, and the error scales with how
   long the player was away.

**This story ships with zero modules defined**, so an empty colony produces nothing, consumes
nothing, `nextColonyThresholdClock` returns `Infinity`, and `advance()` behaves exactly as today.
That is what lets the offline-safety criteria be proven on a synthetic colony before any content
exists. This is the riskiest change in Act VII and the one with the least visible surface — a
rate-integration bug is invisible until a player returns after eight hours and quietly gets the
wrong numbers, which is the worst failure mode an idle game has because nobody reports it.

## Acceptance Criteria

- [ ] New `engine/colony.js`, pure, exporting: `colonyRates(state, modifiers)` returning
      `{ satisfaction, supplyThrottle, gross, demand, net, capacity }` (**one solve**);
      `integrateColony(state, modifiers, step)`; `nextColonyThresholdClock(state, modifiers)`;
      `spendResource(state, resourceId, amount)`; and the `aftermath` / `lifeSupport` phase
      predicates as pure functions.
- [ ] Every resource is clamped to `[0, capacity]` on every integration.
- [ ] A resource at zero **throttles** its dependents by a satisfaction factor
      (`available / required`, clamped `[0,1]`). **Nothing is destroyed, no module is removed, no
      colonist dies, and no currency goes below zero.**
- [ ] `nextColonyThresholdClock` is registered on STORY-017's contributor list (not an edit to
      `findNextEventClock`'s body) and returns the earliest clock at which any resource hits `0` or
      `capacity` at the current net rate, else `Infinity`.
- [ ] Rates are **linear in time within a step** — no compounding, no rate-depends-on-stock terms —
      so the boundary is a closed-form solve rather than a numerical search.
- [ ] `spendResource` is the only debit path into `expedition.resources`; nothing outside
      `colony.js` reaches into the slice.
- [ ] **Offline safety proof.** Drive `advance()` under `node` with a deliberately over-committed
      synthetic colony (net-negative on all three consumables) across an 8-hour delta and assert:
      no resource below 0 or above capacity, no module removed, no currency negative, and the run
      recoverable by adding one generator.
- [ ] **Iteration bound measured.** Record the worst-case iteration count for an 8-hour return in a
      comment, and confirm it against `balanceConfig.safetyCapIterations`. Silently hitting the cap
      under-credits the player with no error anywhere.
- [ ] With no modules owned, an 8-hour `advance()` produces state identical to before this change.
- [ ] `npm run build` passes.

## Notes

- PRD §3.3 (all three parts, plus the two-facts note beneath it) and §11.1 story 0.4.
- **Depends on STORY-017** (contributor list) and **STORY-016** (the `expedition` slice). This
  dependency is genuine and unavoidable.
- `openspec/.../design.md` **Decision 6** is a hard project invariant: no mechanic may reduce a
  currency below zero, and no mechanic may remove the manual income action. The throttle-don't-fail
  rule here is the same guarantee extended to consumables.
- `conventions.md`: engines are pure, take `rng` as a defaulted parameter, and are verified by
  driving them under `node`. There is no test runner — the `node` harness IS the acceptance check.
- PRD §12 criteria 4 and 5 are the measurable form of this story.
