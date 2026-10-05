import {Map, NavigationControl, AttributionControl, setWorkerUrl, addProtocol} from 'maplibre-gl';
import {Protocol} from 'pmtiles';
import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import 'maplibre-gl/dist/maplibre-gl.css';
import {MapLibreOverlay} from '@deck.gl/maplibre';
import {ScatterplotLayer, GeoJsonLayer} from '@deck.gl/layers';
import {HeatmapLayer, HexagonLayer} from '@deck.gl/aggregation-layers';
import './style.css';
import {createCinematicController} from './cinematic.js';

setWorkerUrl(maplibreWorkerUrl);
// The official GSI archive may use PMTiles v2; 3.2 retains v2/v3 decoding.
const pmtilesProtocol = new Protocol();
addProtocol('pmtiles', pmtilesProtocol.tile);

const DATA = './data/';
const COLORS = {
  exact: [221, 90, 58, 210],
  retroStrict: [215, 111, 47, 185],
  retroTown: [226, 160, 59, 105]
};

const els = {
  municipality: document.querySelector('#municipality-select'),
  business: document.querySelector('#business-select'),
  views: document.querySelector('#view-switcher'),
  periods: document.querySelector('#period-switcher'),
  retroToggle: document.querySelector('#retrospective-toggle'),
  slider: document.querySelector('#month-slider'),
  play: document.querySelector('#play-button'),
  start: document.querySelector('#timeline-start'),
  current: document.querySelector('#timeline-current'),
  end: document.querySelector('#timeline-end'),
  coverage: document.querySelector('#coverage-badge'),
  periodLabel: document.querySelector('#period-label'),
  modeNote: document.querySelector('#mode-note'),
  total: document.querySelector('#metric-total'),
  totalLabel: document.querySelector('#metric-total-label'),
  points: document.querySelector('#metric-points'),
  pointsLabel: document.querySelector('#metric-points-label'),
  third: document.querySelector('#metric-third'),
  thirdLabel: document.querySelector('#metric-third-label'),
  empty: document.querySelector('#empty-state'),
  emptyDetail: document.querySelector('#empty-detail'),
  caption: document.querySelector('#map-caption-main'),
  cinematicEnter: document.querySelector('#cinematic-enter'),
  cinematicShell: document.querySelector('#cinematic-shell'),
  cinematicExit: document.querySelector('#cinematic-exit'),
  cinematicPlay: document.querySelector('#cinematic-play'),
  cinematicNext: document.querySelector('#cinematic-next'),
  cinematicMonth: document.querySelector('#cinematic-month'),
  cinematicPeriod: document.querySelector('#cinematic-evidence'),
  cinematicTitle: document.querySelector('#cinematic-title'),
  cinematicHud: document.querySelector('.cinematic-hud'),
  cinematicPlace: document.querySelector('#cinematic-place'),
  cinematicKpiWrap: document.querySelector('#cinematic-kpi-wrap'),
  cinematicKpiLabel: document.querySelector('#cinematic-kpi-label'),
  cinematicKpi: document.querySelector('#cinematic-kpi'),
  cinematicScope: document.querySelector('#cinematic-scope'),
  cinematicSupport: document.querySelector('#cinematic-support'),
  cinematicAnnotation: document.querySelector('#cinematic-annotation'),
  cinematicChart: document.querySelector('#cinematic-chart'),
  cinematicProgress: document.querySelector('#cinematic-progress'),
  cinematicFinal: document.querySelector('#cinematic-final'),
  cinematicClosingStats: document.querySelector('#cinematic-closing-stats'),
  cinematicTargetDogo: document.querySelector('#cinematic-target-dogo'),
  cinematicTargetMitsu: document.querySelector('#cinematic-target-mitsu'),
  cinematicExplore: document.querySelector('#cinematic-explore'),
  cinematicReplay: document.querySelector('#cinematic-replay')
};

const data = await loadData();

