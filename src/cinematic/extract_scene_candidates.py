from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EXACT = ROOT / "data" / "processed" / "restaurant_permit_events_geocoded.csv"
RETRO = ROOT / "data" / "processed" / "matsuyama_restaurant_retrospective_geocoded.csv"
OUT = ROOT / "data" / "processed" / "cinematic"
REPORT = ROOT / "docs" / "research" / "STAGE8_CINEMATIC_INSIGHT_AUDIT.json"
OUT.mkdir(parents=True, exist_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)

START = "2021-06"
END = "2026-07"
EXACT_START = "2024-09"
MATSUYAMA_CODE = "382019"


def boolify(x) -> bool:
    return str(x).lower() == "true"


def month_range(start: str, end: str) -> list[str]:
    return [str(p) for p in pd.period_range(start, end, freq="M")]


def third_mesh(lat: float, lon: float) -> dict:
    p = math.floor(lat * 1.5)
    q = math.floor(lon) - 100
    lat2f = (lat * 1.5 - p) * 8
    lon2f = (lon - math.floor(lon)) * 8
    a = math.floor(lat2f)
    b = math.floor(lon2f)
    lat3f = (lat2f - a) * 10
    lon3f = (lon2f - b) * 10
    c = math.floor(lat3f)
    d = math.floor(lon3f)
    code = f"{p:02d}{q:02d}{a}{b}{c}{d}"
    south = p / 1.5 + a * (5 / 60) + c * (30 / 3600)
    west = 100 + q + b * (7.5 / 60) + d * (45 / 3600)
    north = south + (30 / 3600)
    east = west + (45 / 3600)
    return {
        "mesh_1km": code,
        "mesh_south": south,
        "mesh_west": west,
        "mesh_north": north,
        "mesh_east": east,
        "mesh_center_lat": (south + north) / 2,
        "mesh_center_lon": (west + east) / 2,
    }


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    if any(pd.isna(v) for v in [lat1, lon1, lat2, lon2]):
        return np.nan
    r = 6371.0088
    p1, p2 = math.radians(float(lat1)), math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lon2) - float(lon1))
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def percentile(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    out = x.rank(method="average", pct=True)
    return out.fillna(0.0)


def normalize_town(v: str) -> str:
    x = str(v or "").strip()
    return x if x and x.lower() != "nan" else ""


def load_unified() -> tuple[pd.DataFrame, pd.DataFrame]:
    exact = pd.read_csv(EXACT, dtype=str, keep_default_na=False)
    exact = exact[
        (exact["source_authority"] == "松山市")
        & exact["is_restaurant"].map(boolify)
        & (exact["event_type"] == "new")
        & (exact["coverage_month"] >= EXACT_START)
        & (exact["coverage_month"] <= END)
    ].copy()
    exact_u = pd.DataFrame({
        "event_id": exact["event_id"],
        "month": exact["coverage_month"],
        "date": exact["permit_date"],
        "evidence_tier": "exact_monthly",
        "facility_name": exact["facility_name"],
        "facility_address": exact["facility_address"],
        "normalized_town": exact["normalized_town"].map(normalize_town),
        "latitude": pd.to_numeric(exact["latitude"], errors="coerce"),
        "longitude": pd.to_numeric(exact["longitude"], errors="coerce"),
        "geocode_quality": exact["geocode_quality"],
        "strict": exact["map_usable_strict"].map(boolify),
        "town_or_better": exact["map_usable_town_or_better"].map(boolify),
    })

    retro = pd.read_csv(RETRO, dtype=str, keep_default_na=False)
    retro = retro[
        (retro["historical_month"] >= START)
        & (retro["historical_month"] < EXACT_START)
    ].copy()
    retro_u = pd.DataFrame({
        "event_id": retro["retrospective_id"],
        "month": retro["historical_month"],
        "date": retro["initial_permit_date"],
        "evidence_tier": "retrospective_partial",
        "facility_name": retro["facility_name"],
        "facility_address": retro["facility_address"],
        "normalized_town": retro["normalized_town"].map(normalize_town),
        "latitude": pd.to_numeric(retro["latitude"], errors="coerce"),
        "longitude": pd.to_numeric(retro["longitude"], errors="coerce"),
        "geocode_quality": retro["geocode_quality"],
        "strict": retro["map_usable_strict"].map(boolify),
        "town_or_better": retro["map_usable_town_or_better"].map(boolify),
    })

    all_events = pd.concat([retro_u, exact_u], ignore_index=True)
    all_events = all_events.sort_values(["month", "event_id"]).reset_index(drop=True)
    return all_events, exact_u


def add_mesh(strict: pd.DataFrame) -> pd.DataFrame:
    if strict.empty:
        return strict.copy()
    meta = strict.apply(
        lambda r: pd.Series(third_mesh(float(r["latitude"]), float(r["longitude"]))),
        axis=1,
    )
    return pd.concat([strict.reset_index(drop=True), meta.reset_index(drop=True)], axis=1)


def locality_label(g: pd.DataFrame) -> str:
    vals = [normalize_town(x) for x in g["normalized_town"].tolist()]
    vals = [x for x in vals if x]
    if not vals:
        return ""
    top = Counter(vals).most_common(3)
    return " / ".join(name for name, _ in top)


def build_mesh_panel(events: pd.DataFrame) -> pd.DataFrame:
    strict = events[
        events["strict"]
        & events["latitude"].notna()
        & events["longitude"].notna()
    ].copy()
    strict = add_mesh(strict)

    rows = []
    for (month, mesh), g in strict.groupby(["month", "mesh_1km"]):
        first = g.iloc[0]
        rows.append({
            "month": month,
            "evidence_tier": first["evidence_tier"],
            "mesh_1km": mesh,
            "count": int(len(g)),
            "unique_facilities": int(g["facility_name"].nunique()),
            "locality_label": locality_label(g),
            "mesh_center_lat": float(first["mesh_center_lat"]),
            "mesh_center_lon": float(first["mesh_center_lon"]),
        })
    return pd.DataFrame(rows).sort_values(["month", "count", "mesh_1km"], ascending=[True, False, True]).reset_index(drop=True)


def mesh_count_dict(mesh: pd.DataFrame) -> dict[tuple[str, str], int]:
    return {(r["month"], r["mesh_1km"]): int(r["count"]) for _, r in mesh.iterrows()}


def active_mesh_set(mesh: pd.DataFrame, month: str) -> set[str]:
    return set(mesh.loc[mesh["month"] == month, "mesh_1km"])


def top_meshes(mesh: pd.DataFrame, month: str, n=5) -> list[str]:
    g = mesh[mesh["month"] == month].sort_values(["count", "mesh_1km"], ascending=[False, True])
    return g.head(n)["mesh_1km"].tolist()


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    u = a | b
    return len(a & b) / len(u) if u else 1.0


def monthly_metrics(events: pd.DataFrame, mesh: pd.DataFrame) -> pd.DataFrame:
    months = month_range(START, END)
    mesh_counts = mesh_count_dict(mesh)
    rows = []

    for i, month in enumerate(months):
        g = events[events["month"] == month].copy()
        strict = g[g["strict"] & g["latitude"].notna() & g["longitude"].notna()].copy()
        display = g[g["town_or_better"] & g["latitude"].notna() & g["longitude"].notna()].copy()
        mg = mesh[mesh["month"] == month].copy().sort_values(["count", "mesh_1km"], ascending=[False, True])

        total = len(g)
        strict_n = len(strict)
        display_n = len(display)
        evidence = "exact_monthly" if month >= EXACT_START else "retrospective_partial"

        if strict_n:
            centroid_lat = float(strict["latitude"].mean())
            centroid_lon = float(strict["longitude"].mean())
            dists = [
                haversine_km(centroid_lat, centroid_lon, a, b)
                for a, b in zip(strict["latitude"], strict["longitude"])
            ]
            dispersion_mean = float(np.mean(dists))
            dispersion_p75 = float(np.percentile(dists, 75))
        else:
            centroid_lat = centroid_lon = dispersion_mean = dispersion_p75 = np.nan

        active = set(mg["mesh_1km"])
        counts = mg["count"].astype(float).values
        if len(counts):
            shares = counts / counts.sum()
            hhi = float((shares ** 2).sum())
            entropy = float(-(shares * np.log(shares)).sum())
            norm_entropy = 0.0 if len(shares) <= 1 else entropy / math.log(len(shares))
            top = mg.iloc[0]
            top_mesh = top["mesh_1km"]
            top_count = int(top["count"])
            top_share = float(top_count / counts.sum())
            top_lat = float(top["mesh_center_lat"])
            top_lon = float(top["mesh_center_lon"])
            top_locality = top["locality_label"]
        else:
            hhi = norm_entropy = top_share = np.nan
            top_mesh = ""
            top_count = 0
            top_lat = top_lon = np.nan
            top_locality = ""

        prev_month = months[i - 1] if i > 0 else None
        if prev_month:
            prev_active = active_mesh_set(mesh, prev_month)
            active_jaccard = jaccard(active, prev_active)
            top5_jaccard = jaccard(set(top_meshes(mesh, month)), set(top_meshes(mesh, prev_month)))
            new_active = len(active - prev_active)
            lost_active = len(prev_active - active)
            prev_top_for_current = mesh_counts.get((prev_month, top_mesh), 0) if top_mesh else 0
            current_meshes = active | prev_active
            deltas = [
                (m, mesh_counts.get((month, m), 0) - mesh_counts.get((prev_month, m), 0))
                for m in current_meshes
            ]
            deltas.sort(key=lambda x: (x[1], x[0]), reverse=True)
            surge_mesh, max_mesh_delta = deltas[0] if deltas else ("", 0)
        else:
            active_jaccard = top5_jaccard = np.nan
            new_active = lost_active = 0
            prev_top_for_current = 0
            surge_mesh = ""
            max_mesh_delta = 0

        surge_row = mg[mg["mesh_1km"] == surge_mesh]
        if len(surge_row):
            sr = surge_row.iloc[0]
            surge_lat = float(sr["mesh_center_lat"])
            surge_lon = float(sr["mesh_center_lon"])
            surge_locality = sr["locality_label"]
            surge_count = int(sr["count"])
        else:
            surge_lat = surge_lon = np.nan
            surge_locality = ""
            surge_count = 0

        rows.append({
            "month": month,
            "evidence_tier": evidence,
            "total_events": int(total),
            "display_events_town_or_better": int(display_n),
            "strict_events": int(strict_n),
            "strict_share_total": float(strict_n / total) if total else 0.0,
            "spatial_reliability": min(1.0, strict_n / 20.0),
            "active_meshes_1km": int(len(active)),
            "top_mesh": top_mesh,
            "top_mesh_count": top_count,
            "top_mesh_share": top_share,
            "top_mesh_locality": top_locality,
            "top_mesh_center_lat": top_lat,
            "top_mesh_center_lon": top_lon,
            "hhi_1km": hhi,
            "normalized_entropy_1km": norm_entropy,
            "centroid_lat": centroid_lat,
            "centroid_lon": centroid_lon,
            "dispersion_mean_km": dispersion_mean,
            "dispersion_p75_km": dispersion_p75,
            "active_mesh_jaccard_prev": active_jaccard,
            "mesh_churn_prev": 1.0 - active_jaccard if not pd.isna(active_jaccard) else np.nan,
            "top5_jaccard_prev": top5_jaccard,
            "top5_turnover_prev": 1.0 - top5_jaccard if not pd.isna(top5_jaccard) else np.nan,
            "new_active_meshes": int(new_active),
            "lost_active_meshes": int(lost_active),
            "dominant_mesh_changed": bool(prev_month and top_mesh and top_mesh != (top_meshes(mesh, prev_month, 1) or [""])[0]),
            "top_mesh_growth_vs_prev": int(top_count - prev_top_for_current),
            "surge_mesh": surge_mesh,
            "surge_mesh_count": int(surge_count),
            "max_mesh_delta_vs_prev": int(max_mesh_delta),
            "surge_mesh_locality": surge_locality,
            "surge_mesh_center_lat": surge_lat,
            "surge_mesh_center_lon": surge_lon,
        })

    out = pd.DataFrame(rows)

    # Month-to-month changes.
    out["centroid_move_km"] = np.nan
    out["hhi_change"] = np.nan
    out["entropy_change"] = np.nan
    out["dispersion_change_km"] = np.nan

    for i in range(1, len(out)):
        out.loc[i, "centroid_move_km"] = haversine_km(
            out.loc[i - 1, "centroid_lat"], out.loc[i - 1, "centroid_lon"],
            out.loc[i, "centroid_lat"], out.loc[i, "centroid_lon"],
        )
        if not pd.isna(out.loc[i, "hhi_1km"]) and not pd.isna(out.loc[i - 1, "hhi_1km"]):
            out.loc[i, "hhi_change"] = out.loc[i, "hhi_1km"] - out.loc[i - 1, "hhi_1km"]
        if not pd.isna(out.loc[i, "normalized_entropy_1km"]) and not pd.isna(out.loc[i - 1, "normalized_entropy_1km"]):
            out.loc[i, "entropy_change"] = (
                out.loc[i, "normalized_entropy_1km"] - out.loc[i - 1, "normalized_entropy_1km"]
            )
        if not pd.isna(out.loc[i, "dispersion_mean_km"]) and not pd.isna(out.loc[i - 1, "dispersion_mean_km"]):
            out.loc[i, "dispersion_change_km"] = (
                out.loc[i, "dispersion_mean_km"] - out.loc[i - 1, "dispersion_mean_km"]
            )

    return out


def location_candidates(months: list[str], mesh: pd.DataFrame) -> pd.DataFrame:
    count_map = mesh_count_dict(mesh)
    rows = []

    for i, month in enumerate(months):
        current = mesh[mesh["month"] == month].copy()
        if current.empty:
            continue

        prev3 = months[max(0, i - 3):i]
        next3 = months[i + 1:min(len(months), i + 4)]

        current = current.sort_values(["count", "mesh_1km"], ascending=[False, True])
        current["rank"] = np.arange(1, len(current) + 1)
        total = current["count"].sum()

        for _, r in current.iterrows():
            mesh_id = r["mesh_1km"]
            count = int(r["count"])
            prev1 = count_map.get((months[i - 1], mesh_id), 0) if i > 0 else 0
            prev3_total = sum(count_map.get((m, mesh_id), 0) for m in prev3)
            next3_counts = [count_map.get((m, mesh_id), 0) for m in next3]
            next3_active = sum(1 for x in next3_counts if x > 0)
            next3_total = sum(next3_counts)
            emerged = count >= 3 and prev3_total <= 1
            persistent_emergence = emerged and next3_active >= min(2, len(next3))
            delta_prev = count - prev1
            surge = count >= 4 and delta_prev >= 3

            # Descriptive visual targeting score; no inference/significance claim.
            visual_target_score = (
                2.0 * count
                + 1.5 * max(0, delta_prev)
                + 2.0 * next3_active
                + (8.0 if persistent_emergence else 0.0)
                + (4.0 if surge else 0.0)
            )

            rows.append({
                "month": month,
                "evidence_tier": r["evidence_tier"],
                "mesh_1km": mesh_id,
                "locality_label": r["locality_label"],
                "mesh_center_lat": float(r["mesh_center_lat"]),
                "mesh_center_lon": float(r["mesh_center_lon"]),
                "count": count,
                "share_of_strict_month": float(count / total) if total else 0.0,
                "rank_in_month": int(r["rank"]),
                "prev_month_count": int(prev1),
                "delta_vs_prev": int(delta_prev),
                "prev3_total": int(prev3_total),
                "next3_active_months": int(next3_active),
                "next3_total": int(next3_total),
                "emerged_after_quiet_prev3": bool(emerged),
                "persistent_emergence": bool(persistent_emergence),
                "surge_vs_prev": bool(surge),
                "visual_target_score": round(float(visual_target_score), 3),
            })

    return pd.DataFrame(rows).sort_values(
        ["visual_target_score", "month", "mesh_1km"], ascending=[False, True, True]
    ).reset_index(drop=True)



def hotspot_trajectories(mesh: pd.DataFrame, months: list[str]) -> pd.DataFrame:
    if mesh.empty:
        return pd.DataFrame()

    month_index = {m: i for i, m in enumerate(months)}
    rank_map = {}
    for month, g in mesh.groupby("month"):
        ranked = g.sort_values(["count", "mesh_1km"], ascending=[False, True]).reset_index(drop=True)
        for i, (_, r) in enumerate(ranked.iterrows(), 1):
            rank_map[(month, r["mesh_1km"])] = i

    rows = []
    for mesh_id, g in mesh.groupby("mesh_1km"):
        g = g.sort_values("month")
        active_months = g["month"].tolist()
        active_idx = sorted(month_index[m] for m in active_months)
        longest = 0
        current = 0
        prev = None
        for idx in active_idx:
            if prev is not None and idx == prev + 1:
                current += 1
            else:
                current = 1
            longest = max(longest, current)
            prev = idx

        peak = g.sort_values(["count", "month"], ascending=[False, True]).iloc[0]
        rank1 = sum(rank_map[(r["month"], mesh_id)] == 1 for _, r in g.iterrows())
        top3 = sum(rank_map[(r["month"], mesh_id)] <= 3 for _, r in g.iterrows())
        retro_active = int((g["evidence_tier"] == "retrospective_partial").sum())
        exact_active = int((g["evidence_tier"] == "exact_monthly").sum())

        score = (
            1.0 * len(active_months)
            + 1.5 * longest
            + 2.0 * top3
            + 3.0 * rank1
            + 0.5 * int(g["count"].sum())
            + 1.0 * int(peak["count"])
        )

        if longest >= 12 or len(active_months) >= 30:
            klass = "persistent_city_core"
        elif exact_active >= 5 and retro_active <= 2:
            klass = "emerging_exact_period_cluster"
        elif longest >= 5:
            klass = "recurring_cluster"
        else:
            klass = "episodic_cluster"

        rows.append({
            "mesh_1km": mesh_id,
            "trajectory_class": klass,
            "trajectory_score": round(float(score), 3),
            "active_months": int(len(active_months)),
            "longest_active_streak": int(longest),
            "retrospective_active_months": retro_active,
            "exact_active_months": exact_active,
            "rank1_months": int(rank1),
            "top3_months": int(top3),
            "total_strict_events": int(g["count"].sum()),
            "first_active_month": active_months[0],
            "last_active_month": active_months[-1],
            "peak_month": peak["month"],
            "peak_count": int(peak["count"]),
            "peak_locality_label": peak["locality_label"],
            "mesh_center_lat": float(peak["mesh_center_lat"]),
            "mesh_center_lon": float(peak["mesh_center_lon"]),
        })

    return pd.DataFrame(rows).sort_values(
        ["trajectory_score", "active_months", "mesh_1km"],
        ascending=[False, False, True],
    ).reset_index(drop=True)

def score_months(metrics: pd.DataFrame, locations: pd.DataFrame) -> pd.DataFrame:
    out = metrics.copy()
    emerg = (
        locations.groupby("month")
        .agg(
            persistent_emergence_count=("persistent_emergence", "sum"),
            surge_location_count=("surge_vs_prev", "sum"),
            strongest_location_score=("visual_target_score", "max"),
        )
        .reset_index()
    )
    out = out.merge(emerg, on="month", how="left")
    for c in ["persistent_emergence_count", "surge_location_count", "strongest_location_score"]:
        out[c] = out[c].fillna(0)

    out["abs_hhi_change"] = out["hhi_change"].abs()
    out["abs_entropy_change"] = out["entropy_change"].abs()
    out["positive_mesh_delta"] = out["max_mesh_delta_vs_prev"].clip(lower=0)

    # Percentile scores are calculated within evidence era to avoid directly
    # comparing the different data-generating processes.
    components = [
        "total_events",
        "centroid_move_km",
        "mesh_churn_prev",
        "abs_hhi_change",
        "positive_mesh_delta",
        "strongest_location_score",
        "top_mesh_share",
    ]
    for evidence, idx in out.groupby("evidence_tier").groups.items():
        ix = list(idx)
        for c in components:
            out.loc[ix, c + "_pct"] = percentile(out.loc[ix, c]).values

    reliability = out["spatial_reliability"].astype(float)
    out["volume_component"] = out["total_events_pct"]
    out["movement_component"] = out["centroid_move_km_pct"] * reliability
    out["churn_component"] = out["mesh_churn_prev_pct"] * reliability
    out["structure_component"] = (
        out[["abs_hhi_change_pct", "top_mesh_share_pct"]].max(axis=1) * reliability
    )
    out["hotspot_component"] = (
        out[["positive_mesh_delta_pct", "strongest_location_score_pct"]].max(axis=1) * reliability
    )

    out["visual_interest_score"] = 100 * (
        0.25 * out["volume_component"]
        + 0.15 * out["movement_component"]
        + 0.15 * out["churn_component"]
        + 0.20 * out["structure_component"]
        + 0.25 * out["hotspot_component"]
    )

    out["evidence_confidence_score"] = np.where(
        out["evidence_tier"] == "exact_monthly", 100.0, 65.0
    )
    out["source_boundary_flag"] = out["month"].eq(START)
    out["editorial_priority_score"] = (
        0.80 * out["visual_interest_score"]
        + 0.20 * out["evidence_confidence_score"]
    )

    # Evidence transition is an editorially mandatory scene.
    out.loc[out["month"] == EXACT_START, "editorial_priority_score"] = 100.0

    def primary_type(r):
        if r["month"] == START:
            return "source_boundary_opening"
        if r["month"] == EXACT_START:
            return "evidence_transition"
        comps = {
            "volume_spike": r["volume_component"],
            "centroid_shift": r["movement_component"],
            "spatial_reconfiguration": r["churn_component"],
            "concentration_change": r["structure_component"],
            "hotspot_emergence_or_surge": r["hotspot_component"],
        }
        return max(comps.items(), key=lambda kv: kv[1])[0]

    out["primary_scene_type"] = out.apply(primary_type, axis=1)

    def camera_target(r):
        if r["primary_scene_type"] in {"hotspot_emergence_or_surge", "concentration_change"}:
            if r["surge_mesh"]:
                return pd.Series([
                    r["surge_mesh"], r["surge_mesh_locality"],
                    r["surge_mesh_center_lat"], r["surge_mesh_center_lon"]
                ])
            return pd.Series([
                r["top_mesh"], r["top_mesh_locality"],
                r["top_mesh_center_lat"], r["top_mesh_center_lon"]
            ])
        return pd.Series(["", "", r["centroid_lat"], r["centroid_lon"]])

    out[["camera_mesh", "camera_locality", "camera_lat", "camera_lon"]] = out.apply(camera_target, axis=1)
    out["scene_rank"] = out["editorial_priority_score"].rank(method="first", ascending=False).astype(int)
    return out.sort_values(["editorial_priority_score", "month"], ascending=[False, True]).reset_index(drop=True)


def choose_storyboard(scored: pd.DataFrame, locations: pd.DataFrame) -> list[dict]:
    scenes = []
    by_month = scored.set_index("month")
    used_focus_meshes = {
        "retrospective_partial": Counter(),
        "exact_monthly": Counter(),
    }

    def location_for_month(month: str, scene_type: str):
        r = by_month.loc[month]
        target = locations[locations["month"] == month].sort_values(
            ["visual_target_score", "rank_in_month"], ascending=[False, True]
        )

        # Movement/reconfiguration should be shown citywide around the centroid,
        # not incorrectly forced onto the strongest hotspot.
        if scene_type in {"centroid_shift", "spatial_reconfiguration", "source_boundary_opening", "volume_spike"}:
            return {
                "mesh_1km": "",
                "locality": "",
                "lat": None if pd.isna(r["centroid_lat"]) else float(r["centroid_lat"]),
                "lon": None if pd.isna(r["centroid_lon"]) else float(r["centroid_lon"]),
            }

        if len(target):
            loc = target.iloc[0]
            return {
                "mesh_1km": loc["mesh_1km"],
                "locality": loc["locality_label"],
                "lat": float(loc["mesh_center_lat"]),
                "lon": float(loc["mesh_center_lon"]),
            }
        return {
            "mesh_1km": r["top_mesh"],
            "locality": r["top_mesh_locality"],
            "lat": None if pd.isna(r["top_mesh_center_lat"]) else float(r["top_mesh_center_lat"]),
            "lon": None if pd.isna(r["top_mesh_center_lon"]) else float(r["top_mesh_center_lon"]),
        }

    def add_scene(month: str, role: str, reason: str):
        if month not in by_month.index:
            return
        r = by_month.loc[month]
        target = location_for_month(month, r["primary_scene_type"])
        scenes.append({
            "month": month,
            "role": role,
            "scene_type": r["primary_scene_type"],
            "evidence_tier": r["evidence_tier"],
            "editorial_priority_score": round(float(r["editorial_priority_score"]), 2),
            "visual_interest_score": round(float(r["visual_interest_score"]), 2),
            "total_events": int(r["total_events"]),
            "strict_events": int(r["strict_events"]),
            "top_mesh": r["top_mesh"],
            "top_mesh_locality": r["top_mesh_locality"],
            "camera_target": target,
            "reason": reason,
        })
        if target["mesh_1km"]:
            used_focus_meshes[r["evidence_tier"]][target["mesh_1km"]] += 1

    add_scene(
        START,
        "opening",
        "Source-boundary opening. The retrospective source begins here, so the high June count is not interpreted as a real volume spike."
    )
    add_scene(
        EXACT_START,
        "evidence_transition",
        "Explicit transition from retrospective reconstruction to complete monthly observation."
    )
    add_scene(END, "closing", "End-state frame for comparison with the opening.")

    for tier, max_scenes, spacing in [
        ("retrospective_partial", 4, 3),
        ("exact_monthly", 5, 2),
    ]:
        candidates = scored[
            (scored["evidence_tier"] == tier)
            & (~scored["month"].isin([START, EXACT_START, END]))
        ].sort_values("editorial_priority_score", ascending=False)

        selected = []
        for _, r in candidates.iterrows():
            p = pd.Period(r["month"], freq="M")
            if any(abs(p.ordinal - pd.Period(m, freq="M").ordinal) < spacing for m in selected):
                continue

            target = location_for_month(r["month"], r["primary_scene_type"])
            # Avoid a storyboard that repeatedly zooms to the same dominant mesh.
            if target["mesh_1km"]:
                limit = 1 if tier == "retrospective_partial" else 2
                if used_focus_meshes[tier][target["mesh_1km"]] >= limit:
                    continue

            selected.append(r["month"])
            add_scene(
                r["month"],
                "insight",
                f"High quantitative scene score driven primarily by {r['primary_scene_type']}.",
            )
            if len(selected) >= max_scenes:
                break

    scenes.sort(key=lambda x: x["month"])
    for i, scene in enumerate(scenes, 1):
        scene["sequence"] = i
    return scenes

def main() -> int:
    events, exact = load_unified()
    months = month_range(START, END)
    if sorted(events["month"].unique().tolist()) != months:
        missing = [m for m in months if m not in set(events["month"])]
        raise RuntimeError(f"Hybrid timeline is not complete: missing={missing}")

    mesh = build_mesh_panel(events)
    metrics = monthly_metrics(events, mesh)
    locations = location_candidates(months, mesh)
    trajectories = hotspot_trajectories(mesh, months)
    scored = score_months(metrics, locations)
    storyboard = choose_storyboard(scored, locations)

    metrics.to_csv(OUT / "matsuyama_62m_month_metrics.csv", index=False, encoding="utf-8")
    mesh.to_csv(OUT / "matsuyama_62m_strict_mesh_1km.csv", index=False, encoding="utf-8")
    locations.to_csv(OUT / "matsuyama_location_scene_candidates.csv", index=False, encoding="utf-8")
    trajectories.to_csv(OUT / "matsuyama_hotspot_trajectories.csv", index=False, encoding="utf-8")
    scored.to_csv(OUT / "matsuyama_scene_candidates_ranked.csv", index=False, encoding="utf-8")
    (OUT / "cinematic_storyboard_seed.json").write_text(
        json.dumps(storyboard, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    top_months = scored.head(15)[[
        "month", "evidence_tier", "editorial_priority_score", "visual_interest_score",
        "primary_scene_type", "total_events", "strict_events", "top_mesh",
        "top_mesh_locality", "centroid_move_km", "hhi_1km", "max_mesh_delta_vs_prev",
        "persistent_emergence_count",
    ]].to_dict(orient="records")

    top_locations = locations.head(20)[[
        "month", "evidence_tier", "mesh_1km", "locality_label", "count",
        "delta_vs_prev", "prev3_total", "next3_active_months",
        "persistent_emergence", "surge_vs_prev", "visual_target_score",
    ]].to_dict(orient="records")

    top_trajectories = trajectories.head(15).to_dict(orient="records")

    audit = {
        "stage": 8,
        "timeline": [START, END],
        "months": len(months),
        "retrospective_months": int((metrics["evidence_tier"] == "retrospective_partial").sum()),
        "exact_months": int((metrics["evidence_tier"] == "exact_monthly").sum()),
        "hybrid_event_rows": int(len(events)),
        "exact_event_rows": int(len(exact)),
        "strict_point_rows": int(events["strict"].sum()),
        "strict_mesh_rows": int(len(mesh)),
        "location_candidate_rows": int(len(locations)),
        "storyboard_scene_count": len(storyboard),
        "hotspot_trajectory_rows": int(len(trajectories)),
        "scoring": {
            "visual_interest_weights": {
                "volume": 0.25,
                "centroid_movement": 0.15,
                "mesh_churn": 0.15,
                "structure_concentration": 0.20,
                "hotspot_emergence_or_surge": 0.25,
            },
            "spatial_reliability": "min(1, strict_events/20), applied to all spatial components",
            "percentiles": "calculated separately within retrospective_partial and exact_monthly evidence eras",
            "evidence_confidence_score": {"retrospective_partial": 65, "exact_monthly": 100},
            "editorial_priority": "0.80 * visual_interest + 0.20 * evidence_confidence; 2024-09 transition forced to 100",
        },
        "top_months": top_months,
        "top_locations": top_locations,
        "top_hotspot_trajectories": top_trajectories,
        "storyboard": storyboard,
        "outputs": [
            "data/processed/cinematic/matsuyama_62m_month_metrics.csv",
            "data/processed/cinematic/matsuyama_62m_strict_mesh_1km.csv",
            "data/processed/cinematic/matsuyama_location_scene_candidates.csv",
            "data/processed/cinematic/matsuyama_hotspot_trajectories.csv",
            "data/processed/cinematic/matsuyama_scene_candidates_ranked.csv",
            "data/processed/cinematic/cinematic_storyboard_seed.json",
        ],
    }
    REPORT.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))

    # QA gates.
    if len(metrics) != 62:
        return 2
    if audit["retrospective_months"] != 39 or audit["exact_months"] != 23:
        return 2
    if len(storyboard) < 9:
        return 2
    if not any(s["month"] == EXACT_START and s["role"] == "evidence_transition" for s in storyboard):
        return 2
    if scored["editorial_priority_score"].isna().any():
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
