---
id: STORY-035
title: Build the Ops panel — net rates, the ration, the phase and the standing directive
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: null
worktree_path: null
base_branch: null
pr_url: null
is_architectural: null
approach_summary: null
created: 2026-08-16
updated: 2026-08-16
---

# Build the Ops panel — net rates, the ration, the phase and the standing directive

`ops` is the tab Act VII opens on and, for the first 20–30 minutes, **the only one**. It is the
deliberate echo of Act I, where the whole game was one button on one screen. Today it renders
`PlaceholderPanel` — the words "This panel is not built yet." — so the act opens on an apology.

This is the screen you *watch*, against `fab` which is the screen you *spend* on. It is also the
only place the colony's central mechanic becomes legible: `engine/colony.js` solves a genuine fixed
point every tick — Power buys Provisions and Provisions buy Power — and computes a `satisfaction`
ration that throttles every rate in the act. **None of that is visible anywhere in the game right
now.** An act built on invisible net rates needs the one screen that shows them.

The panel is render-only. Every number comes from `colonyRates(state)`, which already returns
`{ satisfaction, supplyThrottle, gross, demand, net, capacity, passes, salvage }` — this story adds
no arithmetic, and a computed number appearing in the component is the bug `conventions.md` names.

It does **not** carry the Salvage click: `SearchLotButton` lives outside the tab switch in
`AppShell`'s `.hustle-bar`, and §6.6 is explicit that it stays there. It was once inside `LotPanel`
and creating a season silently deleted it.

## Acceptance Criteria

**The readout**

- [ ] `components/expedition/OpsPanel.js` renders real content and no longer returns
      `<PlaceholderPanel />`.
- [ ] Per-resource rows for the four consumables, each showing stock against `capacity` and the
      **net** rate from `colonyRates()`, signed, using `--v7-good` for surplus and `--v7-drain` for
      drain.
- [ ] A resource pinned at zero with negative raw demand, or at capacity with positive raw supply,
      reads as **0/s** and is visibly distinguished (`--v7-alert`) from one merely running negative
      — that clamp is Decision 3.3's throttle-rather-than-fail and the player must be able to see it.
- [ ] The **ration** (`satisfaction`) is shown as a percentage, with `supplyThrottle` distinguished
      from it rather than folded in — they are different facts and the header already treats them so.
- [ ] Salvage/s is shown, sourced from `colonyRates().salvage`, so the panel and `HeaderStats` can
      never disagree about how starved the colony is.

**Phase and directive**

- [ ] The current `expedition.phase` renders as the pill STORY-034 authors, read from that story's
      palette data rather than from a second copy.
- [ ] A standing **directive** line — the act's current objective in the Office's voice — renders
      from prose in `src/data/`, keyed by phase. No string literal in the component.
- [ ] The directive has an entry for every phase in `EXPEDITION_PHASES`, including `majors`, so no
      reachable phase renders an empty line.

**Behaviour under real states**

- [ ] With **no modules owned** (`aftermath`, the act's first 20–30 minutes) the panel renders
      honestly — zeros and the directive, not an empty box and not a crash.
- [ ] Renders without throwing against a save carrying **no `expedition` key at all**, via the
      defaulting accessor rather than a guard in the component.
- [ ] Reads `expedition` through `expeditionSlice()` / `colonyRates()` and never indexes
      `state.expedition.*` directly.

**Verification**

- [ ] `npm run build` passes.
- [ ] Drive `colonyRates()` under `node` against a starved colony, a surplus colony and an empty
      one, and confirm the panel's displayed values against the returned object — the repo's
      substitute for a test runner (`conventions.md`).
- [ ] Any new CSS goes **inside STORY-034's `body.expedition` section**, above the mobile media
      query.

## Notes

- **PRD §6.4** (the `ops` row: "net rates, the directive, the log, and where the Salvage click
  lives") and **§6.6** (the click and the feed stay outside the tab switch). **§5.6** is the
  satisfaction factor this panel is rendering; read it before deciding what to show.
- **Depends on STORY-034** for the palette, the phase pills and the CSS section. Do not author a
  parallel palette — extend that section.
- **The log.** §6.4 lists "the log" on this tab, but `EventFeed` already renders below the active
  panel in every act and §6.6 says it stays there — "the only always-on signal that the simulation
  is running." Do **not** add a second feed. If anything is added here it is a filtered view, and
  the default answer is nothing.
- `conventions.md`: components are **render-only** and "decide nothing about rules, costs, odds or
  availability"; a number inline in a component is a bug. Every figure on this panel is already
  computed by `engine/colony.js`.
- `openspec/changes/colony-consumption-offline-safety/` and `act-seven-full-module-ladder/` are the
  in-flight changes that own the solve and the derived capacity this panel displays. Both are
  **merged**. This story **preserves** their decisions — in particular that capacity is derived and
  never stored, so the panel must render `colonyRates().capacity` and never a stored ceiling.
- `openspec/changes/act-seven-shell/design.md` **Decision 2** (the reveal keys off
  `expedition.phase`, not off parallel milestones) is **preserved** — read the phase, do not
  introduce a milestone to describe it.
- `HeaderStats.js` already renders resource chips (STORY-023, PR #26). This panel is the expanded
  form, not a replacement: do not change the header, and do not let the two compute anything
  differently.
