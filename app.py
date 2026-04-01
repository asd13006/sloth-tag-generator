import streamlit as st
import time
import html as _html
from urllib.parse import quote
from PIL import Image
import io

# ─────────────────────────────────────────
#  頁面設定
# ─────────────────────────────────────────
st.set_page_config(
    page_title="sLoth rAdio · Title Studio",
    page_icon="🎵",
    layout="wide",
)

# ─────────────────────────────────────────
#  全域設計系統 CSS
#  Design System: OLED Dark + Bento Grid
#  Typography:    Righteous (display) + Poppins (body)
#  Accent:        #00ffcc  (neon teal)
#  Background:    #0A0A14  (near-black)
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Righteous&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Poppins', -apple-system, sans-serif;
    color-scheme: dark;
}
.stApp {
    background-color: #0A0A14 !important;
    background-image: radial-gradient(rgba(0,255,204,0.055) 1px, transparent 1px) !important;
    background-size: 30px 30px !important;
}
.block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1280px !important;
}
.stApp > header { background: transparent !important; }

/* ── 標題動畫 ── */
@keyframes gradient-text {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.app-title {
    font-family: 'Righteous', sans-serif;
    font-size: 38px;
    font-weight: 400;
    letter-spacing: 1px;
    background: linear-gradient(270deg, #00ffcc, #b026ff, #00E676, #00ffcc);
    background-size: 300% 300%;
    animation: gradient-text 5s ease infinite;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
}
.app-subtitle {
    color: rgba(255,255,255,0.35);
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── Pipeline Stepper ── */
.stepper {
    display: flex;
    align-items: center;
    gap: 0;
    margin: 28px 0 32px;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
}
.step-item:last-child { flex: 0; }
.step-dot {
    width: 32px; height: 32px;
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.15);
    background: transparent;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700;
    color: rgba(255,255,255,0.3);
    flex-shrink: 0;
    transition: all 0.3s ease;
}
.step-dot.active {
    border-color: #00ffcc;
    background: rgba(0,255,204,0.12);
    color: #00ffcc;
    box-shadow: 0 0 12px rgba(0,255,204,0.25);
}
.step-dot.done {
    border-color: rgba(0,255,204,0.5);
    background: rgba(0,255,204,0.08);
    color: rgba(0,255,204,0.7);
}
.step-label {
    font-size: 12px;
    font-weight: 500;
    color: rgba(255,255,255,0.25);
    white-space: nowrap;
}
.step-label.active { color: #00ffcc; }
.step-label.done   { color: rgba(0,255,204,0.5); }
.step-connector {
    height: 1px;
    background: rgba(255,255,255,0.08);
    flex: 1;
    margin: 0 12px;
}
.step-connector.done { background: rgba(0,255,204,0.25); }

/* ── Section 標題 ── */
.section-heading {
    font-family: 'Righteous', sans-serif;
    font-size: 20px;
    color: #FFFFFF;
    margin: 0 0 6px;
    letter-spacing: 0.5px;
}
.section-sub {
    font-size: 13px;
    color: rgba(255,255,255,0.4);
    margin: 0 0 24px;
}

/* ── 結果卡片（Stage 2-4 用）── */
.result-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
}
.result-label {
    font-size: 11px;
    font-weight: 600;
    color: #00ffcc;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* ── 歌曲 Cards Grid ── */
@keyframes border-pulse {
    0%   { box-shadow: 0 0 0 0 rgba(0,255,204,0.4); }
    70%  { box-shadow: 0 0 0 6px rgba(0,255,204,0); }
    100% { box-shadow: 0 0 0 0 rgba(0,255,204,0); }
}

/* ══ 歌曲卡片固定高度：從 stVerticalBlock 直屬子層開始鎖定 ══
   用「父層含歌曲卡片」的 :has() 選擇器，精準命中每個 element-container，
   從最外層一路往內全部固定為 260px，徹底消除欄位累積誤差 */

/* 層 1：column 內的 stVerticalBlock 的直接子 div（element-container）*/
[data-testid="stVerticalBlock"]:has(button:has(p:nth-of-type(5)))
    > div[data-testid="element-container"] {
    height: 260px !important;
    min-height: 260px !important;
    max-height: 260px !important;
    overflow: hidden !important;
    flex-shrink: 0 !important;
    padding: 0 !important;
    margin: 0 0 8px 0 !important;
}

/* 層 2：element-container 內的 stBaseButtonContainer */
[data-testid="stVerticalBlock"]:has(button:has(p:nth-of-type(5)))
    > div[data-testid="element-container"]
    > [data-testid="stBaseButtonContainer"],
[data-testid="stVerticalBlock"]:has(button:has(p:nth-of-type(5)))
    > div[data-testid="element-container"]
    > div[class*="ButtonContainer"] {
    height: 260px !important;
    max-height: 260px !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* 層 3：button 本身（舊規則備用，同時支援新舊 testid 前綴）*/
button[data-testid^="baseButton"]:has(p:nth-of-type(5)),
button[data-testid^="stBaseButton"]:has(p:nth-of-type(5)) {
    border-radius: 14px !important;
    padding: 16px 18px !important;
    width: 100% !important;
    height: 260px !important;
    min-height: 260px !important;
    max-height: 260px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    text-align: left !important;
    white-space: normal !important;
    overflow: hidden !important;
    cursor: pointer !important;
    transition: border-color 0.2s, background 0.2s, transform 0.18s, box-shadow 0.2s !important;
    position: relative !important;
}

/* 未選取：深色底 + 細邊框 */
button[data-testid="baseButton-secondary"]:has(p:nth-of-type(5)) {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    box-shadow: none !important;
}
button[data-testid="baseButton-secondary"]:has(p:nth-of-type(5)):hover {
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.22) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
}

/* 已選取：純 teal 框線，無底色 */
button[data-testid="baseButton-primary"]:has(p:nth-of-type(5)),
button[data-testid="stBaseButton-primary"]:has(p:nth-of-type(5)),
button[kind="primary"]:has(p:nth-of-type(5)) {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid #00ffcc !important;
    box-shadow: 0 0 12px rgba(0,255,204,0.18) !important;
}
button[data-testid="baseButton-primary"]:has(p:nth-of-type(5)):hover,
button[data-testid="stBaseButton-primary"]:has(p:nth-of-type(5)):hover,
button[kind="primary"]:has(p:nth-of-type(5)):hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3), 0 0 16px rgba(0,255,204,0.25) !important;
}

/* ── 卡片文字層級 ── */
button:has(p:nth-of-type(5)) p {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}

/* P1：編號 badge */
button:has(p:nth-of-type(5)) p:nth-of-type(1) {
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    color: rgba(255,255,255,0.25) !important;
    margin-bottom: 10px !important;
    line-height: 1 !important;
}
button[data-testid="baseButton-primary"]:has(p:nth-of-type(5)) p:nth-of-type(1) {
    color: #00ffcc !important;
}

/* P2：英文主標題 */
button:has(p:nth-of-type(5)) p:nth-of-type(2) {
    font-size: 16px !important;
    font-weight: 700 !important;
    line-height: 1.3 !important;
    margin-bottom: 4px !important;
    letter-spacing: -0.2px !important;
}
button:has(p:nth-of-type(5)) p:nth-of-type(2) strong {
    color: #FFFFFF !important;
}

/* P3：中文副標題 */
button:has(p:nth-of-type(5)) p:nth-of-type(3) {
    font-size: 11.5px !important;
    font-weight: 400 !important;
    color: rgba(255,255,255,0.56) !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 12px !important;
    line-height: 1.3 !important;
    padding-bottom: 10px !important;
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}
button[data-testid="baseButton-primary"]:has(p:nth-of-type(5)) p:nth-of-type(3) {
    color: rgba(255,255,255,0.68) !important;
    border-bottom-color: rgba(0,255,204,0.18) !important;
}

/* P4：英文描述 */
button:has(p:nth-of-type(5)) p:nth-of-type(4) {
    font-size: 11.5px !important;
    font-weight: 400 !important;
    color: rgba(255,255,255,0.75) !important;
    line-height: 1.58 !important;
    margin-bottom: 4px !important;
    display: -webkit-box !important;
    -webkit-line-clamp: 2 !important;
    -webkit-box-orient: vertical !important;
    overflow: hidden !important;
}
button[data-testid="baseButton-primary"]:has(p:nth-of-type(5)) p:nth-of-type(4) {
    color: rgba(255,255,255,0.88) !important;
}

/* P5：中文描述 */
button:has(p:nth-of-type(5)) p:nth-of-type(5) {
    display: -webkit-box !important;
    -webkit-line-clamp: 2 !important;
    -webkit-box-orient: vertical !important;
    overflow: hidden !important;
}
button:has(p:nth-of-type(5)) p:nth-of-type(5) em {
    font-size: 11px !important;
    font-style: normal !important;
    color: rgba(255,255,255,0.58) !important;
    line-height: 1.58 !important;
}
button[data-testid="baseButton-primary"]:has(p:nth-of-type(5)) p:nth-of-type(5) em {
    color: rgba(255,255,255,0.72) !important;
}

/* ── 概念方向卡片（剛好 2 個 <p>，無第 3 個）── */
button[data-testid^="baseButton"]:has(p:nth-of-type(2)):not(:has(p:nth-of-type(3))),
button[data-testid^="stBaseButton"]:has(p:nth-of-type(2)):not(:has(p:nth-of-type(3))) {
    border-radius: 14px !important;
    padding: 18px 20px !important;
    width: 100% !important;
    min-height: 96px !important;
    height: auto !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: center !important;
    text-align: left !important;
    white-space: normal !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}
button:has(p:nth-of-type(2)):not(:has(p:nth-of-type(3))) p:nth-of-type(1) {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    margin-bottom: 6px !important;
    line-height: 1.2 !important;
}
button:has(p:nth-of-type(2)):not(:has(p:nth-of-type(3))) p:nth-of-type(2) {
    font-size: 12px !important;
    font-weight: 400 !important;
    color: rgba(255,255,255,0.58) !important;
    line-height: 1.5 !important;
}
button[data-testid$="-primary"]:has(p:nth-of-type(2)):not(:has(p:nth-of-type(3))) p:nth-of-type(2) {
    color: rgba(255,255,255,0.80) !important;
}

/* ── Action Bar ── */
.action-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 0 0;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin-top: 20px;
}
.selected-count {
    font-size: 13px;
    color: rgba(255,255,255,0.5);
    flex: 1;
}
.selected-count span {
    font-size: 20px;
    font-weight: 800;
    color: #00ffcc;
    font-family: 'Righteous', sans-serif;
}

