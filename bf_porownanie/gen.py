T=[
("RF Microneedling","£180","£110","Micro-needles + radiofrequency heat deep in the skin",
 ["Stimulates new collagen & elastin","Smooths fine lines, acne scars & pores","Firms and refines skin texture"],
 "Lines · scars · texture","1–2 days light redness","Build over 4–6 weeks","RF"),
("ElastiStorm & RF Contour","£210","£130","Muscle stimulation + RF heat. No needles",
 ["Tones facial muscles from within","Tightens skin, defines jawline & neck","Boosts lymphatic drainage"],
 "Jawline · firmness · neck","None","Visible lift after 1st session","LIFT"),
("PorCerAmid","£85","£55","Ceramide treatment that rebuilds your skin barrier",
 ["Deep, long-lasting hydration","Calms dryness, tightness & redness","Smooth, porcelain finish"],
 "Dry · sensitive · winter skin","None","Instant smoothness","CERAMID"),
("Hydrogen Pure Glow","£75","£55","Hydrogen deep cleanse, exfoliation & hydration",
 ["Unclogs and refines pores","Evens out skin tone","Instant, healthy glow"],
 "Dull skin · congested pores","None","Glow straight away","GLOW"),
]
import sys
def row(t,story):
    n,o,p,d,b,best,down,res,kw=t
    bl=''.join(f'<li>{x}</li>' for x in b)
    return f'''<div class="row glass"><div class="hd"><div><div class="nm serif goldtext">{n}</div><div class="ds">{d}</div></div>
<div class="pr"><s>{o}</s><b class="serif goldtext">{p}</b></div></div>
<div class="bd"><ul>{bl}</ul><div class="meta"><div><i>BEST FOR</i>{best}</div><div><i>DOWNTIME</i>{down}</div><div><i>RESULTS</i>{res}</div></div></div>
<div class="kw">DM “{kw}”</div></div>'''
for story,H,out in [(False,1350,'bf_comparison_post.html'),(True,1920,'bf_comparison_story.html')]:
    css=open('style.css').read().replace('__H__',str(H))
    rows=''.join(row(t,story) for t in T)
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600;1,700&family=Montserrat:wght@400;500;600;700&display=block" rel="stylesheet"><link rel="stylesheet" href="common.css"><style>{css}</style></head>
<body class="{'story' if story else 'post'}"><div class="s"><div class="deco"></div><div class="spark" style="left:930px;top:{60 if not story else 150}px;font-size:30px">✦</div>
<div class="top"><div class="pill">BLACK FRIDAY · UNTIL 30.11</div><div class="h serif goldtext">Which treatment <em>is for you?</em></div></div>
<div class="rows">{rows}</div>
<div class="foot">Not sure? Send <b>“BF”</b> and we’ll match you with the right one.</div>
<div class="logo"><img src="logo.png"></div></div></body></html>'''
    open(out,'w').write(html)
