# 28.11 — reviews & gift vouchers (dark gold style). Writes HTML pages; render.js screenshots them.
FONT = '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600;1,700&family=Montserrat:wght@400;500;600;700&display=block" rel="stylesheet"><link rel="stylesheet" href="common.css">'
CSS = '''
.k{font-size:22px;letter-spacing:.32em;color:var(--gold);font-weight:600}
.H{font-family:'Playfair Display',serif;font-weight:800;line-height:1.02}
.H em{font-style:italic;font-weight:600;color:#fbf3e6;-webkit-text-fill-color:#fbf3e6}
.txt{font-size:30px;line-height:1.5;color:#efe6da}.txt b{color:#f6dcae}
.pairs{display:flex;gap:16px}
.ph2{flex:1;position:relative;border-radius:22px;overflow:hidden;border:2px solid rgba(216,173,116,.8);box-shadow:0 16px 40px rgba(0,0,0,.5)}
.ph2 img{width:100%;height:100%;object-fit:cover;display:block}
.tg{position:absolute;left:16px;top:14px;transform:none;font-size:16px;padding:8px 16px;letter-spacing:.2em}
.fine2{font-size:20px;color:#9e8f7c}
.stars{font-size:46px;letter-spacing:.25em;color:#f6dcae}
.qt{font-family:'Playfair Display',serif;font-style:italic;font-weight:600;color:#fbf3e6;line-height:1.35}
.qt b{color:#f6dcae}
.who{display:flex;align-items:center;justify-content:center;gap:16px;font-size:23px;letter-spacing:.22em;color:var(--gold);font-weight:600;margin-top:30px}
.who span{width:60px;height:1px;background:var(--gold)}
.voucher{position:relative;border-radius:26px;padding:46px 50px;background:linear-gradient(135deg,#1b140d,#0d0a07 60%,#1b140d);border:2px solid rgba(216,173,116,.85);box-shadow:0 24px 60px rgba(0,0,0,.6),inset 0 0 0 10px rgba(216,173,116,.08);text-align:center;overflow:hidden}
.voucher::before{content:"";position:absolute;top:0;bottom:0;right:50px;width:40px;background:linear-gradient(180deg,#f3d39e,#c9955a,#f3d39e);opacity:.9}
.voucher::after{content:"";position:absolute;left:0;right:0;bottom:40px;height:40px;background:linear-gradient(90deg,#f3d39e,#c9955a,#f3d39e);opacity:.9}
.vin{position:relative;z-index:2}
.bow{position:absolute;right:-6px;bottom:-14px;z-index:3;font-size:130px;filter:drop-shadow(0 6px 10px rgba(0,0,0,.5))}
.zone{position:absolute;left:0;right:0;text-align:center;font-size:22px;letter-spacing:.3em;color:rgba(246,220,174,.85);font-weight:600}
.stk{position:absolute;left:170px;right:170px;background:#fff;border-radius:24px;padding:24px;font-family:-apple-system,Helvetica,Arial,sans-serif;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,.4)}
.stk .qq{font-size:30px;font-weight:700;color:#111}
.stk .opts{display:flex;border-top:1px solid #ddd;margin-top:16px}
.stk .opts div{flex:1;padding:18px 0 4px;font-size:28px;font-weight:700;background:linear-gradient(90deg,#c9955a,#e8b878);-webkit-background-clip:text;color:transparent}
.stk .opts div+div{border-left:1px solid #ddd}
'''
REVIEW = ('I’m blown away by the fantastic results after each treatment! <b>My skin never looked better.</b> '
          'Monika has a huge knowledge and provides treatments to the highest standards.')

def post(n, total, inner, bg=''):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">{FONT}<style>html,body{{width:1080px;height:1350px}}{CSS}</style></head><body>'
            f'<div class="c">{bg}<div class="deco"></div><div class="no">{n:02d} / {total:02d}</div>{inner}'
            '<div class="lg"><img src="logo.png"></div></div></body></html>')

def story(inner, bg=''):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">{FONT}<style>{CSS}</style></head><body>'
            f'<div class="s">{bg}<div class="deco"></div>{inner}__STK__<div class="logo" style="bottom:70px;width:230px"><img src="logo.png"></div></div></body></html>')

