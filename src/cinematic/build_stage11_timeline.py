from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CIN = ROOT / "data" / "processed" / "cinematic"
METRICS = CIN / "matsuyama_62m_month_metrics.csv"
MESH = CIN / "matsuyama_62m_strict_mesh_1km.csv"
TRAJ = CIN / "matsuyama_hotspot_trajectories.csv"
OUT = CIN / "cinematic_timeline_v2.json"
FOCUS_OUT = CIN / "cinematic_focus_series.json"

START = "2021-06"
END = "2026-07"
DOGO = "50326622"
MITSU = "50326537"
TAKEHARA = "50325690"
AIRPORT = "50325599"


def months() -> list[str]:
    return [str(p) for p in pd.period_range(START, END, freq="M")]


def build_schedule(ms: list[str]) -> list[dict]:
    anchors = {
        "2021-06": 0.0,
        "2021-07": 5.0,
        "2024-02": 15.2,
        "2024-03": 17.7,
        "2024-05": 18.5,
        "2024-06": 20.8,
        "2024-09": 22.0,
        "2024-10": 24.6,
        "2024-11": 25.3,
        "2024-12": 28.2,
        "2025-01": 29.0,
        "2025-05": 37.0,
        "2025-06": 44.5,
        "2025-08": 48.0,
        "2025-09": 53.5,
        "2025-12": 56.0,
        "2026-01": 59.0,
        "2026-02": 61.0,
        "2026-03": 69.5,
        "2026-07": 72.8,
    }
    idx = {m: i for i, m in enumerate(ms)}
    starts: dict[str, float] = {}
    ordered = sorted(anchors, key=lambda m: idx[m])
    for left, right in zip(ordered, ordered[1:]):
        li, ri = idx[left], idx[right]
        lt, rt = anchors[left], anchors[right]
        for i in range(li, ri):
            fraction = (i - li) / (ri - li)
            starts[ms[i]] = lt + (rt - lt) * fraction
    starts[ordered[-1]] = anchors[ordered[-1]]

    result = []
    for i, month in enumerate(ms):
        start = starts[month]
        end = starts[ms[i + 1]] if i + 1 < len(ms) else 80.0
        result.append({"month": month, "start": round(start, 4), "end": round(end, 4)})
    return result


def get_metric(metrics: pd.DataFrame, month: str, col: str) -> float:
    row = metrics.loc[metrics["month"] == month]
    if len(row) != 1:
        raise RuntimeError(f"missing metric {month}")
    return row.iloc[0][col]


def mesh_count(mesh: pd.DataFrame, month: str, mesh_id: str) -> int:
    row = mesh[(mesh["month"] == month) & (mesh["mesh_1km"] == mesh_id)]
    return int(row.iloc[0]["count"]) if len(row) else 0


def mesh_center(mesh: pd.DataFrame, mesh_id: str) -> list[float]:
    row = mesh[mesh["mesh_1km"] == mesh_id].iloc[0]
    return [float(row["mesh_center_lon"]), float(row["mesh_center_lat"])]


def focus_series(mesh: pd.DataFrame, trajectories: pd.DataFrame) -> dict:
    exact_months = [str(p) for p in pd.period_range("2024-09", "2026-07", freq="M")]
    result = {}
    for key, mesh_id, label in [
        ("dogo", DOGO, "道後"),
        ("mitsu", MITSU, "三津"),
    ]:
        t = trajectories.loc[trajectories["mesh_1km"] == mesh_id].iloc[0]
        result[key] = {
            "mesh_1km": mesh_id,
            "label": label,
            "center": mesh_center(mesh, mesh_id),
            "exact_active_months": int(t["exact_active_months"]),
            "exact_total_months": len(exact_months),
            "series": [
                {"month": m, "count": mesh_count(mesh, m, mesh_id)}
                for m in exact_months
            ],
        }
    return result


