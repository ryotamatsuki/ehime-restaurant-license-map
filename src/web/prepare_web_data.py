from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "web" / "public" / "data"
PUBLIC.mkdir(parents=True, exist_ok=True)

EVENTS = ROOT / "data" / "processed" / "permit_events_geocoded.csv"
RETRO = ROOT / "data" / "processed" / "matsuyama_restaurant_retrospective_geocoded.csv"
COVERAGE = ROOT / "data" / "processed" / "coverage_matrix.csv"
SPATIAL = ROOT / "data" / "processed" / "spatial"

MUNICIPALITIES = {
    "382019": "松山市", "382027": "今治市", "382035": "宇和島市",
    "382043": "八幡浜市", "382051": "新居浜市", "382060": "西条市",
    "382078": "大洲市", "382108": "伊予市", "382132": "四国中央市",
    "382141": "西予市", "382159": "東温市", "383562": "上島町",
    "383864": "久万高原町", "384011": "松前町", "384020": "砥部町",
    "384224": "内子町", "384429": "伊方町", "384844": "松野町",
    "384887": "鬼北町", "385069": "愛南町",
}


def boolify(x) -> bool:
    return str(x).lower() == "true"


def clean_business_type(value: str) -> str:
    x = str(value).strip()
    return re.sub(r"^[\u2460-\u2473\u3251-\u325f\u32b1-\u32bf]\s*", "", x)


