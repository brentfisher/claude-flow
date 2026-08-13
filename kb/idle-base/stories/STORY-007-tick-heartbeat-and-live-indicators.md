---
id: STORY-007
title: Add a tick heartbeat, next-event countdown, floating gains, and per-currency rates
status: merged
prd_source: /Users/brent/idle-base/docs/PRD-incremental-odyssey.md
branch: story/STORY-007-tick-indicators
worktree_path: /Users/brent/idle-base-worktrees/STORY-007
base_branch: master
pr_url: https://github.com/brentfisher/idle-base/pull/7
is_architectural: false
approach_summary: >-
  Presentational only: a pulsing heartbeat and a game clock (via the existing
  `formatDuration()`) in `HeaderStats.js`, a countdown bar fed by the value
  `findNextEventClock()` already computes and currently discards, floating +N gain numbers, and
  per-currency rates generalizing what `RevenueTicker.js` already does for cash. Touches
  `components/layout/HeaderStats.js`, `components/ticketing/RevenueTicker.js` and
  `styles/global.css` for keyframes. Must degrade gracefully when `findNextEventClock()`
  returns `Infinity` in the early acts — no NaN, no permanently full bar, no runaway timer —
  and must show only currencies relevant to the current act. Prefer CSS animation over
  state-driven frame updates, since there is no memoization layer. Depends on 001, 003 and 004
  for the values it displays.
created: 2026-08-09
updated: 2026-08-10
---

# Add a tick heartbeat, next-event countdown, floating gains, and per-currency rates

The simulation ticks every second and resolves a game every 60, but `HeaderStats` shows static
totals and nothing on screen moves. This story is the presentational half of the "make the game
feel alive" work (STORY-006 is the narrative half): four small pieces of motion that together
make it obvious at a glance that the game is running.

Notably, one of these values is already computed and thrown away — `findNextEventClock()` in
`engine/tickEngine.js` calculates exactly the countdown target needed and returns it only for
internal stepping.

## Acceptance Criteria

- [ ] **Heartbeat:** a small indicator in `HeaderStats` visibly pulses on every `TICK`.
      A player looking at the screen for two seconds without interacting can tell the game is
      running.
- [ ] **Game clock:** `state.clock` is displayed, formatted with the existing
      `utils/formatNumber.js: formatDuration()` — do not write a new formatter.
- [ ] **Next-event countdown:** a progress bar toward the next scheduled event. Expose the value
      `findNextEventClock()` already computes rather than recalculating it in the component.
- [ ] The countdown degrades gracefully when there is no pending event (early acts, where
      `findNextEventClock()` correctly returns `Infinity`) — it must not render `NaN`, a full
      bar, or a runaway timer.
- [ ] **Floating gains:** a transient `+N` animates away from the currency chips on income tick,
      and from the click button once Act I exists.
- [ ] **Per-currency rates:** every currency shown in `HeaderStats` displays a live per-second
      rate beneath it, extending to all currencies what `RevenueTicker` already does for cash.
- [ ] Only currencies relevant to the current act are shown — the header must not display
      `coins` and `cash` at zero during Act I.
- [ ] Animations are CSS-based in `src/styles/global.css`, consistent with the existing
      single-stylesheet approach. No animation library is added.
- [ ] Running `npm start`: the heartbeat pulses, the countdown advances and resets when a game
      resolves, and floating numbers appear on income.

## Notes

- **Depends on STORY-001** for `state.wallet` (per-currency rates need the multi-currency
  shape) and reads `getUnlockedFeatures`/`progression` from **STORY-004** to decide which
  currencies to show. It can be built against cash alone first and extended, but landing it
  after both is simpler.
- **Depends on STORY-003** for the per-currency rate values — `totalIncomePerSecond()` is what
  the header should display. Do not duplicate rate math in the component.
- `conventions.md`: no selector or memoization layer exists — components call `useGame()` and
  read state directly. Per-second animation should not trigger a full re-render storm; prefer
  CSS animation over state-driven frame updates.
- `conventions.md`: single global stylesheet at `src/styles/global.css`, no CSS-in-JS. Note that
  existing components do use inline `style={{}}` objects for one-off layout (see
  `components/roster/PlayerCard.js`), so that is acceptable for positioning but keyframes belong
  in the stylesheet.
- `conventions.md`: CommonJS throughout; plain `function` declarations.
- `conventions.md` / `package.json`: **no test framework, linter, or CI exists** — only `start`
  and `build`. Verify by running the app and by diff review. Adding a test framework is out of
  scope per PRD §10.
- `key-files.md`: `components/layout/HeaderStats.js` and `components/ticketing/RevenueTicker.js`
  are the anchor files; `RevenueTicker` already demonstrates the rate-display pattern to
  generalize.
- PRD §7 items 1, 3 and 4 specify this story.
