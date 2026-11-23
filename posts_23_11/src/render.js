// node render.js [slots]  — renders 23.11 graphics into ../ ; pass number of free slots for the 20:30 story
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');const slots=process.argv[2];
const SL=slots?`ONLY ${slots} SLOTS LEFT THIS WEEK`:'LIMITED SLOTS THIS WEEK';
const z=t=>`<div class="zone" style="top:${t}px">`;
const QUIZ='<div class="stk" style="top:1190px"><div class="qq">Best for a sagging jawline?</div><div class="o">A · RF microneedling</div><div class="o ok">B · ElastiStrom &amp; RF Contour</div></div>';
const POLL='<div class="stk" style="top:1430px"><div class="qq">Which one would you choose?</div><div class="opts"><div>RF</div><div>ELASTISTROM</div><div>NOT SURE</div></div></div>';
const jobs=[...[1,2,3,4,5,6,7].map(i=>[`p5_${i}`,`P5_karuzela/slajd_${i}.png`,'',1350]),
 ['s1_0830','story1_0830_7_days_quiz.png',z(1250)+'↓ QUIZ ↓</div>'],['s1_0830','podglad_story1_quiz.png',QUIZ],
 ['s2_1300','story2_1300_rf_firming_lift.png',z(1480)+'↓ POLL ↓</div>'],['s2_1300','podglad_story2_ankieta.png',POLL],
 ['s3_2030','story3_2030_rf_czy_elastistrom.png','']];
(async()=>{const b=await chromium.launch();fs.mkdirSync(path.join(OUT,'P5_karuzela'),{recursive:true});
for(const [n,out,stk,h] of jobs){const p=await b.newPage({viewport:{width:1080,height:h||1920}});
 const tmp=path.join(D,'_'+n+'.html');fs.writeFileSync(tmp,fs.readFileSync(path.join(D,n+'.html'),'utf8').replace('__STK__',stk).replace('__SLOTS__',SL));
 await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:path.join(OUT,out)});fs.unlinkSync(tmp);await p.close();}
await b.close();console.log('ok')})();
