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

/* Okuma takibi ve notlar */
.sec-tools { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin: -.4rem 0 1rem; }
.sec-btn {
  display: inline-flex; align-items: center; gap: 5px; height: 28px; padding: 0 11px; border-radius: 999px;
  border: 1px solid var(--border); background: var(--surface); color: var(--muted);
  font: 500 12.5px/1 Inter, system-ui, sans-serif; cursor: pointer; transition: border-color .15s, background .15s;
}
.sec-btn:hover { border-color: var(--accent); color: var(--text); }
.sec-btn[aria-pressed="true"] { background: var(--accent-soft); border-color: var(--accent); color: var(--accent-strong); font-weight: 600; }
.sec-btn.has-note { border-color: color-mix(in srgb, var(--warning) 55%, var(--border)); color: var(--warning); }
.note-box { margin: 0 0 1.2rem; }
.note-card {
  border: 1px solid color-mix(in srgb, var(--warning) 40%, var(--border));
  background: color-mix(in srgb, var(--warning) 8%, var(--surface)); border-radius: 10px; padding: 10px 12px;
}
.note-text { white-space: pre-wrap; overflow-wrap: anywhere; margin: 0; font-size: .95rem; }
.note-card textarea {
  display: block; width: 100%; min-height: 104px; resize: vertical; border: 1px solid var(--border); border-radius: 8px;
  background: var(--surface); color: var(--text); padding: 8px 10px; font: inherit; font-size: .95rem; line-height: 1.55;
}
.note-card textarea:focus { outline: 2px solid var(--accent); outline-offset: 0; border-color: transparent; }
.note-meta { display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: center; margin-top: 8px; font-size: 12px; color: var(--muted); }
.note-meta .sp { flex: 1; }
.link-btn { background: none; border: 0; padding: 2px 4px; color: var(--link); font: 500 12.5px Inter, system-ui, sans-serif; cursor: pointer; }
.link-btn:hover { text-decoration: underline; }
.link-btn.danger { color: var(--caution); }

.toc a.is-read { color: var(--muted); }
.toc-sub a.is-read::after { content: "✓"; float: right; margin-left: 6px; color: var(--accent); font-weight: 700; }
.toc-ch > a[data-prog]::after { content: attr(data-prog); float: right; margin-left: 6px; font-size: 11px; font-weight: 500; color: var(--muted); }
.toc-ch > a.is-read::after { content: "✓"; float: right; margin-left: 6px; color: var(--accent); font-weight: 700; }
.toc a.has-note::before { content: "✎"; margin-right: 5px; color: var(--warning); font-weight: 400; }

