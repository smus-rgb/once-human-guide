
const NAV=[
  {g:'Command',items:[{id:'home',label:'Home',ic:'⌂'},{id:'search',label:'Search',ic:'⌕'},{id:'ai',label:'AI Guide',ic:'✦'}]},
  {g:'World',items:[{id:'map',label:'Map',ic:'◎'},{id:'events',label:'Events',ic:'⏱'},{id:'scenarios',label:'Scenarios',ic:'⚑'}]},
  {g:'Data',items:[
    {id:'db',label:'Database',ic:'☰'},{id:'items',label:'Items',ic:'◆'},{id:'weapons',label:'Weapons',ic:'⚔'},
    {id:'armor',label:'Armor',ic:'⛨'},{id:'mods',label:'Mods',ic:'⬡'},{id:'deviations',label:'Deviations',ic:'✶'},
    {id:'bestiary',label:'Bestiary',ic:'☠'},{id:'animals',label:'Animals DB',ic:'🐾'},{id:'plants',label:'Plants',ic:'❀'},
    {id:'resources',label:'Resources',ic:'▣'},{id:'locations',label:'Locations',ic:'📍'}
  ]},
  {g:'Play',items:[{id:'craft',label:'Crafting',ic:'⚒'},{id:'builds',label:'Build Planner',ic:'♟'},{id:'herbalist',label:'Herbalist',ic:'🍵'},{id:'grafting',label:'Flower Grafting',ic:'⚘'},{id:'animalsys',label:'Animal system',ic:'🐄'}]},
  {g:'Me',items:[{id:'progress',label:'Progress',ic:'☑'},{id:'favorites',label:'Favorites',ic:'★'},{id:'inventory',label:'Inventory',ic:'🎒'}]},
  {g:'System',items:[{id:'agent',label:'AI Agent',ic:'⚙'},{id:'settings',label:'Settings',ic:'sl'},{id:'offline',label:'Offline / Sync',ic:'☁'}]}
];
const PHONE_MORE=['ai','builds','craft','scenarios','progress','herbalist','grafting','animalsys','events','favorites','inventory','agent','settings','offline'];
const DB_CATS={
  items:{key:'materials',title:'Items / Materials'},
  weapons:{key:'weapons',title:'Weapons'},
  armor:{key:'armor',title:'Armor'},
  mods:{key:'mods',title:'Mods'},
  deviations:{key:'deviations',title:'Deviations'},
  bestiary:{key:'creatures',title:'Enemies / Bestiary',extra:'bosses'},
  animals:{key:'animals',title:'Animals'},
  plants:{key:'plants',title:'Plants',extra:'flowers'},
  resources:{key:'materials',title:'Resources'},
  locations:{key:'locations',title:'Locations'}
};
const BUILD_SLOTS=[
  {id:'weapon1',label:'Zbraň 1',cats:['weapons']},
  {id:'weapon2',label:'Zbraň 2',cats:['weapons']},
  {id:'armor',label:'Zbroj (set)',cats:['armor']},
  {id:'mod',label:'Mod',cats:['mods']},
  {id:'deviation',label:'Deviation',cats:['deviations']}
];
/* Doomeris / Anestic multiplikativní buckety */
const BUCKETS=['weapon','elemental','status','critDmg','weakspot','vuln','attack','enemy'];
const META_PRESETS=[
  {id:'shrapnel_socr',name:'Shrapnel Crit (SOCR)',src:'Doomeris / meta · S',tags:['shrapnel','crit','dps','s-tier'],note:'Univerzální PvE. Crit Rate → Shrapnel procs. SOCR Last Valor + Lonewolf/Falcon.',slots:{weaponHint:'SOCR – The Last Valor',armorHint:'Lonewolf 2–4 + Falcon',modHint:'Violent / Crit / Deadshot',devHint:'Lonewolf Whisper / Butterfly'}},
  {id:'sn700_finale',name:'SN700 Finale Shrapnel',src:'Doomeris · S+ bossing',tags:['shrapnel','sniper','weakspot','s-tier'],note:'Top single-target bossing. Weakspot Shrapnel, Reverb stacks.',slots:{weaponHint:'SN700 – Finale',armorHint:'Lonewolf / Treacherous / Ghost Link',modHint:'Shatter / Violent / Shrapnel',devHint:'Butterfly / Lonewolf'}},
  {id:'pdw90_holo',name:'PDW90 Holographic',src:'meta · S Bullseye SMG',tags:['bullseye','smg','crit','s-tier'],note:'Bullseye mark + Vulnerability. Forsaken Giant / silo melter.',slots:{weaponHint:'PDW90 – Holographic Resonance',armorHint:'Lonewolf / 3 Treach + 2 Lonewolf',modHint:'Vulnerability Amplifier',devHint:'Lonewolf / Zapamander'}},
  {id:'doom_bullseye',name:'Doombringer Bullseye',src:'Doomeris',tags:['shotgun','bullseye','close'],note:'Close range, Vulnerability Amp na gun+mask.',slots:{weaponHint:'DBSG – Doombringer',armorHint:'3 Treach + 2 Lonewolf',modHint:'Vulnerability Amplifier',devHint:'Lonewolf Whisper'}},
  {id:'jaws_bomber',name:'Jaws Unstable Bomber',src:'Anestic / Azel · S burst',tags:['unstable-bomber','pistol','burst','crit'],note:'Výbuchy Unstable Bomber. Status + Crit DMG. ≥50 % Crit Rate.',slots:{weaponHint:'DE.50 – Jaws',armorHint:'Falcon / Lonewolf / Wind Interpreter',modHint:'Unstable Bomber suffix',devHint:'Butterfly / Voodoo'}},
  {id:'qbj_fiery',name:'QBJ97 Fiery Trees',src:'Anestic · Unstable Bomber AR',tags:['unstable-bomber','ar','aoe'],note:'Unstable Bomber na AR. AoE clear + burst.',slots:{weaponHint:'QBJ97 – Fiery Trees',armorHint:'Falcon / Lonewolf',modHint:'Unstable Bomber / Crit',devHint:'Butterfly'}},
  {id:'blaze_ebr',name:'Blaze / Burn (EBR)',src:'Doomeris / Anestic',tags:['blaze','burn','status'],note:'Elemental + Status + Burn jako oddělené buckety.',slots:{weaponHint:'EBR-14 – Octopus Grilled Rings',armorHint:'Shelterer / Pyro',modHint:'Blaze / Elemental Overload',devHint:'Pyro deviant'}},
  {id:'acs_pyro',name:'ACS12 Pyroclasm',src:'meta · Blaze shotgun',tags:['blaze','shotgun','s-tier'],note:'Burn on hit, fire pools.',slots:{weaponHint:'ACS12 – Pyroclasm',armorHint:'Shelterer',modHint:'Blaze / Status',devHint:'Pyro'}},
  {id:'surge_shock',name:'Power Surge / Shock',src:'Doomeris',tags:['shock','surge','elemental'],note:'PSI Intensity base. Elemental × Status × Power Surge %.',slots:{weaponHint:'AUG Electron / ACS Corrosion',armorHint:'Shelterer 4 / Stormweaver',modHint:'Elemental Overload',devHint:'Shock deviant'}},
  {id:'frost_path',name:'Frost Vortex (SKS)',src:'Anestic · S all-round',tags:['frost','status','aoe','s-tier'],note:'Balance Status ≈ Weakspot ≈ Elemental.',slots:{weaponHint:'SKS – Pathfinder',armorHint:'Shelterer / Bastille',modHint:'Status + Elemental + Weakspot',devHint:'Frost / Aero'}},
  {id:'mg4_memories',name:'MG4 Conflicting Memories',src:'Anestic · Shrapnel LMG',tags:['shrapnel','lmg','dps'],note:'Shrapnel na více body parts. Sustained.',slots:{weaponHint:'MG4 – Conflicting Memories',armorHint:'Lonewolf / 4 Treacherous',modHint:'Shrapnel / Violent',devHint:'Butterfly Emissary'}},
  {id:'bow_burden',name:'Compound Bow (Bounce)',src:'Anestic · S AoE',tags:['bow','bounce','aoe'],note:'Burden of Betrayal — silný AoE clear.',slots:{weaponHint:'Compound Bow – Burden of Betrayal',armorHint:'Lonewolf / Falcon + Glide Pants',modHint:'Bounce / Crit',devHint:'Voodoo Doll'}}
];
/* v18 ModuleHost — AdaptiveShell + pack channel + tile map + shared components */
const MODULES=[
  {id:'home',route:'/',offline:true,phone:'stack',tablet:'grid2',desktop:'widgets'},
  {id:'ai',route:'/ai',offline:true,phone:'chat-full',tablet:'chat+cite',desktop:'chat+cite+entity'},
  {id:'search',route:'/search',offline:true,phone:'list',tablet:'list+preview',desktop:'palette+inspector'},
  {id:'db',route:'/db',offline:true,phone:'cards',tablet:'list|detail',desktop:'table+inspector'},
  {id:'map',route:'/map',offline:true,phone:'fullbleed+sheet',tablet:'map+rail',desktop:'layers|map|inspector'},
  {id:'craft',route:'/craft',offline:true,phone:'wizard',tablet:'tree|list',desktop:'tree+checklist'},
  {id:'builds',route:'/builds',offline:true,phone:'slots-stack',tablet:'slots|stats',desktop:'canvas+stats'},
  {id:'scenarios',route:'/scenarios',offline:true,phone:'timeline',tablet:'phase|detail',desktop:'timeline+map'},
  {id:'progress',route:'/progress',offline:true,phone:'checklists',tablet:'cats|list',desktop:'cats+export'},
  {id:'herbalist',route:'/herbalist',offline:true,phone:'list',tablet:'plants|recipes',desktop:'table+filters'},
  {id:'grafting',route:'/grafting',offline:true,phone:'two-select',tablet:'parents|result',desktop:'matrix'},
  {id:'animalsys',route:'/animals',offline:true,phone:'cards',tablet:'list|habitat',desktop:'workspace'},
  {id:'events',route:'/events',offline:true,phone:'cards',tablet:'list|detail',desktop:'calendar+inspector'},
  {id:'favorites',route:'/favorites',offline:true,phone:'list',tablet:'list|detail',desktop:'collection'},
  {id:'inventory',route:'/inventory',offline:true,phone:'qty-list',tablet:'list|detail',desktop:'table'},
  {id:'offline',route:'/offline',offline:true,phone:'status',tablet:'status',desktop:'status+queue'},
  {id:'agent',route:'/agent',offline:true,phone:'queue',tablet:'queue|item',desktop:'queue+diff'},
  {id:'settings',route:'/settings',offline:true,phone:'form',tablet:'form',desktop:'form+sync'}
];
window.OHG={version:'19.0',modules:MODULES,nav:NAV,shell:'AdaptiveShell',host:'ModuleHost',sw:'ohg_sw.js',packChannel:'local+sw+remote'};

