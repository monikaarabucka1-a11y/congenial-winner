import html, pathlib
D = pathlib.Path(__file__).parent

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 210mm; height: 297mm; }
body { background: #0f0c0a; color: #efe6d8; font-family: 'Montserrat', sans-serif;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 210mm; height: 297mm; position: relative; overflow: hidden;
  background: radial-gradient(ellipse 120mm 90mm at 50% 8%, #2a2018 0%, #0f0c0a 70%); }
.frame { position: absolute; inset: 7mm; border: 0.35mm solid #b8925a; border-radius: 3mm; }
.frame::after { content: ""; position: absolute; inset: 1.4mm; border: 0.15mm solid rgba(184,146,90,.45); border-radius: 2mm; }
.inner { position: absolute; inset: 7mm; padding: PADmm; display: flex; flex-direction: column; }
.logo { display: block; margin: 0 auto; width: LOGOWmm; mix-blend-mode: screen; }
.title { text-align: center; font-family: 'Playfair Display', serif; color: #d9b67a;
  letter-spacing: .5em; text-transform: uppercase; font-size: TITLEpt; margin-top: 2mm; padding-left: .5em; }
.orn { display:flex; align-items:center; justify-content:center; gap: 3mm; color:#b8925a; margin: 2.5mm 0 MBORNmm; font-size: 8pt; }
.orn::before, .orn::after { content:""; height: .25mm; width: 28mm; background: linear-gradient(90deg, transparent, #b8925a); }
.orn::after { background: linear-gradient(270deg, transparent, #b8925a); }
h2 { font-family: 'Playfair Display', serif; font-weight: 600; color: #d9b67a; font-size: H2pt;
  letter-spacing: .14em; text-transform: uppercase; margin: H2Tmm 0 H2Bmm; display:flex; align-items:center; gap: 3mm; }
h2::after { content:""; flex: 1; height: .2mm; background: linear-gradient(90deg, #b8925a, transparent); }
.row { display: flex; align-items: baseline; gap: 2mm; margin: ROWmm 0; break-inside: avoid; }
.name { font-family: 'Playfair Display', serif; font-size: NAMEpt; color: #f6eee2; white-space: nowrap; }
.desc { font-size: DESCpt; color: #a8998a; font-weight: 400; margin: -.2mm 0 1.2mm; }
.dots { flex: 1; border-bottom: .3mm dotted rgba(184,146,90,.6); transform: translateY(-1mm); min-width: 4mm; }
.price { font-family: 'Montserrat', sans-serif; font-weight: 600; font-size: PRICEpt; color: #e2bf82; white-space: nowrap; }
.price small { font-weight: 400; color: #a8998a; font-size: .78em; margin-right: .8mm; }
.item { break-inside: avoid; }
.cols { column-count: COLS; column-gap: 10mm; }
.cols h2:first-child { margin-top: 0; }
.foot { margin-top: auto; text-align: center; font-size: FOOTpt; color: #b9aa98; letter-spacing: .06em; line-height: 1.7; }
.foot b { color: #d9b67a; font-weight: 600; }
.book { display: flex; align-items: center; gap: 8mm; margin-top: auto; padding: 5mm 7mm;
  border: .3mm solid rgba(184,146,90,.55); border-radius: 3mm; background: rgba(184,146,90,.06); }
.qr { width: 40mm; height: 40mm; background: #fff; border-radius: 2mm; padding: 1.5mm; flex: none; }
.qr img { width: 100%; height: 100%; display: block; }
.book .cta { font-family: 'Playfair Display', serif; font-size: 20pt; color: #f6eee2; line-height: 1.15; }
.book .cta em { color: #e2bf82; font-style: italic; }
.book .sub { font-size: 9pt; color: #b9aa98; margin-top: 2.5mm; line-height: 1.6; letter-spacing: .03em; }
.book .sub b { color: #d9b67a; font-weight: 600; }
.note { text-align:center; font-size: 7.5pt; color:#8d7f71; margin-top: 2.5mm; letter-spacing:.04em; }
"""

def row(name, price, desc=None):
    d = f'<div class="desc">{html.escape(desc)}</div>' if desc else ''
    return (f'<div class="item"><div class="row"><span class="name">{html.escape(name)}</span>'
            f'<span class="dots"></span><span class="price">{price}</span></div>{d}</div>')

def page(title, body, vars):
    css = CSS
    for k, v in vars.items():
        css = css.replace(k, str(v))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>{css}</style></head><body><div class="page"><div class="frame"></div><div class="inner">{body}</div></div></body></html>"""

ADDR = '5 Peckover St, Bradford BD1 5BE &nbsp;·&nbsp; 07505 779013 &nbsp;·&nbsp; elysiumclinic.uk'
HOURS = 'Tue – Fri 9:00 – 19:00 &nbsp;·&nbsp; Saturday 10:00 – 15:00'
HEAD = '<img class="logo" src="logo.png"><div class="title">Price List</div><div class="orn">✦</div>'
fr = '<small>from</small>'

# ---------- Version 1: highlights + QR ----------
s = HEAD
s += '<h2>Signature Treatments</h2>'
s += row('Eternal Radiance Ritual', '£160 <small>/ face & neck</small> £200', 'Our multi-step anti-ageing ritual: glow, firmness, hydration')
s += row('Clarity & Youth Protocol', '£130', 'For acne, pigmentation and dull skin')
s += '<h2>Advanced Skin Treatments</h2>'
s += row('Hydrogen Pure Glow', '£75')
s += row('RF Firming Lift', '£90')
s += row('OxiVelour + VivaLumix Glow', '£140')
s += row('Riviena + RF Lift', '£155')
s += row('ElastiStorm + RF Contour', '£210')
s += '<h2>Facials</h2>'
s += row('Classic Facials', f'{fr}£80')
s += row('Advanced Facials', f'{fr}£80', 'Exosomes · copper peptides · colostrum and more')
s += row('Eye Radiance', '£75')
s += '<h2>Aesthetics</h2>'
s += row('Microneedling', '£95')
s += row('Fractional RF Renewal', '£180')
s += row('Anti-wrinkle Injections', '£140 <small>· 2 areas</small>£160 <small>· 3 areas</small>£190')
s += row('Russian Lips', '£150')
s += row('Vampire Lift', '£200 <small>/ face & neck</small> £250')
s += ('<div class="book"><div class="qr"><img src="qr.jpg"></div><div>'
      '<div class="cta">Scan to <em>book online</em></div>'
      f'<div class="sub">Full treatment menu &amp; available times on Fresha<br>{HOURS}<br>{ADDR}</div></div></div>')
v1 = dict(PAD=12, LOGOW=88, TITLE=12, MBORN=3, H2=12, H2T=6, H2B=2.5, ROW=1.05, NAME=14, DESC=8.5, PRICE=13, COLS=1, FOOT=8.5)
(D/'cennik_A4_QR.html').write_text(page('Elysium Price List', s, v1))

# ---------- Version 2: full menu, no QR ----------
full = [
 ('Signature Treatments', [
   ('Elysium Eternal Radiance Ritual', '£160'), ('&nbsp;&nbsp;– Face & Neck', '£200'),
   ('Elysium Clarity & Youth Protocol', '£130')]),
 ('Advanced Treatments', [
   ('Hydrogen Pure Glow','£75'),('Diamond Radiance Peel','£70'),('OxyLuxe Infusion','£95'),
   ('Riviena Luminous Oxygen','£120'),('Riviena + RF Lift','£155'),('OxiVelour Pro Oxygen Ritual','£120'),
   ('OxiVelour + VivaLumix Glow','£140'),('SonoSilk Crystal Cleanse','£65'),('RF Firming Lift','£90'),
   ('ElastiStorm + RF Contour','£210'),('PureKio Anti-Aging','£95'),('PureKio Acne','£95'),('Vascular Calm','£40')]),
 ('Advanced Facials', [
   ('Collostrelle','£110'),('Exosensial','£140'),('Cica Care','£80'),('Cuprum60','£95'),('Epigenial','£105'),
   ('LuminAze','£90'),('Nuclevive','£100'),('RH+','£95')]),
 ('Eye Treatments', [('Eye Radiance','£75'),('Under-Eye Boost', fr+'£140')]),
 ('Hand Treatments', [('Hand Anti-Ageing Therapy','£70'),('&nbsp;&nbsp;– with injectable mesotherapy','£95')]),
 ('Scalp Treatments', [('Folli-Force','£95'),('PureKio Scalp','£95'),('PRP Scalp', fr+'£190')]),
 ('Classic Facials', [
   ('Acne Logique','£85'),('AdaptoZen','£90'),('Apitox','£95'),('Caviariste','£90'),('Champanique','£110'),
   ('Glass Skin','£90'),('LargoBTX','£95'),('Lactobionique','£80'),('Orientique','£90'),('PorCerAmid','£85'),
   ('Progelift','£100'),('Reactiv','£85'),('Retivage','£95'),('RevitaAll','£90'),('Seduction','£95'),
   ('Temptation','£100'),('VitaForce','£90')]),
 ('Aesthetics', [
   ('Chemical Peels','£70'),('Microneedling','£95'),('Fractional RF Renewal','£180'),
   ('Injectable Mesotherapy', fr+'£90'),('Lipolysis','£95'),('Russian Lips','£150'),
   ('Anti-wrinkle – 1 area','£140'),('Anti-wrinkle – 2 areas','£160'),('Anti-wrinkle – 3 areas','£190'),
   ('PRP','£160'),('PRF', fr+'£180'),('Vampire Lift – Face','£200'),('Vampire Lift – Face & Neck','£250'),
   ('Tissue Stimulators', fr+'£180')]),
]
def row2(n, p):
    return (f'<div class="item"><div class="row"><span class="name">{n}</span>'
            f'<span class="dots"></span><span class="price">{p}</span></div></div>')
s = HEAD + '<div class="cols">'
for cat, items in full:
    s += f'<div class="item"><h2>{cat}</h2>' + row2(*items[0]) + '</div>'
    s += ''.join(row2(*i) for i in items[1:])
s += '</div>'
s += f'<div class="foot"><b>{HOURS}</b><br>{ADDR}</div>'
v2 = dict(PAD=10, LOGOW=70, TITLE=10.5, MBORN=2, H2=9.5, H2T=4.6, H2B=1.6, ROW=1.15, NAME=10.2, DESC=7, PRICE=9.8, COLS=2, FOOT=8.5)
(D/'cennik_A4_pelny.html').write_text(page('Elysium Full Price List', s, v2))