/* ── Tag Pills ── */
.tag-pill {
    display: inline-block;
    background: rgba(0,255,204,0.08);
    border: 1px solid rgba(0,255,204,0.2);
    border-radius: 20px;
    padding: 3px 11px;
    margin: 3px 3px;
    color: #00ffcc;
    font-size: 12px;
    font-weight: 500;
}

/* ── Title Result Card ── */
.title-card {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 8px;
}
.title-num {
    font-family: 'Righteous', sans-serif;
    font-size: 13px;
    color: #00ffcc;
    flex-shrink: 0;
    padding-top: 1px;
    min-width: 28px;
}
.title-text {
    font-size: 14px;
    font-weight: 500;
    color: rgba(255,255,255,0.88);
    line-height: 1.5;
}

/* ═══════════════════════════════════════════════════
   AI 感全域覆蓋 — 徹底去除所有紅色元素
   ─ 覆蓋 Streamlit 1.x 的 --primary-color 紅色變數
   ─ 同時支援 baseButton / stBaseButton 兩種 data-testid
   ─ 覆蓋 :focus-visible 消除點擊後紅色 outline
   ═══════════════════════════════════════════════════ */

/* 1. CSS 變數層：從根部取代 Streamlit 的紅色主題色 */
:root {
    --primary-color: #00ffcc !important;
    --primary: #00ffcc !important;
    --streamlit-primary: #00ffcc !important;
}