const state = {
  municipality: data.manifest.default_municipality_code,
  business: data.manifest.default_business_type,
  view: 'points',
  period: 'monthly',
  month: '2026-07',
  includeRetrospective: true,
  playing: false,
  timer: null,
  cinematic: false
};

const map = new Map({
  container: 'map',
  center: [132.765, 33.84],
  zoom: 11.4,
  minZoom: 7,
  maxZoom: 18,
  attributionControl: false,
  style: {
    version: 8,
    sources: {
      'cinematic-base': {
        type: 'vector', minzoom: 4, maxzoom: 16,
        tiles: ['pmtiles://https://cyberjapandata.gsi.go.jp/xyz/optimal_bvmap-v1/optimal_bvmap-v1.pmtiles/{z}/{x}/{y}'],
        attribution: '<a href="https://github.com/gsi-cyberjapan/optimal_bvmap" target="_blank">国土地理院最適化ベクトルタイル</a>'
      },
      gsi: {
        type: 'raster',
        tiles: ['https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png'],
        tileSize: 256,
        maxzoom: 18,
        attribution: '<a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank">地理院タイル</a>'
      }
    },
    layers: [{id: 'gsi', type: 'raster', source: 'gsi'}, {
      id: 'cinematic-background', type: 'background', layout: {visibility: 'none'},
      paint: {'background-color': '#080f16'}
    }, {
      id: 'cinematic-land', type: 'fill', source: 'cinematic-base', 'source-layer': 'AdmArea',
      layout: {visibility: 'none'}, paint: {'fill-color': '#111b24'}
    }, {
      id: 'cinematic-roads', type: 'line', source: 'cinematic-base', 'source-layer': 'RdCL',
      layout: {visibility: 'none'}, paint: {'line-color': '#30424e',
        'line-opacity': 0.38, 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.35, 14, 0.65]}
    }, {
      id: 'cinematic-coast', type: 'line', source: 'cinematic-base', 'source-layer': 'Cstline',
      layout: {visibility: 'none'}, paint: {'line-color': '#537080', 'line-opacity': 0.7, 'line-width': 0.85}
    }]
  }
});

map.addControl(new NavigationControl({showCompass: false}), 'top-right');
map.addControl(new AttributionControl({compact: true}), 'bottom-right');

const overlay = new MapLibreOverlay({
  interleaved: false,
  layers: [],
  getTooltip: makeTooltip
});
map.addControl(overlay);

const cinematicController = createCinematicController({
  map,
  overlay,
  data,
  state,
  els,
  stopAnalyticalPlayback: stopPlayback,
  analyticalLayers: layersForState,
  analyticalTooltip: makeTooltip,
  updateAnalytical: function() { updateAll(); },
  syncAnalytical: function() {
    syncButtons();
    syncTimeline();
  },
  onExploreTarget: exploreCinematicTarget
});

initializeControls();
updateAll();

function base(path) {
  return new URL(path, window.location.href).toString();
}

async function loadJson(name) {
  const response = await fetch(base(DATA + name));
  if (!response.ok) throw new Error('Failed to load ' + name);
  return response.json();
}

async function loadData() {
  const results = await Promise.all([
    loadJson('manifest.json'),
    loadJson('strict_new_events.json'),
    loadJson('matsuyama_retrospective_events.json'),
    loadJson('matsuyama_retrospective_monthly.json'),
    loadJson('coverage.json'),
    loadJson('municipality_monthly.json'),
    loadJson('matsuyama_mesh_1km_monthly.geojson'),
    loadJson('matsuyama_mesh_500m_monthly.geojson'),
    loadJson('matsuyama_mesh_1km_rolling12.geojson'),
    loadJson('matsuyama_mesh_500m_rolling12.geojson'),
    loadJson('matsuyama_spatial_centroid_monthly.geojson'),
    loadJson('cinematic_timeline_v2.json'),
    loadJson('cinematic_focus_series.json')
  ]);
  return {
    manifest: results[0],
    events: results[1],
    retrospectiveEvents: results[2],
    retrospectiveMonthly: results[3],
    coverage: results[4],
    municipalityMonthly: results[5],
    mesh1Monthly: results[6],
    mesh500Monthly: results[7],
    mesh1Rolling: results[8],
    mesh500Rolling: results[9],
    centroids: results[10],
    cinematicTimeline: results[11],
    cinematicFocusSeries: results[12]
  };
}

