from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
PUBLIC_DATA = ROOT / "web" / "public" / "data"
REPORT = ROOT / "docs" / "research" / "STAGE6_BUILD_AUDIT.json"
REPORT.parent.mkdir(parents=True, exist_ok=True)


def size(path: Path) -> int:
    return path.stat().st_size if path.exists() else 0


def main() -> int:
    manifest = json.loads((PUBLIC_DATA / "manifest.json").read_text(encoding="utf-8"))
    events = json.loads((PUBLIC_DATA / "strict_new_events.json").read_text(encoding="utf-8"))
    retro_events = json.loads((PUBLIC_DATA / "matsuyama_retrospective_events.json").read_text(encoding="utf-8"))

    required_data = [
        "manifest.json",
        "strict_new_events.json",
        "matsuyama_retrospective_events.json",
        "matsuyama_retrospective_monthly.json",
        "coverage.json",
        "municipality_monthly.json",
        "matsuyama_mesh_1km_monthly.geojson",
        "matsuyama_mesh_500m_monthly.geojson",
        "matsuyama_mesh_1km_rolling12.geojson",
        "matsuyama_mesh_500m_rolling12.geojson",
        "matsuyama_spatial_centroid_monthly.geojson",
    ]

    missing_data = [name for name in required_data if not (PUBLIC_DATA / name).exists()]
    dist_files = sorted(
        str(p.relative_to(DIST))
        for p in DIST.rglob("*")
        if p.is_file()
    ) if DIST.exists() else []

    report = {
        "stage": 6,
        "manifest_schema_version": manifest.get("schema_version"),
        "strict_new_events": len(events),
        "business_type_count": len(manifest.get("business_types", [])),
        "retrospective_visible_events": len(retro_events),
        "matsuyama_retrospective_months": len(manifest.get("matsuyama_retrospective_months", [])),
        "matsuyama_hybrid_months": len(manifest.get("matsuyama_hybrid_months", [])),
        "matsuyama_exact_months": len(
            manifest.get("exact_months_by_authority", {}).get("松山市", [])
        ),
        "ehime_exact_months": len(
            manifest.get("exact_months_by_authority", {}).get("愛媛県", [])
        ),
        "rolling12_end_months": len(
            manifest.get("rolling12_end_months_matsuyama", [])
        ),
        "missing_public_data": missing_data,
        "public_data_bytes": {
            name: size(PUBLIC_DATA / name)
            for name in required_data
        },
        "dist_file_count": len(dist_files),
        "dist_files": dist_files,
        "dist_total_bytes": sum(
            p.stat().st_size for p in DIST.rglob("*") if p.is_file()
        ) if DIST.exists() else 0,
        "browser_qa": {
            "framework": "@playwright/test 1.63.0",
            "desktop": "executed by Stage 6 workflow",
            "mobile": "executed by Stage 6 workflow",
        },
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if missing_data:
        return 2
    if not (DIST / "index.html").exists():
        return 2
    if len(events) < 500:
        return 2
    if len(retro_events) < 3500:
        return 2
    if report["matsuyama_retrospective_months"] != 39:
        return 2
    if report["matsuyama_hybrid_months"] != 62:
        return 2
    if report["matsuyama_exact_months"] != 23:
        return 2
    if report["rolling12_end_months"] != 12:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
