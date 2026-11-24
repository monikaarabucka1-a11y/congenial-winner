# Generates a realistic-looking skin cross-section (healthy vs damaged barrier) as SVG.
import random, math
random.seed(11)
PW, GAP = 440, 40
W = PW * 2 + GAP
TOP_BACK, TOP_FRONT = 40, 120      # top face (skin surface) y back / front
SC0, SC1 = TOP_FRONT, 270            # stratum corneum
EP1 = 420                            # epidermis bottom (wavy)
BOT = 600
H = BOT + 10
DEPTH = 34                            # perspective inset of top face

def f(v): return f'{v:.1f}'

def defs():
    return f'''<defs>
<linearGradient id="lip" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbe6bd"/><stop offset=".5" stop-color="#e6b46c"/><stop offset="1" stop-color="#c38a45"/></linearGradient>
<linearGradient id="corneo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6dcc6"/><stop offset="1" stop-color="#ddb08f"/></linearGradient>
<linearGradient id="corneoD" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dcc6b3"/><stop offset="1" stop-color="#b9977c"/></linearGradient>
<linearGradient id="epi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f0c7ad"/><stop offset="1" stop-color="#e3ab90"/></linearGradient>
<linearGradient id="derm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9a99a"/><stop offset="1" stop-color="#c97d71"/></linearGradient>
<linearGradient id="surf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9c1a3"/><stop offset="1" stop-color="#f6d8c0"/></linearGradient>
<linearGradient id="surfD" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfae95"/><stop offset="1" stop-color="#e0c2aa"/></linearGradient>
<radialGradient id="water" cx=".35" cy=".35" r=".8"><stop offset="0" stop-color="#ffffff"/><stop offset=".35" stop-color="#d4ecf9"/><stop offset="1" stop-color="#5fa9d6"/></radialGradient>
<radialGradient id="cellg" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#f9dccb"/><stop offset="1" stop-color="#e2a88e"/></radialGradient>
<filter id="pores" x="0" y="0" width="100%" height="100%">
 <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="3" result="n"/>
 <feDiffuseLighting in="n" surfaceScale="1.6" lighting-color="#fff1e4" result="l"><feDistantLight azimuth="235" elevation="55"/></feDiffuseLighting>
 <feComposite in="l" in2="SourceGraphic" operator="in" result="lc"/>
 <feBlend in="SourceGraphic" in2="lc" mode="multiply"/>
</filter>
<filter id="poresD" x="0" y="0" width="100%" height="100%">
 <feTurbulence type="fractalNoise" baseFrequency="0.55" numOctaves="4" seed="8" result="n"/>
 <feDiffuseLighting in="n" surfaceScale="3.2" lighting-color="#f3e2d2" result="l"><feDistantLight azimuth="235" elevation="45"/></feDiffuseLighting>
 <feComposite in="l" in2="SourceGraphic" operator="in" result="lc"/>
 <feBlend in="SourceGraphic" in2="lc" mode="multiply"/>
</filter>
<filter id="soft"><feGaussianBlur stdDeviation="1.4"/></filter>
<filter id="sh" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="#000" flood-opacity=".35"/></filter>
<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="rgba(255,255,255,0)"/><stop offset=".45" stop-color="rgba(255,255,255,.35)"/><stop offset=".6" stop-color="rgba(255,255,255,0)"/></linearGradient>
</defs>'''

def drop(x, y, s=1.0, op=1.0, blur=False):
    return (f'<g transform="translate({f(x)},{f(y)}) scale({s})" opacity="{op}" {"filter=\"url(#soft)\"" if blur else ""}>'
            '<path d="M0,-30 C9,-14 19,-2 19,10 A19,19 0 1 1 -19,10 C-19,-2 -9,-14 0,-30Z" fill="url(#water)" stroke="rgba(255,255,255,.6)" stroke-width="1.4"/>'
            '<ellipse cx="-6" cy="5" rx="4.5" ry="8" fill="rgba(255,255,255,.8)" transform="rotate(20 -6 5)"/></g>')

def wavy(x0, x1, y, amp, n, phase=0):
    pts = []
    for i in range(0, 61):
        x = x0 + (x1 - x0) * i / 60
        pts.append((x, y + amp * math.sin(phase + i / 60 * n * 2 * math.pi)))
    return pts

