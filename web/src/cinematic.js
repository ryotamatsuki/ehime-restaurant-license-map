import {ScatterplotLayer, GeoJsonLayer} from '@deck.gl/layers';

const FRESH = [255, 224, 185];
const HALO = [255, 117, 63];
const MEMORY = [110, 164, 185];
const AMBIENT = [132, 149, 156];

// Radial falloff keeps the light inside an actual permit's point footprint.
class PermitGlowLayer extends ScatterplotLayer {
  getShaders() {
    const shaders = super.getShaders();
    return {...shaders, inject: {...shaders.inject,
      'fs:DECKGL_FILTER_COLOR': 'color.a *= exp(-4.5 * dot(geometry.uv, geometry.uv)) * (1.0 - smoothstep(0.6, 1.0, length(geometry.uv)));'
    }};
  }
}
PermitGlowLayer.layerName = 'PermitGlowLayer';

function setText(node, text) {
  if (node.textContent !== text) node.textContent = text;
}

function clamp(x, lo = 0, hi = 1) {
  return Math.max(lo, Math.min(hi, x));
}

function smoothstep(t) {
  const x = clamp(t);
  return x * x * (3 - 2 * x);
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function hashUnit(value) {
  let h = 2166136261;
  const s = String(value || '');
  for (let i = 0; i < s.length; i += 1) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0) / 4294967295;
}

function monthOrdinal(month) {
  const [y, m] = month.split('-').map(Number);
  return y * 12 + m;
}

function formatValue(item) {
  if (!item) return '';
  const value = typeof item.value === 'number'
    ? item.value.toLocaleString('ja-JP', {maximumFractionDigits: 2})
    : String(item.value);
  return value + (item.unit || '');
}

function focusPolygon(center) {
  const [lon, lat] = center;
  const dy = 0.008333333333333333 / 2;
  const dx = 0.0125 / 2;
  return {
    type: 'Feature',
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [lon - dx, lat - dy],
        [lon + dx, lat - dy],
        [lon + dx, lat + dy],
        [lon - dx, lat + dy],
        [lon - dx, lat - dy]
      ]]
    },
    properties: {}
  };
}

function activeInWindow(elapsed, window) {
  return Array.isArray(window) && elapsed >= window[0] && elapsed <= window[1];
}

