# Stage 11 post-review fixes

Date: 2026-10-04

Base commit: `050f70a6a0c8c31ffcd77137f526af4a7cb65bc1`

## Changes

- February 2026 KPI entries now own their place, scope, support and sparkline context. At 62 seconds, the film shows Matsuyama-wide 158 permits, with no Dogo-only support or sparkline. At 66 seconds, it shows Dogo's 14 precise records in the same 1 km cell, with Dogo's 23-month sparkline.
- Between the two KPI windows, the place/KPI/graph clear while the camera moves. Dogo's highlighted cell first appears at 64.5 seconds.
- Memory-layer `radiusMinPixels` and `radiusMaxPixels` are numeric limits (0.9 and 4.0). `getRadius` remains the per-record accessor, preserving the distinction between current and older permits and age-dependent opacity.
- Four short local captions are reduced to brief phrases. Month schedule, camera keyframes, major captions, 80-second runtime and small evidence-period note retain their existing timing.
- Browser regression assertions cover the city/local scope transition, including mobile reduced motion. Full desktop/mobile playback records the 62-second frame and asserts scope/graph state at 62 and 66 seconds.

## Local verification

- Timeline/focus regeneration: PASS.
- Stage 11 editorial/numeric QA: PASS (62 contiguous months, 80 seconds, existing numeric checks and new scope checks).
- JavaScript syntax checks: PASS for controller and both browser test files.
- Controller execution with synthetic DOM/map/layer objects: PASS for desktop and mobile/reduced-motion contexts. Checked city/local HUD, transition clearing, focus timing, numeric memory limits, current/older radius and opacity, and existing May/Mitsu KPI contexts. This check does not exercise WebGL or pixel rendering.

## Remote verification

Pending production build, browser regression/full-playback workflow and GitHub Pages deployment after this change is pushed. Workflow results will be added after completion. Physical iPhone testing is outside this environment's verification.
