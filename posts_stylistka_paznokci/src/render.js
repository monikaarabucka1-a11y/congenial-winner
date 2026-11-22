const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');
(async()=>{const b=await chromium.launch();
for(const [n,h,out] of [['post',1350,'post_nowa_stylistka_1080x1350.png'],['story',1920,'story_nowa_stylistka_1080x1920.png']]){
 const p=await b.newPage({viewport:{width:1080,height:h}});await p.goto('file://'+path.join(D,n+'.html'),{waitUntil:'networkidle'});
 await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);await p.screenshot({path:path.join(OUT,out)});await p.close();}
await b.close();console.log('ok')})();
