# Stage 4 — Address normalization and geocoding

Date: 2026-10-04  
Status: **PASS / COMPLETE**

## Objective

Attach reproducible spatial coordinates and explicit location-quality metadata to the exact Stage 3 permit-event panel without silently inventing facility locations.

Input:

- \`data/processed/permit_events_observed.csv\`
- 4,240 exact observed permit events
- 3,300 events classified as \`飲食店営業\`

## Method

Primary normalizer/geocoder:

- \`@geolonia/normalize-japanese-addresses\`
- pinned version: **3.1.3**
- coordinate system: EPSG:4326
- address-data endpoint: \`https://japanese-addresses-v2.geoloniamaps.com/api/ja\`

Repository:

- https://github.com/geolonia/normalize-japanese-addresses
- https://github.com/geolonia/japanese-addresses

The normalizer returns both an address-normalization level and a coordinate point level. Stage 4 preserves these values instead of collapsing every returned coordinate into an "exact point."

The Geolonia source code is MIT licensed. Geolonia address data are CC BY 4.0 and are derived from public address/location sources including MLIT position-reference information and address data related to the Digital Agency Address Base Registry.

Digital Agency Address Base Registry:

- https://www.digital.go.jp/policies/base_registry_address

## Reproducibility

The Node dependency is pinned in \`package.json\` and \`package-lock.json\`.

The pipeline:

1. reads the Stage 3 event panel;
2. normalizes source address strings with Unicode NFKC;
3. prefixes \`愛媛県\` when the source omits the prefecture;
4. deduplicates identical addresses before geocoding;
5. geocodes each unique address;
6. stores the response in \`data/geocode/geocode_cache.json\`;
7. joins the cached result back to all event rows;
8. assigns quality flags;
9. checks coordinates against a broad Ehime bounding box;
10. writes machine-readable QA.

There are **2,564 unique non-empty source addresses** in the 4,240-event exact panel.

Cached results mean later runs do not need to geocode unchanged addresses again.

## Municipality codes

The output retains a source-provided municipality code when one exists.

When the source lacks a municipality code, Stage 4 derives it only when the normalized municipality name matches one of the 20 current Ehime municipalities. The mapping uses the official six-digit local-government codes published by Ehime Prefecture.

No municipality is inferred when the source address contains no municipality information.

Final resolution:

- 4,228 / 4,240 events: municipality code resolved (**99.72%**)
- unresolved: 12 events
  - 11 events have no source facility address
  - 1 source address is \`愛媛県一円\`, which identifies no municipality

These 12 rows are deliberately left unresolved.

## Coordinate quality model

### \`address_or_parcel\`

\`point_level >= 8\`.

Interpretation: address/parcel-level point according to the geocoder's source data. This is the only class automatically eligible for **strict facility point-map display**.

### \`town_centroid\`

\`point_level == 3\`.

Interpretation: town / aza / chome representative point.

This may be used for aggregated or contextual spatial analysis but must not be presented as the exact facility coordinate.

### \`municipality_centroid\`

\`point_level == 2\`.

Interpretation: municipality representative point.

Retained for provenance and municipality-level aggregation only. Excluded from point maps.

### \`prefecture_centroid\`

\`point_level == 1\`.

Excluded from facility point maps.

The only such record in Stage 4 has source location \`愛媛県一円\`.

### \`no_source_address\`

The official source itself has an empty \`facility_address\`.

No coordinate is guessed.

## Results — all permit events

4,240 rows:

- any coordinate: **4,229 (99.74%)**
- address/parcel level: **904 (21.32%)**
- town-or-better: **2,937 (69.27%)**
- municipality centroid: 1,291
- no source address: 11
- prefecture centroid: 1
- coordinates outside broad Ehime bounds: **0**

## Results — restaurant permits

3,300 \`飲食店営業\` events:

- any coordinate: **3,290 (99.70%)**
- address/parcel level: **661 (20.03%)**
- town-or-better: **2,400 (72.73%)**
- municipality centroid: 889
- no source address: 10
- prefecture centroid: 1

## Important authority/source asymmetry

### Matsuyama City

3,018 exact events:

- any coordinate: **100%**
- town-or-better: **95.92%**
- address/parcel level: **29.06%**
- municipality-code resolution: **100%**

This is suitable for neighborhood-scale aggregation and time animation, provided point-level displays respect the precision flag.

### Ehime Prefecture archive, 2021-12 through 2022-04

The old prefectural monthly source often contains only municipality-level facility location, e.g.:

- \`今治市\`
- \`西条市\`
- \`上浮穴郡久万高原町\`

Consequently the archived monthly records have:

- 1,165 events with a returned coordinate
- 1,164 municipality-centroid points
- 1 prefecture-centroid point
- **0 town-or-better points**

This is a limitation of the historical source itself, not a geocoding failure.

These months may support municipality-level monthly counts but **must not be visualized as facility-point movement within municipalities**.

### Current Ehime monthly source, 2026-08

57 events:

- 46 have a coordinate
- 27 address/parcel level
- 15 town centroid
- 4 municipality centroid
- 11 source addresses missing

## Why no Jageocoder bulk fallback in Stage 4

Jageocoder is capable and can provide detailed Japanese address matching, but the current nationwide local dictionary requires more than 20 GB of installed storage, while its public server is explicitly a demonstration endpoint with traffic limits and is not intended for bulk production processing.

For this repository's reproducible GitHub Actions workflow, a pinned Geolonia normalizer plus committed geocode cache is the better operational baseline.

A future precision-improvement experiment may compare a self-hosted Jageocoder or another authoritative geocoder against the currently low-precision rows, but such a comparison is not required to distinguish known precision from unknown precision.

## Canonical outputs

- \`data/geocode/geocode_input.json\`
- \`data/geocode/geocode_cache.json\`
- \`data/processed/permit_events_geocoded.csv\`
- \`data/processed/restaurant_permit_events_geocoded.csv\`
- \`docs/research/STAGE4_GEOCODING_AUDIT.json\`
- \`package.json\`
- \`package-lock.json\`
- \`src/geocode/\`
- \`.github/workflows/stage4-geocode.yml\`

## Stage 4 exit criteria

- [x] Japanese address normalization pipeline
- [x] fixed geocoder/version/source
- [x] coordinates attached where source address permits
- [x] municipality codes retained/derived without silent guessing
- [x] coarse matches explicitly flagged
- [x] missing source addresses explicitly flagged
- [x] coordinate bounds QA
- [x] precision and success rates audited
- [x] original source address remains in output
- [x] geocoding cache committed for reproducibility
- [x] no municipality/town/address coordinate silently invented

Stage 4 is complete.

Stage 5 must use \`geocode_quality\`, \`map_usable_strict\`, and \`map_usable_town_or_better\` explicitly when constructing spatial indicators.
