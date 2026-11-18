// node render.js  — renders all graphics into ../ (drop before.jpg, after.jpg, review.png/jpg into this folder first)
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const D=__dirname,OUT=path.join(D,'..');
const find=n=>['.jpg','.jpeg','.png','.webp'].map(e=>n+e).find(f=>fs.existsSync(path.join(D,f)));
const img=n=>{const f=find(n);return f?`<img src="${f}">`:''};
const jobs=[['p3_post_v2',1350,'P3_post_v2_1080x1350.png'],['p3_post',1350,'P3_post_1080x1350.png'],['story1_question',1920,'story1_0830_question.png'],['story2_review',1920,'story2_1300_review.png'],['story3_p3',1920,'story3_2030_P3.png']];
(async()=>{const b=await chromium.launch();
for(const [n,h,out] of jobs){const p=await b.newPage({viewport:{width:1080,height:h}});
 let html=fs.readFileSync(path.join(D,n+'.html'),'utf8').replace('__BEFORE__',img('before')).replace('__AFTER__',img('after')).replace('__REVIEW__',img('review'));
 const tmp=path.join(D,'_'+n+'.html');fs.writeFileSync(tmp,html);
 await p.goto('file://'+tmp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 await p.screenshot({path:path.join(OUT,out)});fs.unlinkSync(tmp);await p.close();console.log('ok',out);}
await b.close();})();
