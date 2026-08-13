---
id: STORY-033
title: Write the Act VII story beats, feed lines and Earth dispatches
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: null
pr_url: null
approach_summary: null
created: 2026-08-13
updated: 2026-08-13
---

# Write the Act VII story beats, feed lines and Earth dispatches

The connective tissue that makes the act one world rather than five sections. The voice is
institutional and dry — a scouting organization doing paperwork, with the comedy coming from a flat
administrative register colliding with the enormity of the reveal. The reveal is delivered as flat
*corrections to the player's terminology*, not as exposition.

The emotional payload of the act lives here: the frozen league carrying on without the player,
reported at long intervals as if from very far away.

## Acceptance Criteria

- [ ] Story beats added to `data/storyBeats.js` matching its existing shape. The Act VII intro keeps
      `kind: 'actIntro', actIndex: 6` so `getActIntroBeat()` and `AppShell` need **no change**.
- [ ] Beat triggers are **level predicates, never edges**, so an offline catch-up crossing several
      triggers at once cannot double-fire. Beats record in `progression.storyBeatsSeen`; the Earth
      dispatches ride the same ledger rather than a second one.
- [ ] `StoryCard.js` gains a `{beat.objective && …}` guard — Act VII beats have no objective block
      and it currently renders unconditionally.
- [ ] Act VII feed lines added to `data/feedMessages.js`, covering colony operations, resource
      warnings, launches and contracts.
- [ ] **The frozen-league thread**: 5–8 lines with a clear arc, fired at long intervals. A player who
      plays Act VII for an hour sees at least one (PRD §12 criterion 10).
- [ ] A published **naming convention** for sites, modules, artifacts and contracts, plus name banks,
      so the invented names across other stories read as one institutional vocabulary.
- [ ] Act VII's `clickLabel` is authored here.
- [ ] All prose in `data/`. No string literal in a component.
- [ ] `npm run build` passes.

## Notes

- PRD §10, §12 criterion 9 ("nothing reads as generic sci-fi") and criterion 10.
- **Depends on STORY-021**; can otherwise run parallel to the content stories, and is the most
  parallelizable story in the set.
- `key-files.md`: `data/feedMessages.js`, `toastMessages.js`, `storyBeats.js` are "all player-facing
  prose. A string literal in a component belongs in one of these."
- The scout in `storyBeats.js` is an existing character — reuse rather than inventing a new narrator.
- `conventions.md`: `feed.js` is a capped ring buffer; anything event-driven must be idempotent and
  storm-resistant under offline catch-up.