def blurbg(img, pos='center', br=.35):
    return f'<div style="position:absolute;inset:0;background:url({img}) {pos}/cover;filter:blur(3px) brightness({br});transform:scale(1.05)"></div>'

T = 5
P = {}
P['p_1'] = post(1, T, '''<div style="position:absolute;top:150px;left:0;right:0;text-align:center"><div class="pill">BLACK FRIDAY · 2 DAYS LEFT</div>
<div class="H goldtext ds" style="font-size:110px;margin-top:40px">Your skin,<br><em>our proof</em></div>
<div class="txt" style="margin:36px 120px 0">Real words and real results from our clients this month 🤍</div>
<div class="stars" style="margin-top:40px">★★★★★</div></div><div class="swipe">SWIPE →</div>''', blurbg('party_woman.jpg', 'center 20%'))
P['p_2'] = post(2, T, f'''<div style="position:absolute;top:110px;left:0;right:0;text-align:center"><div class="k">WHAT OUR CLIENTS SAY</div><div class="stars" style="margin-top:20px">★★★★★</div></div>
<div class="glass" style="position:absolute;left:90px;right:90px;top:330px;padding:70px 70px 60px;text-align:center">
<div style="font-family:'Playfair Display',serif;font-size:180px;line-height:.5;color:rgba(216,173,116,.6)">“</div>
<div class="qt" style="font-size:52px;margin-top:10px">{REVIEW}</div>
<div class="who"><span></span>IZABELA B.<span></span></div><div class="fine2" style="margin-top:10px">Facebook recommendation</div></div>
<div class="swipe">→</div>''')
P['p_3'] = post(3, T, '''<div style="position:absolute;top:100px;left:0;right:0;text-align:center"><div class="k">RF MICRONEEDLING</div><div class="H goldtext" style="font-size:72px;margin-top:12px">One session, <em>straight after</em></div></div>
<div class="pairs" style="position:absolute;left:70px;right:70px;top:290px;height:720px"><div class="ph2"><img src="c1_przed.jpg"><div class="tag pill tg">BEFORE</div></div><div class="ph2"><img src="c1_po.jpg"><div class="tag pill tg">AFTER</div></div></div>
<div style="position:absolute;left:0;right:0;top:1040px;text-align:center"><div class="txt">Plumper, smoother skin · collagen builds for 4–6 weeks</div><div class="fine2" style="margin-top:12px">Real client · shared with permission · results vary</div></div><div class="swipe">→</div>''')
P['p_4'] = post(4, T, '''<div style="position:absolute;top:100px;left:0;right:0;text-align:center"><div class="k">HYDROGEN PURE GLOW</div><div class="H goldtext" style="font-size:72px;margin-top:12px">One treatment, <em>no filters</em></div></div>
<div class="pairs" style="position:absolute;left:70px;right:70px;top:290px;height:720px"><div class="ph2"><img src="glow_b.jpg" style="object-position:center 40%"><div class="tag pill tg">BEFORE</div></div><div class="ph2"><img src="glow_a.jpg" style="object-position:center 40%"><div class="tag pill tg">AFTER</div></div></div>
<div style="position:absolute;left:0;right:0;top:1040px;text-align:center"><div class="txt">Clearer pores · brighter, more even tone · instant glow</div><div class="fine2" style="margin-top:12px">Real client · shared with permission · results vary</div></div><div class="swipe">→</div>''')
P['p_5'] = post(5, T, '''<div style="position:absolute;top:120px;left:0;right:0;text-align:center"><div class="pill">YOUR TURN 🤍</div>
<div class="H goldtext ds" style="font-size:96px;margin-top:34px">Ready for <em>your glow?</em></div></div>
<div class="glass" style="position:absolute;left:110px;right:110px;top:520px;padding:40px 46px">
<div style="display:flex;justify-content:space-between;font-size:30px;color:#fbf3e6;padding:12px 0;border-bottom:1px solid rgba(216,173,116,.25)"><b>RF Microneedling</b><span class="goldtext" style="font-family:'Playfair Display',serif;font-weight:800;font-size:44px">£110</span></div>
<div style="display:flex;justify-content:space-between;font-size:30px;color:#fbf3e6;padding:12px 0;border-bottom:1px solid rgba(216,173,116,.25)"><b>ElastiStrom &amp; RF</b><span class="goldtext" style="font-family:'Playfair Display',serif;font-weight:800;font-size:44px">£130</span></div>
<div style="display:flex;justify-content:space-between;font-size:30px;color:#fbf3e6;padding:12px 0;border-bottom:1px solid rgba(216,173,116,.25)"><b>PorCerAmid</b><span class="goldtext" style="font-family:'Playfair Display',serif;font-weight:800;font-size:44px">£55</span></div>
<div style="display:flex;justify-content:space-between;font-size:30px;color:#fbf3e6;padding:12px 0"><b>Hydrogen Pure Glow</b><span class="goldtext" style="font-family:'Playfair Display',serif;font-weight:800;font-size:44px">£55</span></div></div>
<div style="position:absolute;left:0;right:0;top:960px;text-align:center"><div class="txt">Book by <b>Monday 30.11</b> · use until <b>31 January</b></div>
<div class="pill" style="margin-top:30px;font-size:28px;padding:20px 50px">SEND “BF” TO BOOK</div></div>''', blurbg('gabinet.jpg', 'center', .3))

