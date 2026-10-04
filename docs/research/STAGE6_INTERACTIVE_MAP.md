# Stage 6 — Interactive time-map visualization

Date: 2026-10-04  
Status: **PASS / COMPLETE**

## Objective

Build the core interactive exploratory map for the Ehime restaurant-permit project using the Stage 3–5 audited data, while preserving coverage and geocoding-quality limitations in the UI.

This stage implements the application itself. Public deployment to GitHub Pages belongs to Stage 7.

## Technology

Pinned frontend stack:

- MapLibre GL JS **6.11.2**
- deck.gl **9.4.0**
- @deck.gl/maplibre **9.4.0**
- Vite **8.3.2**
- Playwright **1.63.0**
- Node.js 24 in CI

MapLibre provides the synchronized base map and navigation controls. deck.gl provides high-performance Points, Heatmap and Hexagon aggregation layers as well as GeoJSON mesh rendering.

The base map uses GSI pale raster tiles and displays GSI attribution.

## Web data preparation

The browser does not load the full research/audit tables.

`src/web/prepare_web_data.py` creates compact public assets under `web/public/data/`.

Prepared assets include:

- high-precision new permit points
- coverage metadata
- municipality-month restaurant counts
- 1km monthly mesh GeoJSON
- 500m monthly mesh GeoJSON
- 1km rolling-12 GeoJSON
- 500m rolling-12 GeoJSON
- centroid GeoJSON
- manifest / filter metadata

The web point dataset contains **822 exact new permit events** with Stage 4 `address_or_parcel` coordinates across **20 business-type categories**.

Restaurant permits remain the default filter.

## Core interaction

### Municipality filter

All 20 current Ehime municipalities are available.

Coverage is authority-aware:

- Matsuyama uses the 23-month exact Matsuyama window.
- Other municipalities use the six exact Ehime-prefecture months.

Selecting a fine mesh mode automatically changes the scope to Matsuyama because Stage 5 fine spatial meshes are only methodologically valid there.

### Business-type filter

The strict point dataset supports 20 normalized business categories, including:

- 飲食店営業
- 菓子製造業
- そうざい製造業
- 魚介類販売業
- 食肉販売業
- アイスクリーム類製造業
- みそ又はしょうゆ製造業
- etc.

The normalization logic removes only actual Unicode circled-number category prefixes. A QA pass caught and fixed an earlier over-broad Unicode range before Stage 6 closure.

Fine mesh layers are restaurant-only and disable the business-type selector accordingly.

### Visualization modes

Implemented:

- Points
- Heatmap
- Hexagon
- 1km standard mesh
- 500m standard mesh

Points, Heatmap and Hexagon use only high-precision `address_or_parcel` events.

1km/500m modes use the Stage 5 strict restaurant mesh outputs.

### Monthly / rolling 12-month toggle

Monthly mode uses exact month-level observations.

Rolling-12 mode is enabled only for Matsuyama, where 12 complete consecutive monthly windows can be proven.

Valid rolling endpoints:

- 2025-08 through 2026-07

No rolling indicator crosses an incomplete month.

### Time slider and autoplay

The slider is coverage-aware rather than a generic continuous calendar slider.

For Matsuyama it traverses the 23 exact months from 2024-09 through 2026-07.

For other municipalities it traverses only the six exact prefectural months:

- 2021-12
- 2022-01
- 2022-02
- 2022-03
- 2022-04
- 2026-08

Autoplay advances through these valid observation months.

### Coverage indicator

The header visibly distinguishes:

- complete exact monthly observation
- complete rolling-12 window
- partial retrospective / unavailable states where applicable

The application does not present absent historical detail as zero.

### Metrics

The control panel displays:

- total new restaurant permits for the selected municipality/period when valid
- count of high-precision plotted points
- displayed mesh-cell count or period length

## Precision handling

The visualization follows Stage 4/5 quality rules.

Fine spatial layers never use:

- municipality centroids
- prefecture centroids
- missing-address records

This is especially important for the old 2021–2022 Ehime archive, where most source addresses contain only municipality names.

Those records remain usable in municipality-level counts but are not rendered as invented facility locations.

## Responsive/mobile UI

Desktop:

- fixed control panel + map workspace
- map navigation controls
- compact research/status header

Mobile:

- full map background
- bottom control sheet
- reduced secondary explanatory content
- touch-sized controls
- timeline and playback remain accessible

## Production build

The Stage 6 workflow runs:

1. Python web-data preparation
2. pinned npm dependency install
3. Vite production build
4. static-data/build audit
5. Chromium install
6. Playwright desktop browser test
7. Playwright mobile browser test
8. generated asset and lockfile commit

Final production build:

- 22 output files
- approximately **4.65 MB** total
- no missing public data files

Source maps were removed from the production bundle after QA to reduce deployment size.

## Browser QA

Automated Playwright tests run against the built application, not the dev source.

Desktop QA verifies:

- title renders
- MapLibre canvas renders
- exact-coverage badge renders
- Matsuyama default
- restaurant default filter
- Heatmap switch
- Hexagon switch
- 1km mesh switch
- rolling-12 switch
- time slider operation
- no JavaScript page errors

Mobile QA verifies:

- MapLibre map renders at 390 × 844
- control sheet remains visible
- municipality selector remains usable
- time slider remains usable
- autoplay can start and stop
- no JavaScript page errors

Final workflow result: **PASS**.

## Versioned application files

- `web/index.html`
- `web/src/main.js`
- `web/src/style.css`
- `src/web/prepare_web_data.py`
- `src/web/audit_web_build.py`
- `web/public/data/`
- `vite.config.js`
- `playwright.config.js`
- `tests/stage6.spec.js`
- `.github/workflows/stage6-web.yml`
- `package.json`
- `package-lock.json`
- `docs/research/STAGE6_BUILD_AUDIT.json`

## Stage 6 exit criteria

- [x] MapLibre GL JS base map
- [x] deck.gl MapLibre integration
- [x] time slider
- [x] autoplay
- [x] new-permit Points
- [x] Heatmap
- [x] Hexagon
- [x] 1km mesh
- [x] 500m mesh
- [x] business-type filter
- [x] municipality filter
- [x] monthly / rolling-12 toggle
- [x] visible data-coverage indicator
- [x] source/methodology attribution
- [x] low-precision locations excluded from facility-point layers
- [x] mobile layout
- [x] desktop layout
- [x] production build
- [x] automated desktop browser QA
- [x] automated mobile browser QA

Stage 6 is complete.

Stage 7 should deploy the existing production build reproducibly to GitHub Pages and perform final public-URL, attribution, accessibility and performance QA.
