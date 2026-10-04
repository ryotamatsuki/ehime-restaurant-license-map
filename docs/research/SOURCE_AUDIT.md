# Source audit — 2026-10-04

## 1. Ehime Prefecture

Canonical dataset:
https://www.pref.ehime.jp/opendata-catalog/dataset/2344.html

Canonical metadata API:
https://www.pref.ehime.jp/opendata-catalog/api/package_show?id=44d962fa-8684-4be1-9437-030298a483f3

Observed on 2026-10-04:
- coverage: Ehime Prefecture excluding Matsuyama City
- cadence: monthly
- publishes the preceding month's newly permitted facilities and an all-facilities snapshot
- current resource: `新規営業許可施設(R8.8月)・全営業許可施設(R8.8.31現在) .xlsx`
- resource id: `29480`
- resource created: 2026-08-27
- resource updated: 2026-09-25
- license: CC BY
- format: XLSX

Known privacy incident:
- The dataset page states that data published from 2026-08-18 through 2026-08-20 incorrectly placed applicant address and phone values in facility fields.
- The publisher asks users to delete data downloaded during that interval.
- This project must never reconstruct, archive, or redistribute that affected version.
- Current corrected resources may be used, but committed analytical snapshots drop unnecessary direct contact and applicant identity fields.

Historical clue:
- Search indexing still exposes an older June 2026 workbook preview (resource id `25999`), showing that historical resource identifiers/previews may remain discoverable after replacement.
- Stage 3 will systematically enumerate recoverable resource history.

## 2. Matsuyama City — monthly new/renewal

Canonical dataset:
https://www.city.matsuyama.ehime.jp/shisei/opendata/metadata/shokuhinsinki.html

Observed:
- new or renewed food business permits
- monthly update
- stated retention: past one year
- data latest date shown: 2026-07-31
- format: Excel
- license: CC BY

## 3. Matsuyama City — all facilities

Canonical dataset:
https://www.city.matsuyama.ehime.jp/shisei/opendata/metadata/shokuhin.html

Observed:
- annual update
- data snapshot date shown: 2026-03-31
- two CSV resources: permits obtained by end of May 2021 and permits obtained from June 2021 onward
- license: CC BY

## 4. Interpretation rule

The data directly support claims about permit records/events. They do not, by themselves, prove exact opening or closure dates.

Primary wording:
- 新規営業許可
- 許可発生地点
- 許可件数

Avoid unless independently validated:
- 開店
- 閉店
- 現存店舗数

## 5. Stage 2 audit target

For every acquired source:
1. preserve source URL and source SHA-256;
2. inspect sheet names/encodings;
3. map columns;
4. count rows;
5. measure missing permit date/address;
6. detect duplicate permit numbers;
7. write a sanitized snapshot containing only the allowlisted analytical columns.
