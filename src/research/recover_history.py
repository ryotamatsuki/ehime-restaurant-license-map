from __future__ import annotations

import hashlib
import json
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

from src.acquire.current import parse_excel, sanitize_frame, audit_output

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "snapshots" / "history"
REPORT = ROOT / "docs" / "research" / "HISTORY_RECOVERY.json"
OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)

S = requests.Session()
S.headers.update({
    "User-Agent": "ehime-restaurant-license-map-history-recovery/0.1 (+https://github.com/ryotamatsuki/ehime-restaurant-license-map)"
})

EHIME_PATTERN = "https://www.pref.ehime.jp/opendata-catalog/dataset/2344/resource/*"
MATSU_XLSX = "https://www.city.matsuyama.ehime.jp/shisei/opendata/metadata/shokuhinsinki.files/shokuhinsinki.xlsx"

FORBIDDEN = [
    "申請者氏名", "申請者カナ", "申請者住所", "申請者所在地",
    "申請者個人名", "法人代表者氏名", "電話番号", "営業所電話番号",
    "施設電話番号", "連絡先メールアドレス",
]


def cdx(url_pattern: str, collapse: str) -> list[dict]:
    endpoint = "https://web.archive.org/cdx/search/cdx"
    params = [
        ("url", url_pattern),
        ("output", "json"),
        ("filter", "statuscode:200"),
        ("fl", "timestamp,original,statuscode,mimetype,digest,length"),
        ("collapse", collapse),
        ("from", "2021"),
        ("to", "2026"),
        ("limit", "5000"),
    ]
    r = S.get(endpoint, params=params, timeout=90)
    r.raise_for_status()
    data = r.json()
    if not data:
        return []
    header = data[0]
    return [dict(zip(header, row)) for row in data[1:]]


def archive_bytes(timestamp: str, original: str) -> bytes:
    url = f"https://web.archive.org/web/{timestamp}id_/{original}"
    last = None
    for i in range(4):
        try:
            r = S.get(url, timeout=90)
            r.raise_for_status()
            data = r.content
            if not data.startswith(b"PK"):
                raise ValueError(f"not XLSX/ZIP signature: content-type={r.headers.get('content-type')}")
            return data
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"archive download failed: {last}")


def file_sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def month_from_sheet(sheet: str) -> str | None:
    m = re.search(r"(\d{4})年(\d{1,2})月", sheet)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}"
    m = re.search(r"R(\d+)\.(\d+)月", sheet)
    if m:
        return f"{2018 + int(m.group(1)):04d}-{int(m.group(2)):02d}"
    return None


def month_from_ehime_name(text: str) -> str | None:
    m = re.search(r"R(\d+)\.(\d+)月", text)
    if not m:
        return None
    return f"{2018 + int(m.group(1)):04d}-{int(m.group(2)):02d}"


def write_safe(df: pd.DataFrame, path: Path):
    bad = [c for c in df.columns if any(term in c for term in FORBIDDEN)]
    if bad:
        raise RuntimeError(f"forbidden output columns: {bad}")
    df.to_csv(path, index=False, encoding="utf-8")


def compact_audit(df: pd.DataFrame):
    a = audit_output(df)
    return {
        "rows": a["rows"],
        "missing_permit_date": a["missing_permit_date"],
        "missing_facility_address": a["missing_facility_address"],
        "duplicate_permit_number_rows": a["duplicate_permit_number_rows"],
        "business_type_top10": a["business_type_top10"],
    }


def recover_ehime(report: dict):
    rows = cdx(EHIME_PATTERN, "urlkey")
    candidates = []
    for row in rows:
        original = row.get("original", "")
        ts = row.get("timestamp", "")
        decoded_name = requests.utils.unquote(original)
        if ".xlsx" not in decoded_name.lower():
            continue
        if "dataset/2344/resource/" not in decoded_name:
            continue
        month = month_from_ehime_name(decoded_name)
        if not month:
            continue
        # Privacy incident: never ingest any archived July-2026 workbook.
        if month == "2026-07":
            report["safety_exclusions"].append({
                "authority": "愛媛県",
                "month": month,
                "timestamp": ts,
                "original": original,
                "reason": "R8.7 source excluded from archives due 2026-08 privacy incident; only independently verified corrected source may be used."
            })
            continue
        candidates.append((month, ts, original, row.get("digest")))

    # Prefer latest archived capture per month.
    by_month = defaultdict(list)
    for x in candidates:
        by_month[x[0]].append(x)

    for month, items in sorted(by_month.items()):
        items.sort(key=lambda x: x[1], reverse=True)
        recovered = None
        attempts = []
        for _, ts, original, digest in items:
            try:
                data = archive_bytes(ts, original)
                sha = file_sha(data)
                parsed = parse_excel(data)
                new_sheets = [p for p in parsed if p.get("status") == "parsed" and "新規" in p.get("sheet", "")]
                if not new_sheets:
                    raise ValueError("no parsed new-permit sheet")
                p = new_sheets[0]
                out, mapping = sanitize_frame(
                    p["df"], "愛媛県", month, "new",
                    f"wayback:{ts}:{original}", sha
                )
                target = OUT_DIR / f"ehime_prefecture_{month}_new_archive.csv"
                write_safe(out, target)
                recovered = {
                    "month": month,
                    "timestamp": ts,
                    "original": original,
                    "archive_sha256": sha,
                    "output": str(target.relative_to(ROOT)),
                    "sheet": p["sheet"],
                    "mapping": {k: None if v is None else str(v) for k, v in mapping.items()},
                    **compact_audit(out),
                }
                break
            except Exception as e:
                attempts.append({
                    "timestamp": ts, "original": original,
                    "error": f"{type(e).__name__}: {e}"
                })
        if recovered:
            report["ehime"]["recovered"].append(recovered)
        else:
            report["ehime"]["failed_months"].append({"month": month, "attempts": attempts})

    report["ehime"]["cdx_rows"] = len(rows)
    report["ehime"]["candidate_months"] = sorted(by_month)


