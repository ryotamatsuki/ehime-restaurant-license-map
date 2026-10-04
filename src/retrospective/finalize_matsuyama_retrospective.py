from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"data"/"processed"/"permit_events_retrospective_partial.csv"
CACHE=ROOT/"data"/"geocode"/"matsuyama_retrospective_geocode_cache.json"
OUT=ROOT/"data"/"processed"/"matsuyama_restaurant_retrospective_geocoded.csv"
REPORT=ROOT/"docs"/"research"/"MATSUYAMA_RETROSPECTIVE_GEOCODE_AUDIT.json"


def clean(value:str)->str:
    x=unicodedata.normalize("NFKC",str(value or "")).strip()
    x=re.sub(r"[\u3000\t\r\n]+"," ",x)
    return re.sub(r"\s+"," ",x).strip()


def key_for(raw:str)->str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def valid(lat,lon)->bool:
    try:
        return 33.5 <= float(lat) <= 34.2 and 132.3 <= float(lon) <= 133.2
    except Exception:
        return False


def main()->int:
    df=pd.read_csv(SRC,dtype=str,keep_default_na=False)
    df=df[
        (df["source_authority"]=="松山市")
        & df["is_restaurant"].astype(str).str.lower().eq("true")
        & (df["historical_month"]>="2021-06")
        & (df["historical_month"]<="2024-08")
    ].copy()

    payload=json.loads(CACHE.read_text(encoding="utf-8"))
    cache={r["address_key"]:r for r in payload["results"]}

    df["address_key"]=df["facility_address"].map(clean).map(key_for)
    fields=["normalized_city","normalized_town","normalized_addr","unmatched_other","point_level","latitude","longitude","geocode_quality","error"]
    for field in fields:
        target="geocode_error" if field=="error" else field
        df[target]=df["address_key"].map(lambda k,f=field:cache.get(k,{}).get(f,""))

    df["coordinate_valid_matsuyama"]=df.apply(lambda r:valid(r["latitude"],r["longitude"]),axis=1)
    df["map_usable_strict"]=(df["geocode_quality"]=="address_or_parcel") & df["coordinate_valid_matsuyama"]
    df["map_usable_town_or_better"]=df["geocode_quality"].isin(["address_or_parcel","town_centroid"]) & df["coordinate_valid_matsuyama"]
    df["evidence_quality"]="retrospective_partial_survivor_biased"

    OUT.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(OUT,index=False,encoding="utf-8")

    monthly=(
        df.groupby("historical_month")
        .agg(
            rows=("retrospective_id","nunique"),
            strict=("map_usable_strict","sum"),
            town_or_better=("map_usable_town_or_better","sum"),
        )
        .reset_index()
        .rename(columns={"historical_month":"month"})
    )

    report={
        "period":["2021-06","2024-08"],
        "rows":int(len(df)),
        "strict_address_or_parcel":int(df["map_usable_strict"].sum()),
        "town_or_better":int(df["map_usable_town_or_better"].sum()),
        "quality_counts":{str(k):int(v) for k,v in df["geocode_quality"].value_counts().items()},
        "invalid_matsuyama_coordinates":int((~df["coordinate_valid_matsuyama"]).sum()),
        "monthly":monthly.to_dict(orient="records"),
        "interpretation":"Incomplete retrospective series from facilities present in the 2026-03-31 all-facilities snapshot; not complete historical new-permit counts.",
    }
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

    if len(df)!=3743:
        return 2
    if report["invalid_matsuyama_coordinates"]>0:
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