/* 2. 全域 button focus outline 覆蓋（點擊後紅色框的根源）*/
button:focus,
button:focus-visible {
    outline: 2px solid rgba(0,255,204,0.50) !important;
    outline-offset: 2px !important;
    box-shadow: none !important;
}

/* 3. 主要按鈕（非歌曲卡片）── 同時支援兩種 data-testid 前綴 */
button[data-testid="baseButton-primary"]:not(:has(p:nth-of-type(5))),
button[data-testid="stBaseButton-primary"]:not(:has(p:nth-of-type(5))),
button[kind="primary"]:not(:has(p:nth-of-type(5))) {
    background: linear-gradient(135deg, rgba(0,255,204,0.13) 0%, rgba(176,38,255,0.10) 100%) !important;
    border: 1px solid rgba(0,255,204,0.42) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06) !important;
    color: #ccfff5 !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.25s ease !important;
}
button[data-testid="baseButton-primary"]:not(:has(p:nth-of-type(5))) p,
button[data-testid="stBaseButton-primary"]:not(:has(p:nth-of-type(5))) p,
button[kind="primary"]:not(:has(p:nth-of-type(5))) p {
    color: #ccfff5 !important;
}
button[data-testid="baseButton-primary"]:not(:has(p:nth-of-type(5))):hover,
button[data-testid="stBaseButton-primary"]:not(:has(p:nth-of-type(5))):hover,
button[kind="primary"]:not(:has(p:nth-of-type(5))):hover {
    background: linear-gradient(135deg, rgba(0,255,204,0.20) 0%, rgba(176,38,255,0.16) 100%) !important;
    border-color: rgba(0,255,204,0.65) !important;
    box-shadow: 0 0 22px rgba(0,255,204,0.16), inset 0 1px 0 rgba(255,255,255,0.08) !important;
    transform: translateY(-1px) !important;
}
button[data-testid="baseButton-primary"]:not(:has(p:nth-of-type(5))):active,
button[data-testid="stBaseButton-primary"]:not(:has(p:nth-of-type(5))):active,
button[kind="primary"]:not(:has(p:nth-of-type(5))):active {
    transform: translateY(0) !important;
    background: linear-gradient(135deg, rgba(0,255,204,0.22) 0%, rgba(176,38,255,0.18) 100%) !important;
    border-color: rgba(0,255,204,0.70) !important;
    box-shadow: none !important;
}
button[data-testid="baseButton-primary"]:not(:has(p:nth-of-type(5))):focus-visible,
button[data-testid="stBaseButton-primary"]:not(:has(p:nth-of-type(5))):focus-visible,
button[kind="primary"]:not(:has(p:nth-of-type(5))):focus-visible {
    outline: 2px solid rgba(0,255,204,0.55) !important;
    outline-offset: 2px !important;
}

/* 4. 次要按鈕（非歌曲卡片）── 玻璃感深色 */
button[data-testid="baseButton-secondary"]:not(:has(p:nth-of-type(5))),
button[data-testid="stBaseButton-secondary"]:not(:has(p:nth-of-type(5))),
button[kind="secondary"]:not(:has(p:nth-of-type(5))) {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    color: rgba(255,255,255,0.62) !important;
    transition: all 0.25s ease !important;
}
button[data-testid="baseButton-secondary"]:not(:has(p:nth-of-type(5))):hover,
button[data-testid="stBaseButton-secondary"]:not(:has(p:nth-of-type(5))):hover,
button[kind="secondary"]:not(:has(p:nth-of-type(5))):hover {
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.20) !important;
    color: rgba(255,255,255,0.88) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
}
button[data-testid="baseButton-secondary"]:not(:has(p:nth-of-type(5))):active,
button[data-testid="stBaseButton-secondary"]:not(:has(p:nth-of-type(5))):active,
button[kind="secondary"]:not(:has(p:nth-of-type(5))):active {
    background: rgba(255,255,255,0.10) !important;
    border-color: rgba(255,255,255,0.25) !important;
}

/* 5. 已選取歌曲卡片 — 點擊 active / focus 狀態去紅 */
button[data-testid="baseButton-primary"]:has(p:nth-of-type(5)):focus-visible,
button[data-testid="stBaseButton-primary"]:has(p:nth-of-type(5)):focus-visible,
button[kind="primary"]:has(p:nth-of-type(5)):focus-visible {
    outline: 2px solid rgba(0,255,204,0.55) !important;
    outline-offset: 2px !important;
}
button[data-testid="baseButton-primary"]:has(p:nth-of-type(5)):active,
button[data-testid="stBaseButton-primary"]:has(p:nth-of-type(5)):active,
button[kind="primary"]:has(p:nth-of-type(5)):active {
    background: rgba(255,255,255,0.04) !important;
    border-color: #00ffcc !important;
}
/* 未選取歌曲卡片 active */
button[data-testid="baseButton-secondary"]:has(p:nth-of-type(5)):active,
button[data-testid="stBaseButton-secondary"]:has(p:nth-of-type(5)):active,
button[kind="secondary"]:has(p:nth-of-type(5)):active {
    background: rgba(255,255,255,0.09) !important;
    border-color: rgba(255,255,255,0.28) !important;
}

