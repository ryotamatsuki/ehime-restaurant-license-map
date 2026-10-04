from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "processed" / "permit_events_retrospective_partial.csv"
OUT = ROOT / "data" / "geocode" / "matsuyama_retrospective_input.json"
OUT.parent.mkdir(parents=True, exist_ok=True)


def clean_address(value: str) -> str:
    x = unicodedata.normalize("NFKC", str(value or "")).strip()
    x = re.sub(r"[\u3000\t\r\n]+", " ", x)
    return re.sub(r"\s+", " ", x).strip()


def key_for(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def main() -> None:
    df = pd.read_csv(SRC, dtype=str, keep_default_na=False)
    df = df[
        (df["source_authority"] == "松山市")
        & df["is_restaurant"].astype(str).str.lower().eq("true")
        & (df["historical_month"] >= "2021-06")
        & (df["historical_month"] <= "2024-08")
    ].copy()
    df["_address"] = df["facility_address"].map(clean_address)

    counts = Counter(df["_address"])
    items=[]
    for address in sorted(counts):
        if not address:
            continue
        items.append({
            "address_key":key_for(address),
            "source_address":address,
            "geocode_input":address if address.startswith("愛媛県") else "愛媛県"+address,
            "row_count":int(counts[address]),
        })

    payload={
        "schema_version":1,
        "period":["2021-06","2024-08"],
        "restaurant_rows":int(len(df)),
        "unique_nonempty_addresses":len(items),
        "items":items,
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in payload.items() if k!="items"},ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
