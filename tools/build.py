#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thread Mimarisi dokümanı derleyicisi
====================================

`bolumler/` klasöründeki Markdown bölümlerini dosya adı sırasıyla birleştirir ve
iki çıktı üretir:

* ``Thread-Mimarisi.md``   – GitHub'da doğrudan okunabilen tek parça Markdown
                             (otomatik içindekiler tablosu ile)
* ``Thread-Mimarisi.html`` – kenar menülü, aramalı, açık/koyu temalı, tek dosya HTML

Kullanım::

    py tools/build.py          (Windows)
    python3 tools/build.py     (Linux / macOS)

Gereksinim::

    pip install markdown
"""
from __future__ import annotations

import datetime as _dt
import html
import re
import sys
import unicodedata
from pathlib import Path

try:
    import markdown
    from markdown.extensions.toc import TocExtension
except ImportError:  # pragma: no cover
    sys.exit("Hata: 'markdown' paketi gerekli ->  pip install markdown")

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "bolumler"
OUT_MD = ROOT / "Thread-Mimarisi.md"
OUT_HTML = ROOT / "Thread-Mimarisi.html"
TOC_MARKER = "<!-- ICINDEKILER -->"
GRID_TOKEN = "@@BOLUM_KARTLARI@@"

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")

CALLOUTS = {
    "NOTE": "Not",
    "TIP": "İpucu",
    "IMPORTANT": "Önemli",
    "WARNING": "Uyarı",
    "CAUTION": "Dikkat",
}


# --------------------------------------------------------------------------- #
#  Yardımcılar
# --------------------------------------------------------------------------- #
def slugify(value: str, separator: str = "-") -> str:
    """GitHub ile uyumlu başlık çapası (anchor) üretir.

    Küçük harfe çevirir; harf, rakam, birleşik işaret, alt çizgi, boşluk ve tire
    dışındaki her şeyi atar; boşlukları tireye çevirir. Türkçe karakterler korunur.
    """
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value).strip().lower()
    kept = []
    for ch in value:
        if ch in (" ", "-"):
            kept.append(ch)
            continue
        cat = unicodedata.category(ch)
        if cat[0] in "LMN" or cat == "Pc":
            kept.append(ch)
    return "".join(kept).replace(" ", separator)


TOC_EXCLUDE = {slugify("İçindekiler")}


def iter_headings(text: str):
    """Kod blokları dışındaki (seviye, başlık) çiftlerini döndürür."""
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if m:
            yield len(m.group(1)), m.group(2)


def build_md_toc(text: str) -> tuple[str, list[str]]:
    """GitHub çapalarıyla iç içe içindekiler listesi ve çakışan başlık uyarıları."""
    used: dict[str, int] = {}
    lines: list[str] = []
    warnings: list[str] = []
    for level, title in iter_headings(text):
        plain = LINK_RE.sub(r"\1", title)
        slug = slugify(plain)
        n = used.get(slug, 0)
        used[slug] = n + 1
        anchor = slug if n == 0 else f"{slug}-{n}"
        if n and level <= 3:
            warnings.append(f"Tekrarlanan başlık çapası: '{title}' (#{slug})")
        if level not in (2, 3) or slug in TOC_EXCLUDE:
            continue
        indent = "  " * (level - 2)
        lines.append(f"{indent}- [{plain}](#{anchor})")
    return "\n".join(lines), warnings


def read_sources() -> list[Path]:
    files = sorted(p for p in SRC_DIR.glob("*.md") if p.is_file())
    if not files:
        sys.exit(f"Hata: {SRC_DIR} içinde .md dosyası yok")
    return files


# --------------------------------------------------------------------------- #
#  HTML üretimi
# --------------------------------------------------------------------------- #
def _clean_mermaid(src: str) -> str:
    """Satır içi çoklu boşlukları teke indirir (Mermaid 'wrap' modunda çift boşluk çizimi bozar)."""
    lines = []
    for line in src.split("\n"):
        stripped = line.lstrip(" ")
        indent = line[: len(line) - len(stripped)]
        lines.append(indent + re.sub(r" {2,}", " ", stripped))
    return "\n".join(lines)


def post_process(body: str) -> str:
    # Mermaid diyagramları
    body = re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        lambda m: f'<figure class="diagram"><pre class="mermaid">{_clean_mermaid(m.group(1))}</pre></figure>',
        body,
        flags=re.S,
    )
    # Tabloları yatay kaydırılabilir sarmalayıcıya al
    body = body.replace("<table>", '<div class="table-wrap"><table>')
    body = body.replace("</table>", "</table></div>")

    # GitHub tarzı uyarı kutuları:  > [!NOTE]
    def _callout(m: re.Match) -> str:
        kind = m.group(1)
        return (
            f'<blockquote class="callout callout-{kind.lower()}">'
            f'<p class="callout-title">{CALLOUTS[kind]}</p><p>'
        )

    body = re.sub(
        r"<blockquote>\s*<p>\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(?:<br\s*/?>)?\s*",
        _callout,
        body,
    )
    # Boş kalan ilk paragrafı temizle
    body = re.sub(r'(<p class="callout-title">[^<]*</p>)<p>\s*</p>', r"\1", body)

    # Başlıklara kalıcı bağlantı (#) ekle
    body = re.sub(
        r'<h([2-4]) id="([^"]+)">(.*?)</h\1>',
        r'<h\1 id="\2">\3<a class="anchor" href="#\2" aria-label="Bu başlığa bağlantı">#</a></h\1>',
        body,
        flags=re.S,
    )
    return body


def _name(tok: dict) -> str:
    return html.escape(html.unescape(tok["name"]), quote=False)


def build_sidebar(tokens: list[dict]) -> str:
    out = ['<ul class="toc" id="toc">']
    for t in tokens:
        if t["id"] in TOC_EXCLUDE:
            continue
        kids = t.get("children", [])
        out.append(f'<li class="toc-ch"><a href="#{t["id"]}">{_name(t)}</a>')
        if kids:
            out.append('<ul class="toc-sub">')
            for k in kids:
                out.append(f'<li><a href="#{k["id"]}">{_name(k)}</a></li>')
            out.append("</ul>")
        out.append("</li>")
    out.append("</ul>")
    return "\n".join(out)


def build_grid(tokens: list[dict]) -> str:
    cards = []
    for t in tokens:
        if t["id"] in TOC_EXCLUDE:
            continue
        name = html.unescape(t["name"])
        m = re.match(r"^(\d+|[A-ZÇĞİÖŞÜ])\.\s*(.*)$", name)
        num, title = (m.group(1), m.group(2)) if m else ("•", name)
        n_sub = len(t.get("children", []))
        cards.append(
            f'<a class="card" href="#{t["id"]}"><span class="card-num">{html.escape(num)}</span>'
            f'<span class="card-title">{html.escape(title)}</span>'
            f'<span class="card-meta">{n_sub} alt başlık</span></a>'
        )
    return '<nav class="chapter-grid" aria-label="Bölümler">' + "".join(cards) + "</nav>"


def build_html(full_text: str, stats: dict) -> str:
    text = full_text.replace(TOC_MARKER, GRID_TOKEN)
    md = markdown.Markdown(
        extensions=["extra", "sane_lists", TocExtension(slugify=slugify, toc_depth="2-3")],
        output_format="html5",
    )
    body = md.convert(text)
    tokens = md.toc_tokens
    body = post_process(body)
    body = body.replace(f"<p>{GRID_TOKEN}</p>", build_grid(tokens))
    page = TEMPLATE
    for key, val in {
        "%%SIDEBAR%%": build_sidebar(tokens),
        "%%BODY%%": body,
        "%%DATE%%": stats["date"],
        "%%WORDS%%": f'{stats["words"]:,}'.replace(",", "."),
        "%%MINUTES%%": str(stats["minutes"]),
        "%%CHAPTERS%%": str(stats["chapters"]),
    }.items():
        page = page.replace(key, val)
    return page


# --------------------------------------------------------------------------- #
#  Ana akış
# --------------------------------------------------------------------------- #
def main() -> None:
    files = read_sources()
    parts = [p.read_text(encoding="utf-8").strip() for p in files]
    full = "\n\n".join(parts) + "\n"

    toc, warnings = build_md_toc(full)
    for w in warnings:
        print("UYARI:", w)

    header = (
        "<!-- Bu dosya tools/build.py tarafından bolumler/ klasöründen otomatik üretilir. "
        "Düzenlemeleri bolumler/ altında yapıp betiği yeniden çalıştırın. -->\n\n"
    )
    OUT_MD.write_text(header + full.replace(TOC_MARKER, toc), encoding="utf-8", newline="\n")

    words = len(re.findall(r"\w+", full))
    chapters = sum(1 for lvl, t in iter_headings(full) if lvl == 2 and slugify(t) not in TOC_EXCLUDE)
    stats = {
        "date": _dt.date.today().strftime("%d.%m.%Y"),
        "words": words,
        "minutes": max(1, round(words / 180)),
        "chapters": chapters,
    }
    OUT_HTML.write_text(build_html(full, stats), encoding="utf-8", newline="\n")

    n_lines = full.count("\n")
    print(f"{len(files)} kaynak dosya -> {OUT_MD.name} ({n_lines} satır, {words} kelime, {chapters} bölüm)")
    print(f"HTML -> {OUT_HTML.name} ({OUT_HTML.stat().st_size // 1024} KB)")


# --------------------------------------------------------------------------- #
#  HTML şablonu
# --------------------------------------------------------------------------- #
TEMPLATE = r"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thread Ağ Mimarisi</title>
<meta name="description" content="Thread (IEEE 802.15.4 / 6LoWPAN / IPv6) ağ mimarisi ve haberleşme yapısı üzerine kapsamlı Türkçe teknik rehber.">
<script>
  (function () {
    try {
      var t = localStorage.getItem("thread-doc-theme");
      if (t === "light" || t === "dark") document.documentElement.setAttribute("data-theme", t);
    } catch (e) {}
  })();
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #f7f6f2; --surface: #ffffff; --surface-2: #f0eee8; --text: #1c1d1f; --muted: #5d6166;
  --border: #e2dfd6; --accent: #0d7a5f; --accent-strong: #0a5e49; --accent-soft: #e2f1ec;
  --link: #0b5fae; --code-bg: #f3f1eb; --code-text: #24292f;
  --note: #0b5fae; --tip: #1a7f37; --important: #8250df; --warning: #9a6700; --caution: #cf222e;
  --shadow: 0 1px 2px rgba(0,0,0,.04), 0 6px 20px rgba(0,0,0,.05);
  --sidebar-w: 320px; --topbar-h: 56px;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0f1214; --surface: #161a1d; --surface-2: #1d2226; --text: #e6e4df; --muted: #9ea4aa;
    --border: #2a3035; --accent: #3cc59a; --accent-strong: #5ad6ad; --accent-soft: #12302a;
    --link: #79b8ff; --code-bg: #1a1f23; --code-text: #e1e4e8;
    --note: #58a6ff; --tip: #3fb950; --important: #a371f7; --warning: #d29922; --caution: #f85149;
    --shadow: 0 1px 2px rgba(0,0,0,.3);
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #0f1214; --surface: #161a1d; --surface-2: #1d2226; --text: #e6e4df; --muted: #9ea4aa;
  --border: #2a3035; --accent: #3cc59a; --accent-strong: #5ad6ad; --accent-soft: #12302a;
  --link: #79b8ff; --code-bg: #1a1f23; --code-text: #e1e4e8;
  --note: #58a6ff; --tip: #3fb950; --important: #a371f7; --warning: #d29922; --caution: #f85149;
  --shadow: 0 1px 2px rgba(0,0,0,.3);
  color-scheme: dark;
}
* { box-sizing: border-box; }
html { scroll-padding-top: calc(var(--topbar-h) + 16px); -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font: 16.5px/1.72 Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased; overflow-x: hidden;
}
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Üst çubuk */
.topbar {
  position: fixed; inset: 0 0 auto 0; height: var(--topbar-h); z-index: 30;
  display: flex; align-items: center; gap: 12px; padding: 0 16px;
  background: var(--surface); border-bottom: 1px solid var(--border);
}
.brand { display: flex; align-items: center; gap: 10px; min-width: 0; }
.brand-mark {
  width: 30px; height: 30px; border-radius: 8px; flex: none;
  background: var(--accent); color: #fff; display: grid; place-items: center; font-weight: 800; font-size: 15px;
}
.brand-text { min-width: 0; }
.brand-title { font-weight: 700; font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.brand-sub { font-size: 12px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.spacer { flex: 1; }
.meta-pill { font-size: 12.5px; color: var(--muted); white-space: nowrap; }
.icon-btn {
  border: 1px solid var(--border); background: var(--surface-2); color: var(--text);
  height: 34px; min-width: 34px; padding: 0 10px; border-radius: 8px; cursor: pointer; font: inherit; font-size: 14px;
}
.icon-btn:hover { border-color: var(--accent); }
#menuBtn { display: none; }

/* Kenar menü */
.sidebar {
  position: fixed; top: var(--topbar-h); bottom: 0; left: 0; width: var(--sidebar-w); z-index: 20;
  background: var(--surface); border-right: 1px solid var(--border);
  overflow-y: auto; padding: 0 10px 40px; overscroll-behavior: contain;
}
.search-wrap { position: sticky; top: 0; background: var(--surface); padding: 14px 4px 10px; z-index: 1; }
.search-wrap input {
  width: 100%; height: 36px; border-radius: 9px; border: 1px solid var(--border);
  background: var(--surface-2); color: var(--text); padding: 0 12px; font: inherit; font-size: 14px;
}
.search-wrap input:focus { outline: 2px solid var(--accent); outline-offset: 0; border-color: transparent; }
.toc, .toc ul { list-style: none; margin: 0; padding: 0; }
.toc a {
  display: block; padding: 5px 10px; border-radius: 7px; color: var(--muted);
  font-size: 13.5px; line-height: 1.4; text-decoration: none;
}
.toc a:hover { background: var(--surface-2); color: var(--text); }
.toc-ch > a { font-weight: 600; color: var(--text); margin-top: 2px; }
.toc-sub { display: none; margin: 2px 0 6px 10px !important; border-left: 1px solid var(--border); padding-left: 6px !important; }
.toc-ch.open > .toc-sub { display: block; }
.toc a.active { background: var(--accent-soft); color: var(--accent-strong); }
.toc li.hidden { display: none; }

/* İçerik */
main { margin-left: var(--sidebar-w); padding: calc(var(--topbar-h) + 28px) 40px 80px; }
.content { max-width: 940px; margin: 0 auto; }
.content h1 { font-size: 2.35rem; line-height: 1.2; letter-spacing: -0.02em; margin: .4em 0 .5em; }
.content h2 {
  font-size: 1.8rem; line-height: 1.25; letter-spacing: -0.01em;
  margin: 3.6rem 0 1rem; padding-top: 1.6rem; border-top: 2px solid var(--border);
}
.content h3 { font-size: 1.32rem; line-height: 1.3; margin: 2.4rem 0 .7rem; }
.content h4 { font-size: 1.08rem; margin: 1.8rem 0 .5rem; }
.content h2, .content h3, .content h4 { position: relative; }
.anchor { margin-left: .4em; color: var(--muted); opacity: 0; font-weight: 400; text-decoration: none !important; }
h2:hover .anchor, h3:hover .anchor, h4:hover .anchor { opacity: .7; }
.content p, .content li { overflow-wrap: anywhere; }
.content ul, .content ol { padding-left: 1.4em; }
.content li + li { margin-top: .2em; }
.content hr { border: none; border-top: 1px solid var(--border); margin: 2.5rem 0; }
.content img { max-width: 100%; }
.content strong { font-weight: 650; }

code, pre { font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Consolas, monospace; }
:not(pre) > code {
  background: var(--code-bg); color: var(--code-text); padding: .1em .38em; border-radius: 5px;
  font-size: .86em; border: 1px solid var(--border); overflow-wrap: anywhere;
}
pre {
  position: relative; background: var(--code-bg); color: var(--code-text);
  border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px;
  overflow-x: auto; font-size: 13.2px; line-height: 1.55; tab-size: 4;
}
pre code { background: none; border: 0; padding: 0; font-size: inherit; }
.copy-btn {
  position: absolute; top: 8px; right: 8px; font: 12px Inter, sans-serif; padding: 3px 8px;
  border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--muted);
  cursor: pointer; opacity: 0; transition: opacity .15s;
}
pre:hover .copy-btn, .copy-btn:focus { opacity: 1; }

.table-wrap { overflow-x: auto; margin: 1.2rem 0; border: 1px solid var(--border); border-radius: 10px; background: var(--surface); }
table { width: 100%; border-collapse: collapse; font-size: .9rem; line-height: 1.5; }
th, td { padding: 8px 12px; text-align: left; vertical-align: top; border-bottom: 1px solid var(--border); }
th { background: var(--surface-2); font-weight: 650; white-space: nowrap; }
tr:last-child td { border-bottom: none; }
tbody tr:hover td { background: var(--surface-2); }

blockquote { margin: 1.2rem 0; padding: .6rem 1rem; border-left: 4px solid var(--border); color: var(--muted); background: var(--surface); border-radius: 0 10px 10px 0; }
blockquote p { margin: .4em 0; }
.callout { color: var(--text); --c: var(--note); border-left-color: var(--c); background: color-mix(in srgb, var(--c) 7%, var(--surface)); }
.callout-title { font-weight: 700; color: var(--c); margin-bottom: .2em !important; font-size: .92rem; letter-spacing: .02em; text-transform: uppercase; }
.callout-tip { --c: var(--tip); } .callout-important { --c: var(--important); }
.callout-warning { --c: var(--warning); } .callout-caution { --c: var(--caution); }

.diagram {
  margin: 1.4rem 0; padding: 16px; background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; overflow-x: auto; text-align: center; box-shadow: var(--shadow);
}
.diagram pre.mermaid { background: transparent; border: 0; padding: 0; margin: 0; text-align: left; white-space: pre; }
.diagram pre.mermaid[data-processed="true"] { text-align: center; white-space: normal; }
.diagram svg { max-width: 100%; height: auto; }

.chapter-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px; margin: 1.2rem 0 2rem; }
.card {
  display: flex; flex-direction: column; gap: 4px; padding: 12px 14px; border-radius: 11px;
  background: var(--surface); border: 1px solid var(--border); color: var(--text); text-decoration: none !important;
  transition: border-color .15s, transform .15s;
}
.card:hover { border-color: var(--accent); transform: translateY(-1px); }
.card-num { font-size: 12px; font-weight: 700; color: var(--accent); }
.card-title { font-weight: 600; font-size: 14.5px; line-height: 1.35; }
.card-meta { font-size: 12px; color: var(--muted); }

.page-footer { margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid var(--border); color: var(--muted); font-size: 13px; }

#progress { position: fixed; top: 0; left: 0; height: 3px; width: 0; background: var(--accent); z-index: 40; }
#toTop {
  position: fixed; right: 18px; bottom: 18px; z-index: 25; width: 42px; height: 42px; border-radius: 50%;
  border: 1px solid var(--border); background: var(--surface); color: var(--text); box-shadow: var(--shadow);
  cursor: pointer; font-size: 18px; opacity: 0; pointer-events: none; transition: opacity .2s;
}
#toTop.show { opacity: 1; pointer-events: auto; }
.overlay { display: none; }

@media (max-width: 1050px) {
  #menuBtn { display: inline-block; }
  .meta-pill { display: none; }
  .sidebar { transform: translateX(-100%); transition: transform .2s ease; width: min(86vw, 340px); box-shadow: var(--shadow); }
  body.nav-open .sidebar { transform: none; }
  body.nav-open .overlay { display: block; position: fixed; inset: var(--topbar-h) 0 0 0; background: rgba(0,0,0,.35); z-index: 15; }
  main { margin-left: 0; padding: calc(var(--topbar-h) + 18px) 16px 64px; }
  .content h1 { font-size: 1.8rem; }
  .content h2 { font-size: 1.45rem; }
  .content h3 { font-size: 1.18rem; }
  body { font-size: 15.5px; }
}
@media print {
  .topbar, .sidebar, #progress, #toTop, .copy-btn, .anchor, .overlay { display: none !important; }
  main { margin: 0; padding: 0; }
  body { background: #fff; color: #000; font-size: 11pt; }
  .content { max-width: none; }
  .content h2 { break-before: page; border-top: none; }
  pre, .table-wrap, .diagram, blockquote { break-inside: avoid; }
  a { color: inherit; }
}
</style>
</head>
<body>
<div id="progress"></div>
<header class="topbar">
  <button class="icon-btn" id="menuBtn" aria-label="İçindekiler menüsünü aç/kapat">☰</button>
  <div class="brand">
    <div class="brand-mark" aria-hidden="true">T</div>
    <div class="brand-text">
      <div class="brand-title">Thread Ağ Mimarisi ve Haberleşme Yapısı</div>
      <div class="brand-sub">IEEE 802.15.4 · 6LoWPAN · IPv6 · MLE · Matter</div>
    </div>
  </div>
  <div class="spacer"></div>
  <span class="meta-pill">%%CHAPTERS%% bölüm · %%WORDS%% kelime · ≈%%MINUTES%% dk okuma</span>
  <button class="icon-btn" id="themeBtn" aria-label="Açık/koyu tema">◐</button>
</header>
<div class="overlay" id="overlay"></div>
<nav class="sidebar" id="sidebar" aria-label="İçindekiler">
  <div class="search-wrap"><input id="tocSearch" type="search" placeholder="Başlıklarda ara…" autocomplete="off"></div>
  %%SIDEBAR%%
</nav>
<main>
  <article class="content" id="content">
%%BODY%%
    <footer class="page-footer">
      Bu sayfa <code>tools/build.py</code> ile <code>bolumler/</code> klasöründeki Markdown kaynaklarından üretilmiştir · Derleme tarihi: %%DATE%%
    </footer>
  </article>
</main>
<button id="toTop" aria-label="Başa dön">↑</button>

<script>
(function () {
  var root = document.documentElement;
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function isDark() {
    var t = root.getAttribute("data-theme");
    if (t) return t === "dark";
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  /* Tema */
  document.getElementById("themeBtn").addEventListener("click", function () {
    var next = isDark() ? "light" : "dark";
    root.setAttribute("data-theme", next);
    store("thread-doc-theme", next);
    renderMermaid();
  });

  /* Mobil menü */
  function closeNav() { document.body.classList.remove("nav-open"); }
  document.getElementById("menuBtn").addEventListener("click", function () { document.body.classList.toggle("nav-open"); });
  document.getElementById("overlay").addEventListener("click", closeNav);

  /* İçindekiler: aktif bölüm takibi */
  var links = Array.prototype.slice.call(document.querySelectorAll("#toc a"));
  var byId = {};
  links.forEach(function (a) {
    byId[decodeURIComponent(a.getAttribute("href").slice(1))] = a;
    a.addEventListener("click", function () { if (window.innerWidth <= 1050) closeNav(); });
  });
  var heads = Array.prototype.slice.call(document.querySelectorAll(".content h2[id], .content h3[id]"))
    .filter(function (h) { return byId[h.id]; });
  var current = null;
  function setActive(id) {
    if (id === current) return;
    current = id;
    links.forEach(function (a) { a.classList.remove("active"); });
    document.querySelectorAll(".toc-ch.open").forEach(function (li) { if (!searchActive) li.classList.remove("open"); });
    var a = byId[id];
    if (!a) return;
    a.classList.add("active");
    var ch = a.closest(".toc-ch");
    if (ch) {
      ch.classList.add("open");
      ch.querySelector("a").classList.add("active");
    }
    var sb = document.getElementById("sidebar");
    var r = a.getBoundingClientRect(), sr = sb.getBoundingClientRect();
    if (r.top < sr.top + 60 || r.bottom > sr.bottom - 20) sb.scrollTop += r.top - sr.top - sr.height / 3;
  }
  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      var y = window.scrollY, h = document.documentElement.scrollHeight - window.innerHeight;
      document.getElementById("progress").style.width = (h > 0 ? (y / h) * 100 : 0) + "%";
      document.getElementById("toTop").classList.toggle("show", y > 700);
      var id = null;
      for (var i = 0; i < heads.length; i++) {
        if (heads[i].getBoundingClientRect().top < 110) id = heads[i].id; else break;
      }
      if (id) setActive(id);
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  document.getElementById("toTop").addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });

  /* İçindekiler araması */
  var searchActive = false;
  var input = document.getElementById("tocSearch");
  input.addEventListener("input", function () {
    var q = input.value.trim().toLocaleLowerCase("tr");
    searchActive = q.length > 0;
    document.querySelectorAll("#toc > li").forEach(function (ch) {
      var chText = ch.querySelector("a").textContent.toLocaleLowerCase("tr");
      var subs = ch.querySelectorAll(".toc-sub li"), anySub = false;
      subs.forEach(function (li) {
        var hit = !q || li.textContent.toLocaleLowerCase("tr").indexOf(q) !== -1 || chText.indexOf(q) !== -1;
        li.classList.toggle("hidden", !hit);
        if (hit && q) anySub = true;
      });
      var show = !q || chText.indexOf(q) !== -1 || anySub;
      ch.classList.toggle("hidden", !show);
      ch.classList.toggle("open", !!q && show);
    });
    if (!q) { var c = current; current = null; if (c) setActive(c); }
  });

  /* Kod kopyalama */
  document.querySelectorAll(".content pre:not(.mermaid)").forEach(function (pre) {
    var btn = document.createElement("button");
    btn.className = "copy-btn"; btn.type = "button"; btn.textContent = "Kopyala";
    btn.addEventListener("click", function () {
      var code = pre.querySelector("code");
      var text = (code || pre).innerText;
      var done = function () { btn.textContent = "Kopyalandı"; setTimeout(function () { btn.textContent = "Kopyala"; }, 1400); };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () {});
    });
    pre.appendChild(btn);
  });

  /* Mermaid diyagramları */
  var blocks = Array.prototype.slice.call(document.querySelectorAll("pre.mermaid"));
  blocks.forEach(function (b) { b.setAttribute("data-src", b.textContent); });
  window.renderMermaid = renderMermaid;
  function renderMermaid() {
    if (!window.mermaid || !blocks.length) return;
    blocks.forEach(function (b) { b.removeAttribute("data-processed"); b.textContent = b.getAttribute("data-src"); });
    window.mermaid.initialize({
      startOnLoad: false, securityLevel: "strict", theme: isDark() ? "dark" : "default",
      fontFamily: "Inter, system-ui, sans-serif",
      flowchart: { htmlLabels: true, curve: "basis" },
      sequence: { mirrorActors: false, useMaxWidth: true, wrap: true, width: 170, actorMargin: 70, messageFontSize: 14, noteFontSize: 13 }
    });
    window.mermaid.run({ nodes: blocks }).catch(function (e) { console.error(e); });
  }
  window.addEventListener("load", renderMermaid);
})();
</script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js" defer></script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
