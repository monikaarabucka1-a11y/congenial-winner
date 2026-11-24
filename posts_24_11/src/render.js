// node render.js — renders 24.11 graphics into ../
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');const DATES=fs.readFileSync(path.join(D,'dates.html'),'utf8');
const z=t=>`<div class="zone" style="top:${t}px">`;
const SLIDE='<div class="stk" style="top:1420px"><div class="qq">How dry is your skin this week?</div><div class="bar"><i>🤍</i></div></div>';
const POLL='<div class="stk" style="top:1400px"><div class="qq">Sound familiar?</div><div class="opts"><div>YES, ALL 3</div><div>JUST ONE</div></div></div>';
const jobs=[...[1,2,3,4].map(i=>[`p_${i}`,`post_karuzela/slajd_${i}.png`,'',1350]),
 ['s1_0830','story1_0830_porcelain_day.png',z(1470)+'↓ EMOJI SLIDER ↓</div>'],['s1_0830','podglad_story1_suwak.png',SLIDE],
 ['s2_1300','story2_1300_bariera.png',z(1450)+'↓ POLL ↓</div>'],['s2_1300','podglad_story2_ankieta.png',POLL],
 ['s3_2030','story3_2030_porceramid_terminy.png',''],
 ['s4_glow','story_pakiet_glow_before_christmas.png',z(1370)+'↓ QUESTION ↓</div>'],['s4_glow','podglad_story_pakiet.png','<div class="stk"><div class="qq">Want the Glow package? Send GLOW ✨</div><div class="ans">Type something…</div></div>']];
(async()=>{const b=await chromium.launch();fs.mkdirSync(path.join(OUT,'post_karuzela'),{recursive:true});
for(const [n,out,stk,h] of jobs){const p=await b.newPage({viewport:{width:1080,height:h||1920}});
 const tmp=path.join(D,'_'+n+'.html');fs.writeFileSync(tmp,fs.readFileSync(path.join(D,n+'.html'),'utf8').replace('__STK__',stk).replace('__DATES__',DATES));
 await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:path.join(OUT,out)});fs.unlinkSync(tmp);await p.close();}
await b.close();console.log('ok')})();
