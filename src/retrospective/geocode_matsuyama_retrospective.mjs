import fs from 'node:fs';
import path from 'node:path';
import {normalize} from '@geolonia/normalize-japanese-addresses';

const root=process.cwd();
const inputPath=path.join(root,'data','geocode','matsuyama_retrospective_input.json');
const exactCachePath=path.join(root,'data','geocode','geocode_cache.json');
const outputPath=path.join(root,'data','geocode','matsuyama_retrospective_geocode_cache.json');

function readJson(p,fallback){
  if(!fs.existsSync(p)) return fallback;
  return JSON.parse(fs.readFileSync(p,'utf8'));
}

function quality(pointLevel,hasPoint){
  if(!hasPoint) return 'failed';
  if(pointLevel>=8) return 'address_or_parcel';
  if(pointLevel>=3) return 'town_centroid';
  if(pointLevel>=2) return 'municipality_centroid';
  if(pointLevel>=1) return 'prefecture_centroid';
  return 'failed';
}

async function geocodeOne(item){
  try{
    const r=await normalize(item.geocode_input);
    const point=r?.point||null;
    const lat=point && Number.isFinite(Number(point.lat)) ? Number(point.lat) : null;
    const lon=point && Number.isFinite(Number(point.lng)) ? Number(point.lng) : null;
    const pointLevel=Number(point?.level??0);
    const q=quality(pointLevel,lat!==null&&lon!==null);
    return {
      address_key:item.address_key,
      source_address:item.source_address,
      normalized_prefecture:r?.pref||'',
      normalized_city:r?.city||'',
      normalized_town:r?.town||'',
      normalized_addr:r?.addr||'',
      unmatched_other:r?.other||'',
      normalize_level:Number(r?.level??0),
      point_level:pointLevel,
      latitude:lat,
      longitude:lon,
      geocode_quality:q,
      error:''
    };
  }catch(error){
    return {
      address_key:item.address_key,
      source_address:item.source_address,
      normalized_prefecture:'',
      normalized_city:'',
      normalized_town:'',
      normalized_addr:'',
      unmatched_other:'',
      normalize_level:0,
      point_level:0,
      latitude:null,
      longitude:null,
      geocode_quality:'failed',
      error:String(error?.message||error)
    };
  }
}

async function main(){
  const input=readJson(inputPath,null);
  if(!input) throw new Error('missing input');

  const exact=readJson(exactCachePath,{results:[]});
  const old=readJson(outputPath,{results:[]});
  const cache=new Map();

  for(const r of exact.results||[]) cache.set(r.address_key,r);
  for(const r of old.results||[]) cache.set(r.address_key,r);

  const pending=input.items.filter(x=>!cache.has(x.address_key));
  let cursor=0,completed=0;
  const concurrency=12;

  async function worker(){
    while(true){
      const i=cursor++;
      if(i>=pending.length) return;
      const result=await geocodeOne(pending[i]);
      cache.set(pending[i].address_key,result);
      completed++;
      if(completed%100===0||completed===pending.length){
        console.log('geocoded '+completed+'/'+pending.length);
      }
    }
  }

  await Promise.all(Array.from({length:Math.min(concurrency,pending.length||1)},()=>worker()));

  const results=input.items.map(x=>cache.get(x.address_key)).filter(Boolean);
  const q={};
  for(const r of results) q[r.geocode_quality]=(q[r.geocode_quality]||0)+1;

  const output={
    schema_version:1,
    geocoder:{engine:'@geolonia/normalize-japanese-addresses',version:'3.1.3',crs:'EPSG:4326'},
    reused_exact_cache_addresses:input.items.length-pending.length,
    newly_geocoded_addresses:pending.length,
    results
  };
  fs.writeFileSync(outputPath,JSON.stringify(output,null,2),'utf8');
  console.log(JSON.stringify({total:results.length,reused:output.reused_exact_cache_addresses,newly_geocoded:pending.length,quality_counts:q},null,2));
}

await main();
