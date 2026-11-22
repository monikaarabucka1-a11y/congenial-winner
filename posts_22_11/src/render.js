// node render.js — renders 22.11 graphics into ../
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');
const z=(t)=>`<div class="zone" style="top:${t}px">`;
const POLL='<div class="stk" style="top:1420px"><div class="qq">What bothers you more?</div><div class="opts"><div>JAWLINE</div><div>WRINKLES</div></div></div>';
const ASK='<div class="stk" style="top:1050px"><div class="qq">Ask me anything about skin 🤍</div><div class="ans">Type something…</div></div>';
const SLIDE='<div class="stk" style="top:1400px"><div class="qq">Do you use SPF on your hands?</div><div class="bar"><i>👋</i></div></div>';
const jobs=[
 ['s1_0930','story1_0930_ankieta_owal_zmarszczki.png',z(1470)+'↓ POLL ↓</div>'],['s1_0930','podglad_story1_ankieta.png',POLL],
 ['s1b_0935','story1b_0935_zapytaj_mnie.png',z(1120)+'↓ QUESTION ↓</div>'],['s1b_0935','podglad_story1b_pytanie.png',ASK],
 ['s2_1300','story2_1300_spf_dlonie.png',z(1460)+'↓ EMOJI SLIDER ↓</div>'],['s2_1300','podglad_story2_suwak.png',SLIDE],
 ['s3_1800','story3_1800_8_days_left.png',''],
 ['post_8dni','post_zapasowy_8_days_left_1080x1350.png','',1350]];
(async()=>{const b=await chromium.launch();
for(const [n,out,stk,h] of jobs){const p=await b.newPage({viewport:{width:1080,height:h||1920}});
 const tmp=path.join(D,'_'+n+'.html');fs.writeFileSync(tmp,fs.readFileSync(path.join(D,n+'.html'),'utf8').replace('__STK__',stk));
 await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:path.join(OUT,out)});fs.unlinkSync(tmp);await p.close();}
await b.close();console.log('ok')})();
