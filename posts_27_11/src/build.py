# Luxury magazine-style story builder (light satin, black text, gold accents)
HEAD='''<!doctype html><html lang="en"><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Montserrat:wght@400;500;600;700&display=block" rel="stylesheet"><link rel="stylesheet" href="common.css"><style>
.s{background:#f3e6cf}.tex{position:absolute;inset:0}
.ph{position:absolute;left:0;right:0}
.gl{position:absolute;left:0;right:0;height:3px;background:linear-gradient(90deg,#7a561c,#e9c983,#fff0c8,#c99a4b,#7a561c)}
.top{position:absolute;top:95px;left:0;right:0;text-align:center}
.k{font-size:22px;letter-spacing:.42em;font-weight:500;color:#1a1410}
.k2{width:120px;height:1px;background:linear-gradient(90deg,transparent,#a37b3a,transparent);margin:20px auto 0}
.new{display:inline-block;margin-top:16px;font-size:18px;letter-spacing:.3em;color:#1a1410;font-weight:600;border:1px solid #a37b3a;border-radius:40px;padding:8px 22px}
.h{font-family:'Playfair Display',serif;font-size:100px;font-weight:500;line-height:1;margin-top:18px;color:#0e0b08}
.h em{font-style:italic;font-weight:600;background:linear-gradient(180deg,#5e400f 0%,#a8782e 40%,#d9b46c 55%,#8f6421 80%,#5a3c10 100%);-webkit-background-clip:text;color:transparent}
.body{position:absolute;left:90px;right:90px;text-align:center;color:#1a1410}
.rw{display:flex;justify-content:space-between;align-items:center;padding:15px 0;border-bottom:1px solid rgba(163,123,58,.4);text-align:left}
.rw:last-child{border-bottom:none}
.rw .n{font-size:29px;font-weight:700;color:#0e0b08}.rw .d{font-size:20px;color:#5a4a3a;margin-top:4px}
.rw .p{font-family:'Playfair Display',serif;font-size:54px;font-weight:700;color:#0e0b08;white-space:nowrap}
.rw .p s{font-size:26px;color:#8a7a68;margin-left:8px;font-weight:500}
.chip{display:inline-block;font-size:22px;letter-spacing:.3em;font-weight:700;color:#0e0b08;padding:14px 34px;border:1.5px solid #a37b3a;border-radius:40px;background:rgba(255,250,240,.6)}
.big{font-family:'Playfair Display',serif;font-size:58px;line-height:1.15;color:#0e0b08}
.big em{font-style:italic;color:#7a561c}
.txt{font-size:30px;line-height:1.5;color:#2a2018}.txt b{color:#0e0b08}
.zone{position:absolute;left:0;right:0;text-align:center;font-size:20px;letter-spacing:.34em;color:#8a6a35;font-weight:600}
.zoneD{position:absolute;left:0;right:0;text-align:center;font-size:20px;letter-spacing:.34em;color:#f3d9a4;font-weight:600;text-shadow:0 2px 8px rgba(0,0,0,.6)}
.lg2{position:absolute;left:0;right:0;bottom:30px;text-align:center}.lg2 img{width:230px;filter:brightness(0) saturate(100%)}
</style></head><body><div class="s"><img class="tex" src="satin_bg.svg" style="width:1080px;height:1920px">'''
def story(photo, ptop, ph, pos, top_html, body_html, extra=''):
    return (HEAD+f'<div class="ph" style="top:{ptop}px;height:{ph}px;background:url({photo}) {pos} no-repeat"></div>'
            f'<div class="gl" style="top:{ptop-2}px"></div><div class="gl" style="top:{ptop+ph}px"></div>'
            '<img src="lux_decor_bg.svg" style="position:absolute;inset:0;width:1080px;height:1920px">'
            f'<div class="top">{top_html}</div>{body_html}{extra}__STK__<div class="lg2"><img src="logo.png"></div></div></body></html>')
ROWS='''<div class="rw"><div><div class="n">RF Microneedling</div><div class="d">lines · pores · scars</div></div><div class="p">£110<s>£180</s></div></div>
<div class="rw"><div><div class="n">ElastiStrom &amp; RF Contour</div><div class="d">lift · jawline · no needles</div></div><div class="p">£130<s>£210</s></div></div>
<div class="rw"><div><div class="n">PorCerAmid</div><div class="d">ceramides · winter skin SOS</div></div><div class="p">£55<s>£85</s></div></div>
<div class="rw"><div><div class="n">Hydrogen Pure Glow</div><div class="d">deep cleanse · instant glow</div></div><div class="p">£55<s>£75</s></div></div>
<div class="rw"><div><div class="n">Glow before Christmas</div><div class="d">Hydrogen Pure Glow + PorCerAmid</div></div><div class="p">£75<s>£160</s></div></div>'''
# 8:30 — It's Black Friday
open('s1.html','w').write(story('party_woman.jpg',470,860,'center 0px/1080px auto',
 '<div class="k">GOOD MORNING FROM ELYSIUM</div><div class="k2"></div><div class="h" style="font-size:86px">It’s <em>Black Friday</em></div>',
 '<div class="body" style="top:1370px"><div class="big">The last weekend<br>of our <em>offers</em> 🖤</div></div>',
 '<div class="zone" style="top:1600px">↓ COUNTDOWN ↓</div>'))
# 13:00 — Fully booked
open('s2.html','w').write(story('party_girls.jpg',470,600,'center -300px/1080px auto',
 '<div class="k">THANK YOU 🤍</div><div class="k2"></div><div class="h">Fully <em>booked</em></div><div class="txt" style="margin-top:14px">this weekend · you’re amazing</div>',
 '<div class="body" style="top:1110px"><div class="big" style="font-size:52px">Still want <em>Black Friday</em> prices?</div>'
 '<div class="txt" style="margin-top:26px">Book by <b>Monday 30.11</b><br>and enjoy your treatment<br>any time until <b>31 January</b> ✨</div>'
 '<div style="margin-top:34px"><span class="chip">SEND “BF” · I REPLY WITHIN 1 HOUR</span></div></div>',
 '<div class="zone" style="top:1680px">↓ LINK ↓</div>'))
# 20:30 — ends Monday + menu
open('s3.html','w').write(story('gabinet.jpg',470,380,'center 62%/1080px auto',
 '<div class="k">BLACK FRIDAY · ENDS MONDAY AT MIDNIGHT</div><div class="k2"></div><div class="new">▶ NEW REEL · LAST WEEKEND</div><div class="h">Last <em>chance</em></div>',
 '<div class="body" style="top:880px">'+ROWS+'<div class="txt" style="margin-top:22px;font-size:26px">Book by <b>30.11</b> · use until <b>31.01</b></div></div>',
 '<div class="zone" style="top:1620px">BOOK NOW ↓</div><div class="zone" style="top:1725px;font-size:18px;letter-spacing:.22em;color:#5a4a3a">or send “BF” in DM · I reply within 1 hour</div>'))
