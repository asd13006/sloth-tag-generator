"""
sLoth rAdio · Title Studio — Dynamic Wizard Mode (DEMO)
No API key required. Uses mock data to demonstrate the 4-step wizard flow.

UI Language: Traditional Chinese
Design: OLED Dark + Neon Teal (#00ffcc / #b026ff)
"""

import time
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="sLoth rAdio · Title Studio (Demo)",
    page_icon="🎵",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS  ── OLED Dark + Neon Cyberpunk design system
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Righteous&display=swap');

/* ── Base ── */
html, body, [class*="css"] { font-family: 'Poppins', -apple-system, sans-serif; color-scheme: dark; }
.stApp {
    background-color: #0A0A14 !important;
    background-image:
        radial-gradient(ellipse 80% 60% at 50% 0%, rgba(0,255,204,0.04) 0%, transparent 60%),
        radial-gradient(rgba(0,255,204,0.025) 1px, transparent 1px) !important;
    background-size: 100% 100%, 30px 30px !important;
}
.block-container { padding: 1.5rem 2.5rem 3rem !important; max-width: 1200px !important; }
.stApp > header { background: transparent !important; }

/* ── Animations ── */
@keyframes gradient-text { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
@keyframes neon-breathe { 0%, 100% { box-shadow: 0 0 8px rgba(0,255,204,0.15), inset 0 0 8px rgba(0,255,204,0.03); } 50% { box-shadow: 0 0 16px rgba(0,255,204,0.28), inset 0 0 12px rgba(0,255,204,0.05); } }
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; }
}

