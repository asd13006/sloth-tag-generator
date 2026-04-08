"""
Material 3 Surface Hierarchy — sLoth Title Studio Production
Fonts: Manrope (body) + Space Grotesk (display/label) + JetBrains Mono (code)
CJK Fallback: PingFang TC → PingFang SC → SF Pro TC → Noto Sans TC → Microsoft JhengHei
Primary: #99f7ff · Secondary: #d674ff · Accent: #34D399 · BG: #0e0e0e
"""

import streamlit as st

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+TC:wght@300;400;500;600;700&display=swap');

/* ═══════════════════════════════════════════
   DESIGN TOKENS
   ═══════════════════════════════════════════ */
:root {
    /* ── Surface Hierarchy (Material 3 from idea) ── */
    --bg:                   #0e0e0e;
    --surface:              rgba(38, 38, 38, 0.4);
    --elevated:             rgba(32, 31, 31, 0.65);
    --surface-container-lowest:  #000000;
    --surface-container-low:     #131313;
    --surface-container:         #1a1919;
    --surface-container-high:    #201f1f;
    --surface-variant:           #262626;
    --surface-bright:            #2c2c2c;

    /* ── Brand Colors ── */
    --primary:        #99f7ff;
    --primary-dim:    #00e2ee;
    --primary-fixed:  #00f1fe;
    --secondary:      #d674ff;
    --secondary-dim:  #bb00fd;
    --secondary-container: #9800d0;
    --accent:         #34D399;
    --warning:        #FBBF24;
    --danger:         #ff716c;
    --error-container: #9f0519;

    /* ── On-Surface (Text) ── */
    --text:           #ffffff;
    --text-secondary: #f9f9f9;
    --text-muted:     #adaaaa;
    --outline:        #777575;
    --outline-variant: #494847;

    /* ── Borders ── */
    --border:         rgba(255, 255, 255, 0.05);
    --border-hover:   rgba(255, 255, 255, 0.12);

    /* ── Fonts ── */
    --font-body:  'Manrope', 'PingFang TC', 'PingFang SC', 'SF Pro TC', 'SF Pro Display', 'Noto Sans TC', 'Microsoft JhengHei', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-display: 'Space Grotesk', 'PingFang TC', 'PingFang SC', 'Noto Sans TC', cursive;
    --font-mono:  'JetBrains Mono', 'Fira Code', 'PingFang TC', monospace;

    /* ── Shape ── */
    --radius-sm:  4px;
    --radius-md:  8px;
    --radius-lg:  12px;
    --radius-xl:  16px;

    /* ── Effects ── */
    --blur-surface: blur(24px);
    --blur-elevated: blur(20px);
    --ease-out:   cubic-bezier(0.0, 0.0, 0.2, 1);
    --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);

    /* ── Neon Glow Presets ── */
    --glow-primary: 0 0 40px rgba(153, 247, 255, 0.08);
    --glow-neon-line: 0 4px 12px -2px rgba(153, 247, 255, 0.3);
}

/* ═══════════════════════════════════════════
   BASE RESET
   ═══════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    color-scheme: dark;
}
.stApp {
    background-color: var(--bg) !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(153,247,255,0.05) 0%, transparent 55%),
        radial-gradient(ellipse 50% 35% at 85% 15%, rgba(214,116,255,0.04) 0%, transparent 45%),
        radial-gradient(ellipse 40% 30% at 10% 80%, rgba(52,211,153,0.025) 0%, transparent 50%) !important;
}
/* 浮動光斑層 — absolute positioned orbs */
.stApp::before {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none; z-index: 0;
    background:
        radial-gradient(circle 400px at 20% 30%, rgba(153,247,255,0.025) 0%, transparent 100%),
        radial-gradient(circle 350px at 75% 60%, rgba(214,116,255,0.02) 0%, transparent 100%),
        radial-gradient(circle 300px at 50% 85%, rgba(52,211,153,0.015) 0%, transparent 100%);
    animation: orbFloat 20s ease-in-out infinite alternate;
}
.stApp::after {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none; z-index: 0;
    background:
        radial-gradient(circle 250px at 80% 20%, rgba(153,247,255,0.02) 0%, transparent 100%),
        radial-gradient(circle 200px at 30% 70%, rgba(214,116,255,0.015) 0%, transparent 100%);
    animation: orbFloat 25s ease-in-out infinite alternate-reverse;
}
/* 文字選取 */
::selection { background: rgba(153, 247, 255, 0.3); }
.block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1200px !important;
}
/* 隱藏 Streamlit 預設 UI chrome（保留 sidebar 收合控制） */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton,
#MainMenu {
    display: none !important; height: 0 !important; min-height: 0 !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    pointer-events: none !important;
}
/* 確保 sidebar 收合後的展開按鈕可見 */
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    z-index: 999999 !important;
    pointer-events: auto !important;
    position: fixed !important;
    top: 0.75rem !important;
    left: 0.75rem !important;
}
[data-testid="stSidebarCollapsedControl"] button {
    color: var(--text-muted) !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    transition: all 0.2s var(--ease-out) !important;
}
[data-testid="stSidebarCollapsedControl"] button:hover {
    color: var(--text) !important;
    border-color: var(--border-hover) !important;
    background: var(--elevated) !important;
}

/* ═══════════════════════════════════════════
   KEYFRAME ANIMATIONS
   ═══════════════════════════════════════════ */

/* 頁面載入 — 由下向上淡入 */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* 品牌漸層文字 */
@keyframes gradientText {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 骨架屏光帶掃描 */
@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* 脈搏呼吸 */
@keyframes pulse {
    0%, 100% { opacity: 0.5; }
    50%      { opacity: 1; }
}

/* 旋轉 loader */
@keyframes spin {
    to { transform: rotate(360deg); }
}

/* 漸層邊框流動 */
@keyframes gradientBorder {
    0%   { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}

/* 霓虹呼吸光 */
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 8px rgba(153,247,255,0.15), 0 4px 16px rgba(0,0,0,0.3); }
    50%      { box-shadow: 0 0 20px rgba(153,247,255,0.25), 0 4px 20px rgba(0,0,0,0.4); }
}

/* 背景浮動光斑 */
@keyframes orbFloat {
    0%   { transform: translate(0, 0) scale(1); }
    33%  { transform: translate(30px, -20px) scale(1.05); }
    66%  { transform: translate(-20px, 15px) scale(0.97); }
    100% { transform: translate(15px, -10px) scale(1.02); }
}

/* 無障礙：尊重使用者偏好 */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* ═══════════════════════════════════════════
   STAGGERED ENTRANCE — .anim-N class
   ═══════════════════════════════════════════ */