function initializeControls() {
  data.manifest.municipalities.forEach(function(m) {
    const option = document.createElement('option');
    option.value = m.code;
    option.textContent = m.name;
    els.municipality.append(option);
  });
  els.municipality.value = state.municipality;

  const all = document.createElement('option');
  all.value = '__ALL__';
  all.textContent = 'すべての業種';
  els.business.append(all);

  data.manifest.business_types.forEach(function(item) {
    const option = document.createElement('option');
    option.value = item.value;
    option.textContent = item.value + ' (' + item.count + ')';
    els.business.append(option);
  });
  els.business.value = state.business;
  els.retroToggle.checked = state.includeRetrospective;

  els.municipality.addEventListener('change', function() {
    stopPlayback();
    state.municipality = els.municipality.value;
    if (state.municipality !== '382019') {
      if (state.period === 'rolling12') state.period = 'monthly';
      if (state.view === 'mesh1' || state.view === 'mesh500') state.view = 'points';
    }
    resetMonthToLatest();
    syncButtons();
    updateAll(true);
  });

  els.business.addEventListener('change', function() {
    stopPlayback();
    state.business = els.business.value;
    if (!retroEligible() && isRetroMonth()) resetMonthToLatest();
    syncButtons();
    updateAll();
  });

  els.retroToggle.addEventListener('change', function() {
    stopPlayback();
    state.includeRetrospective = els.retroToggle.checked;
    if (!state.includeRetrospective && isRetroMonth()) resetMonthToLatest();
    syncTimeline();
    updateAll();
  });

  els.views.addEventListener('click', function(event) {
    const button = event.target.closest('button[data-view]');
    if (!button || button.disabled) return;
    const next = button.dataset.view;

    if ((next === 'mesh1' || next === 'mesh500') && state.municipality !== '382019') {
      state.municipality = '382019';
      els.municipality.value = '382019';
      resetMonthToLatest();
    }
    if (next === 'mesh1' || next === 'mesh500') {
      state.business = '飲食店営業';
      els.business.value = state.business;
    }

    state.view = next;
    syncButtons();
    updateAll(true);
  });

  els.periods.addEventListener('click', function(event) {
    const button = event.target.closest('button[data-period]');
    if (!button || button.disabled) return;
    state.period = button.dataset.period;

    if (
      state.period === 'rolling12'
      && !data.manifest.rolling12_end_months_matsuyama.includes(state.month)
    ) {
      state.month = data.manifest.rolling12_end_months_matsuyama.at(-1);
    }

    syncButtons();
    syncTimeline();
    updateAll();
  });

  els.slider.addEventListener('input', function() {
    stopPlayback();
    const months = timelineMonths();
    state.month = months[Number(els.slider.value)] || months.at(-1);
    updateAll();
  });

  els.play.addEventListener('click', function() {
    if (state.playing) stopPlayback();
    else startPlayback();
  });

  cinematicController.bindControls();

  syncButtons();
  syncTimeline();
}

function authorityForMunicipality(code) {
  return code === '382019' ? '松山市' : '愛媛県';
}

function retroEligible() {
  return (
    state.municipality === '382019'
    && state.business === '飲食店営業'
    && state.period === 'monthly'
    && state.includeRetrospective
  );
}

function isRetroMonth(month = state.month) {
  return data.manifest.matsuyama_retrospective_months.includes(month);
}

