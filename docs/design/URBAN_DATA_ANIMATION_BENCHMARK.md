# Urban Data Animation Benchmark for the Cinematic Mode

Date: 2026-10-04  
Project: Ehime Restaurant License Map  
Purpose: research benchmark before designing a separate, high-impact animation mode.

## 1. Why this benchmark exists

The current map is intentionally analytical and conservative. It is good for checking months, counts, precision, and coverage, but it does not yet turn the 62-month Matsuyama series into a strong visual story.

The next mode should therefore be **additive**, not a replacement:

- **Current mode:** precise, inspectable, research-oriented.
- **New cinematic mode:** visually striking, time-driven, insight-oriented, but still honest about evidence quality.

The benchmark focuses on projects that are either formally awarded/recognized, institutionally important, or repeatedly cited as exemplary urban/data visualization work.

Evaluation dimensions:

1. temporal storytelling;
2. visual impact;
3. ability to reveal spatial patterns;
4. interaction design;
5. camera / scale choreography;
6. motion design;
7. clarity of analytical message;
8. transferability to the Matsuyama restaurant-permit dataset.

---

## 2. Benchmark set

### A. NYC Taxis: A Day in the Life — Chris Whong

Project:
- https://chriswhong.github.io/nyctaxi/
- https://github.com/chriswhong/nyctaxi

Recognition:
- **Gold Winner, Motion Infographic, Kantar Information is Beautiful Awards 2014**
- Featured as a Google Chrome Experiment.
- GitHub repository has hundreds of stars and forks.

Sources:
- https://www.informationisbeautifulawards.com/showcase?acategory=commercial-project&action=index&award=2014&controller=showcase&page=1&pcategory=short-list
- https://experiments.withgoogle.com/nyc-taxis-a-day-in-the-life

What it does:
- Compresses one taxi's 24-hour activity into an accelerated map animation.
- Shows occupied/empty state, trip routes, pickups/drop-offs, and running financial totals.
- Gives the user playback-speed control.

Why it works:
- **One clear temporal protagonist.** Instead of visualizing 170 million trips at once, it makes a single taxi legible.
- **Motion is data.** The movement itself explains where the taxi operates and when demand appears.
- **Persistent running totals** make the animation analytical rather than merely decorative.
- **A visible timeline** anchors the viewer in time.
- The map, timeline, and numerical KPIs move together.

Transfer to Matsuyama:
- Keep a large persistent date/month counter.
- Add live running totals such as permits this month, cumulative permits in the current chapter, active hotspot count, or change from the previous period.
- Avoid showing every historical point identically; give the viewer a visual protagonist or focal zone at any moment.
- Playback speed should be adjustable.

Key lesson:
> A successful temporal map needs a visible clock and a second analytical channel that changes with the animation.

---

### B. District Mobility — CLEVER°FRANKE + District Department of Transportation

Project:
- https://www.cleverfranke.com/project/district-mobility/

Recognition:
- **Red Dot Design Award**
- **The Webby Award — Honoree**
- **CSS Design Award — Site of the Day**
- **Awwwards — Honorable Mention**
- European Design Award finalist
- Information is Beautiful Awards 2017 shortlist.

Sources:
- https://www.cleverfranke.com/project/district-mobility/toolkit/content-strategy-%26-editorial-outline
- https://www.red-dot.org/de/project/district-mobility-16390-16390
- https://www.informationisbeautifulawards.com/showcase/1775-district-mobility

What it does:
- Uses transportation data to explain mobility conditions and policy challenges in Washington, D.C.
- Keeps the map as a persistent visual field while explanatory narrative and controls change alongside it.
- Uses a tightly controlled visual language and repeated geometric motifs.

Why it works:
- **Narrative and exploration coexist.** Users can be guided through findings, then explore.
- **Persistent map + changing narrative** prevents loss of spatial orientation.
- **Strong visual archetype.** The diamond shape of D.C. is reused as a design motif.
- **Minimal palette and typography** let the data remain the visual focus.
- Highlights direct the eye to important map regions rather than asking users to discover everything themselves.
- Red Dot's jury specifically praised the combination of hard facts, entertainment, interactivity, and easy comprehension.

