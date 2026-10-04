# Matsuyama Cinematic Scene Extraction — Stage 8

Date: 2026-10-04  
Status: **PASS / COMPLETE**  
Scope: Matsuyama 2021-06 through 2026-07, 62-month hybrid timeline

## 1. Purpose

This stage converts the benchmark research in `URBAN_DATA_ANIMATION_BENCHMARK.md` into quantitative scene selection.

The objective is not to choose attractive months subjectively. It is to identify:

- which months contain strong temporal/spatial change;
- which 1km locations should receive camera attention;
- which clusters are persistent city cores versus temporary activity;
- which scenes are suitable for a guided cinematic narrative.

The output is a **storyboard seed**, not yet the cinematic renderer.

---

## 2. Input and evidence tiers

Hybrid timeline:

- 2021-06–2024-08: retrospective partial reconstruction
- 2024-09–2026-07: exact monthly observations
- total: 62 consecutive months

Rows used:

- retrospective restaurant rows: 3,743
- exact new restaurant permit rows: 2,281
- hybrid rows: 6,024
- strict address/parcel points usable for comparable fine-spatial analysis: 1,627

Fine-spatial metrics use the strict address/parcel subset in **both eras**, so the 1km analysis remains comparable even though the retrospective total-count series is incomplete.

Important:
- retrospective counts remain survivor/carry-forward biased;
- the 2021-06 opening month is a **source-boundary month** and its unusually high count is not interpreted as a real citywide spike.

---

## 3. Quantitative scene score

Every month is evaluated on five dimensions.

| Component | Weight |
|---|---:|
| permit-event volume | 25% |
| centroid movement | 15% |
| active-mesh churn | 15% |
| concentration / spatial-structure change | 20% |
| hotspot emergence or surge | 25% |

Spatial components are multiplied by:

`spatial_reliability = min(1, strict_points / 20)`

This prevents low-sample months from winning simply because HHI, centroid movement, or top-mesh share becomes unstable when only a few strict points exist.

Percentile scores are calculated **separately within each evidence era**. Retrospective and exact counts are therefore not treated as the same data-generating process.

Evidence-confidence score:
- retrospective partial = 65
- exact monthly = 100

Final editorial priority:
- 80% visual-interest score
- 20% evidence-confidence score

The 2024-09 evidence transition is a mandatory editorial scene.

---

## 4. Strongest month-level findings

### 4.1 2024-09 — mandatory evidence transition

Editorial score: **100**

- exact monthly observations begin;
- total new restaurant events: 139;
- strict points: 53;
- dominant 1km mesh: `50326622`;
- locality: 道後湯之町 / 道後鷺谷町 / 道後多幸町;
- dominant-mesh strict events: 15;
- dominant share of strict points: about 28%;
- increase in the strongest mesh versus previous month: +14;
- centroid movement: about 1.47 km.

There is also a strong secondary location event:
- 東石井四丁目 / 東石井三丁目 / 東石井六丁目;
- 4 strict events;
- previous 3-month total: 0;
- active in each of the next 3 months.

**Cinematic use:** a deliberate visual sharpening from “retrospective reconstruction” to “complete monthly observation,” followed by a push toward Dogo while a secondary Higashi-Ishii cluster appears.

---

### 4.2 2026-02 — strongest exact-period climax

Editorial score: **96.35**  
Visual-interest score: **95.43**

- total events: 158;
- strict points: 48;
- centroid movement from previous month: about **2.71 km**;
- dominant mesh: `50326622`;
- locality: 道後湯之町 / 道後緑台 / 祝谷町一丁目;
- Dogo strict events: **14**;
- change from previous month: **+14**;
- Dogo share of strict points: about **29%**;
- HHI: about 0.110.

This is the strongest non-mandatory exact scene in the model.

**Cinematic use:** major late-film climax. Citywide pulse → rapid camera push into Dogo → strong halo/extrusion → pull back to show the simultaneous centroid shift.

---

### 4.3 2025-05 — broad citywide volume pulse

Editorial score: **80.26**

- total events: **165**, the largest high-priority exact-period monthly volume in the scene ranking;
- strict points: 40;
- centroid movement: about 1.56 km.

The month is not dominated by one single mesh, so it should be treated as a **citywide expansion scene**, not another Dogo close-up.

Secondary persistent-after-quiet signal:
- 南吉田町;
- 3 strict events after a quiet previous 3 months;
- remains active in all next 3 months.

**Cinematic use:** wide establishing camera, many simultaneous sparks, faster pulse rate across the city rather than a single focal hotspot.

---

### 4.4 2025-08 — Mitsu re-acceleration after a quiet spell

Editorial score: **75.48**

- total events: 126;
- strict points: 35;
- dominant mesh: `50326537`;
- locality: 祓川二丁目 / 三津一丁目 / 三津二丁目;
- current strict count: 5;
- previous 3-month total in the mesh: 1;
- active in all next 3 months.