/* ── Header ── */
.hdr { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.hdr-left { display: flex; align-items: baseline; gap: 14px; }
.hdr-title {
    font-family: 'Righteous', sans-serif; font-size: 32px; font-weight: 400; letter-spacing: 1px;
    background: linear-gradient(270deg, #00ffcc, #b026ff, #00E676, #00ffcc); background-size: 300% 300%;
    animation: gradient-text 5s ease 1 forwards;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hdr-sub { color: rgba(255,255,255,0.40); font-size: 11px; font-weight: 500; letter-spacing: 3px; text-transform: uppercase; }
.demo-pill {
    display: inline-block; background: rgba(255,180,0,0.10); border: 1px solid rgba(255,180,0,0.25);
    border-radius: 20px; padding: 2px 12px; font-size: 10px; font-weight: 700;
    color: rgba(255,180,0,0.85); letter-spacing: 1.5px; text-transform: uppercase; vertical-align: middle; margin-left: 10px;
}

/* ── Stepper ── */
.stepper { display: flex; align-items: center; margin: 16px 0 24px; }
.s-item { display: flex; align-items: center; gap: 8px; }
.s-item:not(:last-child) { flex: 1; }
.s-dot {
    width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; flex-shrink: 0; transition: all 0.3s ease;
    border: 2px solid rgba(255,255,255,0.20); color: rgba(255,255,255,0.30); background: transparent;
}
.s-dot.active { border-color: #00ffcc; color: #00ffcc; background: rgba(0,255,204,0.12); box-shadow: 0 0 14px rgba(0,255,204,0.5); }
.s-dot.done { border-color: rgba(0,255,204,0.4); color: rgba(0,255,204,0.6); background: rgba(0,255,204,0.06); }
.s-lbl { font-size: 12px; font-weight: 500; color: rgba(255,255,255,0.35); white-space: nowrap; }
.s-lbl.active { color: #00ffcc; font-weight: 700; }
.s-lbl.done { color: rgba(0,255,204,0.45); }
.s-line { flex: 1; height: 1px; background: rgba(255,255,255,0.06); margin: 0 14px; }
.s-line.done { background: linear-gradient(90deg, rgba(0,255,204,0.3), rgba(0,255,204,0.08)); }

/* ── Glass Container ── */
.glass {
    background: rgba(14,14,24,0.75); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.06); border-radius: 20px;
    padding: 36px 40px 32px; margin-bottom: 20px; position: relative; overflow: hidden;
}
.glass::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,255,204,0.15), rgba(176,38,255,0.1), transparent);
}

/* ── Section text ── */
.sec-title { font-family: 'Righteous', sans-serif; font-size: 22px; color: #FFFFFF; margin: 0 0 4px; letter-spacing: 0.5px; }
.sec-desc { font-size: 13px; color: rgba(255,255,255,0.45); margin: 0 0 28px; line-height: 1.6; }

/* ── Card-style buttons (icon + name, 2 paragraphs) ── */
button[data-testid^="baseButton"]:has(p:nth-of-type(2)),
button[data-testid^="stBaseButton"]:has(p:nth-of-type(2)) {
    min-height: 100px !important; height: 100px !important;
    display: flex !important; flex-direction: column !important;
    justify-content: center !important; align-items: center !important;
    text-align: center !important; white-space: normal !important;
    padding: 12px 8px !important; gap: 0 !important;
}
button:has(p:nth-of-type(2)) p { margin: 0 !important; padding: 0 !important; }
button:has(p:nth-of-type(2)) p:nth-of-type(1) { font-size: 28px !important; line-height: 1.2 !important; margin-bottom: 6px !important; }
button:has(p:nth-of-type(2)) p:nth-of-type(2) { font-size: 13px !important; font-weight: 600 !important; }
button[data-testid="baseButton-secondary"]:has(p:nth-of-type(2)) p:nth-of-type(2) { color: rgba(255,255,255,0.75) !important; }

/* ── All buttons base ── */
button[data-testid^="baseButton"], button[data-testid^="stBaseButton"] {
    cursor: pointer !important; border-radius: 14px !important; transition: all 0.25s ease !important;
}

/* ── Secondary (unselected) ── */
button[data-testid="baseButton-secondary"],
button[data-testid="stBaseButton-secondary"] {
    background: rgba(255,255,255,0.025) !important; border: 1.5px solid rgba(255,255,255,0.10) !important;
    color: rgba(255,255,255,0.55) !important;
}
button[data-testid="baseButton-secondary"]:hover,
button[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(255,255,255,0.06) !important; border-color: rgba(255,255,255,0.30) !important;
    transform: translateY(-2px) !important; box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important;
}

/* ── Primary (selected / action) ── */
button[data-testid="baseButton-primary"],
button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, rgba(0,255,204,0.08), rgba(176,38,255,0.06)) !important;
    border: 1.5px solid rgba(0,255,204,0.50) !important; color: #00ffcc !important;
    font-weight: 600 !important; animation: neon-breathe 3s ease-in-out infinite !important;
}
button[data-testid="baseButton-primary"] p,
button[data-testid="stBaseButton-primary"] p { color: #00ffcc !important; }
button[data-testid="baseButton-primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 28px rgba(0,255,204,0.25), 0 8px 24px rgba(0,0,0,0.4) !important;
}

/* ── Info / Review cards ── */
.info-card {
    background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 18px 22px; margin-bottom: 16px;
}
.review-card {
    background: rgba(176,38,255,0.04); border-left: 3px solid #b026ff;
    border-radius: 0 14px 14px 0; padding: 20px 24px; margin-bottom: 20px;
}
.review-label { font-size: 11px; font-weight: 600; color: #b026ff; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px; }
.review-text { color: rgba(255,255,255,0.65); font-size: 14px; line-height: 1.8; white-space: pre-wrap; }

/* ── Chip / pill ── */
.chip {
    display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; margin: 3px 4px;
}
.chip-teal { background: rgba(0,255,204,0.08); border: 1px solid rgba(0,255,204,0.25); color: #00ffcc; }
.chip-purple { background: rgba(176,38,255,0.08); border: 1px solid rgba(176,38,255,0.25); color: #b026ff; }

/* ── Card description (under buttons) ── */
.card-desc { text-align: center; font-size: 11px; color: rgba(255,255,255,0.38); margin-top: 6px; line-height: 1.4; }

/* ── Counter ── */
.counter { text-align: center; margin: 12px 0 4px; font-size: 13px; color: rgba(255,255,255,0.40); }
.counter b { font-size: 20px; font-family: 'Righteous', sans-serif; }
.counter b.teal { color: #00ffcc; }
.counter b.purple { color: #b026ff; }

/* ── Feature cards ── */
.feat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 20px; }
.feat-card {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
    border-radius: 16px; padding: 28px 20px; text-align: center; transition: all 0.25s ease;
}
.feat-card:hover { border-color: rgba(255,255,255,0.12); transform: translateY(-2px); }
.feat-icon { font-size: 28px; margin-bottom: 12px; }
.feat-title { font-size: 14px; font-weight: 600; color: rgba(255,255,255,0.80); margin-bottom: 6px; }
.feat-desc { font-size: 12px; color: rgba(255,255,255,0.42); line-height: 1.6; }

/* ── Nav spacer ── */
.nav-spacer { height: 12px; }

/* ── Inputs ── */
[data-baseweb="textarea"] { border-radius: 14px !important; }
[data-baseweb="textarea"] textarea { background: rgba(255,255,255,0.03) !important; color: rgba(255,255,255,0.85) !important; font-size: 14px !important; line-height: 1.7 !important; }
[data-baseweb="textarea"]:focus-within { border-color: rgba(0,255,204,0.45) !important; box-shadow: 0 0 0 2px rgba(0,255,204,0.08), 0 0 20px rgba(0,255,204,0.06) !important; }

/* ── Misc ── */
hr { border-color: rgba(255,255,255,0.05) !important; }
a, a:visited { color: #00ffcc !important; }
button:focus, button:focus-visible { outline: 2px solid rgba(0,255,204,0.45) !important; outline-offset: 2px !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-thumb { background: rgba(0,255,204,0.30); border-radius: 2px; }
.stSlider > div { padding-left: 0 !important; }

/* ── Footer ── */
.footer { text-align: center; color: rgba(255,255,255,0.25); font-size: 10px; letter-spacing: 2px; margin-top: 40px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MOCK DATA  ── realistic lofi-themed content for demo
# ─────────────────────────────────────────────────────────────────────────────
_MOCK_TITLES_EN = [
    "Midnight Pages… Chill Lofi for Late Night Study & Focus 📚 🌙",
    "Rainy Café Daydream… Cozy Lofi for Relaxation & Calm ☕ 🌧️",
    "Warm Silence… Soothing Jazz Lofi for Sleep & Comfort 🕯️ 💤",
    "Paper & Ink… Gentle Lofi for Writing, Reading & Peace ✒️ 🍃",
    "Golden Hour Drift… Soft Lofi for Afternoon Chill & Vibes 🌅 🎧",
]
_MOCK_TITLES_ZH = [
    "午夜書頁… 深夜讀書＆專注的 Chill Lofi 📚 🌙",
    "雨天咖啡白日夢… 放鬆＆平靜的溫暖 Lofi ☕ 🌧️",
    "溫暖的沉默… 助眠＆舒適的爵士 Lofi 🕯️ 💤",
    "紙與墨… 書寫、閱讀＆寧靜的輕柔 Lofi ✒️ 🍃",
    "金色時光漫遊… 午後放鬆＆氛圍的柔和 Lofi 🌅 🎧",
]
_MOCK_TAGS = (
    "lofi, lofi music, chill lofi, lofi hip hop, lofi beats, study music, "
    "relax music, chill music, cozy lofi, rainy day lofi, lofi cafe, "
    "late night lofi, lofi jazz, soothing music, ambient lofi, sleep lofi, "
    "focus music, lo-fi, chillhop, lofi radio, lofi mix, soft lofi, "
    "reading music, writing music, peaceful music, calm beats, "
    "midnight study lofi, rainy cafe ambience, warm lofi vibes, "
    "aesthetic lofi, lofi for work, deep focus lofi, cozy night lofi, "
    "gentle piano lofi, autumn lofi, winter lofi playlist, lofi 2024, "
    "morning coffee lofi, sunday lofi, healing lofi beats"
)
_MOCK_LONG_STORY_EN = (
    "You sit by the window, watching raindrops trace slow paths down the glass. "
    "The café is nearly empty — just you, a half-finished cup of tea, and the quiet hum of a lofi playlist "
    "drifting from somewhere behind the counter.\n\n"
    "Outside, the city feels far away. Streetlights blur into soft halos through the rain, "
    "and the occasional car passes like a whisper. You open your notebook, but there's no rush to write. "
    "Tonight, just being here is enough.\n\n"
    "The barista wipes down the espresso machine with practiced ease, glancing at the clock but never hurrying. "
    "A stack of old paperbacks sits on the shelf by the door — someone left them here months ago, "
    "and now they belong to no one and everyone.\n\n"
    "You pick up your pen. The first sentence comes slowly, then another, then a whole paragraph "
    "that feels like it was always waiting inside you. The rain keeps its gentle rhythm, "
    "and the lofi beats carry you forward, one soft note at a time.\n\n"
    "When you finally look up, the tea has gone cold and the rain has stopped. "
    "But the words on the page glow warm, and you smile — knowing that some of the best things "
    "are written in the quiet hours, when no one is watching."
)
_MOCK_LONG_STORY_ZH = (
    "你坐在窗邊，看著雨滴在玻璃上緩緩滑落。咖啡廳裡幾乎空無一人——"
    "只有你、一杯喝了一半的茶，和從吧台後方某處飄來的 lofi 音樂。\n\n"
    "窗外，城市彷彿很遙遠。街燈在雨中暈成柔和的光圈，"
    "偶爾有車經過，像一聲低語。你翻開筆記本，但不急著寫。"
    "今夜，就只是待在這裡，已經足夠。\n\n"
    "咖啡師熟練地擦拭義式咖啡機，看了一眼時鐘，卻從不趕時間。"
    "門邊的書架上放著一疊舊平裝書——幾個月前有人留下的，"
    "現在它們不屬於任何人，又屬於每個人。\n\n"
    "你拿起筆。第一句話來得很慢，然後又一句，接著是一整段——"
    "那些文字彷彿一直在你心裡等候。雨聲保持著溫柔的節奏，"
    "lofi 的音符帶著你前行，一個柔和的音符接著一個。\n\n"
    "當你終於抬起頭，茶已經涼了，雨也停了。"
    "但紙上的文字散發著溫暖的光，你微笑——因為最好的東西，"
    "往往是在安靜的時刻、無人注視時寫下的。"
)
_MOCK_SHORT_STORY_EN = (
    "Late night. Warm lights. A half-finished cup of tea and nowhere to be. ☕🌙\n\n"
    "The rain taps gently on the window while lofi melodies fill the quiet corners of the café. "
    "You write. You dream. You breathe. 📝✨\n\n"
    "Some nights don't need a plan — just a playlist, a pen, and the permission to simply exist. "
    "This is one of those nights. 🌧️💫\n\n"
    "Stay cozy. Stay curious. The best stories begin in silence. 🍃"
)
_MOCK_SHORT_STORY_ZH = (
    "深夜。暖光。一杯喝了一半的茶，哪裡也不用去。☕🌙\n\n"
    "雨輕輕敲著窗戶，lofi 旋律填滿了咖啡廳安靜的角落。"
    "你書寫。你做夢。你呼吸。📝✨\n\n"
    "有些夜晚不需要計畫——只需要一張播放清單、一支筆，"
    "和允許自己單純存在的勇氣。今夜就是這樣的夜晚。🌧️💫\n\n"
    "保持溫暖。保持好奇。最好的故事，始於寂靜。🍃"
)
_MOCK_TRACKLIST = [
    {"id": 1, "en_title": "Midnight Pages", "zh_title": "午夜書頁",
     "en_theme": "Quiet pen scratches under a dim desk lamp", "zh_theme": "昏暗檯燈下筆尖沙沙的聲音"},
    {"id": 2, "en_title": "Rainy Café", "zh_title": "雨天咖啡館",
     "en_theme": "Raindrops on glass and the scent of fresh brew", "zh_theme": "玻璃上的雨滴和新煮咖啡的香氣"},
    {"id": 3, "en_title": "Paper & Ink", "zh_title": "紙與墨",
     "en_theme": "A worn journal filled with half-finished thoughts", "zh_theme": "一本寫滿未完思緒的舊日記"},
    {"id": 4, "en_title": "Warm Silence", "zh_title": "溫暖的沉默",
     "en_theme": "Two cups of tea, no words needed", "zh_theme": "兩杯茶，不需要言語"},
    {"id": 5, "en_title": "Golden Hour Drift", "zh_title": "金色時光漫遊",
     "en_theme": "Sunlight fading through linen curtains", "zh_theme": "陽光透過亞麻窗簾漸漸消逝"},
    {"id": 6, "en_title": "Autumn Letters", "zh_title": "秋日信箋",
     "en_theme": "A letter you meant to send but never did", "zh_theme": "一封你想寄出卻始終沒寄的信"},
    {"id": 7, "en_title": "Foggy Window Sill", "zh_title": "霧氣窗台",
     "en_theme": "Drawing shapes on a fogged-up window", "zh_theme": "在起霧的玻璃上隨手畫圖案"},
    {"id": 8, "en_title": "Bookshop Lullaby", "zh_title": "書店搖籃曲",
     "en_theme": "Old books and the creak of wooden floors", "zh_theme": "舊書和木地板的吱嘎聲"},
    {"id": 9, "en_title": "Slow Morning", "zh_title": "緩慢的早晨",
     "en_theme": "No alarm, just birdsong and soft light", "zh_theme": "沒有鬧鐘，只有鳥鳴和柔光"},
    {"id": 10, "en_title": "Last Train Home", "zh_title": "末班車回家",
     "en_theme": "City lights blurring past a tired smile", "zh_theme": "城市燈光在疲倦的微笑前模糊而過"},
]


# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "step": 1,
    "selected_outputs": [],      # 想生成咩：titles / tags / long_story / short_story / tracklist
    "existing_materials": [],    # 已有嘅材料（同樣 5 類）
    "user_context": "",          # Step 3 用戶輸入
    "n_songs": 15,               # 歌單數量
    "results": {},               # AI / mock 結果
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_pipeline():
    for k, v in _DEFAULTS.items():
        st.session_state[k] = v if not isinstance(
            v, (list, dict)) else type(v)()


# ─────────────────────────────────────────────────────────────────────────────
#  MOCK AI  (demo mode — no API key needed)
# ─────────────────────────────────────────────────────────────────────────────
def mock_generate(selected_outputs: list, n_songs: int) -> dict:
    """Simulate AI generation with mock data. Returns only the requested keys."""
    time.sleep(1.5)  # 模擬 loading
    result = {}
    if "titles" in selected_outputs:
        result["titles"] = _MOCK_TITLES_EN
        result["titles_zh"] = _MOCK_TITLES_ZH
    if "tags" in selected_outputs:
        result["tags"] = _MOCK_TAGS
    if "long_story" in selected_outputs:
        result["long_story"] = _MOCK_LONG_STORY_EN
        result["long_story_zh"] = _MOCK_LONG_STORY_ZH
    if "short_story" in selected_outputs:
        result["short_story"] = _MOCK_SHORT_STORY_EN
        result["short_story_zh"] = _MOCK_SHORT_STORY_ZH
    if "tracklist" in selected_outputs:
        result["tracklist"] = _MOCK_TRACKLIST[:n_songs]
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  HTML HELPERS  (dashboard iframes — reused from original)
# ─────────────────────────────────────────────────────────────────────────────
def _ae(t: str) -> str:
    return t.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&#39;').replace('<', '&lt;').replace('>', '&gt;')


def _he(t: str) -> str:
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')


_BASE_CSS = (
    "* { box-sizing: border-box; margin: 0; padding: 0; }"
    "html, body { background: transparent; font-family: 'Poppins', -apple-system, sans-serif; overflow-x: hidden; color: #e8e8f0; }"
    ".lbl { font-size: 11px; font-weight: 700; color: #00ffcc; letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 12px; }"
    ".card { background: rgba(14,14,24,0.6); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 20px 22px; }"
    ".copy-btn { background: rgba(0,255,204,0.06); border: 1px solid rgba(0,255,204,0.20); border-radius: 8px; color: #00ffcc; font-size: 11px; font-weight: 600; padding: 5px 14px; cursor: pointer; font-family: inherit; transition: all 0.2s; }"
    ".copy-btn:hover, .copy-btn.ok { background: rgba(0,255,204,0.15); border-color: rgba(0,255,204,0.45); }"
    ".trans-btn { background: rgba(176,38,255,0.06); border: 1px solid rgba(176,38,255,0.20); border-radius: 8px; color: #b026ff; font-size: 11px; font-weight: 600; padding: 5px 12px; cursor: pointer; font-family: inherit; transition: all 0.2s; margin-right: 6px; }"
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
    ".stheme-zh { font-size: 12px; color: rgba(255,255,255,0.40); line-height: 1.5; font-style: italic; }"
    "@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; } }"
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


# ─────────────────────────────────────────────────────────────────────────────
#  OPTION DEFINITIONS (shared by Step 1 & Step 2)
# ─────────────────────────────────────────────────────────────────────────────
_OPTIONS = [
    ("titles",      "🏆", "YouTube 標題",  "5 個高點擊率標題"),
    ("tags",        "🏷️", "YouTube 標籤",  "450-500 字元 SEO Tags"),
    ("long_story",  "📖", "長故事",         "4-6 段沉浸式散文"),
    ("short_story", "💬", "短故事",         "Instagram 風格短文"),
    ("tracklist",   "🎵", "Suno 歌單",     "詩意歌名與意境"),
]

_MATERIAL_LABELS = {
    "titles": "標題", "tags": "標籤",
    "long_story": "長故事", "short_story": "短故事", "tracklist": "歌單",
}


# ═════════════════════════════════════════════════════════════════════════════
#  HEADER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='hdr'>"
    "<div class='hdr-left'>"
    "<span class='hdr-title'>Title Studio</span>"
    "<span class='demo-pill'>Demo</span>"
    "<span class='hdr-sub'>sLoth rAdio</span>"
    "</div></div>",
    unsafe_allow_html=True,
)

# ── Stepper ──
step = st.session_state.step
_steps = ["🎯 目標", "📦 材料", "📝 輸入", "📊 成果"]
_sh = "<div class='stepper'>"
for _i, _lbl in enumerate(_steps, 1):
    cls = "active" if _i == step else ("done" if _i < step else "")
    _sh += f"<div class='s-item'><div class='s-dot {cls}'>{'✓' if _i < step else _i}</div><span class='s-lbl {cls}'>{_lbl}</span></div>"
    if _i < len(_steps):
        _sh += f"<div class='s-line {'done' if _i < step else ''}'></div>"
_sh += "</div>"
st.markdown(_sh, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  STEP 1 — 確認目標
# ═════════════════════════════════════════════════════════════════════════════
if step == 1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sec-title'>今日想我幫手生成啲咩？</div>"
        "<div class='sec-desc'>可多選 · 至少揀一項先可以繼續</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(5, gap="medium")
    for ci, (key, icon, name, desc) in enumerate(_OPTIONS):
        with cols[ci]:
            is_sel = key in st.session_state.selected_outputs
            if st.button(
                f"{icon}\n\n**{name}**",
                key=f"out_{key}",
                type="primary" if is_sel else "secondary",
                use_container_width=True,
            ):
                if is_sel:
                    st.session_state.selected_outputs.remove(key)
                else:
                    st.session_state.selected_outputs.append(key)
                st.rerun()
            st.markdown(
                f"<div class='card-desc'>{desc}</div>", unsafe_allow_html=True)

    n_sel = len(st.session_state.selected_outputs)
    st.markdown(
        f"<div class='counter'>已選 <b class='teal'>{n_sel}</b> 項</div>", unsafe_allow_html=True)

    # Navigation
    st.markdown("<div class='nav-spacer'></div>", unsafe_allow_html=True)
    nav_l, _, nav_r = st.columns([1, 3, 1])
    with nav_l:
        if st.button("✓ 全選直入", use_container_width=True):
            st.session_state.selected_outputs = [k for k, *_ in _OPTIONS]
            st.session_state.existing_materials = []
            st.session_state.step = 3
            st.rerun()
    with nav_r:
        if st.button("下一步 →", type="primary", use_container_width=True, disabled=(n_sel == 0)):
            st.session_state.step = 2
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # close .glass

    # Feature cards (landing — only when nothing selected)
    if n_sel == 0:
        st.markdown(
            "<div class='feat-grid'>"
            "<div class='feat-card'><div class='feat-icon'>✨</div><div class='feat-title'>動態嚮導</div><div class='feat-desc'>根據你嘅選擇，自動調整問題同 AI Prompt</div></div>"
            "<div class='feat-card'><div class='feat-icon'>🎯</div><div class='feat-title'>精準生成</div><div class='feat-desc'>告訴 AI 你已有咩材料，生成更貼切嘅結果</div></div>"
            "<div class='feat-card'><div class='feat-icon'>📋</div><div class='feat-title'>按需展示</div><div class='feat-desc'>只顯示你揀咗嘅內容，版面乾淨利落</div></div>"
            "</div>",
            unsafe_allow_html=True,
        )


# ═════════════════════════════════════════════════════════════════════════════
#  STEP 2 — 現有材料
# ═════════════════════════════════════════════════════════════════════════════
elif step == 2:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sec-title'>你手上已經有啲咩材料？</div>"
        "<div class='sec-desc'>可多選 · 冇都可以直接跳過</div>",
        unsafe_allow_html=True,
    )

    # Context chips — what they're generating
    gen_chips = " ".join(
        f"<span class='chip chip-teal'>{_MATERIAL_LABELS[k]}</span>" for k in st.session_state.selected_outputs)
    st.markdown(
        f"<div class='info-card'><span style='font-size:12px;color:rgba(255,255,255,0.45);'>你要生成：</span><br>{gen_chips}</div>",
        unsafe_allow_html=True,
    )

    # Filter out items the user wants to generate
    available = [(k, ic, nm, ds) for k, ic, nm,
                 ds in _OPTIONS if k not in st.session_state.selected_outputs]

    if not available:
        st.markdown(
            "<div style='text-align:center;padding:32px 0;color:rgba(255,255,255,0.40);font-size:14px;'>"
            "你選擇生成所有類型，冇需要提供已有材料。直接跳到輸入頁面吧！</div>",
            unsafe_allow_html=True,
        )
    else:
        cols = st.columns(len(available), gap="medium")
        for ci, (key, icon, name, _) in enumerate(available):
            with cols[ci]:
                is_sel = key in st.session_state.existing_materials
                if st.button(f"{icon}\n\n**已有{name}**", key=f"mat_{key}",
                             type="primary" if is_sel else "secondary", use_container_width=True):
                    if is_sel:
                        st.session_state.existing_materials.remove(key)
                    else:
                        st.session_state.existing_materials.append(key)
                    st.rerun()

    n_mat = len(st.session_state.existing_materials)
    st.markdown(
        f"<div class='counter'>已選 <b class='purple'>{n_mat}</b> 項材料</div>", unsafe_allow_html=True)

    # Navigation
    st.markdown("<div class='nav-spacer'></div>", unsafe_allow_html=True)
    nav_l, nav_skip, _, nav_r = st.columns([1, 1.5, 1.5, 1])
    with nav_l:
        if st.button("← 返回", key="s2_back", use_container_width=True):
            st.session_state.existing_materials = []
            st.session_state.step = 1
            st.rerun()
    with nav_skip:
        if st.button("跳過，從零開始", key="s2_skip", use_container_width=True):
            st.session_state.existing_materials = []
            st.session_state.step = 3
            st.rerun()
    with nav_r:
        if st.button("下一步 →", key="s2_next", type="primary", use_container_width=True):
            st.session_state.step = 3
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # close .glass


# ═════════════════════════════════════════════════════════════════════════════
#  STEP 3 — 收集上下文
# ═════════════════════════════════════════════════════════════════════════════
elif step == 3:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>📝 提供你嘅素材</div>",
                unsafe_allow_html=True)

    # Context summary chips
    gen_chips = " ".join(
        f"<span class='chip chip-teal'>{_MATERIAL_LABELS[k]}</span>" for k in st.session_state.selected_outputs)
    mat_chips = " ".join(
        f"<span class='chip chip-purple'>{_MATERIAL_LABELS[k]}</span>" for k in st.session_state.existing_materials)

    summary = f"<div class='info-card'><div style='margin-bottom:8px;'><span style='font-size:12px;color:rgba(255,255,255,0.45);'>要生成：</span> {gen_chips}</div>"
    if mat_chips:
        summary += f"<div><span style='font-size:12px;color:rgba(255,255,255,0.45);'>已有材料：</span> {mat_chips}</div>"
    summary += "</div>"
    st.markdown(summary, unsafe_allow_html=True)

    # Dynamic prompt
    gen_names = "、".join(_MATERIAL_LABELS[k]
                         for k in st.session_state.selected_outputs)
    mat_names = "、".join(_MATERIAL_LABELS[k]
                         for k in st.session_state.existing_materials)

    if st.session_state.existing_materials:
        hint = f"請將已有嘅 {mat_names} 同任何靈感貼喺下面，我會用嚟生成 {gen_names}："
    elif st.session_state.selected_outputs == ["tracklist"]:
        hint = "請描述你想要嘅風格或氛圍："
    else:
        hint = f"請將你現有嘅靈感、故事或歌單貼喺下面，我會幫你生成 {gen_names}："

    st.markdown(
        f"<div class='sec-desc' style='margin-bottom:12px;'>{hint}</div>", unsafe_allow_html=True)

    user_input = st.text_area(
        "content_input",
        value=st.session_state.user_context,
        height=220,
        placeholder="例如：深夜獨自在咖啡廳讀書，窗外下著小雨，播放著溫暖的 lofi 音樂...",
        label_visibility="collapsed",
    )
    st.session_state.user_context = user_input

    # Song count slider
    if "tracklist" in st.session_state.selected_outputs:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.45);font-size:11px;letter-spacing:2px;"
            "text-transform:uppercase;margin:14px 0 4px;'>🎚️ 歌單數量</div>",
            unsafe_allow_html=True,
        )
        st.session_state.n_songs = st.slider(
            "n_songs", min_value=1, max_value=20,
            value=st.session_state.n_songs, step=1,
            label_visibility="collapsed",
        )

    # Navigation
    st.markdown("<div class='nav-spacer'></div>", unsafe_allow_html=True)
    nav_l, _, nav_r = st.columns([1, 3, 1])
    with nav_l:
        if st.button("← 返回", key="s3_back", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with nav_r:
        gen_btn = st.button("✨ 開始生成", key="s3_gen",
                            type="primary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close .glass

    if gen_btn:
        with st.status("⚙️ Demo 生成中...", expanded=True) as status:
            st.write("🤖 使用 Mock Data 模擬 AI 生成...")
            results = mock_generate(
                st.session_state.selected_outputs, st.session_state.n_songs)
            if results:
                st.session_state.results = results
                status.update(label="✅ 完成！", state="complete", expanded=False)
            else:
                status.update(label="❌ 生成失敗", state="error", expanded=False)
        if st.session_state.results:
            st.session_state.step = 4
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
#  STEP 4 — 結果看板
# ═════════════════════════════════════════════════════════════════════════════
elif step == 4:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sec-title'>📊 成果總覽</div>"
        "<div class='sec-desc'>複製你需要嘅內容 → YouTube Studio 🎬</div>",
        unsafe_allow_html=True,
    )

    # Review card
    ctx = st.session_state.user_context.strip()
    if ctx:
        mat_chips = " ".join(
            f"<span class='chip chip-purple'>{_MATERIAL_LABELS[k]}</span>" for k in st.session_state.existing_materials)
        mat_line = f"<div style='margin-top:10px;'>{mat_chips}</div>" if mat_chips else ""
        st.markdown(
            f"<div class='review-card'>"
            f"<div class='review-label'>根據你提供的資訊</div>"
            f"<div class='review-text'>{_he(ctx)}</div>"
            f"{mat_line}</div>",
            unsafe_allow_html=True,
        )

    # Dashboard iframe
    r = st.session_state.results
    selected = st.session_state.selected_outputs
    html = build_dashboard(r, selected)

    h = 0
    if "tracklist" in selected and r.get("tracklist"):
        h += 110 * len(r["tracklist"]) + 80
    if "long_story" in selected:
        h += 420
    if "short_story" in selected:
        h += 300
    if "titles" in selected and r.get("titles"):
        h += 90 * len(r["titles"]) + 80
    if "tags" in selected:
        h += 260
    h = max(h, 400)

    st.components.v1.html(html, height=h, scrolling=True)

    # Navigation
    st.markdown("<div class='nav-spacer'></div>", unsafe_allow_html=True)
    nav_l, _, nav_r = st.columns([1, 3, 1])
    with nav_l:
        if st.button("← 返回修改", key="s4_back", use_container_width=True):
            st.session_state.results = {}
            st.session_state.step = 3
            st.rerun()
    with nav_r:
        if st.button("🔄 開始新企劃", key="s4_new", type="primary", use_container_width=True):
            reset_pipeline()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # close .glass


# ═════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='footer'>sLoth rAdio · Title Studio · Dynamic Wizard Demo</div>",
            unsafe_allow_html=True)
