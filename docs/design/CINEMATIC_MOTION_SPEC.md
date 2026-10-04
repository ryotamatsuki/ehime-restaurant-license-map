# Stage 9 — Matsuyama Cinematic Motion Specification

Date: 2026-10-04  
Status: **IMPLEMENTATION SPEC / COMPLETE**  
Depends on:
- `docs/design/URBAN_DATA_ANIMATION_BENCHMARK.md`
- `docs/design/MATSUYAMA_CINEMATIC_SCENE_EXTRACTION.md`
- `data/processed/cinematic/cinematic_storyboard_seed.json`

## 1. Product contract

Cinematic Mode is a guided, silent-first, approximately **80-second** data film embedded beside the analytical map.

It is not:
- a replacement for Explore mode;
- a claim that permit events equal shop openings;
- an animation of physical movement;
- an equal-time slideshow of 62 months.

It is:
- a temporal narrative derived from measured change;
- a persistent-map experience with authored camera movement;
- a visual-memory system in which new permit events ignite and older events decay;
- an evidence-aware story that visibly changes treatment at 2024-09.

Benchmark synthesis:
- Flight Patterns: dark field + luminous memory;
- Urban Layers: accumulation and persistence;
- HERE Traffic Analytics: camera/editorial choreography;
- District Mobility: guided insight cards;
- NYC Taxis: visible clock + live KPI;
- Real Time Rome: city pulse;
- HubCab: scale-aware marks and nonlinear magnitude.

## 2. Runtime and temporal grammar

Target runtime: **80.0 s**.

The 62 source months remain temporally ordered. Routine months are compressed into bridge playback; authored scenes slow down around detected changes.

Global phases:
- 0.0–2.5 s: title / orientation;
- 2.5–38.0 s: retrospective reconstruction;
- 38.0–44.5 s: evidence transition;
- 44.5–76.5 s: exact-observation story;
- 76.5–80.0 s: end-state / handoff to Explore.

Playback clock:
- persistent upper-left month label;
- routine bridge rate: 0.45–0.65 s per source month;
- insight hold: 4.5–7.5 s;
- never jump backward in source time;
- chapter transition may hold the same month while camera/style changes.

## 3. Visual hierarchy

At every instant the viewer should be able to identify, in order:
1. where attention belongs;
2. what month it is;
3. what changed;
4. one headline number;
5. whether evidence is retrospective or exact.

Do not show more than:
- 1 headline annotation;
- 1 primary KPI;
- 2 supporting micro-KPIs;
- 1 evidence badge;
simultaneously.

The map must occupy >= 78% of desktop viewport area and >= 70% of mobile viewport height during autoplay.

## 4. Basemap and color grammar

Cinematic basemap:
- near-black neutral land;
- water slightly lighter/different luminance than land, not saturated;
- roads low contrast;
- labels hidden during high-motion phases and restored during holds;
- administrative boundaries extremely faint.

Data luminance must dominate the basemap.

Evidence grammar:
- retrospective partial: lower saturation/luminance, softer halo, slightly dashed/dithered evidence badge;
- exact monthly: full luminance, crisp event core, sharper annotation rule;
- 2024-09 transition: no hue gimmick required; use a deliberate **focus sharpening**:
  - basemap blur/veil reduces;
  - point cores sharpen;
  - evidence badge changes from `参考復元・不完全` to `完全観測・月次`.

Do not imply retrospective points are less geographically real merely because historical coverage is incomplete. Evidence styling communicates coverage quality, not location uncertainty. Location precision continues to be encoded separately.

## 5. Event lifecycle model

Each permit event has a visual lifecycle. No point moves across the map.

Let `a` be normalized age in animation time since the event enters the current month.

### 5.1 Ignition

Duration: 420 ms.

Core radius:
`r_core = 2.2 + 1.6 * sin(pi * clamp(a/0.42,0,1)) px`

Halo radius:
- starts 3 px;
- expands to 12 px desktop / 9 px mobile;
- ease-out cubic.

Opacity:
- core 0 → 1 in first 120 ms;
- halo 0 → 0.70 by 100 ms → 0.15 at 420 ms.

A deterministic event-id hash supplies 0–180 ms jitter so a month does not ignite as one synthetic flash.

### 5.2 Fresh state

Age 0–1 source month:
- core opacity 0.92 exact / 0.72 retrospective;
- radius 2.2 px;
- hotspot contribution weight 1.0.

