"""
Dashboard HTML 建構模組 — iframe 內嵌儀表板
HTML escape helpers + 各區段 (titles, tags, stories, songs) HTML 生成
"""


# ─────────────────────────────────────────────────────────────────────────────
#  HTML Escape helpers
# ─────────────────────────────────────────────────────────────────────────────
def _ae(t: str) -> str:
    return t.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&#39;').replace('<', '&lt;').replace('>', '&gt;')


def _he(t: str) -> str:
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')


# ─────────────────────────────────────────────────────────────────────────────
#  內嵌 CSS & JS
# ─────────────────────────────────────────────────────────────────────────────
_BASE_CSS = (
    "* { box-sizing: border-box; margin: 0; padding: 0; }"
    "html, body { background: transparent; font-family: 'Poppins', -apple-system, sans-serif; overflow-x: hidden; color: #e8e8f0; }"
    ".lbl { font-size: 11px; font-weight: 700; color: #00ffcc; letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 12px; }"
    ".card { background: rgba(14,14,24,0.6); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 20px 22px; }"
    ".copy-btn { background: rgba(0,255,204,0.06); border: 1px solid rgba(0,255,204,0.20); border-radius: 8px; color: #00ffcc; font-size: 11px; font-weight: 600; padding: 5px 14px; cursor: pointer; font-family: inherit; transition: background 0.2s, border-color 0.2s, color 0.2s, transform 0.2s; }"
    ".copy-btn:hover, .copy-btn.ok { background: rgba(0,255,204,0.15); border-color: rgba(0,255,204,0.45); }"
    ".trans-btn { background: rgba(176,38,255,0.06); border: 1px solid rgba(176,38,255,0.20); border-radius: 8px; color: #b026ff; font-size: 11px; font-weight: 600; padding: 5px 12px; cursor: pointer; font-family: inherit; transition: background 0.2s, border-color 0.2s, color 0.2s, transform 0.2s; margin-right: 6px; }"
    ".trans-btn:hover { background: rgba(176,38,255,0.18); border-color: rgba(176,38,255,0.45); }"
    ".content { color: rgba(255,255,255,0.72); font-size: 14px; line-height: 1.9; }"
    ".btn-row { display: flex; justify-content: flex-end; align-items: center; gap: 6px; margin-bottom: 14px; }"
    ".sec { margin-bottom: 24px; }"
    ".title-row { display: flex; align-items: center; gap: 14px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 14px 18px; margin-bottom: 8px; transition: border-color 0.2s; }"
    ".title-row:hover { border-color: rgba(0,255,204,0.18); }"
    ".tnum { font-size: 13px; color: #00ffcc; flex-shrink: 0; min-width: 26px; font-weight: 700; font-family: 'Righteous', sans-serif; }"
    ".ttxt-wrap { flex: 1; } .ttxt { font-size: 14px; font-weight: 600; color: rgba(255,255,255,0.88); line-height: 1.5; }"
    ".tag-pill { display: inline-block; background: rgba(0,255,204,0.06); border: 1px solid rgba(0,255,204,0.15); border-radius: 20px; padding: 4px 12px; margin: 3px; color: #00ffcc; font-size: 12px; font-weight: 500; transition: background 0.2s; }"
    ".tag-pill:hover { background: rgba(0,255,204,0.12); }"
    ".song-row { display: flex; align-items: flex-start; gap: 12px; padding: 14px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }"
    ".song-row:last-child { border-bottom: none; }"
    ".sinfo { flex: 1; } .stitle { font-size: 14px; font-weight: 700; color: rgba(255,255,255,0.88); margin-bottom: 6px; line-height: 1.4; }"
    ".stheme-lbl { font-size: 10px; color: #00ffcc; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 4px; }"
    ".stheme-en { font-size: 12px; color: rgba(255,255,255,0.55); line-height: 1.5; margin-bottom: 2px; }"
    ".stheme-zh { font-size: 12px; color: rgba(255,255,255,0.55); line-height: 1.5; font-style: italic; }"
    "@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; } }"
    "::-webkit-scrollbar { width: 6px; height: 6px; }"
    "::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); border-radius: 3px; }"
    "::-webkit-scrollbar-thumb { background: rgba(0,255,204,0.25); border-radius: 3px; }"
    "::-webkit-scrollbar-thumb:hover { background: rgba(0,255,204,0.40); }"
    "html { scrollbar-color: rgba(0,255,204,0.25) rgba(255,255,255,0.02); scrollbar-width: thin; }"
)

