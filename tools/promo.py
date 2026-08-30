#!/usr/bin/env python3
"""Generate the Clanker Labs promo animation frames."""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1000, 562
FPS = 20
OUT = sys.argv[1] if len(sys.argv) > 1 else "frames"
os.makedirs(OUT, exist_ok=True)

# Chain Teal, as RGB byte tuples for Pillow — see Clanker-Labs/branding.
# This file used to carry a third palette (GitHub greys under "clanker orange")
# that predated the brand system entirely.
BG = (0x0F, 0x14, 0x19)      # --color-bg
PANEL = (0x17, 0x1D, 0x26)   # --color-bg-raised
FG = (0xE8, 0xED, 0xF2)      # --color-heading
DIM = (0x7C, 0x88, 0x96)     # --color-muted
ACC = (0x00, 0xD4, 0xAA)     # --color-accent
ACC2 = (0x00, 0xA8, 0x88)    # --color-accent-dim
OK = (0x4A, 0xDE, 0x80)      # --color-up

FONTS = "/home/wardn/.local/share/fonts/"
def font(name, size):
    for p in (FONTS + name, "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()

F_TITLE = font("JetBrainsMonoNerdFont-ExtraBold.ttf", 54)
F_TAG   = font("JetBrainsMonoNerdFont-Regular.ttf", 21)
F_MONO  = font("JetBrainsMonoNerdFont-Regular.ttf", 19)
F_BOLD  = font("JetBrainsMonoNerdFont-Bold.ttf", 19)
F_SM    = font("JetBrainsMonoNerdFont-Regular.ttf", 15)
F_CARD  = font("JetBrainsMonoNerdFont-Bold.ttf", 17)
F_CARDD = font("JetBrainsMonoNerdFont-Regular.ttf", 13)

PRODUCTS = [
    ("setup",            "provision any machine",      ACC2),
    ("chezmoi",          "deploy the whole stack",     ACC2),
    ("LeHarness",        "serve local LLMs",           ACC),
    ("LeClanker",        "the agent that runs it",     ACC),
    ("selfkey",          "credentials, encrypted",     OK),
    ("selfmail",         "mail relay at home",         OK),
    ("selflix",          "your media, streamed",       OK),
    ("clanked-obsidian", "notes, agent-readable",     OK),
]

LOG = [
    ("setup",     "provisioning nuc-01 ......", "docker · uv · node · dotfiles"),
    ("chezmoi",   "deploying stack .........", "8 services · reverse proxy · tailnet"),
    ("LeHarness", "detecting hardware ......", "1x RTX 4090 -> vLLM · TP=1 · FP16"),
    ("LeClanker", "waking the agent ........", "langgraph · mcp · subagents"),
]


def ease(t):
    return t * t * (3 - 2 * t)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def blend(c1, c2, t):
    t = clamp(t)
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def grid(d, alpha=1.0):
    col = blend(BG, (30, 36, 46), alpha)
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=col)
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=col)


def glow_dot(d, x, y, r, col, a=1.0):
    for i in range(4, 0, -1):
        d.ellipse([x - r * i, y - r * i, x + r * i, y + r * i],
                  fill=blend(BG, col, a * 0.12 / i))
    d.ellipse([x - r, y - r, x + r, y + r], fill=blend(BG, col, a))


def rrect(d, box, rad, fill, outline=None, w=1):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline, width=w)


def draw_logo(d, cx, cy, s, a=1.0):
    """Bracket-and-core mark."""
    col = blend(BG, ACC, a)
    col2 = blend(BG, ACC2, a)
    d.line([(cx - s, cy - s * 0.75), (cx - s * 1.35, cy), (cx - s, cy + s * 0.75)],
           fill=col, width=max(2, int(s * 0.13)), joint="curve")
    d.line([(cx + s, cy - s * 0.75), (cx + s * 1.35, cy), (cx + s, cy + s * 0.75)],
           fill=col, width=max(2, int(s * 0.13)), joint="curve")
    d.ellipse([cx - s * 0.34, cy - s * 0.34, cx + s * 0.34, cy + s * 0.34], fill=col2)
    d.ellipse([cx - s * 0.14, cy - s * 0.14, cx + s * 0.14, cy + s * 0.14], fill=(255, 255, 255))