function timelineMonths() {
  if (state.period === 'rolling12') {
    return data.manifest.rolling12_end_months_matsuyama;
  }
  if (retroEligible()) {
    return data.manifest.matsuyama_hybrid_months;
  }
  return data.manifest.exact_months_by_authority[authorityForMunicipality(state.municipality)] || [];
}

function resetMonthToLatest() {
  const months = timelineMonths();
  state.month = months.at(-1) || state.month;
}

function normalizeViewForMonth() {
  if (isRetroMonth() && (state.view === 'mesh1' || state.view === 'mesh500')) {
    state.view = 'points';
  }
}

function syncTimeline() {
  const months = timelineMonths();
  if (!months.includes(state.month)) state.month = months.at(-1);
  const index = Math.max(0, months.indexOf(state.month));
  els.slider.max = String(Math.max(0, months.length - 1));
  els.slider.value = String(index);
  els.slider.disabled = months.length <= 1;
  els.start.textContent = months.at(0) || '—';
  els.current.textContent = state.month || '—';
  els.end.textContent = months.at(-1) || '—';
}

function syncButtons() {
  normalizeViewForMonth();

  els.views.querySelectorAll('button').forEach(function(button) {
    const mesh = button.dataset.view === 'mesh1' || button.dataset.view === 'mesh500';
    button.disabled = mesh && isRetroMonth();
    button.classList.toggle('active', button.dataset.view === state.view);
  });

  els.periods.querySelectorAll('button').forEach(function(button) {
    const rolling = button.dataset.period === 'rolling12';
    button.disabled = rolling && state.municipality !== '382019';
    button.classList.toggle('active', button.dataset.period === state.period);
  });

  els.retroToggle.disabled = !(
    state.municipality === '382019'
    && state.business === '飲食店営業'
    && state.period === 'monthly'
  );

  const meshMode = state.view === 'mesh1' || state.view === 'mesh500';
  els.business.disabled = meshMode;

  if (isRetroMonth()) {
    els.modeNote.textContent = '参考復元期：2026-03-31時点の全施設一覧を初回許可日に遡及。町丁目代表点を含み、当時の全新規許可を完全収録していません。';
  } else if (meshMode) {
    els.modeNote.textContent = 'メッシュは完全観測期の飲食店営業・番地/地番レベル座標のみ。';
  } else if (state.period === 'rolling12') {
    els.modeNote.textContent = '12か月すべて完全観測できる松山市の期間だけ表示。';
  } else {
    els.modeNote.textContent = '完全観測期：Point / Heatmap / Hexagon は高精度地点のみ。';
  }
}

function startPlayback() {
  const months = timelineMonths();
  if (months.length <= 1) return;

  state.playing = true;
  els.play.textContent = 'Ⅱ';
  state.timer = window.setInterval(function() {
    const current = months.indexOf(state.month);
    state.month = months[(current + 1) % months.length];
    syncTimeline();
    updateAll();
  }, 800);
}

function stopPlayback() {
  if (state.timer) window.clearInterval(state.timer);
  state.timer = null;
  state.playing = false;
  els.play.textContent = '▶';
}

function monthWindow(endMonth) {
  const parts = endMonth.split('-').map(Number);
  const end = new Date(Date.UTC(parts[0], parts[1] - 1, 1));
  const months = [];

  for (let i = 11; i >= 0; i -= 1) {
    const d = new Date(Date.UTC(end.getUTCFullYear(), end.getUTCMonth() - i, 1));
    months.push(
      d.getUTCFullYear()
      + '-'
      + String(d.getUTCMonth() + 1).padStart(2, '0')
    );
  }
  return new Set(months);
}

function filteredEvents() {
  if (state.period === 'monthly' && isRetroMonth() && retroEligible()) {
    return data.retrospectiveEvents.filter(function(d) {
      return d.month === state.month;
    });
  }

  const windowMonths = state.period === 'rolling12' ? monthWindow(state.month) : null;

  return data.events.filter(function(d) {
    if (d.municipality_code !== state.municipality) return false;
    if (state.business !== '__ALL__' && d.business_type !== state.business) return false;

    if (state.period === 'rolling12') {
      return windowMonths.has(d.month);
    }
    return d.month === state.month;
  });
}

