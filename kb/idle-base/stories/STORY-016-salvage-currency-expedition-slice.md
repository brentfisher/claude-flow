---
id: STORY-016
title: Add the salvage currency and the expedition state slice with a defaulting accessor
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: null
pr_url: null
approach_summary: null
created: 2026-08-13
updated: 2026-08-13
---

# Add the salvage currency and the expedition state slice with a defaulting accessor

Act VII introduces a fourth currency (Salvage, monotonic, a header chip) and a new top-level state
slice holding four consumables with capacity ceilings. Every Act VII story reads this slice, so it
lands alone and first — which also proves the absent-slice defaulting against real saves before
anything depends on it.

`persistence/saveLoad.js` discards any save whose `meta.version` mismatches and there is **no
migration path**. This story deliberately does **not** bump `CURRENT_VERSION`: an in-flight save at
any act must load, default `expedition` to empty, and play on.

## Acceptance Criteria

- [ ] `data/currencies.js` gains `salvage` as a fourth entry, ordered per the file's cheapest-first
      convention.
- [ ] `state/initialState.js` gains `wallet.salvage: 0` and the `expedition` slice in the shape of
      PRD §4 (`phase`, `resources` with `{ amount, capacity }` per resource, `modules`, `sites`,
      `puzzles`, `contracts`, `launches`).
- [ ] An `expeditionSlice(state)` defaulting accessor exists, following the `concessionsSlice()` /
      `wallBallSlice()` pattern, and **tolerates the slice being entirely absent**.
- [ ] `CURRENT_VERSION` is **not** bumped.
- [ ] A save fixture written before this change loads without error and plays. Verify for a fixture
      from at least Acts I, III and VI.
- [ ] No component hardcodes a currency name — `HeaderStats` must render Salvage from the config
      list, not a literal (`currencies.js` header documents why).
- [ ] `npm run build` passes.

## Notes

- `key-files.md`: `src/persistence/saveLoad.js` "sets the hardest constraint in the repo: no save
  migration. A version mismatch discards the save, so every new slice must be readable when absent."
- `conventions.md` names the defaulting slice accessor as "the most important pattern in the repo"
  and gives the canonical example.
- `state/initialState.js` documents the null-vs-present-and-empty rule; `expedition`'s collections
  are dereferenced by `advance()` every iteration, so they are **present-and-empty**, not null.
- PRD §3.4 and §11.1 story 0.3.
