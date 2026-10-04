from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SNAP = ROOT / "data" / "snapshots"
HIST = SNAP / "history"
OUT = ROOT / "data" / "processed"
DOCS = ROOT / "docs" / "research"
OUT.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

# Stage 3 audited reconstruction window.
START_MONTH = "2021-12"
END_MONTH = "2026-08"

KEY_COLS = [
    "source_authority","source_snapshot_date","permit_number","initial_permit_date",
    "permit_date","permit_expiry_date","business_type","facility_name","facility_address",
    "municipality_code","town_id","latitude","longitude","application_type","record_scope",
    "source_url","source_sha256"
]


def read_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for c in KEY_COLS:
        if c not in df.columns:
            df[c] = ""
    return df[KEY_COLS].copy()


def norm(s) -> str:
    if pd.isna(s):
        return ""
    return str(s).strip()


def restaurant_label(s: str) -> bool:
    x = re.sub(r"^[①-㊿]\s*", "", norm(s))
    return x == "飲食店営業"


def classify_event(row) -> str:
    if norm(row["source_authority"]) == "愛媛県" and norm(row["record_scope"]) == "new":
        return "new"
    initial = norm(row["initial_permit_date"])
    permit = norm(row["permit_date"])
    if initial and permit:
        return "new" if initial == permit else "renewal"
    return "unknown"


def make_event_id(row) -> str:
    parts = [
        norm(row["source_authority"]),
        norm(row["permit_date"]),
        norm(row["permit_number"]),
        norm(row["business_type"]),
        norm(row["facility_name"]),
        norm(row["facility_address"]),
    ]
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:24]


def exact_sources():
    specs = []
    current_ehime = SNAP / "ehime_prefecture_2026-08-31_new.csv"
    if current_ehime.exists():
        specs.append(("愛媛県", "2026-08", current_ehime, "official_current_monthly"))
    for p in sorted(HIST.glob("ehime_prefecture_*_new_archive.csv")):
        m = re.search(r"(\d{4}-\d{2})", p.name)
        if m:
            specs.append(("愛媛県", m.group(1), p, "wayback_archived_monthly"))

    for p in sorted(SNAP.glob("matsuyama_monthly_????-??.csv")):
        m = re.search(r"(\d{4}-\d{2})", p.name)
        if m:
            specs.append(("松山市", m.group(1), p, "official_current_rolling_workbook"))
    for p in sorted(HIST.glob("matsuyama_monthly_*_archive.csv")):
        m = re.search(r"(\d{4}-\d{2})", p.name)
        if m:
            specs.append(("松山市", m.group(1), p, "wayback_archived_rolling_workbook"))

    # Current official files win over archived duplicates for the same authority/month.
    priority = {
        "official_current_monthly": 3,
        "official_current_rolling_workbook": 3,
        "wayback_archived_monthly": 2,
        "wayback_archived_rolling_workbook": 2,
    }
    best = {}
    for authority, month, path, kind in specs:
        k=(authority,month)
        if k not in best or priority[kind] > priority[best[k][3]]:
            best[k]=(authority,month,path,kind)
    return [best[k] for k in sorted(best)]


def build_exact():
    frames=[]
    manifest=[]
    for authority,month,path,kind in exact_sources():
        df=read_csv(path)
        df["source_kind"]=kind
        df["coverage_month"]=month
        df["event_type"]=df.apply(classify_event,axis=1)
        df["event_id"]=df.apply(make_event_id,axis=1)
        df["is_restaurant"]=df["business_type"].map(restaurant_label)
        frames.append(df)
        manifest.append({
            "authority":authority,"month":month,
            "path":str(path.relative_to(ROOT)),"source_kind":kind,
            "rows":int(len(df)),
            "new_rows":int((df["event_type"]=="new").sum()),
            "renewal_rows":int((df["event_type"]=="renewal").sum()),
            "restaurant_rows":int(df["is_restaurant"].sum()),
        })
    if not frames:
        return pd.DataFrame(),manifest,0
    panel=pd.concat(frames,ignore_index=True)
    before=len(panel)
    panel=panel.sort_values(
        ["source_authority","permit_date","permit_number","business_type","facility_name","facility_address","source_kind"],
        kind="stable"
    ).drop_duplicates("event_id",keep="last").reset_index(drop=True)
    return panel,manifest,before-len(panel)


def retrospective_sources():
    specs=[]
    p=SNAP/"ehime_prefecture_2026-08-31_all.csv"
    if p.exists():
        specs.append(("愛媛県","2026-08",p))
    for p in sorted(SNAP.glob("matsuyama_all_2026-03-31_part*.csv")):
        specs.append(("松山市","2026-03",p))
    return specs


def build_retrospective():
    frames=[]
    manifest=[]
    for authority,snapshot_month,path in retrospective_sources():
        df=read_csv(path)
        # For these sources initial_permit_date is populated where source supplies usable history.
        df["historical_month"]=df["initial_permit_date"].str.slice(0,7)
        df["retrospective_id"]=df.apply(make_event_id,axis=1)
        df["is_restaurant"]=df["business_type"].map(restaurant_label)
        df["evidence_quality"]="retrospective_all_facilities_snapshot"
        usable=df[df["historical_month"].str.match(r"^\d{4}-\d{2}$",na=False)].copy()
        frames.append(usable)
        manifest.append({
            "authority":authority,
            "snapshot_month":snapshot_month,
            "path":str(path.relative_to(ROOT)),
            "rows":int(len(df)),
            "usable_historical_date_rows":int(len(usable)),
            "restaurant_rows":int(usable["is_restaurant"].sum()),
        })
    if not frames:
        return pd.DataFrame(),manifest
    panel=pd.concat(frames,ignore_index=True)
    panel=panel.drop_duplicates("retrospective_id",keep="last").reset_index(drop=True)
    return panel,manifest