.anim-1 { animation: fadeSlideUp 0.5s var(--ease-out) 0.05s both; }
.anim-2 { animation: fadeSlideUp 0.5s var(--ease-out) 0.12s both; }
.anim-3 { animation: fadeSlideUp 0.5s var(--ease-out) 0.19s both; }
.anim-4 { animation: fadeSlideUp 0.5s var(--ease-out) 0.26s both; }
.anim-5 { animation: fadeSlideUp 0.5s var(--ease-out) 0.33s both; }
.anim-6 { animation: fadeSlideUp 0.5s var(--ease-out) 0.40s both; }
.anim-7 { animation: fadeSlideUp 0.5s var(--ease-out) 0.47s both; }
.anim-8 { animation: fadeSlideUp 0.5s var(--ease-out) 0.54s both; }

/* ═══════════════════════════════════════════
   SIDEBAR (native st.sidebar override)
   ═══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--surface-container-low) !important;
    backdrop-filter: none;
    border-right: none !important;
    min-width: 260px !important;
    max-width: 260px !important;
    box-shadow: 1px 0 0 0 rgba(153,247,255,0.06);
}
[data-testid="stSidebar"]::after {
    content: '';
    position: absolute; top: 0; right: 0; bottom: 0; width: 1px;
    background: linear-gradient(180deg, rgba(153,247,255,0.1), rgba(214,116,255,0.08), transparent);
    pointer-events: none;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1rem !important;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}
/* Sidebar 收合切換按鈕 */
[data-testid="stSidebar"] [data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    color: var(--text-muted) !important;
}

/* ── Sidebar Brand ── */
.sb-brand {
    font-family: var(--font-display);
    font-size: 24px; font-weight: 700;
    background: linear-gradient(135deg, #99f7ff, #00f1fe);
    background-size: 200% 200%;
    animation: gradientText 6s ease infinite;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    margin: 0; padding: 0;
}
.sb-subtitle {
    font-family: var(--font-body);
    font-size: 11px; font-weight: 500;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: var(--text-muted);
    margin: 4px 0 0;
}
.sb-divider {
    height: 1px; border: none; margin: 24px 0 20px;
    background: var(--border);
}
.sb-section-label {
    font-family: var(--font-display);
    font-size: 10px; font-weight: 600;
    letter-spacing: 3px; text-transform: uppercase;
    color: var(--text-muted);
    margin: 0 0 14px 16px;
}
.sb-version {
    font-size: 10px; color: var(--outline);
    text-align: center; letter-spacing: 2px; text-transform: uppercase;
    margin-top: auto;
    padding-top: 24px;
}

/* Sidebar Nav Buttons */
[data-testid="stSidebar"] button[data-testid^="stBaseButton"] {
    width: 100% !important;
    height: 44px !important; min-height: 44px !important;
    border-radius: var(--radius-md) !important;
    border: none !important;
    background: transparent !important;
    color: var(--text-muted) !important;
    font-family: var(--font-body) !important;
    font-size: 11px !important; font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    text-align: left !important; justify-content: flex-start !important;
    padding: 0 16px 0 16px !important;
    transition: all 0.2s var(--ease-out) !important;
    cursor: pointer !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] button[data-testid^="stBaseButton"] p {
    color: inherit !important; font-size: 11px !important; font-weight: 600 !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    margin: 0 !important;
}
[data-testid="stSidebar"] button[data-testid^="stBaseButton"]:hover {
    background: rgba(255,255,255,0.06) !important;
    color: var(--text) !important;
}
/* Active nav item — left border cyan glow with wider bar */
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(to right, rgba(153,247,255,0.08), transparent) !important;
    border-left: 3px solid var(--primary) !important;
    border-right: none !important;
    color: var(--primary) !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] p {
    color: var(--primary) !important; font-weight: 700 !important;
}

/* ═══════════════════════════════════════════
   GLASS CARD — Level 1 (Surface)
   ═══════════════════════════════════════════ */
.glass {
    background: var(--surface);
    backdrop-filter: var(--blur-surface);
    -webkit-backdrop-filter: var(--blur-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 32px 36px 28px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s var(--ease-out), box-shadow 0.3s var(--ease-out), border-color 0.3s var(--ease-out);
}
.glass::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(153,247,255,0.15), rgba(214,116,255,0.1), transparent);
}
.glass::after {
    content: ''; position: absolute;
    top: -60px; right: -60px; width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(214,116,255,0.06) 0%, transparent 70%);
    pointer-events: none;
    filter: blur(40px);
}
.glass:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(153,247,255,0.06), 0 4px 16px rgba(0,0,0,0.3);
    border-color: var(--border-hover);
}

/* Glass Card — Level 2 (Elevated) */
.glass-elevated {
    background: var(--elevated);
    backdrop-filter: var(--blur-elevated);
    -webkit-backdrop-filter: var(--blur-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 28px 32px 24px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s var(--ease-out), box-shadow 0.3s var(--ease-out), border-color 0.3s var(--ease-out);
}
.glass-elevated::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(214,116,255,0.15), rgba(153,247,255,0.1), transparent);
}
.glass-elevated:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(214,116,255,0.05), 0 4px 12px rgba(0,0,0,0.25);
    border-color: var(--border-hover);
}

/* ═══════════════════════════════════════════
   SECTION TITLES
   ═══════════════════════════════════════════ */
.sec-title {
    font-family: var(--font-display);
    font-size: 22px; color: var(--text-secondary);
    margin: 0 0 4px; letter-spacing: -0.3px;
}
.sec-desc {
    font-size: 13px; color: var(--text-muted);
    margin: 0 0 24px; line-height: 1.6; font-weight: 300;
}
.hero-title {
    font-family: var(--font-display);
    font-size: 32px; font-weight: 700; color: var(--text-secondary);
    margin: 0; letter-spacing: -0.5px;
}
.hero-desc {
    font-size: 14px; color: var(--text-muted); font-weight: 300;
    margin: 6px 0 24px; line-height: 1.7;
}

