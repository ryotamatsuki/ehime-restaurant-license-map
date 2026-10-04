from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "research" / "HISTORY_PROBE.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

S = requests.Session()
S.headers.update({
    "User-Agent": "ehime-restaurant-license-map-history-probe/0.1 (+https://github.com/ryotamatsuki/ehime-restaurant-license-map)"
})

BODIK_DATASETS = [
    "380008_2344_cc-by",      # Ehime current catalog dataset mirror
    "382019_3669_cc-by",      # Matsuyama current mirror
    "382019_3375_cc-by",      # older Matsuyama catalog-id mirror discovered in search index
]

EHIME_DATASET = "https://www.pref.ehime.jp/opendata-catalog/dataset/2344.html"
MATSU_CURRENT = "https://www.city.matsuyama.ehime.jp/shisei/opendata/metadata/shokuhinsinki.html"
MATSU_OLD_CATALOG = [
    "https://www.pref.ehime.jp/opendata-catalog/dataset/3669.html",
    "https://www.pref.ehime.jp/opendata-catalog/dataset/3375.html",
]


def get_json(url: str, params=None):
    r = S.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def get_text(url: str):
    r = S.get(url, timeout=60)
    r.raise_for_status()
    return r.text


def ckan_action(action: str, **params):
    url = f"https://odm.bodik.jp/api/3/action/{action}"
    try:
        data = get_json(url, params=params)
        return {
            "ok": bool(data.get("success")),
            "result": data.get("result"),
            "url": requests.Request("GET", url, params=params).prepare().url,
        }
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def slim_resource(r: dict):
    return {
        "id": r.get("id"),
        "name": r.get("name"),
        "url": r.get("url"),
        "format": r.get("format"),
        "created": r.get("created"),
        "last_modified": r.get("last_modified"),
        "metadata_modified": r.get("metadata_modified"),
        "size": r.get("size"),
        "hash": r.get("hash"),
    }


def probe_bodik(dataset_id: str):
    pkg = ckan_action("package_show", id=dataset_id)
    activity = ckan_action("package_activity_list", id=dataset_id, limit=100, offset=0)
    out = {"dataset_id": dataset_id, "package_show_ok": pkg.get("ok", False)}
    if pkg.get("ok") and isinstance(pkg.get("result"), dict):
        p = pkg["result"]
        out["package"] = {
            "id": p.get("id"),
            "name": p.get("name"),
            "title": p.get("title"),
            "metadata_created": p.get("metadata_created"),
            "metadata_modified": p.get("metadata_modified"),
            "resources": [slim_resource(r) for r in p.get("resources", [])],
            "extras": p.get("extras", []),
        }
    else:
        out["package_error"] = pkg.get("error")

    out["activity_ok"] = activity.get("ok", False)
    if activity.get("ok") and isinstance(activity.get("result"), list):
        acts = []
        for a in activity["result"]:
            item = {
                "id": a.get("id"),
                "timestamp": a.get("timestamp"),
                "activity_type": a.get("activity_type"),
                "object_id": a.get("object_id"),
            }
            data = a.get("data")
            if isinstance(data, dict):
                pkgdata = data.get("package") or data.get("dataset")
                if isinstance(pkgdata, dict):
                    item["package_snapshot"] = {
                        "title": pkgdata.get("title"),
                        "metadata_modified": pkgdata.get("metadata_modified"),
                        "resources": [slim_resource(r) for r in pkgdata.get("resources", [])],
                    }
            acts.append(item)
        out["activities"] = acts
    else:
        out["activity_error"] = activity.get("error")
    return out


def html_resource_links(url: str):
    try:
        html = get_text(url)
        soup = BeautifulSoup(html, "html.parser")
        vals = []
        for a in soup.find_all("a", href=True):
            href = urljoin(url, a["href"])
            txt = a.get_text(" ", strip=True)
            if re.search(r"\.(xlsx?|csv)(?:\?|$)", href, flags=re.I) or "食品営業" in txt or "許可" in txt:
                vals.append({"text": txt, "url": href})
        # stable dedup
        seen = set()
        out = []
        for x in vals:
            key = (x["text"], x["url"])
            if key not in seen:
                seen.add(key)
                out.append(x)
        return {"ok": True, "links": out}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def wayback_cdx(url: str):
    endpoint = "https://web.archive.org/cdx/search/cdx"
    params = {
        "url": url,
        "output": "json",
        "filter": "statuscode:200",
        "filter": "mimetype:text/html",
        "fl": "timestamp,original,statuscode,digest",
        "collapse": "digest",
        "from": "2021",
        "to": "2026",
    }
    try:
        r = S.get(endpoint, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        return {"ok": True, "captures": data[1:] if data and isinstance(data[0], list) else data}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def main():
    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "bodik": {d: probe_bodik(d) for d in BODIK_DATASETS},
        "official_html": {
            "ehime_current": html_resource_links(EHIME_DATASET),
            "matsuyama_current": html_resource_links(MATSU_CURRENT),
            **{f"matsuyama_old_{i+1}": html_resource_links(u) for i, u in enumerate(MATSU_OLD_CATALOG)},
        },
        "wayback": {
            "ehime_dataset": wayback_cdx(EHIME_DATASET),
            "matsuyama_current": wayback_cdx(MATSU_CURRENT),
            "matsuyama_old_3669": wayback_cdx(MATSU_OLD_CATALOG[0]),
            "matsuyama_old_3375": wayback_cdx(MATSU_OLD_CATALOG[1]),
        },
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
