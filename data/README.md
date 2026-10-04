# Data directory

`data/` contains only data that are safe and necessary to redistribute in this public repository.

- `data/raw/`: temporary acquisition cache; ignored by Git.
- `data/snapshots/`: source-derived snapshots with unnecessary direct identifiers removed.
- `data/processed/`: normalized/geocoded analytical data.

Every committed snapshot must preserve provenance: source URL, snapshot date, and SHA-256 of the downloaded source.

Do not commit applicant names, applicant kana, applicant addresses, or phone numbers.
