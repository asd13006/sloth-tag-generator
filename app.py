"""
sLoth rAdio · Title Studio
YouTube SEO Pipeline powered by Google Gemini AI

UI Language: Traditional Chinese
Design: OLED Dark + Neon Teal (#00ffcc / #b026ff)
"""

import json
import streamlit as st
from PIL import Image

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    st.error(
        "❌ **缺少 `google-genai` 套件**\n\n"
        "請在 Streamlit Cloud 管理頁面：\n"
        "1. 點擊右下角 **Manage app**\n"
        "2. 點擊 **Reboot** 或三點選單中的 **Clear cache and deploy**\n\n"
        "如問題持續，請確認 `requirements.txt` 中包含 `google-genai>=1.0.0`"
    )
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="sLoth rAdio · Title Studio",
    page_icon="🎵",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS  ── OLED Dark + Bento Grid design system
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Righteous&display=swap&font-display=swap');

html, body, [class*="css"] { font-family: 'Poppins', -apple-system, sans-serif; color-scheme: dark; }
.stApp {
    background-color: #0A0A14 !important;
    background-image: radial-gradient(rgba(0,255,204,0.03) 1px, transparent 1px) !important;
    background-size: 30px 30px !important;
}
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1280px !important; }
.stApp > header { background: transparent !important; }