export function createCinematicController({
  map,
  overlay,
  data,
  state,
  els,
  stopAnalyticalPlayback,
  analyticalLayers,
  analyticalTooltip,
  updateAnalytical,
  syncAnalytical,
  onExploreTarget
}) {
  const timeline = data.cinematicTimeline;
  const schedule = timeline.month_schedule;
  const focusSeries = data.cinematicFocusSeries;
  const allEvents = data.retrospectiveEvents.concat(
    data.events.filter(d => d.municipality_code === '382019' && d.business_type === '飲食店営業')
  );
  const monthIndex = new Map(schedule.map((m, i) => [m.month, i]));
  const eventMonthIndex = new Map(schedule.map((m, i) => [m.month, i]));

  const chapter = document.querySelector('#cinematic-chapter');
  const geonames = ['dogo', 'mitsu'].map(key => ({
    key, node: document.querySelector('#cinematic-geoname-' + key)
  }));
  let chartKey = null;
  let lastCamera = null;
  let layersKey = null;
  const focusCache = new Map();
  const run = {
    playing: false,
    elapsed: 0,
    startedAt: 0,
    pausedAt: 0,
    raf: null,
    savedCamera: null,
    reduced: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    selectedExploreTarget: 'dogo',
    cacheMonth: null,
    cache: null,
    lastBeatId: null,
    seenMonths: new Set(),
    destroyed: false
  };

  function isMobile() {
    return window.innerWidth <= 760;
  }

  function monthAtTime(elapsed) {
    const t = clamp(elapsed, 0, timeline.runtime_seconds - 0.0001);
    let lo = 0;
    let hi = schedule.length - 1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      const item = schedule[mid];
      if (t < item.start) hi = mid - 1;
      else if (t >= item.end) lo = mid + 1;
      else return item;
    }
    return schedule.at(-1);
  }

  function beatAtTime(elapsed) {
    return timeline.beats.find(b => elapsed >= b.start && elapsed < b.end) || null;
  }

  function periodNote(month) {
    return month < '2024-09'
      ? '2021-06〜2024-08：参考復元'
      : '2024-09〜2026-07：月次観測';
  }

  function cameraAtTime(elapsed) {
    const frames = timeline.camera_keyframes;
    if (run.reduced) {
      let chosen = frames[0];
      for (const frame of frames) {
        if (frame.t <= elapsed) chosen = frame;
        else break;
      }
      return adjustCamera({
        lon: chosen.lon,
        lat: chosen.lat,
        zoom: chosen.zoom,
        pitch: Math.min(chosen.pitch, 12),
        bearing: 0
      });
    }

    if (elapsed <= frames[0].t) return adjustCamera({...frames[0]});
    if (elapsed >= frames.at(-1).t) return adjustCamera({...frames.at(-1)});

    let a = frames[0];
    let b = frames[1];
    for (let i = 0; i < frames.length - 1; i += 1) {
      if (elapsed >= frames[i].t && elapsed <= frames[i + 1].t) {
        a = frames[i];
        b = frames[i + 1];
        break;
      }
    }
    const u = smoothstep((elapsed - a.t) / Math.max(0.001, b.t - a.t));
    return adjustCamera({
      lon: lerp(a.lon, b.lon, u),
      lat: lerp(a.lat, b.lat, u),
      zoom: lerp(a.zoom, b.zoom, u),
      pitch: lerp(a.pitch, b.pitch, u),
      bearing: lerp(a.bearing, b.bearing, u)
    });
  }

  function adjustCamera(camera) {
    if (!isMobile()) return camera;
    const local = camera.zoom >= 12;
    return {
      lon: camera.lon,
      lat: camera.lat - (local ? 0.0045 : 0.0020),
      zoom: Math.max(9.5, camera.zoom - (local ? 0.65 : 0.35)),
      pitch: Math.min(camera.pitch, 32),
      bearing: camera.bearing * 0.55
    };
  }

  function applyCamera(elapsed) {
    const c = cameraAtTime(elapsed);
    if (!lastCamera || ['lon', 'lat', 'zoom', 'pitch', 'bearing'].some(k => Math.abs(c[k] - lastCamera[k]) > 1e-7)) map.jumpTo({
      center: [c.lon, c.lat],
      zoom: c.zoom,
      pitch: c.pitch,
      bearing: c.bearing
    });
    lastCamera = c;
    for (const {key, node} of geonames) {
      const point = map.project(focusSeries[key].center);
      node.style.transform = `translate(${point.x + 12}px, ${point.y - 24}px)`;
      node.style.opacity = c.zoom < 12 ? '0.7' : '0';
    }
    return c;
  }

  function memoryAlpha(age) {
    if (age <= 0) return 0.78;
    if (age <= 3) return lerp(0.42, 0.27, (age - 1) / 2);
    if (age <= 12) return lerp(0.19, 0.08, (age - 4) / 8);
    return 0.045;
  }

  function rebuildMonthCache(month) {
    if (run.cacheMonth === month && run.cache) return run.cache;
    const currentIndex = eventMonthIndex.get(month);
    const visibleStrict = [];
    const ambient = [];
    const freshStrict = [];

    for (const event of allEvents) {
      const idx = eventMonthIndex.get(event.month);
      if (idx == null || idx > currentIndex) continue;
      const strict = event.quality === 'address_or_parcel';
      if (!strict) {
        if (event.evidence !== 'exact_monthly') ambient.push(event);
        continue;
      }
      const age = currentIndex - idx;
      visibleStrict.push({...event, _age: age, _alpha: memoryAlpha(age)});
      if (idx === currentIndex) freshStrict.push(event);
    }

    run.cacheMonth = month;
    run.cache = {visibleStrict, ambient, freshStrict};
    return run.cache;
  }

  function ignitionPhase(event, elapsed, monthInfo) {
    const duration = Math.max(0.05, monthInfo.end - monthInfo.start);
    const jitter = hashUnit(event.id) * Math.min(0.18, duration * 0.32);
    const age = elapsed - (monthInfo.start + jitter);
    if (age < 0) return {core: 0, halo: 0, radius: 0};
    const rise = clamp(age / Math.min(0.11, duration * 0.35));
    const haloAge = age / Math.min(0.42, Math.max(0.12, duration * 0.9));
    const halo = haloAge <= 1 ? Math.sin(Math.PI * clamp(haloAge)) : 0;
    return {
      core: clamp(rise),
      halo,
      radius: 1 + 1.55 * halo
    };
  }

  function focusFeatures(beat) {
    if (!beat) return [];
    if (focusCache.has(beat.id)) return focusCache.get(beat.id);
    const centers = [];
    if (beat?.focus_center) centers.push(beat.focus_center);
    if (beat?.focus_centers) centers.push(...beat.focus_centers);
    const features = centers.map(focusPolygon);
    focusCache.set(beat.id, features);
    return features;
  }

  function layersForTime(elapsed, monthInfo, beat) {
    const cache = rebuildMonthCache(monthInfo.month);
    const layers = [
      new ScatterplotLayer({
        id: 'cin-ambient-' + monthInfo.month,
        data: cache.ambient,
        getPosition: d => [d.lon, d.lat],
        getRadius: 14,
        radiusMinPixels: 0.8,
        radiusMaxPixels: 2.2,
        getFillColor: [...AMBIENT, 24],
        stroked: false,
        pickable: false
      }),
      new ScatterplotLayer({
        id: 'cin-memory-' + monthInfo.month,
        data: cache.visibleStrict,
        getPosition: d => [d.lon, d.lat],
        getRadius: d => d._age === 0 ? 24 : 14,
        radiusMinPixels: 0.9,
        radiusMaxPixels: 4.0,
        getFillColor: d => [...MEMORY, Math.round(255 * d._alpha)],
        stroked: false,
        pickable: false
      })
    ];

    if (!run.reduced && cache.freshStrict.length) {
      layers.push(new PermitGlowLayer({
        id: 'cin-halo-' + monthInfo.month,
        data: cache.freshStrict,
        getPosition: d => [d.lon, d.lat],
        getRadius: d => 46 * ignitionPhase(d, elapsed, monthInfo).radius,
        radiusMinPixels: 7,
        radiusMaxPixels: 14,
        getFillColor: d => [...HALO, Math.round(190 * Math.max(0.22, ignitionPhase(d, elapsed, monthInfo).halo))],
        updateTriggers: {
          getRadius: Math.floor(elapsed * 30),
          getFillColor: Math.floor(elapsed * 30)
        },
        stroked: false,
        pickable: false
      }));
    }

    layers.push(new ScatterplotLayer({
      id: 'cin-core-' + monthInfo.month,
      data: cache.freshStrict,
      getPosition: d => [d.lon, d.lat],
      getRadius: 18,
      radiusMinPixels: 1.8,
      radiusMaxPixels: 3.8,
      getFillColor: d => {
        const phase = run.reduced ? 1 : ignitionPhase(d, elapsed, monthInfo).core;
        return [...FRESH, Math.round(235 * phase)];
      },
      updateTriggers: {getFillColor: Math.floor(elapsed * 20)},
      stroked: false,
      pickable: false
    }));

    const focus = focusFeatures(beat);
    const focusVisible = beat?.focus_window
      ? activeInWindow(elapsed, beat.focus_window)
      : beat && elapsed >= beat.start + 0.55;
    if (focus.length && focusVisible) {
      layers.push(new GeoJsonLayer({
        id: 'cin-focus-mesh-' + beat.id,
        data: {type: 'FeatureCollection', features: focus},
        filled: true,
        stroked: true,
        getFillColor: [255, 139, 75, 16],
        getLineColor: [255, 184, 118, 110],
        getLineWidth: 1.1,
        lineWidthMinPixels: 1,
        pickable: false
      }));
    }
    return layers;
  }

  function findKpi(beat, elapsed) {
    if (!beat) return null;
    if (beat.kpi_sequence) {
      return beat.kpi_sequence.find(k => elapsed >= k.start && elapsed <= k.end) || null;
    }
    if (beat.local_count != null && activeInWindow(elapsed, beat.caption_window)) {
      return {
        label: beat.place,
        value: beat.local_count,
        unit: '件'
      };
    }
    return null;
  }

  function renderSparkline(key, currentMonth) {
    const nextKey = key ? key + ':' + currentMonth : '';
    if (chartKey === nextKey) return;
    chartKey = nextKey;
    if (!key || !timeline.local_comparisons?.[key]) {
      els.cinematicChart.innerHTML = '';
      els.cinematicChart.classList.remove('is-visible');
      return;
    }
    const series = timeline.local_comparisons[key];
    const max = Math.max(1, ...series.map(d => d.count));
    const bars = series.map((d, i) => {
      const h = d.count / max * 38;
      const x = 12 + i * 55;
      const color = d.month === currentMonth ? '#ffd7bb' : '#6ea4b9';
      return `<rect x="${x}" y="${53-h}" width="28" height="${Math.max(1,h)}" fill="${color}" opacity="${d.count ? 0.85 : 0.35}"/>`
        + `<text x="${x+14}" y="${47-h}" text-anchor="middle">${d.count}</text>`
        + `<text x="${x+14}" y="70" text-anchor="middle" class="bar-date">${d.month.slice(5)}月</text>`;
    }).join('');
    const label = series.map(d => d.month + ' ' + d.count + '件').join('、');
    els.cinematicChart.innerHTML = `<svg viewBox="0 0 232 76" role="img" aria-label="${label}">${bars}</svg><span>同一区画の許可件数<br>${series[0].month.slice(0,4)}年${series[0].month.slice(5)}月–${currentMonth.replace('-', '年')}月</span>`;
    els.cinematicChart.classList.add('is-visible');
  }

  function renderHud(elapsed, monthInfo, beat) {
    const month = monthInfo.month;
    setText(els.cinematicMonth, month.replace('-', '.'));
    setText(chapter, elapsed < 37 ? '01｜記録を重ねる' : elapsed < 72.8 ? '02｜場所の違いを読む' : '03｜次の問いへ');
    setText(els.cinematicPeriod, periodNote(month));

    const kpi = findKpi(beat, elapsed);
    const place = kpi?.place ?? beat?.place ?? '';
    const scope = kpi?.scope ?? beat?.scope ?? '';
    const support = kpi?.support ?? beat?.support ?? '';
    const sparkline = kpi?.sparkline ?? beat?.sparkline ?? null;
    const captionVisible = beat && activeInWindow(elapsed, beat.caption_window);
    const ctaVisible = beat && activeInWindow(elapsed, beat.cta_window);

    const focusBeat = beat && !['opening', 'major_citywide', 'passing_citywide'].includes(beat.style);
    els.cinematicMonth.classList.toggle('is-focus', Boolean(focusBeat));
    els.cinematicMonth.classList.toggle('is-bridge', !beat || beat.style === 'passing_citywide');

    setText(els.cinematicTitle, beat?.title || '');
    els.cinematicTitle.classList.toggle('is-visible', Boolean(beat?.title && elapsed <= 4.2));

    setText(els.cinematicPlace, place);
    els.cinematicPlace.classList.toggle('is-visible', Boolean(place && elapsed >= beat.start + 0.45));

    if (kpi) {
      setText(els.cinematicKpiLabel, kpi.label || '');
      setText(els.cinematicKpi, formatValue(kpi));
      setText(els.cinematicScope, scope);
      els.cinematicScope.classList.toggle('is-redundant', scope === place);
      els.cinematicKpiWrap.classList.add('is-visible');
    } else {
      els.cinematicKpiWrap.classList.remove('is-visible');
    }

    setText(els.cinematicSupport, support);
    els.cinematicSupport.classList.toggle('is-visible', Boolean(kpi && support));

    setText(els.cinematicAnnotation, beat?.caption || '');
    els.cinematicAnnotation.classList.toggle('is-visible', Boolean(captionVisible && beat.style !== 'closing'));

    if (sparkline && kpi) renderSparkline(sparkline, month);
    else renderSparkline(null, month);

    const final = beat?.style === 'closing';
    els.cinematicFinal.classList.toggle('is-visible', Boolean(final && ctaVisible));
    if (final) {
      if (!els.cinematicClosingStats.dataset.ready) {
        els.cinematicClosingStats.innerHTML = ['dogo', 'mitsu'].map(key => {
          const f = focusSeries[key];
          const dots = f.series.map(d => `<i class="${d.count ? 'recorded' : ''}" title="${d.month}: ${d.count}件"></i>`).join('');
          return `<div class="closing-row"><strong>${f.label} ${f.exact_active_months}/23か月</strong><div class="closing-months" aria-label="${f.label}の23か月の許可記録">${dots}</div></div>`;
        }).join('');
        els.cinematicClosingStats.dataset.ready = 'true';
      }
    }

    const closingQuiet = Boolean(final && beat.caption_window && elapsed > beat.caption_window[1]);
    const hudHasContent = Boolean(
      beat
      && !final
      && !closingQuiet
      && (place || beat.title || kpi || captionVisible || support || sparkline)
    );
    els.cinematicHud.classList.toggle('is-active', hudHasContent);

    els.cinematicProgress.style.width =
      Math.min(100, elapsed / timeline.runtime_seconds * 100) + '%';
  }

  function setMapTone(on) {
    document.body.classList.toggle('cinematic-active', on);
    lastCamera = null;
    layersKey = null;
    try {
      map.setLayoutProperty('gsi', 'visibility', on ? 'none' : 'visible');
      map.setLayoutProperty('cinematic-base', 'visibility', on ? 'visible' : 'none');
    } catch (_) {}
  }

  function updateDebug(elapsed, monthInfo, beat, camera) {
    run.seenMonths.add(monthInfo.month);
    const focusCenter = beat?.focus_center || beat?.focus_centers?.[0] || null;
    const focusPixel = focusCenter ? map.project(focusCenter) : null;
    const hudRect = els.cinematicHud?.getBoundingClientRect?.() || null;
    window.__CINEMATIC_DEBUG__ = {
      elapsed,
      month: monthInfo.month,
      beat: beat?.id || null,
      playing: run.playing,
      reduced: run.reduced,
      camera,
      focusPixel: focusPixel ? {x: focusPixel.x, y: focusPixel.y} : null,
      hudRect: hudRect ? {top: hudRect.top, bottom: hudRect.bottom, left: hudRect.left, right: hudRect.right} : null,
      seenMonths: Array.from(run.seenMonths),
      selectedExploreTarget: run.selectedExploreTarget
    };
  }

  function render(elapsed) {
    const safe = clamp(elapsed, 0, timeline.runtime_seconds - 0.001);
    const monthInfo = monthAtTime(safe);
    const beat = beatAtTime(safe);
    const camera = applyCamera(safe);
    const animated = safe - monthInfo.start < 0.7;
    const focusVisible = beat?.focus_window ? activeInWindow(safe, beat.focus_window) : Boolean(beat && safe >= beat.start + 0.55);
    const key = monthInfo.month + ':' + (animated ? Math.floor(safe * 30) : 'hold') + ':' + beat?.id + ':' + focusVisible;
    if (layersKey !== key) {
      overlay.setProps({layers: layersForTime(safe, monthInfo, beat), getTooltip: null});
      layersKey = key;
    }
    renderHud(safe, monthInfo, beat);
    updateDebug(safe, monthInfo, beat, camera);
  }

  function frame(now) {
    if (!run.playing || !state.cinematic || run.destroyed) return;
    run.elapsed = run.pausedAt + (now - run.startedAt) / 1000;
    if (run.elapsed >= timeline.runtime_seconds) {
      run.elapsed = timeline.runtime_seconds - 0.001;
      render(run.elapsed);
      pause();
      return;
    }
    render(run.elapsed);
    run.raf = requestAnimationFrame(frame);
  }

  function pause() {
    if (run.raf) cancelAnimationFrame(run.raf);
    run.raf = null;
    if (run.playing) run.pausedAt = run.elapsed;
    run.playing = false;
    els.cinematicPlay.textContent = '▶';
    if (window.__CINEMATIC_DEBUG__) window.__CINEMATIC_DEBUG__.playing = false;
  }

  function play() {
    if (!state.cinematic) return;
    if (run.elapsed >= timeline.runtime_seconds - 0.01) {
      run.elapsed = 0;
      run.pausedAt = 0;
      run.seenMonths.clear();
    }
    run.playing = true;
    run.startedAt = performance.now();
    els.cinematicPlay.textContent = 'Ⅱ';
    run.raf = requestAnimationFrame(frame);
  }

  function toggle() {
    if (run.playing) pause();
    else play();
  }

  function enter() {
    stopAnalyticalPlayback();
    state.cinematic = true;
    run.savedCamera = {
      center: map.getCenter().toArray(),
      zoom: map.getZoom(),
      pitch: map.getPitch(),
      bearing: map.getBearing()
    };
    run.elapsed = 0;
    run.pausedAt = 0;
    run.cacheMonth = null;
    run.cache = null;
    run.seenMonths.clear();
    run.selectedExploreTarget = 'dogo';
    syncTargetButtons();
    els.cinematicShell.hidden = false;
    document.querySelector('.topbar')?.setAttribute('aria-hidden', 'true');
    document.querySelector('.panel')?.setAttribute('aria-hidden', 'true');
    setMapTone(true);
    render(0);
    if (run.reduced) {
      pause();
    } else {
      play();
    }
  }

  function exit({restoreCamera = true} = {}) {
    if (!state.cinematic) return;
    pause();
    state.cinematic = false;
    els.cinematicShell.hidden = true;
    document.querySelector('.topbar')?.removeAttribute('aria-hidden');
    document.querySelector('.panel')?.removeAttribute('aria-hidden');
    setMapTone(false);
    overlay.setProps({layers: analyticalLayers(), getTooltip: analyticalTooltip});
    if (restoreCamera && run.savedCamera) {
      map.jumpTo(run.savedCamera);
    }
    syncAnalytical();
    updateAnalytical();
  }

  function jumpToBeat(delta) {
    const beats = timeline.beats;
    let idx = beats.findIndex(b => run.elapsed >= b.start && run.elapsed < b.end);
    if (idx < 0) idx = beats.findIndex(b => b.start > run.elapsed) - 1;
    idx = Math.max(0, Math.min(beats.length - 1, idx + delta));
    pause();
    run.elapsed = beats[idx].start + 0.02;
    run.pausedAt = run.elapsed;
    render(run.elapsed);
  }

  function replay() {
    pause();
    run.elapsed = 0;
    run.pausedAt = 0;
    run.cacheMonth = null;
    run.seenMonths.clear();
    render(0);
    if (!run.reduced) play();
  }

  function syncTargetButtons() {
    els.cinematicTargetDogo.classList.toggle('active', run.selectedExploreTarget === 'dogo');
    els.cinematicTargetMitsu.classList.toggle('active', run.selectedExploreTarget === 'mitsu');
    const target = timeline.explore_targets[run.selectedExploreTarget];
    els.cinematicExplore.textContent = target.label + 'の許可を確かめる';
  }

  function chooseTarget(key) {
    run.selectedExploreTarget = key;
    syncTargetButtons();
    if (window.__CINEMATIC_DEBUG__) {
      window.__CINEMATIC_DEBUG__.selectedExploreTarget = key;
    }
  }

  function exploreSelected() {
    const target = timeline.explore_targets[run.selectedExploreTarget];
    exit({restoreCamera: false});
    onExploreTarget(target);
  }

  function seek(seconds) {
    pause();
    run.elapsed = clamp(Number(seconds) || 0, 0, timeline.runtime_seconds - 0.001);
    run.pausedAt = run.elapsed;
    render(run.elapsed);
  }

  function bindControls() {
    window.__CINEMATIC_TEST_API__ = {seek, play, pause, replay};
    els.cinematicEnter.addEventListener('click', enter);
    els.cinematicExit.addEventListener('click', () => exit());
    els.cinematicPlay.addEventListener('click', toggle);
    els.cinematicNext.addEventListener('click', () => jumpToBeat(1));
    els.cinematicReplay.addEventListener('click', replay);
    els.cinematicTargetDogo.addEventListener('click', () => chooseTarget('dogo'));
    els.cinematicTargetMitsu.addEventListener('click', () => chooseTarget('mitsu'));
    els.cinematicExplore.addEventListener('click', exploreSelected);

    document.addEventListener('keydown', event => {
      if (!state.cinematic) return;
      if (event.code === 'Space') {
        event.preventDefault();
        toggle();
      } else if (event.code === 'ArrowRight') {
        event.preventDefault();
        jumpToBeat(1);
      } else if (event.code === 'ArrowLeft') {
        event.preventDefault();
        jumpToBeat(-1);
      } else if (event.code === 'Escape') {
        exit();
      }
    });

    document.addEventListener('visibilitychange', () => {
      if (document.hidden && state.cinematic && run.playing) pause();
    });
  }

  function destroy() {
    run.destroyed = true;
    pause();
  }

  return {
    bindControls,
    enter,
    exit,
    pause,
    play,
    toggle,
    replay,
    render,
    seek,
    destroy
  };
}
