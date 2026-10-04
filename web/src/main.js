import maplibregl, {setWorkerUrl} from 'maplibre-gl';
import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import 'maplibre-gl/dist/maplibre-gl.css';
import {MapLibreOverlay} from '@deck.gl/maplibre';
import {ScatterplotLayer, GeoJsonLayer} from '@deck.gl/layers';
import {HeatmapLayer, HexagonLayer} from '@deck.gl/aggregation-layers';
import './style.css';

setWorkerUrl(maplibreWorkerUrl);

const DATA = './data/';
const COLORS = {
  accent: [221, 90, 58, 210]
};

const els = {
  municipality: document.querySelector('#municipality-select'),
  business: document.querySelector('#business-select'),
  views: document.querySelector('#view-switcher'),
  periods: document.querySelector('#period-switcher'),
  slider: document.querySelector('#month-slider'),
  play: document.querySelector('#play-button'),
  start: document.querySelector('#timeline-start'),
  current: document.querySelector('#timeline-current'),
  end: document.querySelector('#timeline-end'),
  coverage: document.querySelector('#coverage-badge'),
  periodLabel: document.querySelector('#period-label'),
  modeNote: document.querySelector('#mode-note'),
  total: document.querySelector('#metric-total'),
  points: document.querySelector('#metric-points'),
  third: document.querySelector('#metric-third'),
  thirdLabel: document.querySelector('#metric-third-label'),
  empty: document.querySelector('#empty-state'),
  emptyDetail: document.querySelector('#empty-detail'),
  caption: document.querySelector('#map-caption-main')
};

const data = await loadData();

const state = {
  municipality: data.manifest.default_municipality_code,
  business: data.manifest.default_business_type,
  view: 'points',
  period: 'monthly',
  month: '2026-07',
  playing: false,
  timer: null
};

const map = new maplibregl.Map({
  container: 'map',
  center: [132.765, 33.84],
  zoom: 11.4,
  minZoom: 7,
  maxZoom: 18,
  attributionControl: false,
  style: {
    version: 8,
    sources: {
      gsi: {
        type: 'raster',
        tiles: ['https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png'],
        tileSize: 256,
        maxzoom: 18,
        attribution: '<a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank">地理院タイル</a>'
      }
    },
    layers: [{id: 'gsi', type: 'raster', source: 'gsi'}]
  }
});

map.addControl(new maplibregl.NavigationControl({showCompass: false}), 'top-right');
map.addControl(new maplibregl.AttributionControl({compact: true}), 'bottom-right');

const overlay = new MapLibreOverlay({
  interleaved: false,
  layers: [],
  getTooltip: makeTooltip
});
map.addControl(overlay);

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
    loadJson('coverage.json'),
    loadJson('municipality_monthly.json'),
    loadJson('matsuyama_mesh_1km_monthly.geojson'),
    loadJson('matsuyama_mesh_500m_monthly.geojson'),
    loadJson('matsuyama_mesh_1km_rolling12.geojson'),
    loadJson('matsuyama_mesh_500m_rolling12.geojson'),
    loadJson('matsuyama_spatial_centroid_monthly.geojson')
  ]);
  return {
    manifest: results[0],
    events: results[1],
    coverage: results[2],
    municipalityMonthly: results[3],
    mesh1Monthly: results[4],
    mesh500Monthly: results[5],
    mesh1Rolling: results[6],
    mesh500Rolling: results[7],
    centroids: results[8]
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
    state.business = els.business.value;
    updateAll();
  });

  els.views.addEventListener('click', function(event) {
    const button = event.target.closest('button[data-view]');
    if (!button) return;
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

  syncButtons();
  syncTimeline();
}

function authorityForMunicipality(code) {
  return code === '382019' ? '松山市' : '愛媛県';
}

function timelineMonths() {
  if (state.period === 'rolling12') {
    return data.manifest.rolling12_end_months_matsuyama;
  }
  return data.manifest.exact_months_by_authority[authorityForMunicipality(state.municipality)] || [];
}

function resetMonthToLatest() {
  const months = timelineMonths();
  state.month = months.at(-1) || state.month;
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
  els.views.querySelectorAll('button').forEach(function(button) {
    button.classList.toggle('active', button.dataset.view === state.view);
  });

  els.periods.querySelectorAll('button').forEach(function(button) {
    const rolling = button.dataset.period === 'rolling12';
    button.disabled = rolling && state.municipality !== '382019';
    button.classList.toggle('active', button.dataset.period === state.period);
  });

  const meshMode = state.view === 'mesh1' || state.view === 'mesh500';
  els.business.disabled = meshMode;

  if (meshMode) {
    els.modeNote.textContent = 'メッシュは飲食店営業・番地/地番レベル座標のみ。';
  } else if (state.period === 'rolling12') {
    els.modeNote.textContent = '12か月すべて完全観測できる松山市の期間だけ表示。';
  } else {
    els.modeNote.textContent = 'Point / Heatmap / Hexagon は高精度地点のみ。';
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
  }, 900);
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

  if (state.view === 'points') {
    return [
      new ScatterplotLayer({
        id: 'points-' + state.month + '-' + state.period,
        data: events,
        getPosition: function(d) { return [d.lon, d.lat]; },
        getRadius: 36,
        radiusMinPixels: 4,
        radiusMaxPixels: 10,
        getFillColor: COLORS.accent,
        getLineColor: [255, 255, 255, 220],
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
        id: 'heat-' + state.month + '-' + state.period,
        data: events,
        getPosition: function(d) { return [d.lon, d.lat]; },
        getWeight: 1,
        radiusPixels: 46,
        intensity: 1.1,
        threshold: 0.03
      })
    ];
  }

  if (state.view === 'hexagon') {
    return [
      new HexagonLayer({
        id: 'hex-' + state.month + '-' + state.period,
        data: events,
        getPosition: function(d) { return [d.lon, d.lat]; },
        radius: 350,
        extruded: true,
        elevationScale: 22,
        elevationRange: [0, 1600],
        coverage: 0.82,
        upperPercentile: 100,
        pickable: true,
        colorRange: [
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
    return {
      html:
        '<strong>' + escapeHtml(object.facility_name) + '</strong>'
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
    return {text: String(object.points.length) + ' high-precision permit points'};
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

  els.total.textContent = municipality
    ? municipality.new_restaurant_permits.toLocaleString('ja-JP')
    : '—';

  els.points.textContent = filtered.length.toLocaleString('ja-JP');

  if (mesh) {
    els.thirdLabel.textContent = '表示セル';
    els.third.textContent = mesh.features.length.toLocaleString('ja-JP');
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
    municipalityName + ' / ' + state.month + ' / ' + viewLabel();

  const empty = mesh ? mesh.features.length === 0 : filtered.length === 0;
  els.empty.hidden = !empty;

  if (empty) {
    if (state.municipality === '382019') {
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

window.addEventListener('beforeunload', stopPlayback);
