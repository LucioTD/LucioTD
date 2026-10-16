"""Render the profile SVGs (divider, project cards, stats) in light and dark.

Pulls live numbers from the Modrinth and GitHub APIs, outlines the heavy
titles from Inter Black so they look the same on every OS, and writes
assets/*.svg. Run locally or from .github/workflows/stats.yml.
"""

import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
FONT = TTFont(ROOT / "scripts" / "fonts" / "Inter-Black.otf")
USER = "LucioTD"
UA = {"User-Agent": "LucioTD/profile-readme (github.com/LucioTD/LucioTD)"}

# Sampled from the banner and pfp. red is the pfp crosshair, sharpened for 1px lines.
THEMES = {
    "light": dict(bg="#f6f6f6", ink="#060606", soft="#3a3a3a", dot="#8a8a8a", dot_op=0.35,
                  rule="#8a8a8a", cobalt="#1254c6", sky="#24a2ea", red="#d42a3c",
                  hi_bg="#c7e6c2", hi_fg="#060606", bar="#060606", bar_fg="#f6f6f6"),
    "dark": dict(bg="#060606", ink="#f2f2f2", soft="#b8bcc6", dot="#24a2ea", dot_op=0.22,
                 rule="#3a4250", cobalt="#1254c6", sky="#24a2ea", red="#d42a3c",
                 hi_bg="#a6e3a1", hi_fg="#060606", bar="#f2f2f2", bar_fg="#060606"),
}
MONO = "ui-monospace,SFMono-Regular,'Cascadia Mono',Consolas,Menlo,monospace"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"


def get(url, token=None):
    headers = dict(UA)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return json.load(r)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def outline(text, size, x, y, fill, tracking=-0.03):
    """Heavy title as an SVG path. Returns (svg, width)."""
    gs = FONT.getGlyphSet()
    cmap = FONT.getBestCmap()
    scale = size / FONT["head"].unitsPerEm
    pen = SVGPathPen(gs)
    cx = 0.0
    for ch in text:
        name = cmap[ord(ch)]
        gs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x + cx, y)))
        cx += gs[name].width * scale + tracking * size
    width = cx - tracking * size
    return f'<path d="{pen.getCommands()}" fill="{fill}"/>', width


def mono_w(text, size):
    return len(text) * size * 0.6


def dots(t, w, h, step=10):
    return (f'<defs><pattern id="d" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<circle cx="{step/2}" cy="{step/2}" r="0.6" fill="{t["dot"]}"/></pattern></defs>'
            f'<rect width="{w}" height="{h}" fill="url(#d)" opacity="{t["dot_op"]}"/>')


def reg_marks(t, w, h, inset=6, arm=9):
    p = []
    for cx, cy, dx, dy in [(inset, inset, 1, 1), (w - inset, inset, -1, 1),
                           (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1)]:
        p.append(f"M{cx} {cy + dy * arm}V{cy}H{cx + dx * arm}")
    return f'<path d="{"".join(p)}" stroke="{t["ink"]}" stroke-width="1" fill="none"/>'


def hud_cross(t, x, y, r=5):
    return (f'<g stroke="{t["rule"]}" stroke-width="0.75" fill="none">'
            f'<circle cx="{x}" cy="{y}" r="{r}"/><path d="M{x - r - 3} {y}H{x + r + 3}M{x} {y - r - 3}V{y + r + 3}"/></g>')


def red_crosshair(t, x, y, w, h, x0=0, y0=0, gap=4):
    return (f'<g stroke="{t["red"]}" stroke-width="0.9">'
            f'<path d="M{x} {y0}V{y - gap}M{x} {y + gap}V{h}M{x0} {y}H{x - gap}M{x + gap} {y}H{w}" opacity="0.9"/>'
            f'<circle cx="{x}" cy="{y}" r="1.6" fill="{t["red"]}" stroke="none"/></g>')


def svg(w, h, title, body, t):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-labelledby="t"><title id="t">{esc(title)}</title>'
            f'<rect width="{w}" height="{h}" fill="{t["bg"]}"/>\n{body}\n</svg>\n')


