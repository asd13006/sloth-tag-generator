import streamlit as st
import time
import json
import google.generativeai as genai
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
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Righteous&display=swap&font-display=swap');

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
/* 尊重用戶設定：停止裝飾性動畫 */
@media (prefers-reduced-motion: reduce) {
    .app-title { animation: none !important; }
    * { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; }
}
.app-subtitle {
    color: rgba(255,255,255,0.52);
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
    border: 2px solid rgba(255,255,255,0.25);
    background: transparent;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700;
    color: rgba(255,255,255,0.45);
    flex-shrink: 0;
    transition: all 0.3s ease;
}
.step-dot.active {
    border-color: #00ffcc;
    background: rgba(0,255,204,0.16);
    color: #00ffcc;
    box-shadow: 0 0 18px rgba(0,255,204,0.55), 0 0 6px rgba(0,255,204,0.75);
}
.step-dot.done {
    border-color: rgba(0,255,204,0.5);
    background: rgba(0,255,204,0.08);
    color: rgba(0,255,204,0.7);
}
.step-label {
    font-size: 13px;
    font-weight: 500;
    color: rgba(255,255,255,0.48);
    white-space: nowrap;
}
.step-label.active { color: #00ffcc; font-weight: 700; }
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
    font-size: 14px;
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
    font-size: 12px;
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
    font-size: 11px !important;
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
    font-size: 13px !important;
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
    font-size: 13px !important;
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
    font-size: 12px !important;
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
    font-size: 13px !important;
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
    font-size: 13px;
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
    font-size: 14px;
    color: #00ffcc;
    flex-shrink: 0;
    padding-top: 1px;
    min-width: 28px;
}
.title-text {
    font-size: 15px;
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

/* ── 圖片上傳預覽 */
[data-testid="stImage"] img {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
}

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  狀態管理
# ─────────────────────────────────────────
for key, default in [
    ("step", 1), ("song_data", []), ("selected_song_ids", []),
    ("concept_options", []), ("selected_concept", None), ("final_results", {}),
    ("n_songs", 10), ("_api_key", ""), ("_api_key_verified", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def next_step():   st.session_state.step += 1
def go_to(n):      st.session_state.step = n


# ─────────────────────────────────────────
#  Sidebar — API Key 設定與驗證
# ─────────────────────────────────────────
def _verify_api_key(key: str) -> bool:
    """對 Gemini 發送最小測試請求，回傳金鑰是否有效。"""
    try:
        genai.configure(api_key=key)
        m = genai.GenerativeModel("gemini-2.0-flash")
        m.generate_content(
            "hi",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1),
        )
        return True
    except Exception:
        return False


with st.sidebar:
    st.markdown(
        "<div style='font-family:Righteous,sans-serif;font-size:18px;"
        "color:#00ffcc;letter-spacing:1px;margin-bottom:4px;'>⚙️ 設定</div>",
        unsafe_allow_html=True,
    )
    _secret_key = ""
    try:
        _secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass

    if _secret_key:
        # Secrets 金鑰：首次自動驗證
        if not st.session_state._api_key_verified:
            st.session_state._api_key = _secret_key
            with st.spinner("🔍 驗證 Secrets 金鑰中..."):
                if _verify_api_key(_secret_key):
                    st.session_state._api_key_verified = True
                else:
                    st.error("❌ Secrets 金鑰無效，請重新設定。")
        else:
            st.markdown(
                "<div style='font-size:12px;color:rgba(0,255,204,0.7);"
                "padding:8px 10px;background:rgba(0,255,204,0.07);"
                "border:1px solid rgba(0,255,204,0.2);border-radius:8px;'>"
                "✅ API Key 已從 Secrets 載入並驗證</div>",
                unsafe_allow_html=True,
            )
    else:
        # 手動輸入金鑰
        _typed = st.text_input(
            "🔑 Gemini API Key",
            value=st.session_state._api_key,
            type="password",
            placeholder="AIza...",
            help="前往 aistudio.google.com 取得金鑰",
        )
        # 金鑰內容有變動 → 重置驗證狀態
        if _typed != st.session_state._api_key:
            st.session_state._api_key = _typed
            st.session_state._api_key_verified = False

        if st.session_state._api_key_verified:
            st.markdown(
                "<div style='font-size:12px;color:rgba(0,255,204,0.7);"
                "padding:8px 10px;background:rgba(0,255,204,0.07);"
                "border:1px solid rgba(0,255,204,0.2);border-radius:8px;"
                "margin-top:4px;'>✅ 金鑰驗證通過</div>",
                unsafe_allow_html=True,
            )
            if st.button("🔄 更換金鑰", use_container_width=True):
                st.session_state._api_key = ""
                st.session_state._api_key_verified = False
                st.rerun()
        elif st.session_state._api_key:
            if st.button("🔍 驗證金鑰", type="primary", use_container_width=True):
                with st.spinner("驗證中..."):
                    if _verify_api_key(st.session_state._api_key):
                        st.session_state._api_key_verified = True
                        st.rerun()
                    else:
                        st.error("❌ 金鑰無效，請確認後重試。")
        else:
            st.markdown(
                "<div style='font-size:12px;color:rgba(255,180,0,0.8);"
                "padding:6px 10px;background:rgba(255,180,0,0.06);"
                "border:1px solid rgba(255,180,0,0.2);border-radius:8px;"
                "margin-top:4px;'>⚠️ 請輸入 API Key 並驗證</div>",
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown(
        "<div style='font-size:11px;color:rgba(255,255,255,0.25);line-height:1.6;'>"
        "使用 Google Gemini API。<br>"
        "Key 僅存於本 session，不會傳送至第三方。"
        "</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
#  複製卡片 helpers（Stage 4 用）
# ─────────────────────────────────────────
_CARD_CSS = (
    "* { box-sizing: border-box; margin: 0; padding: 0; }"
    "html, body { background: transparent; font-family: -apple-system, 'Segoe UI', sans-serif; overflow: hidden; }"
    ".lbl { font-size: 12px; font-weight: 600; color: #00ffcc; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }"
    ".card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 18px 20px; }"
    ".copy-btn { background: rgba(0,255,204,0.08); border: 1px solid rgba(0,255,204,0.25); border-radius: 6px;"
    " color: #00ffcc; font-size: 12px; font-weight: 600; padding: 4px 12px; cursor: pointer; font-family: inherit; transition: background 0.2s; }"
    ".copy-btn:hover,.copy-btn.ok { background: rgba(0,255,204,0.2); border-color: rgba(0,255,204,0.5); }"
    ".trans-btn{background:rgba(176,38,255,0.1);border:1px solid rgba(176,38,255,0.3);border-radius:6px;"
    "color:#b026ff;font-size:12px;font-weight:600;padding:4px 10px;cursor:pointer;font-family:inherit;"
    "transition:background 0.2s;margin-right:6px;}"
    ".trans-btn:hover{background:rgba(176,38,255,0.22);border-color:rgba(176,38,255,0.55);}"
)

_COPY_JS = (
    "function doCopy(btn){"
    "var t=btn.getAttribute('data-text');"
    "function ok(){btn.textContent='已複製 ✓';btn.classList.add('ok');setTimeout(function(){btn.textContent='複製';btn.classList.remove('ok');},1500);}"
    "function fail(){btn.textContent='失敗';setTimeout(function(){btn.textContent='複製';},1500);}"
    "if(navigator.clipboard&&navigator.clipboard.writeText){"
    "navigator.clipboard.writeText(t).then(ok).catch(function(){"
    "var ta=document.createElement('textarea');ta.value=t;ta.style.cssText='position:fixed;opacity:0;';document.body.appendChild(ta);ta.select();"
    "try{document.execCommand('copy');ok();}catch(e){fail();}document.body.removeChild(ta);});}"
    "else{"
    "var ta=document.createElement('textarea');ta.value=t;ta.style.cssText='position:fixed;opacity:0;';document.body.appendChild(ta);ta.select();"
    "try{document.execCommand('copy');ok();}catch(e){fail();}document.body.removeChild(ta);}}"
)

_TRANS_JS = (
    "function toggleLang(){"
    "var w=document.getElementById('bl-wrapper');"
    "var l=w.getAttribute('data-lang')==='en'?'zh':'en';"
    "w.setAttribute('data-lang',l);"
    "var en=document.querySelectorAll('.en-block');"
    "var zh=document.querySelectorAll('.zh-block');"
    "for(var i=0;i<en.length;i++)en[i].style.display=l==='en'?'':'none';"
    "for(var i=0;i<zh.length;i++)zh[i].style.display=l==='zh'?'':'none';"
    "var tb=document.getElementById('trans-btn');"
    "if(tb)tb.textContent=l==='en'?'\U0001f310 \u4e2d\u6587':'\U0001f310 EN';}"
    "function doCopyBi(btn){"
    "var w=document.getElementById('bl-wrapper');"
    "var l=w.getAttribute('data-lang')||'en';"
    "var t=l==='en'?btn.getAttribute('data-en'):btn.getAttribute('data-zh');"
    "function ok(){btn.textContent='\u5df2\u8907\u88fd \u2713';btn.classList.add('ok');setTimeout(function(){btn.textContent='\u8907\u88fd';btn.classList.remove('ok');},1500);}"
    "function fail(){btn.textContent='\u5931\u6557';setTimeout(function(){btn.textContent='\u8907\u88fd';},1500);}"
    "if(navigator.clipboard&&navigator.clipboard.writeText){"
    "navigator.clipboard.writeText(t).then(ok).catch(function(){"
    "var ta=document.createElement('textarea');ta.value=t;ta.style.cssText='position:fixed;opacity:0;';document.body.appendChild(ta);ta.select();"
    "try{document.execCommand('copy');ok();}catch(e){fail();}document.body.removeChild(ta);});}"
    "else{"
    "var ta=document.createElement('textarea');ta.value=t;ta.style.cssText='position:fixed;opacity:0;';document.body.appendChild(ta);ta.select();"
    "try{document.execCommand('copy');ok();}catch(e){fail();}document.body.removeChild(ta);}}"
)


def _ae(text: str) -> str:
    return (text.replace('&', '&amp;').replace('"', '&quot;')
                .replace("'", '&#39;').replace('<', '&lt;').replace('>', '&gt;'))


def _he(text: str) -> str:
    return (text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                .replace('\n', '<br>'))


def _est_height(text: str, chars_per_line: int = 55, line_px: int = 28, overhead: int = 124) -> int:
    lines = sum(max(1, (len(p) + chars_per_line - 1) // chars_per_line)
                for p in text.split('\n'))
    return max(145, overhead + lines * line_px)


def _copy_card_html(label: str, content_html: str, raw_text: str, card_extra_style: str = "") -> str:
    ae_raw = _ae(raw_text)
    return (
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
        + _CARD_CSS
        + '.content{color:rgba(255,255,255,0.75);font-size:15px;line-height:1.85;}'
        + '</style></head><body>'
        + f'<div class="lbl">{label}</div>'
        + f'<div class="card" style="{card_extra_style}">'
        + '<div style="display:flex;justify-content:flex-end;margin-bottom:12px;">'
        + f'<button class="copy-btn" data-text="{ae_raw}" onclick="doCopy(this)">複製</button>'
        + '</div>'
        + f'<div class="content">{content_html}</div>'
        + '</div>'
        + f'<script>{_COPY_JS}</script>'
        + '</body></html>'
    )


def _bilingual_story_html(label: str, en_text: str, zh_text: str, card_extra_style: str = "") -> str:
    ae_en = _ae(en_text)
    ae_zh = _ae(zh_text)
    return (
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
        + _CARD_CSS
        + '.content{color:rgba(255,255,255,0.75);font-size:15px;line-height:1.85;}'
        + '</style></head><body><div id="bl-wrapper" data-lang="en">'
        + f'<div class="lbl">{label}</div>'
        + f'<div class="card" style="{card_extra_style}">'
        + '<div style="display:flex;justify-content:flex-end;align-items:center;gap:6px;margin-bottom:12px;">'
        + '<button class="trans-btn" id="trans-btn" onclick="toggleLang()">🌐 中文</button>'
        + f'<button class="copy-btn" data-en="{ae_en}" data-zh="{ae_zh}" onclick="doCopyBi(this)">複製</button>'
        + '</div>'
        + f'<div class="en-block content">{_he(en_text)}</div>'
        + f'<div class="zh-block content" style="display:none">{_he(zh_text)}</div>'
        + '</div>'
        + f'</div><script>{_TRANS_JS}</script>'
        + '</body></html>'
    )


def _bilingual_titles_html(titles_en: list, titles_zh: list) -> str:
    pairs = list(zip(titles_en, (titles_zh or titles_en)))
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
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
        + _CARD_CSS
        + '.title-row{display:flex;align-items:flex-start;gap:14px;background:rgba(255,255,255,0.04);'
        + 'border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px 18px;margin-bottom:8px;}'
        + '.tnum{font-size:14px;color:#00ffcc;flex-shrink:0;padding-top:2px;min-width:28px;font-weight:700;}'
        + '.ttxt-wrap{flex:1;}'
        + '.ttxt{font-size:15px;font-weight:500;color:rgba(255,255,255,0.88);line-height:1.5;}'
        + '</style></head><body>'
        + '<div id="bl-wrapper" data-lang="en">'
        + '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
        + '<div class="lbl" style="margin:0;">🏆 High-Click Titles</div>'
        + '<button class="trans-btn" id="trans-btn" onclick="toggleLang()">🌐 中文</button>'
        + '</div>'
        + rows
        + f'</div><script>{_TRANS_JS}</script>'
        + '</body></html>'
    )


def _title_cards_html(titles: list) -> str:
    rows = "".join(
        f'<div class="title-row">'
        f'<span class="tnum">#{i}</span>'
        f'<span class="ttxt">{_he(t)}</span>'
        f'<button class="copy-btn" data-text="{_ae(t)}" onclick="doCopy(this)">複製</button>'
        f'</div>'
        for i, t in enumerate(titles, 1)
    )
    return (
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
        + _CARD_CSS
        + '.title-row{display:flex;align-items:flex-start;gap:14px;background:rgba(255,255,255,0.04);'
        + 'border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px 18px;margin-bottom:8px;}'
        + '.tnum{font-size:14px;color:#00ffcc;flex-shrink:0;padding-top:1px;min-width:28px;font-weight:700;}'
        + '.ttxt{font-size:15px;font-weight:500;color:rgba(255,255,255,0.88);line-height:1.5;flex:1;}'
        + '.title-row .copy-btn{margin-left:auto;padding:3px 8px;font-size:11px;align-self:center;flex-shrink:0;}'
        + '</style></head><body>'
        + '<div class="lbl">🏆 高點擊標題</div>'
        + rows
        + f'<script>{_COPY_JS}</script>'
        + '</body></html>'
    )


def _tags_card_html(tags_str: str) -> str:
    count = len(tags_str)
    pills = "".join(
        f'<span class="tag-pill">{_he(t.strip())}</span>'
        for t in tags_str.split(',') if t.strip()
    )
    return (
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
        + _CARD_CSS
        + '.count{color:rgba(255,255,255,0.3);font-size:12px;font-weight:400;letter-spacing:0;}'
        + '.tag-pill{display:inline-block;background:rgba(0,255,204,0.08);border:1px solid rgba(0,255,204,0.2);'
        + 'border-radius:20px;padding:3px 11px;margin:3px 3px;color:#00ffcc;font-size:13px;font-weight:500;}'
        + '</style></head><body>'
        + f'<div class="lbl">🏷️ SEO Tags &nbsp;<span class="count">{count} / 500</span></div>'
        + '<div class="card">'
        + '<div style="display:flex;justify-content:flex-end;margin-bottom:12px;">'
        + f'<button class="copy-btn" data-text="{_ae(tags_str)}" onclick="doCopy(this)">複製</button>'
        + '</div>'
        + pills
        + '</div>'
        + f'<script>{_COPY_JS}</script>'
        + '</body></html>'
    )


def _songs_card_html(songs: list) -> str:
    rows = ""
    for i, s in enumerate(songs, 1):
        en = s.get("en_title", "")
        zh = s.get("zh_title", "")
        en_theme = s.get("en_theme", "")
        zh_theme = s.get("zh_theme", "")
        copy_text = f"{i}. \u300a{en}\u300b {zh}\nLyric Theme: {en_theme}\n{zh_theme}"
        rows += (
            f'<div class="song-row">'
            f'<div class="sinfo">'
            f'<div class="stitle">{i}. \u300a{_he(en)}\u300b\u3000{_he(zh)}</div>'
            f'<div class="stheme-lbl">Lyric Theme</div>'
            f'<div class="stheme-en">{_he(en_theme)}</div>'
            f'<div class="stheme-zh">{_he(zh_theme)}</div>'
            f'</div>'
            f'<button class="copy-btn" style="flex-shrink:0;align-self:flex-start;margin-top:2px;"'
            f' data-text="{_ae(copy_text)}" onclick="doCopy(this)">\u8907\u88fd</button>'
            f'</div>'
        )
    count = len(songs)
    label = f'{count} track{"s" if count != 1 else ""}'
    return (
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
        + _CARD_CSS
        + '.song-row{display:flex;align-items:flex-start;gap:12px;padding:14px 0;'
        + 'border-bottom:1px solid rgba(255,255,255,0.06);}'
        + '.song-row:last-child{border-bottom:none;}'
        + '.sinfo{flex:1;}'
        + '.stitle{font-size:15px;font-weight:700;color:rgba(255,255,255,0.92);margin-bottom:6px;line-height:1.4;}'
        + '.stheme-lbl{font-size:11px;color:#00ffcc;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;}'
        + '.stheme-en{font-size:13px;color:rgba(255,255,255,0.62);line-height:1.55;margin-bottom:3px;}'
        + '.stheme-zh{font-size:13px;color:rgba(255,255,255,0.38);line-height:1.55;font-style:italic;}'
        + '</style></head><body>'
        + f'<div class="lbl">\U0001f3b5 Selected Songs &nbsp;<span style="color:rgba(255,255,255,0.3);font-size:12px;font-weight:400;letter-spacing:0;">{label}</span></div>'
        + '<div class="card">'
        + rows
        + '</div>'
        + f'<script>{_COPY_JS}</script>'
        + '</body></html>'
    )


def _dashboard_html(songs, long_story, long_story_zh,
                    short_story, short_story_zh,
                    titles, titles_zh, tags_str):
    css = (
        "* { box-sizing: border-box; margin: 0; padding: 0; }"
        "html { overflow-y: hidden; } body { background: transparent; font-family: -apple-system, 'Segoe UI', sans-serif; overflow: hidden; }"
        ".sec:last-child { margin-bottom: 0; }"
        ".lbl { font-size: 12px; font-weight: 600; color: #00ffcc; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }"
        ".card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 18px 20px; }"
        ".copy-btn { background: rgba(0,255,204,0.08); border: 1px solid rgba(0,255,204,0.25); border-radius: 6px; color: #00ffcc; font-size: 12px; font-weight: 600; padding: 4px 12px; cursor: pointer; font-family: inherit; transition: background 0.2s; }"
        ".copy-btn:hover,.copy-btn.ok { background: rgba(0,255,204,0.2); border-color: rgba(0,255,204,0.5); }"
        ".trans-btn { background: rgba(176,38,255,0.1); border: 1px solid rgba(176,38,255,0.3); border-radius: 6px; color: #b026ff; font-size: 12px; font-weight: 600; padding: 4px 10px; cursor: pointer; font-family: inherit; transition: background 0.2s; margin-right: 6px; }"
        ".trans-btn:hover { background: rgba(176,38,255,0.22); border-color: rgba(176,38,255,0.55); }"
        ".sec { margin-bottom: 20px; }"
        ".content { color: rgba(255,255,255,0.75); font-size: 15px; line-height: 1.85; }"
        ".btn-row { display: flex; justify-content: flex-end; align-items: center; gap: 6px; margin-bottom: 12px; }"
        ".song-row { display: flex; align-items: flex-start; gap: 12px; padding: 14px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }"
        ".song-row:last-child { border-bottom: none; }"
        ".sinfo { flex: 1; }"
        ".stitle { font-size: 15px; font-weight: 700; color: rgba(255,255,255,0.92); margin-bottom: 6px; line-height: 1.4; }"
        ".stheme-lbl { font-size: 11px; color: #00ffcc; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 4px; }"
        ".stheme-en { font-size: 13px; color: rgba(255,255,255,0.62); line-height: 1.55; margin-bottom: 3px; }"
        ".stheme-zh { font-size: 13px; color: rgba(255,255,255,0.38); line-height: 1.55; font-style: italic; }"
        ".title-row { display: flex; align-items: flex-start; gap: 14px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px 18px; margin-bottom: 8px; }"
        ".tnum { font-size: 14px; color: #00ffcc; flex-shrink: 0; padding-top: 2px; min-width: 28px; font-weight: 700; }"
        ".ttxt-wrap { flex: 1; }"
        ".ttxt { font-size: 15px; font-weight: 500; color: rgba(255,255,255,0.88); line-height: 1.5; }"
        ".count { color: rgba(255,255,255,0.3); font-size: 12px; font-weight: 400; letter-spacing: 0; }"
        ".tag-pill { display: inline-block; background: rgba(0,255,204,0.08); border: 1px solid rgba(0,255,204,0.2); border-radius: 20px; padding: 3px 11px; margin: 3px 3px; color: #00ffcc; font-size: 13px; font-weight: 500; }"
    )
    js = (
        "function toggleLang(btn){"
        "var w=btn.closest('[data-lang]');"
        "var l=w.getAttribute('data-lang')==='en'?'zh':'en';"
        "w.setAttribute('data-lang',l);"
        "var en=w.querySelectorAll('.en-block');"
        "var zh=w.querySelectorAll('.zh-block');"
        "for(var i=0;i<en.length;i++)en[i].style.display=l==='en'?'':'none';"
        "for(var i=0;i<zh.length;i++)zh[i].style.display=l==='zh'?'':'none';"
        "btn.textContent=l==='en'?'\U0001f310 \u4e2d\u6587':'\U0001f310 EN';}"
        "function _cp(t,ok,fail){"
        "if(navigator.clipboard&&navigator.clipboard.writeText){"
        "navigator.clipboard.writeText(t).then(ok).catch(function(){"
        "var ta=document.createElement('textarea');ta.value=t;ta.style.cssText='position:fixed;opacity:0;';document.body.appendChild(ta);ta.select();"
        "try{document.execCommand('copy');ok();}catch(e){fail();}document.body.removeChild(ta);});}"
        "else{var ta=document.createElement('textarea');ta.value=t;ta.style.cssText='position:fixed;opacity:0;';document.body.appendChild(ta);ta.select();"
        "try{document.execCommand('copy');ok();}catch(e){fail();}document.body.removeChild(ta);}}"
        "function _fb(btn){return function ok(){btn.textContent='\u5df2\u8907\u88fd \u2713';btn.classList.add('ok');setTimeout(function(){btn.textContent='\u8907\u88fd';btn.classList.remove('ok');},1500);}}"
        "function _ff(btn){return function fail(){btn.textContent='\u5931\u6557';setTimeout(function(){btn.textContent='\u8907\u88fd';},1500);}}"
        "function doCopy(btn){_cp(btn.getAttribute('data-text'),_fb(btn),_ff(btn));}"
        "function doCopyBi(btn){"
        "var w=btn.closest('[data-lang]');"
        "var l=w?(w.getAttribute('data-lang')||'en'):'en';"
        "var t=l==='en'?btn.getAttribute('data-en'):btn.getAttribute('data-zh');"
        "_cp(t,_fb(btn),_ff(btn));}"
    )
    # Songs section
    song_rows = ""
    for i, s in enumerate(songs, 1):
        en, zh = s.get("en_title", ""), s.get("zh_title", "")
        et, zt = s.get("en_theme", ""), s.get("zh_theme", "")
        ct = f"{i}. \u300a{en}\u300b {zh}\nLyric Theme: {et}\n{zt}"
        song_rows += (
            f'<div class="song-row">'
            f'<div class="sinfo">'
            f'<div class="stitle">{i}. \u300a{_he(en)}\u300b\u3000{_he(zh)}</div>'
            f'<div class="stheme-lbl">Lyric Theme</div>'
            f'<div class="stheme-en">{_he(et)}</div>'
            f'<div class="stheme-zh">{_he(zt)}</div>'
            f'</div>'
            f'<button class="copy-btn" style="flex-shrink:0;align-self:flex-start;margin-top:2px;"'
            f' data-text="{_ae(ct)}" onclick="doCopy(this)">\u8907\u88fd</button>'
            f'</div>'
        )
    n = len(songs)
    songs_sec = (
        f'<div class="sec">'
        f'<div class="lbl">\U0001f3b5 Selected Songs'
        f'&nbsp;<span style="color:rgba(255,255,255,0.3);font-size:11px;font-weight:400;letter-spacing:0;">'
        f'{n} track{"s" if n != 1 else ""}</span></div>'
        f'<div class="card">{song_rows}</div>'
        f'</div>'
    ) if songs else ""

    # Story helper
    def _story_sec(lbl, en_t, zh_t, extra=""):
        return (
            f'<div class="sec" data-lang="en">'
            f'<div class="lbl">{lbl}</div>'
            f'<div class="card" style="{extra}">'
            f'<div class="btn-row">'
            f'<button class="trans-btn" onclick="toggleLang(this)">\U0001f310 \u4e2d\u6587</button>'
            f'<button class="copy-btn" data-en="{_ae(en_t)}" data-zh="{_ae(zh_t)}" onclick="doCopyBi(this)">\u8907\u88fd</button>'
            f'</div>'
            f'<div class="en-block content">{_he(en_t)}</div>'
            f'<div class="zh-block content" style="display:none">{_he(zh_t)}</div>'
            f'</div></div>'
        )

    # Titles section
    title_rows = "".join(
        f'<div class="title-row">'
        f'<span class="tnum">#{i}</span>'
        f'<div class="ttxt-wrap">'
        f'<span class="en-block ttxt">{_he(en)}</span>'
        f'<span class="zh-block ttxt" style="display:none">{_he(zh)}</span>'
        f'</div>'
        f'<button class="copy-btn" style="flex-shrink:0;align-self:center;padding:3px 8px;font-size:11px;"'
        f' data-en="{_ae(en)}" data-zh="{_ae(zh)}" onclick="doCopyBi(this)">\u8907\u88fd</button>'
        f'</div>'
        for i, (en, zh) in enumerate(zip(titles, titles_zh or titles), 1)
    )
    titles_sec = (
        f'<div class="sec" data-lang="en">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
        f'<div class="lbl" style="margin:0;">\U0001f3c6 High-Click Titles</div>'
        f'<button class="trans-btn" onclick="toggleLang(this)">\U0001f310 \u4e2d\u6587</button>'
        f'</div>'
        f'{title_rows}'
        f'</div>'
    )

    # Tags section
    n_tags = sum(1 for t in tags_str.split(',') if t.strip())
    pills = "".join(
        f'<span class="tag-pill">{_he(t.strip())}</span>'
        for t in tags_str.split(',') if t.strip()
    )
    tags_sec = (
        f'<div class="sec">'
        f'<div class="lbl">\U0001f3f7\ufe0f SEO Tags'
        f'&nbsp;<span class="count">{len(tags_str)} / 500</span></div>'
        f'<div class="card">'
        f'<div class="btn-row">'
        f'<button class="copy-btn" data-text="{_ae(tags_str)}" onclick="doCopy(this)">\u8907\u88fd</button>'
        f'</div>'
        f'{pills}'
        f'</div></div>'
    )

    body = (songs_sec
            + _story_sec("\U0001f4d6 Long Story", long_story, long_story_zh)
            + _story_sec("\U0001f4ac Short Story", short_story, short_story_zh,
                         extra="white-space:pre-wrap;")
            + titles_sec
            + tags_sec)
    return (
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>' +
        css + '</style></head><body>'
        + body
        + f'<script>{js}</script>'
        + '</body></html>'
    )


def reset_pipeline():
    for k in ["song_data", "selected_song_ids", "concept_options", "selected_concept", "final_results"]:
        st.session_state[k] = [] if k in ("song_data", "selected_song_ids", "concept_options") else (
            None if k == "selected_concept" else {})
    st.session_state.step = 1


# ─────────────────────────────────────────
#  Gemini AI 輔助函式
# ─────────────────────────────────────────
def _get_model():
    """取得設定好 API Key 的 Gemini 模型，若無 Key 回傳 None。"""
    key = st.session_state.get("_api_key", "")
    if not key:
        return None
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-2.0-flash")


def _call_gemini_json(prompt: str) -> dict | list | None:
    """呼叫 Gemini 並解析 JSON 回應；失敗時回傳 None。"""
    model = _get_model()
    if model is None:
        return None
    try:
        resp = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.9,
                response_mime_type="application/json",
            ),
        )
        return json.loads(resp.text)
    except Exception as e:
        st.warning(f"⚠️ Gemini 呼叫失敗：{e}")
        return None


def ai_generate_songs(n: int) -> list[dict]:
    """用 Gemini 生成 n 首 lofi 歌曲資料，失敗時回傳空列表。"""
    prompt = f"""You are a creative lofi music curator. Generate {n} unique lofi music track concepts.
Return a JSON array with exactly {n} objects. Each object must have these keys:
- "en_title": evocative English title (2-5 words, poetic, lowercase-style)
- "zh_title": poetic Traditional Chinese translation (3-6 characters)
- "en_theme": one vivid, sensory English sentence (max 15 words) describing the mood or scene
- "zh_theme": Traditional Chinese translation of en_theme (avoid literal translation, keep poetry)

Aesthetics: cozy, introspective, lofi/chillhop — everyday quiet moments.
Return ONLY a valid JSON array. No markdown, no explanation."""
    data = _call_gemini_json(prompt)
    if isinstance(data, list) and len(data) >= n:
        # 補上 id 欄位
        return [{"id": i + 1, **{k: str(item.get(k, "")) for k in ("en_title", "zh_title", "en_theme", "zh_theme")}}
                for i, item in enumerate(data[:n])]
    return []


def ai_generate_concepts(sel_songs: list[dict], vibe: str) -> list[tuple[str, str]]:
    """用 Gemini 生成 3 個概念方向，失敗時回傳預設選項。"""
    song_names = "、".join(s["zh_title"] for s in sel_songs[:6])
    prompt = f"""You are a creative director for a lofi music YouTube channel.
Songs in this video: {song_names}
Vibe/atmosphere keywords from the creator: "{vibe or '無特定氛圍'}"

Generate exactly 3 distinct visual/story concept directions for the video thumbnail & description.
Return a JSON array of 3 objects, each with:
- "title": short concept title in Traditional Chinese with ONE leading emoji (max 10 characters total)
- "desc": one atmospheric sentence in Traditional Chinese describing the scene (max 30 characters)

Make each concept feel different: vary the time of day, setting, or emotional angle.
Return ONLY a valid JSON array. No markdown, no explanation."""
    data = _call_gemini_json(prompt)
    if isinstance(data, list) and len(data) >= 3:
        return [(str(item.get("title", f"概念 {i+1}")), str(item.get("desc", "")))
                for i, item in enumerate(data[:3])]
    return []


def ai_generate_assets(sel_songs: list[dict], concept: str) -> dict:
    """用 Gemini 生成完整 SEO 素材，失敗時回傳空字典。"""
    song_list = "\n".join(
        f"- {s['en_title']} / {s['zh_title']}: {s['en_theme']}" for s in sel_songs
    )
    prompt = f"""You are a YouTube SEO copywriter for a lofi music channel called "sLoth rAdio".

Songs included in this video:
{song_list}

Creative direction / concept: {concept}

Generate the following assets and return as a single JSON object with these exact keys:
- "long_story": atmospheric English prose (4–6 paragraphs, 280–380 words), written in second-person ("you"), immersive slice-of-life style
- "long_story_zh": Traditional Chinese translation of long_story, equally poetic
- "short_story": Instagram-caption style English version with relevant emojis (3–4 short paragraphs, ~130 words)
- "short_story_zh": Traditional Chinese translation of short_story
- "titles": JSON array of 5 YouTube title strings in English; SEO-optimized; include lofi genre keyword; end with relevant emojis
- "titles_zh": JSON array of 5 matching Traditional Chinese YouTube titles
- "tags": comma-separated string of 35–45 YouTube SEO tags, mix of broad and niche lofi keywords

Return ONLY a valid JSON object. No markdown, no explanation."""
    data = _call_gemini_json(prompt)
    if isinstance(data, dict) and data.get("long_story"):
        # 確保 titles 欄位是 list
        for k in ("titles", "titles_zh"):
            if not isinstance(data.get(k), list):
                data[k] = []
        return data
    return {}


# ─────────────────────────────────────────
#  Mock 歌單資料
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  API Key Gate — 未驗證時顯示封鎖畫面
# ─────────────────────────────────────────
if not st.session_state._api_key_verified:
    st.markdown(
        """
        <div style='display:flex;flex-direction:column;align-items:center;
             justify-content:center;padding:80px 20px;text-align:center;'>
          <div style='font-size:56px;margin-bottom:24px;'>🔑</div>
          <div style='font-family:Righteous,sans-serif;font-size:28px;
               background:linear-gradient(90deg,#00ffcc,#b026ff);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               margin-bottom:12px;'>Title Studio</div>
          <div style='font-size:14px;color:rgba(255,255,255,0.45);
               letter-spacing:1px;margin-bottom:32px;'>sLoth rAdio · Gemini AI</div>
          <div style='font-size:15px;color:rgba(255,255,255,0.6);
               background:rgba(255,255,255,0.04);
               border:1px solid rgba(255,255,255,0.08);
               border-radius:14px;padding:24px 32px;max-width:380px;line-height:1.8;'>
            請在左側側欄輸入<br>
            <span style='color:#00ffcc;font-weight:600;'>Gemini API Key</span>
            並按下「驗證金鑰」<br>
            驗證通過後即可使用 Title Studio。
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ─────────────────────────────────────────
#  App Header
# ─────────────────────────────────────────
hcol1, hcol2 = st.columns([1, 3])
with hcol1:
    st.markdown("<div class='app-title'>Title Studio</div><div class='app-subtitle'>sLoth rAdio · Gemini AI</div>", unsafe_allow_html=True)
with hcol2:
    if st.session_state.step > 1 or st.session_state.song_data:
        _hdr_info, _hdr_btn = st.columns([3, 1])
        with _hdr_info:
            st.markdown(
                "<div style='display:flex;align-items:center;height:100%;justify-content:flex-end;'>"
                "<span style='color:rgba(255,255,255,0.50);font-size:12px;letter-spacing:2px;text-transform:uppercase;'>AI · YouTube SEO Pipeline</span>"
                "</div>",
                unsafe_allow_html=True,
            )
        with _hdr_btn:
            if st.button("🔄 重置", key="header_reset", use_container_width=True):
                reset_pipeline()
                st.rerun()
    else:
        st.markdown(
            "<div style='display:flex;align-items:center;justify-content:flex-end;height:100%;'>"
            "<span style='color:rgba(255,255,255,0.50);font-size:12px;letter-spacing:2px;text-transform:uppercase;'>AI · YouTube SEO Pipeline</span>"
            "</div>",
            unsafe_allow_html=True,
        )

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
            st.markdown("<div style='color:rgba(255,255,255,0.40); font-size:12px; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;'>🎚️ 生成數量</div>", unsafe_allow_html=True)
            n = st.slider("n_songs_slider", min_value=1, max_value=20,
                          value=st.session_state.n_songs, step=1, label_visibility="collapsed")
            st.session_state.n_songs = n
            if st.button(f"✨  生成 {n} 首歌曲", type="primary", use_container_width=True):
                with st.spinner("✨ AI 生成中..."):
                    _songs = ai_generate_songs(n)
                if _songs:
                    st.session_state.song_data = _songs
                    st.rerun()

        st.write("")
        _fc1, _fc2, _fc3 = st.columns(3)
        for _fc, (_ficon, _ftitle, _fdesc) in zip(
            [_fc1, _fc2, _fc3],
            [
                ("🎵", "AI 歌單生成", "一鍵產生詩意歌名與意境描述，快速建立創作素材庫"),
                ("🎨", "視覺概念提煉", "輸入氛圍關鍵字，AI 生成 3 個差異化故事方向"),
                ("📋", "完整 SEO 套件", "長文故事 · 短文貼文 · 高點擊標題 · Tags 全套輸出"),
            ],
        ):
            with _fc:
                st.markdown(
                    f"<div style='background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);"
                    f"border-radius:14px;padding:22px 20px;text-align:center;'>"
                    f"<div style='font-size:28px;margin-bottom:10px;'>{_ficon}</div>"
                    f"<div style='font-size:14px;font-weight:600;color:rgba(255,255,255,0.80);margin-bottom:6px;'>{_ftitle}</div>"
                    f"<div style='font-size:13px;color:rgba(255,255,255,0.36);line-height:1.6;'>{_fdesc}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

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
            "<div style='border-top:1px solid rgba(255,255,255,0.07);margin-top:16px;margin-bottom:0;'></div>", unsafe_allow_html=True)
        _ac0, _ac1, _ac2, _ac3 = st.columns([2, 1, 1, 3])
        with _ac0:
            st.markdown(
                f"<div style='display:flex;align-items:center;padding-top:6px;'>"
                f"<span style='font-size:13px;color:rgba(255,255,255,0.5);'>"
                f"<span style='font-size:20px;font-weight:800;color:#00ffcc;font-family:Righteous,sans-serif;'>{n_selected}</span>"
                f" / {len(songs)} ✓</span></div>",
                unsafe_allow_html=True,
            )
        with _ac1:
            if st.button("✓ 全選", use_container_width=True):
                st.session_state.selected_song_ids = [s["id"] for s in songs]
                st.rerun()
        with _ac2:
            if st.button("✕ 清除", use_container_width=True):
                st.session_state.selected_song_ids = []
                st.rerun()
        with _ac3:
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
        f"<div class='result-card'><div class='result-label'>🎵 已選歌曲</div><span style='color:rgba(255,255,255,0.7); font-size:15px;'>{names}</span></div>", unsafe_allow_html=True)

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
                sel_songs = [s for s in st.session_state.song_data if s["id"]
                             in st.session_state.selected_song_ids]
                opts = ai_generate_concepts(sel_songs, vibe)
            if opts:
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
    else:
        st.markdown(
            "<div style='text-align:center;padding:40px 0 20px;'>"
            "<div style='font-size:36px;margin-bottom:12px;'>🎲</div>"
            "<div style='font-size:14px;letter-spacing:1px;color:rgba(255,255,255,0.22);'>按下「生成方向」讓 AI 構思故事視角</div>"
            "</div>",
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════
#  STAGE 3 — SEO Assets
# ═══════════════════════════════════════════════════════
elif step == 3:
    st.markdown("<div class='section-heading'>✍️ SEO 素材</div><div class='section-sub'>生成故事 · 標題 · Tags</div>",
                unsafe_allow_html=True)

    sel_songs = [s for s in st.session_state.song_data if s["id"]
                 in st.session_state.selected_song_ids]
    concept = st.session_state.selected_concept or "—"
    _song_preview = " · ".join(s["zh_title"] for s in sel_songs[:4])
    if len(sel_songs) > 4:
        _song_preview += f" +{len(sel_songs) - 4}"
    st.markdown(
        f"<div class='result-card'>"
        f"<div class='result-label'>🎯 Creative Brief</div>"
        f"<p style='color:rgba(255,255,255,0.6); font-size:14px; margin:0 0 4px;'>🎵 <span style='color:#fff;'>{len(sel_songs)} 首</span>"
        f"<span style='color:rgba(255,255,255,0.35); font-size:13px; margin-left:8px;'>{_song_preview}</span></p>"
        f"<p style='color:rgba(255,255,255,0.6); font-size:14px; margin:0;'>🎨 <span style='color:#00ffcc;'>{concept}</span></p>"
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
            with st.status("⚙️ AI 生成中...", expanded=True) as s:
                st.write("🤖 呼叫 Gemini，撰寫故事與 SEO 素材...")
                results = ai_generate_assets(sel_songs, concept)
                if results:
                    st.session_state.final_results = results
                    s.update(label="✅ 完成！", state="complete", expanded=False)
                else:
                    s.update(label="❌ 生成失敗，請稍後再試。",
                             state="error", expanded=False)
            if st.session_state.final_results:
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
    sel_songs = [s for s in st.session_state.song_data
                 if s["id"] in st.session_state.selected_song_ids]

    long_story = r.get("long_story", "")
    long_story_zh = r.get("long_story_zh", long_story)
    short_story = r.get("short_story", "")
    short_story_zh = r.get("short_story_zh", short_story)
    titles = r.get("titles", [])
    titles_zh = r.get("titles_zh", titles)
    tags_str = r.get("tags", "")

    n_tags = sum(1 for t in tags_str.split(',') if t.strip())
    # 依照 CSS 實際渲染高度精算：
    st.iframe(
        _dashboard_html(sel_songs, long_story, long_story_zh,
                        short_story, short_story_zh,
                        titles, titles_zh, tags_str),
        height="content",
    )
    st.divider()
    _s4c1, _s4c2 = st.columns(2)
    with _s4c1:
        if st.button("← 返回素材", use_container_width=True):
            go_to(3)
            st.rerun()
    with _s4c2:
        if st.button("🔄 重新開始", use_container_width=True):
            reset_pipeline()
            st.rerun()


# ─────────────────────────────────────────
#  Footer
# ─────────────────────────────────────────
st.write("")
st.markdown("<div style='text-align:center; color:rgba(255,255,255,0.35); font-size:11px; letter-spacing:1px; margin-top:48px;'>sLoth rAdio · YouTube Title Studio · Powered by Gemini</div>", unsafe_allow_html=True)