function municipalityMetric() {
  if (state.business !== '飲食店営業') return null;

  if (state.period === 'monthly' && isRetroMonth() && retroEligible()) {
    const row = data.retrospectiveMonthly.find(function(d) {
      return d.month === state.month;
    });
    if (!row) return null;
    return {
      new_restaurant_permits: Number(row.retrospective_rows),
      strict_address_or_parcel: Number(row.strict_address_or_parcel),
      town_or_better: Number(row.town_or_better),
      retrospective: true
    };
  }

  if (state.period === 'monthly') {
    return data.municipalityMonthly.find(function(d) {
      return d.municipality_code === state.municipality && d.month === state.month;
    }) || null;
  }

  const months = monthWindow(state.month);
  const rows = data.municipalityMonthly.filter(function(d) {
    return d.municipality_code === state.municipality && months.has(d.month);
  });

  if (rows.length !== 12) return null;

  return {
    new_restaurant_permits: rows.reduce(function(sum, d) {
      return sum + d.new_restaurant_permits;
    }, 0),
    strict_address_or_parcel: rows.reduce(function(sum, d) {
      return sum + d.strict_address_or_parcel;
    }, 0),
    town_or_better: rows.reduce(function(sum, d) {
      return sum + d.town_or_better;
    }, 0)
  };
}

function selectedMeshData() {
  const rolling = state.period === 'rolling12';
  let source;

  if (state.view === 'mesh500') {
    source = rolling ? data.mesh500Rolling : data.mesh500Monthly;
  } else {
    source = rolling ? data.mesh1Rolling : data.mesh1Monthly;
  }

  const key = rolling ? 'window_end_month' : 'month';

  return {
    type: 'FeatureCollection',
    features: source.features.filter(function(feature) {
      return feature.properties[key] === state.month;
    })
  };
}

function colorForCount(value, max) {
  const t = max <= 1 ? 1 : Math.max(0, Math.min(1, value / max));
  return [
    Math.round(236 - 69 * t),
    Math.round(209 - 139 * t),
    Math.round(158 - 115 * t),
    Math.round(95 + 130 * t)
  ];
}

