// node render.js — renders all 19.11 graphics into ../
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');
const HEAD=`<!doctype html><html lang="en"><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600;1,700&family=Montserrat:wght@400;500;600;700&display=block" rel="stylesheet"><link rel="stylesheet" href="common.css">`;
const jobs=[ // [source html, output png, transparent?]
 ['story1_quiz','story1_0830_myth_or_fact.png'],
 ['story1b_answer','story1b_answer_myth.png'],
 ['story2_ceramides','story2_1300_ceramides.png'],
 ['story2_photo','story2_1300_ceramides_zdjecie.png'],
 ['story2_photo','podglad_story2_z_ankieta.png',false,'<div class="poll"><div class="qq">Does your skin feel tight in winter?</div><div class="opts"><div>YES</div><div>NO</div></div></div>'],
 ['story2_overlay','story2_1300_overlay_na_wideo.png',true],
 ['story3_offer','story3_2030_porceramid.png'],
];
// R3 reel boards: [file, number, title EN, sub EN, PL]
const boards=[
 ['0_okladka','','3 mistakes that <em class="goldtext">ruin</em> your skin in winter','Save this before you forget 🤍','3 błędy, które niszczą Twoją skórę zimą'],
 ['1_goraca_woda','1','Hot <em class="goldtext">water</em>','Washes away your skin’s lipids → rough, tight skin','Gorąca woda'],
 ['2_brak_spf','2','Skipping <em class="goldtext">SPF</em>','UVA rays work in November too','Brak SPF'],
 ['3_nawilzenie','3','Not enough <em class="goldtext">hydration</em>','Winter skin loses water faster','Za mało nawilżenia'],
 ['4_rozwiazanie','✦','The fix: <em class="goldtext">ceramides</em>','They rebuild your skin barrier · PorCerAmid £55 <s style="opacity:.6">£85</s> until 30.11','Rozwiązanie: ceramidy'],
];
const reelHtml=(b,mode)=>{const [,n,t,sub,pl]=b;const full=mode==='full';
 let body;
 if(full) body=(n?`<div class="num goldtext ds">${n}</div>`:`<div class="pill" style="margin-bottom:40px">R3 · WINTER SKIN</div>`)+`<div class="t tsh">${t}</div><div class="sub">${sub}</div><div class="pl">${pl}</div>`;
 else body=(n?`<div class="row"><div class="num goldtext">${n}</div><div class="t">${t}</div></div>`:`<div class="kick">WINTER SKIN</div><div class="center"><div class="t">${t}</div></div>`)+`<div class="sub">${sub}</div><div class="pl">${pl}</div>`;
 return fs.readFileSync(path.join(D,'reel_board.html'),'utf8')
  .replace('__MODE__',full?'full':'ov tr').replace('__GLASS__',full?'':'glass')
  .replace('__DECO__',full?'<div class="deco"></div><div class="spark" style="left:880px;top:300px;font-size:40px">✦</div><div class="spark" style="left:150px;top:1450px;font-size:26px">✦</div>':'')
  .replace('__LOGO__',full?'<div class="logo"><img src="logo.png"></div>':'').replace('__BODY__',body);};
(async()=>{const b=await chromium.launch();
 const all=[...jobs.map(([n,o,t,poll])=>[fs.readFileSync(path.join(D,n+'.html'),'utf8').replace('__POLL__',poll||'<div class="zone">↓ POLL ↓</div>'),o,t])];
 fs.mkdirSync(path.join(OUT,'rolka_R3_plansze/pelne'),{recursive:true});fs.mkdirSync(path.join(OUT,'rolka_R3_plansze/nakladki_na_wideo'),{recursive:true});
 for(const bd of boards){all.push([reelHtml(bd,'full'),`rolka_R3_plansze/pelne/${bd[0]}.png`]);all.push([reelHtml(bd,'ov'),`rolka_R3_plansze/nakladki_na_wideo/${bd[0]}.png`,true]);}
 let i=0;for(const [src,out,tr] of all){const p=await b.newPage({viewport:{width:1080,height:1920}});
  const tmp=path.join(D,`_tmp${i++}.html`);fs.writeFileSync(tmp,src.replace('__HEAD__',HEAD));
  await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
  await p.screenshot({path:path.join(OUT,out),omitBackground:!!tr});fs.unlinkSync(tmp);await p.close();console.log('ok',out);}
 await b.close();})();