/* Card header row (icon + title + action) */
.card-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 16px;
}
.card-icon {
    font-size: 20px; line-height: 1;
    width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    border-radius: var(--radius-md);
    background: rgba(153,247,255,0.06);
    border: 1px solid rgba(153,247,255,0.12);
    flex-shrink: 0;
}
.card-icon.purple { background: rgba(214,116,255,0.06); border-color: rgba(214,116,255,0.12); }
.card-icon.green  { background: rgba(52,211,153,0.06);  border-color: rgba(52,211,153,0.12); }
.card-icon.amber  { background: rgba(251,191,36,0.06);  border-color: rgba(251,191,36,0.12); }
.card-title {
    font-family: var(--font-display);
    font-size: 17px; color: var(--text);
    letter-spacing: 0.3px; flex: 1; margin: 0;
}
.card-badge {
    font-size: 11px; font-weight: 600;
    padding: 3px 10px; border-radius: 20px;
    background: rgba(153,247,255,0.1);
    border: 1px solid rgba(153,247,255,0.2);
    color: var(--primary);
    letter-spacing: 0.5px;
}
.card-badge.green {
    background: rgba(52,211,153,0.1);
    border-color: rgba(52,211,153,0.2);
    color: var(--accent);
}

/* ═══════════════════════════════════════════
   TITLE LIST
   ═══════════════════════════════════════════ */
.title-row {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 12px 16px; margin-bottom: 6px;
    border-radius: var(--radius-md);
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(173,170,170,0.06);
    transition: background 0.2s ease, border-color 0.2s ease;
}
.title-row:hover {
    background: rgba(153,247,255,0.04);
    border-color: rgba(153,247,255,0.12);
}
.title-num {
    font-family: var(--font-display);
    font-size: 14px; color: var(--primary);
    min-width: 24px; text-align: center;
    padding-top: 2px; opacity: 0.7;
}
.title-text {
    font-size: 14px; color: var(--text);
    line-height: 1.6; flex: 1;
}
.title-copy {
    font-size: 14px; cursor: pointer;
    opacity: 0.3; transition: opacity 0.2s ease;
    padding: 2px 6px; flex-shrink: 0;
}
.title-copy:hover { opacity: 0.8; }

/* ═══════════════════════════════════════════
   TAG PILLS
   ═══════════════════════════════════════════ */
.tag-cloud { display: flex; flex-wrap: wrap; gap: 6px; }
.tag-pill {
    display: inline-block; padding: 5px 14px;
    border-radius: 20px; font-size: 12px; font-weight: 500;
    font-family: var(--font-mono);
    background: rgba(153,247,255,0.06);
    border: 1px solid rgba(153,247,255,0.15);
    color: rgba(153,247,255,0.85);
    transition: all 0.2s ease;
    cursor: default;
}
.tag-pill:hover {
    background: rgba(153,247,255,0.12);
    border-color: rgba(153,247,255,0.3);
    color: var(--primary);
    transform: translateY(-1px);
}
.tag-counter {
    font-size: 12px; color: var(--text-muted);
    font-family: var(--font-mono);
    margin-top: 12px; text-align: right;
}

/* ═══════════════════════════════════════════
   STORY PROSE
   ═══════════════════════════════════════════ */
.story-prose {
    font-size: 14px; color: rgba(249,249,249,0.85);
    line-height: 1.85; white-space: pre-wrap;
}
.story-prose p { margin-bottom: 14px; }

/* ═══════════════════════════════════════════
   TRACKLIST
   ═══════════════════════════════════════════ */
.track-row {
    display: flex; align-items: center; gap: 14px;
    padding: 12px 16px; margin-bottom: 6px;
    border-radius: var(--radius-md);
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(173,170,170,0.06);
    transition: background 0.2s ease, border-color 0.2s ease;
}
.track-row:hover {
    background: rgba(214,116,255,0.04);
    border-color: rgba(214,116,255,0.12);
}
.track-num {
    font-family: var(--font-display);
    font-size: 13px; color: var(--secondary);
    min-width: 28px; text-align: center; opacity: 0.7;
}
.track-info { flex: 1; }
.track-title {
    font-size: 14px; font-weight: 600; color: var(--text);
    margin-bottom: 2px;
}
.track-sub {
    font-size: 12px; color: var(--text-muted);
}
.track-theme {
    font-size: 11px; padding: 3px 10px;
    border-radius: 12px;
    background: rgba(214,116,255,0.08);
    border: 1px solid rgba(214,116,255,0.18);
    color: rgba(214,116,255,0.85);
    white-space: nowrap;
}

/* ═══════════════════════════════════════════
   SKELETON LOADER
   ═══════════════════════════════════════════ */