### 5.3 Short memory

Age 1–3 months:
- opacity decays 0.55 → 0.34;
- radius 1.8 px;
- hotspot contribution weight 0.62 → 0.40.

### 5.4 Medium memory

Age 4–12 months:
- opacity decays 0.24 → 0.10;
- radius 1.4 px;
- hotspot contribution weight 0.28 → 0.12.

### 5.5 Long urban memory

Age >12 months:
- opacity floor 0.045 exact / 0.035 retrospective;
- radius 1.0 px;
- no pulsing;
- no claim of active shop status.

The legend must call this layer **過去の許可発生の残像**, never “existing restaurants”.

## 6. Hotspot field model

The glow field is descriptive, not inferential.

Input:
- strict address/parcel points for fine-spatial focal scenes;
- town-or-better points may appear as ambient context but cannot drive precise hotspot claims.

Kernel:
- screen-space Gaussian-like glow;
- base radius 18 px citywide, 26 px neighborhood;
- magnitude scale: `sqrt(count)`, not linear;
- max intensity clamped at the 95th percentile of scene-level mesh intensity.

Persistent-core memory:
`I_memory = sum(w_age * w_evidence * w_precision)`

where:
- `w_age` follows the event lifecycle;
- `w_evidence = 1.0 exact, 0.72 retrospective`;
- `w_precision = 1.0 strict, 0.35 town-centroid ambient only`.

For an authored hotspot scene:
- focal mesh receives a 900–1200 ms breathing envelope;
- scale 1.00 → 1.10 → 1.00;
- one cycle only unless the data itself changes again;
- no endless decorative breathing.

## 7. Camera system

Default citywide camera:
- center approximately Matsuyama urban core: lon 132.755, lat 33.840;
- zoom 11.1 desktop / 10.6 mobile;
- pitch 32°;
- bearing -8°.

Neighborhood focus:
- zoom 13.0–13.7 desktop / 12.3–13.0 mobile;
- pitch 42–48°;
- bearing chosen only to keep focal cluster and nearby urban fabric legible.

Camera rules:
- minimum move duration 1.4 s;
- typical move 2.0–2.8 s;
- major chapter move <= 3.4 s;
- no continuous orbit;
- no bearing change > 28° in one move;
- no pitch > 50°;
- no zoom > 14.0;
- use easeInOutCubic for editorial moves;
- use easeOutCubic for focal push-ins;
- pull back before moving to a distant district when direct pan would be disorienting.

Reduced motion:
- pitch 0–15°;
- no flyTo;
- 180 ms crossfade between static camera states;
- ignition becomes opacity/radius fade without expanding halo;
- all information remains available.

## 8. KPI system

Persistent KPI rail:
- primary KPI: one large number, tabular numerals;
- two micro-KPIs maximum;
- values tween only when the semantic measure is comparable;
- when evidence tier changes, crossfade rather than tween across incompatible series.

Allowed primary KPIs:
- `今月の新規営業許可` for exact period;
- `この月に復元できた許可` for retrospective period;
- `厳密地点数` only when explaining spatial confidence;
- focal `1kmメッシュ件数` for hotspot scenes.

Supporting KPIs:
- 前月差;
- 重心移動 km;
- focal mesh count;
- active mesh count;
- evidence tier.

Do not present retrospective monthly totals with the exact-period label `今月の新規営業許可`.

## 9. Silent-first annotation motion

No scene depends on audio.

Every insight follows a four-beat visual sentence:
1. **Orient** — date and citywide field stable for >=600 ms.
2. **Cue** — a thin leader/ring or KPI change indicates where to look.
3. **Explain** — annotation appears after the visual change has begun.
4. **Resolve** — annotation fades before the next camera move.

Annotation timing:
- title enters 180–240 ms after camera deceleration begins;
- body line enters 120 ms later;
- minimum readable hold 2.2 s;
- maximum body length ~34 Japanese characters per line, 2 lines;
- use verbs such as `集中`, `再加速`, `重心が移動`, `観測方法が切り替わる`;
- avoid causal language.

Visual attention cues:
- local scene: halo → leader line → label;
- citywide scene: KPI pulse → field brightening → annotation;
- evidence transition: evidence badge morph/crossfade → sharpening → explanatory copy.

## 10. Second-by-second storyboard

### Scene 1 — 0.0–6.0 s — 2021-06 / source-boundary opening

