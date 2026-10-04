# Stage 10 — Cinematic Mode Implementation & QA

Date: 2026-10-04  
Status: **PASS / COMPLETE**

## Implemented

The Stage 9 80-second silent-first cinematic specification is now implemented as an additive mode in the existing GitHub Pages application.

### Entry / exit
- `Cinematic` button added to the existing header.
- Existing analytical mode remains unchanged and is restored on exit.
- `Exploreへ戻る` and Escape exit Cinematic Mode.

### Playback
- machine timeline: `data/processed/cinematic/cinematic_timeline_v1.json`
- published to `web/public/data/cinematic_timeline_v1.json` by the reproducible web-data build.
- requestAnimationFrame-driven deterministic clock.
- pause/resume.
- next authored insight.
- Left/Right keyboard scene navigation.
- Space play/pause.
- autoplay pauses when the page becomes hidden.

### Map / motion
- same MapLibre map instance is reused.
- cinematic dark treatment is applied through raster saturation/brightness/contrast.
- deck.gl layers implement:
  - historical memory;
  - fresh-event emphasis;
  - focal hotspot cue.
- events never travel between coordinates.
- event history accumulates and decays according to age.
- retrospective and exact observations use distinct luminance.
- authored camera states use the committed scene coordinates.
- 2024-09 changes the evidence badge to exact monthly.
- 2026-02 remains the principal climax.

### HUD
- persistent month clock.
- evidence badge.
- one primary KPI.
- compact supporting KPI line.
- authored Japanese annotation.
- playback progress.
- explicit permit/opening disclaimer.

### Mobile / accessibility
- mobile HUD uses a compact bottom treatment.
- reduced-motion users start paused.
- reduced-motion camera uses jumpTo with limited pitch instead of fly/ease motion.
- keyboard controls implemented.

## Automated QA

### Stage 6 build and browser regression

GitHub Actions run:
- run `37177268739`
- conclusion: **success**

Passed:
- production Vite build;
- web data/bundle audit;
- existing desktop analytical-map test;
- existing mobile analytical-map test;
- Cinematic entry / scene navigation / 2024-09 evidence transition / exit;
- Cinematic mobile + reduced-motion behavior;
- no page errors in tested desktop path.

### GitHub Pages deploy

GitHub Actions run:
- run `37177275406`
- conclusion: **success**

Public deployment smoke test now additionally verifies:
- cinematic timeline is publicly retrievable;
- runtime = 80 seconds;
- 2024-09 evidence transition exists;
- 2026-02 climax KPI = 158.

## Important implementation note

The current implementation is a performant first production realization of the Stage 9 specification. It implements the core data-film grammar and authored story without replacing the analytical map.

The following remain legitimate future polish rather than Stage 10 blockers:
- custom vector dark basemap instead of darkened GSI raster;
- shader-level Gaussian glow;
- richer scene-internal camera interpolation for every sub-beat;
- screenshot-based visual-regression thresholds;
- measured frame-time telemetry on a physical iPhone.

## Exit criteria

- [x] additive Cinematic entry point
- [x] dark cinematic map treatment
- [x] deterministic committed timeline
- [x] historical memory + fresh event emphasis
- [x] authored camera states
- [x] evidence transition
- [x] scene-specific HUD / KPI / annotation
- [x] pause / resume / next / exit
- [x] keyboard controls
- [x] reduced motion
- [x] mobile layout
- [x] production build PASS
- [x] desktop browser QA PASS
- [x] mobile browser QA PASS
- [x] public Pages deployment PASS
- [x] public cinematic data smoke test PASS

Stage 10 is complete.