.skeleton {
    background: linear-gradient(90deg,
        rgba(173,170,170,0.06) 25%,
        rgba(173,170,170,0.12) 50%,
        rgba(173,170,170,0.06) 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s ease-in-out infinite;
    border-radius: var(--radius-md);
}
.skeleton-line {
    height: 14px; margin-bottom: 10px;
    border-radius: 6px;
}
.skeleton-line.w-75 { width: 75%; }
.skeleton-line.w-50 { width: 50%; }
.skeleton-line.w-90 { width: 90%; }
.skeleton-block {
    height: 100px; margin-bottom: 12px;
}

/* ═══════════════════════════════════════════
   BUTTONS (main content)
   ═══════════════════════════════════════════ */
button[data-testid^="stBaseButton"],
button[data-testid^="baseButton"] {
    cursor: pointer !important;
    border-radius: var(--radius-md) !important;
    transition: all 0.15s var(--ease-out) !important;
    font-family: var(--font-body) !important;
}
/* Primary — gradient from idea: from-primary to-primary-container */
button[data-testid="stBaseButton-primary"],
button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #99f7ff, #00f1fe) !important;
    border: none !important;
    color: #004145 !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-size: 12px !important;
}
button[data-testid="stBaseButton-primary"] p,
button[data-testid="baseButton-primary"] p { color: #004145 !important; font-weight: 700 !important; }
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
    box-shadow: 0 0 20px rgba(153,247,255,0.4), 0 4px 16px rgba(0,0,0,0.3) !important;
    transform: translateY(-1px) !important;
}
button[data-testid="stBaseButton-primary"]:active,
button[data-testid="baseButton-primary"]:active {
    transform: scale(0.95) !important;
    transition-duration: 0.06s !important;
}
/* Secondary — surface-container-highest bg from idea */
button[data-testid="stBaseButton-secondary"],
button[data-testid="baseButton-secondary"] {
    background: var(--surface-container-highest, #262626) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-muted) !important;
}
button[data-testid="stBaseButton-secondary"] p,
button[data-testid="baseButton-secondary"] p { color: var(--text-muted) !important; }
button[data-testid="stBaseButton-secondary"]:hover,
button[data-testid="baseButton-secondary"]:hover {
    background: var(--surface-bright) !important;
    border-color: var(--border-hover) !important;
    color: var(--text) !important;
}
button[data-testid="stBaseButton-secondary"]:active,
button[data-testid="baseButton-secondary"]:active {
    transform: scale(0.95) !important;
    transition-duration: 0.06s !important;
}
/* Focus ring */
button:focus-visible {
    outline: 2px solid rgba(153,247,255,0.45) !important;
    outline-offset: 2px !important;
}

/* ═══════════════════════════════════════════
   EXPORT BAR
   ═══════════════════════════════════════════ */

/* ── Glass containers via st.container(key=...) ── */
.st-key-input_glass,
.st-key-doubao_glass,
.st-key-api_glass,
.st-key-settings_glass {
    background: var(--surface) !important;
    backdrop-filter: var(--blur-surface) !important;
    -webkit-backdrop-filter: var(--blur-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 24px 28px 20px !important;
    margin-bottom: 20px !important;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s var(--ease-out), box-shadow 0.3s var(--ease-out);
    animation: fadeSlideUp 0.5s var(--ease-out) 0.12s both;
}
.st-key-input_glass:hover,
.st-key-doubao_glass:hover,
.st-key-api_glass:hover,
.st-key-settings_glass:hover {
    border-color: var(--border-hover) !important;
    box-shadow: 0 4px 20px rgba(153,247,255,0.06), 0 2px 8px rgba(0,0,0,0.2);
}

.export-bar {
    display: flex; align-items: center; gap: 10px; padding: 14px 20px;
    background: rgba(255,255,255,0.015);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    margin-top: 8px;
}
.export-label {
    font-size: 11px; font-weight: 700; color: var(--text-muted);
    letter-spacing: 2px; text-transform: uppercase; margin-right: auto;
}

/* ═══════════════════════════════════════════
   INPUTS (from idea: surface-container-lowest bg, neon focus)
   ═══════════════════════════════════════════ */
[data-baseweb="textarea"] { border-radius: var(--radius-lg) !important; }
[data-baseweb="textarea"] textarea {
    background: var(--surface-container-lowest) !important;
    color: var(--text-secondary) !important;
    font-size: 16px !important;
    line-height: 1.7 !important;
    font-family: var(--font-body) !important;
    border: none !important;
}
[data-baseweb="textarea"]:focus-within {
    border-color: transparent !important;
    box-shadow: none !important;
}
/* Neon underline on focus (from idea: bottom border expanding) */
[data-baseweb="input"],
[data-baseweb="textarea"] {
    position: relative !important;
}
/* Text inputs */
[data-baseweb="input"] input {
    background: var(--surface-container-lowest) !important;
    border: none !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-body) !important;
}
[data-baseweb="input"]:focus-within {
    box-shadow: 0 2px 0 0 var(--primary) !important;
}
/* Slider custom — neon thumb glow (from idea) */
[data-testid="stSlider"] [role="slider"] {
    background: var(--text-secondary) !important;
    border: none !important;
    box-shadow: 0 0 10px rgba(153, 247, 255, 0.8) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] > div > div:first-child {
    background: var(--surface-variant) !important;
}
/* Label styling — match idea's uppercase tracking */
.stTextInput label, .stTextArea label, .stSlider label,
.stSelectbox label, .stMultiSelect label, .stFileUploader label {
    font-family: var(--font-display) !important;
    font-size: 11px !important; font-weight: 500 !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
}

/* ═══════════════════════════════════════════
   STATUS INDICATOR (API / sidebar)
   ═══════════════════════════════════════════ */
.status-dot {
    display: inline-block; width: 8px; height: 8px;
    border-radius: 50%; margin-right: 8px; vertical-align: middle;
}
.status-dot.connected { background: var(--accent); box-shadow: 0 0 8px rgba(52,211,153,0.4); }
.status-dot.disconnected { background: var(--danger); box-shadow: 0 0 8px rgba(248,113,113,0.3); }
.status-text {
    font-size: 12px; color: var(--text-muted); vertical-align: middle;
}

/* Sidebar API status compact display */
.sb-api-compact {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 16px;
    border-radius: var(--radius-md);
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    margin-bottom: 4px;
}
.sb-api-compact .sb-api-icon { font-size: 14px; flex-shrink: 0; }
.sb-api-compact .sb-api-info { flex: 1; min-width: 0; }
.sb-api-compact .sb-api-title {
    font-size: 11px; font-weight: 600;
    letter-spacing: 1px; text-transform: uppercase;
    color: var(--text-muted);
    margin: 0;
}
.sb-api-compact .sb-api-detail {
    font-size: 10px; color: var(--outline);
    margin: 2px 0 0; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
}
.sb-api-compact.connected {
    border-color: rgba(52,211,153,0.2);
}
.sb-api-compact.connected .sb-api-title { color: var(--accent); }
.sb-api-compact.error {
    border-color: rgba(255,113,108,0.15);
}
.sb-api-compact.error .sb-api-title { color: var(--danger); }

/* ═══════════════════════════════════════════
   CHIP / PILL (reusable)
   ═══════════════════════════════════════════ */
.chip {
    display: inline-block; padding: 4px 14px;
    border-radius: 20px; font-size: 12px; font-weight: 600;
    margin: 3px 4px;
}
.chip-blue   { background: rgba(153,247,255,0.08);  border: 1px solid rgba(153,247,255,0.2);  color: var(--primary); }
.chip-purple { background: rgba(214,116,255,0.08); border: 1px solid rgba(214,116,255,0.2); color: var(--secondary); }
.chip-green  { background: rgba(52,211,153,0.08);  border: 1px solid rgba(52,211,153,0.2);  color: var(--accent); }

/* ═══════════════════════════════════════════
   MISC
   ═══════════════════════════════════════════ */
hr { border-color: var(--border) !important; }
a, a:visited { color: var(--primary) !important; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); border-radius: 10px; }
::-webkit-scrollbar-thumb { background: var(--surface-variant); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--surface-bright); }
html { scrollbar-color: var(--surface-variant) var(--bg); scrollbar-width: thin; }

.footer {
    text-align: center; color: var(--outline-variant);
    font-family: var(--font-body);
    font-size: 11px; letter-spacing: 1px;
    margin-top: 48px; text-transform: uppercase;
}

/* Streamlit expander override */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    background: rgba(255,255,255,0.015) !important;
}
[data-testid="stExpander"]:hover {
    border-color: var(--border-hover) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: var(--text) !important;
}

/* Streamlit tabs override (inside expander) */
[data-testid="stTabs"] {
    background: transparent !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
    border-bottom: 1px solid var(--border) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
    padding: 10px 20px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border: none !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.2s var(--ease-out) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text) !important;
    background: rgba(153, 247, 255, 0.06) !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--primary) !important;
    font-weight: 600 !important;
    background: rgba(153, 247, 255, 0.08) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: var(--primary) !important;
}
.stTabs [data-baseweb="tab-border"] {
    background-color: var(--border) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 16px !important;
    background: transparent !important;
}