0.0–1.0:
- black-to-map fade;
- citywide camera static;
- title: `松山｜飲食店営業許可の62か月`.

1.0–2.5:
- 2021-06 month appears;
- retrospective badge enters;
- reconstructed points ignite with subdued treatment.

2.5–4.5:
- primary KPI: `復元できた許可 202`;
- supporting: `厳密地点 60`;
- annotation: `ここからは参考復元。月次の全件ではありません`.

4.5–6.0:
- title recedes;
- long-memory layer begins;
- bridge clock starts.

Camera:
- [0.0] 132.755, 33.840, z11.0, p28, b-8
- [6.0] 132.763, 33.839, z11.2, p32, b-8

### Scene 2 — 6.0–11.5 s — 2021-08 / centroid shift

6.0–7.0:
- bridge through 2021-07;
- memory remains.

7.0–8.8:
- month reaches 2021-08;
- centroid trace appears as a short line from previous centroid.

8.8–10.5:
- KPI: `重心移動 約2.69 km`;
- annotation: `復元地点の重心が大きく移動`.

10.5–11.5:
- centroid trace fades to memory.

Camera:
- citywide only; subtle 0.8 km equivalent recenter;
- no hotspot zoom.

### Scene 3 — 11.5–17.0 s — 2022-08 / spatial reconfiguration

11.5–13.0:
- compressed bridge through 2021-09–2022-07;
- clock visibly accelerates;
- old events accumulate as faint memory.

13.0–14.8:
- 2022-08 slows;
- active-mesh field brightens.

14.8–16.2:
- KPI: `空間配置が変化`;
- micro-KPI: `strict 26地点`;
- annotation: `活動の分布が組み替わる`.

16.2–17.0:
- pull to neutral citywide.

Camera:
- [11.5] citywide z11.1
- [14.0] center 132.757,33.831 z11.6 p34
- [17.0] z11.1 p30

### Scene 4 — 17.0–23.0 s — 2024-02 / retrospective Dogo core

17.0–19.0:
- bridge through 2022-09–2024-01;
- Dogo persistent memory gradually becomes visibly brighter than surrounding field.

19.0–20.8:
- cue ring appears over Dogo;
- camera pushes in.

20.8–22.3:
- KPI: `道後｜持続する核`;
- micro: `この月 strict 48地点`;
- annotation: `参考復元期でも、道後の集積は繰り返し現れる`.

22.3–23.0:
- focal glow settles into memory.

Camera target:
- 132.78125,33.85417
- z13.2, p44, b8

### Scene 5 — 23.0–29.0 s — 2024-05 / Takehara–Fujiwara

23.0–24.2:
- pull back before lateral move.

24.2–25.8:
- clock reaches 2024-05;
- push to Takehara/Fujiwara.

25.8–28.0:
- KPI: `竹原・藤原`;
- micro: `strict 33地点`;
- annotation: `別の集積軸が浮かび、都市は一極ではない`.

28.0–29.0:
- label fades;
- camera begins pullback.

Camera target:
- 132.75625,33.82917
- z13.1, p42, b-12

### Scene 6 — 29.0–38.0 s — bridge to evidence boundary

29.0–35.5:
- compressed months 2024-06–2024-08;
- return to citywide;
- retrospective badge remains persistent;
- month clock becomes the dominant UI.

35.5–38.0:
- motion slows;
- a vertical temporal marker / subtle full-screen rule announces `2024.09`;
- existing glow dims 12% to create contrast for transition.

No claim is shown yet.

### Scene 7 — 38.0–44.5 s — 2024-09 / evidence transition + Dogo

38.0–39.2:
- evidence badge crossfades:
  `参考復元・不完全` → `完全観測・月次`;
- point cores sharpen over 700 ms.

39.2–41.2:
- exact September events ignite;
- Dogo becomes dominant;
- camera pushes to Dogo.

41.2–43.5:
- primary KPI: `新規許可 139`;
- supporting: `道後 strict 15｜前月比 +14`;
- annotation line 1: `ここから月次を完全観測`;
- annotation line 2: `道後で強い集中`.

43.5–44.5:
- optional secondary ring flashes once at Higashi-Ishii;
- micro-label: `東石井でも再浮上`.

Camera:
- citywide → 132.78125,33.85417
- z13.4, p46, b10

### Scene 8 — 44.5–50.0 s — 2024-11 / Airport–Takehara redistribution

