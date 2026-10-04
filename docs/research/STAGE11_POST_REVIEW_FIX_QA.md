# Stage 11 post-review fixes

Date: 2026-10-04

Base commit: `050f70a6a0c8c31ffcd77137f526af4a7cb65bc1`

## Changes

- February 2026 KPI entries now own their place, scope, support and sparkline context. At 62 seconds, the film shows Matsuyama-wide 158 permits, with no Dogo-only support or sparkline. At 66 seconds, it shows Dogo's 14 precise records in the same 1 km cell, with Dogo's 23-month sparkline.
- Between the two KPI windows, the place/KPI/graph clear while the camera moves. Dogo's highlighted cell first appears at 64.5 seconds.
- Memory-layer `radiusMinPixels` and `radiusMaxPixels` are numeric limits (0.9 and 4.0). `getRadius` remains the per-record accessor, preserving the distinction between current and older permits and age-dependent opacity.
- Glow/core layer IDs remain stable within a month. `updateTriggers` updates halo radius/color at the existing 30 Hz cadence and core color at the existing 20 Hz cadence, avoiding repeated GPU layer initialization while keeping the same ignition clock.
- Four short local captions are reduced to brief phrases. Month schedule, camera keyframes, major captions, 80-second runtime and small evidence-period note retain their existing timing.
- Browser regression assertions cover the city/local scope transition, including mobile reduced motion. Full desktop/mobile playback reads film time and HUD atomically, asserts scope/graph state during the relevant film-time windows, then captures exact 62/66-second frames after uninterrupted playback.

## Local verification

- Timeline/focus regeneration: PASS.
- Stage 11 editorial/numeric QA: PASS (62 contiguous months, 80 seconds, existing numeric checks and new scope checks).
- JavaScript syntax checks: PASS for controller and both browser test files.
- Controller execution with synthetic DOM/map/layer objects: PASS for desktop and mobile/reduced-motion contexts. Checked city/local HUD, transition clearing, focus timing, numeric memory limits, current/older radius and opacity, existing May/Mitsu KPI contexts, stable glow IDs and advancing ignition/update triggers. This check does not exercise WebGL or pixel rendering.

## Remote verification

- Scope/radius/caption fix: `5c1fb858f165e48ac55628ae6450ce51fd09d614`.
- Film-clock test correction: `cbe1d1cbf8f8ab2810a69345937863542fef3620`.
- Glow reuse: `20047ebccd8250125d8ac9ee1e3aeae135104c4c`.
- Initial workflow `37188603013`: six control/regression tests passed; two playback tests failed because host-loop indices were incorrectly treated as film time. HUD sampling was consolidated and exact-frame checks separated from continuous playback.
- Intermediate workflow `37189085862`: succeeded with one desktop playback retry (first attempt observed 56/62 months under CI rendering load). Successful desktop and mobile telemetry both reached 62 months and film time 79.999. Exact 62/66-second screenshots were inspected in both viewports: city-wide 158 has no local sparkline/cell highlight; Dogo 14 has the local cell, precise-point scope and sparkline.
- Final glow-reuse build/browser workflow: SUCCESS, [37189498455](https://github.com/ryotamatsuki/ehime-restaurant-license-map/actions/runs/37189498455). Seven tests passed on their first attempt; desktop full playback passed on its configured retry (first attempt 59/62 months). Successful desktop/mobile telemetry each has 81 samples, ends at film time 79.999 and records all 62 months. Exact 62/66-second screenshots were also inspected again after the glow-reuse change. Rendering under CI load still produces an intermittent skipped-month result; this is a remaining reliability limitation, not a clean first-attempt pass.
- Final GitHub Pages deployment and public smoke tests: PASS, workflow `37189498485`.
- The subsequent bot commit `42ca0f2b55c0bc6b9eec190fa92c83f86b5317c6` changes only `STAGE6_BUILD_AUDIT.json`; tested and deployed application source is identical.
- Final recorded playback artifact: [11298234780](https://github.com/ryotamatsuki/ehime-restaurant-license-map/actions/runs/37189498455/artifacts/11298234780), retained through 2026-10-11.
- Physical iPhone testing remains unverified; mobile checks use a 390×844 Chromium viewport.
