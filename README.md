# clanker-labs-public

The public site for [Clanker Labs](https://github.com/Clanker-Labs) — what we're
building, the ten projects, and how to get the stack running.

**Live:** <https://clanker-labs.github.io/clanker-labs-public/>

## What's here

```
index.html              single-page site, no build step, no dependencies
assets/promo.mp4        promo video (h264, 12s, loops)
assets/promo.webm       same, VP9 — served first, smaller
assets/promo.gif        same, for the org profile README (GitHub can't play video)
assets/poster.png       video poster + og:image
.github/workflows/      Pages deploy on push to main
```

No framework, no bundler, no analytics. Edit `index.html` and push.

## Regenerating the promo

The animation is generated from `promo.py` (kept in this repo under `tools/`).
It renders 247 PNG frames and encodes three formats:

```bash
python3 tools/promo.py frames

# GIF for the org README — palette-optimised, ~1.3 MB
ffmpeg -y -framerate 20 -i frames/f%04d.png \
  -vf "scale=900:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" \
  -loop 0 assets/promo.gif

# MP4 + WebM for the site
ffmpeg -y -framerate 20 -i frames/f%04d.png -c:v libx264 -pix_fmt yuv420p \
  -crf 20 -movflags +faststart assets/promo.mp4
ffmpeg -y -framerate 20 -i frames/f%04d.png -c:v libvpx-vp9 -crf 34 -b:v 0 \
  -pix_fmt yuv420p assets/promo.webm
```

Requires `ffmpeg`, Python 3 with Pillow, and JetBrains Mono Nerd Font (falls
back to DejaVu Sans Mono).

To change what the promo shows, edit `PRODUCTS` and `LOG` at the top of
`promo.py` — the terminal scene and the card grid both read from them.

## Local preview

```bash
python3 -m http.server 8080
# http://localhost:8080
```

## License

MIT