44.5–45.5:
- pull back to z11.6.

45.5–47.2:
- advance through October to November;
- camera moves southwest.

47.2–49.2:
- KPI: `新規許可 123`;
- annotation: `集中の形が変わり、空港通・竹原側へ視線が移る`.

49.2–50.0:
- local glow resolves.

Camera target:
- 132.74375,33.82917
- z13.0, p42, b-8

### Scene 9 — 50.0–56.0 s — 2025-05 / citywide pulse

50.0–52.0:
- compressed bridge Dec–Apr;
- pull to citywide.

52.0–53.5:
- May ignition uses wider deterministic jitter, 0–260 ms;
- many simultaneous sparks across city.

53.5–55.3:
- primary KPI: `新規許可 165`;
- annotation: `局所ではなく、市全体で許可発生が強まる`.

55.3–56.0:
- one soft global luminance pulse, max +8%;
- no local zoom.

Camera:
- 132.751,33.845 z11.2 p32 b-8

### Scene 10 — 56.0–62.0 s — 2025-08 / Mitsu re-acceleration

56.0–57.3:
- advance Jun–Jul;
- pull slightly farther out before westward move.

57.3–59.0:
- camera moves to Mitsu;
- focal mesh cue.

59.0–61.2:
- primary KPI: `三津周辺 5件`;
- supporting: `直前3か月 合計1件`;
- annotation: `長く続く西の核が、静穏期から再加速`.

61.2–62.0:
- memory reveals older Mitsu events underneath new sparks.

Camera target:
- 132.71875,33.86250
- z13.3 p44 b-18

### Scene 11 — 62.0–67.5 s — 2025-12 / broad pulse

62.0–64.0:
- bridge Sep–Nov;
- return citywide.

64.0–65.2:
- December sparks ignite.

65.2–66.8:
- primary KPI: `新規許可 131`;
- annotation: `年末、再び広い範囲で発生`.

66.8–67.5:
- no hotspot claim;
- prepare for final push.

Camera:
- citywide 132.762,33.832 z11.3 p32 b-4

### Scene 12 — 67.5–75.0 s — 2026-02 / Dogo climax

67.5–68.8:
- January passes quickly;
- citywide field dims 8% except fresh events.

68.8–70.8:
- February ignition;
- centroid trace appears;
- camera pushes rapidly but smoothly toward Dogo.

70.8–73.5:
- primary KPI: `新規許可 158`;
- supporting:
  - `道後 14件｜前月比 +14`
  - `重心移動 約2.71 km`
- annotation: `完全観測期で最も強い変化。道後が再び大きく発光`.

73.5–75.0:
- Dogo glow settles;
- old Dogo memory remains clearly visible behind new events.

Camera target:
- 132.78125,33.85417
- z13.7 p48 b12

### Closing — 75.0–80.0 s — 2026-07 / end-state

75.0–76.5:
- bridge Mar–Jul; optionally show a 450 ms Yogo/Homen cue in March without stopping.

76.5–78.0:
- pull to citywide;
- all 62-month memory field visible.

78.0–79.2:
- primary KPI changes to `62か月`;
- supporting: `道後 50/62か月で活動` and `三津 47/62か月で活動`;
- annotation: `一時の点ではなく、繰り返し現れる都市の核が残る`.

79.2–80.0:
- CTA crossfade: `自分で時間を動かして見る →`;
- autoplay stops;
- Explore controls become available.

Camera:
- 132.755,33.840 z10.9 p28 b-8

## 11. Chapter transitions

Chapter titles are optional on desktop and omitted on small mobile.

If used:
- 0.8 s total;
- 160 ms fade-in;
- 480 ms hold;
- 160 ms fade-out;
- never blank the map.

Suggested labels:
- `復元された都市の記憶`
- `繰り返し現れる核`
- `観測が鮮明になる`
- `再加速する場所`
- `62か月の残像`

## 12. Mobile adaptation

Mobile is not a cropped desktop film.

Rules:
- camera target is vertically offset upward by 8–12% viewport so bottom annotation does not cover the focal area;
- zoom is 0.5–0.8 lower than desktop;
- pitch max 38°;
- annotations occupy bottom sheet <= 28vh;
- one supporting KPI only;
- locality labels shorten to 1–2 representative names;
- evidence badge remains visible at all times;
- no side-by-side KPI rail.

## 13. Typography and number motion

