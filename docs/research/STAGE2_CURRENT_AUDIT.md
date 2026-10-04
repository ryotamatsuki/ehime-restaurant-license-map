# Stage 2 — Current-data acquisition and schema audit

Date: 2026-10-04

## Result

Stage 2 current-source acquisition is reproducible through `src/acquire/current.py` and the GitHub Actions workflow `Refresh current permit snapshots`.

The workflow downloads official source files, records SHA-256, parses their actual schema, drops direct applicant/contact identifiers, and commits only the analytical snapshot columns.

## Ehime Prefecture

Current source:
- snapshot: 2026-08-31
- coverage: Ehime Prefecture excluding Matsuyama City
- source workbook SHA-256: `25a87cae539181514c03f62ec6dcbff14cc683358a8b0cd9cb26b803479ceee1`

New permits for August 2026:
- 57 permit rows
- 41 are `飲食店営業`
- permit date missing: 0
- source coordinates: none

All-facilities snapshot:
- 10,897 permit rows
- 7,164 are `飲食店営業`
- permit date missing: 0
- source coordinates: none

The prefecture workbook stores address information across `営業所所在地` plus continuation columns. The acquisition code concatenates these fields before committing the sanitized address.

Some rows still have no facility address in the published source and must not receive guessed coordinates.

## Matsuyama City — monthly new / renewal

Current workbook contains twelve monthly sheets:
- 2025-08 through 2026-07

Observed schema contains:
- facility name
- business type
- combined facility address
- municipality code
- town ID field
- latitude / longitude fields
- permit number
- initial permit date
- current permit date
- permit expiry date
- application type field

Important audit findings:
1. `所在地＿連結表記` has no missing values in the twelve current monthly sheets.
2. Latitude/longitude columns exist but contain no usable coordinates in the current source.
3. `申請区分` exists but is empty in the current source.
4. New vs renewal can nevertheless be derived:
   - likely new: `initial_permit_date == permit_date`
   - likely renewal: `initial_permit_date != permit_date`
5. A real renewal example was observed in the July 2026 sheet: permit `第260491号`, initial permit date 2021-08-30, current permit date 2026-07-10.

This derivation must be retained as a derived field with provenance rather than presented as a source-provided classification.

## Matsuyama City — all facilities

The annual 2026-03-31 dataset is split into two files:
- facilities licensed by end-May 2021: 577 rows
- facilities licensed from June 2021 onward: 7,110 rows

The legacy pre-June-2021 file does not contain usable permit dates in the published fields, so it is useful for current location inventory but not for reconstructing exact historical permit-event dates.

### Permit number is not a primary key

Permit numbers are reused across time. Example:

- `第201号` — 2021-06-02 — フェイス
- `第201号` — 2022-05-23 — Pears.

Therefore no transform may use `permit_number` alone as a unique event identifier.

Stage 3 will build a deterministic event key from source authority, permit date, permit number, business type and facility identity/location, with collision QA.

## Privacy / public-repository QA

The source files contain fields such as applicant personal name, corporate representative, facility phone and contact information.

These are intentionally excluded from committed snapshots. Raw downloads are temporary and ignored by Git.

The repository also explicitly excludes the erroneous Ehime data version published from 2026-08-18 through 2026-08-20.

## Stage 2 exit status

PASS for current-source ingestion and schema discovery.

Remaining work belongs to later stages:
- Stage 3: historical coverage and new/renewal event reconstruction
- Stage 4: address normalization and geocoding
