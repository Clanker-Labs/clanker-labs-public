#!/usr/bin/env python3
"""Render the demo animations from real output captured on a running box.

Not mockups. Every line these play back was produced by the actual scripts on
the actual machine — `make checks` really does print those eleven rows, and the
agent really did file that idea. The only edits are redactions: a tailnet
hostname and a home directory are not things to publish on a page anyone can
read, so they are replaced with obvious placeholders rather than blurred.

Two scenes, because they are the two halves of the pitch that are hard to
believe without seeing:

  checks  — the box tests itself, and says so plainly when it is broken. The
            recording deliberately keeps the three failures in. A demo where
            everything passes is a demo nobody trusts, and "the drive is not
            mounted" is a better advertisement for the checks than a green wall.

  agent   — a sentence typed into Telegram becomes a row in a database, with no
            app opened. That is the whole point of the agent layer and it takes
            nine seconds to show.

Porchlight tokens throughout (see the branding repo). The older promo.py in this
directory predates the brand and uses a different orange; it has not been
retrofitted because regenerating it would change a file nobody asked to change.

Usage:  python3 tools/demos.py <scene> <outdir>      # scene: checks | agent
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1000, 620
FPS = 20

# --- Porchlight -------------------------------------------------------------
BG       = (0x10, 0x12, 0x11)
RAISED   = (0x18, 0x1b, 0x19)
LINE     = (0x27, 0x2b, 0x28)
HEADING  = (0xe9, 0xeb, 0xe7)
BODY     = (0xa9, 0xae, 0xa8)
#: One step up from the panel. RAISED is the window's own fill, so a bubble
#: painted in it is a bubble you cannot see -- the first render had the incoming
#: messages reading as loose text floating in the frame.
BUBBLE   = (0x23, 0x27, 0x24)
MUTED    = (0x7e, 0x84, 0x7e)
FAINT    = (0x63, 0x69, 0x63)
ACCENT   = (0xe7, 0x9a, 0x4b)
UP       = (0x6f, 0xbf, 0x8b)
DOWN     = (0xd4, 0x69, 0x5f)


def font(size, bold=False):
    """JetBrains Mono is the brand face; DejaVu stands in when it is absent.

    Both are monospace at the same nominal size, so a layout that fits in one
    fits in the other -- which is why nothing here measures text to place it.
    """
    for path in (
        "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-%s.ttf"
        % ("Bold" if bold else "Regular"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono%s.ttf"
        % ("-Bold" if bold else ""),
    ):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


F_H   = font(21, bold=True)
F     = font(17)
F_B   = font(17, bold=True)
F_SM  = font(14)
F_TAG = font(13, bold=True)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def chrome(draw, title):
    """The window the scene plays inside."""
    draw.rectangle([0, 0, W, H], fill=BG)
    draw.rounded_rectangle([28, 26, W - 28, H - 26], 12, fill=RAISED, outline=LINE, width=1)
    draw.line([28, 68, W - 28, 68], fill=LINE, width=1)
    for i, colour in enumerate((DOWN, ACCENT, UP)):
        draw.ellipse([52 + i * 20, 41, 63 + i * 20, 52], fill=colour)
    draw.text((124, 39), title, font=F_SM, fill=FAINT)


def typed(draw, x, y, prompt, command, progress, cursor_on):
    """A command being typed, one character at a time."""
    draw.text((x, y), prompt, font=F_B, fill=ACCENT)
    shown = command[: int(len(command) * ease(progress))]
    draw.text((x + 26, y), shown, font=F_B, fill=HEADING)
    if cursor_on and progress < 1.0:
        w = draw.textlength(shown, font=F_B)
        draw.rectangle([x + 26 + w + 2, y, x + 26 + w + 11, y + 19], fill=ACCENT)


# ---------------------------------------------------------------------------
# Scene: checks
# ---------------------------------------------------------------------------
# Verbatim from `bash scripts/92-checks.sh`, with the tailnet host and the home
# path replaced. The failures are real and are kept.
CHECKS = [
    ("ok",   "agent-answers",      "replied in 4s: pong"),
    ("ok",   "mcp-jinsen",         "answering on :8093 (HTTP 406)"),
    ("ok",   "mcp-chezmoi",        "answering on :8092 (HTTP 406)"),
    ("ok",   "gateway-models",     "8 models at http://spark.<tailnet>:8000/v1"),
    ("fail", "gateway-tools",      "model answered in TEXT instead of calling the tool"),
    ("fail", "media-drive",        "the drive is NOT mounted — resolves to /"),
    ("ok",   "disk-root",          "/ is 79% full"),
    ("ok",   "containers-healthy", "no container reports unhealthy"),
    ("ok",   "containers-stable",  "nothing is in a restart loop"),
    ("fail", "datastores-private", "reachable from the tailnet: 2 ports"),
    ("ok",   "backups",            "most recent backup is 14h old"),
]


def scene_checks(out):
    type_frames, per_row, tail = 26, 7, 46
    total = type_frames + len(CHECKS) * per_row + tail
    for f in range(total):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        chrome(d, "make checks")
        typed(d, 56, 96, "$", "make checks", f / type_frames, (f // 6) % 2 == 0)

        shown = max(0, (f - type_frames) // per_row)
        y = 138
        for i, (status, name, detail) in enumerate(CHECKS[:shown]):
            # The newest row fades in rather than appearing, so the eye can
            # follow which line just arrived.
            age = (f - type_frames - i * per_row) / per_row
            t = ease(min(1.0, age))
            mark, colour = ("✓", UP) if status == "ok" else ("✕", DOWN)
            def fade(c):
                return tuple(int(BG[j] + (c[j] - BG[j]) * t) for j in range(3))
            d.text((60, y), mark, font=F_B, fill=fade(colour))
            d.text((88, y), name, font=F, fill=fade(HEADING if status == "ok" else DOWN))
            d.text((312, y), detail, font=F_SM, fill=fade(MUTED))
            y += 30

        if shown >= len(CHECKS):
            t = ease(min(1.0, (f - type_frames - len(CHECKS) * per_row) / 14))
            def fade(c):
                return tuple(int(BG[j] + (c[j] - BG[j]) * t) for j in range(3))
            d.line([56, y + 10, W - 56, y + 10], fill=fade(LINE), width=1)
            d.text((60, y + 26), "3 failing", font=F_B, fill=fade(DOWN))
            d.text((176, y + 26),
                   "— reported to Telegram, and the healer gets a shot at them at 07:15",
                   font=F_SM, fill=fade(MUTED))
        img.save(os.path.join(out, "f%04d.png" % f))
    return total


# ---------------------------------------------------------------------------
# Scene: agent
# ---------------------------------------------------------------------------
# The real exchange. The reply is what LeClanker actually sent back.
CONVO = [
    ("in",  "I had an idea: a solar-powered weather station"),
    ("in",  "for the garden that logs to Jinsen. Capture it."),
    ("act", "jinsen_idea_add"),
    ("out", "Your idea for a solar-powered garden weather"),
    ("out", "station has been captured and is now being"),
    ("out", "researched by Jinsen."),
]


def scene_agent(out):
    hold, per, tail = 16, 22, 60
    total = hold + len(CONVO) * per + tail
    for f in range(total):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        chrome(d, "telegram → LeClanker → jinsen")

        shown = max(0, (f - hold) // per)
        y = 108
        for i, (kind, text) in enumerate(CONVO[:shown + 1]):
            if i > shown:
                break
            t = ease(min(1.0, (f - hold - i * per) / (per * 0.6)))
            if t <= 0:
                continue
            def fade(c, mul=1.0):
                return tuple(int(BG[j] + (c[j] - BG[j]) * t * mul) for j in range(3))

            if kind == "in":
                d.rounded_rectangle([60, y - 8, 640, y + 26], 8,
                                    fill=fade(BUBBLE), outline=fade(LINE), width=1)
                d.text((78, y), text, font=F, fill=fade(BODY))
                y += 44
            elif kind == "act":
                # The tool call is the moment worth showing: this is where a
                # sentence stops being chat and becomes a row in a database.
                d.rounded_rectangle([60, y - 6, 60 + 300, y + 26], 8,
                                    fill=fade((0x22, 0x1c, 0x12)), outline=fade(ACCENT), width=1)
                d.text((78, y), "→ " + text, font=F_B, fill=fade(ACCENT))
                y += 52
            else:
                d.text((78, y), text, font=F, fill=fade(HEADING))
                y += 28

        if shown >= len(CONVO) - 1:
            t = ease(min(1.0, (f - hold - len(CONVO) * per) / 18))
            if t > 0:
                def fade(c):
                    return tuple(int(BG[j] + (c[j] - BG[j]) * t) for j in range(3))
                by = H - 150
                d.line([56, by - 22, W - 56, by - 22], fill=fade(LINE), width=1)
                d.text((60, by), "jinsen-ideas", font=F_TAG, fill=fade(FAINT))
                d.rounded_rectangle([60, by + 24, W - 60, by + 78], 8,
                                    fill=fade(RAISED), outline=fade(LINE), width=1)
                d.text((78, by + 38), "#3", font=F_B, fill=fade(FAINT))
                d.text((120, by + 38), "Solar-powered garden weather station",
                       font=F_B, fill=fade(HEADING))
                d.text((W - 210, by + 38), "analysing", font=F_SM, fill=fade(ACCENT))
        img.save(os.path.join(out, "f%04d.png" % f))
    return total


SCENES = {"checks": scene_checks, "agent": scene_agent}

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in SCENES:
        sys.exit("usage: demos.py {%s} <outdir>" % "|".join(SCENES))
    outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    n = SCENES[sys.argv[1]](outdir)
    print("%d frames -> %s (%.1fs at %d fps)" % (n, outdir, n / FPS, FPS))