This is not the first appearance of Mitsu. The trajectory analysis shows Mitsu is a long-running second city core. The scene is better interpreted as **re-acceleration / renewed activity after a quiet period**.

**Cinematic use:** camera leaves the usual central/eastern focal areas and moves west to Mitsu. This provides geographic variety and shows that the spatial story is not only Dogo.

---

### 4.5 2026-03 — Yogo / Homen / Yogo-minami follow-up surge

Editorial score: **74.35**

- total events: 152;
- strict points: 44;
- top mesh: `50325579`;
- locality: 余戸東一丁目 / 保免西三丁目 / 余戸南一丁目;
- strict count: 5;
- previous 3-month total: 0;
- active in 2 of the next 3 months.

This month narrowly falls outside the canonical 12-scene seed because it is adjacent to the 2026-02 climax, but it is a strong **optional insert**.

**Cinematic use:** after the Dogo climax, a short lateral camera move toward the southwest can show that activity is not simply returning to one established core.

---

### 4.6 2021-08 — early centroid shift

Retrospective partial.  
Editorial score: **71.85**

- total retrospective rows: 106;
- strict points: 31;
- centroid movement: about **2.69 km**.

Because this is retrospective evidence, the scene should not claim that all restaurant activity “moved.” It is suitable for visually establishing that the spatial center of observed reconstructed permits can shift substantially.

**Cinematic use:** citywide camera with a subtle center-of-gravity trace rather than a local zoom.

---

### 4.7 2022-08 — spatial reconfiguration

Retrospective partial.  
Editorial score: **69.35**

- total retrospective rows: 99;
- strict points: 26;
- centroid movement: about 1.86 km;
- leading strict mesh around 祓川 / 住吉.

**Cinematic use:** wide spatial redistribution scene; good bridge between the early retrospective period and later hotspot-focused scenes.

---

### 4.8 2024-02 — retrospective Dogo concentration change

Retrospective partial.  
Editorial score: **76.94**

- total rows: 124;
- strict points: 48;
- leading mesh: Dogo;
- locality: 道後喜多町 / 道後北代 / 道後多幸町.

This is the strongest retrospective scene in the scoring model.

**Cinematic use:** one pre-transition Dogo scene establishes Dogo as a persistent historical core before exact observation begins.

---

### 4.9 2024-05 — Takehara / Fujiwara structural change

Retrospective partial.  
Editorial score: **69.86**

- total rows: 119;
- strict points: 33;
- focal mesh: `50325690`;
- locality: 竹原二丁目 / 藤原一丁目 / 藤原二丁目.

**Cinematic use:** a geographically distinct pre-transition scene; useful for avoiding a Dogo-only narrative.

---

### 4.10 2024-11 — Airport-district / Takehara dispersion change

Exact monthly.  
Editorial score: **69.65**

- total events: 123;
- strict points: 40;
- focal locality: 空港通二丁目 / 竹原三丁目.

The model classifies this under concentration/structure change; the important point is the **change in spatial arrangement**, not necessarily increased concentration.

**Cinematic use:** lateral camera shift and wider field, emphasizing redistribution rather than a singular glowing hotspot.

---

## 5. Persistent location trajectories

The most important insight from the 62-month strict-point analysis is that the city has recurring spatial cores.

### 5.1 Dogo — dominant persistent core

Mesh: `50326622`

Representative locality:
- 道後湯之町
- 道後鷺谷町
- 道後多幸町

Trajectory:
- active in **50 of 62 months**;
- longest continuous active streak: 13 months;
- rank #1 in 17 months;
- top 3 in 34 months;
- total strict events: **180**;
- peak: 2024-09, 15 strict events.

This is the clearest long-run spatial protagonist in the dataset.

**Narrative role:** persistent core → exact-data transition → late surge in 2026-02.

---

### 5.2 Mitsu / Sumiyoshi / Harukawa — second persistent core

Mesh: `50326537`

Representative locality:
- 三津
- 住吉
- 祓川

Trajectory:
- active in **47 of 62 months**;
- longest continuous streak: **16 months**;
- rank #1 in 12 months;
- top 3 in 20 months;
- total strict events: 103.

This is not a newly created 2025 hotspot; it is a persistent western core that becomes especially visually interesting in 2025-08 after a quiet spell.

**Narrative role:** the major counterpoint to Dogo.

---

### 5.3 Asoda / Tachibana / Izumi-minami — persistent southern-central core

Mesh: `50325681`

- active in 41 months;
- rank #1 in 4 months;
- top 3 in 12 months;
- 69 strict events.

**Narrative role:** recurring third center; useful when showing a polycentric rather than single-core city.

---

### 5.4 Nakamura / Kosaka / Edamatsu area

Mesh: `50325692`

- active in 35 months;
- top 3 in 11 months;
- 65 strict events.

**Narrative role:** repeated east/southeast activity; useful as part of the long-run “urban memory” layer.

---

### 5.5 Yogo / Homen — episodic but strong late-period location