@keyframes gradient-text {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.app-title {
    font-family: 'Righteous', sans-serif; font-size: 38px; font-weight: 400;
    letter-spacing: 1px;
    background: linear-gradient(270deg, #00ffcc, #b026ff, #00E676, #00ffcc);
    background-size: 300% 300%;
    animation: gradient-text 5s ease 1 forwards;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1.2;
}
@media (prefers-reduced-motion: reduce) {
    .app-title { animation: none !important; }
    * { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; }
}
.app-subtitle { color: rgba(255,255,255,0.52); font-size: 12px; font-weight: 500; letter-spacing: 3px; text-transform: uppercase; margin-top: 4px; }

/* Pipeline Stepper */
.stepper { display: flex; align-items: center; gap: 0; margin: 28px 0 32px; }
.step-item { display: flex; align-items: center; gap: 10px; flex: 1; }
.step-item:last-child { flex: 0; }
.step-dot { width: 32px; height: 32px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.45); background: transparent; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; color: rgba(255,255,255,0.45); flex-shrink: 0; transition: all 0.3s ease; }
.step-dot.active { border-color: #00ffcc; background: rgba(0,255,204,0.16); color: #00ffcc; box-shadow: 0 0 18px rgba(0,255,204,0.55), 0 0 6px rgba(0,255,204,0.75); }
.step-dot.done { border-color: rgba(0,255,204,0.5); background: rgba(0,255,204,0.08); color: rgba(0,255,204,0.7); }
.step-label { font-size: 13px; font-weight: 500; color: rgba(255,255,255,0.55); white-space: nowrap; }
.step-label.active { color: #00ffcc; font-weight: 700; }
.step-label.done { color: rgba(0,255,204,0.5); }
.step-connector { height: 1px; background: rgba(255,255,255,0.08); flex: 1; margin: 0 12px; }
.step-connector.done { background: rgba(0,255,204,0.25); }

/* Section headings */
.section-heading { font-family: 'Righteous', sans-serif; font-size: 20px; color: #FFFFFF; margin: 0 0 6px; letter-spacing: 0.5px; }
.section-sub { font-size: 14px; color: rgba(255,255,255,0.55); margin: 0 0 24px; }

/* Result cards */
.result-card { background: rgba(10,10,20,0.7); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px; margin-bottom: 20px; }
.result-label { font-size: 12px; font-weight: 600; color: #00ffcc; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }

/* Song Cards */
[data-testid="stVerticalBlock"]:has(button:has(p:nth-of-type(5)))
    > div[data-testid="element-container"] {
    height: 260px !important; min-height: 260px !important; max-height: 260px !important;
    overflow: hidden !important; flex-shrink: 0 !important; padding: 0 !important; margin: 0 0 8px 0 !important;
}
[data-testid="stVerticalBlock"]:has(button:has(p:nth-of-type(5)))
    > div[data-testid="element-container"]
    > [data-testid="stBaseButtonContainer"],
[data-testid="stVerticalBlock"]:has(button:has(p:nth-of-type(5)))
    > div[data-testid="element-container"]
    > div[class*="ButtonContainer"] {
    height: 260px !important; max-height: 260px !important; overflow: hidden !important; padding: 0 !important; margin: 0 !important;
}
button[data-testid^="baseButton"]:has(p:nth-of-type(5)),
button[data-testid^="stBaseButton"]:has(p:nth-of-type(5)) {
    border-radius: 14px !important; padding: 16px 18px !important; width: 100% !important;
    height: 260px !important; min-height: 260px !important; max-height: 260px !important;
    display: flex !important; flex-direction: column !important; align-items: flex-start !important;
    justify-content: flex-start !important; text-align: left !important; white-space: normal !important;
    overflow: hidden !important; cursor: pointer !important; position: relative !important;
    transition: border-color 0.2s, background 0.2s, transform 0.18s, box-shadow 0.2s !important;
}
button[data-testid="baseButton-secondary"]:has(p:nth-of-type(5)) { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.1) !important; box-shadow: none !important; }
button[data-testid="baseButton-secondary"]:has(p:nth-of-type(5)):hover { background: rgba(255,255,255,0.07) !important; border-color: rgba(255,255,255,0.45) !important; transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important; }
button[data-testid="baseButton-primary"]:has(p:nth-of-type(5)),
button[data-testid="stBaseButton-primary"]:has(p:nth-of-type(5)) { background: rgba(255,255,255,0.04) !important; border: 1.5px solid #00ffcc !important; box-shadow: 0 0 12px rgba(0,255,204,0.18) !important; }
button[data-testid="baseButton-primary"]:has(p:nth-of-type(5)):hover,
button[data-testid="stBaseButton-primary"]:has(p:nth-of-type(5)):hover { transform: translateY(-2px) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.5), 0 0 12px rgba(0,255,204,0.4) !important; }

/* Song card typography */
button:has(p:nth-of-type(5)) p { margin: 0 !important; padding: 0 !important; width: 100% !important; }
button:has(p:nth-of-type(5)) p:nth-of-type(1) { font-size: 11px !important; font-weight: 700 !important; letter-spacing: 1.5px !important; color: rgba(255,255,255,0.45) !important; margin-bottom: 10px !important; line-height: 1 !important; }
button[data-testid="baseButton-primary"]:has(p:nth-of-type(5)) p:nth-of-type(1) { color: #00ffcc !important; }
button:has(p:nth-of-type(5)) p:nth-of-type(2) { font-size: 16px !important; font-weight: 700 !important; line-height: 1.3 !important; margin-bottom: 4px !important; }
button:has(p:nth-of-type(5)) p:nth-of-type(2) strong { color: #FFFFFF !important; }
button:has(p:nth-of-type(5)) p:nth-of-type(3) { font-size: 13px !important; color: rgba(255,255,255,0.56) !important; letter-spacing: 0.5px !important; margin-bottom: 12px !important; line-height: 1.3 !important; padding-bottom: 10px !important; border-bottom: 1px solid rgba(255,255,255,0.08) !important; }
button[data-testid="baseButton-primary"]:has(p:nth-of-type(5)) p:nth-of-type(3) { color: rgba(255,255,255,0.68) !important; border-bottom-color: rgba(0,255,204,0.18) !important; }
button:has(p:nth-of-type(5)) p:nth-of-type(4) { font-size: 13px !important; color: rgba(255,255,255,0.75) !important; line-height: 1.58 !important; margin-bottom: 4px !important; display: -webkit-box !important; -webkit-line-clamp: 2 !important; -webkit-box-orient: vertical !important; overflow: hidden !important; }
button:has(p:nth-of-type(5)) p:nth-of-type(5) { display: -webkit-box !important; -webkit-line-clamp: 2 !important; -webkit-box-orient: vertical !important; overflow: hidden !important; }
button:has(p:nth-of-type(5)) p:nth-of-type(5) em { font-size: 12px !important; font-style: normal !important; color: rgba(255,255,255,0.58) !important; line-height: 1.58 !important; }

/* Concept cards */
button[data-testid^="baseButton"]:has(p:nth-of-type(2)):not(:has(p:nth-of-type(3))),
button[data-testid^="stBaseButton"]:has(p:nth-of-type(2)):not(:has(p:nth-of-type(3))) {
    border-radius: 14px !important; padding: 18px 20px !important; width: 100% !important;
    min-height: 96px !important; height: auto !important; display: flex !important;
    flex-direction: column !important; align-items: flex-start !important; justify-content: center !important;
    text-align: left !important; white-space: normal !important; cursor: pointer !important; transition: all 0.2s ease !important;
}
button:has(p:nth-of-type(2)):not(:has(p:nth-of-type(3))) p:nth-of-type(1) { font-size: 14px !important; font-weight: 700 !important; color: #FFFFFF !important; margin-bottom: 6px !important; line-height: 1.2 !important; }
button:has(p:nth-of-type(2)):not(:has(p:nth-of-type(3))) p:nth-of-type(2) { font-size: 13px !important; color: rgba(255,255,255,0.58) !important; line-height: 1.5 !important; }
button[data-testid="baseButton-secondary"]:has(p:nth-of-type(2)):not(:has(p:nth-of-type(3))):hover { background: rgba(255,255,255,0.07) !important; border-color: rgba(255,255,255,0.45) !important; transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important; }
button[data-testid="baseButton-primary"]:has(p:nth-of-type(2)):not(:has(p:nth-of-type(3))):hover,
button[data-testid="stBaseButton-primary"]:has(p:nth-of-type(2)):not(:has(p:nth-of-type(3))):hover { transform: translateY(-2px) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.5), 0 0 12px rgba(0,255,204,0.4) !important; }

/* CSS variables & theme */
:root { --primary-color: #00ffcc !important; }
button:focus, button:focus-visible { outline: 2px solid rgba(0,255,204,0.50) !important; outline-offset: 2px !important; box-shadow: none !important; }

/* All buttons */
button[data-testid^="baseButton"], button[data-testid^="stBaseButton"] { cursor: pointer !important; }

/* Primary buttons */
button[data-testid="baseButton-primary"]:not(:has(p:nth-of-type(5))),
button[data-testid="stBaseButton-primary"]:not(:has(p:nth-of-type(5))) {
    background: linear-gradient(135deg, rgba(0,255,204,0.13) 0%, rgba(176,38,255,0.10) 100%) !important;
    border: 1px solid rgba(0,255,204,0.42) !important; color: #ccfff5 !important;
    font-weight: 600 !important; transition: all 0.25s ease !important;
}
button[data-testid="baseButton-primary"]:not(:has(p:nth-of-type(5))) p,
button[data-testid="stBaseButton-primary"]:not(:has(p:nth-of-type(5))) p { color: #ccfff5 !important; }
button[data-testid="baseButton-primary"]:not(:has(p:nth-of-type(5))):hover,
button[data-testid="stBaseButton-primary"]:not(:has(p:nth-of-type(5))):hover {
    background: linear-gradient(135deg, rgba(0,255,204,0.20) 0%, rgba(176,38,255,0.16) 100%) !important;
    border-color: rgba(0,255,204,0.65) !important; transform: translateY(-1px) !important;
    box-shadow: 0 0 22px rgba(0,255,204,0.16) !important;
}

/* Secondary buttons */
button[data-testid="baseButton-secondary"]:not(:has(p:nth-of-type(5))),
button[data-testid="stBaseButton-secondary"]:not(:has(p:nth-of-type(5))) {
    background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.10) !important;
    color: rgba(255,255,255,0.62) !important; transition: all 0.25s ease !important;
}
button[data-testid="baseButton-secondary"]:not(:has(p:nth-of-type(5))):hover,
button[data-testid="stBaseButton-secondary"]:not(:has(p:nth-of-type(5))):hover {
    background: rgba(255,255,255,0.07) !important; border-color: rgba(255,255,255,0.20) !important;
    color: rgba(255,255,255,0.88) !important; box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
}

/* Inputs */
[data-baseweb="input"] { background: rgba(255,255,255,0.04) !important; border-color: rgba(255,255,255,0.10) !important; border-radius: 10px !important; }
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within { border-color: rgba(0,255,204,0.52) !important; box-shadow: 0 0 0 2px rgba(0,255,204,0.10) !important; }

/* Misc */
hr { border-color: rgba(255,255,255,0.06) !important; }
a, a:visited { color: #00ffcc !important; }
[data-testid="stImage"] img { border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.10) !important; }
[data-testid="stFileUploaderDropzone"] { background: rgba(255,255,255,0.02) !important; border: 1.5px dashed rgba(255,255,255,0.12) !important; border-radius: 12px !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-thumb { background: rgba(0,255,204,0.38); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "step": 1,
    "song_data": [],
    "selected_song_ids": [],
    "concept_options": [],
    "selected_concept": None,
    "final_results": {},
    "n_songs": 10,
    "_api_key": "",
    "_api_key_verified": False,
    "_model": "",         # model name confirmed working for this key
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def next_step():
    st.session_state.step += 1


def go_to(n):
    st.session_state.step = n


def reset_pipeline():
    for k in ("song_data", "selected_song_ids", "concept_options"):
        st.session_state[k] = []
    st.session_state.selected_concept = None
    st.session_state.final_results = {}
    st.session_state.step = 1


# ─────────────────────────────────────────────────────────────────────────────
#  GEMINI — API KEY VERIFICATION
#  Strategy: try a curated list of current model names directly.
#  models.list() is NOT used because it fails silently for many key types.
# ─────────────────────────────────────────────────────────────────────────────

# Ordered by preference (newest flash first, then stable fallbacks)
_MODEL_CANDIDATES = [
    "gemini-2.5-flash-preview-04-17",
    "gemini-2.5-pro-exp-03-25",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
]


def _try_model(client, model_name: str) -> tuple[bool, str]:
    """Return (True, "") if successful, or (False, error_message)."""
    try:
        client.models.generate_content(
            model=model_name,
            contents="hi",
            config=genai_types.GenerateContentConfig(max_output_tokens=1),
        )
        return True, ""
    except Exception as e:
        return False, str(e)


def verify_api_key(key: str) -> tuple[bool, str]:
    """
    Verify an API key by trying each candidate model.
    Returns (ok, model_name) on success, or (False, error_message) on failure.
    """
    if not key or not key.strip():
        return False, "請輸入 API Key"
    key = key.strip()
    try:
        client = genai.Client(api_key=key)
    except Exception as e:
        return False, f"無法建立 Gemini 客戶端：{e}"

    last_error = ""
    for model in _MODEL_CANDIDATES:
        success, err_msg = _try_model(client, model)
        if success:
            return True, model   # 成功，回傳使用的 model 名稱
        else:
            last_error = err_msg  # 記錄錯誤訊息

    return False, (
        f"無法使用 Gemini API。\n"
        f"❌ 伺服器真正錯誤訊息：{last_error}\n\n"
        "可能原因：\n"
        "⊙ API Key 無效或已過期\n"
        "⊙ 地區 IP 限制（如果在香港執行，請確保 Terminal/IDE 有連上 VPN）"
    )


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR — API KEY INPUT & VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-family:Righteous,sans-serif;font-size:18px;"
        "color:#00ffcc;letter-spacing:1px;margin-bottom:12px;'>⚙️ 設定</div>",
        unsafe_allow_html=True,
    )

    # Check Streamlit Secrets first
    _secret_key = ""
    try:
        _secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass

    if _secret_key:
        # Auto-verify on first load
        if not st.session_state._api_key_verified:
            st.session_state._api_key = _secret_key
            with st.spinner("🔍 驗證 Secrets 金鑰中..."):
                _ok, _result = verify_api_key(_secret_key)
            if _ok:
                st.session_state._api_key_verified = True
                st.session_state._model = _result
                st.rerun()
            else:
                st.error(f"❌ Secrets 金鑰驗證失敗：\n{_result}")
        else:
            _short = st.session_state._model.replace("models/", "")
            st.markdown(
                f"<div style='font-size:12px;color:rgba(0,255,204,0.8);padding:10px 12px;"
                f"background:rgba(0,255,204,0.07);border:1px solid rgba(0,255,204,0.2);"
                f"border-radius:8px;'>✅ Secrets 金鑰已驗證<br>"
                f"<span style='color:rgba(255,255,255,0.50);font-size:11px;'>{_short}</span></div>",
                unsafe_allow_html=True,
            )
    else:
        # Manual input
        _typed = st.text_input(
            "🔑 Gemini API Key",
            value=st.session_state._api_key,
            type="password",
            placeholder="AIza...",
            help="前往 aistudio.google.com 免費取得",
        )
        # Reset verification if key changed
        if _typed != st.session_state._api_key:
            st.session_state._api_key = _typed
            st.session_state._api_key_verified = False
            st.session_state._model = ""

        if st.session_state._api_key_verified:
            _short = st.session_state._model.replace("models/", "")
            st.markdown(
                f"<div style='font-size:12px;color:rgba(0,255,204,0.8);padding:10px 12px;"
                f"background:rgba(0,255,204,0.07);border:1px solid rgba(0,255,204,0.2);"
                f"border-radius:8px;margin-top:6px;'>✅ 金鑰驗證通過<br>"
                f"<span style='color:rgba(255,255,255,0.50);font-size:11px;'>{_short}</span></div>",
                unsafe_allow_html=True,
            )
            if st.button("🔄 更換金鑰", use_container_width=True):
                st.session_state._api_key = ""
                st.session_state._api_key_verified = False
                st.session_state._model = ""
                st.rerun()

        elif st.session_state._api_key:
            if st.button("🔍 驗證金鑰", type="primary", use_container_width=True):
                with st.spinner("驗證中，請稍候..."):
                    _ok, _result = verify_api_key(st.session_state._api_key)
                if _ok:
                    st.session_state._api_key_verified = True
                    st.session_state._model = _result
                    st.rerun()
                else:
                    st.error(f"❌ 驗證失敗\n\n{_result}")
        else:
            st.markdown(
                "<div style='font-size:12px;color:rgba(255,180,0,0.8);padding:8px 10px;"
                "background:rgba(255,180,0,0.06);border:1px solid rgba(255,180,0,0.2);"
                "border-radius:8px;margin-top:6px;'>⚠️ 請輸入 API Key 並驗證</div>",
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown(
        "<div style='font-size:11px;color:rgba(255,255,255,0.56);line-height:1.7;'>"
        "使用 Google Gemini API。<br>"
        "Key 僅存於本次 session，<br>不會傳送至任何第三方。"
        "</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  API KEY GATE — block access until verified
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state._api_key_verified:
    st.markdown("""
    <div style='display:flex;flex-direction:column;align-items:center;
         justify-content:center;padding:80px 20px;text-align:center;'>
      <div style='margin-bottom:24px;color:#00ffcc;'>
      <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="m15.5 7.5 2.3 2.3a1 1 0 0 0 1.4 0l2.1-2.1a1 1 0 0 0 0-1.4L19 4"></path>
        <path d="m21 2-9.6 9.6"></path>
        <circle cx="7.5" cy="15.5" r="5.5"></circle>
      </svg>
    </div>
      <div style='font-family:Righteous,sans-serif;font-size:28px;
           background:linear-gradient(90deg,#00ffcc,#b026ff);
           -webkit-background-clip:text;-webkit-text-fill-color:transparent;
           margin-bottom:12px;'>Title Studio</div>
      <div style='font-size:14px;color:rgba(255,255,255,0.45);
           letter-spacing:1px;margin-bottom:32px;'>sLoth rAdio · Gemini AI</div>
      <div style='font-size:15px;color:rgba(255,255,255,0.6);
           background:rgba(255,255,255,0.04);
           border:1px solid rgba(255,255,255,0.08);
           border-radius:14px;padding:24px 32px;max-width:420px;line-height:2;'>
        請在左側側欄輸入<br>
        <span style='color:#00ffcc;font-weight:600;'>Gemini API Key</span>
        並按下「驗證金鑰」<br>
        驗證通過後即可使用 Title Studio。
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
#  GEMINI AI HELPERS  (only called after key is verified)
# ─────────────────────────────────────────────────────────────────────────────
def _gemini_client():
    return genai.Client(api_key=st.session_state._api_key)


def _call_json(prompt: str) -> dict | list | None:
    """Call Gemini and parse JSON response. Returns None on failure."""
    try:
        client = _gemini_client()
        resp = client.models.generate_content(
            model=st.session_state._model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.9,
                response_mime_type="application/json",
            ),
        )
        return json.loads(resp.text)
    except Exception as e:
        st.warning(f"⚠️ Gemini 呼叫失敗：{e}")
        return None


def ai_generate_songs(n: int) -> list[dict]:
    prompt = f"""You are a creative lofi music curator. Generate {n} unique lofi music track concepts.
Return a JSON array with exactly {n} objects. Each object must have:
- "en_title": evocative English title (2-5 words, poetic)
- "zh_title": poetic Traditional Chinese translation (3-6 characters)
- "en_theme": one vivid sensory English sentence (max 15 words) describing the mood/scene
- "zh_theme": poetic Traditional Chinese translation of en_theme

Aesthetics: cozy, introspective, lofi/chillhop everyday quiet moments.
Return ONLY a valid JSON array. No markdown, no explanation."""
    data = _call_json(prompt)
    if not isinstance(data, list) or len(data) < 1:
        return []
    result = []
    for i, item in enumerate(data[:n]):
        result.append({
            "id": i + 1,
            "en_title": str(item.get("en_title", f"Track {i+1}")),
            "zh_title": str(item.get("zh_title", f"曲目 {i+1}")),
            "en_theme": str(item.get("en_theme", "")),
            "zh_theme": str(item.get("zh_theme", "")),
        })
    return result


def ai_generate_concepts(sel_songs: list[dict], vibe: str) -> list[tuple[str, str]]:
    song_names = "、".join(s["zh_title"] for s in sel_songs[:6])
    prompt = f"""You are a creative director for a lofi music YouTube channel.
Songs: {song_names}
Vibe keywords: "{vibe or '無特定氛圍'}"

Generate exactly 3 distinct visual/story concept directions.
Return a JSON array of 3 objects with:
- "title": Traditional Chinese concept title with ONE leading emoji (max 10 chars total)
- "desc": one atmospheric Traditional Chinese sentence describing the scene (max 30 chars)

Make each concept different: vary time of day, setting, emotional angle.
Return ONLY a valid JSON array. No markdown, no explanation."""
    data = _call_json(prompt)
    if not isinstance(data, list) or len(data) < 3:
        return []
    return [
        (str(item.get("title", f"概念 {i+1}")), str(item.get("desc", "")))
        for i, item in enumerate(data[:3])
    ]


def ai_generate_assets(sel_songs: list[dict], concept: str) -> dict:
    song_list = "\n".join(
        f"- {s['en_title']} / {s['zh_title']}: {s['en_theme']}"
        for s in sel_songs
    )
    prompt = f"""You are a YouTube SEO copywriter for a lofi music channel called "sLoth rAdio".

Songs in this video:
{song_list}

Creative concept: {concept}

Return a single JSON object with these exact keys:
- "long_story": atmospheric English prose (4-6 paragraphs, 280-380 words), second-person "you", immersive slice-of-life
- "long_story_zh": Traditional Chinese translation of long_story, equally poetic
- "short_story": Instagram-caption English with emojis (3-4 short paragraphs, ~130 words)
- "short_story_zh": Traditional Chinese translation of short_story
- "titles": JSON array of 12 SEO-optimized YouTube titles in English. STRICT FORMAT for each: "{Catchy Short Name}… {Genre e.g. Chill Lofi/Cozy R&B/Soothing Jazz} for {Use-Case Keywords} {emoji} {emoji}". Example: "Cozy Tea Moments… Chill Lofi for Relaxation, Study & Calm ☕ 🌙". The short name must be 2-5 evocative words, the subtitle must include a genre keyword (Lofi/R&B/Jazz) plus 2-3 use-case words joined by commas or '&'. End with exactly 2 emojis.
- "titles_zh": JSON array of 12 matching Traditional Chinese YouTube titles in SAME format: "{中文短標題}… {類型} for {用途關鍵字} {emoji} {emoji}"
- "tags": comma-separated string of 35-45 YouTube SEO tags, mix broad and niche lofi keywords

Return ONLY a valid JSON object. No markdown, no explanation."""
    data = _call_json(prompt)
    if not isinstance(data, dict) or not data.get("long_story"):
        return {}
    for key in ("titles", "titles_zh"):
        if not isinstance(data.get(key), list):
            data[key] = []
    return data


# ─────────────────────────────────────────────────────────────────────────────
#  HTML HELPERS  (dashboard iframes)
# ─────────────────────────────────────────────────────────────────────────────
def _ae(t: str) -> str:
    return t.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&#39;').replace('<', '&lt;').replace('>', '&gt;')


def _he(t: str) -> str:
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')


_BASE_CSS = (
    "* { box-sizing: border-box; margin: 0; padding: 0; }"
    "html, body { background: transparent; font-family: 'Poppins', -apple-system, 'Segoe UI', sans-serif; overflow: hidden; }"
    ".lbl { font-size: 12px; font-weight: 600; color: #00ffcc; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }"
    ".card { background: rgba(10,10,20,0.7); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 18px 20px; }"
    ".copy-btn { background: rgba(0,255,204,0.08); border: 1px solid rgba(0,255,204,0.25); border-radius: 6px; color: #00ffcc; font-size: 12px; font-weight: 600; padding: 4px 12px; cursor: pointer; font-family: inherit; transition: background 0.2s; }"
    ".copy-btn:hover, .copy-btn.ok { background: rgba(0,255,204,0.2); border-color: rgba(0,255,204,0.5); cursor: pointer; }"
    ".trans-btn { background: rgba(176,38,255,0.1); border: 1px solid rgba(176,38,255,0.3); border-radius: 6px; color: #b026ff; font-size: 12px; font-weight: 600; padding: 4px 10px; cursor: pointer; font-family: inherit; transition: background 0.2s; margin-right: 6px; }"
    ".trans-btn:hover { background: rgba(176,38,255,0.22); border-color: rgba(176,38,255,0.55); cursor: pointer; }"
    ".content { color: rgba(255,255,255,0.75); font-size: 15px; line-height: 1.85; }"
    ".btn-row { display: flex; justify-content: flex-end; align-items: center; gap: 6px; margin-bottom: 12px; }"
    ".sec { margin-bottom: 20px; }"
    ".title-bullet { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }"
    ".title-bullet:last-child { border-bottom: none; }"
    ".bullet-dot { color: rgba(255,255,255,0.45); font-size: 18px; flex-shrink: 0; line-height: 1.4; }"
    ".ttxt-wrap { flex: 1; } .ttxt { font-size: 15px; font-weight: 600; color: rgba(255,255,255,0.92); line-height: 1.55; }"
    ".tag-pill { display: inline-block; background: rgba(0,255,204,0.08); border: 1px solid rgba(0,255,204,0.2); border-radius: 20px; padding: 3px 11px; margin: 3px; color: #00ffcc; font-size: 13px; font-weight: 500; }"
    ".song-row { display: flex; align-items: flex-start; gap: 12px; padding: 14px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }"
    ".song-row:last-child { border-bottom: none; }"
    ".sinfo { flex: 1; } .stitle { font-size: 15px; font-weight: 700; color: rgba(255,255,255,0.92); margin-bottom: 6px; line-height: 1.4; }"
    ".stheme-lbl { font-size: 11px; color: #00ffcc; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 4px; }"
    ".stheme-en { font-size: 13px; color: rgba(255,255,255,0.62); line-height: 1.55; margin-bottom: 3px; }"
    ".stheme-zh { font-size: 13px; color: rgba(255,255,255,0.50); line-height: 1.55; font-style: italic; }"
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
        f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap">'
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
    all_en = "\n".join(en for en, _ in pairs)
    all_zh = "\n".join(zh for _, zh in pairs)
    rows = "".join(
        f'<div class="title-bullet">'
        f'<span class="bullet-dot">&bull;</span>'
        f'<div class="ttxt-wrap">'
        f'<span class="en-block ttxt">{_he(en)}</span>'
        f'<span class="zh-block ttxt" style="display:none">{_he(zh)}</span>'
        f'</div>'
        f'<button class="copy-btn" style="flex-shrink:0;align-self:center;padding:3px 8px;font-size:11px;"'
        f' data-en="{_ae(en)}" data-zh="{_ae(zh)}" onclick="doCopyBi(this)">複製</button>'
        f'</div>'
        for en, zh in pairs
    )
    return (
        f'<div class="sec" data-lang="en">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
        f'<div class="lbl" style="margin:0;">🏆 High-Click Titles'
        f'&nbsp;<span style="color:rgba(255,255,255,0.50);font-size:12px;font-weight:400;letter-spacing:0;">'
        f'{len(pairs)} titles</span></div>'
        f'<div style="display:flex;gap:6px;">'
        f'<button class="trans-btn" onclick="toggleLang(this)">🌐 中文</button>'
        f'<button class="copy-btn" data-en="{_ae(all_en)}" data-zh="{_ae(all_zh)}" onclick="doCopyBi(this)">全部複製</button>'
        f'</div></div>'
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
        f'<div class="sec"><div class="lbl">🎵 Selected Songs'
        f'&nbsp;<span style="color:rgba(255,255,255,0.50);font-size:11px;font-weight:400;letter-spacing:0;">'
        f'{n} track{"s" if n != 1 else ""}</span></div>'
        f'<div class="card">{rows}</div></div>'
    )


def build_dashboard(songs, long_en, long_zh, short_en, short_zh, titles_en, titles_zh, tags) -> str:
    body = (
        _songs_sec(songs)
        + _story_sec("📖 Long Story", long_en, long_zh)
        + _story_sec("💬 Short Story", short_en, short_zh)
        + _titles_sec(titles_en, titles_zh)
        + _tags_sec(tags)
    )
    return _html_page(body)


# ─────────────────────────────────────────────────────────────────────────────
#  APP HEADER
# ─────────────────────────────────────────────────────────────────────────────
hcol1, hcol2 = st.columns([2, 1])
with hcol1:
    st.markdown(
        "<div class='app-title'>Title Studio</div>"
        "<div class='app-subtitle'>sLoth rAdio · Gemini AI</div>",
        unsafe_allow_html=True,
    )
with hcol2:
    if st.session_state.step > 1 or st.session_state.song_data:
        _ic1, _ic2 = st.columns([3, 1])
        with _ic1:
            st.markdown(
                "<div style='display:flex;align-items:center;height:100%;justify-content:flex-end;'>"
                "<span style='color:rgba(255,255,255,0.50);font-size:12px;letter-spacing:2px;text-transform:uppercase;'>"
                "AI · YouTube SEO Pipeline</span></div>",
                unsafe_allow_html=True,
            )
        with _ic2:
            if st.button("🔄 重置", key="hdr_reset", use_container_width=True):
                reset_pipeline()
                st.rerun()
    else:
        st.markdown(
            "<div style='display:flex;align-items:center;justify-content:flex-end;height:100%;'>"
            "<span style='color:rgba(255,255,255,0.50);font-size:12px;letter-spacing:2px;text-transform:uppercase;'>"
            "AI · YouTube SEO Pipeline</span></div>",
            unsafe_allow_html=True,
        )

# Stepper
step = st.session_state.step
_steps = ["🎵 選歌", "🎨 概念", "✍️ 素材", "📊 成果"]
_sh = "<div class='stepper'>"
for _i, _lbl in enumerate(_steps, 1):
    _st = "active" if _i == step else ("done" if _i < step else "")
    _sh += f"<div class='step-item'><div class='step-dot {_st}'>{'✓' if _i < step else _i}</div><span class='step-label {_st}'>{_lbl}</span></div>"
    if _i < len(_steps):
        _sh += f"<div class='step-connector {'done' if _i < step else ''}'></div>"
_sh += "</div>"
st.markdown(_sh, unsafe_allow_html=True)
st.divider()


# ─────────────────────────────────────────────────────────────────────────────
#  STAGE 1 — Music Ideation
# ─────────────────────────────────────────────────────────────────────────────
if step == 1:
    if not st.session_state.song_data:
        st.markdown(
            "<div class='section-heading'>🎵 Music Ideation</div>"
            "<div class='section-sub'>選擇數量 · 一鍵生成詩意歌名與意境</div>",
            unsafe_allow_html=True,
        )
        _, ctr, _ = st.columns([1, 2, 1])
        with ctr:
            st.markdown(
                "<div style='color:rgba(255,255,255,0.55);font-size:12px;letter-spacing:2px;"
                "text-transform:uppercase;margin-bottom:6px;'>🎚️ 生成數量</div>",
                unsafe_allow_html=True,
            )
            n = st.slider("n", min_value=1, max_value=20,
                          value=st.session_state.n_songs, step=1,
                          label_visibility="collapsed")
            st.session_state.n_songs = n
            if st.button(f"✨  生成 {n} 首歌曲", type="primary", use_container_width=True):
                with st.spinner("✨ AI 生成中..."):
                    songs = ai_generate_songs(n)
                if songs:
                    st.session_state.song_data = songs
                    st.rerun()

        st.write("")
        fc1, fc2, fc3 = st.columns(3)
        for _col, (_icon, _title, _desc) in zip(
            [fc1, fc2, fc3],
            [
                ("🎵", "AI 歌單生成", "一鍵產生詩意歌名與意境，快速建立創作素材庫"),
                ("🎨", "視覺概念提煉", "輸入氛圍關鍵字，AI 生成 3 個差異化故事方向"),
                ("📋", "完整 SEO 套件", "長文故事 · 短文貼文 · 高點擊標題 · Tags 全套輸出"),
            ],
        ):
            with _col:
                st.markdown(
                    f"<div style='background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);"
                    f"border-radius:14px;padding:22px 20px;text-align:center;'>"
                    f"<div style='font-size:28px;margin-bottom:10px;'>{_icon}</div>"
                    f"<div style='font-size:14px;font-weight:600;color:rgba(255,255,255,0.80);margin-bottom:6px;'>{_title}</div>"
                    f"<div style='font-size:13px;color:rgba(255,255,255,0.58);line-height:1.6;'>{_desc}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
    else:
        n_sel = len(st.session_state.selected_song_ids)
        st.markdown(
            "<div class='section-heading'>🎵 選擇歌曲</div>"
            "<div class='section-sub'>點選卡片 · 可多選 · 再按取消</div>",
            unsafe_allow_html=True,
        )
        songs = st.session_state.song_data
        NUM_COLS = min(4, len(songs))
        cols = st.columns(NUM_COLS, gap="small")
        for ci, col in enumerate(cols):
            with col:
                for song in songs[ci::NUM_COLS]:
                    is_sel = song["id"] in st.session_state.selected_song_ids
                    _num = f"{song['id']:02d}"
                    _check = "✓" if is_sel else _num
                    lbl = (
                        f"{_check}\n\n"
                        f"**{song['en_title']}**\n\n"
                        f"{song['zh_title']}\n\n"
                        f"{song['en_theme']}\n\n"
                        f"*— {song['zh_theme']}*"
                    )
                    if st.button(lbl, key=f"s{song['id']}",
                                 type="primary" if is_sel else "secondary",
                                 use_container_width=True):
                        if is_sel:
                            st.session_state.selected_song_ids.remove(
                                song["id"])
                        else:
                            st.session_state.selected_song_ids.append(
                                song["id"])
                        st.rerun()

        st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.07);margin-top:16px;'></div>",
                    unsafe_allow_html=True)
        tool_c0, tool_c1, tool_c2, _ = st.columns([2, 1, 1, 5])
        with tool_c0:
            st.markdown(
                f"<div style='display:flex;align-items:center;padding-top:6px;'>"
                f"<span style='font-size:13px;color:rgba(255,255,255,0.56);'>"
                f"<span style='font-size:20px;font-weight:800;color:#00ffcc;font-family:Righteous,sans-serif;'>{n_sel}</span>"
                f" / {len(songs)} ✓</span></div>",
                unsafe_allow_html=True,
            )
        with tool_c1:
            if st.button("✓ 全選", use_container_width=True):
                st.session_state.selected_song_ids = [s["id"] for s in songs]
                st.rerun()
        with tool_c2:
            if st.button("✕ 清除", use_container_width=True):
                st.session_state.selected_song_ids = []
                st.rerun()

        st.write("")
        nav_l, _, nav_r = st.columns([1, 4, 1])
        with nav_r:
            if st.button("🎨 概念方向 →", type="primary", use_container_width=True):
                if not st.session_state.selected_song_ids:
                    st.warning("⚠️ 請至少選一首歌。")
                else:
                    next_step()
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  STAGE 2 — Visual Concept
# ─────────────────────────────────────────────────────────────────────────────
elif step == 2:
    st.markdown(
        "<div class='section-heading'>🎨 概念方向</div>"
        "<div class='section-sub'>輸入氛圍關鍵字 · AI 生成 3 個故事方向</div>",
        unsafe_allow_html=True,
    )

    sel_songs = [s for s in st.session_state.song_data
                 if s["id"] in st.session_state.selected_song_ids]
    names = "、".join(s["zh_title"] for s in sel_songs[:5])
    if len(sel_songs) > 5:
        names += f" ⋯ +{len(sel_songs) - 5}"
    st.markdown(
        f"<div class='result-card'><div class='result-label'>🎵 已選歌曲</div>"
        f"<span style='color:rgba(255,255,255,0.7);font-size:15px;'>{names}</span></div>",
        unsafe_allow_html=True,
    )

    vibe = st.text_input("🌙 氛圍關鍵字（選填）", placeholder="凌晨的微雨 · 暖燈 · 黑膠唱片...")

    b1, b_space, b2 = st.columns([1, 4, 1])
    with b1:
        if st.button("← 返回", use_container_width=True):
            st.session_state.concept_options = []
            go_to(1)
            st.rerun()
    with b2:
        if st.button("🎲 生成方向", type="primary", use_container_width=True):
            with st.spinner("🎨 構思中..."):
                opts = ai_generate_concepts(sel_songs, vibe)
            if opts:
                st.session_state.concept_options = opts
                if st.session_state.selected_concept not in [o[0] for o in opts]:
                    st.session_state.selected_concept = None
                st.rerun()

    if st.session_state.concept_options:
        st.write("")
        st.markdown("<div class='result-label' style='margin-bottom:12px;'>🎯 選擇一個方向</div>",
                    unsafe_allow_html=True)
        ccols = st.columns(3, gap="small")
        for ci, (title, desc) in enumerate(st.session_state.concept_options):
            with ccols[ci]:
                is_sel = st.session_state.selected_concept == title
                if st.button(f"{title}\n\n{desc}", key=f"c{ci}",
                             type="primary" if is_sel else "secondary",
                             use_container_width=True):
                    st.session_state.selected_concept = title
                    st.rerun()

        if st.session_state.selected_concept:
            st.write("")
            _, _, n2 = st.columns([1, 4, 1])
            with n2:
                if st.button("✍️ 生成 SEO 素材 →", type="primary", use_container_width=True):
                    next_step()
                    st.rerun()
    else:
        st.markdown(
            "<div style='text-align:center;padding:40px 0 20px;'>"
            "<div style='font-size:36px;margin-bottom:12px;'>🎲</div>"
            "<div style='font-size:14px;letter-spacing:1px;color:rgba(255,255,255,0.45);'>"
            "按下「生成方向」讓 AI 構思故事視角</div></div>",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
#  STAGE 3 — SEO Assets
# ─────────────────────────────────────────────────────────────────────────────
elif step == 3:
    st.markdown(
        "<div class='section-heading'>✍️ SEO 素材</div>"
        "<div class='section-sub'>生成故事 · 標題 · Tags</div>",
        unsafe_allow_html=True,
    )

    sel_songs = [s for s in st.session_state.song_data
                 if s["id"] in st.session_state.selected_song_ids]
    concept = st.session_state.selected_concept or "—"
    preview = " · ".join(s["zh_title"] for s in sel_songs[:4])
    if len(sel_songs) > 4:
        preview += f" +{len(sel_songs) - 4}"

    st.markdown(
        f"<div class='result-card'><div class='result-label'>🎯 Creative Brief</div>"
        f"<p style='color:rgba(255,255,255,0.6);font-size:14px;margin:0 0 4px;'>"
        f"🎵 <span style='color:#fff;'>{len(sel_songs)} 首</span>"
        f"<span style='color:rgba(255,255,255,0.50);font-size:13px;margin-left:8px;'>{preview}</span></p>"
        f"<p style='color:rgba(255,255,255,0.6);font-size:14px;margin:0;'>"
        f"🎨 <span style='color:#00ffcc;'>{concept}</span></p></div>",
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "🖼️ 上傳縮圖（選填）", type=["png", "jpg", "jpeg", "webp"])
    if uploaded:
        st.image(Image.open(uploaded), use_container_width=True)

    st.write("")

    if not st.session_state.final_results:
        if st.button("🚀 生成所有素材", type="primary", use_container_width=True):
            with st.status("⚙️ AI 生成中...", expanded=True) as status:
                st.write("🤖 呼叫 Gemini，撰寫故事與 SEO 素材...")
                results = ai_generate_assets(sel_songs, concept)
                if results:
                    st.session_state.final_results = results
                    status.update(
                        label="✅ 完成！", state="complete", expanded=False)
                else:
                    status.update(label="❌ 生成失敗，請稍後再試。",
                                  state="error", expanded=False)
            if st.session_state.final_results:
                st.rerun()
    else:
        st.success("✅ 所有素材已就緒！")
        c1, c_space, c2 = st.columns([1, 4, 1])
        with c1:
            if st.button("← 返回", use_container_width=True):
                st.session_state.final_results = {}
                go_to(2)
                st.rerun()
        with c2:
            if st.button("📊 查看成果 →", type="primary", use_container_width=True):
                next_step()
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  STAGE 4 — Final Dashboard
# ─────────────────────────────────────────────────────────────────────────────
elif step == 4:
    st.markdown(
        "<div class='section-heading'>📊 成果總覽</div>"
        "<div class='section-sub'>複製 → YouTube Studio 🎬</div>",
        unsafe_allow_html=True,
    )

    r = st.session_state.final_results
    sel_songs = [s for s in st.session_state.song_data
                 if s["id"] in st.session_state.selected_song_ids]

    st.iframe(
        build_dashboard(
            sel_songs,
            r.get("long_story", ""),
            r.get("long_story_zh", ""),
            r.get("short_story", ""),
            r.get("short_story_zh", ""),
            r.get("titles", []),
            r.get("titles_zh", []),
            r.get("tags", ""),
        ),
        height="content",
    )

    st.divider()
    s4c1, s4space, s4c2 = st.columns([1, 4, 1])
    with s4c1:
        if st.button("← 返回", use_container_width=True):
            go_to(3)
            st.rerun()
    with s4c2:
        if st.button("🔄 重新開始", use_container_width=True):
            reset_pipeline()
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.write("")
st.markdown(
    "<div style='text-align:center;color:rgba(255,255,255,0.56);font-size:11px;"
    "letter-spacing:1px;margin-top:48px;'>sLoth rAdio · YouTube Title Studio · Powered by Gemini</div>",
    unsafe_allow_html=True,
)
