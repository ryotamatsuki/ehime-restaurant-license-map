# Stage 12 — Cinematic Implementation QA

Date: 2026-10-05  
Status: **PASS / COMPLETE**

## Scope

Final closeout for Cinematic Mode after editorial review. This QA covers:
- rendered desktop/mobile review;
- full 80-second playback;
- all 62 source months;
- scoped KPI and local-chart semantics;
- MapLibre/GSI attribution placement;
- regression against Explore mode;
- GitHub Pages build/deploy/public smoke test.

## Final code change

PR: #11 `Stage 12 final QA: avoid attribution overlap`

Application commit:
- `aa2419fea5ca218a0c6cd52e3a4678dd0b8f9e33`

Generated build/audit commit:
- `82674a7e9355ddb5ea3386dd486aec38da73e2f6`

The final visual review found one remaining layout defect: the compact MapLibre/GSI attribution control crossed the cinematic closing card near 78 seconds. The fix keeps attribution visible but moves the control to the upper-right safe area during Cinematic Mode. A regression assertion now checks that the attribution container and `#cinematic-final` do not intersect at the exact 78-second frame in both desktop and mobile viewport runs.

## Browser and build QA

Workflow:
- Stage 6 build and test time map
- run: **37258027663**
- result: **SUCCESS**
- Browser QA: **8 passed (3.4m)**
- no flaky/retry summary in the final run

Build/audit verified:
- cinematic runtime: **80 seconds**
- month schedule: **62**
- first month: **2021-06**
- last month: **2026-07**
- Dogo exact-active months: **19**
- Mitsu exact-active months: **15**
- 2025-05 Matsuyama citywide: **165**
- 2026-02 Dogo 1km/high-precision: **14**

## Full-playback artifact

Artifact:
- name: `cinematic-playback`
- id: **11323826318**
- source run: **37258027663**
- retention: through 2026-10-12

Final telemetry extracted from the artifact:
- desktop: 81 samples, elapsed 79.999, final month 2026-07, seen months **62/62**
- mobile: 81 samples, elapsed 79.999, final month 2026-07, seen months **62/62**

Recorded video container durations include Playwright setup/teardown:
- desktop: approximately **86.68 s**
- mobile: approximately **85.04 s**

Exact rendered frames reviewed:
- 2 s: opening
- 25 s: early authored hold
- 40 s: 2025-05 citywide
- 51 s: Mitsu
- 62 s: 2026-02 Matsuyama-wide 158
- 66 s: Dogo 14
- 78 s: closing comparison and Explore handoff

The 78-second desktop and mobile frames confirm the attribution control is visible and no longer overlaps the closing card.

## Public deployment

Workflow:
- Deploy GitHub Pages
- run: **37258027646**
- result: **SUCCESS**

Jobs:
- build: SUCCESS
- deploy: SUCCESS
- public URL smoke-test: SUCCESS

The smoke test confirms the public HTML and generated cinematic JSON assets are reachable from the deployed Pages environment and checks the 62-month / 80-second timeline plus Dogo/Mitsu and selected numeric values.

An additional fetch from the assistant's general web/container network could not resolve the GitHub Pages hostname in this session. Therefore the public availability claim is grounded in the Pages deployment job's own successful network smoke test, not a second independent network path.

## Final visual assessment

Desktop and mobile frames were inspected, not only test assertions.

PASS:
- first frame identifies the subject as permit records;
- current-month points remain visually dominant over map context;
- 2025-05 separates citywide total 165 from 40 map-visible high-precision points;
- Mitsu uses the same 1km/high-precision definition for KPI, highlight and chart;
- 2026-02 correctly separates Matsuyama-wide 158 from Dogo-local 14;
- Dogo's 14-point local scene aligns with its 1km cell and local chart;
- ending explains 19/23 and 15/23 as months with permit records in the same 1km/high-precision scope;
- attribution remains visible without covering the final CTA.

No further application changes are required for Stage 12 closeout.

## Known constraint

Physical iPhone hardware was not available. The project therefore does **not** claim an iPhone-device PASS. Mobile verification is real Chromium rendering at 390×844 with full 80-second playback, exact-frame screenshots and overlap regression checks.

Stage 12 is closed with this constraint explicitly recorded.