- use the site's Japanese sans stack; do not introduce a decorative display font solely for cinematic mode;
- month: tabular numerals, large;
- KPI: tabular numerals;
- number tween duration 350–550 ms;
- never tween retrospective total directly into exact total across 2024-09;
- annotation title 18–22 px desktop / 16–18 px mobile;
- body 13–15 px desktop / 12–14 px mobile;
- WCAG-readable contrast for all essential text.

## 14. Performance budget

Target hardware: current mid-range mobile Safari/Chrome and desktop Chromium.

Budgets:
- 60 fps target desktop; 30 fps acceptable floor mobile;
- <= 16.7 ms average render frame desktop during normal playback;
- <= 33 ms p95 mobile during glow-heavy scenes;
- no per-frame DOM creation;
- event jitter precomputed from event_id;
- point age/intensity calculated in GPU layer accessors/shaders where practical;
- maximum simultaneously animated ignition halos: 180; overflow events batch into density field;
- memory points use a single layer, not one DOM/SVG node per event;
- avoid map label relayout during camera flight;
- prefetch all cinematic JSON before play;
- first-play start <= 1.5 s after user action on broadband after page load.

Graceful degradation:
1. reduce halo blur/radius;
2. disable 3D extrusion;
3. reduce memory-point opacity updates to discrete month steps;
4. reduce pitch;
5. preserve clock, evidence badge, KPI and annotations.

## 15. Accessibility / reduced motion

`prefers-reduced-motion: reduce`:
- no fly/orbit;
- static camera cuts via 180 ms opacity crossfade;
- no breathing;
- no expanding rings;
- month progression remains user-controllable;
- annotations and KPI remain identical;
- autoplay default OFF.

Keyboard:
- Space: play/pause;
- Left/Right: previous/next authored scene;
- Esc: exit cinematic mode;
- focus indicator always visible.

Autoplay must stop when:
- tab becomes hidden;
- user opens an inspection panel;
- user enters Explore mode.

## 16. Interaction states

### Watch
- authored 80 s sequence;
- minimal chrome;
- pause/scrub available;
- “Skip to next insight” control.

### Paused Watch
- current scene remains visually stable;
- hover/tap can inspect only current focal events;
- no camera drift.

### Explore
- current analytical map;
- full filters and evidence inspection;
- user can return to Watch from current month or restart.

## 17. Truthfulness constraints

Never write:
- `店が増えた`
- `繁華街が拡大した`
- `開店した`
unless another dataset establishes those facts.

Use:
- `新規営業許可が発生`
- `許可発生地点が集中`
- `復元できた許可地点`
- `完全観測期では…`

The motion may amplify visibility but may not manufacture a spatial trajectory that is absent from the data.

## 18. Implementation handoff

Recommended components:
- `CinematicMode.tsx`: state machine and playback clock
- `cinematicTimeline.ts`: loads machine timeline
- `CinematicMapLayers.ts`: fresh, memory, hotspot, centroid layers
- `CinematicHUD.tsx`: month, evidence, KPI, annotation
- `cameraController.ts`: deterministic keyframe interpolation
- `motionMath.ts`: easing, age decay, deterministic jitter
- `useReducedMotion.ts`
- Playwright visual/interaction tests

State machine:
`idle -> intro -> bridge -> cue -> explain -> resolve -> bridge ... -> outro -> paused`

All state changes derive from elapsed cinematic time and the committed timeline JSON, not scattered setTimeout calls.

## 19. Stage 9 exit criteria

- [x] runtime fixed
- [x] second-level 12-scene sequence fixed
- [x] camera system and keyframes specified
- [x] event lifecycle fixed numerically
- [x] glow / hotspot / memory model specified
- [x] evidence-tier grammar specified
- [x] annotation timing and copy specified
- [x] KPI semantics specified
- [x] silent-first attention choreography specified
- [x] reduced-motion alternative specified
- [x] mobile framing specified
- [x] performance budget specified
- [x] truthfulness constraints retained
- [x] implementation architecture specified
- [x] machine-readable timeline + QA generated

Stage 9 is complete when the machine timeline passes QA.


---

# Stage 11 editorial revision — 2026-10-04

This section supersedes the Stage 9 scene-by-scene timing wherever the two differ. The analytical map remains unchanged.

## Editorial premise

The film now follows one continuous idea:

> 許可の記録が月ごとに重なり、道後、三津、その他の地区に、繰り返し現れるまとまりが見えてくる。

