from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EVENTS = ROOT / "data" / "processed" / "restaurant_permit_events_geocoded.csv"
COVERAGE = ROOT / "data" / "processed" / "coverage_matrix.csv"
OUT = ROOT / "data" / "processed" / "spatial"
REPORT = ROOT / "docs" / "research" / "STAGE5_SPATIAL_METRICS_AUDIT.json"
OUT.mkdir(parents=True, exist_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)

MUNICIPALITIES = {
    "382019": "松山市",
    "382027": "今治市",
    "382035": "宇和島市",
    "382043": "八幡浜市",
    "382051": "新居浜市",
    "382060": "西条市",
    "382078": "大洲市",
    "382108": "伊予市",
    "382132": "四国中央市",
    "382141": "西予市",
    "382159": "東温市",
    "383562": "上島町",
    "383864": "久万高原町",
    "384011": "松前町",
    "384020": "砥部町",
    "384224": "内子町",
    "384429": "伊方町",
    "384844": "松野町",
    "384887": "鬼北町",
    "385069": "愛南町",
}

MATSUYAMA_CODE = "382019"


def b(x) -> bool:
    return str(x).lower() == "true"


def period_range(start: str, end: str) -> list[str]:
    return [str(p) for p in pd.period_range(start, end, freq="M")]


def third_mesh(lat: float, lon: float) -> dict:
    # Standard Japanese 3rd-level mesh (~1km).
    p = math.floor(lat * 1.5)
    q = math.floor(lon) - 100

    lat2f = (lat * 1.5 - p) * 8
    lon2f = (lon - math.floor(lon)) * 8
    a = math.floor(lat2f)
    b_ = math.floor(lon2f)

    lat3f = (lat2f - a) * 10
    lon3f = (lon2f - b_) * 10
    c = math.floor(lat3f)
    d = math.floor(lon3f)

    code = f"{p:02d}{q:02d}{a}{b_}{c}{d}"

    south = p / 1.5 + a * (5 / 60) + c * (30 / 3600)
    west = 100 + q + b_ * (7.5 / 60) + d * (45 / 3600)
    north = south + (30 / 3600)
    east = west + (45 / 3600)

    return {
        "mesh_1km": code,
        "mesh_1km_south": south,
        "mesh_1km_west": west,
        "mesh_1km_north": north,
        "mesh_1km_east": east,
        "mesh_1km_center_lat": (south + north) / 2,
        "mesh_1km_center_lon": (west + east) / 2,
    }


def half_mesh(lat: float, lon: float) -> dict:
    one = third_mesh(lat, lon)
    south = one["mesh_1km_south"]
    west = one["mesh_1km_west"]
    lat_step = (30 / 3600) / 2
    lon_step = (45 / 3600) / 2

    north_half = lat >= south + lat_step
    east_half = lon >= west + lon_step

    # Statistics Bureau convention: SW=1, SE=2, NW=3, NE=4.
    quadrant = 1 + int(east_half) + 2 * int(north_half)

    s = south + (lat_step if north_half else 0)
    w = west + (lon_step if east_half else 0)
    n = s + lat_step
    e = w + lon_step

    return {
        **one,
        "mesh_500m": one["mesh_1km"] + str(quadrant),
        "mesh_500m_south": s,
        "mesh_500m_west": w,
        "mesh_500m_north": n,
        "mesh_500m_east": e,
        "mesh_500m_center_lat": (s + n) / 2,
        "mesh_500m_center_lon": (w + e) / 2,
    }


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    if any(pd.isna(v) for v in [lat1, lon1, lat2, lon2]):
        return np.nan
    r = 6371.0088
    p1 = math.radians(float(lat1))
    p2 = math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lon2) - float(lon1))
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def exact_complete_authority_months(coverage: pd.DataFrame) -> set[tuple[str, str]]:
    c = coverage[coverage["coverage_status"] == "complete_exact_monthly"]
    return set(zip(c["authority"], c["month"]))


def complete_12m_end_months(coverage: pd.DataFrame, authority: str) -> list[str]:
    exact = set(
        coverage.loc[
            (coverage["authority"] == authority)
            & (coverage["coverage_status"] == "complete_exact_monthly"),
            "month",
        ]
    )
    if not exact:
        return []
    all_months = sorted(exact)
    result = []
    for end in all_months:
        p = pd.Period(end, freq="M")
        window = [str(p - i) for i in range(11, -1, -1)]
        if all(m in exact for m in window):
            result.append(end)
    return result