def main() -> int:
    metrics = pd.read_csv(METRICS, dtype={"month": str, "top_mesh": str, "surge_mesh": str})
    mesh = pd.read_csv(MESH, dtype={"month": str, "mesh_1km": str})
    trajectories = pd.read_csv(TRAJ, dtype={"mesh_1km": str})
    ms = months()
    schedule = build_schedule(ms)
    focus = focus_series(mesh, trajectories)

    checks = {
        "2024-02_dogo": mesh_count(mesh, "2024-02", DOGO),
        "2024-05_takehara": mesh_count(mesh, "2024-05", TAKEHARA),
        "2024-09_dogo": mesh_count(mesh, "2024-09", DOGO),
        "2024-11_airport": mesh_count(mesh, "2024-11", AIRPORT),
        "2025-05_city_total": int(get_metric(metrics, "2025-05", "total_events")),
        "2025-05_city_strict": int(get_metric(metrics, "2025-05", "strict_events")),
        "2025-08_mitsu": mesh_count(mesh, "2025-08", MITSU),
        "2025-12_city_total": int(get_metric(metrics, "2025-12", "total_events")),
        "2026-02_city_total": int(get_metric(metrics, "2026-02", "total_events")),
        "2026-02_dogo": mesh_count(mesh, "2026-02", DOGO),
        "dogo_exact_active": focus["dogo"]["exact_active_months"],
        "mitsu_exact_active": focus["mitsu"]["exact_active_months"],
    }
    expected = {
        "2024-02_dogo": 6,
        "2024-05_takehara": 4,
        "2024-09_dogo": 15,
        "2024-11_airport": 4,
        "2025-05_city_total": 165,
        "2025-05_city_strict": 40,
        "2025-08_mitsu": 5,
        "2025-12_city_total": 131,
        "2026-02_city_total": 158,
        "2026-02_dogo": 14,
        "dogo_exact_active": 19,
        "mitsu_exact_active": 15,
    }
    if checks != expected:
        raise RuntimeError(f"Stage 11 numeric check failed: {checks} != {expected}")

    centers = {
        "dogo": mesh_center(mesh, DOGO),
        "mitsu": mesh_center(mesh, MITSU),
        "takehara": mesh_center(mesh, TAKEHARA),
        "airport": mesh_center(mesh, AIRPORT),
    }

    timeline = {
        "version": "2.0.0",
        "runtime_seconds": 80,
        "story": "許可の記録が月ごとに重なり、道後、三津、その他の地区に、繰り返し現れるまとまりが見えてくる。",
        "period_notes": [
            {"start_month": "2021-06", "end_month": "2024-08", "label": "2021-06〜2024-08：参考復元"},
            {"start_month": "2024-09", "end_month": "2026-07", "label": "2024-09〜2026-07：月次観測"},
        ],
        "month_schedule": schedule,
        "camera_keyframes": [
            {"t": 0.0, "lon": 132.755, "lat": 33.840, "zoom": 10.9, "pitch": 22, "bearing": 0},
            {"t": 5.0, "lon": 132.755, "lat": 33.840, "zoom": 11.0, "pitch": 26, "bearing": -4},
            {"t": 14.5, "lon": 132.755, "lat": 33.840, "zoom": 10.8, "pitch": 24, "bearing": -4},
            {"t": 15.7, "lon": centers["dogo"][0], "lat": centers["dogo"][1], "zoom": 12.8, "pitch": 38, "bearing": 6},
            {"t": 17.2, "lon": centers["dogo"][0], "lat": centers["dogo"][1], "zoom": 12.8, "pitch": 38, "bearing": 6},
            {"t": 17.8, "lon": 132.755, "lat": 33.840, "zoom": 10.7, "pitch": 24, "bearing": 0},
            {"t": 18.8, "lon": centers["takehara"][0], "lat": centers["takehara"][1], "zoom": 12.6, "pitch": 36, "bearing": -8},
            {"t": 20.3, "lon": centers["takehara"][0], "lat": centers["takehara"][1], "zoom": 12.6, "pitch": 36, "bearing": -8},
            {"t": 21.6, "lon": 132.755, "lat": 33.840, "zoom": 10.8, "pitch": 24, "bearing": -2},
            {"t": 22.2, "lon": 132.758, "lat": 33.842, "zoom": 11.0, "pitch": 26, "bearing": -2},
            {"t": 23.0, "lon": centers["dogo"][0], "lat": centers["dogo"][1], "zoom": 12.9, "pitch": 39, "bearing": 6},
            {"t": 24.2, "lon": centers["dogo"][0], "lat": centers["dogo"][1], "zoom": 12.9, "pitch": 39, "bearing": 6},
            {"t": 24.8, "lon": 132.755, "lat": 33.840, "zoom": 10.7, "pitch": 24, "bearing": 0},
            {"t": 25.7, "lon": centers["airport"][0], "lat": centers["airport"][1], "zoom": 12.5, "pitch": 34, "bearing": -8},
            {"t": 27.7, "lon": centers["airport"][0], "lat": centers["airport"][1], "zoom": 12.5, "pitch": 34, "bearing": -8},
            {"t": 29.0, "lon": 132.755, "lat": 33.840, "zoom": 10.9, "pitch": 24, "bearing": -2},
            {"t": 36.5, "lon": 132.755, "lat": 33.840, "zoom": 10.95, "pitch": 24, "bearing": -2},
            {"t": 44.5, "lon": 132.755, "lat": 33.840, "zoom": 10.95, "pitch": 24, "bearing": -2},
            {"t": 46.5, "lon": 132.755, "lat": 33.840, "zoom": 10.35, "pitch": 18, "bearing": 0},
            {"t": 47.3, "lon": 132.738, "lat": 33.851, "zoom": 10.6, "pitch": 22, "bearing": -8},
            {"t": 48.8, "lon": centers["mitsu"][0], "lat": centers["mitsu"][1], "zoom": 12.9, "pitch": 38, "bearing": -14},
            {"t": 52.8, "lon": centers["mitsu"][0], "lat": centers["mitsu"][1], "zoom": 12.9, "pitch": 38, "bearing": -14},
            {"t": 53.7, "lon": 132.755, "lat": 33.840, "zoom": 10.7, "pitch": 22, "bearing": -3},
            {"t": 61.0, "lon": 132.755, "lat": 33.840, "zoom": 10.95, "pitch": 24, "bearing": -2},
            {"t": 63.0, "lon": 132.760, "lat": 33.843, "zoom": 11.1, "pitch": 26, "bearing": 0},
            {"t": 64.5, "lon": centers["dogo"][0], "lat": centers["dogo"][1], "zoom": 13.15, "pitch": 40, "bearing": 8},
            {"t": 68.5, "lon": centers["dogo"][0], "lat": centers["dogo"][1], "zoom": 13.15, "pitch": 40, "bearing": 8},
            {"t": 70.0, "lon": 132.755, "lat": 33.840, "zoom": 10.7, "pitch": 22, "bearing": -2},
            {"t": 73.8, "lon": 132.748, "lat": 33.846, "zoom": 10.55, "pitch": 20, "bearing": 0},
            {"t": 80.0, "lon": 132.748, "lat": 33.846, "zoom": 10.55, "pitch": 20, "bearing": 0},
        ],
        "beats": [
            {
                "id": "opening",
                "start": 0.0, "end": 5.0,
                "title": "松山、62か月の許可の足跡。",
                "caption": "光は、その月の許可の記録。",
                "caption_window": [1.4, 4.5],
                "scope": "松山市",
                "style": "opening",
            },
            {
                "id": "retro_dogo",
                "start": 15.2, "end": 17.7,
                "place": "道後",
                "focus_mesh": DOGO,
                "focus_center": centers["dogo"],
                "scope": "道後周辺の1km区画・高精度地点",
                "local_count": checks["2024-02_dogo"],
                "caption": "道後にも、許可のまとまりが繰り返し現れる。",
                "caption_window": [16.0, 17.55],
                "style": "minor_local",
            },
            {
                "id": "takehara",
                "start": 18.5, "end": 20.8,
                "place": "竹原・藤原",
                "focus_mesh": TAKEHARA,
                "focus_center": centers["takehara"],
                "scope": "竹原・藤原周辺の1km区画・高精度地点",
                "local_count": checks["2024-05_takehara"],
                "caption": "竹原・藤原にも、許可のまとまりが見える。",
                "caption_window": [19.05, 20.65],
                "style": "minor_local",
            },
            {
                "id": "dogo_202409",
                "start": 22.0, "end": 24.6,
                "place": "道後",
                "focus_mesh": DOGO,
                "focus_center": centers["dogo"],
                "scope": "道後周辺の1km区画・高精度地点",
                "local_count": checks["2024-09_dogo"],
                "caption": "道後周辺に、許可がまとまって現れる。",
                "caption_window": [23.15, 24.5],
                "style": "minor_local",
            },
            {
                "id": "airport_takehara",
                "start": 25.3, "end": 28.2,
                "place": "空港通・竹原",
                "focus_mesh": AIRPORT,
                "focus_center": centers["airport"],
                "scope": "空港通・竹原周辺の1km区画・高精度地点",
                "local_count": checks["2024-11_airport"],
                "caption": "空港通・竹原にも、別のまとまりが現れる。",
                "caption_window": [26.15, 28.0],
                "style": "minor_local",
            },
            {
                "id": "city_202505",
                "start": 37.0, "end": 44.5,
                "place": "松山市全体",
                "scope": "松山市全体",
                "kpi_sequence": [
                    {"start": 38.0, "end": 44.0, "label": "松山市全体", "value": checks["2025-05_city_total"], "unit": "件"},
                ],
                "support": f"地図上の高精度地点 {checks['2025-05_city_strict']}件",
                "caption": "2025年5月。許可の発生が市内に広がる。",
                "caption_window": [39.0, 42.5],
                "style": "major_citywide",
            },
            {
                "id": "mitsu_202508",
                "start": 48.0, "end": 53.5,
                "place": "三津",
                "focus_mesh": MITSU,
                "focus_center": centers["mitsu"],
                "scope": "三津周辺の1km区画・高精度地点",
                "kpi_sequence": [
                    {"start": 49.25, "end": 53.1, "label": "三津周辺", "value": checks["2025-08_mitsu"], "unit": "件"},
                ],
                "support": "直前3か月は同じ区画で合計1件",
                "sparkline": "mitsu",
                "caption": "三津。この月、許可が再びまとまって現れる。",
                "caption_window": [50.15, 52.95],
                "style": "major_local",
            },
            {
                "id": "year_end",
                "start": 56.0, "end": 59.0,
                "place": "松山市全体",
                "scope": "松山市全体",
                "kpi_sequence": [
                    {"start": 56.8, "end": 58.5, "label": "松山市全体", "value": checks["2025-12_city_total"], "unit": "件"},
                ],
                "style": "passing_citywide",
            },
            {
                "id": "dogo_202602",
                "start": 61.0, "end": 69.5,
                "place": "道後",
                "focus_mesh": DOGO,
                "focus_center": centers["dogo"],
                "scope": "道後周辺の1km区画・高精度地点",
                "kpi_sequence": [
                    {"start": 61.5, "end": 63.25, "label": "松山市全体", "value": checks["2026-02_city_total"], "unit": "件"},
                    {"start": 64.55, "end": 69.0, "label": "道後周辺", "value": checks["2026-02_dogo"], "unit": "件"},
                ],
                "support": "道後周辺の1km区画・高精度地点",
                "sparkline": "dogo",
                "caption": "2026年2月、道後周辺に許可が集中。",
                "caption_window": [65.15, 68.25],
                "style": "climax_local",
            },
            {
                "id": "closing",
                "start": 72.8, "end": 80.0,
                "place": "道後と三津",
                "focus_meshes": [DOGO, MITSU],
                "focus_centers": [centers["dogo"], centers["mitsu"]],
                "scope": "月次観測23か月・同じ1km区画・高精度地点",
                "support": f"道後 {checks['dogo_exact_active']}/23か月　｜　三津 {checks['mitsu_exact_active']}/23か月",
                "caption": "道後と三津。許可が繰り返し現れる場所が見えてくる。",
                "caption_window": [74.5, 77.4],
                "cta_window": [77.0, 80.0],
                "style": "closing",
            },
        ],
        "explore_targets": {
            "dogo": {"label": "道後", "month": "2026-02", "center": centers["dogo"], "zoom": 13.0},
            "mitsu": {"label": "三津", "month": "2025-08", "center": centers["mitsu"], "zoom": 13.0},
        },
        "numeric_checks": checks,
    }

    FOCUS_OUT.write_text(json.dumps(focus, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"timeline": str(OUT), "focus": str(FOCUS_OUT), "checks": checks}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