/* ═══════════════════════════════════════════
   INPUT FLOW — Output Selector Chips
   ═══════════════════════════════════════════ */
.output-chips {
    display: flex; flex-wrap: wrap; gap: 8px;
    margin-bottom: 16px;
}
.output-chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 16px; border-radius: 12px;
    font-size: 13px; font-weight: 500;
    background: rgba(255,255,255,0.025);
    border: 1px solid var(--border);
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.2s var(--ease-out);
}
.output-chip:hover {
    border-color: var(--border-hover);
    background: rgba(153,247,255,0.06);
    color: var(--text);
}
.output-chip.active {
    background: rgba(153,247,255,0.1);
    border-color: rgba(153,247,255,0.35);
    color: var(--primary);
    font-weight: 600;
}
.output-chip .chip-icon { font-size: 15px; }

/* Material input section */
.mat-section {
    background: rgba(255,255,255,0.015);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 20px 24px 16px;
    margin-bottom: 12px;
    transition: border-color 0.2s ease;
}
.mat-section:hover { border-color: var(--border-hover); }
.mat-section-title {
    font-size: 12px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    color: var(--text-muted);
    margin: 0 0 14px;
    display: flex; align-items: center; gap: 8px;
}
.mat-section-title .mat-icon {
    font-size: 14px; opacity: 0.7;
}

/* Tuner / style control */
.tuner-section {
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
    margin-top: 12px;
}
.tuner-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 16px 18px 12px;
    transition: border-color 0.2s ease;
}
.tuner-card:hover { border-color: var(--border-hover); }
.tuner-label {
    font-family: var(--font-display);
    font-size: 11px; font-weight: 500;
    letter-spacing: 2px; text-transform: uppercase;
    color: var(--text-muted);
    margin: 0 0 10px;
}

/* Neon border bottom — from idea */
.neon-border-bottom {
    border-bottom: 2px solid #99f7ff;
    box-shadow: 0 4px 12px -2px rgba(153, 247, 255, 0.3);
}

/* Image upload zone — from idea: dashed outline-variant */
.upload-zone {
    border: 2px dashed var(--outline-variant);
    border-radius: var(--radius-lg);
    padding: 24px; text-align: center;
    color: var(--text-muted); font-size: 13px; font-weight: 300;
    transition: all 0.2s ease;
    cursor: pointer;
    background: var(--surface-container-low);
}
.upload-zone:hover {
    border-color: rgba(153,247,255,0.3);
    background: rgba(255,255,255,0.05);
    color: var(--text);
}

/* ═══════════════════════════════════════════
   LOADING OVERLAY
   ═══════════════════════════════════════════ */
.loading-overlay {
    text-align: center; padding: 48px 24px;
}
.loading-spinner {
    display: inline-block; width: 32px; height: 32px;
    border: 3px solid var(--border);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 16px;
}
.loading-text {
    font-size: 14px; color: var(--text-muted);
    letter-spacing: 0.5px;
}

/* ═══════════════════════════════════════════
   3-STEP WIZARD — Phase / Step Indicators
   ═══════════════════════════════════════════ */
.phase-indicator {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 16px;
}
.phase-indicator .phase-line {
    height: 1px; width: 48px;
    background: var(--primary);
}
.phase-indicator .phase-label {
    font-family: var(--font-display);
    font-size: 11px; font-weight: 500;
    letter-spacing: 3px; text-transform: uppercase;
    color: var(--primary);
}

/* Step progress bar (3 segments) */
.step-bar {
    display: flex; align-items: center; gap: 16px;
}
.step-bar .step-segments {
    display: flex; gap: 6px;
}
.step-bar .step-seg {
    width: 32px; height: 3px;
    border-radius: 2px;
    background: var(--surface-variant);
    transition: background 0.3s ease;
}
.step-bar .step-seg.active {
    background: var(--primary);
}
.step-bar .step-counter {
    font-family: var(--font-display);
    font-size: 12px; font-weight: 500;
    letter-spacing: -0.5px; text-transform: uppercase;
    color: var(--primary);
}

/* ═══════════════════════════════════════════
   ARCHETYPE CARDS (Step 1)
   ═══════════════════════════════════════════ */
.archetype-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-top: 16px;
}
.archetype-card {
    position: relative;
    background: rgba(32, 31, 31, 0.4);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(153, 247, 255, 0.05);
    border-radius: var(--radius-xl);
    padding: 32px 28px;
    cursor: pointer;
    overflow: hidden;
    transition: all 0.4s var(--ease-out);
    aspect-ratio: 3 / 4;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.archetype-card::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(153,247,255,0.03), transparent);
    opacity: 0;
    transition: opacity 0.4s ease;
}
.archetype-card:hover {
    transform: scale(1.02);
    border-color: rgba(153,247,255,0.15);
}
.archetype-card:hover::before { opacity: 1; }
.archetype-card.selected {
    border-color: rgba(153,247,255,0.35);
    box-shadow: 0 0 24px rgba(153,247,255,0.08);
    background: rgba(38,38,38,0.6);
}
.archetype-card.variant-secondary::before {
    background: linear-gradient(135deg, rgba(214,116,255,0.03), transparent);
}
.archetype-card.variant-secondary.selected {
    border-color: rgba(214,116,255,0.35);
    box-shadow: 0 0 24px rgba(214,116,255,0.08);
}
.archetype-card .arch-icon {
    width: 56px; height: 56px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    background: var(--surface-container-lowest);
    border: 1px solid rgba(153,247,255,0.15);
    font-size: 28px;
    margin-bottom: 20px;
    transition: border-color 0.3s ease;
}
.archetype-card:hover .arch-icon { border-color: rgba(153,247,255,0.4); }
.archetype-card.variant-secondary .arch-icon { border-color: rgba(214,116,255,0.15); }
.archetype-card.variant-secondary:hover .arch-icon { border-color: rgba(214,116,255,0.4); }
.archetype-card .arch-title {
    font-family: var(--font-display);
    font-size: 20px; font-weight: 700;
    color: var(--text-secondary);
    margin-bottom: 10px;
    letter-spacing: -0.3px;
}
.archetype-card .arch-desc {
    font-size: 13px; color: var(--text-muted);
    line-height: 1.65; font-weight: 300;
}
.archetype-card .arch-deploy {
    display: flex; align-items: center; justify-content: space-between;
    margin-top: 20px;
    opacity: 0;
    transition: opacity 0.3s ease;
}
.archetype-card:hover .arch-deploy,
.archetype-card.selected .arch-deploy { opacity: 1; }
.archetype-card .arch-deploy span {
    font-size: 10px; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase;
    color: var(--primary);
}
.archetype-card.variant-secondary .arch-deploy span { color: var(--secondary); }
.archetype-card .arch-selected-badge {
    position: absolute; top: 16px; right: 16px;
    font-size: 10px; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase;
    padding: 4px 10px; border-radius: 12px;
    background: rgba(153,247,255,0.15);
    border: 1px solid rgba(153,247,255,0.35);
    color: var(--primary);
    opacity: 0; transition: opacity 0.3s ease;
}
.archetype-card.selected .arch-selected-badge { opacity: 1; }
.archetype-card.variant-secondary .arch-selected-badge {
    background: rgba(214,116,255,0.15);
    border-color: rgba(214,116,255,0.35);
    color: var(--secondary);
}

