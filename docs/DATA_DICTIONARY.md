# Canonical data dictionary

| Field | Meaning | Notes |
|---|---|---|
| `source_authority` | Publishing authority | 愛媛県 / 松山市 |
| `source_snapshot_date` | Source snapshot/month | Provenance field |
| `permit_number` | Published permit number | **Not globally or temporally unique** |
| `initial_permit_date` | First permit date when supplied | Useful for new/renewal derivation in Matsuyama |
| `permit_date` | Permit date represented by source record | Source-specific semantics documented in audit |
| `permit_expiry_date` | Permit expiry date | Not a closure date |
| `business_type` | Licensed business category | Main target is 飲食店営業 |
| `facility_name` | Facility/trade name | Source field, not applicant identity |
| `facility_address` | Facility location address | May be coarse or missing; never silently infer missing address |
| `municipality_code` | Location municipality code | Present in Matsuyama standard schema |
| `town_id` | Town/block ID | Field exists in Matsuyama source; currently often blank |
| `latitude` | Source-provided latitude | Current Matsuyama source field exists but values are blank |
| `longitude` | Source-provided longitude | Current Matsuyama source field exists but values are blank |
| `application_type` | Source application category | Current Matsuyama source field exists but values are blank |
| `record_scope` | Source record class | new / new_or_renewal / all |
| `source_url` | Exact official source URL | Provenance |
| `source_sha256` | SHA-256 of downloaded official file | Reproducibility |

## Planned derived fields

These are not source fields and must be marked as derived.

| Field | Planned derivation |
|---|---|
| `event_type` | Matsuyama: compare initial permit date to current permit date; Ehime monthly sheet is source-labeled new |
| `event_id` | Deterministic hash of authority + date + permit number + business type + facility identity/location, followed by collision QA |
| `normalized_address` | Stage 4 address normalization |
| `geocode_latitude`, `geocode_longitude` | Stage 4 geocoding result |
| `geocode_quality` | exact / interpolated or coarse / failed, according to selected geocoder capabilities |
