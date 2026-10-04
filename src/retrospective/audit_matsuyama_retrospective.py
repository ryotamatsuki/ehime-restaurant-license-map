from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "processed" / "permit_events_retrospective_partial.csv"
OUT = ROOT / "docs" / "research" / "MATSUYAMA_RETROSPECTIVE_AUDIT.json"
OUT.parent.mkdir(parents=True, exist_ok=True)


def is_restaurant(value: str) -> bool:
    x = re.sub(r"^[①-㊿]\s*", "", str(value).strip())
    return x == "飲食店営業"


def main() -> int:
    df = pd.read_csv(SRC, dtype=str, keep_default_na=False)
    m = df[
        (df["source_authority"] == "松山市")
        & df["is_restaurant"].astype(str).str.lower().eq("true")
    ].copy()

    m = m[
        m["historical_month"].str.match(r"^\d{4}-\d{2}$", na=False)
        & (m["historical_month"] >= "2021-06")
        & (m["historical_month"] <= "2024-08")
    ].copy()

    monthly = (
        m.groupby("historical_month")
        .agg(
            rows=("retrospective_id", "nunique"),
            unique_facilities=("facility_name", "nunique"),
            nonempty_address=("facility_address", lambda s: int((s.astype(str).str.strip() != "").sum())),
        )
        .reset_index()
        .rename(columns={"historical_month":"month"})
    )

    report = {
        "scope":"松山市 retrospective partial before exact monthly window",
        "period":["2021-06","2024-08"],
        "months":int(monthly["month"].nunique()),
        "restaurant_rows":int(len(m)),
        "unique_facilities":int(m["facility_name"].nunique()),
        "nonempty_addresses":int((m["facility_address"].astype(str).str.strip() != "").sum()),
        "monthly":monthly.to_dict(orient="records"),
        "interpretation":"Backdated initial-permit dates from the 2026-03-31 all-facilities snapshot; incomplete historical event coverage and subject to survivor/carry-forward bias.",
    }
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