The source-method boundary is no longer a chapter or dramatic beat. It appears only as a small corner note:

- 2021-06〜2024-08：参考復元
- 2024-09〜2026-07：月次観測

There is no pause, blackout, title card, global color change, or explanatory KPI at 2024-09.

## Revised 80-second edit

| Time | Editorial block | Motion priority |
|---|---|---|
| 0–5 s | Matsuyama overview / first light | title, intuitive meaning of light |
| 5–22 s | continuous retrospective months | fast accumulation with short Dogo and Takehara inserts |
| 22–37 s | 2024-09 through spring 2025 | Dogo → Airport/Takehara → return citywide |
| 37–48 s | May 2025 | stable wide shot, 165 citywide permits, quiet read time |
| 48–56 s | Mitsu August 2025 | pull → westward move → push, then still hold |
| 56–70 s | year-end through Feb 2026 | short year-end pass; Feb citywide 158 → Dogo local 14 |
| 70–80 s | Mar–Jul 2026 / ending | return wide, Dogo + Mitsu persistence, Explore handoff |

All 62 months receive an explicit playback interval. Routine months are compressed; authored months receive longer intervals.

## Camera synchronization

Camera motion is now computed from absolute cinematic time on every animation frame. MapLibre asynchronous \`easeTo\` is not used for the film clock.

Consequences:

- pause freezes the camera and data on exactly the same frame;
- resume continues from that frame;
- keyframes between authored scenes are actually interpolated;
- distant moves can use pull → translate → push;
- scene jumps resolve deterministically to the matching camera time.

The canonical keyframes live in \`cinematic_timeline_v2.json\`.

## Point grammar

High-precision permit locations use three states:

1. **core** — small bright center;
2. **halo** — short-lived soft ignition;
3. **memory** — low-opacity residual mark.

The month-level ignition jitter is deterministic from event ID and deliberately does not encode within-month permit-date order.

Retrospective town-centroid points do not receive strong ignition. They remain a weak ambient layer. Fine hotspot claims and highlighted 1km cells use high-precision address/parcel points only.

The same high-precision symbol grammar is maintained across the 2024-09 source boundary.

## Information staging

Major beats follow:

1. establish location;
2. show point/mesh change;
3. introduce the scoped number;
4. show one short caption;
5. remove the caption and hold the map.

Major captions have at least 2.5 seconds of reading time. Camera travel is kept free of principal explanatory copy.

Bridge months emphasize the date. Local holds reduce the date and promote place + local count.

## Scope rules fixed in Stage 11

- 2024-02 Dogo: 6 high-precision events in the Dogo 1km cell. The citywide 48 strict points are not presented as a Dogo count.
- 2024-05 Takehara/Fujiwara: 4 in the same 1km/high-precision definition.
- 2024-09 Dogo: 15. No month-over-month increase is shown across the data-source boundary.
- 2024-11 Airport/Takehara: 4 in the highlighted 1km cell.
- 2025-05: Matsuyama citywide 165 total permit events; 40 high-precision points are explicitly a separate map-availability count.
- 2025-08 Mitsu: 5 in the highlighted 1km cell; the supporting comparison is “直前3か月は同じ区画で合計1件”, not a “5× increase”.
- 2025-12: Matsuyama citywide 131, shown briefly.
- 2026-02: citywide 158 first; after the camera settles on Dogo, the primary number becomes 14 for the Dogo 1km/high-precision cell.
- Final exact-period persistence: Dogo 19/23 months, Mitsu 15/23 months.

## Local comparison graphic

Mitsu and Dogo major local scenes show a compact 23-month sparkline using the identical:

- monthly observation window;
- 1km mesh;
- high-precision point definition.

It is descriptive only and does not imply shop survival.

## Mobile composition

For local scenes:

- zoom is reduced relative to desktop;
- map center is offset so the highlighted cell remains above the lower HUD;
- principal caption remains one short sentence;
- only one primary number is emphasized;
- the same focal-region vs HUD geometry is asserted in browser QA.

## Ending

The ending no longer reports 62-month activity counts as if they were directly comparable with exact monthly observation.

It shows:

- 道後 19/23か月
- 三津 15/23か月

under the label:

\`月次観測23か月・同じ1km区画・高精度地点\`

The viewer can choose Dogo or Mitsu and select:

\`この場所の時間を、自分で見る\`

The handoff opens the analytical map at the selected place and the authored reference month.
