---
id: STORY-026
title: Add powerups that boost Power, Fuel and the other generation rates
status: pending
prd_source: /Users/brent/idle-base/docs/PRD-act-seven-farm-team.md
branch: null
pr_url: null
approach_summary: null
created: 2026-08-13
updated: 2026-08-13
---

# Add powerups that boost Power, Fuel and the other generation rates

Act VII needs its own boost layer: some powerups raise Power/Fuel generation, others raise Oxygen
and Provisions. These must flow through the existing modifier system rather than being applied
locally, or they will be silently inert.

## Acceptance Criteria

- [ ] New bonus keys are added to `data/modifierKeysConfig.js` `BONUS_KEYS` **with clamps**. A
      modifier key not in that list is silently inert — this is the single most likely way this
      story ships broken.
- [ ] Every new key ends in `Mult`, per the naming convention, and is composed through
      `computeModifiers` (`act ← era ← capsShop ← perks ← powerups`), not read directly.
- [ ] Powerup config lives in `data/actSevenPowerupsConfig.js`; the shop renders `listOffers` rows
      verbatim.
- [ ] Purchase honours the per-act currency rather than hardcoding one.
- [ ] Expiry is driven by `expiresAtClock` through the existing powerup expiry path, so it resolves
      correctly during an 8-hour offline catch-up.
- [ ] A powerup active across a phase boundary behaves correctly and does not double-apply.
- [ ] `npm run build` passes.

## Notes

- PRD §5.9.
- `conventions.md`: "Multipliers end in `Mult` and are members of `BONUS_KEYS` in
  `data/modifierKeysConfig.js`. A key not in that list is silently inert."
- `key-files.md`: `engine/modifiers.js` — never read `balanceConfig` directly for anything an act
  can override.
- **Depends on STORY-025.**
- `engine/pacing.js` is the cautionary example: `gameSpeedMult` is the only modifier that *divides*
  a duration. Be explicit about direction for any new key.
