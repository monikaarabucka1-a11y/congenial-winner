// node render.js — renders 21.11 graphics into ../
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');
const POLL='<div class="poll"><div class="qq">Heard of ElastiStrom?</div><div class="opts"><div>YES</div><div>WHAT’S THAT?</div></div></div>';
const ZONE='<div class="zone">↓ POLL ↓</div>';
const jobs=[...[1,2,3,4,5,6].map(i=>[`p4_${i}`,1350,`P4_karuzela/slajd_${i}.png`]),
 ['story2_1300',1920,'story2_1300_elastistrom_ankieta.png',ZONE],['story2_1300',1920,'podglad_story2_z_ankieta.png',POLL],
 ['story3_1800',1920,'story3_1800_oferta_elastistrom.png']];
(async()=>{const b=await chromium.launch();fs.mkdirSync(path.join(OUT,'P4_karuzela'),{recursive:true});
for(const [n,h,out,poll] of jobs){const p=await b.newPage({viewport:{width:1080,height:h}});
 const tmp=path.join(D,'_'+n+'.html');fs.writeFileSync(tmp,fs.readFileSync(path.join(D,n+'.html'),'utf8').replace('__POLL__',poll||''));
 await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:path.join(OUT,out)});fs.unlinkSync(tmp);await p.close();console.log('ok',out);}
await b.close();})();
