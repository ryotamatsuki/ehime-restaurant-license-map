from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from io import BytesIO, StringIO
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SNAP = ROOT / "data" / "snapshots"
REPORT = ROOT / "docs" / "research" / "CURRENT_DATA_AUDIT.json"

RAW.mkdir(parents=True, exist_ok=True)
SNAP.mkdir(parents=True, exist_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)

UA = "ehime-restaurant-license-map/0.2 (+https://github.com/ryotamatsuki/ehime-restaurant-license-map)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": UA})

PREF_API = "https://www.pref.ehime.jp/opendata-catalog/api/package_show?id=44d962fa-8684-4be1-9437-030298a483f3"
MATSU_MONTHLY = "https://www.city.matsuyama.ehime.jp/shisei/opendata/metadata/shokuhinsinki.html"
MATSU_ALL = "https://www.city.matsuyama.ehime.jp/shisei/opendata/metadata/shokuhin.html"

CANONICAL = [
    "source_authority",
    "source_snapshot_date",
    "permit_number",
    "initial_permit_date",
    "permit_date",
    "permit_expiry_date",
    "business_type",
    "facility_name",
    "facility_address",
    "municipality_code",
    "town_id",
    "latitude",
    "longitude",
    "application_type",
    "record_scope",
    "source_url",
    "source_sha256",
]

