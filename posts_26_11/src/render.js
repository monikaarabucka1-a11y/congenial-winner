// node render.js ["SLOTS TEXT"] — renders 26.11 stories (party theme) into ../
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');const SL=process.argv[2]||'LIMITED SLOTS LEFT';
const z=t=>`<div class="zone" style="top:${t}px">`;
const POLL='<div class="stk" style="top:1230px"><div class="qq">When is your Christmas party?</div><div class="o">This weekend 🥂</div><div class="o">Next week</div><div class="o">Later in December</div></div>';
const SLIDE='<div class="stk" style="top:1350px"><div class="qq">How party-ready is your skin?</div><div class="bar"><i>✨</i></div></div>';
const jobs=[['s1_0830','story1_0830_party_poll.png',z(1330)+'↓ POLL ↓</div>'],['s1_0830','podglad_story1_ankieta.png',POLL],
 ['s2_1300','story2_1300_party_prep.png',z(1400)+'↓ EMOJI SLIDER ↓</div>'],['s2_1300','podglad_story2_suwak.png',SLIDE],
 ['s3_2030','story3_2030_party_oferta.png','']];
(async()=>{const b=await chromium.launch();
for(const [n,out,stk] of jobs){const p=await b.newPage({viewport:{width:1080,height:1920}});
 const tmp=path.join(D,'_'+n+'.html');fs.writeFileSync(tmp,fs.readFileSync(path.join(D,n+'.html'),'utf8').replace('__STK__',stk).replace('__SLOTS__',SL));
 await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:path.join(OUT,out)});fs.unlinkSync(tmp);await p.close();}
await b.close();console.log('ok')})();
