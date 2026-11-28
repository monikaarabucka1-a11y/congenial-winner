const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');
const z=t=>`<div class="zone" style="top:${t}px">`;
const ASK='<div class="stk" style="top:1400px"><div class="qq">Tell us about your visit 🤍</div><div class="opts"><div>LOVED IT</div><div>CAN’T WAIT</div></div></div>';
const VQ='<div class="stk" style="top:1350px"><div class="qq">Who would love this gift?</div><div class="opts"><div>MUM 💕</div><div>BESTIE ✨</div></div></div>';
const jobs=[...[1,2,3,4,5,6,7,8,9,10].map(i=>[`p_${i}`,`post_karuzela/slajd_${i}.png`,'',1350]),
 ['s1','story1_0930_opinia.png',z(1440)+'↓ POLL ↓</div>'],['s1','podglad_story1.png',ASK],
 ['s2','story2_1300_bony.png',z(1400)+'↓ POLL ↓</div>'],['s2','podglad_story2.png',VQ],
 ['s3','story3_1800_2_days_left.png',z(1340)+'BOOK NOW ↓</div><div class="zone" style="top:1440px;font-size:19px;color:rgba(239,230,218,.6)">or send “BF” / “VOUCHER” in DM</div>']];
(async()=>{const b=await chromium.launch();fs.mkdirSync(path.join(OUT,'post_karuzela'),{recursive:true});
for(const [n,out,stk,h] of jobs){const p=await b.newPage({viewport:{width:1080,height:h||1920}});
 const tmp=path.join(D,'_'+n+'.html');fs.writeFileSync(tmp,fs.readFileSync(path.join(D,n+'.html'),'utf8').replace('__STK__',stk));
 await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:path.join(OUT,out)});fs.unlinkSync(tmp);await p.close();}
await b.close();console.log('ok')})();
