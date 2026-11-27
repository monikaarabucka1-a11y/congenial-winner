const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');
const jobs=[['s1','story1_0830_black_friday.png'],['s2_dark','story2_1300_fully_booked.png'],['s3_dark','story3_2030_last_chance.png']];
(async()=>{const b=await chromium.launch();
for(const [n,out] of jobs){const p=await b.newPage({viewport:{width:1080,height:1920}});
 const tmp=path.join(D,'_'+n+'.html');fs.writeFileSync(tmp,fs.readFileSync(path.join(D,n+'.html'),'utf8').replace('__STK__',''));
 await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:path.join(OUT,out)});fs.unlinkSync(tmp);await p.close();}
await b.close();console.log('ok')})();
