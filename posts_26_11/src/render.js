// node render.js ["SLOTS TEXT"] — renders 26.11 graphics into ../
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');const SL=process.argv[2]||'LIMITED SLOTS LEFT';
const z=t=>`<div class="zone" style="top:${t}px">`;
const POLL='<div class="stk" style="top:1330px"><div class="qq">Hair or skin first?</div><div class="opts"><div>HAIR ✂️</div><div>SKIN ✨</div></div></div>';
const ASK='<div class="stk" style="top:1150px"><div class="qq">Acne or redness? Ask me 🤍</div><div class="ans">Type something…</div></div>';
const jobs=[...[1,2,3,4,5,6].map(i=>[`p_${i}`,`post_karuzela/slajd_${i}.png`,'',1350]),
 ['s1_0830','story1_0830_team.png',z(1390)+'↓ POLL ↓</div>'],['s1_0830','podglad_story1_ankieta.png',POLL],
 ['s2_1300','story2_1300_vascular_calm.png',z(1200)+'↓ QUESTION ↓</div>'],['s2_1300','podglad_story2_pytanie.png',ASK],
 ['s3_2030','story3_2030_4_days_left.png','']];
(async()=>{const b=await chromium.launch();fs.mkdirSync(path.join(OUT,'post_karuzela'),{recursive:true});
for(const [n,out,stk,h] of jobs){const p=await b.newPage({viewport:{width:1080,height:h||1920}});
 const tmp=path.join(D,'_'+n+'.html');fs.writeFileSync(tmp,fs.readFileSync(path.join(D,n+'.html'),'utf8').replace('__STK__',stk).replace('__SLOTS__',SL));
 await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:path.join(OUT,out)});fs.unlinkSync(tmp);await p.close();}
await b.close();console.log('ok')})();