/* Terminal decorative block */
.terminal-block {
    margin-top: 48px; padding: 28px 32px;
    background: var(--surface-container-lowest);
    border-radius: var(--radius-xl);
    border-left: 2px solid rgba(153,247,255,0.25);
    position: relative; overflow: hidden;
}
.terminal-block::after {
    content: '⌨';
    position: absolute; top: 16px; right: 24px;
    font-size: 64px; opacity: 0.03;
}
.terminal-block p {
    font-family: var(--font-mono);
    font-size: 10.5px; color: rgba(153,247,255,0.35);
    letter-spacing: 2px; text-transform: uppercase;
    margin: 0; line-height: 1.8;
}

/* ═══════════════════════════════════════════
   TUNING TERMINAL (Step 2 right panel)
   ═══════════════════════════════════════════ */
.st-key-tuning_terminal {
    background: rgba(38,38,38,0.4) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: var(--radius-xl) !important;
    padding: 32px 28px 24px !important;
    position: relative;
    overflow: hidden;
}
.st-key-tuning_terminal::after {
    content: '';
    position: absolute;
    top: -80px; right: -80px; width: 256px; height: 256px;
    background: radial-gradient(circle, rgba(214,116,255,0.08) 0%, transparent 70%);
    pointer-events: none;
    filter: blur(100px);
    z-index: 0;
}
.tuning-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 6px;
}
.tuning-header .tune-icon {
    font-size: 22px; color: var(--secondary);
}
.tuning-header h3 {
    font-family: var(--font-display);
    font-size: 18px; font-weight: 700;
    letter-spacing: -0.3px; color: var(--text);
    margin: 0;
}
.tuning-subtitle {
    font-size: 12px; color: var(--text-muted);
    font-weight: 300; margin: 0 0 28px;
}

/* Slider annotation row */
.slider-labels {
    display: flex; justify-content: space-between;
    margin-top: -4px;
}
.slider-labels span {
    font-size: 9.5px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    color: var(--outline);
}
.slider-value {
    font-size: 11px; font-weight: 500;
    font-family: var(--font-mono);
    letter-spacing: -0.5px;
    color: var(--primary);
}
.slider-value.secondary { color: var(--secondary); }

/* Audience grid */
.audience-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
    margin-top: 8px;
}
.audience-btn {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 14px;
    border-radius: var(--radius-md);
    background: var(--surface-container-lowest);
    border: 1px solid rgba(255,255,255,0.05);
    font-size: 11px; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.2s ease;
}
.audience-btn:hover {
    background: rgba(255,255,255,0.05);
}
.audience-btn.active {
    background: var(--surface-container-highest);
    border-color: rgba(153,247,255,0.2);
    color: var(--primary);
}
.audience-btn .radio {
    font-size: 14px; opacity: 0.5;
}
.audience-btn.active .radio { opacity: 1; color: var(--primary); }

/* ═══════════════════════════════════════════
   RESULTS DASHBOARD (Step 3)
   ═══════════════════════════════════════════ */
.result-hero { margin-bottom: 32px; }
.result-hero .result-label {
    font-size: 11px; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase;
    color: var(--secondary);
    margin-bottom: 8px;
}
.result-hero h1 {
    font-family: var(--font-display);
    font-size: 42px; font-weight: 700;
    letter-spacing: -1px; color: var(--text-secondary);
    margin: 0 0 12px;
}
.result-hero .result-desc {
    font-size: 14px; color: var(--text-muted);
    font-weight: 300; max-width: 520px; line-height: 1.7;
}

/* Frost-bordered result container */
.frost-border {
    background: linear-gradient(135deg, rgba(153,247,255,0.15), transparent);
    border-radius: 20px;
    padding: 3px;
    margin-bottom: 24px;
}
.frost-border-inner {
    background: var(--surface-container);
    border-radius: calc(20px - 3px);
    padding: 28px 32px;
}
.frost-border-inner .result-section-header {
    display: flex; justify-content: space-between; align-items: center;
    padding-bottom: 16px; margin-bottom: 20px;
    border-bottom: 1px solid var(--border);
}
.result-section-header .section-left {
    display: flex; align-items: center; gap: 10px;
}
.result-section-header .pulse-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--primary);
    animation: pulse 2s ease-in-out infinite;
}
.result-section-header .section-title {
    font-family: var(--font-display);
    font-size: 12px; font-weight: 600;
    letter-spacing: 3px; text-transform: uppercase;
    color: var(--primary);
}
.result-section-header .section-actions {
    display: flex; gap: 6px;
}
.result-section-header .section-actions button {
    background: transparent; border: none;
    color: var(--text-muted); cursor: pointer;
    padding: 6px 8px; border-radius: var(--radius-sm);
    transition: all 0.2s ease;
    font-size: 16px;
}
.result-section-header .section-actions button:hover {
    background: rgba(255,255,255,0.05);
    color: var(--text);
}

/* Primary title card (big) */
.title-card-primary {
    background: rgba(32,31,31,0.4);
    backdrop-filter: blur(24px);
    border: none; border-radius: var(--radius-lg);
    padding: 24px 28px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: background 0.3s ease;
    cursor: pointer;
}
.title-card-primary::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--primary);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.title-card-primary:hover {
    background: rgba(255,255,255,0.05);
}
.title-card-primary:hover::before { opacity: 1; }
.title-card-primary h2 {
    font-size: 20px; font-weight: 600;
    line-height: 1.4; color: var(--text);
    margin: 0 0 12px;
    transition: color 0.3s ease;
}
.title-card-primary:hover h2 { color: var(--primary); }
.title-card-primary .match-badge {
    font-size: 10px; font-weight: 700;
    padding: 4px 10px; border-radius: 6px;
    background: rgba(153,247,255,0.15);
    color: var(--primary);
    letter-spacing: 0.5px;
    position: absolute; top: 24px; right: 24px;
}
.title-card-primary .actions {
    display: flex; gap: 8px; align-items: center;
}
.title-card-primary .actions button {
    background: transparent; border: none;
    font-size: 11px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    color: var(--outline); cursor: pointer;
    transition: color 0.2s ease;
}
.title-card-primary .actions button:hover { color: var(--text); }
.title-card-primary .actions .dot {
    color: var(--outline-variant); font-size: 8px;
}

