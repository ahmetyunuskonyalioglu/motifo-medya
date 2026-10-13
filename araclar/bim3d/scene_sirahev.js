// Üç birimli, üç katlı sıra ev — inşaat sırası (BİM 4D anlatımı)
const H=3.1, L=[0,3.1,6.2,9.3], ST=0.25, W=21, D=11, UNITS=[0,7,14];
const C={found:hex('#7c7870'),conc:hex('#aaa69f'),beam:hex('#9f9b94'),wall:hex('#e6dccd'),part:hex('#efe9df'),
 blue:hex('#2f6fd6'),red:hex('#d64532'),waste:hex('#7d838c'),duct:hex('#b9c0c9'),tray:hex('#e2b62c'),
 screed:hex('#cbc5ba'),parquet:hex('#b98a58'),tile:hex('#dcdfe2'),glass:hex('#9ec3dc'),frame:hex('#3b3d40'),
 wood:hex('#9a6a42'),roof:hex('#4a4c50'),ground:hex('#d3cfc6'),grass:hex('#bcc7a6'),road:hex('#8e9093'),pave:hex('#e3dfd7'),hedge:hex('#8fa476')};
const STAGES=[
 {key:'temel',no:'01',name:'Temel',line:'Radye temel, kazı kotunda',t0:1.2,t1:3.2},
 {key:'tasiyici',no:'02',name:'Taşıyıcı sistem',line:'Kolon, kiriş ve döşeme, kat kat',t0:3.2,t1:8.8},
 {key:'duvar',no:'03',name:'Duvarlar',line:'Dış duvar, ara duvar, pencere boşlukları',t0:8.8,t1:11.4},
 {key:'tesisat',no:'04',name:'Tesisat',line:'Temiz su, sıcak su, atık su, elektrik, havalandırma',t0:11.4,t1:15.2},
 {key:'sap',no:'05',name:'Şap',line:'Her katta düz bir zemin',t0:15.2,t1:16.6},
 {key:'kaplama',no:'06',name:'Döşeme kaplaması',line:'Parke ve seramik, mahal listesine göre',t0:16.6,t1:18.2},
 {key:'cephe',no:'07',name:'Cephe ve doğrama',line:'Cam, ahşap kaplama, balkonlar',t0:18.2,t1:21.4},
 {key:'cati',no:'08',name:'Çatı',line:'Ve bina tamam',t0:21.4,t1:23.2},
];
SCENE.stages=STAGES; SCENE.duration=26.0;
let CAT='site'; const add=e=>{e.cat=e.cat||CAT; ELEMS.push(e);};
const box=(min,size,color,anim,extra={})=>add(Object.assign({kind:'box',min,size,color,anim},extra));
const pipe=(a,b,r,color,anim,extra={})=>add(Object.assign({kind:'pipe',a,b,r,color,anim,noEdge:true},extra));
const A=(t0,dur,mode)=>({t0,t1:t0+dur,mode});
// --- arazi (baştan var)
box([-70,-0.05,-70],[160,0.05,150],C.ground,null,{noEdge:true});
box([-6,-0.04,-8],[33,0.05,6.4],C.pave,null,{noEdge:true});
box([-30,-0.045,-16],[90,0.05,6.5],C.road,null,{noEdge:true});
box([-6,-0.03,12.4],[33,0.06,6],C.grass,null,{noEdge:true});
for(const x of [-4.5,2,8.5,15,21.5]) box([x,0,-6.6],[3.2,0.7,0.7],C.hedge,null,{noEdge:true});
// --- 01 temel
CAT='struct';
box([-0.4,-0.8,-0.4],[W+0.8,0.8,D+0.8],C.found,A(1.3,1.4,'growY'));
// --- 02 taşıyıcı
const XS=[0.18,3.5,7,10.5,14,17.5,20.82], ZS=[0.18,5.5,10.82];
for(let k=0;k<3;k++){
  const b=3.3+k*1.8; let i=0;
  for(const z of ZS) for(const x of XS){ box([x-0.175,L[k],z-0.175],[0.35,H-ST,0.35],C.conc,A(b+0.012*(i++),0.55,'growY')); }
  for(const z of ZS) box([0,L[k+1]-ST-0.45,z-0.15],[W,0.45,0.3],C.beam,A(b+0.55,0.5,'wipeX'));
  for(const x of XS) box([x-0.15,L[k+1]-ST-0.45,0],[0.3,0.45,D],C.beam,A(b+0.6,0.45,'wipeZ'));
  box([0,L[k+1]-ST,0],[W,ST,D],C.conc,A(b+0.95,0.75,'drop'));
  if(k<2) for(const u of UNITS) box([u+0.5,L[k+1]-ST,-1.5],[6,ST,1.5],C.conc,A(b+1.15,0.6,'drop'));
}
// --- 03 duvarlar
CAT='wall';
const wt=0.22, wh=H-ST;
for(let k=0;k<3;k++){
  const b=8.9+k*0.62, y=L[k];
  for(const u of UNITS){ // arka duvar, pencere boşluklu
    const z=D-wt;
    box([u,y,z],[2.5,wh,wt],C.wall,A(b,0.5,'growY'));
    box([u+4.5,y,z],[2.5,wh,wt],C.wall,A(b+0.05,0.5,'growY'));
    box([u+2.5,y,z],[2,0.9,wt],C.wall,A(b+0.08,0.4,'growY'));
    box([u+2.5,y+2.3,z],[2,wh-2.3,wt],C.wall,A(b+0.3,0.35,'growY'));
    // iç bölmeler (ıslak hacim)
    box([u+0.2,y,6],[3.0,wh,0.12],C.part,A(b+0.25,0.45,'growY'));
    box([u+3.2,y,6],[0.12,wh,D-wt-6],C.part,A(b+0.3,0.45,'growY'));
  }
  for(const x of [0, W-wt]){ // yan duvarlar
    box([x,y,0],[wt,wh,4.5],C.wall,A(b+0.1,0.5,'growY'));
    box([x,y,6.5],[wt,wh,D-6.5],C.wall,A(b+0.12,0.5,'growY'));
    box([x,y,4.5],[wt,0.9,2],C.wall,A(b+0.15,0.4,'growY'));
    box([x,y+2.3,4.5],[wt,wh-2.3,2],C.wall,A(b+0.35,0.35,'growY'));
  }
  for(const x of [7-0.11,14-0.11]) box([x,y,0],[wt,wh,D],C.wall,A(b+0.18,0.5,'growY'));
}
// --- 04 tesisat
CAT='mep'; // görünürlük için çaplar abartılı
pipe([-4,-0.45,-2.2],[25,-0.45,-2.2],0.2,C.waste,A(11.45,1.0,'extend'));
UNITS.forEach((u,i)=>{
  const b=11.7+i*0.2, rx=u+3.9, rz=5.0;
  pipe([rx,-0.45,rz],[rx,9.05,rz],0.1,C.blue,A(b,1.1,'extend'));
  pipe([rx+0.3,-0.45,rz],[rx+0.3,9.05,rz],0.1,C.red,A(b+0.1,1.1,'extend'));
  pipe([rx+0.65,-0.45,rz+0.05],[rx+0.65,9.3,rz+0.05],0.15,C.waste,A(b+0.05,1.2,'extend'));
  pipe([rx+0.65,-0.45,rz+0.05],[rx+0.65,-0.45,-2.2],0.15,C.waste,A(b-0.15,0.45,'extend'));
  box([rx+1.05,L[0],rz-0.1],[0.36,L[3]-0.1,0.1],C.tray,A(b+0.2,1.1,'growY'),{noEdge:true});
  for(let k=0;k<3;k++){
    const c=L[k+1]-ST-0.62, bb=b+1.15+k*0.38;
    pipe([rx,c,rz],[rx,c,1.0],0.08,C.blue,A(bb,0.45,'extend'));
    pipe([rx,c,1.0],[u+0.8,c,1.0],0.08,C.blue,A(bb+0.45,0.4,'extend'));
    pipe([rx+0.3,c-0.18,rz],[rx+0.3,c-0.18,1.3],0.08,C.red,A(bb+0.08,0.45,'extend'));
    pipe([rx+0.3,c-0.18,1.3],[u+6.2,c-0.18,1.3],0.08,C.red,A(bb+0.53,0.4,'extend'));
    pipe([rx+0.65,L[k]+0.16,rz+0.05],[rx+0.65,L[k]+0.16,9.6],0.11,C.waste,A(bb+0.1,0.45,'extend'));
    box([u+1.05,L[k+1]-ST-0.2,2.6],[0.4,0.1,6.0],C.tray,A(bb+0.25,0.5,'wipeZ'),{noEdge:true});
    if(!(k===1&&i===1)) box([u+0.3,L[k+1]-ST-0.98,7.4],[6.4,0.34,0.55],C.duct,A(bb+0.2,0.55,'wipeX'),{noEdge:true});
  }
});
// çakışma: 2. kat önde, kanal z yönlü kirişi (x=10.5) kesiyor → tespit → kot düzeltmesi
{ const y0=L[2]-ST-0.45+0.02;
  box([0.4,y0,3.2],[6.2,0.36,0.6],C.duct,{t0:13.95,t1:14.55,mode:'shift',dy:-0.5,appear:12.75},{});
  box([2.95,y0-0.25,2.85],[1.1,1.0,1.3],hex('#e5322d'),{t0:13.05,t1:13.95,mode:'pulse'},{noShadow:true,unlit:true,alpha:0.95});
}
SCENE.clash={t0:13.0,t1:14.6}; SCENE.xray=[12.75,14.85];
// --- 05 şap
CAT='finish';
for(let k=0;k<3;k++) box([wt,L[k],wt],[W-2*wt,0.07,D-2*wt],C.screed,A(15.3+k*0.35,0.7,'wipeX'),{noEdge:true});
// --- 06 kaplama
for(let k=0;k<3;k++) UNITS.forEach((u,i)=>{
  const b=16.7+k*0.32+i*0.12;
  box([u+0.25,L[k]+0.07,0.25],[6.5,0.03,5.75],C.parquet,A(b,0.6,'wipeX'),{noEdge:true});
  box([u+0.25,L[k]+0.07,6.1],[2.95,0.03,D-wt-6.1],C.tile,A(b+0.2,0.5,'wipeX'),{noEdge:true});
});
// --- 07 cephe
CAT='facade'; // ve doğrama
for(let k=0;k<3;k++){
  const y=L[k], b=18.3+k*0.45;
  UNITS.forEach((u,i)=>{
    const bb=b+i*0.12;
    box([u,y,0],[1.2,wh,wt],C.wall,A(bb,0.5,'growY'));
    box([u+5.8,y,0],[1.2,wh,wt],C.wall,A(bb+0.05,0.5,'growY'));
    box([u+1.2,y+2.45,0],[4.6,wh-2.45,wt],C.wall,A(bb+0.2,0.35,'growY'));
    box([u+1.25,y+0.02,0.06],[4.5,2.4,0.06],C.glass,A(bb+0.45,0.6,'fade'),{alpha:0.38,noEdge:true,noShadow:true});
    for(const fx of [1.2,2.73,4.27,5.75]) box([u+fx,y,0.04],[0.05,2.45,0.1],C.frame,A(bb+0.35,0.4,'growY'),{noEdge:true});
    box([u+2.5,y+0.9,D-wt+0.05],[2,1.4,0.05],C.glass,A(bb+0.5,0.5,'fade'),{alpha:0.38,noEdge:true,noShadow:true});
    for(let s=0;s<5;s++) box([u+0.08+s*0.22,y+0.05,-0.12],[0.12,wh-0.1,0.1],C.wood,A(bb+0.55+s*0.04,0.5,'drop'),{noEdge:true});
    if(k>0) box([u+0.5,L[k]+0.02,-1.48],[6,1.0,0.04],C.glass,A(bb+0.6,0.5,'fade'),{alpha:0.3,noEdge:true,noShadow:true});
  });
}
for(const x of [0,W-wt]) for(let k=0;k<3;k++) box([x+(x?0.03:-0.03),L[k]+0.9,4.5],[0.05,1.4,2],C.glass,A(19.6+k*0.2,0.5,'fade'),{alpha:0.38,noEdge:true,noShadow:true});
// --- 08 çatı
CAT='roof';
const rise=2.2, run=D/2+0.6, len=Math.hypot(run,rise), ang=Math.atan2(rise,run);
box([-0.6,L[3],-0.6],[W+1.2,0.2,len],C.roof,A(21.5,0.9,'drop'),{rot:['x',-ang,[0,L[3],-0.6]]});
box([-0.6,L[3],D+0.6-len],[W+1.2,0.2,len],C.roof,A(21.75,0.9,'drop'),{rot:['x',ang,[0,L[3],D+0.6]]});
// --- kamera: aşamalara göre anahtar kareler
SCENE.center=[10.5,4,5.5]; SCENE.sun=[-0.5,0.8,-0.6]; SCENE.bg=[0.948,0.946,0.938];
const KEYS=[ // t, az(derece), el(derece), R, hedef
 [0.0,-36,36,44,[10.5,3.0,5.5]],
 [3.2,-30,32,42,[10.5,3.6,5.5]],
 [8.8,-16,24,41,[10.5,5.0,5.0]],
 [11.4,-6,16,34,[10.5,5.0,4.5]],
 [12.7,4,16,19,[4.2,5.2,4.0]],
 [14.7,16,14,18,[4.2,5.2,4.0]],
 [16.6,14,13,30,[10.5,4.4,4.5]],
 [18.2,18,15,38,[10.5,5.0,5.0]],
 [21.4,26,18,41,[10.5,5.6,5.0]],
 [26.0,38,22,44,[10.5,6.0,5.0]]];
SCENE.camera=(t)=>{
  let a=KEYS[0],b=KEYS[KEYS.length-1];
  for(let i=0;i<KEYS.length-1;i++) if(t>=KEYS[i][0]&&t<=KEYS[i+1][0]){a=KEYS[i];b=KEYS[i+1];break;}
  const u=b[0]>a[0]?ease((t-a[0])/(b[0]-a[0])):1, l=(x,y)=>x+(y-x)*u;
  const az=l(a[1],b[1])*Math.PI/180, el=l(a[2],b[2])*Math.PI/180, R=l(a[3],b[3]);
  const tg=[l(a[4][0],b[4][0]),l(a[4][1],b[4][1]),l(a[4][2],b[4][2])];
  return {eye:[tg[0]+R*Math.cos(el)*Math.sin(az),tg[1]+R*Math.sin(el),tg[2]-R*Math.cos(el)*Math.cos(az)],target:tg,fov:56*Math.PI/180};
};