Mesh: `50325579`

- active in 19 months;
- top 3 in 7 months;
- 30 strict events;
- peak in 2026-03 with 5.

**Narrative role:** late-period secondary surge after the 2026-02 Dogo climax.

---

## 6. Canonical 12-scene storyboard seed

The algorithm now uses spacing and location-diversity constraints so it does not simply zoom into Dogo repeatedly.

| # | Month | Scene | Camera logic |
|---:|---|---|---|
| 1 | 2021-06 | Source-boundary opening | citywide / centroid |
| 2 | 2021-08 | Centroid shift | citywide |
| 3 | 2022-08 | Spatial reconfiguration | citywide |
| 4 | 2024-02 | Dogo retrospective concentration | Dogo |
| 5 | 2024-05 | Takehara / Fujiwara structural change | Takehara/Fujiwara |
| 6 | 2024-09 | **Retrospective → exact transition** | Dogo, then secondary Higashi-Ishii cue |
| 7 | 2024-11 | Airport-district / Takehara redistribution | local focus |
| 8 | 2025-05 | Citywide volume pulse | citywide |
| 9 | 2025-08 | Mitsu renewed activity | Mitsu |
| 10 | 2025-12 | Citywide volume pulse | citywide |
| 11 | 2026-02 | **Strongest exact-period climax** | Dogo |
| 12 | 2026-07 | Closing / end-state | citywide |

Optional scene:
- **2026-03, Yogo/Homen/余戸南** — recommended if the final runtime can support a 13th beat.

---

## 7. Visual implications for the cinematic mode

The quantitative results imply a stronger story than “monthly dots appearing.”

### Chapter structure

**Chapter 1 — Reconstructed city memory**
- 2021-06 opening
- 2021-08 centroid movement
- 2022-08 spatial reconfiguration
- persistent Dogo and Mitsu cores gradually become visible

**Chapter 2 — Cores become legible**
- 2024-02 Dogo
- 2024-05 Takehara/Fujiwara
- persistent spatial memory is now bright enough for the user to perceive polycentric structure

**Chapter 3 — Evidence sharpens**
- 2024-09 explicit evidence transition
- visual treatment becomes sharper/brighter
- Dogo exact-month surge + Higashi-Ishii secondary emergence

**Chapter 4 — Redistribution and resurgence**
- 2024-11 airport/Takehara
- 2025-05 broad volume pulse
- 2025-08 Mitsu re-acceleration
- 2025-12 broad pulse

**Chapter 5 — Climax**
- 2026-02 Dogo: strongest exact scene
- optional 2026-03 southwest/Yogo-Homen follow-up
- 2026-07 pull-back and final comparison

---

## 8. Rules that must survive implementation

1. The retrospective period remains visibly labeled incomplete.
2. 2021-06 is a source boundary, not a claimed real-world spike.
3. “Persistent emergence” means re-emergence after a quiet previous 3 months, not first-ever creation of a district.
4. Fine spatial metrics use strict address/parcel points only.
5. Town-centroid retrospective points may support ambient visual density but not precise hotspot claims.
6. Dogo can recur in the narrative because persistence itself is an insight.
7. Repeated Dogo scenes must be balanced by Mitsu, Takehara/Fujiwara, Airport/Takehara, and citywide scenes.
8. Camera movement must be driven by these detected changes rather than arbitrary motion.

---

## 9. Canonical machine outputs

- `data/processed/cinematic/matsuyama_62m_month_metrics.csv`
- `data/processed/cinematic/matsuyama_62m_strict_mesh_1km.csv`
- `data/processed/cinematic/matsuyama_location_scene_candidates.csv`
- `data/processed/cinematic/matsuyama_hotspot_trajectories.csv`
- `data/processed/cinematic/matsuyama_scene_candidates_ranked.csv`
- `data/processed/cinematic/cinematic_storyboard_seed.json`
- `docs/research/STAGE8_CINEMATIC_INSIGHT_AUDIT.json`

These files are intended to drive the next implementation stage directly.

---

## 10. Stage 8 exit criteria

- [x] 62-month comparable metric panel
- [x] retrospective and exact evidence tiers separated
- [x] strict-point common spatial basis
- [x] volume anomaly / intensity
- [x] centroid movement
- [x] concentration / entropy structure
- [x] active-mesh churn
- [x] hotspot surge and after-quiet re-emergence
- [x] 1km hotspot trajectory classification
- [x] month ranking
- [x] camera-target coordinates and locality labels
- [x] source-boundary handling for 2021-06
- [x] mandatory evidence transition at 2024-09
- [x] location-diverse storyboard seed
- [x] strongest exact scene (2026-02) retained
- [x] reproducible GitHub Actions build

Stage 8 is complete.

The next stage should translate this quantitative storyboard into a cinematic design specification: scene durations, camera keyframes, glow/decay model, dark basemap treatment, annotation copy, KPI choreography, and performance budget.
