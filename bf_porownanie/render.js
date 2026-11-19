const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for(const [n,h] of [['bf_comparison_post',1350],['bf_comparison_story',1920]]){const p=await b.newPage({viewport:{width:1080,height:h}});
await p.goto('file://'+__dirname+'/'+n+'.html',{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
const r=await p.evaluate(()=>{const R=document.querySelector('.rows').getBoundingClientRect();const F=document.querySelector('.foot').getBoundingClientRect();return [Math.round(R.bottom),Math.round(F.top)]});console.log(n,'rows end',r[0],'foot top',r[1]);
await p.screenshot({path:__dirname+'/'+n+'.png'});await p.close();}
await b.close();})();
