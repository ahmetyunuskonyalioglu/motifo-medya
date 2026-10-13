// Archicad/Revit OBJ → inşaat sırası. Kullanım: SCENE ve ELEMS hazırken buildFromOBJ(objText, {t0, t1, upAxis:'y'|'z', scale})
// Eleman sınıfı, grup/nesne/malzeme adındaki anahtar kelimelerden çıkarılır; aynı sınıf içinde alttan üste sıralanır.
const CLASSES=[
 {cat:'struct',key:'temel',rx:/(temel|found|footing|raft|radye)/i,color:'#7c7870',mode:'growY'},
 {cat:'struct',key:'kolon',rx:/(kolon|column|perde|shear)/i,color:'#aaa69f',mode:'growY'},
 {cat:'struct',key:'kiris',rx:/(kiri[şs]|beam)/i,color:'#9f9b94',mode:'growY'},
 {cat:'struct',key:'doseme',rx:/(d[öo][şs]eme|slab|floor(?!.*finish)|plak)/i,color:'#aaa69f',mode:'drop'},
 {cat:'struct',key:'merdiven',rx:/(merdiven|stair|ramp)/i,color:'#b3afa8',mode:'growY'},
 {cat:'wall',key:'duvar',rx:/(duvar|wall|bölme|partition)/i,color:'#e6dccd',mode:'growY'},
 {cat:'mep',key:'tesisat',rx:/(pipe|boru|duct|kanal|tesisat|mep|plumb|hvac|cable|kablo|sprink)/i,color:'#2f6fd6',mode:'growY'},
 {cat:'finish',key:'kaplama',rx:/(kaplama|finish|parke|seramik|tile|screed|[şs]ap|covering)/i,color:'#b98a58',mode:'fade'},
 {cat:'facade',key:'dograma',rx:/(window|pencere|door|kap[ıi]|glass|cam|curtain|giydirme|do[ğg]rama)/i,color:'#9ec3dc',mode:'fade',alpha:0.4},
 {cat:'facade',key:'cephe',rx:/(cephe|facade|clad|panel|korkuluk|railing)/i,color:'#9a6a42',mode:'drop'},
 {cat:'roof',key:'cati',rx:/(çat[ıi]|cat[ıi]|roof|mertek|parapet)/i,color:'#4a4c50',mode:'drop'},
 {cat:'site',key:'diger',rx:/.*/,color:'#c9c4bb',mode:'fade'}];
function parseOBJ(txt,opt){
  const up=opt.upAxis||'y', sc=opt.scale||1; const V=[]; const groups=new Map(); let cur='nesne';
  const get=n=>{if(!groups.has(n)) groups.set(n,[]); return groups.get(n)};
  for(const line of txt.split('\n')){
    const p=line.trim().split(/\s+/); if(!p[0]) continue;
    if(p[0]==='v'){ let x=+p[1]*sc,y=+p[2]*sc,z=+p[3]*sc; if(up==='z'){const t=y; y=z; z=-t;} V.push([x,y,z]); }
    else if(p[0]==='o'||p[0]==='g') cur=p.slice(1).join(' ')||cur;
    else if(p[0]==='usemtl') cur=(cur.split('|')[0])+'|'+p.slice(1).join(' ');
    else if(p[0]==='f'){ const idx=p.slice(1).map(s=>{const i=parseInt(s.split('/')[0]); return i<0?V.length+i:i-1;});
      const g=get(cur); for(let k=1;k<idx.length-1;k++) g.push(idx[0],idx[k],idx[k+1]); }
  }
  return {V,groups};
}
function buildFromOBJ(txt,opt){
  const {V,groups}=parseOBJ(txt,opt); const items=[];
  for(const [name,tri] of groups){ if(!tri.length) continue;
    const cls=CLASSES.find(c=>c.rx.test(name)); const pos=[],nrm=[]; let mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9];
    for(let i=0;i<tri.length;i+=3){ const a=V[tri[i]],b=V[tri[i+1]],c=V[tri[i+2]]; if(!a||!b||!c) continue;
      const n=norm(cross(sub(b,a),sub(c,a))); for(const q of [a,b,c]){pos.push(...q);nrm.push(...n); for(let k=0;k<3;k++){mn[k]=Math.min(mn[k],q[k]);mx[k]=Math.max(mx[k],q[k]);}} }
    items.push({name,cls,pos,nrm,mn,mx});
  }
  // sıralama: sınıf sırası, sonra alttan üste
  const order=CLASSES.map(c=>c.key); const FH=opt.floorH||2.9; const y0=Math.min(...items.map(i=>i.mn[1]));
  const fl=it=>{const y=(it.cls.key==='doseme'||it.cls.key==='kiris')? it.mx[1]-FH/2 : it.mn[1]; return Math.floor((y-y0+0.4)/FH);};
  const key=it=>{const o=order.indexOf(it.cls.key); return it.cls.cat==='struct'? [0,fl(it),o]:[1,o,fl(it)];};
  items.sort((A,B)=>{const a=key(A),b=key(B); for(let k=0;k<3;k++) if(a[k]!==b[k]) return a[k]-b[k]; return A.mn[1]-B.mn[1];});
  const t0=opt.t0||1, t1=opt.t1||22, n=items.length; const stages=[];
  items.forEach((it,i)=>{
    const s=t0+(t1-t0)*i/Math.max(1,n); const vao=mkVAO(it.pos,it.nrm);
    ELEMS.push({kind:'mesh',vao,mn:it.mn,mx:it.mx,color:hex(it.cls.color),alpha:it.cls.alpha||1,cat:it.cls.cat,noEdge:true,
      anim:{t0:s,t1:s+Math.max(0.35,(t1-t0)/n*4),mode:it.cls.mode}});
    const last=stages[stages.length-1]; if(!last||last.key!==it.cls.key) stages.push({key:it.cls.key,t0:s,name:it.name}); });
  // sahne merkezi
  let mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9]; for(const it of items) for(let k=0;k<3;k++){mn[k]=Math.min(mn[k],it.mn[k]);mx[k]=Math.max(mx[k],it.mx[k]);}
  SCENE.bounds={mn,mx}; SCENE.center=[(mn[0]+mx[0])/2,(mn[1]+mx[1])/2,(mn[2]+mx[2])/2];
  return stages;
}
