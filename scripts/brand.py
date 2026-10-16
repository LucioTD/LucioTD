"""Repo banners and social previews in the profile style.

    python scripts/brand.py <repo-slug> <out-dir>

Writes banner.svg, banner-dark.svg and social-preview.svg (+ .png when
Playwright is installed). Facts here are stable ones (kind, stack, platform,
license); versions and counts belong in live badges so nothing goes stale.
"""

import sys
from pathlib import Path

from render import MONO, SANS, THEMES, dots, esc, hud_cross, outline, reg_marks, mono_w

REPOS = {
    "aura": dict(repo="Aura", title="aura.", kind="desktop app", meta="ELECTRON / OLLAMA / KOKORO",
                 tagline="local music player with a talking ai dj", bar="windows + linux", hi="mit"),
    "yoink": dict(repo="Yoink", title="yoink.", kind="windows app", meta="YT-DLP / FFMPEG",
                  tagline="paste a link, get the best quality the source has", bar="windows", hi="gpl-3.0"),
    "harvest": dict(repo="harvest", title="harvest.", kind="cli + dashboard", meta="PYTHON / PLAYWRIGHT",
                    tagline="polite web scraper with a cli and a local dashboard", bar="python 3.11+", hi="mit"),
    "rootcheck": dict(repo="rootcheck", title="rootcheck.", kind="desktop helper", meta="PYTHON / PYSIDE6",
                      tagline="manual username checks for root, without automation", bar="windows", hi="mit"),
    "permconflictwatchdog": dict(repo="PermConflictWatchdog", title="permconflictwatchdog.", kind="paper plugin", meta="PAPER 26.2 / JAVA 25",
                                 tagline="warns when a second permissions plugin runs next to luckperms",
                                 bar="paper 26.2", hi="mit"),
    "wordle-opt": dict(repo="wordle-opt", title="wordle-opt.", kind="rust", meta="RAYON / BRANCH AND BOUND",
                       tagline="finds the best wordle opener by exhaustive search", bar="cli", hi="mit"),
}


def banner_body(t, p, w=960, h=240):
    b = [dots(t, w, h), reg_marks(t, w, h, inset=8, arm=12)]
    # title: shrink long names to fit left of the crosshair
    size = 72
    _, tw = outline(p["title"], size, 0, 0, t["ink"])
    if tw > 700:
        size = size * 700 / tw
    path, tw = outline(p["title"], size, 34, 124, t["ink"])
    cx, cy = 856, 96
    x0 = max(34 + tw + 36, 620)
    b.append(f'<g stroke="{t["red"]}" stroke-width="1"><path d="M{cx} 48V{cy - 5}M{cx} {cy + 5}V{h}'
             f'M{x0:.0f} {cy}H{cx - 5}M{cx + 5} {cy}H{w}" opacity="0.9"/>'
             f'<circle cx="{cx}" cy="{cy}" r="2" fill="{t["red"]}" stroke="none"/></g>')
    b.append(f'<rect x="36" y="26" width="16" height="16" fill="{t["cobalt"]}"/>')
    b.append(f'<text x="60" y="38.5" font-family="{MONO}" font-size="11" fill="{t["soft"]}" letter-spacing="0.8">{esc(p["kind"].upper())}</text>')
    b.append(f'<text x="924" y="38.5" text-anchor="end" font-family="{MONO}" font-size="11" fill="{t["soft"]}">{esc(p["meta"])}</text>')
    b.append(f'<path d="M36 50.5H924" stroke="{t["rule"]}" stroke-width="0.75" opacity="0.8"/>')
    b.append(path)
    b.append(f'<text x="37" y="160" font-family="{SANS}" font-size="18" fill="{t["soft"]}">{esc(p["tagline"])}</text>')
    bw = mono_w(p["bar"], 12) + 20
    b.append(f'<rect x="36" y="184" width="{bw:.1f}" height="24" fill="{t["bar"]}"/>')
    b.append(f'<text x="46" y="200.5" font-family="{MONO}" font-size="12" font-weight="700" fill="{t["bar_fg"]}">{esc(p["bar"])}</text>')
    x2 = 36 + bw + 8
    b.append(f'<rect x="{x2:.1f}" y="184" width="{mono_w(p["hi"], 12) + 18:.1f}" height="24" fill="{t["hi_bg"]}"/>')
    b.append(f'<text x="{x2 + 9:.1f}" y="200.5" font-family="{MONO}" font-size="12" fill="{t["hi_fg"]}">{esc(p["hi"])}</text>')
    bx = 770
    for bwid in [1, 2, 1, 1, 3, 1, 2, 1]:
        b.append(f'<rect x="{bx}" y="186" width="{bwid}" height="20" fill="{t["ink"]}" opacity="0.85"/>')
        bx += bwid + 2.5
    b.append(hud_cross(t, 748, 196, 5))
    return b


def svg(w, h, title, body, t, vb=None):
    vb = vb or f"0 0 {w} {h}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}" '
            f'role="img" aria-labelledby="t"><title id="t">{esc(title)}</title>\n'
            f'<rect width="100%" height="100%" fill="{t["bg"]}"/>\n' + "\n".join(body) + "\n</svg>\n")


def social(t, p):
    # 1280x640 card: the banner centred, plus the repo path underneath
    inner = "\n".join(banner_body(t, p)[1:])  # skip the banner's own dot grid
    body = [dots(t, 1280, 640, 12),
            f'<g transform="translate(80 150) scale(1.1667)">{inner}</g>',
            f'<text x="117" y="560" font-family="{MONO}" font-size="20" fill="{t["soft"]}">github.com/LucioTD/{esc(p["repo"])}</text>']
    return svg(1280, 640, f'{p["title"]} {p["tagline"]}', body, t)


def main():
    slug, out = sys.argv[1], Path(sys.argv[2])
    p = REPOS[slug.lower()]
    out.mkdir(parents=True, exist_ok=True)
    title = f'{p["title"]} {p["tagline"]}'
    (out / "banner.svg").write_text(svg(960, 240, title, banner_body(THEMES["light"], p), THEMES["light"]), encoding="utf-8", newline="\n")
    (out / "banner-dark.svg").write_text(svg(960, 240, title, banner_body(THEMES["dark"], p), THEMES["dark"]), encoding="utf-8", newline="\n")
    sp = out / "social-preview.svg"
    sp.write_text(social(THEMES["light"], p), encoding="utf-8", newline="\n")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={"width": 1280, "height": 640})
        pg.goto(sp.resolve().as_uri())
        pg.screenshot(path=str(out / "social-preview.png"))
        br.close()


if __name__ == "__main__":
    main()
