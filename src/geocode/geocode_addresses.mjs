import fs from 'node:fs';
import path from 'node:path';
import { normalize } from '@geolonia/normalize-japanese-addresses';

const root = process.cwd();
const inputPath = path.join(root, 'data', 'geocode', 'geocode_input.json');
const cachePath = path.join(root, 'data', 'geocode', 'geocode_cache.json');

const GEOCODER = {
  engine: '@geolonia/normalize-japanese-addresses',
  version: '3.1.3',
  data_endpoint: 'https://japanese-addresses-v2.geoloniamaps.com/api/ja',
  crs: 'EPSG:4326'
};

const EHIME_CODES = {
  '松山市': '382019',
  '今治市': '382027',
  '宇和島市': '382035',
  '八幡浜市': '382043',
  '新居浜市': '382051',
  '西条市': '382060',
  '大洲市': '382078',
  '伊予市': '382108',
  '四国中央市': '382132',
  '西予市': '382141',
  '東温市': '382159',
  '上島町': '383562',
  '久万高原町': '383864',
  '松前町': '384011',
  '砥部町': '384020',
  '内子町': '384224',
  '伊方町': '384429',
  '松野町': '384844',
  '鬼北町': '384887',
  '愛南町': '385069'
};

function readJson(p, fallback) {
  if (!fs.existsSync(p)) return fallback;
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function municipalityCode(city = '') {
  for (const [name, code] of Object.entries(EHIME_CODES)) {
    if (city === name || city.endsWith(name)) return code;
  }
  return '';
}

function quality(level, pointLevel, hasPoint) {
  if (!hasPoint) return 'failed';
  if (pointLevel >= 8) return 'address_or_parcel';
  if (pointLevel >= 3) return 'town_centroid';
  if (pointLevel >= 2) return 'municipality_centroid';
  if (pointLevel >= 1) return 'prefecture_centroid';
  return 'failed';
}

function normalizedAddress(r) {
  return [r.pref || '', r.city || '', r.town || '', r.addr || ''].join('');
}

async function geocodeOne(item) {
  try {
    const r = await normalize(item.geocode_input);
    const point = r?.point || null;
    const level = Number(r?.level ?? 0);
    const pointLevel = Number(point?.level ?? 0);
    const lat = point && Number.isFinite(Number(point.lat)) ? Number(point.lat) : null;
    const lng = point && Number.isFinite(Number(point.lng)) ? Number(point.lng) : null;
    const hasPoint = lat !== null && lng !== null;
    const q = quality(level, pointLevel, hasPoint);
    return {
      address_key: item.address_key,
      source_address: item.source_address,
      geocode_input: item.geocode_input,
      normalized_prefecture: r?.pref || '',
      normalized_city: r?.city || '',
      normalized_town: r?.town || '',
      normalized_addr: r?.addr || '',
      unmatched_other: r?.other || '',
      normalized_address: normalizedAddress(r || {}),
      normalize_level: level,
      point_level: pointLevel,
      latitude: lat,
      longitude: lng,
      geocode_quality: q,
      map_usable_strict: q === 'address_or_parcel',
      map_usable_town_or_better: q === 'address_or_parcel' || q === 'town_centroid',
      derived_municipality_code: municipalityCode(r?.city || ''),
      error: ''
    };
  } catch (error) {
    return {
      address_key: item.address_key,
      source_address: item.source_address,
      geocode_input: item.geocode_input,
      normalized_prefecture: '',
      normalized_city: '',
      normalized_town: '',
      normalized_addr: '',
      unmatched_other: '',
      normalized_address: '',
      normalize_level: 0,
      point_level: 0,
      latitude: null,
      longitude: null,
      geocode_quality: 'failed',
      map_usable_strict: false,
      map_usable_town_or_better: false,
      derived_municipality_code: '',
      error: String(error?.message || error)
    };
  }
}

async function main() {
  const input = readJson(inputPath, null);
  if (!input) throw new Error('Missing ' + inputPath);

  const old = readJson(cachePath, { results: [] });
  const cache = new Map((old.results || []).map(x => [x.address_key, x]));

  const pending = input.items.filter(x => !cache.has(x.address_key));
  const concurrency = 12;
  let cursor = 0;
  let completed = 0;

  async function worker() {
    while (true) {
      const i = cursor++;
      if (i >= pending.length) return;
      const item = pending[i];
      const result = await geocodeOne(item);
      cache.set(item.address_key, result);
      completed += 1;
      if (completed % 100 === 0 || completed === pending.length) {
        console.log('geocoded ' + completed + '/' + pending.length + ' pending addresses');
      }
    }
  }

  await Promise.all(
    Array.from({ length: Math.min(concurrency, pending.length || 1) }, () => worker())
  );

  const results = input.items.map(x => cache.get(x.address_key)).filter(Boolean);
  const output = {
    schema_version: 1,
    geocoder: GEOCODER,
    municipality_code_reference: 'Ehime Prefecture official municipal-code table',
    generated_at: new Date().toISOString(),
    source_unique_addresses: input.unique_nonempty_addresses,
    newly_geocoded_addresses: pending.length,
    results
  };
  fs.writeFileSync(cachePath, JSON.stringify(output, null, 2), 'utf8');

  const q = {};
  for (const r of results) q[r.geocode_quality] = (q[r.geocode_quality] || 0) + 1;
  console.log(JSON.stringify({
    total: results.length,
    newly_geocoded: pending.length,
    quality_counts: q
  }, null, 2));
}

await main();