def recover_matsuyama(report: dict):
    rows = cdx(MATSU_XLSX, "digest")
    # Process captures oldest -> newest. Latest successfully recovered version wins for a month.
    month_versions = defaultdict(list)
    for row in sorted(rows, key=lambda r: r.get("timestamp", "")):
        ts = row.get("timestamp", "")
        original = row.get("original", MATSU_XLSX)
        try:
            data = archive_bytes(ts, original)
            sha = file_sha(data)
            parsed = parse_excel(data)
            workbook_months = []
            for p in parsed:
                if p.get("status") != "parsed":
                    continue
                month = month_from_sheet(p.get("sheet", ""))
                if not month:
                    continue
                try:
                    out, mapping = sanitize_frame(
                        p["df"], "松山市", month, "new_or_renewal",
                        f"wayback:{ts}:{original}", sha
                    )
                except Exception as e:
                    report["matsuyama"]["sheet_errors"].append({
                        "timestamp": ts, "sheet": p.get("sheet"),
                        "error": f"{type(e).__name__}: {e}"
                    })
                    continue
                signature_cols = [
                    "permit_number","initial_permit_date","permit_date","business_type",
                    "facility_name","facility_address"
                ]
                content_signature = hashlib.sha256(
                    out[signature_cols].sort_values(signature_cols).to_csv(index=False).encode("utf-8")
                ).hexdigest()
                month_versions[month].append({
                    "timestamp": ts,
                    "source_sha256": sha,
                    "source_url": original,
                    "content_signature": content_signature,
                    "df": out,
                    "mapping": {k: None if v is None else str(v) for k, v in mapping.items()},
                    "sheet": p.get("sheet"),
                })
                workbook_months.append(month)
            report["matsuyama"]["workbooks"].append({
                "timestamp": ts,
                "original": original,
                "source_sha256": sha,
                "months": sorted(set(workbook_months)),
            })
        except Exception as e:
            report["matsuyama"]["workbook_errors"].append({
                "timestamp": ts,
                "original": original,
                "error": f"{type(e).__name__}: {e}"
            })

    for month, versions in sorted(month_versions.items()):
        versions.sort(key=lambda v: v["timestamp"])
        latest = versions[-1]
        target = OUT_DIR / f"matsuyama_monthly_{month}_archive.csv"
        write_safe(latest["df"], target)
        signatures = sorted(set(v["content_signature"] for v in versions))
        report["matsuyama"]["recovered"].append({
            "month": month,
            "latest_timestamp": latest["timestamp"],
            "version_count": len(versions),
            "distinct_content_versions": len(signatures),
            "latest_content_signature": latest["content_signature"],
            "source_sha256": latest["source_sha256"],
            "output": str(target.relative_to(ROOT)),
            "sheet": latest["sheet"],
            "mapping": latest["mapping"],
            **compact_audit(latest["df"]),
        })

    report["matsuyama"]["cdx_rows"] = len(rows)
    report["matsuyama"]["recovered_months"] = sorted(month_versions)


def main():
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Internet Archive CDX + raw archived XLSX; raw files are processed in-memory and never committed.",
        "safety_exclusions": [],
        "ehime": {"recovered": [], "failed_months": []},
        "matsuyama": {
            "recovered": [], "workbooks": [], "workbook_errors": [], "sheet_errors": []
        },
    }
    try:
        recover_ehime(report)
    except Exception as e:
        report["ehime"]["fatal_error"] = f"{type(e).__name__}: {e}"
    try:
        recover_matsuyama(report)
    except Exception as e:
        report["matsuyama"]["fatal_error"] = f"{type(e).__name__}: {e}"

    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if report["ehime"].get("fatal_error") or report["matsuyama"].get("fatal_error"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