function layersForState() {
  const events = filteredEvents();
  const retro = isRetroMonth() && retroEligible();

  if (state.view === 'points') {
    return [
      new ScatterplotLayer({
        id: 'points-' + state.month + '-' + state.period + '-' + (retro ? 'retro' : 'exact'),
        data: events,
        getPosition: function(d) { return [d.lon, d.lat]; },
        getRadius: function(d) {
          if (!retro) return 36;
          return d.quality === 'address_or_parcel' ? 38 : 58;
        },
        radiusMinPixels: retro ? 3 : 4,
        radiusMaxPixels: retro ? 12 : 10,
        getFillColor: function(d) {
          if (!retro) return COLORS.exact;
          return d.quality === 'address_or_parcel' ? COLORS.retroStrict : COLORS.retroTown;
        },
        getLineColor: retro ? [255, 250, 236, 150] : [255, 255, 255, 220],
        lineWidthMinPixels: 1,
        stroked: true,
        pickable: true,
        autoHighlight: true
      })
    ];
  }

  if (state.view === 'heatmap') {
    return [
      new HeatmapLayer({
        id: 'heat-' + state.month + '-' + state.period + '-' + (retro ? 'retro' : 'exact'),
        data: events,
        getPosition: function(d) { return [d.lon, d.lat]; },
        getWeight: function(d) {
          return retro && d.quality === 'town_centroid' ? 0.7 : 1;
        },
        radiusPixels: retro ? 54 : 46,
        intensity: retro ? 1.25 : 1.1,
        threshold: 0.03
      })
    ];
  }

  if (state.view === 'hexagon') {
    return [
      new HexagonLayer({
        id: 'hex-' + state.month + '-' + state.period + '-' + (retro ? 'retro' : 'exact'),
        data: events,
        getPosition: function(d) { return [d.lon, d.lat]; },
        radius: retro ? 450 : 350,
        extruded: true,
        elevationScale: retro ? 13 : 22,
        elevationRange: [0, 1600],
        coverage: 0.82,
        upperPercentile: 100,
        pickable: true,
        colorRange: retro
          ? [
              [244, 226, 176],
              [239, 200, 126],
              [228, 164, 73],
              [202, 123, 44],
              [158, 88, 39],
              [112, 60, 36]
            ]
          : [
              [240, 221, 181],
              [231, 190, 131],
              [220, 141, 87],
              [199, 91, 61],
              [159, 55, 45],
              [106, 38, 40]
            ]
      })
    ];
  }

  const geo = selectedMeshData();
  const valueKey = state.period === 'rolling12'
    ? 'new_restaurant_permits_12m'
    : 'new_restaurant_permits';

  const values = geo.features.map(function(feature) {
    return Number(feature.properties[valueKey] || 0);
  });
  const max = Math.max.apply(null, [1].concat(values));

  return [
    new GeoJsonLayer({
      id: state.view + '-' + state.month + '-' + state.period,
      data: geo,
      filled: true,
      stroked: true,
      getFillColor: function(feature) {
        return colorForCount(Number(feature.properties[valueKey] || 0), max);
      },
      getLineColor: [255, 255, 255, 180],
      lineWidthMinPixels: 1,
      pickable: true,
      autoHighlight: true
    })
  ];
}

