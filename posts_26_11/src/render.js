// node render.js ["SLOTS TEXT"] — renders 26.11 stories (party theme) into ../
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');const SL=process.argv[2]||'LIMITED SLOTS LEFT';
const z=t=>`<div class="zone" style="top:${t}px">`;
const POLL='<div class="stk" style="top:1270px"><div class="qq">When is your Christmas party?</div><div class="o">This weekend 🥂</div><div class="o">Next week</div><div class="o">Later in December</div></div>';
const SLIDE='<div class="stk" style="top:1390px"><div class="qq">How party-ready is your skin?</div><div class="bar"><i>✨</i></div></div>';
const LUXPOLL='<div class="stk"><div class="qq">When is your Christmas party?</div><div class="o">This weekend 🥂</div><div class="o">Next week</div><div class="o">Later in December</div></div>';
const jobs=[['s1_lux','story1_0830_party_poll.png','<div class="zone" style="top:1560px">↓ POLL ↓</div>'],['s1_lux','podglad_story1_ankieta.png',LUXPOLL],
 ['s2_lux','story2_1300_party_prep.png','<div class="zone" style="top:1610px">↓ EMOJI SLIDER ↓</div>'],['s2_lux','podglad_story2_suwak.png','<div class="stk"><div class="qq">How party-ready is your skin?</div><div class="bar"><i>✨</i></div></div>'],
 ['s3_lux','story3_2030_party_oferta.png','']];
(async()=>{const b=await chromium.launch();
for(const [n,out,stk] of jobs){const p=await b.newPage({viewport:{width:1080,height:1920}});
 const tmp=path.join(D,'_'+n+'.html');fs.writeFileSync(tmp,fs.readFileSync(path.join(D,n+'.html'),'utf8').replace('__STK__',stk).replace('__SLOTS__',SL));
 await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:path.join(OUT,out)});fs.unlinkSync(tmp);await p.close();}
await b.close();console.log('ok')})();
