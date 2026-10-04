from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EVENTS = ROOT / "data" / "processed" / "permit_events_observed.csv"
CACHE = ROOT / "data" / "geocode" / "geocode_cache.json"
OUT = ROOT / "data" / "processed"
REPORT = ROOT / "docs" / "research" / "STAGE4_GEOCODING_AUDIT.json"


def clean_address(value: str) -> str:
    if not value:
        return ""
    x = unicodedata.normalize("NFKC", str(value)).strip()
    x = re.sub(r"[\u3000\t\r\n]+", " ", x)
    return re.sub(r"\s+", " ", x).strip()


def key_for(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def boolify(x) -> bool:
    return str(x).lower() == "true"


def valid_ehime_point(lat, lon) -> bool:
    try:
        lat = float(lat)
        lon = float(lon)
    except Exception:
        return False
    return 32.5 <= lat <= 34.6 and 131.5 <= lon <= 133.9


def pct(a: int, b: int) -> float:
    return round(100.0 * a / b, 2) if b else 0.0


def summarize(part: pd.DataFrame) -> dict:
    n = len(part)
    point = pd.to_numeric(part["latitude"], errors="coerce").notna() & pd.to_numeric(part["longitude"], errors="coerce").notna()
    strict = part["map_usable_strict"].map(boolify)
    town = part["map_usable_town_or_better"].map(boolify)
    muni = part["municipality_code_final"].astype(str).str.len() > 0
    return {
        "rows": int(n),
        "with_any_point": int(point.sum()),
        "with_any_point_pct": pct(int(point.sum()), n),
        "strict_address_or_parcel": int(strict.sum()),
        "strict_address_or_parcel_pct": pct(int(strict.sum()), n),
        "town_or_better": int(town.sum()),
        "town_or_better_pct": pct(int(town.sum()), n),
        "municipality_code_resolved": int(muni.sum()),
        "municipality_code_resolved_pct": pct(int(muni.sum()), n),
        "quality_counts": {str(k): int(v) for k, v in part["geocode_quality"].value_counts(dropna=False).items()},
        "point_level_counts": {str(k): int(v) for k, v in part["point_level"].value_counts(dropna=False).items()},
        "missing_source_address": int((part["facility_address"].astype(str).str.strip() == "").sum()),
        "outside_ehime_bounds": int((point & ~part["coordinate_in_ehime_bounds"]).sum()),
    }


def main() -> int:
    df = pd.read_csv(EVENTS, dtype=str, keep_default_na=False)
    payload = json.loads(CACHE.read_text(encoding="utf-8"))
    records = payload.get("results", [])
    cache = {r["address_key"]: r for r in records}

    df["_clean_address"] = df["facility_address"].map(clean_address)
    df["address_key"] = df["_clean_address"].map(lambda x: key_for(x) if x else "")

    fields = [
        "geocode_input", "normalized_prefecture", "normalized_city", "normalized_town",
        "normalized_addr", "unmatched_other", "normalized_address", "normalize_level",
        "point_level", "latitude", "longitude", "geocode_quality",
        "map_usable_strict", "map_usable_town_or_better",
        "derived_municipality_code", "error",
    ]
    for field in fields:
        target = "geocode_error" if field == "error" else field
        df[target] = df["address_key"].map(
            lambda k, f=field: cache.get(k, {}).get(f, "") if k else ""
        )

    source_code = df["municipality_code"].astype(str).str.strip()
    derived_code = df["derived_municipality_code"].astype(str).str.strip()
    df["municipality_code_final"] = source_code.where(source_code != "", derived_code)
    df["municipality_code_method"] = "unresolved"
    df.loc[source_code != "", "municipality_code_method"] = "source"
    df.loc[(source_code == "") & (derived_code != ""), "municipality_code_method"] = "normalized_city_map"

    df["map_usable_strict"] = df["map_usable_strict"].map(boolify)
    df["map_usable_town_or_better"] = df["map_usable_town_or_better"].map(boolify)

    lat_num = pd.to_numeric(df["latitude"], errors="coerce")
    lon_num = pd.to_numeric(df["longitude"], errors="coerce")
    has_point = lat_num.notna() & lon_num.notna()
    in_bounds = pd.Series(False, index=df.index)
    if has_point.any():
        in_bounds.loc[has_point] = [
            valid_ehime_point(a, b)
            for a, b in zip(lat_num.loc[has_point], lon_num.loc[has_point])
        ]
    df["coordinate_in_ehime_bounds"] = in_bounds
    df.loc[has_point & ~in_bounds, "map_usable_strict"] = False
    df.loc[has_point & ~in_bounds, "map_usable_town_or_better"] = False

    df = df.drop(columns=["_clean_address"])

    all_path = OUT / "permit_events_geocoded.csv"
    rest_path = OUT / "restaurant_permit_events_geocoded.csv"
    df.to_csv(all_path, index=False, encoding="utf-8")
    restaurants = df[df["is_restaurant"].map(boolify)].copy()
    restaurants.to_csv(rest_path, index=False, encoding="utf-8")

    by_authority = {
        authority: summarize(g)
        for authority, g in df.groupby("source_authority", dropna=False)
    }
    by_source_kind = {
        source: summarize(g)
        for source, g in df.groupby("source_kind", dropna=False)
    }

    report = {
        "stage": 4,
        "geocoder": payload.get("geocoder", {}),
        "municipality_code_reference": payload.get("municipality_code_reference"),
        "input": str(EVENTS.relative_to(ROOT)),
        "cache": str(CACHE.relative_to(ROOT)),
        "unique_cached_addresses": len(records),
        "overall": summarize(df),
        "restaurants": summarize(restaurants),
        "by_authority": by_authority,
        "by_source_kind": by_source_kind,
        "quality_semantics": {
            "address_or_parcel": "point_level >= 8; eligible for strict point-map use",
            "town_centroid": "point_level 3; may be used for aggregated/context views, not presented as exact facility coordinate",
            "municipality_centroid": "point_level 2; retained for provenance/context only and excluded from point maps",
            "prefecture_centroid": "point_level 1; excluded from point maps",
            "failed": "no usable coordinate returned",
        },
        "outputs": [
            str(all_path.relative_to(ROOT)),
            str(rest_path.relative_to(ROOT)),
        ],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if len(df) != 4240:
        print(f"Unexpected Stage 3 row count: {len(df)}")
        return 2
    if int((has_point & ~in_bounds).sum()) > 0:
        print("Coordinates outside broad Ehime bounds detected")
        return 2
    resolved = int((df["municipality_code_final"].astype(str).str.len() > 0).sum())
    if resolved < int(0.98 * len(df)):
        print("Municipality code resolution below 98%")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