.bar { display: block; height: 6px; border-radius: 999px; background: var(--border); overflow: hidden; }
.bar > i { display: block; height: 100%; width: 0; background: var(--accent); border-radius: inherit; transition: width .25s; }
.prog-summary {
  display: block; width: 100%; margin-top: 10px; padding: 8px 10px 9px; border: 1px solid var(--border); border-radius: 9px;
  background: var(--surface-2); color: var(--text); font: inherit; font-size: 12.5px; text-align: left; cursor: pointer;
}
.prog-summary:hover { border-color: var(--accent); }
.prog-summary .bar { margin-top: 6px; }
.prog-line { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.card .bar { height: 4px; margin-top: 6px; }
.card.is-read { border-color: color-mix(in srgb, var(--accent) 50%, var(--border)); }
.btn-label { margin-left: 4px; }

.panel {
  width: min(720px, calc(100vw - 32px)); max-height: calc(100vh - 48px); padding: 0; overflow: auto;
  border: 1px solid var(--border); border-radius: 14px; background: var(--surface); color: var(--text);
  box-shadow: 0 20px 60px rgba(0,0,0,.25);
}
.panel::backdrop { background: rgba(0,0,0,.45); }
.panel-head {
  position: sticky; top: 0; z-index: 1; display: flex; align-items: center; gap: 10px;
  padding: 12px 16px 12px 20px; background: var(--surface); border-bottom: 1px solid var(--border);
}
.panel-head h2 { margin: 0; font-size: 1.1rem; flex: 1; }
.panel-body { padding: 18px 20px 24px; }
.panel-sec + .panel-sec { margin-top: 26px; }
.panel-sec h3 { margin: 0 0 10px; font-size: .82rem; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }
.big-stat { font-size: 1.5rem; font-weight: 800; font-variant-numeric: tabular-nums; }
.bar-lg { height: 10px; margin-top: 8px; }
.ch-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 7px; }
.ch-row { display: grid; grid-template-columns: minmax(0, 1fr) 120px 48px; gap: 12px; align-items: center; font-size: 13.5px; }
.ch-row a { color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ch-row .num { text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }
.ch-row.done a { color: var(--accent-strong); }
.note-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.note-item { border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; background: var(--surface-2); }
.note-item-head { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 4px 12px; font-size: 13.5px; }
.note-item-head a { font-weight: 600; }
.note-item-head small { color: var(--muted); }
.note-item p { margin: 6px 0 0; white-space: pre-wrap; overflow-wrap: anywhere; font-size: 13.5px; }
.panel-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.panel-note { font-size: 12.5px; color: var(--muted); margin: 10px 0 0; }
.panel-warn { border: 1px solid var(--caution); color: var(--caution); border-radius: 8px; padding: 8px 10px; font-size: 13px; margin: 0 0 16px; }
.btn {
  height: 34px; padding: 0 13px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface-2);
  color: var(--text); font: 500 13.5px Inter, system-ui, sans-serif; cursor: pointer; white-space: nowrap;
}
.btn:hover { border-color: var(--accent); }
.btn.primary { background: var(--accent); border-color: var(--accent); color: var(--surface); font-weight: 600; }
.btn.danger { color: var(--caution); }
.toast {
  position: fixed; left: 50%; bottom: 18px; transform: translateX(-50%); z-index: 35;
  display: flex; align-items: center; gap: 10px; width: max-content; max-width: calc(100vw - 32px);
  padding: 8px 8px 8px 14px; border-radius: 12px; background: var(--surface); border: 1px solid var(--border);
  box-shadow: 0 10px 30px rgba(0,0,0,.18); font-size: 13.5px;
}
.toast[hidden] { display: none; }
.toast > span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }

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
@media (max-width: 640px) {
  .btn-label { display: none; }
  .ch-row { grid-template-columns: minmax(0, 1fr) 64px 44px; gap: 8px; }
}
@media print {
  .topbar, .sidebar, #progress, #toTop, .copy-btn, .anchor, .overlay, .sec-tools, .note-meta, .toast, .panel { display: none !important; }
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
  <button class="icon-btn" id="progBtn" type="button" aria-label="Okuma ilerlemesi ve notlar">☑<span class="btn-label">İlerleme ve notlar</span></button>
  <button class="icon-btn" id="themeBtn" aria-label="Açık/koyu tema">◐</button>
</header>
<div class="overlay" id="overlay"></div>
<nav class="sidebar" id="sidebar" aria-label="İçindekiler">
  <div class="search-wrap">
    <input id="tocSearch" type="search" placeholder="Başlıklarda ara…" autocomplete="off">
    <button class="prog-summary" id="progSummary" type="button" aria-label="Okuma ilerlemesi ve notlar">
      <span class="prog-line"><span id="sumText">Okuma ilerlemesi</span><strong id="sumPct"></strong></span>
      <span class="bar"><i id="sumBar"></i></span>
    </button>
  </div>
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

<dialog class="panel" id="progDlg" aria-labelledby="progDlgTitle">
  <div class="panel-head">
    <h2 id="progDlgTitle">İlerleme ve notlar</h2>
    <button class="icon-btn" id="progClose" type="button" aria-label="Kapat">✕</button>
  </div>
  <div class="panel-body">
    <p class="panel-warn" id="storeWarn" hidden>Bu tarayıcıda yerel depolama kapalı (ör. gizli pencere ya da engellenmiş site verisi). İşaretlerin ve notların sayfa kapanınca kaybolur; saklamak için aşağıdan <b>Dışa aktar</b>'ı kullan.</p>
    <section class="panel-sec">
      <div class="prog-line"><span class="big-stat" id="pDone">0 / 0</span><span class="big-stat" id="pPct">%0</span></div>
      <span class="bar bar-lg"><i id="pBar"></i></span>
      <p class="panel-note" id="pNextWrap">Sıradaki okunmamış başlık: <a id="pNext" href="#"></a></p>
    </section>
    <section class="panel-sec">
      <h3>Bölümler</h3>
      <ul class="ch-list" id="pChapters"></ul>
    </section>
    <section class="panel-sec">
      <h3>Notlarım (<span id="pNoteCount">0</span>)</h3>
      <div id="pNotes"></div>
    </section>
    <section class="panel-sec">
      <h3>Yedekleme ve taşıma</h3>
      <div class="panel-actions">
        <button class="btn primary" id="exportBtn" type="button">Dışa aktar (.json)</button>
        <button class="btn" id="importBtn" type="button">İçe aktar</button>
        <button class="btn danger" id="resetBtn" type="button">Tümünü sıfırla</button>
        <input type="file" id="importInput" accept="application/json,.json" hidden>
      </div>
      <p class="panel-note" id="ioMsg" role="status"></p>
      <p class="panel-note">Okundu işaretlerin ve notların yalnızca bu tarayıcıda saklanır, hiçbir sunucuya gönderilmez. Başka bir tarayıcıya ya da cihaza taşımak veya yedeklemek için <b>Dışa aktar</b> ile dosya al, diğer tarafta <b>İçe aktar</b> ile yükle. Tarayıcı verilerini temizlersen işaretler de silinir.</p>
    </section>
  </div>
</dialog>
<div class="toast" id="resumeToast" role="status" hidden>
  <span>Kaldığın yer: <b id="resumeTitle"></b></span>
  <button class="btn primary" id="resumeGo" type="button">Devam et</button>
  <button class="icon-btn" id="resumeClose" type="button" aria-label="Kapat">✕</button>
</div>

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

  /* Okuma takibi ve notlar: durum (localStorage) */
  var KEY = "thread-doc:progress:v1";
  var storageOk = (function () {
    try { var k = KEY + ":test"; localStorage.setItem(k, "1"); localStorage.removeItem(k); return true; } catch (e) { return false; }
  })();
  var state = { read: {}, notes: {}, last: null };
  function loadState() {
    if (!storageOk) return;
    try {
      var s = JSON.parse(localStorage.getItem(KEY) || "null");
      if (s && typeof s === "object") {
        state.read = s.read && typeof s.read === "object" ? s.read : {};
        state.notes = s.notes && typeof s.notes === "object" ? s.notes : {};
        state.last = typeof s.last === "string" ? s.last : null;
      }
    } catch (e) {}
  }
  function saveState() {
    if (!storageOk) return;
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { storageOk = false; }
  }
  loadState();
  var resumeId = state.last;
  var lastTimer = null;
  function rememberLast(id) {
    state.last = id;
    clearTimeout(lastTimer);
    lastTimer = setTimeout(saveState, 800);
  }

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
    rememberLast(id);
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

  /* Okuma takibi ve notlar: arayüz */
  function $(id) { return document.getElementById(id); }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function mkBtn(cls, text) { var b = el("button", cls, text); b.type = "button"; return b; }
  function hid(a) { return decodeURIComponent(a.getAttribute("href").slice(1)); }
  function fmtDate(ts) {
    try { return new Date(ts).toLocaleString("tr-TR", { dateStyle: "medium", timeStyle: "short" }); } catch (e) { return ""; }
  }

  // Model: içindekiler ağacından bölüm (h2) ve alt başlık (h3) birimleri
  var chapters = [], units = {}, order = [];
  document.querySelectorAll("#toc > li.toc-ch").forEach(function (li) {
    var a = li.querySelector("a");
    var ch = { id: hid(a), a: a, title: a.textContent, subs: [], chapter: true };
    units[ch.id] = ch; order.push(ch.id);
    li.querySelectorAll(".toc-sub a").forEach(function (sa) {
      var u = { id: hid(sa), a: sa, title: sa.textContent, parent: ch };
      ch.subs.push(u); units[u.id] = u; order.push(u.id);
    });
    chapters.push(ch);
  });
  function leavesOf(ch) { return ch.subs.length ? ch.subs : [ch]; }
  function readCount(ch) { return leavesOf(ch).filter(function (u) { return state.read[u.id]; }).length; }
  var allLeaves = [];
  chapters.forEach(function (ch) { allLeaves = allLeaves.concat(leavesOf(ch)); });
  function hasNote(id) { var n = state.notes[id]; return !!(n && typeof n.text === "string" && n.text.trim()); }

  function setRead(u, on) { if (on) state.read[u.id] = Date.now(); else delete state.read[u.id]; }
  function toggleUnit(u) {
    if (u.chapter) {
      var ls = leavesOf(u), all = readCount(u) === ls.length;
      ls.forEach(function (x) { setRead(x, !all); });
    } else {
      setRead(u, !state.read[u.id]);
    }
    saveState();
    refreshAll();
  }

  // Başlıkların altına "Okundu" ve "Not" düğmeleri
  order.forEach(function (id) {
    var u = units[id], h = document.getElementById(id);
    if (!h) return;
    var bar = el("div", "sec-tools");
    u.readBtn = mkBtn("sec-btn", "");
    u.readBtn.addEventListener("click", function () { toggleUnit(u); });
    u.noteBtn = mkBtn("sec-btn", "");
    u.noteBtn.addEventListener("click", function () { u.editing = true; renderNote(u); });
    bar.appendChild(u.readBtn);
    bar.appendChild(u.noteBtn);
    u.noteBox = el("div", "note-box");
    u.noteBox.hidden = true;
    h.insertAdjacentElement("afterend", bar);
    bar.insertAdjacentElement("afterend", u.noteBox);
  });

  function commitNote(u, text) {
    text = String(text).replace(/\s+$/, "");
    if (text.trim()) state.notes[u.id] = { text: text, updated: Date.now() };
    else delete state.notes[u.id];
    saveState();
    refreshAll();
  }
  function renderNote(u) {
    var box = u.noteBox;
    if (!box) return;
    box.textContent = "";
    var n = state.notes[u.id], card, meta;
    if (u.editing) {
      card = el("div", "note-card");
      var ta = el("textarea");
      ta.value = hasNote(u.id) ? n.text : "";
      ta.placeholder = "Bu başlıkla ilgili notunu yaz… (yazdıkça otomatik kaydedilir)";
      ta.setAttribute("aria-label", u.title + " için not");
      meta = el("div", "note-meta");
      var status = el("span", "", hasNote(u.id) ? "Kaydedildi" : "");
      var del = mkBtn("link-btn danger", "Sil"), done = mkBtn("link-btn", "Bitti");
      meta.appendChild(status); meta.appendChild(el("span", "sp")); meta.appendChild(del); meta.appendChild(done);
      var t = null;
      ta.addEventListener("input", function () {
        status.textContent = "Kaydediliyor…";
        clearTimeout(t);
        t = setTimeout(function () {
          commitNote(u, ta.value);
          status.textContent = storageOk ? "Kaydedildi" : "Bu oturumda tutuluyor (depolama kapalı)";
        }, 400);
      });
      var finish = function () { clearTimeout(t); commitNote(u, ta.value); u.editing = false; renderNote(u); };
      done.addEventListener("click", finish);
      del.addEventListener("click", function () {
        if (ta.value.trim() && !confirm("Bu not silinsin mi?")) return;
        clearTimeout(t); commitNote(u, ""); u.editing = false; renderNote(u);
      });
      ta.addEventListener("keydown", function (e) {
        if (e.key === "Escape" || ((e.ctrlKey || e.metaKey) && e.key === "Enter")) { e.preventDefault(); finish(); }
      });
      card.appendChild(ta); card.appendChild(meta); box.appendChild(card);
      box.hidden = false;
      ta.focus();
      return;
    }
    if (!hasNote(u.id)) { box.hidden = true; return; }
    card = el("div", "note-card");
    card.appendChild(el("p", "note-text", n.text));
    meta = el("div", "note-meta");
    var edit = mkBtn("link-btn", "Düzenle"), rm = mkBtn("link-btn danger", "Sil");
    edit.addEventListener("click", function () { u.editing = true; renderNote(u); });
    rm.addEventListener("click", function () { if (confirm("Bu not silinsin mi?")) { commitNote(u, ""); renderNote(u); } });
    meta.appendChild(el("span", "", "Notun · " + fmtDate(n.updated)));
    meta.appendChild(el("span", "sp")); meta.appendChild(rm); meta.appendChild(edit);
    card.appendChild(meta); box.appendChild(card);
    box.hidden = false;
  }
  function renderAllNotes() { order.forEach(function (id) { if (!units[id].editing) renderNote(units[id]); }); }

  // Bölüm kartlarına ilerleme çubuğu
  var cards = {};
  document.querySelectorAll(".chapter-grid .card").forEach(function (c) {
    var id = hid(c), meta = c.querySelector(".card-meta");
    var bar = el("span", "bar"), fill = el("i");
    bar.appendChild(fill); c.appendChild(bar);
    cards[id] = { el: c, meta: meta, base: meta ? meta.textContent : "", fill: fill };
  });

  var dlg = $("progDlg");
  function refreshAll() {
    var total = allLeaves.length, done = 0;
    chapters.forEach(function (ch) {
      var ls = leavesOf(ch), rc = readCount(ch), full = rc === ls.length;
      done += rc;
      ch.a.classList.toggle("is-read", full);
      if (ch.subs.length && rc > 0 && !full) ch.a.setAttribute("data-prog", rc + "/" + ls.length);
      else ch.a.removeAttribute("data-prog");
      if (ch.readBtn) {
        ch.readBtn.setAttribute("aria-pressed", full ? "true" : "false");
        ch.readBtn.textContent = full ? "✓ Bölüm okundu"
          : ch.subs.length ? "Tüm bölümü okundu işaretle" + (rc ? " (" + rc + "/" + ls.length + ")" : "")
          : "Okundu işaretle";
        ch.readBtn.title = full ? "İşareti kaldırmak için tıkla" : "";
      }
      ch.subs.forEach(function (u) {
        var r = !!state.read[u.id];
        u.a.classList.toggle("is-read", r);
        if (u.readBtn) {
          u.readBtn.setAttribute("aria-pressed", r ? "true" : "false");
          u.readBtn.textContent = r ? "✓ Okundu" : "Okundu işaretle";
          u.readBtn.title = r ? "İşareti kaldırmak için tıkla" : "";
        }
      });
      var card = cards[ch.id];
      if (card) {
        card.el.classList.toggle("is-read", full);
        card.fill.style.width = (rc / ls.length * 100) + "%";
        if (card.meta) card.meta.textContent = full ? "✓ Okundu" : rc ? card.base + " · " + rc + "/" + ls.length + " okundu" : card.base;
      }
    });
    order.forEach(function (id) {
      var u = units[id], has = hasNote(id);
      u.a.classList.toggle("has-note", has);
      if (u.noteBtn) {
        u.noteBtn.textContent = has ? "✎ Notu düzenle" : "✎ Not ekle";
        u.noteBtn.classList.toggle("has-note", has);
      }
    });
    var pct = total ? Math.round(done / total * 100) : 0;
    $("sumText").textContent = done + " / " + total + " başlık okundu";
    $("sumPct").textContent = "%" + pct;
    $("sumBar").style.width = pct + "%";
    if (dlg && dlg.open) renderPanel();
  }

  // İlerleme ve notlar paneli
  function renderPanel() {
    var total = allLeaves.length;
    var done = allLeaves.filter(function (u) { return state.read[u.id]; }).length;
    var pct = total ? Math.round(done / total * 100) : 0;
    $("storeWarn").hidden = storageOk;
    $("pDone").textContent = done + " / " + total + " başlık";
    $("pPct").textContent = "%" + pct;
    $("pBar").style.width = pct + "%";
    var next = null;
    for (var i = 0; i < allLeaves.length; i++) { if (!state.read[allLeaves[i].id]) { next = allLeaves[i]; break; } }
    var nw = $("pNextWrap");
    if (next) {
      nw.textContent = "Sıradaki okunmamış başlık: ";
      var na = el("a", "", next.title); na.href = "#" + next.id; nw.appendChild(na);
    } else {
      nw.textContent = total ? "Tüm başlıkları okundu olarak işaretledin." : "";
    }
    var ul = $("pChapters");
    ul.textContent = "";
    chapters.forEach(function (ch) {
      var ls = leavesOf(ch), rc = readCount(ch);
      var li = el("li", "ch-row" + (rc === ls.length ? " done" : ""));
      var a = el("a", "", ch.title); a.href = "#" + ch.id;
      var bar = el("span", "bar"), fill = el("i"); fill.style.width = (rc / ls.length * 100) + "%"; bar.appendChild(fill);
      li.appendChild(a); li.appendChild(bar); li.appendChild(el("span", "num", rc + "/" + ls.length));
      ul.appendChild(li);
    });
    var ids = Object.keys(state.notes).filter(hasNote);
    ids.sort(function (x, y) {
      var a = order.indexOf(x), b = order.indexOf(y);
      return (a < 0 ? 1e9 : a) - (b < 0 ? 1e9 : b);
    });
    $("pNoteCount").textContent = ids.length;
    var box = $("pNotes");
    box.textContent = "";
    if (!ids.length) {
      box.appendChild(el("p", "panel-note", "Henüz not yok. Bir başlığın altındaki “✎ Not ekle” düğmesiyle not düşebilirsin."));
      return;
    }
    var list = el("ul", "note-list");
    ids.forEach(function (id) {
      var n = state.notes[id], u = units[id];
      var li = el("li", "note-item"), head = el("div", "note-item-head");
      if (u) { var a = el("a", "", u.title); a.href = "#" + id; head.appendChild(a); }
      else head.appendChild(el("strong", "", "Başlığı artık bulunamayan not (" + id + ")"));
      head.appendChild(el("small", "", fmtDate(n.updated)));
      li.appendChild(head); li.appendChild(el("p", "", n.text));
      list.appendChild(li);
    });
    box.appendChild(list);
  }
  function openPanel() {
    closeNav();
    $("ioMsg").textContent = "";
    renderPanel();
    if (typeof dlg.showModal === "function") dlg.showModal(); else dlg.setAttribute("open", "");
  }
  function closePanel() { if (typeof dlg.close === "function") dlg.close(); else dlg.removeAttribute("open"); }
  $("progBtn").addEventListener("click", openPanel);
  $("progSummary").addEventListener("click", openPanel);
  $("progClose").addEventListener("click", closePanel);
  dlg.addEventListener("click", function (e) {
    if (e.target === dlg) { closePanel(); return; }
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (a) closePanel();
  });

  // Dışa / içe aktarma ve sıfırlama
  $("exportBtn").addEventListener("click", function () {
    var data = { app: "thread-mimarisi", version: 1, exported: new Date().toISOString(), read: state.read, notes: state.notes, last: state.last };
    var blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    var a = el("a");
    a.href = URL.createObjectURL(blob);
    a.download = "thread-mimarisi-ilerleme-" + new Date().toISOString().slice(0, 10) + ".json";
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
    $("ioMsg").textContent = "Yedek dosyası indirildi.";
  });
  var importInput = $("importInput");
  $("importBtn").addEventListener("click", function () { importInput.click(); });
  importInput.addEventListener("change", function () {
    var f = importInput.files && importInput.files[0];
    if (!f) return;
    var rd = new FileReader();
    rd.onload = function () {
      try {
        var d = JSON.parse(rd.result);
        if (!d || typeof d !== "object" || (typeof d.read !== "object" && typeof d.notes !== "object")) throw new Error("format");
        var nr = 0, nn = 0;
        Object.keys(d.read || {}).forEach(function (id) {
          if (!state.read[id]) { state.read[id] = Number(d.read[id]) || Date.now(); nr++; }
        });
        Object.keys(d.notes || {}).forEach(function (id) {
          var n = d.notes[id];
          if (!n || typeof n.text !== "string" || !n.text.trim()) return;
          var cur = state.notes[id], upd = Number(n.updated) || Date.now();
          if (!cur || upd > (cur.updated || 0)) { state.notes[id] = { text: n.text, updated: upd }; nn++; }
        });
        saveState(); renderAllNotes(); refreshAll();
        $("ioMsg").textContent = "İçe aktarıldı: " + nr + " yeni okundu işareti, " + nn + " not.";
      } catch (e) {
        $("ioMsg").textContent = "Dosya okunamadı: geçerli bir yedek dosyası değil.";
      }
      importInput.value = "";
    };
    rd.readAsText(f);
  });
  $("resetBtn").addEventListener("click", function () {
    if (!confirm("Tüm okundu işaretleri ve notlar bu tarayıcıdan silinecek. Bu işlem geri alınamaz; istersen önce Dışa aktar ile yedek al. Devam edilsin mi?")) return;
    state.read = {}; state.notes = {}; state.last = null;
    saveState();
    order.forEach(function (id) { units[id].editing = false; });
    renderAllNotes(); refreshAll();
    $("ioMsg").textContent = "Tüm işaretler ve notlar silindi.";
  });

  // Başka bir sekmede yapılan değişiklikleri yansıt
  window.addEventListener("storage", function (e) {
    if (e.key !== KEY) return;
    loadState(); renderAllNotes(); refreshAll();
  });

  // Kaldığın yerden devam et
  var toast = $("resumeToast");
  if (!location.hash && resumeId && units[resumeId] && chapters.length && resumeId !== chapters[0].id) {
    $("resumeTitle").textContent = units[resumeId].title;
    toast.hidden = false;
    var hideToast = function () { toast.hidden = true; };
    $("resumeGo").addEventListener("click", function () { hideToast(); location.hash = resumeId; });
    $("resumeClose").addEventListener("click", hideToast);
    setTimeout(hideToast, 20000);
  }

  renderAllNotes();
  refreshAll();

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
