const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
for(const n of ['quiz','offer']){await p.goto('file://'+__dirname+'/'+n+'.html',{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:__dirname+'/story_'+n+'.png'});}
await b.close();})();
