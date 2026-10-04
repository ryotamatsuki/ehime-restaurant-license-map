# Stage 7 — GitHub Pages publication and public QA

Date: 2026-10-04  
Status: **PASS / COMPLETE**

## Public site

https://ryotamatsuki.github.io/ehime-restaurant-license-map/

## Deployment

GitHub Pages is configured to deploy from GitHub Actions.

Workflow:

- `.github/workflows/deploy-pages.yml`

The deployment workflow:

1. checks out `main`
2. installs Python and Node dependencies
3. runs `npm run build:web`
4. configures GitHub Pages
5. uploads `dist/` as the Pages artifact
6. deploys with `actions/deploy-pages`
7. performs public-URL smoke tests

The workflow runs automatically when relevant application/data/build files change on `main`, and can also be dispatched manually.

## Public URL QA

The deployed URL returned by GitHub Pages is:

`https://ryotamatsuki.github.io/ehime-restaurant-license-map/`

The deploy job successfully fetched the public HTML after deployment.

The strengthened public smoke test also verifies the deployed:

- `data/manifest.json`
- manifest schema version = 1
- Matsuyama exact months = 23
- rolling-12 valid endpoints = 12
- strict new-event count >= 800

Final public deployment workflow: **PASS**.

## Application QA carried forward from Stage 6

The production application is already tested with Playwright/Chromium at:

- desktop viewport 1440 × 900
- mobile viewport 390 × 844

Browser QA covers:

- MapLibre canvas render
- default municipality / business filter
- Points
- Heatmap
- Hexagon
- 1km mesh
- rolling-12 mode
- time slider
- autoplay
- no JavaScript page errors

## Attribution and methodological caveats

The public application contains:

- GSI tile attribution
- link back to the GitHub methodology repository
- explicit statement that permit events are not exact shop opening/closure dates
- explicit statement that Points / Heatmap / Hexagon use high-precision address/parcel points only
- explicit warning that 2021–2022 prefectural historical data are mostly municipality-level and are not rendered as invented facility locations
- explicit rolling-12 completeness rule

## Build size

The audited production bundle is approximately 4.65 MB excluding browser cache/network compression behavior.

The largest JavaScript bundle remains approximately 1.7 MB minified before transfer compression. This is acceptable for the current research PoC, but route/layer-level lazy loading would be the next optimization if the public site expands materially.

## Stage 7 exit criteria

- [x] GitHub Pages enabled
- [x] GitHub Actions deployment workflow
- [x] production build deployed from `main`
- [x] stable public URL
- [x] public HTML smoke test
- [x] public data-manifest smoke test
- [x] provenance / source attribution
- [x] caveat: permit event != exact opening/closure
- [x] location-precision caveat
- [x] mobile browser QA
- [x] desktop browser QA
- [x] production build-size check
- [x] reproducible deployment

Stage 7 is complete. The original Stage 0–7 project plan is fully closed.