def divider(t):
    w, h = 830, 36
    b = [dots(t, w, h, 8),
         f'<rect x="0" y="0" width="{w}" height="{h}" fill="{t["bg"]}" opacity="0.55"/>',
         f'<path d="M0 18.5H{w}" stroke="{t["rule"]}" stroke-width="0.75"/>',
         f'<rect x="0" y="15" width="132" height="7" fill="{t["bar"]}"/>',
         f'<rect x="138" y="15" width="7" height="7" fill="{t["cobalt"]}"/>',
         ''.join(f'<path d="M{x}.5 13V24" stroke="{t["rule"]}" stroke-width="0.75"/>' for x in range(160, 260, 12)),
         hud_cross(t, 415, 18.5, 4),
         f'<text x="{w}" y="11" text-anchor="end" font-family="{MONO}" font-size="8" fill="{t["soft"]}" letter-spacing="1">LUCIO / NL</text>',
         f'<g stroke="{t["red"]}" stroke-width="0.9"><path d="M702 4V33M690 18.5H714"/></g>']
    return svg(w, h, "section divider", "\n".join(b), t)


def card(t, i, p):
    w, h = 400, 150
    b = [dots(t, w, h), reg_marks(t, w, h)]
    if p.get("crosshair"):
        b.append(red_crosshair(t, 332, 58, w, h, x0=266, y0=36))  # clear of the title and header
    # header row: index block, kind label, meta on the right
    b.append(f'<rect x="18" y="14" width="22" height="13" fill="{t["cobalt"]}"/>')
    b.append(f'<text x="29" y="23.5" text-anchor="middle" font-family="{MONO}" font-size="8.5" font-weight="700" fill="#f6f6f6">{i:02d}</text>')
    b.append(f'<text x="47" y="23.5" font-family="{MONO}" font-size="8.5" fill="{t["soft"]}" letter-spacing="0.6">{esc(p["kind"].upper())}</text>')
    b.append(f'<text x="382" y="23.5" text-anchor="end" font-family="{MONO}" font-size="8.5" fill="{t["soft"]}">{esc(p["meta"])}</text>')
    b.append(f'<path d="M18 33.5H382" stroke="{t["rule"]}" stroke-width="0.6" opacity="0.8"/>')
    path, _ = outline(p["title"], 31, 17, 72, t["ink"])
    b.append(path)
    b.append(f'<text x="18" y="94" font-family="{SANS}" font-size="12" fill="{t["soft"]}">{esc(p["desc"])}</text>')
    # stat: solid bar, then an optional green highlight
    bw = mono_w(p["stat"], 10) + 16
    b.append(f'<rect x="18" y="112" width="{bw:.1f}" height="19" fill="{t["bar"]}"/>')
    b.append(f'<text x="26" y="125.5" font-family="{MONO}" font-size="10" font-weight="700" fill="{t["bar_fg"]}">{esc(p["stat"])}</text>')
    if p.get("stat2"):
        x2 = 18 + bw + 6
        b.append(f'<rect x="{x2:.1f}" y="112" width="{mono_w(p["stat2"], 10) + 14:.1f}" height="19" fill="{t["hi_bg"]}"/>')
        b.append(f'<text x="{x2 + 7:.1f}" y="125.5" font-family="{MONO}" font-size="10" fill="{t["hi_fg"]}">{esc(p["stat2"])}</text>')
    # tiny barcode + hud marker bottom right
    bx = 340
    for k, bwid in enumerate([1, 2, 1, 1, 3, 1, 2]):
        b.append(f'<rect x="{bx}" y="114" width="{bwid}" height="15" fill="{t["ink"]}" opacity="0.85"/>')
        bx += bwid + 2
    b.append(hud_cross(t, 322, 121.5, 4))
    return svg(w, h, f'{p["title"]} {p["desc"]}. {p["stat"]}', "\n".join(b), t)


