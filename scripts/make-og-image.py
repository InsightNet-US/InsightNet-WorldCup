#!/usr/bin/env python3
"""Render the 1200x630 (@2x -> 2400x1260) Open Graph share card for the
IDCUP 26 landing page, in the InsightNet brand system used by the dashboard's
og-card.html. Output: images/og-preview.png. Pillow only — no browser needed."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASH = os.path.expanduser("~/wc-risk-assessment-dashboard/assets")
OUT  = os.path.join(ROOT, "images", "og-preview.png")

SCALE = 2
def S(x): return int(round(x * SCALE))
W, H = S(1200), S(630)

# InsightNet palette
INK="#24224C"; INK_SOFT="#4F758B"; INK_FAINT="#8a9bac"; RULE="#cbd9e2"
PAPER="#eaf3f9"; ACCENT="#065D89"; ACCENT_SOFT="#5197CB"; TEAL="#5ABAB6"
def rgb(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))

LATO_BLACK="/usr/share/fonts/truetype/lato/Lato-Black.ttf"
LATO_REG ="/usr/share/fonts/truetype/lato/Lato-Regular.ttf"
PLEX_MONO=os.path.join(ROOT, ".fonts", "IBMPlexMono-Regular.ttf")
f_title=ImageFont.truetype(LATO_BLACK,S(92)); f_sub=ImageFont.truetype(LATO_REG,S(40))
f_desc =ImageFont.truetype(LATO_REG,S(25)); f_eye=ImageFont.truetype(PLEX_MONO,S(19))
f_meta =ImageFont.truetype(PLEX_MONO,S(17))

img=Image.new("RGB",(W,H),rgb(PAPER)); d=ImageDraw.Draw(img)

# --- brand gradient stripe across the top -----------------------------------
def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
stops=[(0.0,rgb(INK)),(0.38,rgb(ACCENT)),(0.70,rgb(ACCENT_SOFT)),(1.0,rgb(TEAL))]
def grad(t):
    for i in range(len(stops)-1):
        t0,c0=stops[i]; t1,c1=stops[i+1]
        if t<=t1: return lerp(c0,c1,(t-t0)/(t1-t0))
    return stops[-1][1]
for x in range(W):
    d.line([(x,0),(x,S(8))],fill=grad(x/W))

# --- floral watermark, faded, upper-right ------------------------------------
wm=Image.open(os.path.join(ROOT,"images","insightnet-watermark.png")).convert("RGBA")
nw=S(900); nh=int(nw*wm.height/wm.width); wm=wm.resize((nw,nh))
px=wm.load()
cx,cy=nw*0.5,nh*0.45; rmax=nw*0.62
for yy in range(nh):
    for xx in range(nw):
        r,g,b,a=px[xx,yy]
        if a:
            dist=((xx-cx)**2+(yy-cy)**2)**0.5
            fall=max(0.0,min(1.0,1.0-(dist-rmax*0.35)/(rmax*0.65)))
            px[xx,yy]=(r,g,b,int(min(255,a*2.4)*fall))
img.paste(wm,(W-nw+S(150),-S(120)),wm)

# --- text helpers ------------------------------------------------------------
def tracked(draw,xy,text,font,fill,track):
    x,y=xy
    for ch in text:
        draw.text((x,y),ch,font=font,fill=fill)
        x+=draw.textlength(ch,font=font)+track
    return x
def wrap(text,font,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines

PADX=S(72)
# eyebrow
y=S(60)
tracked(d,(PADX,y),"IDCUP 26  —  CDC/CFA INSIGHT NET WORKING GROUP",f_eye,rgb(ACCENT),S(3.4))
y+=S(19)+S(28)
# title
d.text((PADX,y),"FIFA World Cup 2026",font=f_title,fill=rgb(INK))
y+=S(92)+S(6)
# subtitle
d.text((PADX,y),"Infectious Disease Risk · Working Group Tools",font=f_sub,fill=rgb(INK_SOFT))
y+=S(40)+S(28)
# description
desc=("Pathogen-specific risk for the 2026 FIFA World Cup — importation, "
      "outbreak potential, and impact — with the working group's published tools.")
for ln in wrap(desc,f_desc,S(760)):
    d.text((PADX,y),ln,font=f_desc,fill=rgb(INK_SOFT)); y+=int(S(25)*1.45)

# --- footer: hairline + meta (left) + InsightNet logo (right) ----------------
BOTTOM=H-S(60)
rule_y=BOTTOM-S(64)
d.line([(PADX,rule_y),(W-PADX,rule_y)],fill=rgb(RULE),width=S(1))
meta="2 PUBLISHED TOOLS  ·  ACCIDDA × EPISTORM × FORESITE"
mh=f_meta.getbbox(meta)[3]
tracked(d,(PADX,BOTTOM-mh),meta,f_meta,rgb(INK_FAINT),S(2))
try:
    logo=Image.open(os.path.join(DASH,"insight-net.png")).convert("RGBA")
    lh=S(40); lw=int(lh*logo.width/logo.height); logo=logo.resize((lw,lh))
    img.paste(logo,(W-PADX-lw,BOTTOM-lh),logo)
except Exception as e:
    print("logo skipped:",e)

img.save(OUT)
print("wrote",OUT,img.size,f"{os.path.getsize(OUT):,} bytes")