def month_range():
    return [str(p) for p in pd.period_range(START_MONTH,END_MONTH,freq="M")]


def coverage_matrix(exact: pd.DataFrame, retro: pd.DataFrame):
    exact_groups={}
    if len(exact):
        for (a,m),g in exact.groupby(["source_authority","coverage_month"]):
            exact_groups[(a,m)]=g
    retro_groups={}
    if len(retro):
        for (a,m),g in retro.groupby(["source_authority","historical_month"]):
            retro_groups[(a,m)]=g

    rows=[]
    for authority in ["愛媛県","松山市"]:
        for month in month_range():
            eg=exact_groups.get((authority,month))
            rg=retro_groups.get((authority,month))
            exact_rows=0 if eg is None else len(eg)
            exact_new=0 if eg is None else int((eg["event_type"]=="new").sum())
            exact_renewal=0 if eg is None else int((eg["event_type"]=="renewal").sum())
            exact_rest=0 if eg is None else int(eg["is_restaurant"].sum())
            retro_rows=0 if rg is None else len(rg)
            retro_rest=0 if rg is None else int(rg["is_restaurant"].sum())

            if eg is not None:
                status="complete_exact_monthly"
                basis="published monthly/new-or-renewal source recovered and parsed"
            else:
                if authority=="愛媛県" and month <= "2026-08":
                    status="partial_retrospective"
                    basis="2026-08-31 all-facilities snapshot can retrospectively identify surviving/listed records, but is not a complete monthly event archive"
                elif authority=="松山市" and month <= "2026-03":
                    status="partial_retrospective"
                    basis="2026-03-31 all-facilities snapshot can retrospectively identify surviving/listed records, but is not a complete monthly event archive"
                else:
                    status="unavailable"
                    basis="no exact monthly source recovered and no later all-facilities snapshot covering this month"

            rows.append({
                "authority":authority,
                "month":month,
                "coverage_status":status,
                "exact_rows":int(exact_rows),
                "exact_new_rows":int(exact_new),
                "exact_renewal_rows":int(exact_renewal),
                "exact_restaurant_rows":int(exact_rest),
                "retrospective_rows":int(retro_rows),
                "retrospective_restaurant_rows":int(retro_rest),
                "basis":basis,
            })
    return pd.DataFrame(rows)


def contiguous_windows(months):
    periods=sorted(pd.Period(m,freq="M") for m in months)
    if not periods:
        return []
    windows=[]
    start=prev=periods[0]
    for p in periods[1:]:
        if p == prev + 1:
            prev=p
            continue
        windows.append([str(start),str(prev)])
        start=prev=p
    windows.append([str(start),str(prev)])
    return windows


def main():
    exact, exact_manifest, deduped = build_exact()
    retro, retro_manifest = build_retrospective()
    coverage=coverage_matrix(exact,retro)

    exact_path=OUT/"permit_events_observed.csv"
    exact_rest_path=OUT/"restaurant_permit_events_observed.csv"
    retro_path=OUT/"permit_events_retrospective_partial.csv"
    coverage_path=OUT/"coverage_matrix.csv"

    exact.to_csv(exact_path,index=False,encoding="utf-8")
    exact[exact["is_restaurant"]].to_csv(exact_rest_path,index=False,encoding="utf-8")
    retro.to_csv(retro_path,index=False,encoding="utf-8")
    coverage.to_csv(coverage_path,index=False,encoding="utf-8")

    exact_months={}
    for authority in ["愛媛県","松山市"]:
        months=coverage.loc[
            (coverage["authority"]==authority)&
            (coverage["coverage_status"]=="complete_exact_monthly"),
            "month"
        ].tolist()
        exact_months[authority]={
            "months":months,
            "continuous_windows":contiguous_windows(months),
            "count":len(months),
        }

    report={
        "stage":"3",
        "range":[START_MONTH,END_MONTH],
        "exact_source_manifest":exact_manifest,
        "retrospective_source_manifest":retro_manifest,
        "exact_rows_after_dedup":int(len(exact)),
        "exact_restaurant_rows":int(exact["is_restaurant"].sum()) if len(exact) else 0,
        "event_id_duplicates_removed":int(deduped),
        "event_type_counts":exact["event_type"].value_counts().to_dict() if len(exact) else {},
        "exact_months":exact_months,
        "coverage_status_counts":(
            coverage.groupby(["authority","coverage_status"]).size()
            .reset_index(name="months").to_dict(orient="records")
        ),
        "methodological_boundary":{
            "complete_exact_monthly":"May be used for month-level event counts and animation.",
            "partial_retrospective":"May be used for exploratory historical location context only; must not be presented as complete monthly opening/new-permit counts.",
            "unavailable":"No monthly count may be inferred.",
        },
        "outputs":[
            str(exact_path.relative_to(ROOT)),
            str(exact_rest_path.relative_to(ROOT)),
            str(retro_path.relative_to(ROOT)),
            str(coverage_path.relative_to(ROOT)),
        ],
    }
    (DOCS/"STAGE3_HISTORY_AUDIT.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8"
    )
    print(json.dumps(report,ensure_ascii=False,indent=2))

    # Hard QA
    if exact["event_id"].duplicated().any():
        return 2
    if set(coverage["coverage_status"]) - {
        "complete_exact_monthly","partial_retrospective","unavailable"
    }:
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