let DATA=window.OHG_DATA||{};
let META=window.OHG_META||{entities:0,version:'local'};
let route='home', selected=null, device='phone';
let lock=localStorage.getItem('ohg_lock')||'auto';
let filterQ='', mapLayer='all';
let user=JSON.parse(localStorage.getItem('ohg_user')||'{"fav":[],"inv":[],"progress":{},"builds":[],"notes":{},"queue":[],"offline":true}');
['fav','inv','builds','queue'].forEach(k=>{ if(!Array.isArray(user[k])) user[k]=[]; });
if(!user.progress) user.progress={};
if(!user.notes) user.notes={};
if(user.offline==null) user.offline=true;
function saveUser(){ localStorage.setItem('ohg_user', JSON.stringify(user)); }

function classOf(w){ if(w<=679) return 'phone'; if(w<=1100) return 'tablet'; if(w<=1599) return 'desktop'; return 'ultrawide'; }
function applyDevice(){
  const w=lock==='auto'?innerWidth:({phone:390,tablet:820,desktop:1280,ultrawide:1800}[lock]||innerWidth);
  device=classOf(w);
  document.getElementById('app').className='app '+device+(selected&&device==='tablet'?' ctx-open':'');
  document.getElementById('devBadge').textContent=device.toUpperCase();
  document.getElementById('lockBtn').textContent=lock==='auto'?'AUTO':lock;
  renderNav();
}
function toast(m){ const t=document.getElementById('toast'); t.textContent=m; t.style.display='block'; setTimeout(()=>t.style.display='none',1800); }
function allEntities(){
  const out=[];
  Object.keys(DATA).forEach(k=>(DATA[k]||[]).forEach(e=>out.push({...e,_cat:k})));
  return out;
}
function catList(key,extra){
  let arr=[...(DATA[key]||[])].map(e=>({...e,_cat:key}));
  if(extra) arr=arr.concat((DATA[extra]||[]).map(e=>({...e,_cat:extra})));
  return arr;
}
function search(q){
  q=(q||'').toLowerCase().trim();
  const pool=allEntities();
  if(!q) return pool.slice(0,50);
  return pool.filter(e=>[e.name,e.type,e.desc,e.region,e.location,e.rarity,e.slot,(e.tags||[]).join(' ')].join(' ').toLowerCase().includes(q)).slice(0,80);
}
function renderNav(){
  const sb=document.getElementById('sidebar');
  sb.innerHTML=NAV.map(g=>`<div class="navg">${g.g}</div>`+g.items.map(i=>`
    <button class="navi ${route===i.id?'active':''}" data-r="${i.id}"><span class="ic">${i.ic==='sl'?'⚙':i.ic}</span><span class="lbl">${i.label}</span></button>`).join('')).join('');
  sb.querySelectorAll('[data-r]').forEach(b=>b.onclick=()=>go(b.dataset.r));
}
function go(r,entity){
  if(r==='more'){ openMore(); return; }
  route=r; selected=entity||null; filterQ='';
  try{ history.replaceState(null,'','#'+r+(entity&&entity.id?('/'+entity.id):'')); }catch(e){}
  applyDevice();
  document.querySelectorAll('#bn [data-r]').forEach(b=>{
    const primary=['home','search','map','db'];
    b.classList.toggle('active', primary.includes(r)?b.dataset.r===r:b.dataset.r==='more');
  });
  render();
}
function openMore(){
  document.getElementById('ov').classList.add('on');
  const sh=document.getElementById('sheet'); sh.className='sheet on';
  const flat=NAV.flatMap(g=>g.items).filter(i=>PHONE_MORE.includes(i.id));
  sh.innerHTML=`<div class="kicker">More</div><h2>Moduly</h2><div class="grid g2">`+
    flat.map(i=>`<button class="card" onclick="closeSheet();go('${i.id}')"><b>${i.label}</b></button>`).join('')+`</div>`;
}
function closeSheet(){ document.getElementById('sheet').classList.remove('on'); document.getElementById('ov').classList.remove('on'); }
document.getElementById('ov').onclick=()=>{ closeSheet(); document.getElementById('cmd').classList.remove('on'); };
function setCtx(html){ document.querySelector('#ctx .body').innerHTML=html||'<span class="muted">Vyber entitu.</span>'; }
function openEntity(e){
  selected=e;
  const html=entityDetail(e);
  if(device==='phone'){
    document.getElementById('ov').classList.add('on');
    const sh=document.getElementById('sheet'); sh.className='sheet on'; sh.innerHTML=html;
  } else {
    setCtx(html);
    if(device==='tablet') applyDevice();
  }
}
function pretty(v){
  if(v==null) return '';
  if(Array.isArray(v)) return v.map(x=>typeof x==='object'?JSON.stringify(x):x).join(', ');
  if(typeof v==='object') return JSON.stringify(v);
  return String(v);
}
function entityDetail(e){
  if(!e) return '';
  const fav=user.fav.includes(e.id);
  const inv=user.inv.find(x=>x.id===e.id);
  const keys=Object.keys(e).filter(k=>!['id','name','_cat'].includes(k)&&e[k]!=null&&e[k]!=='');
  return `<div class="kicker">${e._cat||''}</div><h2 style="margin:4px 0 8px">${e.name||e.id}</h2>
    <div class="row" style="margin-bottom:10px">
      <button class="btn ${fav?'':'ghost'}" onclick="toggleFav('${e.id}')">${fav?'★ Favorite':'☆ Favorite'}</button>
      <button class="btn ghost" onclick="addInv('${e.id}')">${inv?'V inventáři +1':'Do inventáře'}</button>
    </div>
    ${keys.map(k=>`<div style="margin:6px 0"><span class="muted">${k}</span><div>${pretty(e[k])}</div></div>`).join('')}
    <textarea id="note_${e.id}" placeholder="Poznámka…" style="width:100%;margin-top:8px;min-height:70px">${user.notes[e.id]||''}</textarea>
    <button class="btn ghost" style="margin-top:6px" onclick="saveNote('${e.id}')">Uložit poznámku</button>`;
}
function toggleFav(id){
  const i=user.fav.indexOf(id);
  if(i>=0) user.fav.splice(i,1); else user.fav.push(id);
  saveUser(); toast('Favorites uloženy'); openEntity(allEntities().find(e=>String(e.id)===String(id)));
}
function addInv(id){
  const hit=user.inv.find(x=>x.id===id);
  if(hit) hit.qty=(hit.qty||1)+1; else user.inv.push({id,qty:1});
  saveUser(); toast('Inventář +1');
}
function saveNote(id){ const el=document.getElementById('note_'+id); if(el){ user.notes[id]=el.value; saveUser(); toast('Poznámka uložena'); } }

