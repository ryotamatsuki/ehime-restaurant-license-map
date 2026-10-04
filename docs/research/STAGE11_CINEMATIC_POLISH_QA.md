# Stage 11 — Cinematic Polish QA

Date: 2026-10-04  
Status: **PASS / COMPLETE after public deployment**

## Scope

Stage 11 polished only Cinematic Mode and its supporting data/interaction. The analytical Explore mode remains intact and continues to use the existing filters, timeline, points/heatmap/hexagon/mesh views and evidence indicators.

## Editorial changes implemented

### 1. Continuous time instead of scene jumps

The 80-second film now advances through all **62 consecutive months** from 2021-06 through 2026-07.

Routine months are compressed; authored moments slow down:
- 0–5 s: opening;
- 5–22 s: retrospective continuous build-up;
- 22–37 s: 2024-09 through spring 2025;
- 37–48 s: 2025-05 citywide hold and bridge;
- 48–56 s: Mitsu;
- 56–70 s: year-end through 2026-02 Dogo;
- 70–80 s: advance to 2026-07 and closing comparison.

There is no dedicated methodology chapter or stop at the source boundary.

### 2. Retrospective explanation reduced to a corner note

The film only shows:
- `2021-06〜2024-08：参考復元`
- `2024-09〜2026-07：月次観測`

The note switches quietly at 2024-09. No large explanation, color reset, artificial pause or before/after claim is attached to the boundary.

Detailed completeness, location precision, and permit/opening caveats remain available in Explore and the small film disclaimer.

### 3. Time-synchronized camera

Camera state is calculated from cinematic elapsed time on every render frame.

Implemented:
- intermediate camera keyframe interpolation;
- pull → lateral move → push for Mitsu;
- wide static view for citywide beats;
- push-in then hold for Dogo;
- mobile-specific reduced zoom/pitch and vertical offset;
- `prefers-reduced-motion` static keyframe behavior.

Because the camera is derived from the same elapsed clock as month, points and HUD, Pause freezes all of them together. Resume continues from the same state.

### 4. Three-layer point grammar

Cinematic events are rendered as:
- bright high-precision core;
- brief soft halo on monthly ignition;
- decaying high-precision historical memory.

Retrospective town-centroid points are weak ambient context only. Precise local 1km claims/highlights use address/parcel-level points.

No decorative particles, invented paths, or point-to-point motion were added.

### 5. Information staging

Major beats now stage information rather than switching everything simultaneously:
1. establish place;
2. show ignition/focal 1km cell;
3. introduce the scoped number;
4. show one short caption;
5. remove the caption and leave map-only breathing room.

Bridge periods prioritize the date. Local holds reduce the date and prioritize place/count.

Large HUD panels are hidden during quiet bridge/final holds.

### 6. Copy

Key captions were simplified:
- `松山、62か月の許可の足跡。`
- `光は、その月の許可の記録。`
- `竹原・藤原にも、許可のまとまりが見える。`
- `2025年5月。許可の発生が市内に広がる。`
- `三津。この月、許可が再びまとまって現れる。`
- `2026年2月、道後周辺に許可が集中。`
- `道後と三津。許可が繰り返し現れる場所が見えてくる。`

Abstract production-language such as “核”, “集積軸”, “大きく発光”, and source-boundary explanatory captions were removed from principal copy.

## Numeric verification

All values are rebuilt from the current processed data on every web build and asserted by `src/cinematic/qa_stage11.py`.

Verified:
- 2024-02 Dogo 1km / high-precision: **6**
- 2024-05 Takehara/Fujiwara 1km / high-precision: **4**
- 2024-09 Dogo 1km / high-precision: **15**
- 2024-11 Airport/Takehara 1km / high-precision: **4**
- 2025-05 Matsuyama citywide permit events: **165**
- 2025-05 map-visible high-precision points: **40**
- 2025-08 Mitsu 1km / high-precision: **5**
- 2025-12 Matsuyama citywide: **131**
- 2026-02 Matsuyama citywide: **158**
- 2026-02 Dogo 1km / high-precision: **14**
- exact monthly period Dogo active: **19/23 months**
- exact monthly period Mitsu active: **15/23 months**

The 2024-09 scene does not use a month-over-month increase across the source boundary.

Mitsu support copy is `直前3か月は同じ区画で合計1件`; it is not expressed as a “5× increase”.

## Local comparison graphics

Dogo and Mitsu major local scenes show compact 23-month sparklines using the same:
- exact monthly observation window;
- 1km mesh;
- address/parcel high-precision point definition.

This is a descriptive count series and does not imply store survival.

## Ending and Explore handoff

The final hold shows:
- `道後 19/23か月`
- `三津 15/23か月`

The viewer can select Dogo or Mitsu and use the visible CTA:
`この場所の時間を、自分で見る`

The handoff restores Explore mode at:
- Dogo → 2026-02 and the Dogo camera;
- Mitsu → 2025-08 and the Mitsu camera.

Existing analytical interactions remain available after handoff.

## Automated QA

### Full browser build/regression

Latest successful run:
- workflow: Stage 6 build and test time map
- run: **37179549468**
- result: **SUCCESS**

It covers:
- production Vite build;
- generated web-data audit;
- existing desktop Explore regression;
- existing mobile Explore regression;
- Cinematic scoped KPI tests;
- pause/resume clock+camera freeze;
- intermediate camera interpolation;
- reduced-motion behavior;
- full 80-second desktop playback;
- full 80-second mobile playback.

### Full-playback artifact

Artifact:
- `cinematic-playback`
- artifact id: **11294507911**
- retained by GitHub Actions for 7 days.

Recorded Chromium videos:
- desktop artifact duration: approximately **84.76 s** including test setup/teardown;
- mobile artifact duration: approximately **83.40 s** including test setup/teardown.

The Cinematic engine itself remains exactly 80 s.

Telemetry confirms:
- all 62 source months were visited;
- final month = 2026-07;
- no JavaScript page errors in the passing full-playback run.

### Visual review

The rendered desktop and mobile artifacts were inspected, not only screenshots/test assertions.

重点確認:
- opening: map readable, first points establish the light grammar;
- 2025-05: wide view retains citywide scope while 165/40 remain semantically separate;
- Mitsu: pull→move→push lands on the western focus; old memory + five current high-precision events are visible; local sparkline/caption are readable;
- Dogo: citywide 158 precedes the Dogo push; local 14 is the principal number after the camera settles; focal cell and sparkline correspond to the same 1km/high-precision definition;
- closing: citywide return, Dogo/Mitsu persistence values, location selector and Explore CTA are visible.

Mobile browser QA additionally asserts that local focal geometry remains above the lower HUD in the targeted beats.

## Public deployment QA

GitHub Pages deployment is considered Stage 11-complete only after the current main is deployed and:
- public HTML loads;
- `cinematic_timeline_v2.json` is public;
- `cinematic_focus_series.json` is public;
- public timeline has 62 months / 80 seconds;
- public Dogo/Mitsu exact-active counts are 19/15;
- public numeric checks include 2025-05 citywide 165 and 2026-02 Dogo 14.

## Remaining constraints

- Physical iPhone hardware was **not available** in this environment. Mobile verification used real Chromium rendering at 390×844 plus full 80-second capture. This is not reported as an iPhone-device PASS.
- The public map still uses a darkened GSI raster rather than a purpose-built dark vector basemap.
- Frame-time telemetry on physical mobile hardware is not measured.
- The motion remains intentionally data-driven; no decorative particles or invented movement paths were added.

These are recorded constraints, not unreported checks.
