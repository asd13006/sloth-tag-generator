"""
Global CSS — OLED Dark + Neon Cyberpunk design system
Fonts: Poppins (body) + Righteous (display)
Accent: #00ffcc · Secondary: #b026ff · BG: #0A0A14
"""

import streamlit as st

GLOBAL_CSS = """
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
.block-container { padding: 0 2.5rem 3rem !important; max-width: 1200px !important; }
.stApp > header { display: none !important; height: 0 !important; min-height: 0 !important; }
[data-testid="stHeader"] { display: none !important; height: 0 !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
.stDeployButton { display: none !important; }
#MainMenu { display: none !important; }

/* ── Animations ── */
@keyframes gradient-text { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
@keyframes neon-breathe { 0%, 100% { box-shadow: 0 0 8px rgba(0,255,204,0.15), inset 0 0 8px rgba(0,255,204,0.03); } 50% { box-shadow: 0 0 16px rgba(0,255,204,0.28), inset 0 0 12px rgba(0,255,204,0.05); } }
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; }
}

/* ── Navbar (single-row, sticky) ── */
.st-key-navbar {
    position: sticky; top: 0; z-index: 999;
    background: rgba(10,10,20,0.92); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
    margin: 0 -2.5rem; padding: 10px 2.5rem 10px;
}
.st-key-navbar::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,255,204,0.12), rgba(176,38,255,0.08), transparent);
}
/* 品牌標題 */
.nb-brand {
    font-family: 'Righteous', sans-serif; font-size: 26px; font-weight: 400; letter-spacing: 1px;
    background: linear-gradient(270deg, #00ffcc, #b026ff, #00E676, #00ffcc); background-size: 300% 300%;
    animation: gradient-text 5s ease 1 forwards;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1.2; white-space: nowrap;
}
.nb-sub { color: rgba(255,255,255,0.45); font-size: 10px; font-weight: 500; letter-spacing: 2px; text-transform: uppercase; display: block; margin-top: -2px; }
.nb-ver { color: rgba(0,255,204,0.5); font-size: 9px; font-weight: 500; letter-spacing: 1px; display: block; margin-top: 1px; }
/* 狀態指示器 */
.api-status {
    display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px;
    border-radius: 20px; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;
    border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.03);
    white-space: nowrap;
}
.api-status-wrap { display: flex; justify-content: flex-end; align-items: center; height: 100%; }
/* 品牌/按鈕分隔線 */
.nav-sep { width: 1px; height: 24px; background: rgba(255,255,255,0.08); margin: 0 auto; }
.api-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.api-dot.off { background: #ff4757; box-shadow: 0 0 6px rgba(255,71,87,0.5); }
.api-dot.on { background: #00ffcc; box-shadow: 0 0 6px rgba(0,255,204,0.5); }
.api-dot.wait { background: #ffa502; box-shadow: 0 0 6px rgba(255,165,2,0.5); animation: neon-breathe 2s ease-in-out infinite; }
.api-lbl { color: rgba(255,255,255,0.60); }
/* 統一按鈕樣式（button + popover trigger） */
.st-key-navbar button,
.st-key-navbar [data-testid="stPopover"] > button {
    min-height: 34px !important; padding: 4px 10px !important; font-size: 16px !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,0.65) !important;
    cursor: pointer; transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
    box-shadow: none !important;
    position: relative;
}
.st-key-navbar button:hover,
.st-key-navbar [data-testid="stPopover"] > button:hover {
    background: rgba(0,255,204,0.08) !important;
    border-color: rgba(0,255,204,0.25) !important;
    color: #fff !important;
    transform: translateY(-1px);
}
.st-key-navbar button:focus-visible,
.st-key-navbar [data-testid="stPopover"] > button:focus-visible {
    outline: 2px solid rgba(0,255,204,0.45) !important; outline-offset: 2px;
}
/* 隱藏 popover 的下拉箭頭 */
.st-key-navbar [data-testid="stPopover"] > button svg { display: none !important; }
/* 移除 navbar 內 Streamlit 預設間距 */
.st-key-navbar [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-navbar [data-testid="stHorizontalBlock"] { gap: 0.4rem !important; align-items: center !important; }
.st-key-navbar [data-testid="stElementContainer"] { margin: 0 !important; }

/* ── Stepper ── */
.stepper { display: flex; align-items: center; margin: 16px 0 24px; }
.s-item { display: flex; align-items: center; gap: 8px; }
.s-item:not(:last-child) { flex: 1; }
.s-dot {
    width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; flex-shrink: 0; transition: background 0.3s ease, border-color 0.3s ease, color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
    border: 2px solid rgba(255,255,255,0.30); color: rgba(255,255,255,0.50); background: transparent;
}
.s-dot.active { border-color: #00ffcc; color: #00ffcc; background: rgba(0,255,204,0.12); box-shadow: 0 0 14px rgba(0,255,204,0.5); }
.s-dot.done { border-color: rgba(0,255,204,0.4); color: rgba(0,255,204,0.6); background: rgba(0,255,204,0.06); }
.s-lbl { font-size: 12px; font-weight: 500; color: rgba(255,255,255,0.55); white-space: nowrap; }
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
.glass:empty { display: none !important; padding: 0; margin: 0; border: none; min-height: 0; }
.glass::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,255,204,0.15), rgba(176,38,255,0.1), transparent);
}

/* ── History view ── */
.hist-card {
    background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 16px 20px; margin-bottom: 10px;
    cursor: pointer; transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
}
.hist-card:hover { border-color: rgba(0,255,204,0.25); background: rgba(0,255,204,0.03); }
.hist-time { font-size: 11px; color: rgba(255,255,255,0.55); font-weight: 500; }
.hist-summary { font-size: 13px; color: rgba(255,255,255,0.65); margin-top: 6px; line-height: 1.5; }

/* ── Export bar ── */
.export-bar {
    display: flex; align-items: center; gap: 10px; padding: 12px 18px;
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; margin-bottom: 16px;
}
.export-bar .export-label { font-size: 12px; color: rgba(255,255,255,0.55); font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-right: auto; }

/* ── Prompt tuner ── */
.tuner-label { font-size: 11px; color: rgba(255,255,255,0.55); font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; margin: 10px 0 6px; }
.style-chips { display: flex; flex-wrap: wrap; gap: 6px; }

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
    cursor: pointer !important; border-radius: 14px !important; transition: background 0.25s ease, border-color 0.25s ease, color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease !important;
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
    font-weight: 600 !important;
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
.card-desc { text-align: center; font-size: 11px; color: rgba(255,255,255,0.55); margin-top: 6px; line-height: 1.4; }

/* ── Counter ── */
.counter { text-align: center; margin: 12px 0 4px; font-size: 13px; color: rgba(255,255,255,0.55); }
.counter b { font-size: 20px; font-family: 'Righteous', sans-serif; }
.counter b.teal { color: #00ffcc; }
.counter b.purple { color: #b026ff; }

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
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); border-radius: 3px; }
::-webkit-scrollbar-thumb { background: rgba(0,255,204,0.25); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,255,204,0.40); }
html { scrollbar-color: rgba(0,255,204,0.25) rgba(255,255,255,0.02); scrollbar-width: thin; }
.stSlider > div { padding-left: 0 !important; }

/* ── Footer ── */
.footer { text-align: center; color: rgba(255,255,255,0.40); font-size: 10px; letter-spacing: 2px; margin-top: 40px; text-transform: uppercase; }
</style>
"""


def inject_css():
    """注入全域 CSS 到 Streamlit 頁面。"""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