Transfer to Matsuyama:
- Cinematic mode should be a **guided story**, not merely a more colorful map.
- Use a fixed map stage with a compact narrative card that changes at detected turning points.
- Create a Matsuyama-specific visual motif rather than generic dashboard styling.
- Keep existing exploratory mode separate.

Key lesson:
> “Insight” must be authored into the experience through sequencing and highlights; it should not depend on the viewer manually hunting through the map.

---

### C. HERE Traffic Analytics — CLEVER°FRANKE

Project:
- https://www.cleverfranke.com/project/here-traffic-analytics

Recognition:
- **Red Dot Design Award**
- **European Design Award — Silver**
- Information is Beautiful Awards 2017 shortlist.

Sources:
- https://www.cleverfranke.com/project/here-traffic-analytics/toolkit/app-development
- https://www.informationisbeautifulawards.com/showcase/2417

What it does:
- Turns complex traffic datasets into a cinematic interactive demonstration.
- Combines conventional 2D charts, animated 3D scenes, motion graphics, and scenario-based storytelling.
- Explicitly built from data analysis and storyboard creation before visual production.

Why it works:
- **The story starts with discovered patterns**, not visual effects.
- **Before/after and anomaly moments** are emphasized.
- 2D graphics explain values while 3D/motion creates emotional impact.
- Motion is treated as an extra data dimension.
- Visual style is vivid but deliberately subordinate to the message.
- Camera motion and depth give the data a physical presence.

Transfer to Matsuyama:
- First compute “interesting moments”: sudden increases, new clusters, hotspot shifts, center-of-gravity movement, concentration changes.
- Animate those moments differently from routine months.
- Use subtle 3D extrusion only where it represents magnitude.
- Use camera movement to transition between citywide and hotspot views.
- Build the experience around a storyboard of findings, not around effects.

Key lesson:
> Cinematic data visualization should be storyboarded from analysis results. The visuals should amplify discoveries already present in the data.

---

### D. Urban Layers — Morphocode

Project:
- https://io.morphocode.com/urban-layers/

Recognition:
- Published in **Best American Infographics 2015**.
- Named among the **top ten interactive data visualizations by Simon Rogers**.
- Featured as a major CityLab story.
- Morphocode reports more than 129k visits across its projects.

Sources:
- https://morphocode.com/about/
- https://morphocode.com/work/
- https://io.morphocode.com/urban-layers/

What it does:
- Uses NYC PLUTO and building footprints to explore the historical age structure of Manhattan.
- A time range control progressively reveals urban fabric by construction period.
- Color encodes age while the map preserves physical building geometry.

Why it works:
- **Time is represented as accumulation**, not a sequence of unrelated frames.
- The viewer sees the city “grow” and can understand what persists from older periods.
- Building geometry creates a dense urban texture; individual marks matter less than the emerging pattern.
- Color is meaningful and restrained.
- The timeline is directly connected to spatial form.

Transfer to Matsuyama:
- Do not make each month a fresh blank frame.
- Maintain a **visual memory layer**: older permits fade but persist, while new permits ignite.
- Show the accumulation and persistence of restaurant activity.
- Use a decay model so viewers can perceive long-term “urban memory” without confusing it with currently active shops.
- Consider a cumulative “city fabric” view in addition to monthly pulses.

Key lesson:
> Historical change becomes legible when the past remains faintly visible instead of disappearing at every timestep.

---

### E. HubCab — MIT Senseable City Lab

Project:
- https://senseable.mit.edu/hubcab-legacy/

Institutional / research recognition:
- Canonical MIT Senseable City Lab urban-mobility visualization.
- Based on more than **170 million NYC taxi trips**.
- Connected to peer-reviewed research on taxi shareability networks.

Source:
- https://senseable.mit.edu/hubcab-legacy/

