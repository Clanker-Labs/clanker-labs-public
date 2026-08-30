# clanker-labs-public

The public site for [Clanker Labs](https://github.com/Clanker-Labs) — what we're
building, why, and the twenty-one apps it currently runs.

**Live:** <https://clanker-labs.github.io/clanker-labs-public/>

## What's here

```
index.html                  single page, no build step, no dependencies
assets/promo.*              the hero animation (mp4 + webm + gif)
assets/demo-checks.*        `make checks` running, from real output
assets/demo-agent.*         an idea captured from a chat, from a real exchange
assets/*-poster.png         final frames — also what reduced-motion viewers get
tools/promo.py              generates the hero animation
tools/demos.py              generates the two demo animations
.github/workflows/          Pages deploy on push to main
```

No framework, no bundler, no analytics. Edit `index.html` and push.

## Two rules for this page

**Nothing here links to a repo a visitor cannot open.** Most of the stack is
private. Those are described and marked `private` rather than linked, because a
promo page whose "browse the repos" button 404s is worse than one that admits
the repos are closed. When a repo goes public, swap its `<div class="card">` for
an `<a class="card" href="…">` and drop the tag.

**Nothing here shows a command that does not exist.** An earlier version of this
page had a `clanker up --host nuc-01` in the hero and a `clanker status` in the
footer. There is no `clanker` binary. Invented UI in a promo reads as a lie the
moment somebody tries it, and everything else on the page inherits the doubt.

## The demos are recordings, not mockups

`tools/demos.py` plays back output captured from a running box — `make checks`
really does print those eleven rows, three of them failing, and the agent really
did file that idea. The only edits are redactions: a tailnet hostname and a home
directory are not things to publish on a page anyone can read.

The failures are kept deliberately. A demo where everything passes is a demo
nobody believes, and "the drive is not mounted" is a better advertisement for
the checks than a wall of green.

```bash
python3 tools/demos.py checks frames-checks
ffmpeg -y -framerate 20 -i frames-checks/f%04d.png -c:v libx264 -pix_fmt yuv420p \
  -crf 20 -movflags +faststart assets/demo-checks.mp4
ffmpeg -y -framerate 20 -i frames-checks/f%04d.png -c:v libvpx-vp9 -crf 34 -b:v 0 \
  -pix_fmt yuv420p assets/demo-checks.webm
cp frames-checks/$(ls frames-checks | tail -1) assets/demo-checks-poster.png
```

Same for `agent`. Re-capture the source output before regenerating if the
scripts have changed — the point of these is that they are true.

## Brand

Palette, mark, typography and voice come from
[Clanker-Labs/branding](https://github.com/Clanker-Labs/branding) — Chain Teal
on Midnight Navy, adopted from Unchained Labs. The CSS variables at the top of
`index.html` are a copy of `tokens.json`; if the two disagree, branding wins.

**`tools/promo.py` is aligned in source but its output is not yet rebuilt.** The
constants now read the brand tokens, replacing a third palette ("clanker
orange" over GitHub greys) that predated the brand system. The committed
`assets/promo.mp4`, `promo.webm` and `poster.png` are still the old render, so
the hero on this page is orange while everything around it is teal.

Rebuilding needs `JetBrainsMonoNerdFont-ExtraBold.ttf` on the box. Without it
`font()` silently falls back to DejaVu Sans Mono and the hero re-renders in the
wrong face — which is worse than the colour being stale, and is why this was
not regenerated blind.
