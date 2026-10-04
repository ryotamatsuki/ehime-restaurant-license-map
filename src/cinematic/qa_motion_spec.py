from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/"data"/"processed"/"cinematic"/"cinematic_timeline_v1.json"

def main():
    x=json.loads(P.read_text(encoding="utf-8"))
    assert x["runtime_seconds"]==80
    scenes=x["scenes"]
    assert len(scenes)==13  # 12 authored scenes + outro
    assert scenes[0]["start"]==0
    assert scenes[-1]["end"]==80
    for a,b in zip(scenes,scenes[1:]):
        assert a["end"]==b["start"], (a["id"],b["id"])
    for s in scenes:
        assert s["end"]>s["start"]
        assert s["evidence"] in {"retrospective_partial","exact_monthly"}
        cam=s.get("camera",{})
        pts=[]
        if "to" in cam: pts.append(cam["to"])
        if "from" in cam: pts.append(cam["from"])
        for k in cam.get("keyframes",[]): pts.append(k[1:])
        for p in pts:
            lon,lat,zoom,pitch,bearing=p
            assert 132.5 < lon < 133.0
            assert 33.6 < lat < 34.1
            assert 9 <= zoom <= 14
            assert 0 <= pitch <= 50
            assert -180 <= bearing <= 180
    transition=[s for s in scenes if s["month"]=="2024-09"]
    assert len(transition)==1 and transition[0]["type"]=="evidence_transition"
    assert all(s["evidence"]=="retrospective_partial" for s in scenes if s["end"]<=38)
    assert all(s["evidence"]=="exact_monthly" for s in scenes if s["start"]>=38)
    climax=[s for s in scenes if s["month"]=="2026-02"][0]
    assert climax["primary_kpi"]["value"]==158
    print("Stage 9 cinematic timeline QA: PASS")
    print(f"runtime={x['runtime_seconds']}s scenes={len(scenes)}")

if __name__=="__main__":
    main()
