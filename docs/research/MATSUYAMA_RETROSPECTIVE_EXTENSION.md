# Matsuyama retrospective timeline extension

Date: 2026-10-04  
Status: **DEPLOYED**

## Why this extension exists

The exact Matsuyama monthly source provides a strong continuous window from 2024-09 through 2026-07, but 23 months alone produces a relatively short animation.

A later Matsuyama all-facilities snapshot dated 2026-03-31 contains `initial_permit_date` for facilities licensed under the post-June-2021 framework. These dates can be backcast to create a longer, explicitly incomplete historical reference series.

## Retrospective period

Reference reconstruction:

- 2021-06 through 2024-08
- 39 months
- 3,743 restaurant-permit rows
- about 3,703 unique facility names
- source address present on all 3,743 rows

After geocoding:

- address/parcel level: 1,041
- town-or-better: 3,574
- municipality centroid only: 169
- invalid Matsuyama coordinates: 0

The public map displays the 3,574 town-or-better records during this retrospective period.

## Hybrid timeline

The public Matsuyama monthly animation now spans:

**2021-06 through 2026-07: 62 consecutive months**

Evidence changes at the boundary:

- 2021-06 through 2024-08: `参考復元・不完全`
- 2024-09 through 2026-07: `完全観測 月次`

The reference period is visually and textually distinguished in the application.

## Interpretation

The retrospective series is **not** a complete archive of all new permits that occurred in those months.

It is reconstructed from facilities present in the 2026-03-31 all-facilities snapshot and backdated using their initial permit date. Therefore it is subject to survivor/carry-forward bias: facilities that disappeared from the later snapshot may be absent.

Accordingly:

- exact monthly counts and retrospective counts are never labeled the same way;
- the coverage badge changes to `参考復元・不完全`;
- the main metric label becomes `参考復元件数`;
- town-centroid coordinates are allowed only in this explicitly approximate retrospective visualization;
- fine 1km/500m mesh modes remain disabled during the retrospective period;
- rolling-12 indicators remain based only on complete exact monthly data.

## Public QA

Public URL:

https://ryotamatsuki.github.io/ehime-restaurant-license-map/

Deployment smoke test verifies:

- manifest schema version 2
- 23 exact Matsuyama months
- 39 retrospective Matsuyama months
- 62 hybrid Matsuyama months
- 12 valid exact rolling-12 endpoints
- 800+ exact strict events
- 3,500+ retrospective visible events

Final public Pages data QA: **PASS**.
