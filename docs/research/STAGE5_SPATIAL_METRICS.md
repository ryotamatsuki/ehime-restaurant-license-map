# Stage 5 — Spatial and temporal indicators

Date: 2026-10-04  
Status: **PASS / COMPLETE**

## Objective

Convert the Stage 4 geocoded permit-event panel into reproducible spatial and temporal indicators that can be used directly by the interactive visualization.

The analysis target is **new restaurant permits** only. Renewal permits are excluded from location-change indicators so that renewal activity is not mistaken for newly appearing locations.

Input:

- \`data/processed/restaurant_permit_events_geocoded.csv\`
- 3,300 exact restaurant permit events
- 3,088 events classified as \`new\`

## Spatial precision rules

Stage 5 inherits the Stage 4 location-quality flags.

### Municipality-level counts

All exact new restaurant events with a resolved municipality code may be used.

### Fine spatial indicators

1km / 500m mesh counts, rolling hotspots and strict point layers use only:

- \`map_usable_strict == true\`
- Stage 4 quality \`address_or_parcel\`

This avoids placing facilities at a town or municipality centroid and then treating that representative point as an exact restaurant location.

### Centroid movement

Two separate series are produced:

- \`strict_address_or_parcel\`
- \`town_or_better\`

The precision scope is always explicit in the output.

## Standard regional mesh

The project uses the Statistics Bureau of Japan standard regional mesh system.

- 3rd-level / basic regional mesh: approximately 1 km square
- 1/2 regional mesh: approximately 500 m square
- 500m subcells append 1–4 in the official SW, SE, NW, NE order

References:

- https://www.stat.go.jp/data/mesh/m_tuite.html
- https://www.stat.go.jp/data/mesh/pdf/gaiyo1.pdf

Mesh codes and cell bounds are calculated directly from latitude/longitude in the repository. No external GIS service is needed for mesh assignment.

## Municipality monthly panel

Output:

- \`data/processed/spatial/municipality_monthly_new_restaurants.csv\`

Rows are generated for every municipality covered by every exact monthly source, including zero-count municipality-month combinations.

Result:

- 137 municipality × month rows

Composition:

- Ehime Prefecture source: 6 exact months × 19 municipalities excluding Matsuyama = 114 rows
- Matsuyama source: 23 exact months × Matsuyama = 23 rows

This panel is appropriate for municipality-level time-series comparison within the exact coverage windows.

## Matsuyama fine spatial analysis

Matsuyama has 23 consecutive exact monthly observations:

**2024-09 through 2026-07**

New restaurant permit events in those months:

- 2,281 total
- 586 address/parcel-level events used for strict fine spatial analysis

The difference is intentional: lower-precision town/municipality centroids are not silently inserted into the fine mesh layer.

## Monthly mesh outputs

### 1 km

- 391 non-zero month × mesh rows
- \`matsuyama_mesh_1km_monthly.csv\`
- \`matsuyama_mesh_1km_monthly.geojson\`

### 500 m

- 461 non-zero month × mesh rows
- \`matsuyama_mesh_500m_monthly.csv\`
- \`matsuyama_mesh_500m_monthly.geojson\`

Each GeoJSON feature includes its mesh polygon and month-level new-permit count.

## Rolling 12-month metrics

A rolling 12-month value is emitted only when **all 12 constituent months are classified \`complete_exact_monthly\`**.

Matsuyama has 12 valid rolling windows:

- 2024-09–2025-08
- 2024-10–2025-09
- …
- 2025-08–2026-07

Outputs:

- 1km rolling: 755 active mesh-window rows
- 500m rolling: 1,495 active mesh-window rows
- CSV and GeoJSON are both generated

No rolling-12 indicator is generated for the discontinuous Ehime-prefecture historical window.

## Hotspot representation

For each valid rolling-12 window, active 1km meshes are ranked by strict new restaurant permit count.

Fields include:

- \`new_restaurant_permits_12m\`
- \`active_mesh_rank\`
- \`active_mesh_percentile\`
- \`active_mesh_zscore\`
- \`hotspot_class\`

Classes:

- \`top_5pct_active\`
- \`top_20pct_active\`
- \`other_active\`

Important: the z-score and percentile are **descriptive measures among active meshes**. They are not Getis-Ord Gi*, Moran's I or inferential statistical significance tests.

The top-10 extract is:

- \`matsuyama_hotspot_top10_1km_rolling12.csv\`

During all 12 valid rolling windows, mesh \`50326622\` is ranked first. Its rolling strict new-permit count ranges from 32 to 45 in the audited windows. This is a descriptive concentration result; Stage 6 should show the mesh geographically rather than assign a neighborhood name by inference.

## Spatial centroid movement

Output:

- \`matsuyama_spatial_centroid_monthly.csv\`
- \`matsuyama_spatial_centroid_monthly.geojson\`

Two precision scopes × 23 months produce 46 rows.

Movement distance is calculated with the haversine formula only when the previous calendar month is present. No movement value bridges a missing month.

The strict centroid series shows month-to-month shifts typically below several kilometres; these values describe the center of observed new-permit points, not movement of individual businesses.

## Spatial concentration indicators

Output:

- \`matsuyama_monthly_spatial_concentration.csv\`

For each of the 23 complete Matsuyama months, the strict 1km mesh distribution includes:

- number of strict new permits
- active 1km mesh count
- top-mesh share
- 1km HHI
- normalized entropy

These allow the visualization to distinguish a month with many spatially dispersed permits from a month dominated by a small number of cells.

## Visualization-ready point layer

Output:

- \`matsuyama_new_restaurant_points_strict.geojson\`

This contains the 586 strict new restaurant permit points and is suitable for direct use in MapLibre/deck.gl.

Lower-precision town-centroid records remain available in the Stage 4 CSV but are not mixed into this strict point layer.

## Historical Ehime limitation

The 2021-12 through 2022-04 prefectural archive mostly supplies municipality-level addresses only.

Therefore these months are valid for:

- municipality monthly counts

but not for:

- 1km / 500m restaurant-location meshes
- fine-grained hotspot analysis
- within-municipality spatial centroid movement

Stage 5 does not create artificial fine spatial detail from those records.

## Canonical outputs

- \`data/processed/spatial/municipality_monthly_new_restaurants.csv\`
- \`data/processed/spatial/matsuyama_mesh_1km_monthly.csv\`
- \`data/processed/spatial/matsuyama_mesh_1km_monthly.geojson\`
- \`data/processed/spatial/matsuyama_mesh_500m_monthly.csv\`
- \`data/processed/spatial/matsuyama_mesh_500m_monthly.geojson\`
- \`data/processed/spatial/matsuyama_mesh_1km_rolling12.csv\`
- \`data/processed/spatial/matsuyama_mesh_1km_rolling12.geojson\`
- \`data/processed/spatial/matsuyama_mesh_500m_rolling12.csv\`
- \`data/processed/spatial/matsuyama_mesh_500m_rolling12.geojson\`
- \`data/processed/spatial/matsuyama_hotspot_top10_1km_rolling12.csv\`
- \`data/processed/spatial/matsuyama_spatial_centroid_monthly.csv\`
- \`data/processed/spatial/matsuyama_spatial_centroid_monthly.geojson\`
- \`data/processed/spatial/matsuyama_monthly_spatial_concentration.csv\`
- \`data/processed/spatial/matsuyama_new_restaurant_points_strict.geojson\`
- \`docs/research/STAGE5_SPATIAL_METRICS_AUDIT.json\`
- \`src/spatial/build_spatial_metrics.py\`
- \`.github/workflows/stage5-spatial.yml\`

## Stage 5 exit criteria

- [x] monthly new-permit counts
- [x] coverage-aware rolling 12-month counts
- [x] municipality aggregation
- [x] official-standard 1km mesh aggregation
- [x] official-standard 500m mesh aggregation
- [x] descriptive hotspot representation
- [x] spatial centroid movement
- [x] concentration indicators
- [x] visualization-ready GeoJSON
- [x] low-precision coordinates excluded from fine spatial analysis
- [x] no rolling window crosses incomplete months
- [x] reproducible GitHub Actions build

Stage 5 is complete.

Stage 6 can now consume these outputs directly to implement the interactive map, time slider, autoplay, point/mesh modes, rolling-12 hotspot mode and precision/coverage indicators.