/* Secondary title card (small) */
.title-card-secondary {
    background: rgba(32,31,31,0.4);
    backdrop-filter: blur(24px);
    border: none; border-radius: var(--radius-lg);
    padding: 20px 24px;
    transition: background 0.3s ease;
    cursor: pointer;
}
.title-card-secondary:hover {
    background: rgba(255,255,255,0.05);
}
.title-card-secondary h2 {
    font-size: 16px; font-weight: 500;
    line-height: 1.5; color: var(--text-secondary);
    margin: 0 0 10px;
    transition: color 0.3s ease;
}
.title-card-secondary:hover h2 { color: var(--primary-dim); }
.title-card-secondary .viral-row {
    display: flex; align-items: center; justify-content: space-between;
}
.title-card-secondary .viral-label {
    font-size: 10px; color: var(--outline);
    letter-spacing: 0.5px;
}
.title-card-secondary .copy-btn {
    background: transparent; border: none;
    color: var(--text-muted); cursor: pointer;
    font-size: 14px; padding: 4px;
    transition: color 0.2s ease;
}
.title-card-secondary .copy-btn:hover { color: var(--text); }

/* Action bar (step 3) */
.action-bar {
    display: flex; flex-wrap: wrap; gap: 12px;
    justify-content: space-between; align-items: center;
    padding: 24px 0; margin-top: 8px;
    border-top: 1px solid var(--border);
}
.action-bar .action-group { display: flex; gap: 10px; }
.action-bar-btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 24px; border-radius: var(--radius-md);
    font-size: 11px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    cursor: pointer; transition: all 0.2s ease;
    border: none;
}
.action-bar-btn.ghost {
    background: rgba(255,255,255,0.05);
    color: var(--text);
}
.action-bar-btn.ghost:hover { background: rgba(255,255,255,0.1); }
.action-bar-btn.outlined {
    background: transparent;
    border: 1px solid rgba(214,116,255,0.25);
    color: var(--secondary);
}
.action-bar-btn.outlined:hover { border-color: var(--secondary); }

/* ═══════════════════════════════════════════
   WIZARD — Layout helpers
   ═══════════════════════════════════════════ */
