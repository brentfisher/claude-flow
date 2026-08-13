---
id: STORY-005
title: Gate the tab bar on unlocked features with a NEW badge on first reveal
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-incremental-odyssey.md
branch: story/STORY-005-tab-reveal
worktree_path: /Users/brent/idle-base-worktrees/STORY-005
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/5
is_architectural: false
approach_summary: >-
  Filter `AppShell.js`'s static `PANELS` map through
  `getUnlockedFeatures(state.progression.act)` so locked tabs are not rendered at all — no
  greyed-out teasers, since the reveal is the reward. Add a NEW badge in `TabNav.js` driven by
  `progression.seenTabs`, cleared on first visit. Touches `components/layout/AppShell.js`,
  `components/layout/TabNav.js` and `state/actionTypes.js` for a mark-seen action.
  Presentation only — must not define which features unlock when; that stays in `data/acts.js`.
  Preserve the existing `PANELS[activeTab] || FieldView` fallback so a newly-locked active tab
  cannot render blank. Depends on STORY-004.
created: 2026-08-09
updated: 2026-08-10
---

# Gate the tab bar on unlocked features with a NEW badge on first reveal

`AppShell.js` currently declares a static `PANELS` map of eight tabs, all of which render from
the first frame. That is the most visible symptom of the problem this PRD exists to solve: a new
player is handed a franchise-management sim with eight tabs and no idea which one matters.

This story makes the tab bar a function of progression — tabs appear as their act unlocks them,
growing from one tab in Act I to eight in Act VI, with a NEW badge marking each reveal.

## Acceptance Criteria

- [ ] `AppShell.js`'s `PANELS` map is filtered by
      `getUnlockedFeatures(state.progression.act)` rather than rendering all eight tabs
      unconditionally.
- [ ] **Locked tabs are not rendered at all** — no greyed-out or teaser entries. The reveal is
      the reward, and a visible locked tab spoils it (PRD §6.2).
- [ ] `TabNav.js` shows a **NEW** badge on any unlocked tab whose id is not yet in
      `state.progression.seenTabs`.
- [ ] Visiting a tab adds it to `progression.seenTabs` and clears its badge; the badge does not
      return on reload.
- [ ] If the active tab somehow becomes locked (e.g. a prestige reset changing act state), the
      UI falls back to a valid unlocked tab instead of rendering blank. The existing
      `PANELS[activeTab] || FieldView` fallback is the pattern to preserve.
- [ ] At Act VI all eight existing tabs are present and the app behaves exactly as it does
      today.
- [ ] Running `npm start`: with `progression.act` manually set to each value 0–5, the tab bar
      shows the expected growing subset and every visible tab renders without error.

## Notes

- **Depends on STORY-004** for `getUnlockedFeatures` and the `progression` slice. This story is
  presentation only — it must not define which features unlock when; that lives in
  `data/acts.js`.
- `conventions.md`: components are the only layer that imports React and dispatches actions.
  Keep the unlock *query* in `engine/progression.js` and consume it here.
- `conventions.md`: component files are `PascalCase.js` matching their exported component name;
  `components/layout/` holds app chrome.
- `conventions.md`: action-type constants live in `state/actionTypes.js` and are never raw
  string literals at a dispatch site — marking a tab seen needs a new action type there.
- `conventions.md` / `package.json`: **no test framework, linter, or CI exists** — only `start`
  and `build`. Verify by running the app and by diff review. Adding a test framework is out of
  scope per PRD §10.
- `key-files.md`: `components/layout/AppShell.js` is the entry point for the whole UI tree and
  also owns the victory/offseason modals and the `useGameTick()` call — keep this diff focused
  on tab gating and avoid disturbing those.
- PRD §6.2 specifies this story.