def json_dump(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def month_range(start: str, end: str) -> list[str]:
    return [str(p) for p in pd.period_range(start, end, freq="M")]


def main() -> None:
    events = pd.read_csv(EVENTS, dtype=str, keep_default_na=False)
    retro = pd.read_csv(RETRO, dtype=str, keep_default_na=False)
    coverage = pd.read_csv(COVERAGE, dtype=str, keep_default_na=False)
    municipality = pd.read_csv(
        SPATIAL / "municipality_monthly_new_restaurants.csv",
        dtype=str,
        keep_default_na=False,
    )

    strict = events[
        events["event_type"].eq("new")
        & events["map_usable_strict"].map(boolify)
    ].copy()
    strict["business_type_clean"] = strict["business_type"].map(clean_business_type)

    point_records = []
    for _, r in strict.iterrows():
        try:
            lat = float(r["latitude"])
            lon = float(r["longitude"])
        except Exception:
            continue
        point_records.append({
            "id": r["event_id"],
            "month": r["coverage_month"],
            "date": r["permit_date"],
            "authority": r["source_authority"],
            "municipality_code": r["municipality_code_final"],
            "municipality_name": MUNICIPALITIES.get(r["municipality_code_final"], ""),
            "business_type": r["business_type_clean"],
            "facility_name": r["facility_name"],
            "address": r["facility_address"],
            "quality": r["geocode_quality"],
            "evidence": "exact_monthly",
            "lon": lon,
            "lat": lat,
        })
    json_dump(PUBLIC / "strict_new_events.json", point_records)

    retro_visible = retro[retro["map_usable_town_or_better"].map(boolify)].copy()
    retro_records = []
    for _, r in retro_visible.iterrows():
        try:
            lat = float(r["latitude"])
            lon = float(r["longitude"])
        except Exception:
            continue
        retro_records.append({
            "id": r["retrospective_id"],
            "month": r["historical_month"],
            "date": r["initial_permit_date"],
            "authority": "松山市",
            "municipality_code": "382019",
            "municipality_name": "松山市",
            "business_type": "飲食店営業",
            "facility_name": r["facility_name"],
            "address": r["facility_address"],
            "quality": r["geocode_quality"],
            "evidence": "retrospective_partial_survivor_biased",
            "lon": lon,
            "lat": lat,
        })
    json_dump(PUBLIC / "matsuyama_retrospective_events.json", retro_records)

    retro_monthly = (
        retro.groupby("historical_month")
        .agg(
            retrospective_rows=("retrospective_id", "nunique"),
            strict_address_or_parcel=("map_usable_strict", lambda s: int(s.map(boolify).sum())),
            town_or_better=("map_usable_town_or_better", lambda s: int(s.map(boolify).sum())),
        )
        .reset_index()
        .rename(columns={"historical_month": "month"})
    )
    json_dump(PUBLIC / "matsuyama_retrospective_monthly.json", retro_monthly.to_dict(orient="records"))

    json_dump(PUBLIC / "coverage.json", coverage.to_dict(orient="records"))

    municipality_records = []
    for _, r in municipality.iterrows():
        municipality_records.append({
            "authority": r["source_authority"],
            "month": r["month"],
            "municipality_code": r["municipality_code"],
            "municipality_name": r["municipality_name"],
            "new_restaurant_permits": int(r["new_restaurant_permits"]),
            "strict_address_or_parcel": int(r["strict_address_or_parcel"]),
            "town_or_better": int(r["town_or_better"]),
            "coverage_status": r["coverage_status"],
        })
    json_dump(PUBLIC / "municipality_monthly.json", municipality_records)

    exact_by_authority = {}
    for authority, g in coverage[
        coverage["coverage_status"].eq("complete_exact_monthly")
    ].groupby("authority"):
        exact_by_authority[authority] = sorted(g["month"].tolist())

    business_counts = strict["business_type_clean"].value_counts().sort_values(ascending=False)
    business_types = [
        {"value": name, "count": int(count)}
        for name, count in business_counts.items()
    ]

    rolling = pd.read_csv(
        SPATIAL / "matsuyama_mesh_1km_rolling12.csv",
        dtype=str,
        keep_default_na=False,
    )
    rolling_end_months = sorted(rolling["window_end_month"].unique().tolist())
    retrospective_months = month_range("2021-06", "2024-08")
    hybrid_months = retrospective_months + exact_by_authority["松山市"]

    manifest = {
        "schema_version": 2,
        "default_municipality_code": "382019",
        "default_business_type": "飲食店営業",
        "municipalities": [
            {
                "code": code,
                "name": name,
                "authority": "松山市" if code == "382019" else "愛媛県",
            }
            for code, name in MUNICIPALITIES.items()
        ],
        "business_types": business_types,
        "exact_months_by_authority": exact_by_authority,
        "all_exact_months": sorted(
            set(m for months in exact_by_authority.values() for m in months)
        ),
        "matsuyama_retrospective_months": retrospective_months,
        "matsuyama_hybrid_months": hybrid_months,
        "rolling12_end_months_matsuyama": rolling_end_months,
        "strict_new_event_count": len(point_records),
        "retrospective_visible_event_count": len(retro_records),
        "retrospective_total_rows": int(len(retro)),
        "source_notes": {
            "exact_points": "address_or_parcel only",
            "retrospective_points": "town_or_better; incomplete backcast from 2026-03-31 all-facilities snapshot",
            "mesh": "restaurant permits only, strict address/parcel coordinates, exact monthly period only",
            "coverage": "complete_exact_monthly / retrospective_partial_survivor_biased / unavailable",
        },
    }
    json_dump(PUBLIC / "manifest.json", manifest)

    for name in [
        "matsuyama_mesh_1km_monthly.geojson",
        "matsuyama_mesh_500m_monthly.geojson",
        "matsuyama_mesh_1km_rolling12.geojson",
        "matsuyama_mesh_500m_rolling12.geojson",
        "matsuyama_spatial_centroid_monthly.geojson",
    ]:
        shutil.copyfile(SPATIAL / name, PUBLIC / name)

    print(json.dumps({
        "strict_new_events": len(point_records),
        "retrospective_visible_events": len(retro_records),
        "retrospective_total_rows": int(len(retro)),
        "matsuyama_hybrid_months": len(hybrid_months),
        "business_types": len(business_types),
        "exact_months_by_authority": exact_by_authority,
        "rolling12_end_months": rolling_end_months,
        "output": str(PUBLIC.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