def panel(ox, damaged):
    o = []
    clip = f'clip{int(damaged)}'
    # wavy dermal-epidermal junction
    jn = wavy(ox, ox + PW, EP1, 16, 4.5, 0.6 if damaged else 0)
    o.append(f'<clipPath id="{clip}"><rect x="{ox}" y="{SC0}" width="{PW}" height="{BOT-SC0}"/></clipPath>')
    o.append(f'<g clip-path="url(#{clip})">')
    # dermis
    o.append(f'<rect x="{ox}" y="{SC0}" width="{PW}" height="{BOT-SC0}" fill="url(#derm)"/>')
    for i in range(9):   # collagen fibres
        y = EP1 + 30 + i * 18 + random.uniform(-4, 4)
        d = 'M' + ' L'.join(f'{f(x)},{f(yy)}' for x, yy in wavy(ox - 10, ox + PW + 10, y, random.uniform(4, 8), random.uniform(2.5, 4), random.uniform(0, 6)))
        o.append(f'<path d="{d}" stroke="rgba(255,226,214,.55)" stroke-width="{random.uniform(4,7):.1f}" fill="none" stroke-linecap="round"/>')
    for k in range(2):   # capillaries
        cx = ox + 90 + k * 230
        o.append(f'<path d="M{cx},{BOT} C{cx-20},{EP1+90} {cx+30},{EP1+60} {cx+5},{EP1+20} C{cx-10},{EP1+5} {cx+25},{EP1} {cx+30},{EP1+40} C{cx+35},{EP1+80} {cx+70},{EP1+120} {cx+60},{BOT}" stroke="#b5413e" stroke-width="5" fill="none" opacity=".75"/>')
    # epidermis (above junction)
    ep = f'M{ox},{SC1} L{ox+PW},{SC1} L{ox+PW},{f(jn[-1][1])} ' + ' '.join(f'L{f(x)},{f(y)}' for x, y in reversed(jn)) + ' Z'
    o.append(f'<path d="{ep}" fill="url(#epi)"/>')
    # keratinocytes
    for r in range(5):
        y = SC1 + 18 + r * 30
        x = ox + (0 if r % 2 else 16)
        while x < ox + PW:
            rr = random.uniform(13, 17) - r * 0.6
            o.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rr*1.25)}" ry="{f(rr*(1-r*0.06))}" fill="url(#cellg)" stroke="rgba(160,95,75,.35)" stroke-width="1.2"/>')
            o.append(f'<circle cx="{f(x+2)}" cy="{f(y+1)}" r="{f(rr*0.32)}" fill="rgba(150,80,90,.45)"/>')
            x += rr * 2.7
    # stratum corneum
    if not damaged:
        o.append(f'<rect x="{ox}" y="{SC0}" width="{PW}" height="{SC1-SC0}" fill="url(#lip)"/>')
    else:
        o.append(f'<rect x="{ox}" y="{SC0}" width="{PW}" height="{SC1-SC0}" fill="#5b4536"/>')
    rows = 6; rh = (SC1 - SC0 - 6) / rows
    for r in range(rows):
        y = SC0 + 4 + r * rh
        x = ox - (40 if r % 2 else 0)
        while x < ox + PW:
            w = random.uniform(70, 96)
            h = rh - (5 if not damaged else 9)
            dx = dy = rot = 0
            if damaged:
                dy = random.uniform(-3, 3); rot = random.uniform(-6, 6); w -= random.uniform(6, 16)
                if r == 0 and random.random() < .5: dy -= random.uniform(6, 14); rot += random.uniform(-10, 10)
            cx, cy = x + w / 2, y + dy + h / 2
            p = f'M{f(x+8)},{f(y+dy)} L{f(x+w-8)},{f(y+dy)} L{f(x+w)},{f(cy)} L{f(x+w-8)},{f(y+dy+h)} L{f(x+8)},{f(y+dy+h)} L{f(x)},{f(cy)} Z'
            o.append(f'<path d="{p}" fill="url(#{"corneoD" if damaged else "corneo"})" stroke="rgba(150,100,70,.45)" stroke-width="1" transform="rotate({f(rot)} {f(cx)} {f(cy)})"/>')
            x += w + (6 if not damaged else 12)
        if not damaged:  # lipid lamellae lines in the gap below each row
            gy = y + rh - 2.5
            o.append(f'<path d="M{ox},{f(gy-1.2)} H{ox+PW}" stroke="rgba(255,244,214,.85)" stroke-width="1"/>')
            o.append(f'<path d="M{ox},{f(gy+1.2)} H{ox+PW}" stroke="rgba(255,244,214,.55)" stroke-width="1"/>')
    # water
    if not damaged:
        for (x, y, s) in [(70, 170, .5), (250, 205, .45), (360, 160, .42), (150, 330, .5), (330, 360, .45)]:
            o.append(drop(ox + x, y, s, .95))
    o.append('</g>')
    # top face (skin surface) in perspective
    tl, tr = (ox, TOP_FRONT), (ox + PW, TOP_FRONT)
    br, bl = (ox + PW - DEPTH, TOP_BACK), (ox + DEPTH, TOP_BACK)
    face = f'M{tl[0]},{tl[1]} L{tr[0]},{tr[1]} L{br[0]},{br[1]} L{bl[0]},{bl[1]} Z'
    o.append(f'<clipPath id="face{int(damaged)}"><path d="{face}"/></clipPath>')
    o.append(f'<g clip-path="url(#face{int(damaged)})"><rect x="{ox}" y="{TOP_BACK}" width="{PW}" height="{TOP_FRONT-TOP_BACK}" fill="url(#{"surfD" if damaged else "surf"})" filter="url(#{"poresD" if damaged else "pores"})"/>')
    if not damaged:
        o.append(f'<rect x="{ox}" y="{TOP_BACK}" width="{PW}" height="{TOP_FRONT-TOP_BACK}" fill="url(#sheen)" opacity=".9"/>')
    else:
        for i in range(7):
            x = ox + random.uniform(40, PW - 60); y = random.uniform(TOP_BACK + 10, TOP_FRONT - 12)
            o.append(f'<path d="M{f(x)},{f(y)} l{random.uniform(10,20):.0f},{random.uniform(-6,6):.0f} l{random.uniform(8,16):.0f},{random.uniform(-6,6):.0f}" stroke="rgba(90,60,40,.7)" stroke-width="1.6" fill="none"/>')
    o.append('</g>')
    o.append(f'<path d="{face}" fill="none" stroke="rgba(255,240,220,.35)" stroke-width="1"/>')
    if damaged:  # lifted dry flakes
        for i in range(6):
            x = ox + random.uniform(50, PW - 70); y = random.uniform(TOP_BACK + 8, TOP_FRONT - 18)
            w = random.uniform(22, 38)
            o.append(f'<path d="M{f(x)},{f(y)} l{f(w)},{random.uniform(-4,2):.0f} l{random.uniform(-6,-2):.0f},{random.uniform(8,12):.0f} l{f(-w+4)},{random.uniform(0,3):.0f} Z" fill="#efdccb" stroke="rgba(120,90,70,.6)" stroke-width="1" filter="url(#sh)" transform="rotate({random.uniform(-12,12):.0f} {f(x)} {f(y)})"/>')
        for (x, y, s, op) in [(90, 20, .5, .9), (210, -15, .42, .75), (330, 5, .46, .8), (150, -55, .34, .5), (280, -80, .3, .4), (380, -45, .28, .35)]:
            o.append(drop(ox + x, y, s, op, True))
            o.append(f'<path d="M{ox+x},{f(y+20)} v22" stroke="rgba(212,236,249,{op*.6:.2f})" stroke-width="2" stroke-dasharray="3 5"/>')
    # front-face outline
    o.append(f'<rect x="{ox}" y="{SC0}" width="{PW}" height="{BOT-SC0}" fill="none" stroke="{"rgba(246,220,174,.8)" if not damaged else "rgba(185,165,140,.5)"}" stroke-width="2"/>')
    return o

def build():
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H+90}" viewBox="0 -90 {W} {H+90}">', defs()]
    s += panel(0, False)
    s += panel(PW + GAP, True)
    s.append('</svg>')
    return '\n'.join(s)

if __name__ == '__main__':
    open('skin_svg.svg', 'w').write(build())
    print(W, H + 90)
