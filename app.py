"""
sLoth rAdio · Title Studio — Dynamic Wizard Mode
Google Gemini AI-powered YouTube title, tag & SEO asset generator.
Falls back to mock data when no API key is configured.

UI Language: Traditional Chinese
Design: OLED Dark + Neon Teal (#00ffcc / #b026ff)
"""

import json
import time
import traceback
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

from history import load_history, save_generation, delete_history_item, build_dedup_prompt

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="sLoth rAdio · Title Studio",
    page_icon="🎵",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
#  GOOGLE OAUTH  ── login / guest mode
#  自訂實作：修正 streamlit-google-auth PKCE code_verifier 遺失問題
# ─────────────────────────────────────────────────────────────────────────────

import json
import os
import tempfile
import time


class _SlothAuth:
    """輕量 Google OAuth wrapper，將 code_verifier 保存在 temp 檔案以修正 PKCE。
    session_state 在瀏覽器跳轉 Google 後會遺失，改用 state→file 映射。"""

    _PKCE_PREFIX = "sloth_pkce_"

    def __init__(self, cred_path: str, redirect_uri: str):
        self._cred_path = cred_path
        self._redirect_uri = redirect_uri
        st.session_state.setdefault("connected", False)
        st.session_state.setdefault("user_info", {})

    def _make_flow(self):
        import google_auth_oauthlib.flow
        return google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            self._cred_path,
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
            ],
            redirect_uri=self._redirect_uri,
        )

    def _verifier_path(self, state: str) -> str:
        """回傳以 OAuth state 為 key 的 temp 檔案路徑。"""
        import hashlib
        safe = hashlib.sha256(state.encode()).hexdigest()[:32]
        return os.path.join(tempfile.gettempdir(), f"{self._PKCE_PREFIX}{safe}")

    def check_authentification(self):
        if st.session_state["connected"]:
            return
        auth_code = st.query_params.get("code")
        state = st.query_params.get("state")
        if auth_code:
            st.query_params.clear()
            try:
                flow = self._make_flow()
                # 從 temp 檔案取回 PKCE code_verifier（以 state 為 key）
                if state:
                    vp = self._verifier_path(state)
                    if os.path.exists(vp):
                        with open(vp, "r") as f:
                            flow.code_verifier = f.read().strip()
                        os.remove(vp)
                flow.fetch_token(code=auth_code)
                from googleapiclient.discovery import build
                svc = build("oauth2", "v2", credentials=flow.credentials)
                user_info = svc.userinfo().get().execute()
                st.session_state["connected"] = True
                st.session_state["oauth_id"] = user_info.get("id")
                st.session_state["user_info"] = user_info
                st.rerun()
            except Exception as e:
                import logging
                logging.warning(f"OAuth token 交換失敗（略過）: {e}")

    def login(self, color="blue", justify_content="center"):
        if st.session_state["connected"]:
            return
        flow = self._make_flow()
        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
        )
        # 將 PKCE code_verifier 寫入 temp 檔案（以 state 為 key）
        if hasattr(flow, "code_verifier") and flow.code_verifier and state:
            vp = self._verifier_path(state)
            with open(vp, "w") as f:
                f.write(flow.code_verifier)
        bg = "#fff" if color == "white" else "#4285f4"
        fg = "#000" if color == "white" else "#fff"
        st.markdown(
            f'<div style="display:flex;justify-content:{justify_content};">'
            f'<a href="{auth_url}" target="_self" style="background:{bg};color:{fg};'
            f'text-decoration:none;text-align:center;font-size:16px;margin:4px 2px;'
            f'cursor:pointer;padding:8px 12px;border-radius:4px;display:flex;align-items:center;">'
            f'<img src="https://lh3.googleusercontent.com/COxitqgJr1sJnIDe8-jiKhxDx1FrYbtRHKJ9z_hELisAlapwE9LUPh6fcXIfb5vwpbMl4xl9H9TRFPc5NOO8Sb3VSgIBrfRYvW6cUA" '
            f'alt="Google" style="margin-right:8px;width:26px;height:26px;background:#fff;border:2px solid #fff;border-radius:4px;">'
            f'Sign in with Google</a></div>',
            unsafe_allow_html=True,
        )


_AUTH_OBJ = None  # global ref for login button rendering