ALIASES = {
    "permit_number": ["許可番号", "営業許可番号", "許可・届出番号", "許可届出番号"],
    "initial_permit_date": ["初回許可年月日", "新規許可日", "新規許可年月日"],
    "permit_date": ["許可年月日", "新規許可日", "新規許可年月日", "許可日", "営業許可年月日"],
    "permit_expiry_date": ["許可満了日", "許可有効期限", "有効期限", "営業許可有効期限"],
    "business_type": ["営業の種類", "営業種別", "営業許可業種", "業種"],
    "facility_name": ["施設名称", "営業所名称", "営業施設名称", "施設名称1", "名称"],
    "facility_address": ["所在地＿連結表記", "営業所所在地", "施設所在地", "営業施設所在地", "所在地"],
    "municipality_code": ["所在地＿全国地方公共団体コード", "全国地方公共団体コード"],
    "town_id": ["町字ID"],
    "latitude": ["緯度"],
    "longitude": ["経度"],
    "application_type": ["申請区分"],
}
FORBIDDEN_HEADER_TERMS = [
    "申請者氏名", "申請者カナ", "申請者住所", "申請者所在地",
    "申請者個人名", "法人代表者氏名", "電話番号", "営業所電話番号",
    "施設電話番号", "連絡先メールアドレス",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get(url: str) -> requests.Response:
    r = SESSION.get(url, timeout=60)
    r.raise_for_status()
    return r


def normalize_header(x) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    return re.sub(r"[\s\u3000]+", "", str(x)).strip()


def find_header_row(raw: pd.DataFrame, max_rows: int = 30) -> int | None:
    alias_set = {normalize_header(v) for vals in ALIASES.values() for v in vals}
    best = None
    best_score = 0
    for i in range(min(max_rows, len(raw))):
        vals = {normalize_header(v) for v in raw.iloc[i].tolist()}
        score = len(vals & alias_set)
        if score > best_score:
            best, best_score = i, score
    return best if best_score >= 3 else None


def find_col(columns, aliases):
    norm_to_original = {normalize_header(c): c for c in columns}
    for a in aliases:
        if normalize_header(a) in norm_to_original:
            return norm_to_original[normalize_header(a)]
    return None


def clean_date_series(s: pd.Series) -> pd.Series:
    dt = pd.to_datetime(s, errors="coerce")
    return dt.dt.strftime("%Y-%m-%d").where(dt.notna(), "")


def clean_text_series(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip()


def optional_text(df: pd.DataFrame, col):
    if col is None:
        return pd.Series([""] * len(df), index=df.index, dtype="object")
    return clean_text_series(df[col])


def build_facility_name(df: pd.DataFrame, primary):
    out = optional_text(df, primary)
    if primary is not None and normalize_header(primary) == normalize_header("施設名称1"):
        second = find_col(df.columns, ["施設名称2"])
        if second is not None:
            out = (out + optional_text(df, second)).str.strip()
    return out


def build_facility_address(df: pd.DataFrame, primary):
    out = optional_text(df, primary)
    if primary is not None and normalize_header(primary) == normalize_header("営業所所在地"):
        continuation_cols = [
            c for c in df.columns if normalize_header(c).startswith(normalize_header("営業所所在地（続き）"))
        ]
        for c in continuation_cols:
            out = out + optional_text(df, c)
        out = out.str.strip()
    return out


def sanitize_frame(df: pd.DataFrame, authority: str, snapshot_date: str, scope: str, source_url: str, source_sha: str):
    mapping = {k: find_col(df.columns, v) for k, v in ALIASES.items()}
    required = ["permit_number", "permit_date", "business_type", "facility_name", "facility_address"]
    missing_required = [k for k in required if mapping.get(k) is None]
    if missing_required:
        raise ValueError(f"Required columns not found: {missing_required}; columns={list(map(str, df.columns))}")

    out = pd.DataFrame(index=df.index)
    out["source_authority"] = authority
    out["source_snapshot_date"] = snapshot_date
    out["permit_number"] = optional_text(df, mapping["permit_number"])
    if mapping.get("initial_permit_date"):
        out["initial_permit_date"] = clean_date_series(df[mapping["initial_permit_date"]])
    else:
        out["initial_permit_date"] = ""
    out["permit_date"] = clean_date_series(df[mapping["permit_date"]])
    if mapping.get("permit_expiry_date"):
        out["permit_expiry_date"] = clean_date_series(df[mapping["permit_expiry_date"]])
    else:
        out["permit_expiry_date"] = ""
    out["business_type"] = optional_text(df, mapping["business_type"])
    out["facility_name"] = build_facility_name(df, mapping["facility_name"])
    out["facility_address"] = build_facility_address(df, mapping["facility_address"])
    out["municipality_code"] = optional_text(df, mapping.get("municipality_code"))
    out["town_id"] = optional_text(df, mapping.get("town_id"))
    out["latitude"] = optional_text(df, mapping.get("latitude"))
    out["longitude"] = optional_text(df, mapping.get("longitude"))
    out["application_type"] = optional_text(df, mapping.get("application_type"))
    out["record_scope"] = scope
    out["source_url"] = source_url
    out["source_sha256"] = source_sha

    out = out[CANONICAL]
    out = out[(out["permit_number"] != "") | (out["facility_name"] != "") | (out["facility_address"] != "")].copy()
    return out, mapping


def parse_excel(data: bytes):
    xls = pd.ExcelFile(BytesIO(data), engine="openpyxl")
    results = []
    for sheet in xls.sheet_names:
        raw = pd.read_excel(BytesIO(data), sheet_name=sheet, header=None, engine="openpyxl")
        header_row = find_header_row(raw)
        if header_row is None:
            results.append({"sheet": sheet, "status": "no_header", "raw_shape": list(raw.shape)})
            continue
        df = pd.read_excel(BytesIO(data), sheet_name=sheet, header=header_row, engine="openpyxl")
        df = df.dropna(how="all")
        results.append({"sheet": sheet, "status": "parsed", "header_row": header_row, "df": df})
    return results


def decode_csv(data: bytes):
    for enc in ["utf-8-sig", "utf-8", "cp932", "shift_jis"]:
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            pass
    raise UnicodeDecodeError("unknown", b"", 0, 1, "Could not decode CSV")


def parse_csv_with_header_scan(decoded: str):
    raw = pd.read_csv(StringIO(decoded), header=None, dtype=str, keep_default_na=False)
    header_row = find_header_row(raw)
    if header_row is None:
        raise ValueError(f"Could not identify CSV header row; shape={raw.shape}")
    df = pd.read_csv(StringIO(decoded), header=header_row, dtype=str, keep_default_na=False)
    return df.dropna(how="all"), header_row


def snapshot_from_name(name: str) -> str:
    m = re.search(r"R(\d+)\.(\d+)\.(\d+)", name)
    if m:
        y, mo, d = map(int, m.groups())
        return f"{2018+y:04d}-{mo:02d}-{d:02d}"
    m = re.search(r"R(\d+)\.(\d+)月", name)
    if m:
        y, mo = map(int, m.groups())
        return f"{2018+y:04d}-{mo:02d}"
    m = re.search(r"(\d{4})年(\d{1,2})月", name)
    if m:
        y, mo = map(int, m.groups())
        return f"{y:04d}-{mo:02d}"
    return datetime.now(timezone.utc).date().isoformat()


def safe_slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")[:80] or "snapshot"


def write_snapshot(df: pd.DataFrame, filename: str):
    path = SNAP / filename
    df.to_csv(path, index=False, encoding="utf-8")
    bad = [c for c in df.columns if any(term in c for term in FORBIDDEN_HEADER_TERMS)]
    if bad:
        raise RuntimeError(f"Forbidden columns in output: {bad}")
    return str(path.relative_to(ROOT))


def audit_output(df: pd.DataFrame):
    lat_present = (df["latitude"] != "") & (df["longitude"] != "")
    return {
        "rows": int(len(df)),
        "missing_permit_date": int((df["permit_date"] == "").sum()),
        "missing_facility_address": int((df["facility_address"] == "").sum()),
        "duplicate_permit_number_rows": int(df["permit_number"].duplicated(keep=False).sum()),
        "rows_with_coordinates": int(lat_present.sum()),
        "application_type_counts": {str(k): int(v) for k, v in df["application_type"].value_counts().head(20).items() if str(k) != ""},
        "business_type_top10": {str(k): int(v) for k, v in df["business_type"].value_counts().head(10).items()},
    }


def discover_links(page_url: str, extensions: tuple[str, ...]):
    response = get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        absolute = urljoin(page_url, href)
        path_lower = absolute.lower().split("?")[0]
        if any(path_lower.endswith(ext) for ext in extensions):
            links.append((a.get_text(" ", strip=True), absolute))
    out, seen = [], set()
    for text, url in links:
        if url not in seen:
            seen.add(url)
            out.append((text, url))
    return out


def process_ehime(report):
    meta = get(PREF_API).json()
    resources = meta["result"]["resources"]
    if not resources:
        raise RuntimeError("Ehime metadata API returned no resources")
    res = resources[0]
    url = res["download_url"]
    data = get(url).content
    sha = sha256_bytes(data)
    name = res["name"]
    snapshot_date = snapshot_from_name(name)
    parsed = parse_excel(data)
    entry = {
        "authority": "愛媛県",
        "source_url": url,
        "resource_internal_id": res.get("id"),
        "resource_name": name,
        "sha256": sha,
        "bytes": len(data),
        "sheets": [],
        "outputs": [],
    }
    for item in parsed:
        if item["status"] != "parsed":
            entry["sheets"].append(item)
            continue
        sheet = item["sheet"]
        df = item["df"]
        scope = "new" if "新規" in sheet else ("all" if "全" in sheet else "unknown")
        try:
            out, mapping = sanitize_frame(df, "愛媛県", snapshot_date, scope, url, sha)
        except Exception as e:
            entry["sheets"].append({
                "sheet": sheet, "status": "schema_error", "error": str(e),
                "columns": [str(c) for c in df.columns],
            })
            continue
        fname = f"ehime_prefecture_{safe_slug(snapshot_date)}_{scope}.csv"
        rel = write_snapshot(out, fname)
        entry["sheets"].append({
            "sheet": sheet,
            "status": "sanitized",
            "columns": [str(c) for c in df.columns],
            "mapping": {k: (None if v is None else str(v)) for k, v in mapping.items()},
            **audit_output(out),
        })
        entry["outputs"].append(rel)
    report["sources"]["ehime_prefecture"] = entry


def process_matsuyama_monthly(report):
    links = discover_links(MATSU_MONTHLY, (".xlsx", ".xls"))
    if not links:
        raise RuntimeError("No Excel link discovered on Matsuyama monthly page")
    text, url = next(((t, u) for t, u in links if "食品" in t or "許可" in t), links[0])
    data = get(url).content
    sha = sha256_bytes(data)
    parsed = parse_excel(data)
    entry = {
        "authority": "松山市",
        "source_url": url,
        "anchor_text": text,
        "sha256": sha,
        "bytes": len(data),
        "sheets": [],
        "outputs": [],
    }
    for item in parsed:
        if item["status"] != "parsed":
            entry["sheets"].append(item)
            continue
        sheet, df = item["sheet"], item["df"]
        snapshot_date = snapshot_from_name(sheet)
        try:
            out, mapping = sanitize_frame(df, "松山市", snapshot_date, "new_or_renewal", url, sha)
        except Exception as e:
            entry["sheets"].append({
                "sheet": sheet, "status": "schema_error", "error": str(e),
                "columns": [str(c) for c in df.columns],
            })
            continue
        fname = f"matsuyama_monthly_{safe_slug(snapshot_date)}.csv"
        rel = write_snapshot(out, fname)
        entry["sheets"].append({
            "sheet": sheet, "status": "sanitized",
            "columns": [str(c) for c in df.columns],
            "mapping": {k: (None if v is None else str(v)) for k, v in mapping.items()},
            **audit_output(out),
        })
        entry["outputs"].append(rel)
    report["sources"]["matsuyama_monthly"] = entry


def process_matsuyama_all(report):
    links = discover_links(MATSU_ALL, (".csv",))
    if not links:
        raise RuntimeError("No CSV links discovered on Matsuyama all-facilities page")
    entry = {"authority": "松山市", "landing_url": MATSU_ALL, "files": [], "outputs": []}
    for idx, (text, url) in enumerate(links, 1):
        data = get(url).content
        sha = sha256_bytes(data)
        decoded, enc = decode_csv(data)
        df, header_row = parse_csv_with_header_scan(decoded)
        snapshot_date = "2026-03-31"
        try:
            out, mapping = sanitize_frame(df, "松山市", snapshot_date, "all", url, sha)
        except Exception as e:
            entry["files"].append({
                "anchor_text": text, "source_url": url, "status": "schema_error",
                "error": str(e), "encoding": enc, "header_row": header_row,
                "columns": [str(c) for c in df.columns],
            })
            continue
        fname = f"matsuyama_all_2026-03-31_part{idx}.csv"
        rel = write_snapshot(out, fname)
        entry["files"].append({
            "anchor_text": text, "source_url": url, "status": "sanitized",
            "sha256": sha, "bytes": len(data), "encoding": enc, "header_row": header_row,
            "columns": [str(c) for c in df.columns],
            "mapping": {k: (None if v is None else str(v)) for k, v in mapping.items()},
            **audit_output(out),
        })
        entry["outputs"].append(rel)
    report["sources"]["matsuyama_all"] = entry


def main():
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": "ryotamatsuki/ehime-restaurant-license-map",
        "privacy_policy": {
            "raw_files_committed": False,
            "direct_identifier_columns_committed": False,
        },
        "sources": {},
        "errors": {},
    }
    processors = [
        ("ehime_prefecture", process_ehime),
        ("matsuyama_monthly", process_matsuyama_monthly),
        ("matsuyama_all", process_matsuyama_all),
    ]
    for name, fn in processors:
        try:
            fn(report)
        except Exception as e:
            report["errors"][name] = f"{type(e).__name__}: {e}"
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["errors"]:
        return 2
    for source in report["sources"].values():
        if not source.get("outputs"):
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