What it does:
- Maps taxi pickups, drop-offs, and origin-destination relationships.
- Yellow and blue form a strong semantic pair.
- At city scale, intensity follows street geometry; at closer scales, individual dots become visible.
- Specific places/times can be selected to reveal flows.

Why it works:
- **Scale-aware visual grammar.** The representation changes between overview and detail.
- Dense events become an urban “field” rather than visual clutter.
- Strong color semantics make pickup vs drop-off immediately understandable.
- Logarithmic styling prevents large hotspots from overwhelming everything else.
- Queries around recognizable places provide entry points into a massive dataset.

Transfer to Matsuyama:
- At city scale, show density/glow rather than literal points.
- At neighborhood scale, transition to distinct permit sparks.
- Use nonlinear radius/height scaling for hotspots.
- Allow selected hotspots to reveal their historical “fan” or local evolution.

Key lesson:
> The same dataset should not use the same mark at every zoom level.

---

### F. Real Time Rome — MIT Senseable City Lab

Project:
- https://senseable.mit.edu/realtimerome/
- https://senseable.mit.edu/realtimerome/sketches/index.html

Recognition:
- MIT Senseable City Lab contribution to the **2006 Venice Biennale**.

What it does:
- Combines mobile-phone activity, buses, taxis, pedestrian density, traffic, visitors, and gatherings.
- Uses several distinct visualization “software” views: Pulse, Connectivity, Flow, Visitors, Gatherings, etc.

Why it works:
- Frames the city as a **living system with rhythms** rather than as a static GIS.
- Motion trails reveal speed and direction.
- Density appears as breathing/intensity fields.
- Some views compare current conditions with another reference period.
- Different questions receive different visual encodings rather than forcing everything into one layer.

Transfer to Matsuyama:
- Cinematic mode should portray the “pulse” of restaurant formation.
- Months with high activity should visibly breathe or intensify.
- Compare a current month against a trailing baseline.
- A single cinematic mode can contain chapters such as:
  - Pulse
  - Emerging clusters
  - Shifting center
  - Persistent cores
- The map should feel like a temporal system, not a collection of dots.

Key lesson:
> The strongest city visualizations treat the city as a dynamic organism and organize views around questions, not GIS layer types.

---

### G. Flight Patterns — Aaron Koblin

Project:
- https://www.aaronkoblin.com/project/flight-patterns/

Recognition:
- In the **Museum of Modern Art (MoMA) collection**, Department of Architecture and Design.
- Exhibited in MoMA's *Design and the Elastic Mind*, *Action! Design over Time*, and *Applied Design*.

Sources:
- https://www.moma.org/collection/works/110268
- https://momentsofinnovation.mit.edu/data-visualization/content/

What it does:
- Animates air traffic over North America as luminous trails on a dark field.
- Geography emerges through the data rather than through a dominant basemap.
- Day/night rhythms become visible through collective motion.

Why it works:
- **Data draws the map.** Background geography is suppressed.
- Glow, trails, fading, and accumulation create visual memory.
- The viewer first experiences the system emotionally, then recognizes geographic patterns.
- The palette is extremely restricted.
- There is almost no dashboard chrome competing with the visualization.

Transfer to Matsuyama:
- Introduce a “lights of the city” treatment where permits create temporary luminous halos.
- Allow streets/land to recede dramatically during animation.
- Use persistence/trails to reveal repeated activity.
- Treat the basemap as context, not the hero.
- A “cinematic fullscreen” state should remove most controls while playing.

Key lesson:
> Visual impact often comes from removing the map, not adding more map detail.

---

### H. Treepedia — MIT Senseable City Lab

Project:
- https://senseable.mit.edu/treepedia

Recognition:
- **Information is Beautiful Awards 2017 shortlist**, Places, Spaces & Environment.

Sources:
- https://senseable.mit.edu/treepedia
- https://www.informationisbeautifulawards.com/showcase/1766-treepedia

What it does:
- Maps street-level perceived greenery using a Green View Index.
- Uses thousands of small street-associated marks on a dark basemap.
- Includes a concise city-level KPI and street-level inspection.

