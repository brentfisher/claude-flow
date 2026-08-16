---
id: STORY-028
title: Add launch commit, transit, arrivals and the overshoot decision
status: in-progress
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: story/STORY-028-launch-transit
worktree_path: /Users/brent/idle-base-worktrees/STORY-028
base_branch: master
pr_url: null
is_architectural: true
approach_summary: >
  New pure `engine/launch.js` in the house contract shape, owning commit, transit resolution, arrival and the overshoot band. Reads every threshold from `departingThreshold` in `data/actSevenSitesConfig.js` rather than restating it (the derivation exists so the number cannot drift), calls the exported `sites.markSiteReached()` on arrival rather than writing site records itself, and appends a transit wake boundary to `tickEngine`'s contributor list beside `nextBuildClock`. Also discharges STORY-027's deferred minutes-of-income measurement, which only becomes possible here because this is the first branch on which the site ladder can be played. Touches `engine/launch.js` (new), `engine/tickEngine.js`, the measurement block in `data/actSevenSitesConfig.js`, and the `launches` slice.
created: 2026-08-13
updated: 2026-08-16
---

# Add launch commit, transit, arrivals and the overshoot decision

A launch is the act's punctuation: a Fuel threshold is met, the player commits, and a burn runs over
a window. The window is the point — it is the act's one honest invitation to close the tab.

**A committed launch always arrives and never loses the Fuel.** A random outcome resolved inside
`advance()` is resolved during offline catch-up in front of nobody; a player who commits a
40,000-Fuel burn, closes the tab and returns to "the burn was short" has been dealt a loss they
could not see, influence or audit. Risk lives at commit time instead, and is deterministic.

## Acceptance Criteria

- [ ] New `engine/launch.js` (pure) and `data/actSevenLaunchConfig.js`.
- [ ] Shop contract: `listOffers(state)`, `purchase(state, offerId)` (commits the burn),
      `resolveArrivals(state)`, `nextArrivalClock(state)` registered on STORY-017's list.
- [ ] Fuel is debited via `colony.js: spendResource` — **`engine/wallet.js` is not the debit path**,
      since Fuel lives in `expedition.resources`.
- [ ] An in-flight launch is a record in `expedition.launches` with `resolved: false` and an
      `arrivesAtClock`; the log and in-flight state are one list.
- [ ] `resolveArrivals` is **idempotent by construction** — a second pass finds nothing unresolved.
      An 8-hour return crossing several arrivals resolves them in clock order, and re-running
      `advance()` over the same span changes nothing.
- [ ] **No rng anywhere in the launch path.** A launch cannot fail.
- [ ] Overshoot is a deterministic function of `fuelHeld / threshold`: committing dumps the whole
      tank, buying reduced transit and an arrival grant. No hidden state.
- [ ] One launch in flight at a time; "already in flight" is a single refusal check.
- [ ] Launch thresholds are **derived from measured Fuel rates** — hold the target fill minutes and
      recompute the threshold, per the PRD's stated contract.
- [ ] `npm run build` passes.

## Notes

- PRD §7.3 and §7.5.
- **Depends on STORY-027, STORY-018.**
- `conventions.md`: randomness enters an engine as a defaulted `rng` parameter so behaviour is
  reproducible headlessly. This story's decision is that the tick loop takes **no** rng at all.
- `openspec/.../design.md` **Decision 6**: no mechanic may reduce a currency below zero. Committing
  a launch spends a threshold the player provably holds.
