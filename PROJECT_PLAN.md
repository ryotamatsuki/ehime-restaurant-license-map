# Project plan

## Research question

愛媛県において、食品営業許可、とりわけ「飲食店営業」の新規許可地点は時間とともにどのように変化してきたか。どの都市・中心市街地・郊外・交通結節点で新規許可の集積が強まり、また弱まったか。

## Stage 0 — Repository / data governance

### Tasks
- repository layout
- source attribution and license records
- public-repository privacy rule
- raw/source snapshot policy
- terminology rule: permit event ≠ opening / closure

### Exit criteria
- README, plan, source config, acquisition script, audit script are committed.
- unnecessary direct identifiers are excluded from committed datasets.

## Stage 1 — Source discovery

### Tasks
- identify canonical Ehime Prefecture dataset/API
- identify canonical Matsuyama new/renewal dataset
- identify canonical Matsuyama all-facilities dataset
- confirm update frequency, coverage, license, and caveats
- investigate historical URL/resource retention

### Exit criteria
- every source has a canonical landing URL and machine retrieval method or a documented blocker.
- historical availability is classified as `available`, `partially recoverable`, or `not yet verified`.

## Stage 2 — Acquisition & schema audit

### Tasks
- retrieve current files
- calculate SHA-256
- enumerate workbook sheets / CSV encodings
- map source columns to canonical columns
- count rows, duplicates, missing dates/addresses
- extract only analytically necessary columns into Git-managed snapshots
- generate machine-readable audit report

### Canonical minimum schema
- `source_authority`
- `source_snapshot_date`
- `permit_number`
- `permit_date`
- `permit_expiry_date`
- `business_type`
- `facility_name`
- `facility_address`
- `record_scope`
- `source_url`
- `source_sha256`

### Exit criteria
- current Prefecture and Matsuyama sources can be reproduced from scripts.
- source-specific schemas are documented.
- sanitized snapshots contain no applicant name, applicant kana, or phone number.

## Stage 3 — Historical reconstruction

**Status: COMPLETE (2026-10-04)**

### Tasks
- enumerate retained Ehime resource revisions and indexed historical previews
- search archived/current Matsuyama monthly files
- deduplicate permit events
- distinguish new vs renewal where source supports it
- construct monthly event panel
- coverage matrix by month × authority

### Exit criteria
- [x] exact recoverable time window is proven.
- [x] each month has a completeness flag.
- [x] no interpolation is silently treated as observed data.

See `docs/research/STAGE3_HISTORICAL_RECONSTRUCTION.md` and `data/processed/coverage_matrix.csv`.

## Stage 4 — Address normalization / geocoding

**Status: COMPLETE (2026-10-04)**

### Tasks
- normalize Japanese address strings
- geocode using reproducible public geocoder/address base
- detect failures / coarse matches
- attach municipal code and quality level

### Exit criteria
- [x] geocoding success and uncertainty are quantified.
- [x] original address remains traceable in sanitized form.
- [x] low-precision representative points are separated from strict facility points.
- [x] municipality codes are retained or derived only where supportable.

See `docs/research/STAGE4_GEOCODING.md` and `docs/research/STAGE4_GEOCODING_AUDIT.json`.

## Stage 5 — Spatial metrics

**Status: COMPLETE (2026-10-04)**

Generate:
- monthly new permits by municipality
- 500 m / 1 km mesh counts
- hexbin density
- kernel density / hotspot surfaces
- rolling 12-month counts
- spatial centroid / center-of-gravity movement

Potential secondary analyses:
- Matsuyama central shopping street vacant-store rate
- pedestrian counts
- station-area redevelopment periods

Completed outputs include municipality-month counts, standard 1km/500m mesh series, coverage-aware rolling-12 metrics, descriptive hotspot ranks, centroid movement, concentration statistics and GeoJSON layers.

See `docs/research/STAGE5_SPATIAL_METRICS.md`.

## Stage 6 — Interactive visualization

**Status: COMPLETE (2026-10-04)**

Target stack:
- static hosting: GitHub Pages
- map: MapLibre GL JS
- dense rendering: deck.gl
- data: GeoJSON for light layers; Parquet/Arrow if scale requires it

Core interactions:
- [x] month slider + autoplay
- [x] new-permit point display
- [x] Points / Heatmap / Hexagon
- [x] 1km / 500m standard mesh modes
- [x] business-type filter
- [x] municipality filter
- [x] monthly vs rolling-12-month toggle
- [x] source/coverage indicator
- [x] responsive mobile/desktop UI
- [x] production build and Playwright browser QA

See `docs/research/STAGE6_INTERACTIVE_MAP.md`.

## Stage 7 — Publication / QA

- build reproducibly in GitHub Actions
- publish to GitHub Pages
- accessibility and mobile check
- data attribution / caveats
- performance budget
- provenance links to each snapshot


Stage 7 public URL: https://ryotamatsuki.github.io/ehime-restaurant-license-map/

See `docs/research/STAGE7_PUBLICATION_QA.md`.
