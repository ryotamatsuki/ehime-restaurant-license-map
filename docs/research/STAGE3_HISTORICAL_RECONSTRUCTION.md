# Stage 3 — Historical reconstruction report

Date: 2026-10-04  
Status: **PASS / COMPLETE**

## Scope

Stage 3 establishes what monthly permit-event history is genuinely recoverable for the period **2021-12 through 2026-08** and separates three evidence levels:

1. `complete_exact_monthly`: a monthly/new-or-renewal source file was recovered and parsed.
2. `partial_retrospective`: only a later all-facilities snapshot can be used to look backward from `initial_permit_date`; this is not treated as a complete monthly event archive.
3. `unavailable`: neither an exact monthly source nor a later all-facilities snapshot covering the month is available.

No missing month is interpolated or silently treated as observed.

## Exact monthly coverage recovered

### 愛媛県（松山市を除く）

Exact monthly new-permit files recovered:

- 2021-12
- 2022-01
- 2022-02
- 2022-03
- 2022-04
- 2026-08

The 2021-12 through 2022-04 files were recovered from Internet Archive captures of the original Ehime open-data resources. The archived source files were legacy `.xls` workbooks, parsed in-memory and reduced to the repository's allowlisted analytical fields before commit.

The current 2026-08 monthly file is acquired directly from the official Ehime dataset/API.

For months without an exact archived monthly file, the 2026-08-31 all-facilities snapshot provides only **partial retrospective context**. It must not be used as a complete monthly count because the all-facilities snapshot is not a historical event archive and may contain or omit facilities in ways that create survivor/carry-forward bias.

### 松山市

An archived `shokuhinsinki.xlsx` captured on 2025-10-14 was recovered. It contains twelve monthly sheets covering:

- 2024-09 through 2025-08

The current official rolling workbook contains:

- 2025-08 through 2026-07

Current official data are preferred over the archive for the overlapping 2025-08 sheet. The resulting exact continuous window is therefore:

**2024-09 through 2026-07 (23 consecutive months).**

For 2021-12 through 2024-08, the 2026-03-31 all-facilities snapshot supplies partial retrospective dates only.  
For 2026-08, no exact monthly Matsuyama source or covering later all-facilities snapshot was available at the Stage 3 audit date, so that month is classified `unavailable`.

## Event classification

Ehime monthly files are explicitly new-permit sources, so their events are classified `new`.

For Matsuyama, the published schema contains both `初回許可年月日` and `許可年月日`:

- `initial_permit_date == permit_date` → derived `new`
- `initial_permit_date != permit_date` → derived `renewal`
- missing required dates → `unknown`

This is a **derived classification**, not a claim that the source's `申請区分` field supplied the label.

The exact observed panel contains:

- 4,240 deduplicated permit events
- 3,981 derived/source-supported new events
- 259 derived renewal events
- 3,300 events whose business type is `飲食店営業`

## Duplicate QA

Three duplicate rows were removed. All three duplicate groups were exact identity duplicates: same authority, permit date, permit number, business type, facility name and facility address.

Examples include:

- 2024-11-27 / 第1029号 / ITALIAN RESTAURANT Carne e vino
- 2025-04-25 / 第70号 / 焼き鳥・海鮮　一
- 2025-05-28 / 第218号 / tiara

No distinct event was merged solely because it shared a permit number.

This is important because Stage 2 proved that Matsuyama permit numbers are reused across years; `permit_number` alone is never treated as a primary key.

## Coverage matrix

The audit window contains 57 months for each authority.

愛媛県:
- complete exact monthly: 6 months
- partial retrospective: 51 months
- unavailable: 0 months

松山市:
- complete exact monthly: 23 months
- partial retrospective: 33 months
- unavailable: 1 month

The machine-readable matrix is `data/processed/coverage_matrix.csv`.

## Privacy / archive safety

Raw archived workbooks are not committed. They are downloaded transiently, hashed, parsed, sanitized, and discarded.

The known Ehime privacy incident affecting the incorrectly published July 2026 source is explicitly excluded from archive recovery. No archived July-2026 workbook is ingested. July 2026 outside Matsuyama is therefore represented only by partial retrospective evidence from the later corrected all-facilities snapshot.

## Canonical Stage 3 outputs

- `data/processed/permit_events_observed.csv`
- `data/processed/restaurant_permit_events_observed.csv`
- `data/processed/permit_events_retrospective_partial.csv`
- `data/processed/coverage_matrix.csv`
- `docs/research/STAGE3_HISTORY_AUDIT.json`
- `docs/research/HISTORY_RECOVERY.json`
- `docs/research/HISTORY_PROBE.json`
- `data/snapshots/history/`

## Stage 3 exit criteria

- [x] recoverable Ehime historical resources/revisions enumerated
- [x] Matsuyama historical monthly retention investigated
- [x] archived source files recovered where available
- [x] exact observed event panel built
- [x] new vs renewal distinguished where supportable
- [x] deterministic event IDs and duplicate QA applied
- [x] every month × authority classified complete / partial / unavailable
- [x] retrospective data isolated from exact monthly events
- [x] no interpolation treated as observation
- [x] known unsafe archived Ehime source excluded

Stage 3 is complete. Stage 4 may now geocode the exact event panel and separately handle partial retrospective records with explicit quality flags.