def scene_intro(d, t):
    """0.0 - 2.2s : mark + wordmark."""
    grid(d, ease(clamp(t / 0.8)))
    a = ease(clamp((t - 0.15) / 0.6))
    cy = H // 2 - 40
    draw_logo(d, W // 2, cy - 46, 34, a)
    tw = d.textlength("CLANKER LABS", font=F_TITLE)
    slide = (1 - ease(clamp((t - 0.4) / 0.7))) * 18
    d.text((W // 2 - tw / 2, cy + 12 + slide), "CLANKER LABS",
           font=F_TITLE, fill=blend(BG, (240, 246, 252), ease(clamp((t - 0.4) / 0.7))))
    a2 = ease(clamp((t - 0.9) / 0.6))
    tag = "self-host your home.  let the agent run it."
    tw2 = d.textlength(tag, font=F_TAG)
    d.text((W // 2 - tw2 / 2, cy + 84), tag, font=F_TAG, fill=blend(BG, DIM, a2))
    if a2 > 0.2:
        y = cy + 122
        wln = 150 * ease(clamp((t - 1.1) / 0.7))
        d.line([(W // 2 - wln, y), (W // 2 + wln, y)], fill=blend(BG, ACC, a2 * 0.8), width=2)


def scene_terminal(d, t):
    """2.2 - 8.0s : provisioning log."""
    grid(d, 1.0)
    a = ease(clamp(t / 0.45))
    bx, by, bw, bh = 90, 66, W - 180, H - 132
    rrect(d, [bx, by, bx + bw, by + bh], 12, blend(BG, PANEL, a),
          outline=blend(BG, (48, 54, 61), a), w=1)
    rrect(d, [bx, by, bx + bw, by + 38], 12, blend(BG, (28, 33, 40), a))
    d.rectangle([bx, by + 26, bx + bw, by + 38], fill=blend(BG, (28, 33, 40), a))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([bx + 16 + i * 20, by + 13, bx + 26 + i * 20, by + 23],
                  fill=blend(BG, c, a))
    ttl = "clanker up --host nuc-01"
    d.text((bx + bw / 2 - d.textlength(ttl, font=F_SM) / 2, by + 11), ttl,
           font=F_SM, fill=blend(BG, DIM, a))

    x, y = bx + 26, by + 62
    d.text((x, y), "$", font=F_BOLD, fill=blend(BG, OK, a))
    cmd = "clanker up --host nuc-01"
    n = int(clamp((t - 0.35) / 0.9) * len(cmd))
    d.text((x + 20, y), cmd[:n], font=F_MONO, fill=blend(BG, FG, a))
    if n < len(cmd) and int(t * 6) % 2 == 0:
        cw = d.textlength(cmd[:n], font=F_MONO)
        d.rectangle([x + 21 + cw, y + 2, x + 30 + cw, y + 21], fill=ACC)

    y += 42
    for i, (name, action, detail) in enumerate(LOG):
        st = 1.5 + i * 0.85
        if t < st:
            continue
        la = ease(clamp((t - st) / 0.3))
        done = t > st + 0.55
        row = y + i * 58
        col = PRODUCTS[[p[0] for p in PRODUCTS].index(name)][2]
        if done:
            d.text((x, row), "✓", font=F_BOLD, fill=blend(BG, OK, la))
        else:
            ang = (t - st) * 9
            r = 7
            cxp, cyp = x + 7, row + 11
            for k in range(3):
                aa = ang + k * 2.1
                d.ellipse([cxp + math.cos(aa) * r - 2, cyp + math.sin(aa) * r - 2,
                           cxp + math.cos(aa) * r + 2, cyp + math.sin(aa) * r + 2],
                          fill=blend(BG, ACC, la * (1 - k * 0.28)))
        d.text((x + 30, row), name, font=F_BOLD, fill=blend(BG, col, la))
        nx = x + 30 + d.textlength(name, font=F_BOLD) + 14
        d.text((nx, row), action, font=F_MONO, fill=blend(BG, DIM, la))
        if done:
            da = ease(clamp((t - st - 0.55) / 0.3))
            d.text((x + 30, row + 25), detail, font=F_SM, fill=blend(BG, (125, 133, 144), da))

    # closing summary
    ft = 1.5 + len(LOG) * 0.85 + 0.5
    if t > ft:
        fa = ease(clamp((t - ft) / 0.4))
        row = y + len(LOG) * 58 + 6
        d.line([(x, row - 10), (bx + bw - 26, row - 10)],
               fill=blend(BG, (48, 54, 61), fa))
        d.text((x, row + 6), "→", font=F_BOLD, fill=blend(BG, ACC, fa))
        d.text((x + 30, row + 6), "8 services up", font=F_BOLD, fill=blend(BG, FG, fa))
        sx = x + 30 + d.textlength("8 services up", font=F_BOLD) + 12
        d.text((sx, row + 6), "· tailnet-only · 0 cloud accounts",
               font=F_MONO, fill=blend(BG, DIM, fa))
        if int(t * 3) % 2 == 0:
            cw2 = d.textlength("· tailnet-only · 0 cloud accounts", font=F_MONO)
            d.rectangle([sx + cw2 + 10, row + 8, sx + cw2 + 19, row + 27],
                        fill=blend(BG, ACC, fa))


def scene_grid(d, t):
    """8.0 - 12.0s : product grid."""
    grid(d, 1.0)
    a = ease(clamp(t / 0.4))
    draw_logo(d, 62, 56, 20, a)
    d.text((100, 36), "CLANKER LABS", font=font("JetBrainsMonoNerdFont-ExtraBold.ttf", 27),
           fill=blend(BG, (240, 246, 252), a))
    d.text((102, 68), "one stack. your hardware. your data.",
           font=F_SM, fill=blend(BG, DIM, a))

    cols, cw, ch, gap = 4, 212, 96, 18
    ox = (W - (cols * cw + (cols - 1) * gap)) // 2
    oy = 128
    for i, (name, desc, col) in enumerate(PRODUCTS):
        st = 0.25 + i * 0.11
        if t < st:
            continue
        ca = ease(clamp((t - st) / 0.4))
        cx0 = ox + (i % cols) * (cw + gap)
        cy0 = oy + (i // cols) * (ch + gap) + (1 - ca) * 14
        rrect(d, [cx0, cy0, cx0 + cw, cy0 + ch], 10,
              blend(BG, PANEL, ca), outline=blend(BG, (48, 54, 61), ca), w=1)
        d.line([(cx0, cy0 + 10), (cx0, cy0 + ch - 10)], fill=blend(BG, col, ca), width=3)
        glow_dot(d, cx0 + 26, cy0 + 30, 4, col, ca)
        d.text((cx0 + 44, cy0 + 21), name, font=F_CARD, fill=blend(BG, FG, ca))
        d.text((cx0 + 20, cy0 + 56), desc, font=F_CARDD, fill=blend(BG, (125, 133, 144), ca))

    fa = ease(clamp((t - 1.5) / 0.6))
    foot = "github.com/Clanker-Labs"
    d.text((W / 2 - d.textlength(foot, font=F_MONO) / 2, H - 52), foot,
           font=F_MONO, fill=blend(BG, ACC, fa))


SCENES = [(2.2, scene_intro), (6.0, scene_terminal), (4.2, scene_grid)]
TOTAL = sum(s[0] for s in SCENES)


def render(i):
    t = i / FPS
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    acc = 0.0
    for dur, fn in SCENES:
        if t < acc + dur:
            local = t - acc
            fn(d, local)
            # cross-fade tail
            tail = acc + dur - t
            if tail < 0.3 and fn is not SCENES[-1][1]:
                k = 1 - tail / 0.3
                ov = Image.new("RGB", (W, H), BG)
                img = Image.blend(img, ov, k * 0.9)
            break
        acc += dur
    else:
        SCENES[-1][1](d, SCENES[-1][0] - 0.01)
    return img


total_frames = int(TOTAL * FPS)
for i in range(total_frames):
    render(i).save(f"{OUT}/f{i:04d}.png")
print(f"{total_frames} frames -> {OUT}  ({TOTAL:.1f}s @ {FPS}fps)")