Why it works:
- A single, understandable index controls the visual hierarchy.
- Dense street-level points form a recognizable texture.
- KPI and map are tightly linked.
- Dark background + saturated data marks produces immediate visual separation.

Transfer to Matsuyama:
- Develop one headline “pulse” metric for each frame/chapter rather than many dashboard values.
- Use dense but restrained point textures.
- Keep cinematic annotations compact.

Key lesson:
> One strong metric plus one strong spatial texture is often more memorable than a dashboard of many indicators.

---

### I. DataShine — UCL Centre for Advanced Spatial Analysis

Project:
- https://datashine.org.uk/

Recognition:
- Methodology published in the peer-reviewed **Journal of Maps**.
- Created specifically to make large open demographic datasets explorable.

Sources:
- https://datashine.org.uk/
- https://discovery.ucl.ac.uk/id/eprint/1469169/

What it does:
- Combines census/open demographic data with familiar geographic context.
- Provides flexible interactive variables while keeping the map interpretable.

Why it matters to this project:
- DataShine is less cinematic than the other references, but it is a useful counterweight.
- It demonstrates that visual ambition must not destroy geographic legibility.
- Familiar context and simple controls support genuine analysis.

Transfer to Matsuyama:
- Preserve the existing analytical mode unchanged.
- Cinematic mode should always provide a way to return to an inspectable evidence view.
- Avoid “beautiful ambiguity”: users must still be able to inspect what a visual effect means.

Key lesson:
> A cinematic mode should sit beside, not replace, a rigorous exploratory map.

---

## 3. Comparative assessment

Scores below are an internal design assessment for this project, not external award scores.

| Project | Temporal story | Visual impact | Insight guidance | Exploration | Transferability to Matsuyama |
|---|---:|---:|---:|---:|---:|
| NYC Taxis | 5 | 4 | 4 | 4 | 5 |
| District Mobility | 4 | 4 | 5 | 5 | 5 |
| HERE Traffic Analytics | 5 | 5 | 5 | 3 | 5 |
| Urban Layers | 5 | 4 | 4 | 5 | 5 |
| HubCab | 4 | 5 | 4 | 5 | 4 |
| Real Time Rome | 5 | 5 | 4 | 4 | 5 |
| Flight Patterns | 5 | 5 | 3 | 1 | 5 |
| Treepedia | 2 | 4 | 4 | 4 | 3 |
| DataShine | 2 | 3 | 4 | 5 | 3 |

The most useful combination for this project is not one reference alone:

- **Flight Patterns** for atmosphere and visual memory.
- **HERE Traffic Analytics** for cinematic motion and storyboard logic.
- **District Mobility** for guided insight and interaction architecture.
- **Urban Layers** for historical accumulation.
- **NYC Taxis** for a visible temporal clock and live metrics.
- **Real Time Rome** for the concept of the city's pulse.
- **HubCab** for scale-aware rendering.

---

## 4. Repeated design patterns in highly regarded work

### Pattern 1 — The basemap is subdued

The data is the brightest object on screen.

Common methods:
- near-black / dark neutral base;
- reduced road labels;
- monochrome land/water;
- labels appear only when useful;
- fullscreen animation removes nonessential interface chrome.

Implication:
- The cinematic mode should not use the current pale GSI map as its dominant visual field.

---

### Pattern 2 — New events do not simply appear; they have a lifecycle

High-impact motion uses:
1. anticipation;
2. appearance / ignition;
3. short peak;
4. decay;
5. residual memory.

Implication:
- A permit should appear as a brief pulse or spark, then decay into a persistent low-opacity city-memory layer.
- This is much stronger than instantly switching monthly point sets.

---

### Pattern 3 — Persistence makes change understandable

Urban Layers and Flight Patterns both allow history to remain visible.

Implication:
- Keep previous months at decreasing opacity.
- Example conceptual decay:
  - current month = 100%
  - 1–3 months old = 50–70%
  - 4–12 months old = 15–35%
  - older = faint “urban memory”
- This must be visually labeled as historical permit events, not active shops.

