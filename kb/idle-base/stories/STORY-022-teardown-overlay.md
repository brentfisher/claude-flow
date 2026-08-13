---
id: STORY-022
title: Add the teardown overlay that plays once when the act flips
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

# Add the teardown overlay that plays once when the act flips

The single most memorable moment in the game: the baseball UI tears itself apart. It must be short
(this is an idle game, not a cutscene simulator), skippable, and — the hard part — **idempotent
under an 8-hour offline catch-up that crosses the act boundary**.

The tear is **depicted, not performed**. Performing it would require keeping the old shell mounted
and stale, which the `hides` mechanism deliberately forecloses.

## Acceptance Criteria

- [ ] New `components/expedition/TeardownOverlay.js`, driven by CSS stages — **no JS timer, no
      second tick source**.
- [ ] Derived from the act transition via a `prev` ref, exactly as `ToastHost.js:27-32` derives
      toasts. `prev.current === null` is the baseline case and must play **nothing**.
- [ ] Reloading mid-sequence plays nothing and loses nothing. Returning after an 8-hour catch-up
      that crossed the boundary plays it **once**, not once per crossed trigger.
- [ ] Nothing about the sequence is persisted to state.
- [ ] Dismissible/skippable at any point; a repeat viewing is skippable in under a second.
- [ ] Honours `prefers-reduced-motion`.
- [ ] Styles go in a feature section of `styles/global.css` — **not** appended at EOF, which is
      inside an `@media (max-width: 640px)` block and would silently scope the rule to mobile.
- [ ] All copy comes from `data/` (beat id `act-7-teardown`), not the component.
- [ ] `npm run build` passes.

## Notes

- PRD §3.1 (last paragraph, idempotence) and §6.2; §12 criterion 3 is its acceptance test.
- `key-files.md`: `ToastHost.js` "documents why toasts are derived from transitions and never
  stored — an offline catch-up would otherwise fire a storm on load. Read it before adding a toast."
  That header is the model for this component.
- `key-files.md`: `global.css` is 2560 lines and "ends inside an `@media (max-width: 640px)` block".
- **Depends on STORY-021.**