def municipality_monthly(new_events: pd.DataFrame, coverage: pd.DataFrame) -> pd.DataFrame:
    exact = coverage[coverage["coverage_status"] == "complete_exact_monthly"].copy()
    rows = []
    for _, cov in exact.iterrows():
        authority = cov["authority"]
        month = cov["month"]
        if authority == "松山市":
            codes = [MATSUYAMA_CODE]
        else:
            codes = [c for c in MUNICIPALITIES if c != MATSUYAMA_CODE]

        month_events = new_events[
            (new_events["source_authority"] == authority)
            & (new_events["coverage_month"] == month)
        ].copy()

        for code in codes:
            g = month_events[month_events["municipality_code_final"] == code]
            rows.append({
                "source_authority": authority,
                "month": month,
                "municipality_code": code,
                "municipality_name": MUNICIPALITIES[code],
                "new_restaurant_permits": int(len(g)),
                "strict_address_or_parcel": int(g["map_usable_strict"].astype(str).str.lower().eq("true").sum()),
                "town_or_better": int(g["map_usable_town_or_better"].astype(str).str.lower().eq("true").sum()),
                "coverage_status": "complete_exact_monthly",
            })
    return pd.DataFrame(rows).sort_values(["month", "municipality_code"]).reset_index(drop=True)


def mesh_monthly(strict_new_matsu: pd.DataFrame, mesh_col: str) -> pd.DataFrame:
    if strict_new_matsu.empty:
        return pd.DataFrame()

    group_cols = ["coverage_month", mesh_col]
    agg = (
        strict_new_matsu.groupby(group_cols, as_index=False)
        .agg(
            new_restaurant_permits=("event_id", "nunique"),
            unique_facilities=("facility_name", "nunique"),
        )
        .rename(columns={"coverage_month": "month"})
    )

    meta_cols = [
        mesh_col,
        f"{mesh_col}_south",
        f"{mesh_col}_west",
        f"{mesh_col}_north",
        f"{mesh_col}_east",
        f"{mesh_col}_center_lat",
        f"{mesh_col}_center_lon",
    ]
    meta = strict_new_matsu[meta_cols].drop_duplicates(mesh_col)
    out = agg.merge(meta, on=mesh_col, how="left")
    return out.sort_values(["month", "new_restaurant_permits", mesh_col], ascending=[True, False, True]).reset_index(drop=True)


def rolling_mesh(
    monthly: pd.DataFrame,
    mesh_col: str,
    valid_end_months: list[str],
) -> pd.DataFrame:
    if monthly.empty:
        return pd.DataFrame()
    meta_cols = [
        mesh_col,
        f"{mesh_col}_south",
        f"{mesh_col}_west",
        f"{mesh_col}_north",
        f"{mesh_col}_east",
        f"{mesh_col}_center_lat",
        f"{mesh_col}_center_lon",
    ]
    meta = monthly[meta_cols].drop_duplicates(mesh_col)
    count_map = {(r["month"], r[mesh_col]): int(r["new_restaurant_permits"]) for _, r in monthly.iterrows()}
    meshes = sorted(monthly[mesh_col].unique())
    rows = []
    for end in valid_end_months:
        p = pd.Period(end, freq="M")
        months = [str(p - i) for i in range(11, -1, -1)]
        counts = []
        for mesh in meshes:
            count = sum(count_map.get((m, mesh), 0) for m in months)
            if count > 0:
                counts.append((mesh, count))
        if not counts:
            continue

        vals = np.array([c for _, c in counts], dtype=float)
        mean = float(vals.mean())
        sd = float(vals.std(ddof=0))
        order = sorted(counts, key=lambda x: (-x[1], x[0]))
        n_active = len(order)

        for rank, (mesh, count) in enumerate(order, 1):
            z = 0.0 if sd == 0 else (count - mean) / sd
            percentile = 100.0 * (n_active - rank + 1) / n_active
            if percentile >= 95:
                hotspot_class = "top_5pct_active"
            elif percentile >= 80:
                hotspot_class = "top_20pct_active"
            else:
                hotspot_class = "other_active"
            rows.append({
                "window_end_month": end,
                "window_start_month": months[0],
                mesh_col: mesh,
                "new_restaurant_permits_12m": int(count),
                "active_mesh_rank": int(rank),
                "active_mesh_percentile": round(percentile, 2),
                "active_mesh_zscore": round(float(z), 4),
                "hotspot_class": hotspot_class,
            })

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out = out.merge(meta, on=mesh_col, how="left")
    return out.sort_values(["window_end_month", "active_mesh_rank"]).reset_index(drop=True)