_JS = (
    "function _cp(t,ok,fail){"
    "if(navigator.clipboard&&navigator.clipboard.writeText){"
    "navigator.clipboard.writeText(t).then(ok).catch(function(){"
    "var a=document.createElement('textarea');a.value=t;a.style.cssText='position:fixed;opacity:0;'"
    ";document.body.appendChild(a);a.select();"
    "try{document.execCommand('copy');ok();}catch(e){fail();}document.body.removeChild(a);});}"
    "else{var a=document.createElement('textarea');a.value=t;a.style.cssText='position:fixed;opacity:0;'"
    ";document.body.appendChild(a);a.select();"
    "try{document.execCommand('copy');ok();}catch(e){fail();}document.body.removeChild(a);}}"
    "function _ok(b){return function(){b.textContent='已複製 ✓';b.classList.add('ok');"
    "setTimeout(function(){b.textContent='複製';b.classList.remove('ok');},1500);}}"
    "function _fail(b){return function(){b.textContent='失敗';"
    "setTimeout(function(){b.textContent='複製';},1500);}}"
    "function doCopy(b){_cp(b.getAttribute('data-text'),_ok(b),_fail(b));}"
    "function doCopyBi(b){"
    "var w=b.closest('[data-lang]');"
    "var l=w?w.getAttribute('data-lang'):'en';"
    "var t=l==='zh'?b.getAttribute('data-zh'):b.getAttribute('data-en');"
    "_cp(t,_ok(b),_fail(b));}"
    "function toggleLang(b){"
    "var w=b.closest('[data-lang]');"
    "var l=w.getAttribute('data-lang')==='en'?'zh':'en';"
    "w.setAttribute('data-lang',l);"
    "w.querySelectorAll('.en-block').forEach(function(e){e.style.display=l==='en'?'':'none';});"
    "w.querySelectorAll('.zh-block').forEach(function(e){e.style.display=l==='zh'?'':'none';});"
    "b.textContent=l==='en'?'🌐 中文':'🌐 EN';}"
)


# ─────────────────────────────────────────────────────────────────────────────
#  HTML 頁面 & 區段建構
# ─────────────────────────────────────────────────────────────────────────────
def _html_page(body: str) -> str:
    return (
        f'<!DOCTYPE html><html><head><meta charset="UTF-8">'
        f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Righteous&display=swap">'
        f'<style>{_BASE_CSS}</style></head>'
        f'<body>{body}<script>{_JS}</script></body></html>'
    )


def _story_sec(label: str, en: str, zh: str) -> str:
    return (
        f'<div class="sec" data-lang="en">'
        f'<div class="lbl">{label}</div>'
        f'<div class="card">'
        f'<div class="btn-row">'
        f'<button class="trans-btn" onclick="toggleLang(this)">🌐 中文</button>'
        f'<button class="copy-btn" data-en="{_ae(en)}" data-zh="{_ae(zh)}" onclick="doCopyBi(this)">複製</button>'
        f'</div>'
        f'<div class="en-block content">{_he(en)}</div>'
        f'<div class="zh-block content" style="display:none">{_he(zh)}</div>'
        f'</div></div>'
    )


