// node render.js ["SLOTS TEXT"] — renders 25.11 stories into ../
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');const SL=process.argv[2]||'LIMITED SLOTS LEFT';
const z=t=>`<div class="zone" style="top:${t}px">`;
const ASK='<div class="stk" style="top:1270px"><div class="qq">Ask me about RF recovery 🤍</div><div class="ans">Type something…</div></div>';
const QUIZ='<div class="stk" style="top:1270px"><div class="qq">When do RF results peak?</div><div class="o">A · After 1 day</div><div class="o ok">B · After 4–6 weeks</div></div>';
const jobs=[['s1_0830','story1_0830_rf_recovery.png',z(1330)+'↓ QUESTION ↓</div>'],['s1_0830','podglad_story1_pytanie.png',ASK],
 ['s2_1300','story2_1300_rf_quiz.png',z(1330)+'↓ QUIZ ↓</div>'],['s2_1300','podglad_story2_quiz.png',QUIZ],
 ['s3_2030','story3_2030_rf_oferta.png','']];
(async()=>{const b=await chromium.launch();
for(const [n,out,stk] of jobs){const p=await b.newPage({viewport:{width:1080,height:1920}});
 const tmp=path.join(D,'_'+n+'.html');fs.writeFileSync(tmp,fs.readFileSync(path.join(D,n+'.html'),'utf8').replace('__STK__',stk).replace('__SLOTS__',SL));
 await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:path.join(OUT,out)});fs.unlinkSync(tmp);await p.close();}
await b.close();console.log('ok')})();