---

### Pattern 4 — Camera movement is editorial

Good camera motion answers a question.

Useful moves:
- citywide establish shot;
- slow push into a new hotspot;
- short orbit/tilt when a cluster becomes significant;
- pull back to compare multiple centers;
- return to citywide overview at chapter boundaries.

Bad move:
- continuous arbitrary rotation merely because 3D is available.

Implication:
- Camera paths should be triggered by detected spatial changes.

---

### Pattern 5 — High-density moments need nonlinear scaling

HubCab avoids allowing a few extreme locations to dominate.

Implication:
- Use logarithmic/sqrt scaling for glow radius, halo strength, or extrusion height.
- Preserve secondary centers.

---

### Pattern 6 — The best work has an authored narrative and an exploratory layer

District Mobility is the clearest benchmark.

Implication:
- Cinematic mode should have:
  1. **Watch** — guided autoplay with annotations.
  2. **Explore** — pause, scrub, inspect.
- Existing simple mode remains the evidence-first mode.

---

### Pattern 7 — Motion must encode meaning

Examples:
- taxi motion = actual travel;
- wind particle motion = actual vector field;
- trail persistence = repeated movement;
- density breathing = activity level.

For permit data there is no movement vector.

Therefore:
- **Do not animate permit points as if restaurants physically travel.**
- Valid animation variables are:
  - birth/appearance;
  - accumulation;
  - fade/age;
  - concentration;
  - hotspot expansion/contraction;
  - center-of-gravity change;
  - camera transition.

---

### Pattern 8 — Insight moments interrupt routine playback

HERE Traffic Analytics uses scenarios and before/after findings.

Implication:
- Detect and annotate statistically/analytically notable months.
- Playback can slow briefly at:
  - largest month-over-month increase;
  - emergence of a new persistent hotspot;
  - hotspot rank reversal;
  - largest centroid movement;
  - sharp change in spatial concentration;
  - transition from retrospective to exact evidence in 2024-09.

---

### Pattern 9 — The experience uses few colors

Strong projects usually use one dominant data color plus one comparison/accent color.

Suggested conceptual roles for Matsuyama:
- warm amber/gold = retrospective reconstruction;
- vivid coral/orange = exact new permit;
- cool cyan/blue = long-term urban memory / baseline;
- white = annotation and temporal markers.

This is not yet a final color specification.

---

### Pattern 10 — The first 5 seconds matter

The best data-art pieces communicate before the viewer understands the interface.

Cinematic opening should immediately establish:
- Matsuyama geography;
- date;
- what a spark means;
- temporal acceleration;
- a sense of the city accumulating activity.

---

## 5. What the current visualization lacks

The current map is intentionally good at auditability but weak as a cinematic story because:

1. monthly frames replace one another with little visual memory;
2. the map is visually stronger than the data;
3. camera framing is effectively static;
4. all routine months receive similar visual treatment;
5. the viewer is not told where to look;
6. no detected turning points are surfaced;
7. there is limited cumulative context;
8. key metrics do not tell a changing story during playback;
9. there is no narrative beginning, climax, transition, or ending.

These are design limitations, not data limitations.

---

## 6. Design principles for the future cinematic mode

The benchmark supports the following requirements.

### Principle A — Preserve the current mode

The current research/exploration mode stays available and visually simple.

The cinematic mode is a separate entry point, tentatively:

**Cinematic / City Pulse / Story**

No existing analytical capability should be removed.

### Principle B — Show formation, memory, and concentration

The central visual idea should be:

> Each new permit ignites; repeated activity leaves a spatial memory; clusters become visible as the city changes over time.

This matches what the data actually records.

### Principle C — Explicitly encode evidence quality

The 2021-06–2024-08 retrospective period and the 2024-09–2026-07 exact period must remain distinguishable.

The evidence transition at 2024-09 should be a deliberate narrative event, not hidden.

### Principle D — Compute insights before designing scenes

