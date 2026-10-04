from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "processed" / "permit_events_observed.csv"
OUT_DIR = ROOT / "data" / "geocode"
OUTPUT = OUT_DIR / "geocode_input.json"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_address(value: str) -> str:
    if not value:
        return ""
    x = unicodedata.normalize("NFKC", str(value)).strip()
    x = re.sub(r"[\u3000\t\r\n]+", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


def geocode_input(raw: str) -> str:
    if not raw:
        return ""
    return raw if raw.startswith("愛媛県") else f"愛媛県{raw}"


def key_for(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def main() -> None:
    df = pd.read_csv(INPUT, dtype=str, keep_default_na=False)
    if "facility_address" not in df.columns:
        raise RuntimeError("facility_address missing from Stage 3 event panel")

    df["_clean_address"] = df["facility_address"].map(clean_address)
    counts = Counter(df["_clean_address"])
    restaurant_counts = Counter(
        df.loc[df["is_restaurant"].str.lower().eq("true"), "_clean_address"]
    )
    authorities = (
        df.groupby("_clean_address")["source_authority"]
        .agg(lambda s: sorted(set(s)))
        .to_dict()
    )

    items = []
    for raw in sorted(counts):
        if not raw:
            continue
        items.append({
            "address_key": key_for(raw),
            "source_address": raw,
            "geocode_input": geocode_input(raw),
            "event_count": int(counts[raw]),
            "restaurant_event_count": int(restaurant_counts.get(raw, 0)),
            "authorities": authorities.get(raw, []),
        })

    payload = {
        "schema_version": 1,
        "source": str(INPUT.relative_to(ROOT)),
        "event_rows": int(len(df)),
        "unique_nonempty_addresses": len(items),
        "empty_address_rows": int((df["_clean_address"] == "").sum()),
        "items": items,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "items"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
