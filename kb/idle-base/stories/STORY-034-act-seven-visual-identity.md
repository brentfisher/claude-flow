---
id: STORY-034
title: Give Act VII its own palette — the expedition body class, the v7 tokens and the phase pills
status: pr-opened
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: story/STORY-034-visual-identity
worktree_path: null
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/32
is_architectural: true
approach_summary: null
created: 2026-08-16
updated: 2026-08-16
---

# Give Act VII its own palette — the expedition body class, the v7 tokens and the phase pills

**Act VII must not look like the ballpark**, and today it does. Everything §6.8 specifies is
unshipped: nothing in `src/` references `--v7-bg`, `body.expedition`, or any phase pill. A player
who crosses into Act VII watches the ballpark tear itself apart and then lands on the same green
ground it was made of.

The ballpark is warm and saturated — green ground, gold, clay, outfield blue. Act VII is cold and
near-monochrome with **exactly one warm colour in it**: the amber accent, the instrument glow.
Everything the player buys or reads is amber; everything else is blue-grey.

**This story is also the structural owner of Act VII's CSS**, and that is the larger half of its
value. `styles/global.css` **ends inside an `@media (max-width: 640px)` block**, so a rule appended
to the file is silently scoped to phones — it builds clean, it reads correctly in a diff, and it is
invisible on desktop. Four panel stories are queued behind this one and every one of them needs to
add CSS. This story creates the single `body.expedition` feature section, **above** that media
query, that the panel stories extend, plus the shared panel primitives they will all reach for. It
must land before them.

It deliberately does **not** touch any panel body. Panels stay as they are; this story only changes
what they look like when they arrive.

## Acceptance Criteria

**The tokens**

- [ ] `styles/global.css` gains ONE new feature section defining `body.expedition { --v7-*: … }`,
      placed **above** the file's trailing `@media (max-width: 640px)` block, carrying all eleven
      §6.8 tokens: `--v7-bg`, `--v7-panel`, `--v7-chip`, `--v7-border`, `--v7-ink`, `--v7-muted`,
      `--v7-accent`, `--v7-accent-ink`, `--v7-good`, `--v7-drain`, `--v7-alert`.
- [ ] Each token carries its §6.8 value and a comment giving its role and its computed contrast
      ratio, in the shape `data/eras.js:1-17` uses — a named palette with a reason per colour.
- [ ] Overrides for the roughly a dozen selectors §6.8 names — at minimum `.app-shell`,
      `.header-stats`, `.stat-chip` (and its `.label`), `.panel` (and its `h2`), `.muted`, and the
      tab bar's active state — all inside the same section.

**The switch**

- [ ] `AppShell` toggles the `expedition` class on `document.body` from an effect keyed on
      `resolveRules(state).seasonFrozen`, and removes it on unmount. One line, idempotent.
- [ ] **It applies on mount, not after the teardown.** Verify by loading a save that is already in
      Act VII: there must be no frame of ballpark green before the palette lands.
- [ ] Leaving Act VII (or unmounting) restores the ballpark palette with no residue — verify the
      class is gone from `document.body`.

**The phase pills**

- [ ] The five phase pills are authored in `src/data/` in the `{ bg, ink }` shape `data/eras.js`
      uses — `aftermath`, `lifeSupport`, `lunar`, `deepSpace`, `majors` — each with its §6.8 value
      and its computed ratio in a comment.
- [ ] Every pair clears the **4.7:1** floor `eras.js` set for itself. Compute the ratios rather
      than copying them, and record the computation.
- [ ] A pill renders somewhere the player can see the current phase. Keep it to one surface; do not
      add a tab.

**Shared primitives for the panels queued behind this**

- [ ] The section defines the reusable pieces the four panel stories will need — at minimum a
      rate/meter treatment using `--v7-good` / `--v7-drain` / `--v7-alert`, and a shop-row
      treatment — so the panel stories extend this section rather than each inventing one.
- [ ] A comment at the head of the section states that it is the Act VII CSS home, that later panel
      stories add their rules **inside** it, and **why**: `global.css` ends inside a mobile media
      query and an appended rule is silently desktop-invisible.

**Verification**

- [ ] `npm run build` passes.
- [ ] No player-facing string is added to a component — any new prose lives in `src/data/`.

## Notes

- **PRD §6.8** in full. §6.8 also specifies the application mechanism (one class on
  `document.body`, toggled by an effect in `AppShell` keyed on `seasonFrozen`) and rules out the
  alternatives: a second stylesheet or a second shell are what **Decision 3.1** forbids. The
  ballpark ground is painted on `html, body` (`global.css:5-13`) and `body` is the only element
  above the React root, so there is no way to reach it from inside the tree.
- **This story LANDS FIRST among the Act VII UI stories.** STORY-035/036/037 (and later 038/039/040)
  all add CSS, and it must go inside this story's section. Running them in parallel with this one
  produces a four-way conflict on the one file whose wrong resolution is invisible.
- `conventions.md`: **no number inline in a component** — the palette is data. Player-facing prose
  lives in `src/data/`; a string literal in a component is the same bug. Config files end in
  `Config.js`; `data/eras.js` is the naming precedent for a palette specifically, so match whichever
  reads more naturally and say why in a comment.
- **MERGE-NOTES Phase 2, hazard 3** is the reason this story exists as a structural owner rather
  than as a coat of paint: STORY-022 and STORY-023 both hit this exact trap, and the resolution
  note records that a rule landing after the mobile block "would produce a build that passes, a diff
  that looks right, and a teardown overlay plus a set of resource chips that are unstyled on
  desktop."
- `openspec/changes/act-seven-shell/design.md` **Decision 4** (the `'field'`/`FieldView` fallbacks
  were removed rather than special-cased) is a decision this story **preserves** — do not
  reintroduce a fallback surface to hang a palette off.
- `openspec/changes/act-seven-header-resource-readout/` is in flight in `changes/` and owns
  `HeaderStats.js` and the `.stat-chip` markup this story restyles. It is **merged** (PR #26), so
  the markup is settled; restyle it, do not restructure it.
- Contrast matters here more than usual and §6.8 says why: "chips render at 0.78rem on a phone,
  which is normal-size text for contrast purposes, so anything under 4.5:1 is unreadable in
  sunlight on the bus."