Before implementation, derive a scene/event table containing:
- monthly count;
- rolling baseline;
- anomaly score;
- hotspot rank and persistence;
- centroid movement;
- concentration / entropy;
- newly emerging clusters;
- disappearing clusters;
- evidence quality.

Scene choreography should be generated from these signals.

### Principle E — Prefer “2.5D” over gratuitous 3D

Use:
- pitch;
- controlled elevation;
- glow;
- volumetric-looking halos;
- extrusion for intensity;
- depth-of-field-like visual hierarchy where performant.

Avoid:
- spinning globe effects;
- arbitrary skyscraper-like bars unrelated to data;
- camera movement that makes geography hard to read.

### Principle F — Fullscreen playback should feel like a film

During autoplay:
- collapse most controls;
- display only date, chapter title, a small KPI group, and pause/exit controls;
- allow annotations to appear and disappear with the scene;
- use smooth camera easing;
- keep a visible but restrained timeline.

---

## 7. Candidate cinematic structure for Matsuyama

This is a benchmark-derived direction, not yet the implementation specification.

### Opening — “The city wakes”

- Start nearly dark.
- Matsuyama outline/street structure fades in.
- Date: **2021-06**.
- Retrospective evidence badge appears once.
- First permit points ignite.
- Old sparks decay into faint memory.

### Chapter 1 — Formation

- Continuous month progression.
- Camera remains mostly citywide.
- Repeated activity creates glowing cores.

### Chapter 2 — Emerging centers

- When a persistent hotspot emerges, playback slows.
- Camera pushes toward the area.
- Small annotation gives the finding and magnitude.
- Return to overview.

### Chapter 3 — Changing spatial structure

- Show center-of-gravity movement and concentration changes.
- Avoid literal “movement” of restaurants; animate the summary geometry instead.

### Chapter 4 — Evidence transition

- At **2024-09**, pause or soften motion.
- Explicit transition:
  **参考復元 → 完全観測**
- Color/visual texture becomes sharper to signify improved evidence.

### Ending — “What changed?”

- Pull back to citywide view.
- Show beginning vs ending hotspot structure.
- Surface 3–5 computed findings.
- Offer:
  **Replay / Explore on analytical map**

---

## 8. Anti-patterns to avoid

1. Particle effects with no data meaning.
2. Continuous camera orbit.
3. Excessive neon color diversity.
4. Every point remaining fully opaque forever.
5. Fake movement paths between restaurant locations.
6. 3D columns purely for spectacle.
7. Hiding retrospective-data incompleteness.
8. Auto-playing so fast that geographic patterns cannot be recognized.
9. Making the user read a dashboard while the map is moving.
10. Replacing the inspectable analytical mode.

---

## 9. Recommended benchmark hierarchy

For the actual design phase, use these as primary references in this order:

1. **HERE Traffic Analytics** — cinematic data storytelling.
2. **District Mobility** — guided urban-data narrative and public-sector clarity.
3. **Flight Patterns** — visual impact, darkness, glow, persistence.
4. **Urban Layers** — historical accumulation and time interaction.
5. **NYC Taxis: A Day in the Life** — temporal UI and live metrics.
6. **Real Time Rome** — city-as-living-system framing.
7. **HubCab** — large-scale spatial density and zoom-dependent representation.

Treepedia and DataShine should act as guardrails for clarity and analytical integrity.

---

## 10. Decision from this benchmark

The new mode should **not** be “the current map with prettier colors and more particles.”

It should be a separate **data-driven cinematic narrative engine** with:

- historical visual memory;
- event ignition / decay;
- dark, subordinate cartography;
- camera choreography driven by detected spatial changes;
- scene annotations at meaningful turning points;
- cumulative and comparative KPIs;
- evidence-quality transition at 2024-09;
- watch mode + pause/explore;
- a final summary of what changed.

The strongest benchmark synthesis is:

> **Flight Patterns atmosphere × Urban Layers historical accumulation × HERE Traffic Analytics motion/storyboard × District Mobility insight guidance × NYC Taxi temporal instrumentation.**

That combination is the design target for the Matsuyama cinematic mode.