function itemRow(e){
  return `<button class="item ${selected&&selected.id===e.id?'sel':''}" onclick='openEntity(${JSON.stringify(e).replace(/'/g,"&#39;")})'>
    <div><b>${e.name||e.id}</b><div class="muted">${e._cat||''} · ${e.type||e.rarity||e.region||''}</div></div>
    <span class="chip">${e.rarity||e.slot||e.phase||'·'}</span></button>`;
}
function listPane(arr){
  const q=filterQ.toLowerCase();
  const f=q?arr.filter(e=>(e.name||'').toLowerCase().includes(q)):arr;
  return `<div class="filters"><input placeholder="Filtrovat…" value="${filterQ.replace(/"/g,'&quot;')}" oninput="filterQ=this.value;render()"/></div>
    <div class="muted" style="margin-bottom:8px">${f.length} záznamů</div>
    <div class="list">${f.map(itemRow).join('')||'<div class="muted">Nic.</div>'}</div>`;
}
function fillList(arr){
  const col=document.getElementById('listCol');
  if(device==='ultrawide'||device==='desktop'){ col.innerHTML=listPane(arr); }
  else col.innerHTML='';
}

function viewHome(){
  const ev=DATA.events||[];
  const sc=DATA.scenarios||[];
  const n=META.entities||allEntities().length;
  const done=Object.values(user.progress).filter(Boolean).length;
  const bp=typeof calcBuild==='function'?calcBuild():{power:0,filled:0};
  return `<div class="kicker">Dashboard</div><h1>Once Human Guide</h1>
    <p class="sub">App 18.0 · ModuleHost · ${META.version||'pack'} · Patch ${META.patch||'3.0.7'} · ${n} entit · ${MODULES.length} modulů · AdaptiveShell ${device}</p>
    <div class="grid g4">
      <div class="card"><div class="kicker">Databáze</div><div class="stat">${n}</div><div class="muted">lokální pack</div></div>
      <div class="card"><div class="kicker">Build Power</div><div class="stat">${bp.power||'—'}</div><div class="muted">${bp.filled||0}/5 slotů</div></div>
      <div class="card"><div class="kicker">Favorites</div><div class="stat">${user.fav.length}</div></div>
      <div class="card"><div class="kicker">Progress</div><div class="stat">${done}</div></div>
    </div>
    <div class="grid g2" style="margin-top:12px">
      <div class="card"><div class="kicker">Scénáře</div>${sc.slice(0,4).map(s=>`<div class="item" style="margin-top:8px" onclick="go('scenarios')"><b>${s.name}</b><span class="chip">${s.phase||s.type||''}</span></div>`).join('')}</div>
      <div class="card"><div class="kicker">Eventy</div>${ev.map(s=>`<div class="item" style="margin-top:8px" onclick="go('events')"><b>${s.name}</b><span class="chip">${s.status||s.timer||''}</span></div>`).join('')||'<p class="muted">Žádné eventy</p>'}</div>
    </div>
    <div class="row" style="margin-top:14px">
      <button class="btn" onclick="go('ai')">AI Guide</button>
      <button class="btn ghost" onclick="go('map')">Mapa</button>
      <button class="btn ghost" onclick="go('db')">Databáze</button>
      <button class="btn ghost" onclick="go('craft')">Crafting</button>
    </div>`;
}
function viewSearch(){
  const res=search(filterQ);
  fillList(res);
  return `<div class="kicker">Search</div><h1>Globální vyhledávání</h1>
    <div class="filters"><input style="flex:1;min-width:200px" placeholder="Zbraň, deviation, lokace…" value="${filterQ}" oninput="filterQ=this.value;render()"/></div>
    <div class="list">${res.map(itemRow).join('')||'<div class="muted">Nic nenalezeno.</div>'}</div>`;
}
function viewAI(){
  const hits=search(filterQ).slice(0,8);
  return `<div class="kicker">AI Guide</div><h1>Lokální retrieval</h1>
    <p class="sub">AI nemění databázi. Odpovědi jdou z lokálního packu; návrhy jdou do Agent queue.</p>
    <div class="filters">
      <input style="flex:1;min-width:220px" id="aip" placeholder="Např. best PVE deviation, silo Theta drops…" value="${filterQ}" oninput="filterQ=this.value"/>
      <button class="btn" onclick="filterQ=document.getElementById('aip').value;render()">Zeptat se</button>
    </div>
    ${filterQ?`<div class="card"><b>Retrieval</b><p class="muted">Dotaz „${filterQ}“ — ${hits.length} zásahů v lokální DB (${user.offline?'OFFLINE':'ONLINE'}).</p>
      <div class="list">${hits.map(itemRow).join('')}</div>
      <button class="btn ghost" style="margin-top:10px" onclick="queueProposal('${filterQ.replace(/'/g,"\\'")}')">Poslat do Agent queue</button>
    </div>`:`<div class="card muted">Zadej dotaz. Pipeline: intent → local DB → source badge → entity chips.</div>`}`;
}
function queueProposal(q){
  user.queue.push({q,at:new Date().toISOString(),status:'pending'});
  saveUser(); toast('Návrh ve frontě'); go('agent');
}
function viewDB(){
  return `<div class="kicker">Database</div><h1>Kategorie</h1>
    <div class="grid g3">${Object.entries(DB_CATS).map(([id,c])=>{
      const n=catList(c.key,c.extra).length;
      return `<button class="card" onclick="go('${id}')"><div class="kicker">${id}</div><b>${c.title}</b><div class="muted">${n} záznamů</div></button>`;
    }).join('')}</div>`;
}
function viewCat(id){
  const c=DB_CATS[id]; if(!c) return viewDB();
  const arr=catList(c.key,c.extra);
  fillList(arr);
  return `<div class="kicker">Database</div><h1>${c.title}</h1>${device==='ultrawide'||device==='desktop'?'<p class="sub">Seznam v levém sloupci, detail v kontextu.</p>':listPane(arr)}`;
}
const MAP_LAYERS=['all','settlement','poi','silo','monolith','resource','event'];
function locLayer(l){
  const t=(l.type||l.kind||l.region||'poi').toLowerCase();
  if(/silo/.test(t+' '+(l.name||''))) return 'silo';
  if(/mono/.test(t+' '+(l.name||''))) return 'monolith';
  if(/town|settle|base|camp/.test(t+' '+(l.name||''))) return 'settlement';
  if(/ore|wood|resour|mine/.test(t+' '+(l.tags||[]).join(' '))) return 'resource';
  if(/event|rift|tide/.test(t)) return 'event';
  return l.type||'poi';
}
function viewMap(){
  const locs=(DATA.locations||[]).map(l=>({...l,_layer:locLayer(l),_cat:'locations'}));
  const layers=[...new Set(['all',...locs.map(l=>l._layer)])];
  const shown=mapLayer==='all'?locs:locs.filter(l=>l._layer===mapLayer);
  fillList(shown);
  return `<div class="kicker">Map · vrstvy</div><h1>Interaktivní mapa</h1>
    <p class="sub">${shown.length} bodů · vrstva <b>${mapLayer}</b> · telefon = sheet, PC = inspector</p>
    <div class="filters">
      ${layers.map(l=>`<button class="btn ${mapLayer===l?'':'ghost'}" onclick="mapLayer='${l}';render()">${l}</button>`).join('')}
    </div>
    <div class="mapbox">${shown.map(l=>{
      const x=Math.max(6,Math.min(94,Number(l.x)||((String(l.id||l.name).length*17)%88+6)));
      const y=Math.max(8,Math.min(92,Number(l.y)||((String(l.name||'').length*13)%80+10)));
      return `<span class="pin" style="left:${x}%;top:${y}%" title="${l.name}" onclick='openEntity(${JSON.stringify(l).replace(/'/g,"&#39;")})'>📍</span>`;
    }).join('')}</div>
    ${device==='desktop'||device==='ultrawide'?'':`<div class="list" style="margin-top:12px">${shown.slice(0,24).map(itemRow).join('')}</div>`}`;
}
function viewCraft(){
  const rec=DATA.recipes||[];
  fillList(rec.map(e=>({...e,_cat:'recipes'})));
  return `<div class="kicker">Crafting</div><h1>Recepty</h1>
    <p class="sub">Strom surovin → stanice → výstup. Položky lze poslat do inventáře.</p>
    ${listPane(rec.map(e=>({...e,_cat:'recipes'})))}`;
}
/* ── Build multiplier (Doomeris + Anestic) ──
   Stejný bucket = aditivní; různé buckety = multiplikativní product (1+pct/100). */
function emptyBuckets(){ return {weapon:0,elemental:0,status:0,critDmg:0,weakspot:0,vuln:0,attack:0,enemy:0}; }
function addBucket(b,key,pct){ if(pct) b[key]=(b[key]||0)+pct; }
function contributeEntity(buckets,e,role){
  if(!e) return;
  const tags=(e.tags||[]).map(t=>String(t).toLowerCase());
  const desc=(e.desc||'')+' '+(e.name||'');
  const rare=e.rarity||'';
  const rarePct={Legendary:18,Epic:12,Rare:7,Uncommon:4,Common:2}[rare]||3;
  if(role==='weapon') addBucket(buckets,'weapon',rarePct*0.6), addBucket(buckets,'attack',rarePct*0.25);
  else if(role==='armor') addBucket(buckets,'weapon',rarePct*0.35);
  else if(role==='mod') addBucket(buckets,'weapon',rarePct*0.25);
  else if(role==='dev') addBucket(buckets,'attack',rarePct*0.3);
  if(tags.includes('shrapnel')||tags.includes('dps')) addBucket(buckets,'weapon',8);
  if(tags.includes('crit')||/crit/i.test(desc)) addBucket(buckets,'critDmg',10);
  if(tags.includes('s-tier')) addBucket(buckets,'weapon',6), addBucket(buckets,'critDmg',4);
  if(tags.includes('blaze')||tags.includes('burn')||/burn|blaze|pyro/i.test(desc)){ addBucket(buckets,'elemental',10); addBucket(buckets,'status',8); }
  if(tags.includes('shock')||tags.includes('surge')||/power surge|shock|elect/i.test(desc)){ addBucket(buckets,'elemental',12); addBucket(buckets,'status',6); }
  if(tags.includes('frost')||/frost|vortex|ice/i.test(desc)){ addBucket(buckets,'elemental',10); addBucket(buckets,'status',10); }
  if(tags.includes('weakspot')||/weakspot|weak spot|bullseye|bingo/i.test(desc)) addBucket(buckets,'weakspot',12);
  if(/bullseye|vulnerability|marked/i.test(desc)) addBucket(buckets,'vuln',8);
  if(tags.includes('endgame')) addBucket(buckets,'weapon',5), addBucket(buckets,'enemy',4);
  if(/lonewolf|falcon/i.test(desc)||tags.includes('crit')) addBucket(buckets,'critDmg',6);
  if(/treacherous|low hp|low-hp/i.test(desc)) addBucket(buckets,'weapon',15), addBucket(buckets,'status',10);
  if(/shelterer|deviant energy/i.test(desc)) addBucket(buckets,'elemental',12);
  if(/renegade|archer/i.test(desc)) addBucket(buckets,'weakspot',10);
  if(/status/i.test(desc)&&role!=='weapon') addBucket(buckets,'status',6);
  if(/elemental overload|elemental/i.test(desc)) addBucket(buckets,'elemental',8);
  (desc.match(/(\d+(?:\.\d+)?)\s*%/g)||[]).forEach(p=>{
    const v=parseFloat(p);
    if(v>=3&&v<=60){
      if(/crit/i.test(desc)) addBucket(buckets,'critDmg',v*0.4);
      else if(/weak/i.test(desc)) addBucket(buckets,'weakspot',v*0.4);
      else if(/weapon|attack/i.test(desc)) addBucket(buckets,'weapon',v*0.35);
      else if(/element|blaze|frost|shock/i.test(desc)) addBucket(buckets,'elemental',v*0.35);
      else if(/status|burn|surge/i.test(desc)) addBucket(buckets,'status',v*0.35);
      else addBucket(buckets,'weapon',v*0.2);
    }
  });
  if(role==='armor'&&(e.pieces||0)>=4){
    addBucket(buckets,'weapon',8);
    if(tags.includes('crit')||/lonewolf|falcon/i.test(desc)) addBucket(buckets,'critDmg',8);
    if(/shelterer/i.test(desc)) addBucket(buckets,'elemental',15);
    if(/treacherous/i.test(desc)) addBucket(buckets,'weapon',20), addBucket(buckets,'status',12);
  }
}
function productMult(buckets){ let m=1; BUCKETS.forEach(k=>{ m*=(1+(buckets[k]||0)/100); }); return m; }
function calcBuild(build){
  const b=build||user.currentBuild||{};
  const get=id=>allEntities().find(x=>String(x.id)===String(id));
  const w1=get(b.weapon1), w2=get(b.weapon2), ar=get(b.armor), mo=get(b.mod), dv=get(b.deviation);
  const buckets=emptyBuckets();
  contributeEntity(buckets,w1,'weapon');
  if(w2){ const tmp=emptyBuckets(); contributeEntity(tmp,w2,'weapon'); BUCKETS.forEach(k=>addBucket(buckets,k,(tmp[k]||0)*0.45)); }
  contributeEntity(buckets,ar,'armor');
  contributeEntity(buckets,mo,'mod');
  contributeEntity(buckets,dv,'dev');
  if(w1&&mo){
    const wt=(w1.tags||[]).concat((w1.desc||'').toLowerCase());
    const mt=(mo.tags||[]).concat((mo.desc||'').toLowerCase());
    if(wt.some(t=>/shrapnel|crit/.test(t))&&mt.some(t=>/crit|violent|deadshot/.test(t))) addBucket(buckets,'critDmg',8);
    if(wt.some(t=>/bullseye|shotgun|doom/.test(t))&&mt.some(t=>/vulnerab|bullseye/.test(t))) addBucket(buckets,'vuln',8);
    if(wt.some(t=>/blaze|burn|shock|frost|surge/.test(t))&&mt.some(t=>/element|status|blaze|surge/.test(t))){ addBucket(buckets,'elemental',6); addBucket(buckets,'status',6); }
  }
  if(w1&&ar&&w1.style&&ar.style&&w1.style===ar.style&&w1.style!=='—') addBucket(buckets,'weapon',6);
  const mult=productMult(buckets);
  const power=Math.round(mult*22);
  const filled=[w1,w2,ar,mo,dv].filter(Boolean).length;
  const vals=[buckets.elemental||0,buckets.status||0,buckets.weakspot||0].filter(v=>v>0);
  let balance='—';
  if(vals.length>=2){ const spread=Math.max(...vals)-Math.min(...vals); balance=spread<12?'vyvážené':'nestejnoměrné (Anestic: srovnej)'; }
  return {power,filled,mult,buckets,balance,entities:{w1,w2,ar,mo,dv}};
}
function entityScore(e){
  if(!e) return 0;
  const b=emptyBuckets();
  const role=e._cat==='weapons'?'weapon':e._cat==='armor'?'armor':e._cat==='mods'?'mod':'dev';
  contributeEntity(b,e,role);
  return productMult(b);
}
function viewBuilds(){
  if(!user.currentBuild) user.currentBuild={};
  const sc=calcBuild();
  const bk=sc.buckets||{};
  const bucketRows=[['Weapon DMG',bk.weapon],['Elemental',bk.elemental],['Status',bk.status],['Crit DMG',bk.critDmg],['Weakspot',bk.weakspot],['Vulnerability',bk.vuln],['Attack',bk.attack],['Enemy type',bk.enemy]].filter(([,v])=>v>0.5);
  const slotsHtml=BUILD_SLOTS.map(s=>{
    const id=user.currentBuild[s.id];
    const e=id?allEntities().find(x=>String(x.id)===String(id)):null;
    return `<div class="slot ${e?'filled':''}"><div><div class="kicker">${s.label}</div><b>${e?e.name:'Prázdný slot'}</b>${e?`<div class="muted">${e.rarity||''} · ×${entityScore(e).toFixed(2)}</div>`:''}</div>
      <div class="row">${e?`<button class="btn ghost" onclick="clearSlot('${s.id}')">×</button>`:''}<button class="btn" onclick="pickSlot('${s.id}')">${e?'Změnit':'Vybrat'}</button></div></div>`;
  }).join('');
  const metaFilter=window._metaFilter||'all';
  const metaTags=['all','shrapnel','bullseye','unstable-bomber','blaze','frost','shock','aoe','smg','sniper'];
  const filteredMeta=metaFilter==='all'?META_PRESETS:META_PRESETS.filter(p=>(p.tags||[]).includes(metaFilter));
  const metaHtml=`<div class="row" style="margin-bottom:10px">${metaTags.map(t=>`<button class="chip ${metaFilter===t?'acc':''}" style="cursor:pointer" onclick="window._metaFilter='${t}';render()">${t}</button>`).join('')}</div>
    ${filteredMeta.map(p=>`<div class="card" style="margin-bottom:8px"><div class="kicker">${p.src}</div><b>${p.name}</b>
      <p class="muted" style="margin:6px 0;font-size:12px">${p.note}</p>
      <div class="tagrow">${(p.tags||[]).map(t=>`<span class="chip">${t}</span>`).join('')}</div>
      <div class="muted" style="margin-top:6px;font-size:11px">Zbraň: ${p.slots.weaponHint} · Zbroj: ${p.slots.armorHint}<br>Mod: ${p.slots.modHint} · Dev: ${p.slots.devHint}</div></div>`).join('')||'<p class="muted">Žádná šablona.</p>'}`;
  return `<div class="kicker">Build Planner</div><h1>Loadout</h1>
    <p class="sub">Model Doomeris + Anestic · multiplikativní buckety · AdaptiveShell ${device}</p>
    <div class="score-box">
      <div class="card"><div class="kicker">Build Power</div><div class="stat">${sc.power}</div>
        <div class="progress"><i style="width:${Math.min(100,sc.power)}%"></i></div>
        <div class="muted" style="margin-top:4px">×${(sc.mult||1).toFixed(2)} celkový mult</div></div>
      <div class="card"><div class="kicker">Zaplněno</div><div class="stat">${sc.filled}/5</div><div class="muted">${sc.balance||''}</div></div>
    </div>
    ${bucketRows.length?`<div class="card" style="margin-bottom:12px"><div class="kicker">Buckety (sčítají se uvnitř, násobí se mezi sebou)</div>
      ${bucketRows.map(([n,v])=>`<div class="row" style="justify-content:space-between;margin-top:4px"><span class="muted">${n}</span><b>+${v.toFixed(0)}%</b></div>`).join('')}</div>`:''}
    <div class="grid g2" style="margin-bottom:12px">${slotsHtml}</div>
    <div class="row" style="margin-bottom:14px">
      <button class="btn" onclick="saveBuild()">Uložit build</button>
      <button class="btn ghost" onclick="user.currentBuild={};saveUser();render()">Reset</button>
    </div>
    <div class="kicker">Meta šablony (Doomeris / Anestic)</div>
    <div style="margin-top:8px">${metaHtml}</div>
    <div class="kicker" style="margin-top:14px">Uložené</div>
    <div class="list" style="margin-top:8px">
      ${(user.builds||[]).map((b,i)=>{ const p=calcBuild(b.slots).power;
        return `<div class="item"><div><b>${b.name}</b><div class="muted">Power ${p}</div></div>
          <div class="row"><button class="btn ghost" onclick="loadBuild(${i})">Načíst</button>
          <button class="btn danger" onclick="delBuild(${i})">Smazat</button></div></div>`;
      }).join('')||'<p class="muted">Žádný uložený build.</p>'}
    </div>
    <details style="margin-top:16px" class="muted"><summary style="cursor:pointer;color:var(--acc)">Logika Doomeris / Anestic</summary>
      <p style="font-size:12px;margin-top:8px;line-height:1.55">Fyzický / Shrapnel / Bullseye: Base × (1+Weapon%) × (1+Attack%) × (1+CritDMG%) × (1+Weakspot%) × (1+Vuln%) × (1+Enemy%)<br>
      Element / Status / Burn / Surge / Frost: (PSI × keyword%) × (1+Elemental%) × (1+Status%) × (1+Burn/Surge%) × (1+Enemy%)<br>
      Stejný bucket = aditivní. Různé buckety = multiplikativní. Anestic: vyvažuj Status ≈ Weakspot ≈ Elemental.</p></details>`;
}
function pickSlot(slot){
  const def=BUILD_SLOTS.find(s=>s.id===slot);
  const cat=(def&&def.cats&&def.cats[0])||'weapons';
  const pool=DATA[cat]||[];
  const html=`<div class="kicker">${def?def.label:slot}</div><h2>Vyber</h2><div class="list">${pool.map(e=>
    `<button class="item" onclick='user.currentBuild["${slot}"]="${e.id}";saveUser();closeSheet();render()'><b>${e.name}</b><span class="chip">${e.rarity||e.type||''}</span></button>`).join('')}</div>`;
  if(device==='phone'){ document.getElementById('ov').classList.add('on'); const sh=document.getElementById('sheet'); sh.className='sheet on'; sh.innerHTML=html; }
  else setCtx(html);
}
function clearSlot(s){ delete user.currentBuild[s]; saveUser(); render(); }
function saveBuild(){ if(!user.builds) user.builds=[]; user.builds.push({name:'Build '+(user.builds.length+1),slots:{...user.currentBuild}}); saveUser(); toast('Build uložen'); render(); }
function loadBuild(i){ const b=user.builds[i]; if(b){ user.currentBuild={...(b.slots||{})}; saveUser(); toast('Build načten'); render(); } }
function delBuild(i){ user.builds.splice(i,1); saveUser(); render(); }

function viewScenarios(){
  const arr=(DATA.scenarios||[]).map(e=>({...e,_cat:'scenarios'}));
  fillList(arr);
  return `<div class="kicker">Scenarios</div><h1>Průvodce scénáři</h1>${listPane(arr)}`;
}
function viewProgress(){
  const groups={scenarios:DATA.scenarios,deviations:DATA.deviations,locations:DATA.locations,bosses:DATA.bosses,recipes:DATA.recipes};
  let html=`<div class="kicker">Progress</div><h1>Tracker</h1>`;
  Object.entries(groups).forEach(([k,arr])=>{
    const a=arr||[];
    const done=a.filter(e=>user.progress[k+':'+e.id]).length;
    html+=`<div class="card" style="margin-bottom:10px"><div class="row" style="justify-content:space-between"><b>${k}</b><span class="muted">${done}/${a.length}</span></div>
      <div class="progress" style="margin:8px 0"><i style="width:${a.length?done/a.length*100:0}%"></i></div>
      ${a.slice(0,12).map(e=>`<label class="row" style="margin:4px 0"><input type="checkbox" ${user.progress[k+':'+e.id]?'checked':''} onchange="user.progress['${k}:${e.id}']=this.checked;saveUser();render()"/> ${e.name}</label>`).join('')}</div>`;
  });
  html+=`<button class="btn ghost" onclick="downloadProgress()">Export JSON</button>`;
  return html;
}
function downloadProgress(){
  const blob=new Blob([JSON.stringify(user,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='ohg_user.json'; a.click();
}
function viewHerbalist(){
  const rec=(DATA.recipes||[]).filter(r=>/cook|food|herb|buff|meal|drink/i.test([r.type,r.name,r.effect,r.station].join(' ')));
  const plants=DATA.plants||[];
  return `<div class="kicker">Herbalist</div><h1>Vaření a byliny</h1>
    <div class="grid g2">
      <div class="card"><b>Rostliny</b>${plants.map(p=>itemRow({...p,_cat:'plants'})).join('')}</div>
      <div class="card"><b>Recepty</b>${(rec.length?rec:DATA.recipes||[]).map(p=>itemRow({...p,_cat:'recipes'})).join('')}</div>
    </div>`;
}
function viewGrafting(){
  const fl=DATA.flowers||[];
  return `<div class="kicker">Grafting</div><h1>Křížení květin</h1>
    <div class="grid g2">
      <div><label class="muted">Parent A</label><select id="ga" onchange="graftResult()">${fl.map(f=>`<option value="${f.id}">${f.name}</option>`).join('')}</select></div>
      <div><label class="muted">Parent B</label><select id="gb" onchange="graftResult()">${fl.map(f=>`<option value="${f.id}">${f.name}</option>`).join('')}</select></div>
    </div>
    <div class="card" id="gres" style="margin-top:12px">Vyber dva rodiče.</div>
    <div class="list" style="margin-top:12px">${fl.map(f=>itemRow({...f,_cat:'flowers'})).join('')}</div>`;
}
function graftResult(){
  const a=(DATA.flowers||[]).find(f=>f.id===document.getElementById('ga').value);
  const b=(DATA.flowers||[]).find(f=>f.id===document.getElementById('gb').value);
  const box=document.getElementById('gres'); if(!box||!a||!b) return;
  box.innerHTML=`<b>${a.name} × ${b.name}</b><p>${a.result||a.genetics||'Kombinace v experimentálním módu.'}</p><p class="muted">${b.mutations||b.desc||''}</p>`;
}
function viewAnimals(){
  const arr=(DATA.animals||[]).map(e=>({...e,_cat:'animals'}));
  return `<div class="kicker">Animal system</div><h1>Zvířata</h1>
    <p class="sub">Habitat, taming, produkty. Napojení na mapu a inventář.</p>${listPane(arr)}`;
}
function viewEvents(){
  const arr=(DATA.events||[]).map(e=>({...e,_cat:'events'}));
  return `<div class="kicker">Events</div><h1>Aktivity</h1>${listPane(arr)}`;
}
function viewFavorites(){
  const arr=user.fav.map(id=>allEntities().find(e=>String(e.id)===String(id))).filter(Boolean);
  return `<div class="kicker">Favorites</div><h1>Kolekce</h1>${listPane(arr)}`;
}
function viewInventory(){
  const rows=user.inv.map(x=>{
    const e=allEntities().find(i=>String(i.id)===String(x.id));
    return `<div class="item"><div><b>${e?e.name:x.id}</b><div class="muted">${e?e._cat:''}</div></div>
      <div class="row"><button class="btn ghost" onclick="chgInv('${x.id}',-1)">−</button><span>${x.qty||1}</span>
      <button class="btn ghost" onclick="chgInv('${x.id}',1)">+</button></div></div>`;
  }).join('')||'<p class="muted">Prázdný inventář. Přidej entitu z detailu.</p>';
  return `<div class="kicker">Inventory</div><h1>Osobní inventář</h1>${rows}`;
}
function chgInv(id,d){
  const hit=user.inv.find(x=>x.id===id); if(!hit) return;
  hit.qty=(hit.qty||1)+d; if(hit.qty<=0) user.inv=user.inv.filter(x=>x.id!==id);
  saveUser(); render();
}
function viewAgent(){
  return `<div class="kicker">AI Agent</div><h1>Review queue</h1>
    <p class="sub">Návrhy na aktualizaci DB. Agent nemění produkční data bez schválení.</p>
    ${(user.queue||[]).map((q,i)=>`<div class="card" style="margin-bottom:8px"><b>${q.q}</b><div class="muted">${q.at} · ${q.status}</div>
      <div class="row" style="margin-top:8px">
        <button class="btn" onclick="user.queue[${i}].status='approved';saveUser();render()">Schválit</button>
        <button class="btn danger" onclick="user.queue.splice(${i},1);saveUser();render()">Zahodit</button>
      </div></div>`).join('')||'<p class="muted">Fronta prázdná. Pošli návrh z AI Guide.</p>'}`;
}
function viewSettings(){
  return `<div class="kicker">Settings</div><h1>Nastavení a sync</h1>
    <div class="card">
      <p>Layout lock</p>
      <div class="row">${['auto','phone','tablet','desktop','ultrawide'].map(x=>`<button class="btn ${lock===x?'':'ghost'}" onclick="lock='${x}';localStorage.setItem('ohg_lock',lock);applyDevice();render()">${x}</button>`).join('')}</div>
    </div>
    <div class="card" style="margin-top:10px">
      <p>Offline režim: <b>${user.offline?'ON':'OFF'}</b></p>
      <button class="btn ghost" onclick="user.offline=!user.offline;saveUser();render()">Přepnout</button>
    </div>
    <div class="card" style="margin-top:10px">
      <button class="btn ghost" onclick="downloadProgress()">Export user layer</button>
      <label class="btn ghost">Import JSON<input type="file" accept="application/json" style="display:none" onchange="importUser(this)"/></label>
      <button class="btn danger" onclick="if(confirm('Smazat user layer?')){localStorage.removeItem('ohg_user');location.reload()}">Reset user data</button>
    </div>
    <p class="muted">OHG v18 · pack ${META.version} · ${META.entities} entit · AdaptiveShell phone/tablet/desktop/ultrawide · user layer = localStorage</p>`;
}
function viewOffline(){
  const sw = navigator.serviceWorker && navigator.serviceWorker.controller ? 'ACTIVE' : (window.OHG_SW||'NONE');
  return `<div class="kicker">Offline</div><h1>Cache a synchronizace</h1>
    <div class="card"><div class="kicker">Status</div><b>${user.offline?'OFFLINE FIRST':'ONLINE PREFERRED'}</b>
      <p class="muted">Pack v ohg_data.js (${META.entities} záznamů). User layer = localStorage. Service worker cache = ohg-v18-307. Pack kanál: local first, SW precache, volitelný remote version.json.</p>
      <div class="row"><span class="badge on">LOCAL PACK</span><span class="badge ${sw==='ACTIVE'?'on':''}">SW ${sw}</span></div>
      <div class="row" style="margin-top:10px">
        <button class="btn ghost" onclick="user.offline=!user.offline;saveUser();render()">Přepnout offline flag</button>
        <button class="btn" onclick="registerSW(true)">Registrovat SW</button>
      </div>
    </div>
    <div class="card" style="margin-top:10px"><b>Sync fronta</b><p class="muted">${user.queue.length} agent návrhů čeká na review.</p>
      <button class="btn" onclick="go('agent')">Otevřít Agent</button></div>`;
}

function render(){
  applyDevice();
  const ws=document.getElementById('ws');
  fillList([]);
  const map={
    home:viewHome,search:viewSearch,ai:viewAI,db:viewDB,map:viewMap,craft:viewCraft,builds:viewBuilds,
    scenarios:viewScenarios,progress:viewProgress,herbalist:viewHerbalist,grafting:viewGrafting,
    animalsys:viewAnimals,events:viewEvents,favorites:viewFavorites,inventory:viewInventory,
    agent:viewAgent,settings:viewSettings,offline:viewOffline
  };
  if(DB_CATS[route]) ws.innerHTML=viewCat(route);
  else ws.innerHTML=(map[route]||viewHome)();
  if(route==='grafting') setTimeout(graftResult,0);
  if(selected && device!=='phone') setCtx(entityDetail(selected));
}

document.getElementById('lockBtn').onclick=()=>{
  const order=['auto','phone','tablet','desktop','ultrawide'];
  lock=order[(order.indexOf(lock)+1)%order.length];
  localStorage.setItem('ohg_lock',lock); applyDevice(); render();
};
document.getElementById('q').addEventListener('focus',()=>openCmd());
document.getElementById('q').addEventListener('input',e=>{ filterQ=e.target.value; if(route==='search') render(); });
function openCmd(){
  document.getElementById('cmd').classList.add('on');
  document.getElementById('ov').classList.add('on');
  const inp=document.getElementById('cmdq'); inp.value=document.getElementById('q').value; inp.focus(); drawCmd();
}
function drawCmd(){
  const q=document.getElementById('cmdq').value;
  document.getElementById('cmdres').innerHTML=search(q).slice(0,20).map(e=>
    `<button class="item" onclick='document.getElementById("cmd").classList.remove("on");closeSheet();openEntity(${JSON.stringify(e).replace(/'/g,"&#39;")})'><b>${e.name}</b><span class="chip">${e._cat}</span></button>`
  ).join('')||'<div class="muted" style="padding:12px">Nic.</div>';
}
document.getElementById('cmdq').addEventListener('input',drawCmd);
document.addEventListener('keydown',e=>{
  if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){ e.preventDefault(); openCmd(); }
  if(e.key==='Escape'){ document.getElementById('cmd').classList.remove('on'); closeSheet(); }
});
document.getElementById('bn').addEventListener('click',e=>{
  const b=e.target.closest('[data-r]'); if(b) go(b.dataset.r);
});
window.addEventListener('resize',()=>{ if(lock==='auto'){ applyDevice(); }});
function importUser(inp){
  const f=inp.files&&inp.files[0]; if(!f) return;
  const r=new FileReader();
  r.onload=()=>{
    try{
      const j=JSON.parse(r.result);
      const layer=j.progress&&!j.fav? {fav:user.fav,inv:user.inv,progress:j.progress||j,builds:user.builds,notes:user.notes,queue:user.queue,offline:user.offline}:j;
      user=Object.assign({fav:[],inv:[],progress:{},builds:[],notes:{},queue:[],offline:true},layer);
      ['fav','inv','builds','queue'].forEach(k=>{ if(!Array.isArray(user[k])) user[k]=[]; });
      saveUser(); toast('User layer importován'); render();
    }catch(err){ toast('Neplatný JSON'); }
  };
  r.readAsText(f);
}
function bootHash(){
  const parts=(location.hash||'#home').replace(/^#/,'').split('/');
  const h=parts[0]||'home';
  const known=['home','search','ai','db','map','craft','builds','scenarios','progress','herbalist','grafting','animalsys','events','favorites','inventory','agent','settings','offline'].concat(Object.keys(DB_CATS));
  if(known.includes(h)) route=h;
  if(parts[1]){
    const ent=allEntities().find(e=>String(e.id)===decodeURIComponent(parts[1]));
    if(ent) selected=ent;
  }
}
window.addEventListener('hashchange',()=>{ bootHash(); render(); });
document.getElementById('syncBadge').textContent='PACK '+((META.entities)||'?');
window.OHG_SW='NONE';
function registerSW(force){
  if(!('serviceWorker' in navigator)){ window.OHG_SW='UNSUPPORTED'; toast('SW není v tomto prohlížeči'); return; }
  navigator.serviceWorker.register('ohg_sw.js').then(()=>{
    window.OHG_SW=navigator.serviceWorker.controller?'ACTIVE':'REGISTERED';
    if(force) toast('Service worker '+window.OHG_SW);
  }).catch(()=>{ window.OHG_SW='FAIL'; if(force) toast('SW registrace selhala (potřeba http server)'); });
}
registerSW(false);
bootHash();
applyDevice(); render();