def stats(t, s):
    w, h = 830, 132
    b = [dots(t, w, h), reg_marks(t, w, h)]
    b.append(f'<text x="18" y="24" font-family="{MONO}" font-size="8.5" fill="{t["soft"]}" letter-spacing="0.6">NUMBERS</text>')
    b.append(f'<text x="812" y="24" text-anchor="end" font-family="{MONO}" font-size="8.5" fill="{t["soft"]}">updated {s["date"]}</text>')
    b.append(f'<path d="M18 33.5H812" stroke="{t["rule"]}" stroke-width="0.6" opacity="0.8"/>')
    cols = [(s["downloads"], "modrinth downloads"), (s["plugins"], "paper plugins"),
            (s["repos"], "public repos"), (s["releases"], "release downloads")]
    cw = (812 - 18) / len(cols)
    for k, (num, label) in enumerate(cols):
        x = 18 + k * cw
        if k:
            b.append(f'<path d="M{x - 10:.1f} 46V112" stroke="{t["rule"]}" stroke-width="0.6"/>')
        fill = t["ink"]
        if k == 0:  # headline number: highlighter on paper, green ink on black
            if t is THEMES["light"]:
                _, nw = outline(num, 38, x - 1, 88, fill)
                b.append(f'<rect x="{x - 4:.1f}" y="70" width="{nw + 8:.1f}" height="20" fill="{t["hi_bg"]}"/>')
            else:
                fill = t["hi_bg"]
        path, _ = outline(num, 38, x - 1, 88, fill)
        b.append(path)
        b.append(f'<rect x="{x:.1f}" y="101" width="6" height="6" fill="{t["cobalt"]}"/>')
        b.append(f'<text x="{x + 11:.1f}" y="107" font-family="{MONO}" font-size="9" fill="{t["soft"]}" letter-spacing="0.4">{label}</text>')
    title = ", ".join(f"{n} {l}" for n, l in cols)
    return svg(w, h, title, "\n".join(b), t)


def collect():
    token = os.environ.get("GITHUB_TOKEN")
    mr = {p["slug"]: p for p in get(f"https://api.modrinth.com/v2/user/{USER}/projects")}
    repos = [r for r in get(f"https://api.github.com/users/{USER}/repos?per_page=100", token)
             if not r["fork"] and r["name"] not in (USER, "Lucio73-collab")]  # profile repos
    rel = {}
    for name in ("Yoink", "Aura"):
        rs = get(f"https://api.github.com/repos/{USER}/{name}/releases", token)
        rel[name] = (sum(a["download_count"] for r in rs for a in r["assets"]), rs[0]["tag_name"] if rs else "")
    return mr, repos, rel


def fmt(n):
    return f"{n:,}"


def main():
    mr, repos, rel = collect()
    ssf = mr["shieldstunfix"]
    gv = ssf["game_versions"]
    aura_dl, aura_tag = rel["Aura"]
    projects = [
        dict(slug="shieldstunfix", title="shieldstunfix.", kind="paper plugin", meta="MC-268147",
             desc="brings back the shield stun paper broke in 1.21",
             stat=f"{fmt(ssf['downloads'])} downloads", stat2=f"{gv[0]} to {gv[-1]}", crosshair=True),
        dict(slug="yoink", title="yoink.", kind="windows app", meta="YT-DLP / FFMPEG",
             desc="video and audio downloader for 1800+ sites",
             stat=f"{fmt(rel['Yoink'][0])} downloads", stat2=rel["Yoink"][1]),
        dict(slug="aura", title="aura.", kind="desktop app", meta="ELECTRON",
             desc="local music player with a talking ai dj",
             # a fresh release reads better as its version than as a tiny count
             stat=f"{fmt(aura_dl)} downloads" if aura_dl >= 25 else aura_tag, stat2="ollama + kokoro tts"),
        dict(slug="wordle-opt", title="wordle-opt.", kind="rust", meta="RAYON",
             desc="finds the best wordle opener by exhaustive search",
             stat="110M pairs searched", stat2="tarse: 3.42 avg"),
    ]
    s = dict(date=dt.date.today().isoformat(),
             downloads=fmt(sum(p["downloads"] for p in mr.values())),
             plugins=str(len(mr)), repos=str(len(repos)),
             releases=fmt(sum(dl for dl, _ in rel.values())))
    OUT.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (OUT / f"divider-{name}.svg").write_text(divider(t), encoding="utf-8", newline="\n")
        for i, p in enumerate(projects, 1):
            (OUT / f"card-{p['slug']}-{name}.svg").write_text(card(t, i, p), encoding="utf-8", newline="\n")
        (OUT / f"stats-{name}.svg").write_text(stats(t, s), encoding="utf-8", newline="\n")
    print(json.dumps(s))


if __name__ == "__main__":
    main()