.wizard-hero {
    margin-bottom: 40px;
    padding-left: 16px;
}
.wizard-hero h1 {
    font-family: var(--font-display);
    font-size: 48px; font-weight: 700;
    color: var(--text-secondary);
    line-height: 1.05; letter-spacing: -1.5px;
    max-width: 600px;
    margin: 0 0 16px;
}
.wizard-hero h1 .gradient-text {
    background: linear-gradient(135deg, var(--secondary), var(--secondary-dim));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.wizard-hero .hero-sub {
    font-size: 16px; color: var(--text-muted);
    font-weight: 300; line-height: 1.7; max-width: 520px;
}
/* Step header with progress */
.wizard-header {
    display: flex; flex-wrap: wrap;
    justify-content: space-between; align-items: flex-end;
    gap: 16px; margin-bottom: 32px;
}
.wizard-header .left { flex: 1; min-width: 300px; }
.wizard-header h1 {
    font-family: var(--font-display);
    font-size: 42px; font-weight: 700;
    color: var(--text-secondary);
    letter-spacing: -1px; margin: 0 0 6px;
}
.wizard-header .subtitle {
    font-size: 14px; color: var(--text-muted);
    font-weight: 300; max-width: 440px;
}

/* Bottom action row (Back + Confirm) */
.wizard-actions {
    display: flex; gap: 12px;
    margin-top: 32px; padding-top: 24px;
    border-top: 1px solid var(--border);
}
.wizard-actions .btn-back {
    flex: 1; padding: 14px; text-align: center;
    background: var(--surface-container-highest);
    border: none; border-radius: var(--radius-xl);
    color: var(--text-secondary); font-weight: 700;
    font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
    cursor: pointer; transition: all 0.2s ease;
}
.wizard-actions .btn-back:hover { background: var(--surface-bright); }
.wizard-actions .btn-next {
    flex: 2; padding: 14px; text-align: center;
    background: linear-gradient(135deg, #99f7ff, #00f1fe);
    border: none; border-radius: var(--radius-xl);
    color: #004145; font-weight: 800;
    font-size: 11px; letter-spacing: 3px; text-transform: uppercase;
    cursor: pointer; transition: all 0.2s ease;
}
.wizard-actions .btn-next:hover {
    box-shadow: 0 0 20px rgba(153,247,255,0.4);
}

/* Context input section label (Step 2) */
.context-label {
    font-family: var(--font-display);
    font-size: 11px; font-weight: 500;
    letter-spacing: 3px; text-transform: uppercase;
    color: var(--text-muted);
    margin: 0 0 12px 4px;
}
.vision-badge {
    font-size: 10px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    padding: 3px 10px; border-radius: 4px;
    border: 1px solid rgba(214,116,255,0.25);
    color: var(--secondary);
}

/* ═══════════════════════════════════════════
   PRODUCTION-SPECIFIC — API Gate
   ═══════════════════════════════════════════ */
.api-gate-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 100px);
    padding: 0 24px;
}
.api-gate {
    text-align: center; padding: 60px 48px 48px;
    max-width: 520px;
    width: 100%;
}
.api-gate-icon {
    font-size: 64px; margin-bottom: 20px; line-height: 1;
    filter: grayscale(0.3);
}
.api-gate-title {
    font-family: var(--font-display); font-size: 24px; color: var(--text);
    margin-bottom: 12px; letter-spacing: 0.5px;
}
.api-gate-desc {
    color: var(--text-muted); font-size: 14px; line-height: 1.7;
    max-width: 480px; margin: 0 auto 28px;
}
.api-gate-link {
    display: inline-block; padding: 10px 24px; border-radius: var(--radius-md);
    background: rgba(153,247,255,0.12); border: 1px solid rgba(153,247,255,0.35);
    color: var(--primary); font-weight: 600; font-size: 13px; letter-spacing: 0.5px;
    text-decoration: none; transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
.api-gate-link:hover {
    background: rgba(153,247,255,0.2); border-color: rgba(153,247,255,0.6);
    box-shadow: 0 0 16px rgba(153,247,255,0.25);
}
@media (prefers-reduced-motion: reduce) {
    .api-gate-link { transition: none; }
}

/* ═══════════════════════════════════════════
   PRODUCTION-SPECIFIC — Profile Center
   ═══════════════════════════════════════════ */
.profile-header {
    display: flex; align-items: center; gap: 20px; padding: 8px 0;
}
.profile-avatar {
    width: 64px; height: 64px; border-radius: 50%; flex-shrink: 0;
    border: 2px solid rgba(153,247,255,0.3); object-fit: cover;
}
.profile-avatar-placeholder {
    width: 64px; height: 64px; border-radius: 50%; flex-shrink: 0;
    border: 2px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; background: rgba(255,255,255,0.04);
}
.profile-info { flex: 1; min-width: 0; }
.profile-name {
    font-family: var(--font-display); font-size: 20px; color: var(--text);
    margin-bottom: 2px; letter-spacing: 0.5px;
}
.profile-email { font-size: 13px; color: var(--text-muted); margin-bottom: 4px; }
.profile-stat { font-size: 12px; color: var(--outline); }

/* ═══════════════════════════════════════════
   PRODUCTION-SPECIFIC — History
   ═══════════════════════════════════════════ */
.hist-card {
    background: rgba(255,255,255,0.025); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 16px 20px; margin-bottom: 10px;
    cursor: pointer; transition: background 0.2s ease, border-color 0.2s ease;
}
.hist-card:hover { border-color: rgba(153,247,255,0.25); background: rgba(153,247,255,0.03); }
.hist-time { font-size: 11px; color: var(--text-muted); font-weight: 500; }
.hist-summary { font-size: 13px; color: var(--outline); margin-top: 6px; line-height: 1.5; }

/* ═══════════════════════════════════════════
   PRODUCTION-SPECIFIC — Review / Info Cards
   ═══════════════════════════════════════════ */
.info-card {
    background: rgba(255,255,255,0.025); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 18px 22px; margin-bottom: 16px;
}
.review-card {
    background: rgba(214,116,255,0.04); border-left: 3px solid var(--secondary);
    border-radius: 0 var(--radius-lg) var(--radius-lg) 0; padding: 20px 24px; margin-bottom: 20px;
}
.review-label { font-size: 11px; font-weight: 600; color: var(--secondary); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px; }
.review-text { color: var(--outline); font-size: 14px; line-height: 1.8; white-space: pre-wrap; }

/* ═══════════════════════════════════════════
   PRODUCTION-SPECIFIC — Export
   ═══════════════════════════════════════════ */
.export-bar {
    display: flex; align-items: center; gap: 10px; padding: 14px 20px;
    background: rgba(255,255,255,0.015);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    margin-top: 8px;
}
.export-label {
    font-size: 11px; font-weight: 700; color: var(--text-muted);
    letter-spacing: 2px; text-transform: uppercase; margin-right: auto;
}

/* ═══════════════════════════════════════════
   PRODUCTION-SPECIFIC — Doubao Tool
   ═══════════════════════════════════════════ */
.doubao-result-header { margin: 16px 0 12px; }
.doubao-video-info { margin: 12px 0; display: flex; gap: 8px; flex-wrap: wrap; }
.doubao-download-btn {
    display: block; text-align: center; padding: 14px 24px; margin: 16px 0;
    border-radius: var(--radius-lg); font-size: 15px; font-weight: 600;
    background: rgba(153,247,255,0.10); border: 1px solid rgba(153,247,255,0.30);
    color: var(--primary); text-decoration: none; transition: all 0.2s ease;
}
.doubao-download-btn:hover { background: rgba(153,247,255,0.18); box-shadow: 0 0 16px rgba(153,247,255,0.15); }

/* ═══════════════════════════════════════════
   PRODUCTION-SPECIFIC — Auth Badge
   ═══════════════════════════════════════════ */
.auth-badge {
    display: inline-flex; align-items: center; gap: 8px;
    height: 38px; padding: 0 16px; border-radius: var(--radius-md);
    font-size: 13px; font-weight: 600; letter-spacing: 0.5px;
    border: 1px solid var(--border); background: rgba(255,255,255,0.06);
    white-space: nowrap; color: var(--text-muted);
    box-sizing: border-box; box-shadow: 0 2px 6px rgba(0,0,0,0.3);
}
.auth-badge.guest { color: var(--outline); }

/* ═══════════════════════════════════════════
   PRODUCTION-SPECIFIC — Counters
   ═══════════════════════════════════════════ */
.counter { text-align: right; margin: 0; font-size: 13px; color: var(--text-muted); display: flex; align-items: center; justify-content: flex-end; height: 100%; }
.counter b { font-size: 20px; font-family: var(--font-display); }
.counter b.teal { color: var(--primary); }
.counter b.purple { color: var(--secondary); }

/* ═══════════════════════════════════════════
   PRODUCTION-SPECIFIC — Nav Spacer
   ═══════════════════════════════════════════ */
.nav-spacer { height: 12px; }

/* ═══════════════════════════════════════════
   PRODUCTION-SPECIFIC — Card Descriptions
   ═══════════════════════════════════════════ */
.card-desc { text-align: center; font-size: 11px; color: var(--text-muted); margin-top: 6px; line-height: 1.4; }

/* ═══════════════════════════════════════════
   PRODUCTION-SPECIFIC — Sidebar API Input
   ═══════════════════════════════════════════ */
.sb-api-section {
    padding: 8px 14px;
    margin-bottom: 8px;
}
.sb-api-label {
    font-size: 10px; font-weight: 600;
    letter-spacing: 2px; text-transform: uppercase;
    color: var(--outline);
    margin-bottom: 6px;
}
.sb-api-status {
    font-size: 11px; color: var(--text-muted);
    margin-top: 4px;
}

/* ═══════════════════════════════════════════
   PRODUCTION-SPECIFIC — Material Lab
   ═══════════════════════════════════════════ */
.matlab-label {
    font-family: var(--font-display); font-size: 10px; font-weight: 600;
    letter-spacing: 2.5px; text-transform: uppercase;
    color: var(--text-muted); margin: 0 0 12px 2px;
}
.ai-vision-badge {
    font-size: 9px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
    padding: 3px 10px; border-radius: 4px;
    color: var(--secondary); border: 1px solid rgba(214,116,255,0.30); background: transparent;
}
.st-key-matlab_actions { margin-top: 8px; padding-top: 20px; border-top: 1px solid var(--border); }
</style>
"""


def inject_css():
    """注入 Glass Morphism 2.0 Neon Frost CSS 到 Streamlit 頁面。"""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