/* ── Radio 完整覆蓋 */
input[type="radio"], input[type="checkbox"] {
    accent-color: #00ffcc !important;
}
[data-testid="stRadio"] label {
    color: rgba(255,255,255,0.65) !important;
    transition: color 0.15s ease !important;
}
[data-testid="stRadio"] [role="radio"] {
    border-color: rgba(255,255,255,0.22) !important;
}
[data-testid="stRadio"] [role="radio"][aria-checked="true"] {
    border-color: #00ffcc !important;
    background: rgba(0,255,204,0.15) !important;
    box-shadow: 0 0 8px rgba(0,255,204,0.25) !important;
}
[data-testid="stRadio"] [role="radio"][aria-checked="true"] > div:first-child {
    background-color: #00ffcc !important;
}

/* ── 文字輸入框 */
[data-baseweb="input"] {
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="textarea"]:focus-within {
    border-color: rgba(0,255,204,0.52) !important;
    box-shadow: 0 0 0 2px rgba(0,255,204,0.10), 0 0 14px rgba(0,255,204,0.06) !important;
}

/* ── 通知 / 警告 / 成功 / 錯誤 ── 去紅統一玻璃感 */
[data-testid="stAlert"] {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(8px) !important;
}
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.72) !important;
}
[data-testid="stAlert"] svg { opacity: 0.7 !important; }
/* success → teal 主題色 */
[data-testid="stAlert"][data-baseweb="notification"],
div[data-stale="false"] > div > [data-testid="stAlert"] {
    border-color: rgba(0,255,204,0.28) !important;
    background: rgba(0,255,204,0.04) !important;
}
[data-testid="stAlert"] svg[data-testid="check-circle"],
[data-testid="stAlert"] svg[data-testid="stAlertDynamicIcon-success"] {
    color: #00ffcc !important;
    fill: #00ffcc !important;
}
/* warning → 琥珀（非紅） */
[data-testid="stAlert"] svg[data-testid="stAlertDynamicIcon-warning"],
[data-testid="stAlert"] svg[data-testid="warning"] {
    color: #f0c060 !important;
    fill: #f0c060 !important;
}

/* ── 文件上傳區 */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1.5px dashed rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: rgba(0,255,204,0.38) !important;
    background: rgba(0,255,204,0.025) !important;
    box-shadow: 0 0 18px rgba(0,255,204,0.07) !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: rgba(0,255,204,0.08) !important;
    border: 1px solid rgba(0,255,204,0.30) !important;
    color: #00ffcc !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: rgba(0,255,204,0.14) !important;
    border-color: rgba(0,255,204,0.50) !important;
}
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span:not(button span) {
    color: rgba(255,255,255,0.32) !important;
}

/* ── Spinner / Status / Loading */
[data-testid="stSpinner"] svg {
    color: #00ffcc !important;
}
.stSpinner > div {
    border-top-color: #00ffcc !important;
    border-right-color: rgba(0,255,204,0.15) !important;
    border-bottom-color: rgba(0,255,204,0.15) !important;
    border-left-color: rgba(0,255,204,0.15) !important;
}
[data-testid="stStatusWidget"] {
    background: rgba(0,255,204,0.03) !important;
    border-color: rgba(0,255,204,0.22) !important;
    border-radius: 12px !important;
}
[data-testid="stStatusWidget"] summary {
    color: rgba(255,255,255,0.65) !important;
}

/* ── Expander (st.container border / st.expander) */
details[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
details[data-testid="stExpander"] summary {
    color: rgba(255,255,255,0.62) !important;
}
details[data-testid="stExpander"] summary:hover {
    color: rgba(255,255,255,0.88) !important;
}
details[data-testid="stExpander"] summary svg {
    fill: rgba(255,255,255,0.38) !important;
}

/* ── st.code 程式碼區塊 */
[data-testid="stCode"] {
    background: rgba(0,0,0,0.38) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
}
[data-testid="stCode"] pre code {
    color: rgba(0,255,204,0.78) !important;
}

/* ── 分隔線 */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── 自訂 Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(0,255,204,0.22);
    border-radius: 2px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(0,255,204,0.42); }

/* ── 全域連結色 */
a, a:visited {
    color: #00ffcc !important;
}
a:hover {
    color: rgba(0,255,204,0.75) !important;
    text-decoration: none !important;
}