def _titles_sec(titles_en: list, titles_zh: list) -> str:
    pairs = list(zip(titles_en, titles_zh or titles_en))
    rows = "".join(
        f'<div class="title-row">'
        f'<span class="tnum">#{i}</span>'
        f'<div class="ttxt-wrap">'
        f'<span class="en-block ttxt">{_he(en)}</span>'
        f'<span class="zh-block ttxt" style="display:none">{_he(zh)}</span>'
        f'</div>'
        f'<button class="copy-btn" style="flex-shrink:0;align-self:center;padding:3px 8px;font-size:11px;"'
        f' data-en="{_ae(en)}" data-zh="{_ae(zh)}" onclick="doCopyBi(this)">複製</button>'
        f'</div>'
        for i, (en, zh) in enumerate(pairs, 1)
    )
    return (
        f'<div class="sec" data-lang="en">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
        f'<div class="lbl" style="margin:0;">🏆 High-Click Titles'
        f'&nbsp;<span style="color:rgba(255,255,255,0.50);font-size:12px;font-weight:400;letter-spacing:0;">'
        f'{len(pairs)} titles · ranked by CTR</span></div>'
        f'<button class="trans-btn" onclick="toggleLang(this)">🌐 中文</button>'
        f'</div>'
        f'{rows}</div>'
    )


def _tags_sec(tags_str: str) -> str:
    count = len(tags_str)
    pills = "".join(
        f'<span class="tag-pill">{_he(t.strip())}</span>'
        for t in tags_str.split(',') if t.strip()
    )
    return (
        f'<div class="sec"><div class="lbl">🏷️ SEO Tags'
        f'&nbsp;<span style="color:rgba(255,255,255,0.50);font-size:12px;font-weight:400;letter-spacing:0;">'
        f'{count} / 500</span></div>'
        f'<div class="card">'
        f'<div class="btn-row"><button class="copy-btn" data-text="{_ae(tags_str)}" onclick="doCopy(this)">複製</button></div>'
        f'{pills}</div></div>'
    )


def _songs_sec(songs: list) -> str:
    rows = ""
    for i, s in enumerate(songs, 1):
        en, zh = s.get("en_title", ""), s.get("zh_title", "")
        et, zt = s.get("en_theme", ""), s.get("zh_theme", "")
        ct = f"{i}. 《{en}》 {zh}\nLyric Theme: {et}\n{zt}"
        rows += (
            f'<div class="song-row">'
            f'<div class="sinfo">'
            f'<div class="stitle">{i}. 《{_he(en)}》　{_he(zh)}</div>'
            f'<div class="stheme-lbl">Lyric Theme</div>'
            f'<div class="stheme-en">{_he(et)}</div>'
            f'<div class="stheme-zh">{_he(zt)}</div>'
            f'</div>'
            f'<button class="copy-btn" style="flex-shrink:0;align-self:flex-start;margin-top:2px;"'
            f' data-text="{_ae(ct)}" onclick="doCopy(this)">複製</button>'
            f'</div>'
        )
    n = len(songs)
    return (
        f'<div class="sec"><div class="lbl">🎵 Tracklist'
        f'&nbsp;<span style="color:rgba(255,255,255,0.50);font-size:11px;font-weight:400;letter-spacing:0;">'
        f'{n} track{"s" if n != 1 else ""}</span></div>'
        f'<div class="card">{rows}</div></div>'
    )


def build_dashboard(results: dict, selected_outputs: list) -> str:
    """Build HTML dashboard with only the selected output sections."""
    body = ""
    if "tracklist" in selected_outputs and results.get("tracklist"):
        body += _songs_sec(results["tracklist"])
    if "long_story" in selected_outputs and results.get("long_story"):
        body += _story_sec("📖 Long Story",
                           results["long_story"], results.get("long_story_zh", ""))
    if "short_story" in selected_outputs and results.get("short_story"):
        body += _story_sec("💬 Short Story",
                           results["short_story"], results.get("short_story_zh", ""))
    if "titles" in selected_outputs and results.get("titles"):
        body += _titles_sec(results["titles"], results.get("titles_zh", []))
    if "tags" in selected_outputs and results.get("tags"):
        body += _tags_sec(results["tags"])
    return _html_page(body)
