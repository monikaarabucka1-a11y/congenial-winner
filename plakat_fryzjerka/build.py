import re,sys
base=open('poster.html').read()
# restore chosen square text/sizes
base=base.replace("font-size:72px;line-height:1;margin-top:26px;white-space:nowrap","font-size:var(--tsize,90px);line-height:1;margin-top:28px;white-space:nowrap")
base=base.replace("font-size:74px;line-height:1.05;color:#fbf3e6;margin:8px 0 0 4px;white-space:nowrap","font-size:96px;line-height:1;color:#fbf3e6;margin:4px 0 0 6px;white-space:nowrap")
base=base.replace(".kicker{font-size:21px",".kicker{font-size:17px")
T={'pl':dict(kicker='DOŁĄCZ DO NASZEGO ZESPOŁU',title='FRYZJERKA',script='Poszukiwana',tsize='90px',
  li=['Prężnie działający salon','Piękne środowisko pracy','Wielka baza klientów','Elastyczne godziny pracy','Wspierający, rozwojowy zespół'],call='ZADZWOŃ / NAPISZ'),
 'en':dict(kicker='JOIN OUR TEAM',title='HAIRDRESSER',script='Wanted',tsize='68px',
  li=['Busy, thriving salon','Beautiful working environment','Large client base','Flexible working hours','Supportive team to help you grow'],call='CALL / MESSAGE')}
def fill(html,t):
    html=re.sub(r'<div class="kicker">.*?</div>',f'<div class="kicker">{t["kicker"]}</div>',html)
    html=re.sub(r'<div class="title goldtext">.*?</div>',f'<div class="title goldtext" style="--tsize:{t["tsize"]}">{t["title"]}</div>',html)
    html=re.sub(r'<div class="script">.*?</div>',f'<div class="script">{t["script"]}</div>',html)
    html=re.sub(r'<ul>.*?</ul>','<ul>'+''.join(f'<li><b>✓</b>{x}</li>' for x in t['li'])+'</ul>',html,flags=re.S)
    html=html.replace('ZADZWOŃ / NAPISZ',t['call'])
    if t is T['en']: html=html.replace('lang="pl"','lang="en"')
    return html
STORY_CSS='''
html,body{width:1080px;height:1920px}
.poster{width:1080px;height:1920px}
.bg svg{width:1080px;height:1920px}
.bg .tint{background:linear-gradient(180deg,rgba(8,6,4,.55) 0%,rgba(8,6,4,.45) 30%,rgba(8,6,4,.85) 55%,rgba(8,6,4,.92) 100%),
  radial-gradient(ellipse 600px 500px at 50% 62%,rgba(150,100,50,.2),transparent 70%)}
.bg .rays{left:540px;top:560px;width:1800px;height:1800px;margin:-900px 0 0 -900px}
.logo{left:50%;top:80px;width:520px;transform:translateX(-50%)}
.arch{left:50%;right:auto;top:300px;width:520px;height:560px;margin-left:-260px;border-radius:260px 260px 14px 14px}
.arch .inner{border-radius:253px 253px 9px 9px}
.arch img{object-position:42% 50%}
.arch2{left:50%;right:auto;top:272px;width:580px;height:616px;margin-left:-290px;border-radius:300px 300px 20px 20px}
.hair{right:170px;top:690px;width:200px;height:200px}
.left{left:0;right:0;top:905px;width:auto;text-align:center}
.kicker{font-size:22px}
.title{font-size:calc(var(--tsize) * 1.25);margin-top:22px}
.script{font-size:104px;margin:0}
.divider{margin:20px auto 28px;width:560px}
ul{display:inline-block;text-align:left}
li{font-size:24px;margin-bottom:18px}
li b{width:36px;height:36px;font-size:18px}
.contact{bottom:210px;left:70px;right:70px;height:170px}
.contact .name{font-size:36px}.contact .line{font-size:21px}.contact .num{font-size:48px}
'''
for lang,t in T.items():
    sq=fill(base,t)
    open(f'sq_{lang}.html','w').write(sq)
    st=sq.replace('</style>',STORY_CSS+'</style>')
    st=st.replace('viewBox="0 0 1080 1080" width="1080" height="1080"','viewBox="0 0 1080 1920" width="1080" height="1920"')
    st=st.replace('translate(0,-55)','translate(0,880)')
    st=st.replace('r()*1080}px;top:${r()*1080}','r()*1080}px;top:${r()*1920}').replace('i<46','i<80')
    st=st.replace('[[600,60],[600,830],[640,880],[40,640],[560,190]]','[[120,80],[930,300],[60,900],[990,1180],[150,1560],[880,1690]]')
    # bokeh repositions for story
    st=st.replace('left:560px;top:760px','left:880px;top:1500px').replace('left:380px;top:860px','left:120px;top:1300px').replace('left:20px;top:520px','left:40px;top:640px')
    st=re.sub(r'(height:\$\{.*?\})','\\1',st)
    open(f'st_{lang}.html','w').write(st)