function makeTooltip(info) {
  if (!info || !info.object) return null;
  const object = info.object;

  if (object.facility_name) {
    let evidence = '';
    if (object.evidence === 'retrospective_partial_survivor_biased') {
      const precision = object.quality === 'address_or_parcel'
        ? '番地/地番レベル'
        : '町丁目代表点';
      evidence = '<div style="color:#f2c36f">参考復元・不完全 / ' + precision + '</div>';
    }
    return {
      html:
        '<strong>' + escapeHtml(object.facility_name) + '</strong>'
        + evidence
        + '<div>' + escapeHtml(object.business_type || '') + '</div>'
        + '<div>' + escapeHtml(object.date || '') + '</div>'
        + '<div style="opacity:.68">' + escapeHtml(object.address || '') + '</div>'
    };
  }

  if (object.properties) {
    const p = object.properties;
    const count = p.new_restaurant_permits_12m != null
      ? p.new_restaurant_permits_12m
      : p.new_restaurant_permits;
    const mesh = p.mesh_500m || p.mesh_1km || '';

    return {
      html:
        '<strong>' + escapeHtml(mesh) + '</strong>'
        + '<div>新規飲食店許可 ' + escapeHtml(String(count || 0)) + '件</div>'
    };
  }

  if (object.points) {
    return {text: String(object.points.length) + ' displayed permit points'};
  }

  return null;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function coverageStatus() {
  if (state.period === 'rolling12') {
    if (data.manifest.rolling12_end_months_matsuyama.includes(state.month)) {
      return {label: '完全観測 12か月', cls: 'complete'};
    }
    return {label: '12か月不足', cls: 'unavailable'};
  }

  if (isRetroMonth() && retroEligible()) {
    return {label: '参考復元・不完全', cls: 'partial'};
  }

  const authority = authorityForMunicipality(state.municipality);
  const row = data.coverage.find(function(d) {
    return d.authority === authority && d.month === state.month;
  });

  if (!row) return {label: '観測範囲外', cls: 'unavailable'};

  if (row.coverage_status === 'complete_exact_monthly') {
    return {label: '完全観測 月次', cls: 'complete'};
  }
  if (row.coverage_status === 'partial_retrospective') {
    return {label: '部分遡及', cls: 'partial'};
  }
  return {label: '利用不可', cls: 'unavailable'};
}

function updateAll(fly) {
  syncTimeline();
  normalizeViewForMonth();
  syncButtons();

  overlay.setProps({
    layers: layersForState(),
    getTooltip: makeTooltip
  });

  const filtered = filteredEvents();
  const municipality = municipalityMetric();
  const mesh = state.view === 'mesh1' || state.view === 'mesh500'
    ? selectedMeshData()
    : null;
  const retro = isRetroMonth() && retroEligible();

  els.totalLabel.textContent = retro ? '参考復元件数' : '新規飲食店許可';
  els.pointsLabel.textContent = retro ? '表示地点（町丁目以上）' : '高精度地点';

  els.total.textContent = municipality
    ? municipality.new_restaurant_permits.toLocaleString('ja-JP')
    : '—';

  els.points.textContent = filtered.length.toLocaleString('ja-JP');

  if (mesh) {
    els.thirdLabel.textContent = '表示セル';
    els.third.textContent = mesh.features.length.toLocaleString('ja-JP');
  } else if (retro && municipality) {
    els.thirdLabel.textContent = '番地/地番';
    els.third.textContent = Number(municipality.strict_address_or_parcel).toLocaleString('ja-JP');
  } else {
    els.thirdLabel.textContent = state.period === 'rolling12' ? '対象月数' : '対象月';
    els.third.textContent = state.period === 'rolling12' ? '12' : '1';
  }

  const cov = coverageStatus();
  els.coverage.className = 'badge ' + cov.cls;
  els.coverage.textContent = cov.label;

  if (state.period === 'rolling12') {
    const months = Array.from(monthWindow(state.month));
    els.periodLabel.textContent = months[0] + ' → ' + state.month;
  } else {
    els.periodLabel.textContent = state.month;
  }

  els.current.textContent = state.month;

  const municipalityInfo = data.manifest.municipalities.find(function(m) {
    return m.code === state.municipality;
  });
  const municipalityName = municipalityInfo ? municipalityInfo.name : '';

  els.caption.textContent =
    municipalityName + ' / ' + state.month + ' / ' + viewLabel()
    + (retro ? ' / 参考復元' : '');

  const empty = mesh ? mesh.features.length === 0 : filtered.length === 0;
  els.empty.hidden = !empty;

  if (empty) {
    if (retro) {
      els.emptyDetail.textContent =
        'この参考復元月には町丁目以上で表示できる地点がありません。';
    } else if (state.municipality === '382019') {
      els.emptyDetail.textContent =
        '選択した月・業種・精度条件に該当する地点がありません。';
    } else {
      els.emptyDetail.textContent =
        '県旧履歴は市町村レベル住所が中心のため、細かな施設点を推定表示していません。';
    }
  }

  if (fly) {
    if (state.municipality === '382019') {
      map.flyTo({center: [132.765, 33.84], zoom: 11.4, duration: 600});
    } else {
      map.flyTo({center: [132.77, 33.65], zoom: 8.4, duration: 600});
    }
  }
}


function exploreCinematicTarget(target) {
  stopPlayback();
  state.municipality = '382019';
  state.business = '飲食店営業';
  state.view = 'points';
  state.period = 'monthly';
  state.includeRetrospective = true;
  state.month = target.month;

  els.municipality.value = state.municipality;
  els.business.value = state.business;
  els.retroToggle.checked = true;

  syncButtons();
  syncTimeline();
  updateAll();
  map.jumpTo({
    center: target.center,
    zoom: target.zoom,
    pitch: 0,
    bearing: 0
  });
}

function viewLabel() {
  const labels = {
    points: 'Points',
    heatmap: 'Heatmap',
    hexagon: 'Hexagon',
    mesh1: '1km mesh',
    mesh500: '500m mesh'
  };
  return labels[state.view];
}

window.addEventListener('beforeunload', function() {
  stopPlayback();
  cinematicController.destroy();
});
