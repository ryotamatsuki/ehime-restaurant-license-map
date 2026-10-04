from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SNAP = ROOT / "data" / "snapshots"
OUT = ROOT / "data" / "processed"
REPORT = ROOT / "docs" / "research" / "STAGE3_CURRENT_PANEL_AUDIT.json"
OUT.mkdir(parents=True, exist_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)

EVENT_FIELDS = [
    "source_authority",
    "source_snapshot_date",
    "permit_number",
    "initial_permit_date",
    "permit_date",
    "permit_expiry_date",
    "business_type",
    "facility_name",
    "facility_address",
    "municipality_code",
    "record_scope",
    "source_url",
    "source_sha256",
]


def clean(x) -> str:
    if pd.isna(x):
        return ""
    return str(x).strip()


def event_type(row) -> str:
    scope = clean(row["record_scope"])
    initial = clean(row["initial_permit_date"])
    permit = clean(row["permit_date"])
    if scope == "new":
        return "new"
    if scope == "new_or_renewal" and initial and permit:
        return "new" if initial == permit else "renewal"
    return "unknown"


def event_id(row) -> str:
    parts = [
        clean(row["source_authority"]),
        clean(row["permit_date"]),
        clean(row["permit_number"]),
        clean(row["business_type"]),
        clean(row["facility_name"]),
        clean(row["facility_address"]),
    ]
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:24]


def main() -> int:
    files = sorted(SNAP.glob("*.csv"))
    event_files = [
        p for p in files
        if "_new.csv" in p.name or p.name.startswith("matsuyama_monthly_")
    ]
    if not event_files:
        raise RuntimeError("No event-bearing snapshots found")

    frames = []
    source_rows = {}
    for path in event_files:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        missing = [c for c in EVENT_FIELDS if c not in df.columns]
        if missing:
            raise ValueError(f"{path.name}: missing columns {missing}")
        df = df[EVENT_FIELDS].copy()
        source_rows[path.name] = int(len(df))
        frames.append(df)

    panel = pd.concat(frames, ignore_index=True)
    panel["event_type"] = panel.apply(event_type, axis=1)
    panel["event_id"] = panel.apply(event_id, axis=1)
    panel["event_month"] = panel["permit_date"].str.slice(0, 7)
    panel["is_restaurant"] = panel["business_type"].str.replace("① ", "", regex=False).eq("飲食店営業")

    dup_mask = panel["event_id"].duplicated(keep=False)
    duplicate_event_rows = int(dup_mask.sum())
    duplicate_event_ids = sorted(panel.loc[dup_mask, "event_id"].unique().tolist())
    if duplicate_event_rows:
        # Identical event rows may be duplicated across snapshots. Keep one only,
        # but report the collision candidates for QA.
        panel = panel.drop_duplicates(subset=["event_id"], keep="first").copy()

    panel = panel.sort_values(
        ["permit_date", "source_authority", "permit_number", "business_type", "facility_name"],
        kind="stable",
    ).reset_index(drop=True)

    all_path = OUT / "permit_events_current.csv"
    restaurant_path = OUT / "restaurant_permit_events_current.csv"
    panel.to_csv(all_path, index=False, encoding="utf-8")
    panel.loc[panel["is_restaurant"]].to_csv(restaurant_path, index=False, encoding="utf-8")

    report = {
        "input_files": source_rows,
        "rows_before_event_dedup": int(sum(source_rows.values())),
        "duplicate_event_rows_before_dedup": duplicate_event_rows,
        "duplicate_event_ids_sample": duplicate_event_ids[:20],
        "rows_after_event_dedup": int(len(panel)),
        "restaurant_rows": int(panel["is_restaurant"].sum()),
        "missing_permit_date": int((panel["permit_date"] == "").sum()),
        "missing_facility_address": int((panel["facility_address"] == "").sum()),
        "event_type_counts": {
            str(k): int(v) for k, v in panel["event_type"].value_counts(dropna=False).items()
        },
        "coverage_by_authority_month": (
            panel.groupby(["source_authority", "event_month"], dropna=False)
            .size()
            .reset_index(name="rows")
            .to_dict(orient="records")
        ),
        "outputs": [
            str(all_path.relative_to(ROOT)),
            str(restaurant_path.relative_to(ROOT)),
        ],
        "event_id_rule": (
            "sha256(authority|permit_date|permit_number|business_type|facility_name|facility_address)[:24]"
        ),
        "event_type_rule": {
            "Ehime_prefecture_new_sheet": "new",
            "Matsuyama_monthly": "new if initial_permit_date == permit_date, else renewal; unknown if dates missing",
        },
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if report["missing_permit_date"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
