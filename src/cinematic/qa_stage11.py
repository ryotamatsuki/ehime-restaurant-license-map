from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CIN = ROOT / "data" / "processed" / "cinematic"
TIMELINE = CIN / "cinematic_timeline_v2.json"
FOCUS = CIN / "cinematic_focus_series.json"


def main() -> int:
    t = json.loads(TIMELINE.read_text(encoding="utf-8"))
    f = json.loads(FOCUS.read_text(encoding="utf-8"))

    expected_months = [str(p) for p in pd.period_range("2021-06", "2026-07", freq="M")]
    schedule = t["month_schedule"]
    assert t["version"] == "2.0.0"
    assert t["runtime_seconds"] == 80
    assert [x["month"] for x in schedule] == expected_months
    assert schedule[0]["start"] == 0
    assert schedule[-1]["end"] == 80
    for a, b in zip(schedule, schedule[1:]):
        assert abs(float(a["end"]) - float(b["start"])) < 1e-6
        assert float(a["end"]) > float(a["start"])

    frames = t["camera_keyframes"]
    assert frames[0]["t"] == 0
    assert frames[-1]["t"] == 80
    assert all(a["t"] < b["t"] for a, b in zip(frames, frames[1:]))
    for frame in frames:
        assert 132.5 < float(frame["lon"]) < 133.0
        assert 33.6 < float(frame["lat"]) < 34.1
        assert 9.5 <= float(frame["zoom"]) <= 14
        assert 0 <= float(frame["pitch"]) <= 50
        assert -28 <= float(frame["bearing"]) <= 28

    beats = t["beats"]
    beat_ids = {b["id"] for b in beats}
    assert "evidence_transition" not in beat_ids
    assert "evidence_boundary_approach" not in beat_ids

    # No dedicated methodology subtitle or KPI scene.
    text_fields = []
    for beat in beats:
        for key in ["title", "caption", "place", "support"]:
            if beat.get(key):
                text_fields.append(str(beat[key]))
    joined = "\n".join(text_fields)
    assert "次の月から" not in joined
    assert "ここから月次" not in joined
    assert "完全観測期" not in joined

    # Major captions must have meaningful read time.
    for beat_id in ["city_202505", "mitsu_202508", "dogo_202602", "closing"]:
        beat = next(b for b in beats if b["id"] == beat_id)
        start, end = beat["caption_window"]
        assert end - start >= 2.5, (beat_id, end - start)

    # Brief local glimpses use short captions without stretching the film clock.
    for beat in beats:
        if beat.get("style") == "minor_local":
            assert len(beat["caption"]) <= 12, (beat["id"], beat["caption"])

    # February's whole-city KPI must never inherit Dogo's local context.
    climax = next(b for b in beats if b["id"] == "dogo_202602")
    city, local = climax["kpi_sequence"]
    assert city["value"] == 158 and city["place"] == "松山市全体"
    assert city["scope"] == "松山市全体"
    assert not city["support"] and not city["sparkline"]
    assert local["value"] == 14 and local["place"] == "道後"
    assert local["scope"] == "道後周辺の1km区画・高精度地点"
    assert local["sparkline"] == "dogo"
    assert city["end"] < climax["focus_window"][0] <= local["start"]
    assert not any(climax.get(k) for k in ["place", "scope", "support", "sparkline"])

    checks = t["numeric_checks"]
    assert checks["2024-02_dogo"] == 6
    assert checks["2024-05_takehara"] == 4
    assert checks["2024-09_dogo"] == 15
    assert checks["2024-11_airport"] == 4
    assert checks["2025-05_city_total"] == 165
    assert checks["2025-05_city_strict"] == 40
    assert checks["2025-08_mitsu"] == 5
    assert checks["2025-12_city_total"] == 131
    assert checks["2026-02_city_total"] == 158
    assert checks["2026-02_dogo"] == 14
    assert checks["dogo_exact_active"] == 19
    assert checks["mitsu_exact_active"] == 15

    assert f["dogo"]["exact_active_months"] == 19
    assert f["mitsu"]["exact_active_months"] == 15
    assert len(f["dogo"]["series"]) == 23
    assert len(f["mitsu"]["series"]) == 23
    assert next(x for x in f["dogo"]["series"] if x["month"] == "2026-02")["count"] == 14
    assert next(x for x in f["mitsu"]["series"] if x["month"] == "2025-08")["count"] == 5

    period_labels = [x["label"] for x in t["period_notes"]]
    assert period_labels == [
        "2021-06〜2024-08：参考復元",
        "2024-09〜2026-07：月次観測",
    ]

    # Required editorial pacing anchors.
    starts = {x["month"]: float(x["start"]) for x in schedule}
    assert starts["2024-09"] == 22.0
    assert starts["2025-05"] == 37.0
    assert starts["2025-08"] == 48.0
    assert starts["2025-12"] == 56.0
    assert starts["2026-02"] == 61.0
    assert starts["2026-07"] == 72.8

    closing = next(b for b in beats if b["id"] == "closing")
    assert closing["cta_window"][1] == 80
    assert set(t["explore_targets"]) == {"dogo", "mitsu"}

    print("Stage 11 cinematic timeline/data QA: PASS")
    print(json.dumps({
        "months": len(schedule),
        "runtime": t["runtime_seconds"],
        "beats": len(beats),
        "dogo_exact_active": f["dogo"]["exact_active_months"],
        "mitsu_exact_active": f["mitsu"]["exact_active_months"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