/* ── 複製按鈕 ── */
.copy-btn {
    background: rgba(0,255,204,0.08);
    border: 1px solid rgba(0,255,204,0.25);
    border-radius: 6px;
    color: #00ffcc;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 4px 10px;
    cursor: pointer;
    transition: background 0.2s, border-color 0.2s;
    white-space: nowrap;
    font-family: 'Poppins', sans-serif;
}
.copy-btn:hover {
    background: rgba(0,255,204,0.18);
    border-color: rgba(0,255,204,0.5);
}
.title-card .copy-btn {
    margin-left: auto;
    padding: 3px 8px;
    font-size: 10px;
    align-self: center;
    flex-shrink: 0;
}
</style>
<script>
function copyText(enc, btn) {
    navigator.clipboard.writeText(decodeURIComponent(enc))
        .then(function(){ btn.textContent='已複製 ✓'; setTimeout(function(){ btn.textContent='複製'; }, 1500); })
        .catch(function(){ btn.textContent='失敗'; setTimeout(function(){ btn.textContent='複製'; }, 1500); });
}
</script>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  狀態管理
# ─────────────────────────────────────────
for key, default in [
    ("step", 1), ("song_data", []), ("selected_song_ids", []),
    ("concept_options", []), ("selected_concept", None), ("final_results", {}),
    ("n_songs", 10),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def next_step():   st.session_state.step += 1
def go_to(n):      st.session_state.step = n


def reset_pipeline():
    for k in ["song_data", "selected_song_ids", "concept_options", "selected_concept", "final_results"]:
        st.session_state[k] = [] if k in ("song_data", "selected_song_ids", "concept_options") else (
            None if k == "selected_concept" else {})
    st.session_state.step = 1


# ─────────────────────────────────────────
#  Mock 歌單資料
# ─────────────────────────────────────────
MOCK_SONGS = [
    {"id": 1,  "en_title": "Soft Landing",          "zh_title": "柔軟的著陸",
        "en_theme": "Sinking into a chair, feeling your body remember how to let go.",                   "zh_theme": "沉入椅子，感受身體重新記起如何放手。"},
    {"id": 2,  "en_title": "Golden Honey Light",    "zh_title": "金色蜜光",
        "en_theme": "The warmth of afternoon sun touching the skin through a sheer curtain.",            "zh_theme": "午後陽光透過薄紗簾灑在皮膚上的和煦溫暖。"},
    {"id": 3,  "en_title": "Paper Moon Lullaby",    "zh_title": "紙月亮搖籃曲",
        "en_theme": "A bedside lamp glowing softly, pages turning themselves.",                         "zh_theme": "床頭燈柔柔地亮著，書頁自己在翻動。"},
    {"id": 4,  "en_title": "Rainy Window Theatre",  "zh_title": "雨窗小劇場",
        "en_theme": "Watching raindrops race down the glass, picking your champion.",                   "zh_theme": "看雨滴在玻璃上賽跑，默默為牠打氣。"},
    {"id": 5,  "en_title": "Midnight Pour-Over",    "zh_title": "午夜手沖",
        "en_theme": "The quiet ritual of coffee at 2 AM, steam curling upward.",                        "zh_theme": "凌晨兩點沖咖啡的安靜儀式，蒸氣向上捲曲。"},
    {"id": 6,  "en_title": "Wool Socks Morning",    "zh_title": "毛襪的早晨",
        "en_theme": "Sliding across wooden floors in thick socks, no plans today.",                     "zh_theme": "穿著厚毛襪在木地板上滑行，今天沒有計劃。"},
    {"id": 7,  "en_title": "Fog & Honey",           "zh_title": "霧與蜂蜜",
        "en_theme": "Morning fog dissolving as you stir honey into warm milk.",                         "zh_theme": "晨霧散去的時候，你正把蜂蜜攪進溫牛奶裡。"},
    {"id": 8,  "en_title": "Last Train Home",       "zh_title": "末班車歸途",
        "en_theme": "Leaning against the window, city lights blurring into streaks.",                   "zh_theme": "靠在車窗上，城市燈火糊成一道道光痕。"},
    {"id": 9,  "en_title": "Rooftop Satellite",     "zh_title": "天台衛星",
        "en_theme": "Sitting on the rooftop, pretending the stars are listening.",                      "zh_theme": "坐在天台上，假裝星星們都在聽。"},
    {"id": 10, "en_title": "Bookshop Rain",         "zh_title": "書店裡的雨",
        "en_theme": "Trapped in a bookshop by sudden rain, and not minding at all.",                    "zh_theme": "被突如其來的雨困在書店裡，卻一點也不介意。"},
    {"id": 11, "en_title": "Velvet Afternoon",      "zh_title": "絲絨午後",
        "en_theme": "Sunlight pooling on unmade sheets, dust dancing slowly.",                          "zh_theme": "陽光灑在沒摺的床單上，灰塵在慢慢跳舞。"},
    {"id": 12, "en_title": "Laundry Day Blues",     "zh_title": "洗衣日藍調",
        "en_theme": "The hypnotic tumble of clothes in a dryer, warmth on your face.",                  "zh_theme": "衣服在烘乾機裡催眠般翻滾，暖氣撲在臉上。"},
    {"id": 13, "en_title": "Tangerine Dream",       "zh_title": "橘子味的夢",
        "en_theme": "Peeling a tangerine in silence, the scent filling the room.",                      "zh_theme": "安靜地剝一顆橘子，香氣漫滿整個房間。"},
    {"id": 14, "en_title": "3 AM Skyline",          "zh_title": "凌晨三點的天際線",
        "en_theme": "The city is asleep but the lights are still on, humming softly.",                 "zh_theme": "城市睡著了但燈還亮著，發出輕柔的嗡嗡聲。"},
    {"id": 15, "en_title": "Cat Nap Atlas",         "zh_title": "貓咪午睡地圖",
        "en_theme": "Following a cat's logic: sleep where the sunbeam lands.",                          "zh_theme": "跟著貓的邏輯：陽光照到哪裏就睡哪裏。"},
    {"id": 16, "en_title": "Cinnamon Static",       "zh_title": "肉桂色的雜訊",
        "en_theme": "Old radio crackling in a kitchen that smells like baking.",                        "zh_theme": "老收音機在飄著烘焙香氣的廚房裡沙沙響。"},
    {"id": 17, "en_title": "Slow Dissolve",         "zh_title": "緩慢溶解",
        "en_theme": "Sugar cube sinking into tea, thoughts sinking into nothing.",                      "zh_theme": "方糖沉入茶裡，思緒沉入虛無。"},
    {"id": 18, "en_title": "Window Seat Poet",      "zh_title": "靠窗詩人",
        "en_theme": "Scribbling half-thoughts on a napkin, watching people pass by.",                   "zh_theme": "在餐巾紙上寫下半句想法，看行人路過。"},
    {"id": 19, "en_title": "Cloud Pillow",          "zh_title": "雲朵枕頭",
        "en_theme": "That perfect moment when the pillow is cool on both sides.",                       "zh_theme": "枕頭兩面都是涼的，那個完美瞬間。"},
    {"id": 20, "en_title": "Vinyl Sunset",          "zh_title": "黑膠唱片的日落",
        "en_theme": "Needle on the record, sun going down, nowhere else to be.",                        "zh_theme": "唱針落在唱片上，太陽正在下山，哪裡都不用去。"},
]


# ─────────────────────────────────────────
#  App Header
# ─────────────────────────────────────────
hcol1, hcol2 = st.columns([1, 3])
with hcol1:
    st.markdown("<div class='app-title'>Title Studio</div><div class='app-subtitle'>sLoth rAdio · Demo Mode</div>", unsafe_allow_html=True)

# Pipeline Stepper
step = st.session_state.step
steps = ["🎵 選歌", "🎨 概念", "✍️ 素材", "📊 成果"]
step_html = "<div class='stepper'>"
for i, label in enumerate(steps, 1):
    state = "active" if i == step else ("done" if i < step else "")
    step_html += f"""
    <div class='step-item'>
        <div class='step-dot {state}'>{'✓' if i < step else i}</div>
        <span class='step-label {state}'>{label}</span>
    </div>"""
    if i < len(steps):
        conn_cls = "done" if i < step else ""
        step_html += f"<div class='step-connector {conn_cls}'></div>"
step_html += "</div>"
st.markdown(step_html, unsafe_allow_html=True)

st.divider()


# ═══════════════════════════════════════════════════════
#  STAGE 1 — Music Ideation
# ═══════════════════════════════════════════════════════
if step == 1:

    if not st.session_state.song_data:
        st.markdown(
            "<div class='section-heading'>🎵 Music Ideation</div><div class='section-sub'>選擇數量 · 一鍵生成詩意歌名與意境</div>", unsafe_allow_html=True)
        _, ctr, _ = st.columns([1, 2, 1])
        with ctr:
            st.markdown("<div style='color:rgba(255,255,255,0.40); font-size:11px; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;'>🎚️ 生成數量</div>", unsafe_allow_html=True)
            n = st.slider("n_songs_slider", min_value=1, max_value=20,
                          value=st.session_state.n_songs, step=1, label_visibility="collapsed")
            st.session_state.n_songs = n
            if st.button(f"✨  生成 {n} 首歌曲", type="primary", use_container_width=True):
                with st.spinner("✨ 生成中..."):
                    time.sleep(1.2)
                    st.session_state.song_data = MOCK_SONGS[:n]
                    st.rerun()

    else:
        n_selected = len(st.session_state.selected_song_ids)
        st.markdown(
            f"<div class='section-heading'>🎵 選擇歌曲</div>"
            f"<div class='section-sub'>點選卡片 · 可多選 · 再按取消</div>",
            unsafe_allow_html=True,
        )

        NUM_COLS = min(4, len(st.session_state.song_data))
        songs = st.session_state.song_data
        cols = st.columns(NUM_COLS, gap="small")

        for col_i, col in enumerate(cols):
            with col:
                for song in songs[col_i::NUM_COLS]:
                    is_sel = song["id"] in st.session_state.selected_song_ids
                    btype = "primary" if is_sel else "secondary"
                    badge = "✓" if is_sel else f"{song['id']:02d}"
                    label = (
                        f"{badge}\n\n"
                        f"**{song['en_title']}**\n\n"
                        f"{song['zh_title']}\n\n"
                        f"{song['en_theme']}\n\n"
                        f"*— {song['zh_theme']}*"
                    )
                    if st.button(label, key=f"s{song['id']}", type=btype, use_container_width=True):
                        if is_sel:
                            st.session_state.selected_song_ids.remove(
                                song["id"])
                        else:
                            st.session_state.selected_song_ids.append(
                                song["id"])
                        st.rerun()

        # Action bar
        st.markdown(
            f"<div class='action-bar'>"
            f"<span class='selected-count'><span>{n_selected}</span> / {len(songs)} ✓</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        ac1, ac2, ac3 = st.columns([1, 1, 3])
        with ac1:
            if st.button("✓ 全選", use_container_width=True):
                st.session_state.selected_song_ids = [s["id"] for s in songs]
                st.rerun()
        with ac2:
            if st.button("✕ 清除", use_container_width=True):
                st.session_state.selected_song_ids = []
                st.rerun()
        with ac3:
            if st.button("🎨 概念方向 →", type="primary", use_container_width=True):
                if not st.session_state.selected_song_ids:
                    st.warning("⚠️ 請至少選一首歌。")
                else:
                    next_step()
                    st.rerun()


# ═══════════════════════════════════════════════════════
#  STAGE 2 — Visual Concept
# ═══════════════════════════════════════════════════════
elif step == 2:
    st.markdown("<div class='section-heading'>🎨 概念方向</div><div class='section-sub'>輸入氛圍關鍵字 · AI 生成 3 個故事方向</div>",
                unsafe_allow_html=True)

    sel_songs = [s for s in st.session_state.song_data if s["id"]
                 in st.session_state.selected_song_ids]
    names = "、".join(s["zh_title"] for s in sel_songs[:5])
    if len(sel_songs) > 5:
        names += f" ⋯ +{len(sel_songs) - 5}"
    st.markdown(
        f"<div class='result-card'><div class='result-label'>🎵 已選歌曲</div><span style='color:rgba(255,255,255,0.7); font-size:14px;'>{names}</span></div>", unsafe_allow_html=True)

    vibe = st.text_input(
        "🌙 氛圍關鍵字（選填）", placeholder="凌晨的微雨 · 暖燈 · 黑膠唱片...", label_visibility="visible")

    b1, b2 = st.columns([1, 3])
    with b1:
        if st.button("← 返回", use_container_width=True):
            st.session_state.concept_options = []
            go_to(1)
            st.rerun()
    with b2:
        if st.button("🎲 生成方向", type="primary", use_container_width=True):
            with st.spinner("🎨 構思中..."):
                time.sleep(1.2)
                if vibe and "雨" in vibe:
                    opts = [
                        ("☔ 微雨窗邊", "雨滴沿玻璃蜿蜒，你蜷縮在毛毯裡放空"),
                        ("🌧️ 雨後霓虹", "積水映照整個城市的燈火色彩"),
                        ("🌿 雨中陽台", "植物們在雨裡安靜地呼吸"),
                    ]
                elif vibe and ("咖啡" in vibe or "coffee" in vibe.lower()):
                    opts = [
                        ("☕ 暖光手沖", "熱水緩緩注入濾杯，香氣漫延整個空間"),
                        ("🫖 深巷老館", "木質吧台上的咖啡漬是歲月的印記"),
                        ("🌅 冷掉的拿鐵", "拉花已融化，但窗外更好看"),
                    ]
                else:
                    opts = [
                        ("☔ 微雨放空", "世界安靜了，只剩雨聲和呼吸"),
                        ("☕ 暖光手沖", "蒸氣緩緩上升，時間彷彿凝固"),
                        ("🌙 深夜書檯", "檯燈圈出一個只屬於你的小宇宙"),
                    ]
                st.session_state.concept_options = opts
                if st.session_state.selected_concept not in [o[0] for o in opts]:
                    st.session_state.selected_concept = None
                st.rerun()

    if st.session_state.concept_options:
        st.write("")
        st.markdown(
            "<div class='result-label' style='margin-bottom:12px;'>🎯 選擇一個方向</div>", unsafe_allow_html=True)
        ccols = st.columns(3, gap="small")
        for ci, (title, desc) in enumerate(st.session_state.concept_options):
            with ccols[ci]:
                is_sel = st.session_state.selected_concept == title
                ctype = "primary" if is_sel else "secondary"
                if st.button(f"{title}\n\n{desc}", key=f"c{ci}", type=ctype, use_container_width=True):
                    st.session_state.selected_concept = title
                    st.rerun()

        if st.session_state.selected_concept:
            st.write("")
            if st.button("✍️ 生成 SEO 素材 →", type="primary", use_container_width=True):
                next_step()
                st.rerun()


# ═══════════════════════════════════════════════════════
#  STAGE 3 — SEO Assets
# ═══════════════════════════════════════════════════════
elif step == 3:
    st.markdown("<div class='section-heading'>✍️ SEO 素材</div><div class='section-sub'>生成故事 · 標題 · Tags</div>",
                unsafe_allow_html=True)

    sel_songs = [s for s in st.session_state.song_data if s["id"]
                 in st.session_state.selected_song_ids]
    concept = st.session_state.selected_concept or "—"
    st.markdown(
        f"<div class='result-card'>"
        f"<div class='result-label'>🎯 Creative Brief</div>"
        f"<p style='color:rgba(255,255,255,0.6); font-size:13px; margin:0 0 6px;'>🎵 <span style='color:#fff;'>{len(sel_songs)} 首</span></p>"
        f"<p style='color:rgba(255,255,255,0.6); font-size:13px; margin:0;'>🎨 <span style='color:#00ffcc;'>{concept}</span></p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader("🖼️ 上傳縮圖（選填）", type=[
                                "png", "jpg", "jpeg", "webp"])
    if uploaded:
        st.image(Image.open(uploaded), use_container_width=True)

    st.write("")

    if not st.session_state.final_results:
        if st.button("🚀 生成所有素材", type="primary", use_container_width=True):
            with st.status("⚙️ 生成中...", expanded=True) as s:
                st.write("📖 撰寫長文故事...")
                time.sleep(0.8)
                st.write("💬 撰寫對話短篇...")
                time.sleep(0.6)
                st.write("🏆 生成 5 個高點擊標題...")
                time.sleep(0.6)
                st.write("🏷️ 生成 SEO Tags...")
                time.sleep(0.5)
                first = sel_songs[0] if sel_songs else {
                    "en_title": "Soft Landing", "zh_title": "柔軟的著陸"}
                st.session_state.final_results = {
                    "long_story": (
                        f"凌晨兩點半，窗外的雨終於慢了下來。你把毛毯拉到下巴，聽見遠處有人在彈鋼琴。"
                        f"那旋律像是從記憶深處飄來的，帶著肉桂和舊書的味道。桌上的咖啡已經涼了，"
                        f"但你不想動——因為此刻的溫度剛剛好。你想起那天下午，陽光把整個房間染成蜂蜜色。"
                        f"那時候你也在聽這首歌——{first['zh_title']}。"
                        f"空氣裡有洗好的床單味，有遠處電車聲，有貓咪踩在紙箱上的沙沙聲。"
                        f"你閉上眼睛，感覺自己正在慢慢融化成這個房間的一部分。沒有要去的地方，只有呼吸，只有此刻。"
                        f"窗簾被風輕輕吹起，像在說：留下來吧，這裡很安全。"
                    ),
                    "short_story": (
                        f"🌙 「欸，你有冇試過凌晨兩點突然好想飲嘢？」\n\n"
                        f"☕ 「有啊，我上次半夜爬起身沖咖啡，坐喺窗邊聽歌聽到天光。」\n\n"
                        f"🎵 「聽咩歌？」\n\n"
                        f"🎧 「{first['en_title']}。嗰種感覺⋯成個世界靜晒，淨係得你同音樂。」\n\n"
                        f"🐱 「然後隻貓跳上你大腿？」\n\n"
                        f"😂 「你點知㗎！佢仲踩咗我杯咖啡，不過嗰一刻真係好治癒。」\n\n"
                        f"✨ 「呢啲就係生活俾你嘅小禮物啦。」"
                    ),
                    "titles": [
                        f"🌙 凌晨兩點的溫柔 | {first['en_title']} — 3 Hour Lofi Mix for Late Night Healing",
                        f"☕ 把失眠變成禮物 | Midnight {first['en_title']} — Calm Lofi Beats to Breathe & Relax",
                        f"🐱 貓咪都睡了只剩我和音樂 | {first['en_title']} — Soft Lofi for Quiet Souls",
                        f"🌧️ 雨聲 × Lofi × 一杯涼掉的咖啡 | {first['en_title']} — Aesthetic Chill Mix",
                        f"✨ 致每一個還醒著的溫柔靈魂 | {first['en_title']} — 3Hr Lofi Radio for Night Owls",
                    ],
                    "tags": (
                        f"lofi,lofi hip hop,chill beats,study music,late night lofi,"
                        f"{first['en_title'].lower().replace(' ','')},治癒音樂,深夜音樂,"
                        f"lofi mix,lofi radio,chill lofi,beats to relax,beats to study,"
                        f"lofi 2026,aesthetic lofi,cozy lofi,rainy lofi,midnight lofi,"
                        f"lofi playlist,soft lofi,warm lofi,lofi cafe,coffee lofi,"
                        f"sloth radio,樹懶電台,讀書音樂,放鬆音樂,助眠音樂,"
                        f"chill hop,lo-fi,lofi chill,japanese lofi,korean lofi,"
                        f"bedroom lofi,night owl music,3am music,healing music,"
                        f"rain and lofi,cozy bedroom,late night vibes,alone time music,"
                        f"溫柔音樂,失眠音樂,凌晨歌單,深夜電台,慵懶音樂,貓咪音樂"
                    ),
                }
                s.update(label="✅ 完成！",
                         state="complete", expanded=False)
            st.rerun()
    else:
        st.success("✅ 所有素材已就緒！")
        c1, c2 = st.columns(2)
        if c1.button("← 返回", use_container_width=True):
            st.session_state.final_results = {}
            go_to(2)
            st.rerun()
        if c2.button("📊 查看成果 →", type="primary", use_container_width=True):
            next_step()
            st.rerun()


# ═══════════════════════════════════════════════════════
#  STAGE 4 — Final Dashboard
# ═══════════════════════════════════════════════════════
elif step == 4:
    st.markdown("<div class='section-heading'>📊 成果總覽</div><div class='section-sub'>複製 → YouTube Studio 🎬</div>",
                unsafe_allow_html=True)

    r = st.session_state.final_results

    # 長故事
    long_story = r.get("long_story", "")
    st.markdown(
        f"<div class='result-label' style='margin-bottom:8px;'>📖 長文故事</div>"
        f"<div class='result-card'>"
        f"<div style='display:flex; justify-content:flex-end; margin-bottom:10px;'>"
        f"<button class='copy-btn' onclick='copyText(\"{quote(long_story)}\",this)'>複製</button>"
        f"</div>"
        f"<p style='color:rgba(255,255,255,0.75); line-height:1.85; font-size:14px; margin:0;'>"
        f"{_html.escape(long_story)}</p></div>",
        unsafe_allow_html=True)
    st.write("")

    # 短故事
    short_story = r.get("short_story", "")
    st.markdown(
        f"<div class='result-label' style='margin-bottom:8px;'>💬 對話短篇</div>"
        f"<div class='result-card' style='white-space:pre-wrap;'>"
        f"<div style='display:flex; justify-content:flex-end; margin-bottom:10px;'>"
        f"<button class='copy-btn' onclick='copyText(\"{quote(short_story)}\",this)'>複製</button>"
        f"</div>"
        f"<p style='color:rgba(255,255,255,0.75); line-height:1.9; font-size:14px; margin:0;'>"
        f"{_html.escape(short_story)}</p></div>",
        unsafe_allow_html=True)
    st.write("")

    # 5 標題（每條單獨複製）
    st.markdown("<div class='result-label' style='margin-bottom:8px;'>🏆 高點擊標題</div>",
                unsafe_allow_html=True)
    for i, t in enumerate(r.get("titles", []), 1):
        st.markdown(
            f"<div class='title-card'>"
            f"<span class='title-num'>#{i}</span>"
            f"<span class='title-text'>{_html.escape(t)}</span>"
            f"<button class='copy-btn' onclick='copyText(\"{quote(t)}\",this)'>複製</button>"
            f"</div>",
            unsafe_allow_html=True)
    st.write("")

    # Tags
    tags_str = r.get("tags", "")
    pills = "".join(
        f"<span class='tag-pill'>{_html.escape(tag.strip())}</span>"
        for tag in tags_str.split(",") if tag.strip())
    st.markdown(
        f"<div class='result-label' style='margin-bottom:8px;'>🏷️ SEO Tags"
        f"&nbsp;<span style='color:rgba(255,255,255,0.3); font-size:11px; font-weight:400; letter-spacing:0;'>"
        f"{len(tags_str)} / 500</span></div>"
        f"<div class='result-card'>"
        f"<div style='display:flex; justify-content:flex-end; margin-bottom:10px;'>"
        f"<button class='copy-btn' onclick='copyText(\"{quote(tags_str)}\",this)'>複製</button>"
        f"</div>"
        f"{pills}</div>",
        unsafe_allow_html=True)

    st.write("")
    st.divider()
    if st.button("🔄 重新開始", use_container_width=True):
        reset_pipeline()
        st.rerun()


# ─────────────────────────────────────────
#  Footer
# ─────────────────────────────────────────
st.write("")
st.markdown("<div style='text-align:center; color:rgba(255,255,255,0.15); font-size:11px; letter-spacing:1px; margin-top:48px;'>sLoth rAdio · YouTube Title Studio · Demo Mode</div>", unsafe_allow_html=True)