def _init_auth():
    """Initialise Google OAuth. Returns (logged_in, email, name, photo_url).
    Falls back to guest mode when secrets are missing or auth fails."""
    global _AUTH_OBJ
    try:
        _client_id = st.secrets["google_oauth"]["client_id"]
        _client_secret = st.secrets["google_oauth"]["client_secret"]
        _redirect_uri = st.secrets["google_oauth"].get(
            "redirect_uri", "http://localhost:8501")

        _cred_path = os.path.join(tempfile.gettempdir(), "sloth_oauth_creds.json")
        _cred_data = {
            "web": {
                "client_id": _client_id,
                "client_secret": _client_secret,
                "redirect_uris": [_redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        with open(_cred_path, "w") as f:
            json.dump(_cred_data, f)

        auth = _SlothAuth(cred_path=_cred_path, redirect_uri=_redirect_uri)
        auth.check_authentification()
        _AUTH_OBJ = auth
        return (
            st.session_state.get("connected", False),
            st.session_state.get("user_info", {}).get("email"),
            st.session_state.get("user_info", {}).get("name"),
            st.session_state.get("user_info", {}).get("picture"),
        )
    except (KeyError, FileNotFoundError):
        return False, None, None, None
    except Exception as e:
        import logging
        logging.warning(f"OAuth 初始化失敗: {e}")
        return False, None, None, None


_LOGGED_IN, _USER_EMAIL, _USER_NAME, _USER_PHOTO = _init_auth()
_IS_GUEST = not _LOGGED_IN

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
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MODEL CANDIDATES  ── preference order
# ─────────────────────────────────────────────────────────────────────────────
_MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
]


# ─────────────────────────────────────────────────────────────────────────────
#  MOCK DATA  ── realistic lofi-themed content for demo fallback
# ─────────────────────────────────────────────────────────────────────────────
_MOCK_TITLES_EN = [
    "Cozy Tea Moments… Chill Lofi for Relaxation, Study & Calm 🍵 🌙",
    "Find Your Calm… Soothing R&B for Work, Rest & Healing 🌸 ☕",
    "Slow Morning Chores… Chill R&B for Study, Work & Gentle Focus 🧰 🧰",
    "Peace in the Garden… Chill R&B for Study, Work & Soft Focus ⏳ 🫖",
    "Rest in the Morning Light… Chill R&B for Yoga & Peaceful Moments 🧘 🌞",
]
_MOCK_TITLES_ZH = [
    "溫馨茶時光… 放鬆、讀書＆平靜的 Chill Lofi 🍵 🌙",
    "找到你的安寧… 工作、休憩＆療癒的舒緩 R&B 🌸 ☕",
    "慢活早晨家務… 讀書、工作＆溫柔專注的 Chill R&B 🧰 🧰",
    "花園裡的寧靜… 讀書、工作＆柔和專注的 Chill R&B ⏳ 🫖",
    "晨光中的休憩… 瑜伽＆平靜時刻的 Chill R&B 🧘 🌞",
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
    "The barista glances at the clock but never hurries. "
    "A stack of old paperbacks sits on the shelf by the door — they belong to no one and everyone.\n\n"
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
    "Making Tea 🍵\n"
    "Evening settles outside the window 🌙. You fill the kettle and set it on the stove, "
    "then choose your favorite cup—the one with the crack in the glaze you never bothered to replace.\n\n"
    "The kettle hums low. When it whistles, you pour. Steam rises, fogging the window above the sink 💨. "
    "You watch the water darken, then wrap your hands around the warm cup, letting the heat seep through ☕.\n\n"
    "When you finally take a slow sip, you carry the cup to the living room and sink into the couch 🛋️. "
    "The last light has gone. Only the warmth in your hands and the slow, easy quiet of the evening 🌿."
)
_MOCK_SHORT_STORY_ZH = (
    "泡一杯茶 🍵\n"
    "夜色在窗外慢慢沉澱 🌙。你把水壺裝滿放上爐子，"
    "然後挑了你最愛的那只杯子——釉面上有道裂痕，你從沒想過要換掉它。\n\n"
    "水壺發出低沉的嗡鳴。壺嘴一響，你傾倒熱水。蒸氣升起，在水槽上方的窗玻璃上凝成一層薄霧 💨。"
    "你看著茶湯漸漸變深，然後雙手捧住溫熱的杯身，讓暖意慢慢滲透 ☕。\n\n"
    "當你終於小啜一口，便端著杯子走進客廳，陷入沙發裡 🛋️。"
    "最後的光已經散去。只剩手中的溫暖，和這個夜晚緩慢而安靜的呼吸 🌿。"
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
    "existing_materials": [],    # 已有嘅材料（同樣 5 類 + images）
    "user_context": "",          # Step 3 用戶輸入
    "n_songs": 15,               # 歌單數量
    "results": {},               # AI / mock 結果
    "uploaded_images": [],       # Step 3 上傳嘅圖片 (UploadedFile objects)
    "view_mode": "wizard",       # "wizard" | "history"
    "api_key": "",               # API key
    "api_status": "disconnected",  # "disconnected" | "validating" | "connected"
    "api_model": "",             # 模型名稱
    "prompt_tone": 50,           # 語氣 slider 0-100
    "prompt_styles": [],         # 風格 chips
    "prompt_audience": "",       # 目標受眾
    "prompt_extra": "",          # 額外指示
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_pipeline():
    _preserve = {"api_key", "api_status", "api_model"}
    for k, v in _DEFAULTS.items():
        if k in _preserve:
            continue
        st.session_state[k] = v if not isinstance(
            v, (list, dict)) else type(v)()


# ─────────────────────────────────────────────────────────────────────────────
#  GEMINI API  ── real AI generation
# ─────────────────────────────────────────────────────────────────────────────
def _get_client() -> genai.Client | None:
    """Return a configured genai Client, or None if no key."""
    key = st.session_state.api_key
    if not key:
        return None
    return genai.Client(api_key=key)


def _validate_api_key(key: str) -> tuple[bool, str]:
    """Validate API key and find best available model. Returns (ok, model_name)."""
    if not key:
        return False, ""
    try:
        client = genai.Client(api_key=key)
        available = set()
        for m in client.models.list():
            available.add(m.name.split("/")[-1] if "/" in m.name else m.name)
        for candidate in _MODEL_CANDIDATES:
            if candidate in available:
                return True, candidate
        # If none of the candidates match, use the first available generative model
        for m_name in available:
            if "gemini" in m_name:
                return True, m_name
        return False, ""
    except Exception:
        return False, ""


def _call_json(prompt: str, image_parts: list | None = None) -> dict | list:
    """Call Gemini with JSON response mode. Returns parsed JSON."""
    client = _get_client()
    if not client:
        raise RuntimeError("API key 未設定")
    model = st.session_state.api_model
    contents = []
    if image_parts:
        for img_bytes, mime in image_parts:
            contents.append(types.Part.from_bytes(
                data=img_bytes, mime_type=mime))
    contents.append(prompt)
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.9,
        ),
    )
    return json.loads(response.text)


def _build_tone_style_block() -> str:
    """Build prompt fragment from tone/style/audience/extra settings."""
    parts = []
    tone_map = {0: "溫暖柔和", 25: "寧靜治癒", 50: "平衡自然", 75: "明亮活潑", 100: "活潑有力"}
    tone = tone_map.get(st.session_state.prompt_tone, "平衡自然")
    parts.append(f"語氣風格：{tone}")
    if st.session_state.prompt_styles:
        parts.append(f"創作風格：{', '.join(st.session_state.prompt_styles)}")
    if st.session_state.prompt_audience and st.session_state.prompt_audience != "不指定":
        parts.append(f"目標受眾：{st.session_state.prompt_audience}")
    if st.session_state.prompt_extra:
        parts.append(f"額外指示：{st.session_state.prompt_extra}")
    return "\n".join(parts)


def _prepare_images() -> list | None:
    """Prepare uploaded images as (bytes, mime_type) tuples for API."""
    imgs = st.session_state.get("uploaded_images", [])
    if not imgs:
        return None
    parts = []
    for f in imgs[:5]:  # 最多 5 張
        data = f.getvalue()
        mime = f.type or "image/jpeg"
        parts.append((data, mime))
    return parts


def ai_generate_tracklist(n: int, context: str, user_email: str | None = None) -> list:
    """Generate tracklist via Gemini."""
    style_block = _build_tone_style_block()
    dedup_block = build_dedup_prompt(user_email)
    prompt = f"""You are a lofi music curator creating a tracklist for a YouTube lofi playlist.

Generate {n} lofi track concepts. Style: cozy, introspective, lofi/chillhop, quiet everyday moments.

{f"User's creative context: {context}" if context else ""}
{style_block}
{dedup_block}

Return a JSON array of exactly {n} objects. Each object must have:
- "en_title": English title, 2-5 words, poetic
- "zh_title": Traditional Chinese title, 3-6 characters
- "en_theme": English theme sentence, ≤15 words
- "zh_theme": Traditional Chinese theme sentence

Return ONLY the JSON array, no wrapping object."""

    image_parts = _prepare_images()
    data = _call_json(prompt, image_parts)
    if isinstance(data, dict) and "tracklist" in data:
        data = data["tracklist"]
    for i, item in enumerate(data, 1):
        item["id"] = i
    return data[:n]


def ai_generate_assets(selected_outputs: list, context: str, tracklist: list | None, user_email: str | None = None) -> dict:
    """Generate titles, tags, stories via a single Gemini call."""
    style_block = _build_tone_style_block()
    dedup_block = build_dedup_prompt(user_email)

    tracklist_text = ""
    if tracklist:
        lines = []
        for s in tracklist:
            lines.append(
                f"  - 《{s.get('en_title', '')}》({s.get('zh_title', '')}): {s.get('en_theme', '')}")
        tracklist_text = "Tracklist for reference:\n" + "\n".join(lines)

    # 構建需要生成的項目描述
    output_specs = []
    if "titles" in selected_outputs:
        output_specs.append("""- "titles": array of 5 English YouTube titles, ranked by predicted CTR (high→low).
  Each title MUST follow this exact format: "{Catchy Name 2-5 words}… {Genre with Lofi/R&B/Jazz keyword} for {Use Case 2-3 words} {emoji} {emoji}"
  IMPORTANT: Vary the genre keyword across titles (mix Lofi, R&B, Jazz — don't repeat the same one).
  Vary the use cases (Study, Work, Relaxation, Yoga, Healing, Focus, etc.) and moods (Cozy, Peaceful, Slow, Warm, etc.).
  Use diverse, evocative emoji pairs — avoid repeating the same pair.
  Examples of good diversity:
  - "Cozy Tea Moments… Chill Lofi for Relaxation, Study & Calm 🍵 🌙"
  - "Find Peace in Small Tasks… Chill Lofi for Relaxation & Unwinding 🧼 🌿"
  - "Find Your Calm… Soothing R&B for Work, Rest & Healing 🌸 ☕"
  - "Slow Morning Chores… Chill R&B for Study, Work & Gentle Focus 🧰 🧰"
  - "Rest in the Morning Light… Chill R&B for Yoga & Peaceful Moments 🧘 🌞"
- "titles_zh": array of 5 Traditional Chinese titles, 1:1 corresponding to the English titles.""")
    if "tags" in selected_outputs:
        output_specs.append("""- "tags": a single comma-separated string of 35-45 YouTube SEO tags.
  Mix broad keywords (e.g. lofi, chill music) with niche keywords (e.g. cozy rainy night lofi).
  Total character count should be 450-500.""")
    if "long_story" in selected_outputs:
        output_specs.append("""- "long_story": English prose, 3-5 paragraphs. Second person "you". Immersive slice-of-life style.
  Total length MUST be around 1000 characters (not words). Paragraphs separated by \\n\\n.
- "long_story_zh": Traditional Chinese translation with equal poetic quality. Also ~1000 characters total.""")
    if "short_story" in selected_outputs:
        output_specs.append("""- "short_story": English short prose, 200-600 characters total. Format:
  Line 1: A short evocative title followed by one emoji (e.g. "Making Tea 🍵")
  Then 2-3 paragraphs in second person "you", present tense, with sensory details.
  Place emojis at the END of sentences (not inline). Paragraphs separated by \\n\\n.
  Example:
  "Making Tea 🍵\nEvening settles outside the window 🌙. You fill the kettle and set it on the stove...\n\nYou don't drink yet. You just stand there, holding it..."
- "short_story_zh": Traditional Chinese translation in the same format. Also 200-600 characters total.""")

    specs_text = "\n".join(output_specs)

    prompt = f"""You are a YouTube SEO copywriter specializing in lofi/chill music channels.

{f"User's creative context: {context}" if context else "No specific context provided — create a cozy lofi theme."}
{tracklist_text}
{style_block}
{dedup_block}

Generate the following as a single JSON object:
{specs_text}

Return ONLY the JSON object."""

    image_parts = _prepare_images()
    return _call_json(prompt, image_parts)


def ai_generate(selected_outputs: list, n_songs: int, context: str, user_email: str | None = None) -> dict:
    """Full AI generation pipeline."""
    result = {}

    # Step 1: 生成歌單（如果需要）
    if "tracklist" in selected_outputs:
        tracklist = ai_generate_tracklist(n_songs, context, user_email)
        result["tracklist"] = tracklist
    else:
        tracklist = None

    # Step 2: 生成其他素材（標題、標籤、故事）
    asset_outputs = [k for k in selected_outputs if k != "tracklist"]
    if asset_outputs:
        assets = ai_generate_assets(
            asset_outputs, context, tracklist or result.get("tracklist"), user_email)
        result.update(assets)

    return result


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
    "images": "圖片",
}