S = {}
S['s1'] = story(f'''<div style="position:absolute;top:150px;left:0;right:0;text-align:center"><div class="pill">GOOD MORNING FROM ELYSIUM ☕</div><div class="stars" style="margin-top:36px">★★★★★</div></div>
<div class="glass" style="position:absolute;left:90px;right:90px;top:420px;padding:70px 64px;text-align:center">
<div style="font-family:'Playfair Display',serif;font-size:170px;line-height:.5;color:rgba(216,173,116,.6)">“</div>
<div class="qt" style="font-size:50px">{REVIEW}</div><div class="who"><span></span>IZABELA B.<span></span></div></div>
<div style="position:absolute;left:0;right:0;top:1300px;text-align:center" class="txt">Thank you for trusting us 🤍</div>''')
S['s2'] = story('''<div style="position:absolute;top:150px;left:0;right:0;text-align:center"><div class="pill">CHRISTMAS GIFT SORTED 🎄</div>
<div class="H goldtext ds" style="font-size:104px;margin-top:30px">The gift of<br><em>glowing skin</em></div></div>
<div style="position:absolute;left:110px;right:110px;top:640px"><div class="voucher"><div class="vin">
<div class="k" style="color:#f6dcae">ELYSIUM CLINIC</div><div class="H goldtext" style="font-size:88px;margin-top:14px">Gift Voucher</div>
<div class="txt" style="margin-top:20px;margin-bottom:60px;font-size:28px">Any treatment · <b>Black Friday prices</b></div></div><div class="bow">🎀</div></div></div>
<div style="position:absolute;left:0;right:0;top:1180px;text-align:center"><div class="txt">At Black Friday prices <b>until Monday 30.11</b></div></div>''', blurbg('party_woman.jpg', 'center 25%', .28))
S['s3'] = story('''<div style="position:absolute;top:150px;left:0;right:0;text-align:center"><div class="pill">BLACK FRIDAY · NEW POST</div>
<div class="H goldtext ds" style="font-size:330px;margin-top:20px;line-height:.9">2</div><div style="font-size:44px;letter-spacing:.34em;color:#fbf3e6;font-weight:700;margin-top:8px">DAYS LEFT</div></div>
<div class="glass" style="position:absolute;left:110px;right:110px;top:800px;padding:40px;text-align:center">
<div class="txt">RF Microneedling <b>£110</b> · ElastiStrom &amp; RF <b>£130</b><br>PorCerAmid <b>£55</b> · Hydrogen Pure Glow <b>£55</b><br>Glow before Christmas <b>£75</b> · Gift vouchers 🎁</div></div>
<div style="position:absolute;left:0;right:0;top:1230px;text-align:center" class="txt">Book by <b>30.11</b> · use until <b>31.01</b></div>''', blurbg('rf_blue.jpg', 'center 30%', .32))

for k, v in {**P, **S}.items():
    open(k + '.html', 'w').write(v)
