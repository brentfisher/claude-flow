---
id: STORY-040
title: Build the Contracts panel — the optional board, paid in Fuel
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: null
worktree_path: null
base_branch: null
pr_url: null
is_architectural: false
approach_summary: >
  Renders engine/contracts.js (STORY-030, merged #34). Must read as an OPPORTUNITY, never a chore — §6.4 makes it the only purely optional tab and a player who never opens it still finishes. MUST RUN LAST OF THE SIX: it also removes PlaceholderPanel.js and the blurb / ACT_SEVEN_PLACEHOLDER_NOTE entries once nothing consumes them, keeping id/label/title which TabNav still spreads — so it needs 035-039 landed first, and must re-verify that the three id lists (actSevenPanels, AppShell PANELS, TabNav TABS) still agree, two of which fail SILENTLY.
created: 2026-08-16
updated: 2026-08-17
---

# Build the Contracts panel — the optional board, paid in Fuel

`contracts` is last in the tab order, and §6.4 is explicit about why: **it is the only purely
optional tab in the act.** A player who never opens it still finishes, slowly — which is Decision
3.6 applied to the fuel economy. That framing is the design constraint on this panel, not a
footnote: it must read as an opportunity, never as a chore the act is withholding progress behind.

§9's contracts pay **fixed Fuel**, and §9.2 names two numbers that must not be conflated. This panel
renders whichever the engine exposes and must not compute either.

## Acceptance Criteria

- [ ] `components/expedition/ContractsPanel.js` renders real content and no longer returns
      `<PlaceholderPanel />`.
- [ ] The board renders from `engine/contracts.js`'s listing function; the panel resolves no payout
      and no availability.
- [ ] Accepting and completing a contract dispatch through a `state/actions/` module; a refused
      action is a no-op.
- [ ] Each row shows what it asks for and what it pays, in Fuel, from the engine's values.
- [ ] An empty board renders honestly rather than as a broken panel.
- [ ] Renders without throwing against a save with no `expedition` key and no contract state.
- [ ] No component-side timer or `Date.now()`; any contract clock is read from state.
- [ ] `npm run build` passes.
- [ ] Drive the contracts engine under `node` across an empty board, an active contract and a
      completed one, and confirm the panel matches the engine's return values.
- [ ] Any new CSS goes **inside STORY-034's `body.expedition` section**, above the mobile media
      query.

## Notes

- **PRD §9** in full — **§9.1** (why contracts exist at all), **§9.2** (payout sizing and the two
  numbers that must not be conflated), **§9.4** (the board) and **§9.6** (the engine spec).
- **BLOCKED on STORY-030**, which builds `engine/contracts.js` and the twelve contracts. This story
  renders that engine and implements none of it.
- **Depends on STORY-034** for the palette and CSS section.
- **Ledger R3** rules that contract payouts resolve **per launch, not per phase**. If the panel shows
  any progress or timing, it must reflect that; a per-phase reading would be a different game.
- **This is the last of the six panels.** When it lands, `components/expedition/PlaceholderPanel.js`
  and the `blurb` / `ACT_SEVEN_PLACEHOLDER_NOTE` entries in `data/actSevenPanels.js` have no
  remaining consumer. **Remove them in this story** and keep the `id` / `label` / `title` entries,
  which the tab bar still spreads. `data/actSevenPanels.js:11-16` records that three id lists must
  agree and that two of them fail silently — verify all three still agree after the removal.
- `conventions.md`: render-only components, prose in `src/data/`. Contract prose is authored in the
  contracts config by STORY-030 — render it, do not restate it.
