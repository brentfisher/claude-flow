---
id: STORY-015
title: Add a `hides` array to act config so an act can retire a tab
status: in-progress
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: story/STORY-015-act-hides
worktree_path: /Users/brent/idle-base-worktrees/STORY-015
base_branch: master
pr_url: null
is_architectural: true
approach_summary: >-
  Extend `getUnlockedFeatures()` in `engine/progression.js` to subtract an optional per-act
  `hides` array after building the existing unlocks union, keeping the result derived and never
  stored. Ships with no act declaring `hides`, so it is a provable no-op — verified by comparing
  output across act indices 0-5 under node. Touches `engine/progression.js` plus the `acts.js`
  header comment documenting the new key.
created: 2026-08-13
updated: 2026-08-13
---

# Add a `hides` array to act config so an act can retire a tab

`engine/progression.js:22 getUnlockedFeatures(actIndex)` builds the cumulative union of `unlocks`
across acts `0..actIndex`. It can only ever *add* feature ids. Act VII's premise — the game tears
down the baseball UI — is not expressible in the current config at all.

This story adds the primitive and nothing else. It lands with **no act declaring `hides`**, so it
is a provable no-op until Act VII uses it, which is exactly what makes it safe to ship early.

## Acceptance Criteria

- [ ] `getUnlockedFeatures(actIndex)` builds the `unlocks` union as today, then subtracts every id
      in the `hides` arrays of acts `0..actIndex`.
- [ ] `hides` is optional on an act; an act without it behaves exactly as today.
- [ ] Unlocks remain **derived on every read and never stored** — no new persisted field. Retuning
      which act hides which feature must take effect on an existing save with no migration.
- [ ] With no act declaring `hides`, `getUnlockedFeatures` returns identical output to the current
      implementation for every act index 0–5. Verify under `node` across all indices.
- [ ] A comment records why subtraction happens after the union rather than per-act, and that
      `hides` wins over a later `unlocks` of the same id.
- [ ] `npm run build` passes.

## Notes

- PRD §3.1 (Decision: acts gain a `hides` array) and §11.1 story 0.2.
- `openspec/.../design.md` **Decision 5** ("Unlocks are derived, not stored") is the property this
  story must not break. It is the reason `hides` is config rather than a stored flag.
- `conventions.md`: feature ids in an act's `unlocks` array must equal the `PANELS` key in
  `AppShell.js` when they gate a whole tab. The same is true of `hides`.
- `AppShell.js:60-70` already falls back to the first visible tab when the active one stops being
  unlocked, so no component change is required by this story.