_api_st = st.session_state.api_status
_api_dot = "on" if _api_st == "connected" else (
    "wait" if _api_st == "validating" else "off")
_api_txt = (
    f"Gemini · {st.session_state.api_model}" if _api_st == "connected"
    else ("驗證中..." if _api_st == "validating" else "未連接")
)
_hist_count = len(load_history(_USER_EMAIL)) if _USER_EMAIL else 0

# ═════════════════════════════════════════════════════════════════════════
#  NAVBAR ─ single-row: brand | buttons | user/status
# ═════════════════════════════════════════════════════════════════════════
with st.container(key="navbar"):
    _c_brand, _c_sep, _c_key, _c_hist, _c_set, _c_reset, _c_space, _c_user, _c_status = st.columns(
        [1.8, 0.12, 0.5, 0.5, 0.5, 0.5, 3, 1.2, 1.6], vertical_alignment="center"
    )
    # ── 品牌標題 ──
    with _c_brand:
        st.markdown(
            "<span class='nb-brand'>Title Studio</span>"
            "<span class='nb-sub'>sLoth rAdio</span>",
            unsafe_allow_html=True,
        )
    # ── 分隔線 ──
    with _c_sep:
        st.markdown("<div class='nav-sep'></div>", unsafe_allow_html=True)
    # ── 🔑 API Key ──
    with _c_key:
        _api_pop = st.popover("🔑", use_container_width=True, help="API Key 設定")
        with _api_pop:
            st.markdown("##### 🔑 API Key 設定")
            _new_key = st.text_input(
                "api_key_input", value=st.session_state.api_key,
                type="password", placeholder="輸入 Google Gemini API Key...",
                label_visibility="collapsed",
            )
            if _new_key != st.session_state.api_key:
                st.session_state.api_key = _new_key
                if _new_key:
                    st.session_state.api_status = "validating"
                    ok, model = _validate_api_key(_new_key)
                    if ok:
                        st.session_state.api_status = "connected"
                        st.session_state.api_model = model
                    else:
                        st.session_state.api_status = "disconnected"
                        st.session_state.api_model = ""
                else:
                    st.session_state.api_status = "disconnected"
                    st.session_state.api_model = ""
                st.rerun()
            if st.session_state.api_status == "connected":
                st.caption(f"✅ 已連接 · 模型：{st.session_state.api_model}")
            elif st.session_state.api_status == "disconnected" and st.session_state.api_key:
                st.caption("❌ API Key 無效或無可用模型")
            else:
                st.caption("💡 輸入 API Key 啟用 Gemini AI。未連接時使用模擬資料。")
    # ── 📋 歷史 ──
    with _c_hist:
        if st.button("📋", key="nb_hist_btn", use_container_width=True, help=f"歷史記錄 ({_hist_count})"):
            st.session_state.view_mode = "history" if st.session_state.view_mode != "history" else "wizard"
            st.rerun()
    # ── ⚙️ 設定 ──
    with _c_set:
        _settings_pop = st.popover("⚙️", use_container_width=True, help="設定")
        with _settings_pop:
            st.markdown("##### ⚙️ 設定")
            st.markdown("**模型偏好**")
            st.selectbox(
                "model_pref", options=["Gemini 2.5 Flash (推薦)", "Gemini 2.5 Pro", "Gemini 2.0 Flash"],
                index=0, label_visibility="collapsed", key="model_select",
            )
            st.markdown("**介面語言**")
            st.selectbox(
                "lang_pref", options=["繁體中文", "English"],
                index=0, label_visibility="collapsed", key="lang_select",
            )
            st.caption("設定會在下次生成時生效。")
    # ── 🔄 重置 ──
    with _c_reset:
        if st.button("🔄", key="nb_reset_btn", use_container_width=True, help="重置所有步驟"):
            reset_pipeline()
            st.rerun()
    # ── 👤 用戶 ──
    with _c_user:
        if _LOGGED_IN:
            _user_pop = st.popover(
                f"👤", use_container_width=True, help=_USER_NAME or _USER_EMAIL)
            with _user_pop:
                _display = _USER_NAME or _USER_EMAIL or "用戶"
                st.markdown(f"##### 👋 {_display}")
                st.caption(f"📧 {_USER_EMAIL}")
                st.caption(f"📋 共 {_hist_count} 筆歷史記錄")
                if st.button("🚪 登出", key="nb_logout", use_container_width=True):
                    st.session_state["connected"] = False
                    st.session_state["user_info"] = {}
                    st.rerun()
        else:
            _login_pop = st.popover("🔒", use_container_width=True, help="登入")
            with _login_pop:
                st.markdown("##### 🔒 登入")
                st.caption("使用 Google 帳號登入以儲存歷史記錄，跨裝置同步。")
                if _AUTH_OBJ is not None:
                    _AUTH_OBJ.login(color="blue", justify_content="center")
                else:
                    st.caption("未設定 OAuth → 功能暫不可用。")
    # ── 狀態指示器（右側） ──
    with _c_status:
        st.markdown(
            f"<div class='api-status-wrap'><div class='api-status'><span class='api-dot {_api_dot}'></span><span class='api-lbl'>{_api_txt}</span></div></div>",
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
#  HISTORY VIEW
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.view_mode == "history":
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sec-title'>📋 歷史記錄</div>"
        "<div class='sec-desc'>點擊任意記錄可查看完整結果</div>",
        unsafe_allow_html=True,
    )

    if _IS_GUEST:
        st.markdown(
            "<div style='text-align:center;padding:40px 0;color:rgba(255,255,255,0.55);font-size:14px;'>"
            "🔒 請先登入 Google 帳號以查看歷史記錄<br>"
            "<span style='font-size:12px;'>登入後，生成記錄會自動保存並可跨裝置同步</span></div>",
            unsafe_allow_html=True,
        )
    else:
        _history = load_history(_USER_EMAIL)
        if not _history:
            st.markdown(
                "<div style='text-align:center;padding:40px 0;color:rgba(255,255,255,0.55);font-size:14px;'>"
                "尚無歷史記錄<br><span style='font-size:12px;'>完成一次生成後會自動保存</span></div>",
                unsafe_allow_html=True,
            )
        else:
            for hi, entry in enumerate(_history):
                _ts = entry.get("timestamp", "")
                _types = " ".join(
                    f"<span class='chip chip-teal'>{_MATERIAL_LABELS.get(k, k)}</span>"
                    for k in entry.get("selected_outputs", [])
                )
                _preview = entry.get("user_context", "")[:80]
                if len(entry.get("user_context", "")) > 80:
                    _preview += "..."
                _no_input = '<em style="color:rgba(255,255,255,0.50);">無輸入文字</em>'
                _summary_html = _he(_preview) if _preview else _no_input
                _mode = entry.get("mode", "demo")
                _mode_badge = (
                    "<span style='font-size:10px;color:#00ffcc;font-weight:600;margin-left:8px;'>AI</span>"
                    if _mode == "ai" else
                    "<span style='font-size:10px;color:rgba(255,180,0,0.85);font-weight:600;margin-left:8px;'>Demo</span>"
                )
                st.markdown(
                    f"<div class='hist-card'>"
                    f"<div class='hist-time'>{_he(_ts)}{_mode_badge}</div>"
                    f"<div style='margin:6px 0;'>{_types}</div>"
                    f"<div class='hist-summary'>{_summary_html}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                _hcol1, _hcol2 = st.columns([3, 1])
                with _hcol1:
                    if st.button("📊 查看結果", key=f"hist_view_{hi}", use_container_width=True):
                        st.session_state.results = entry.get("results", {})
                        st.session_state.selected_outputs = entry.get(
                            "selected_outputs", [])
                        st.session_state.user_context = entry.get(
                            "user_context", "")
                        st.session_state.existing_materials = entry.get(
                            "existing_materials", [])
                        st.session_state.n_songs = entry.get("n_songs", 15)
                        st.session_state.step = 4
                        st.session_state.view_mode = "wizard"
                        st.rerun()
                with _hcol2:
                    _entry_id = entry.get("id", "")
                    if _entry_id and st.button("🗑️", key=f"hist_del_{hi}", use_container_width=True, help="刪除此記錄"):
                        delete_history_item(_USER_EMAIL, _entry_id)
                        st.rerun()

    st.markdown("<div class='nav-spacer'></div>", unsafe_allow_html=True)
    if st.button("← 返回精靈", key="hist_back", use_container_width=True):
        st.session_state.view_mode = "wizard"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer'>sLoth rAdio · Title Studio</div>",
                unsafe_allow_html=True)
    st.stop()


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
        f"<div class='info-card'><span style='font-size:12px;color:rgba(255,255,255,0.55);'>你要生成：</span><br>{gen_chips}</div>",
        unsafe_allow_html=True,
    )

    # Filter out items the user wants to generate + always include images
    available = [(k, ic, nm, ds) for k, ic, nm,
                 ds in _OPTIONS if k not in st.session_state.selected_outputs]
    # Append image as a material option (always available)
    available.append(("images", "🖼️", "圖片", "上傳參考圖讓 AI 理解視覺風格"))

    cols = st.columns(len(available), gap="medium")
    for ci, (key, icon, name, _) in enumerate(available):
        with cols[ci]:
            is_sel = key in st.session_state.existing_materials
            if st.button(f"{icon}\n\n**已有{name}**", key=f"mat_{key}",
                         type="primary" if is_sel else "secondary", use_container_width=True):
                if is_sel:
                    st.session_state.existing_materials.remove(key)
                    if key == "images":
                        st.session_state.uploaded_images = []
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

    summary = f"<div class='info-card'><div style='margin-bottom:8px;'><span style='font-size:12px;color:rgba(255,255,255,0.55);'>要生成：</span> {gen_chips}</div>"
    if mat_chips:
        summary += f"<div><span style='font-size:12px;color:rgba(255,255,255,0.55);'>已有材料：</span> {mat_chips}</div>"
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

    # Image uploader (when user selected "已有圖片")
    if "images" in st.session_state.existing_materials:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.55);font-size:11px;letter-spacing:2px;"
            "text-transform:uppercase;margin:14px 0 4px;'>🖼️ 上傳參考圖片</div>",
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader(
            "upload_images",
            type=["png", "jpg", "jpeg", "webp", "gif"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded:
            st.session_state.uploaded_images = uploaded
            # Preview thumbnails
            thumb_cols = st.columns(min(len(uploaded), 5))
            for ti, f in enumerate(uploaded[:5]):
                with thumb_cols[ti]:
                    st.image(f, use_container_width=True, caption=f.name)
            if len(uploaded) > 5:
                st.caption(f"...及另外 {len(uploaded) - 5} 張圖片")

    # Song count slider
    if "tracklist" in st.session_state.selected_outputs:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.55);font-size:11px;letter-spacing:2px;"
            "text-transform:uppercase;margin:14px 0 4px;'>🎚️ 歌單數量</div>",
            unsafe_allow_html=True,
        )
        st.session_state.n_songs = st.slider(
            "n_songs", min_value=1, max_value=20,
            value=st.session_state.n_songs, step=1,
            label_visibility="collapsed",
        )

    # ── Prompt 微調器 ──
    with st.expander("🎛️ 進階設定", expanded=False):
        st.markdown("<div class='tuner-label'>🎤 語氣</div>",
                    unsafe_allow_html=True)
        _tone_labels = {0: "溫暖柔和", 25: "寧靜治癒",
                        50: "平衡自然", 75: "明亮活潑", 100: "活潑有力"}
        st.session_state.prompt_tone = st.slider(
            "tone", min_value=0, max_value=100,
            value=st.session_state.prompt_tone, step=25,
            format="%d%%", label_visibility="collapsed", key="tone_slider",
        )
        _tone_txt = _tone_labels.get(st.session_state.prompt_tone, "平衡自然")
        st.markdown(
            f"<div style='text-align:center;font-size:12px;color:rgba(255,255,255,0.55);margin-top:-8px;'>{_tone_txt}</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='tuner-label'>🎨 風格</div>",
                    unsafe_allow_html=True)
        _style_options = ["詩意", "神秘", "治癒", "復古", "都市", "自然", "夢幻", "懷舊"]
        _style_cols = st.columns(4)
        for si, style in enumerate(_style_options):
            with _style_cols[si % 4]:
                _is_active = style in st.session_state.prompt_styles
                if st.button(
                    f"{'✓ ' if _is_active else ''}{style}",
                    key=f"style_{style}",
                    type="primary" if _is_active else "secondary",
                    use_container_width=True,
                ):
                    if _is_active:
                        st.session_state.prompt_styles.remove(style)
                    else:
                        st.session_state.prompt_styles.append(style)
                    st.rerun()

        st.markdown("<div class='tuner-label'>👥 目標受眾</div>",
                    unsafe_allow_html=True)
        st.session_state.prompt_audience = st.radio(
            "audience", options=["讀書/專注", "睡眠/放鬆", "咖啡廳/日常", "工作/生產力", "不指定"],
            index=4, horizontal=True, label_visibility="collapsed", key="audience_radio",
        )

        st.markdown("<div class='tuner-label'>💡 額外指示</div>",
                    unsafe_allow_html=True)
        st.session_state.prompt_extra = st.text_input(
            "extra_prompt", value=st.session_state.prompt_extra,
            placeholder="例如：帶有日式和風元素、避免使用 emoji...",
            label_visibility="collapsed", key="extra_input",
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
        _use_ai = st.session_state.api_status == "connected"
        _mode_label = "Gemini AI" if _use_ai else "Demo（模擬資料）"
        with st.status(f"⚙️ {_mode_label} 生成中...", expanded=True) as status:
            try:
                if _use_ai:
                    st.write(f"🤖 使用 {st.session_state.api_model} 生成中...")
                    results = ai_generate(
                        st.session_state.selected_outputs,
                        st.session_state.n_songs,
                        st.session_state.user_context,
                        user_email=_USER_EMAIL,
                    )
                else:
                    st.write("🤖 使用模擬資料（未連接 API）...")
                    results = mock_generate(
                        st.session_state.selected_outputs, st.session_state.n_songs)
                if results:
                    st.session_state.results = results
                    # 儲存到持久化歷史記錄（需要登入）
                    if _USER_EMAIL:
                        save_generation(
                            email=_USER_EMAIL,
                            results=dict(results),
                            selected_outputs=list(
                                st.session_state.selected_outputs),
                            existing_materials=list(
                                st.session_state.existing_materials),
                            context=st.session_state.user_context,
                            n_songs=st.session_state.n_songs,
                            mode="ai" if _use_ai else "demo",
                        )
                    status.update(
                        label="✅ 完成！", state="complete", expanded=False)
                else:
                    status.update(label="❌ 生成失敗",
                                  state="error", expanded=False)
            except Exception as e:
                st.error(f"生成失敗：{e}")
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

    # Show uploaded image thumbnails
    imgs = st.session_state.get("uploaded_images", [])
    if imgs:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.55);font-size:11px;letter-spacing:2px;"
            "text-transform:uppercase;margin-bottom:8px;'>🖼️ 參考圖片</div>",
            unsafe_allow_html=True,
        )
        thumb_cols = st.columns(min(len(imgs), 5))
        for ti, f in enumerate(imgs[:5]):
            with thumb_cols[ti]:
                st.image(f, use_container_width=True)
        if len(imgs) > 5:
            st.caption(f"...及另外 {len(imgs) - 5} 張圖片")

    # ── 匯出列 ──
    r = st.session_state.results
    selected = st.session_state.selected_outputs

    def _build_export_text(res: dict, sel: list) -> str:
        """構建純文字匯出內容"""
        parts = []
        if "titles" in sel and res.get("titles"):
            parts.append("═══ YouTube 標題 ═══")
            for i, t in enumerate(res["titles"], 1):
                parts.append(f"  {i}. {t}")
            if res.get("titles_zh"):
                parts.append("\n── 中文 ──")
                for i, t in enumerate(res["titles_zh"], 1):
                    parts.append(f"  {i}. {t}")
        if "tags" in sel and res.get("tags"):
            parts.append("\n═══ SEO Tags ═══")
            parts.append(res["tags"])
        if "long_story" in sel and res.get("long_story"):
            parts.append("\n═══ Long Story (EN) ═══")
            parts.append(res["long_story"])
            if res.get("long_story_zh"):
                parts.append("\n── 中文 ──")
                parts.append(res["long_story_zh"])
        if "short_story" in sel and res.get("short_story"):
            parts.append("\n═══ Short Story (EN) ═══")
            parts.append(res["short_story"])
            if res.get("short_story_zh"):
                parts.append("\n── 中文 ──")
                parts.append(res["short_story_zh"])
        if "tracklist" in sel and res.get("tracklist"):
            parts.append("\n═══ Tracklist ═══")
            for s in res["tracklist"]:
                parts.append(
                    f"  {s.get('id','')}. 《{s.get('en_title','')}》 {s.get('zh_title','')}")
                parts.append(
                    f"     Theme: {s.get('en_theme','')} / {s.get('zh_theme','')}")
        return "\n".join(parts)

    # ── 匯出按鈕列 ──
    st.markdown(
        "<div class='export-bar'><span class='export-label'>📥 匯出</span></div>",
        unsafe_allow_html=True,
    )
    _ex1, _ex2 = st.columns(2)
    with _ex1:
        _dl_txt_pop = st.popover("📄 下載 TXT", use_container_width=True)
        with _dl_txt_pop:
            st.markdown("##### 📄 選擇要匯出的項目")
            _txt_sel = []
            for _ek, _eicon, _ename, _ in _OPTIONS:
                if _ek in selected and r.get(_ek if _ek != "titles" else "titles"):
                    if st.checkbox(f"{_eicon} {_ename}", value=True, key=f"txt_sel_{_ek}"):
                        _txt_sel.append(_ek)
            if _txt_sel:
                _filtered_txt = _build_export_text(r, _txt_sel)
                st.download_button(
                    "⬇️ 確認下載 TXT", _filtered_txt,
                    file_name="title_studio_export.txt",
                    mime="text/plain", use_container_width=True, key="dl_txt",
                )
            else:
                st.caption("請至少選擇一項")
    with _ex2:
        _dl_json_pop = st.popover("📦 下載 JSON", use_container_width=True)
        with _dl_json_pop:
            st.markdown("##### 📦 選擇要匯出的項目")
            _json_sel = []
            for _ek, _eicon, _ename, _ in _OPTIONS:
                if _ek in selected and r.get(_ek if _ek != "titles" else "titles"):
                    if st.checkbox(f"{_eicon} {_ename}", value=True, key=f"json_sel_{_ek}"):
                        _json_sel.append(_ek)
            if _json_sel:
                _filtered_results = {}
                for _fk in _json_sel:
                    for _rk, _rv in r.items():
                        if _rk.startswith(_fk):
                            _filtered_results[_rk] = _rv
                _filtered_json = json.dumps({
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "selected_outputs": _json_sel,
                        "user_context": st.session_state.user_context[:200],
                    },
                    "results": _filtered_results,
                }, ensure_ascii=False, indent=2)
                st.download_button(
                    "⬇️ 確認下載 JSON", _filtered_json,
                    file_name="title_studio_export.json",
                    mime="application/json", use_container_width=True, key="dl_json",
                )
            else:
                st.caption("請至少選擇一項")

    # Dashboard iframe
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
st.markdown("<div class='footer'>sLoth rAdio · Title Studio</div>",
            unsafe_allow_html=True)
