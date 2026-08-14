---
id: STORY-021
title: Add the Act VII config and swap the tab shell using hides
status: pr-opened
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: story/STORY-021-act-seven-shell
worktree_path: /Users/brent/idle-base-worktrees/STORY-021
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/21
is_architectural: true
approach_summary: null
created: 2026-08-13
updated: 2026-08-14
---

# Add the Act VII config and swap the tab shell using hides

This is where the UI teardown actually happens as *config*: Act VII declares what it unlocks, what
it hides, and that the season is frozen. `AppShell` renders a different set of panels without any
structural change to how it routes.

## Acceptance Criteria

- [ ] `data/acts.js` gains Act VII with `id: 6`, `rules: { seasonFrozen: true, ... }` (click keys
      per PRD §5.2), `unlocks`, `hides`, and `exit: null`. `FINAL_ACT_INDEX` becomes 6.
- [ ] `hides` lists **only tab ids**, and does **not** include `hustle` — the manual click exists in
      every act and is never removed (hard project invariant).
- [ ] Six new `PANELS` entries: `ops`, `fab`, `launch`, `sites`, `artifacts`, `contracts`, with
      matching `TabNav` registration. A `PANELS` miss silently renders `FieldView` and a `TabNav`
      miss silently renders nothing — confirm both are registered.
- [ ] Panels may ship as minimal placeholders; this story owns the **routing**, not their contents.
- [ ] Progressive intra-act reveal keys off a **phase-rank comparison against `expedition.phase`**,
      not new milestones — `engine/sites.js` is the single writer of that field and a second source
      of truth is a race that only shows up on a real save.
- [ ] Entering Act VII leaves `season`, `league`, `roster` and `stadium` intact and the league
      frozen; the player cannot reach any baseball tab.
- [ ] `progression.seenTabs` is **not** cleared.
- [ ] `npm run build` passes.

## Notes

- PRD §6.3, §6.5, and ledger **R4** (phase as the single progression signal).
- **Depends on STORY-015** (`hides`), **STORY-019** (`seasonFrozen`), **STORY-014**.
- `conventions.md`: "Feature ids in an act's `unlocks` array must equal the `PANELS` key in
  `AppShell.js` when they gate a whole tab."
- `openspec/.../design.md` **Decision 6**: the manual click action is never removed or disabled.
  This is why `hustle` must survive the teardown.
- `module-map.md`: "`AppShell`'s `PANELS` keys must match feature ids in `acts.js` `unlocks`."