def centroid_monthly(matsu_new: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scope, mask_col in [
        ("strict_address_or_parcel", "map_usable_strict"),
        ("town_or_better", "map_usable_town_or_better"),
    ]:
        subset = matsu_new[matsu_new[mask_col].astype(str).str.lower().eq("true")].copy()
        subset["latitude_num"] = pd.to_numeric(subset["latitude"], errors="coerce")
        subset["longitude_num"] = pd.to_numeric(subset["longitude"], errors="coerce")
        subset = subset.dropna(subset=["latitude_num", "longitude_num"])
        for month, g in subset.groupby("coverage_month"):
            rows.append({
                "month": month,
                "precision_scope": scope,
                "event_count": int(len(g)),
                "centroid_latitude": float(g["latitude_num"].mean()),
                "centroid_longitude": float(g["longitude_num"].mean()),
            })

    out = pd.DataFrame(rows).sort_values(["precision_scope", "month"]).reset_index(drop=True)
    out["movement_from_previous_month_km"] = np.nan
    for scope, idx in out.groupby("precision_scope").groups.items():
        inds = list(idx)
        prev = None
        prev_month = None
        for i in inds:
            month = pd.Period(out.loc[i, "month"], freq="M")
            if prev is not None and month == prev_month + 1:
                out.loc[i, "movement_from_previous_month_km"] = haversine_km(
                    out.loc[prev, "centroid_latitude"],
                    out.loc[prev, "centroid_longitude"],
                    out.loc[i, "centroid_latitude"],
                    out.loc[i, "centroid_longitude"],
                )
            prev = i
            prev_month = month
    return out


def monthly_concentration(mesh_1km: pd.DataFrame, valid_months: list[str]) -> pd.DataFrame:
    rows = []
    for month in valid_months:
        g = mesh_1km[mesh_1km["month"] == month]
        total = int(g["new_restaurant_permits"].sum()) if len(g) else 0
        if total == 0:
            rows.append({
                "month": month,
                "strict_new_restaurant_permits": 0,
                "active_1km_meshes": 0,
                "top_1km_mesh_share": np.nan,
                "hhi_1km": np.nan,
                "normalized_entropy_1km": np.nan,
            })
            continue
        shares = g["new_restaurant_permits"].astype(float) / total
        hhi = float((shares ** 2).sum())
        entropy = float(-(shares * np.log(shares)).sum())
        normalized_entropy = 0.0 if len(shares) <= 1 else entropy / math.log(len(shares))
        rows.append({
            "month": month,
            "strict_new_restaurant_permits": total,
            "active_1km_meshes": int(len(g)),
            "top_1km_mesh_share": round(float(shares.max()), 6),
            "hhi_1km": round(hhi, 6),
            "normalized_entropy_1km": round(normalized_entropy, 6),
        })
    return pd.DataFrame(rows)


def main() -> int:
    events = pd.read_csv(EVENTS, dtype=str, keep_default_na=False)
    coverage = pd.read_csv(COVERAGE, dtype=str, keep_default_na=False)

    if len(events) != 3300:
        raise RuntimeError(f"Unexpected restaurant event count: {len(events)}")

    # Location-change analysis is based on new permits only.
    new = events[events["event_type"] == "new"].copy()
    new["latitude_num"] = pd.to_numeric(new["latitude"], errors="coerce")
    new["longitude_num"] = pd.to_numeric(new["longitude"], errors="coerce")

    municipality = municipality_monthly(new, coverage)
    municipality.to_csv(OUT / "municipality_monthly_new_restaurants.csv", index=False, encoding="utf-8")

    matsu = new[
        (new["source_authority"] == "松山市")
        & (new["municipality_code_final"] == MATSUYAMA_CODE)
    ].copy()

    strict = matsu[
        matsu["map_usable_strict"].astype(str).str.lower().eq("true")
        & matsu["latitude_num"].notna()
        & matsu["longitude_num"].notna()
    ].copy()

    if len(strict):
        mesh_meta = strict.apply(
            lambda r: pd.Series(half_mesh(float(r["latitude_num"]), float(r["longitude_num"]))),
            axis=1,
        )
        strict = pd.concat([strict.reset_index(drop=True), mesh_meta.reset_index(drop=True)], axis=1)

    mesh1 = mesh_monthly(strict, "mesh_1km")
    mesh500 = mesh_monthly(strict, "mesh_500m")
    mesh1.to_csv(OUT / "matsuyama_mesh_1km_monthly.csv", index=False, encoding="utf-8")
    mesh500.to_csv(OUT / "matsuyama_mesh_500m_monthly.csv", index=False, encoding="utf-8")

    rolling_ends = complete_12m_end_months(coverage, "松山市")
    roll1 = rolling_mesh(mesh1, "mesh_1km", rolling_ends)
    roll500 = rolling_mesh(mesh500, "mesh_500m", rolling_ends)
    roll1.to_csv(OUT / "matsuyama_mesh_1km_rolling12.csv", index=False, encoding="utf-8")
    roll500.to_csv(OUT / "matsuyama_mesh_500m_rolling12.csv", index=False, encoding="utf-8")

    centroid = centroid_monthly(matsu)
    centroid.to_csv(OUT / "matsuyama_spatial_centroid_monthly.csv", index=False, encoding="utf-8")

    matsu_exact_months = sorted(
        coverage.loc[
            (coverage["authority"] == "松山市")
            & (coverage["coverage_status"] == "complete_exact_monthly"),
            "month",
        ]
    )
    concentration = monthly_concentration(mesh1, matsu_exact_months)
    concentration.to_csv(OUT / "matsuyama_monthly_spatial_concentration.csv", index=False, encoding="utf-8")

    # Summary of rolling-12 hotspot leaders for quick visualization/reporting.
    leaders = pd.DataFrame()
    if not roll1.empty:
        leaders = roll1[roll1["active_mesh_rank"] <= 10].copy()
        leaders.to_csv(OUT / "matsuyama_hotspot_top10_1km_rolling12.csv", index=False, encoding="utf-8")
    else:
        leaders.to_csv(OUT / "matsuyama_hotspot_top10_1km_rolling12.csv", index=False, encoding="utf-8")

    report = {
        "stage": 5,
        "input_restaurant_events": int(len(events)),
        "new_restaurant_events": int(len(new)),
        "municipality_monthly_rows": int(len(municipality)),
        "matsuyama_new_restaurant_events": int(len(matsu)),
        "matsuyama_strict_address_or_parcel_new_events": int(len(strict)),
        "matsuyama_complete_months": matsu_exact_months,
        "matsuyama_complete_month_count": len(matsu_exact_months),
        "matsuyama_valid_rolling12_end_months": rolling_ends,
        "matsuyama_valid_rolling12_window_count": len(rolling_ends),
        "mesh_1km_monthly_rows": int(len(mesh1)),
        "mesh_500m_monthly_rows": int(len(mesh500)),
        "rolling12_1km_rows": int(len(roll1)),
        "rolling12_500m_rows": int(len(roll500)),
        "centroid_rows": int(len(centroid)),
        "concentration_rows": int(len(concentration)),
        "methodological_rules": {
            "municipality_counts": "all exact new restaurant events with resolved municipality code",
            "fine_mesh": "Matsuyama new restaurant events with map_usable_strict=true only",
            "mesh_standard": "Statistics Bureau standard regional mesh: 3rd-level ~1km and 1/2 mesh ~500m",
            "hotspot": "rolling-12-month strict 1km counts ranked among active meshes; z-score/percentile are descriptive, not inferential significance tests",
            "centroid": "two series: strict address/parcel and town-or-better; centroid movement only between consecutive observed months",
            "rolling12": "only emitted when all 12 constituent Matsuyama months are complete_exact_monthly",
            "ehime_2021_2022_fine_spatial": "not used for mesh/hotspot because historical source is municipality-level only",
        },
        "outputs": [
            "data/processed/spatial/municipality_monthly_new_restaurants.csv",
            "data/processed/spatial/matsuyama_mesh_1km_monthly.csv",
            "data/processed/spatial/matsuyama_mesh_500m_monthly.csv",
            "data/processed/spatial/matsuyama_mesh_1km_rolling12.csv",
            "data/processed/spatial/matsuyama_mesh_500m_rolling12.csv",
            "data/processed/spatial/matsuyama_hotspot_top10_1km_rolling12.csv",
            "data/processed/spatial/matsuyama_spatial_centroid_monthly.csv",
            "data/processed/spatial/matsuyama_monthly_spatial_concentration.csv",
        ],
    }

    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    # QA gates.
    if len(matsu_exact_months) != 23:
        raise RuntimeError(f"Expected 23 complete Matsuyama months, got {len(matsu_exact_months)}")
    if len(rolling_ends) != 12:
        raise RuntimeError(f"Expected 12 valid rolling-12 windows, got {len(rolling_ends)}")
    if not mesh1.empty and not mesh1["mesh_1km"].str.match(r"^\d{8}$").all():
        raise RuntimeError("Invalid 1km mesh code")
    if not mesh500.empty and not mesh500["mesh_500m"].str.match(r"^\d{9}$").all():
        raise RuntimeError("Invalid 500m mesh code")
    if len(strict) and (
        strict["latitude_num"].min() < 32.5
        or strict["latitude_num"].max() > 34.6
        or strict["longitude_num"].min() < 131.5
        or strict["longitude_num"].max() > 133.9
    ):
        raise RuntimeError("Strict points outside broad Ehime bounds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
