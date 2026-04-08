"""
sLoth rAdio · Title Studio — Dynamic Wizard Mode
Google Gemini AI-powered YouTube title, tag & SEO asset generator.

UI Language: Traditional Chinese
Design: OLED Dark + Neon Teal (#00ffcc / #b026ff)
"""

__version__ = "0.3.0"

import json
from datetime import datetime

import streamlit as st
from PIL import Image
import io

import asyncio

from history import load_history, save_generation, delete_history_item
from auth import init_auth, get_auth_object, get_login_url, inject_auth_cookies, clear_session
from styles import inject_css
from gemini_api import MODEL_CANDIDATES, validate_api_key, ai_generate
from dashboard import build_dashboard, _he
from doubao_parser.image import doubao_image_parse
from doubao_parser.video import doubao_video_parse, yunque_video_parse

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="sLoth rAdio · Title Studio",
    page_icon="🎵",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────────────────────────────────────
_LOGGED_IN, _USER_EMAIL, _USER_NAME, _USER_PHOTO = init_auth()
_IS_GUEST = not _LOGGED_IN
_AUTH_OBJ = get_auth_object()
inject_auth_cookies()
inject_css()


# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "step": 1,
    "selected_outputs": [],      # 想生成咩：titles / tags / long_story / short_story / tracklist
    "existing_materials": [],    # 已有嘅材料（同樣 5 類 + images）
    "user_context": "",          # Step 3 用戶輸入
    "n_songs": 15,               # 歌單數量
    "results": {},               # AI 結果
    "uploaded_images": [],       # Step 3 上傳嘅圖片 (UploadedFile objects)
    "material_inputs": {},        # 各材料獨立輸入 {"titles": "...", "tags": "...", ...}
    "view_mode": "wizard",       # "wizard" | "profile"
    "api_key": "",               # API key
    "api_status": "disconnected",  # "disconnected" | "validating" | "connected"
    "api_model": "",             # 模型名稱
    "prompt_tone": 50,           # 語氣 slider 0-100
    "prompt_styles": [],         # 風格 chips
    "prompt_audience": "",       # 目標受眾
    "prompt_extra": "",          # 額外指示
    "doubao_url": "",             # 豆包連結
    "doubao_results": None,       # 豆包解析結果
    "doubao_type": "image",       # "image" | "video"
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


_hist_count = len(load_history(_USER_EMAIL)) if _USER_EMAIL else 0

# ═════════════════════════════════════════════════════════════════════════
#  NAVBAR ─ [brand] ··· [api | reset | auth]
# ═════════════════════════════════════════════════════════════════════════
with st.container(key="navbar"):
    _c_brand, _c_space, _c_doubao, _c_key, _c_reset, _c_auth = st.columns(
        [3.0, 3.4, 1.0, 0.5, 0.5, 1.6], vertical_alignment="center"
    )
    # ── 品牌標題（點擊回首頁）──
    with _c_brand:
        if st.button("Title Studio ⸱ SLOTH RADIO", key="nb_brand_home", use_container_width=True):
            st.session_state.step = 1
            st.session_state.view_mode = "wizard"
            st.rerun()
    # ── �️ 豆包無水印工具 ──
    with _c_doubao:
        _doubao_active = st.session_state.view_mode == "doubao"
        if st.button(
            "🖼️ 豆包" if not _doubao_active else "🖼️ 豆包",
            key="nb_doubao_btn",
            type="primary" if _doubao_active else "secondary",
            use_container_width=True,
            help="豆包無水印圖片/影片提取",
        ):
            st.session_state.view_mode = "doubao" if not _doubao_active else "wizard"
            st.rerun()
    # ── �🔑 API Key（動態 key 觸發狀態 CSS）──
    with _c_key:
        _api_btn_label = {"connected": "🟢", "disconnected": "🔑"}.get(
            st.session_state.api_status, "🔑")
        if st.session_state.api_status == "disconnected" and st.session_state.api_key:
            _api_btn_label = "🔴"
        _api_key_name = f"api_{st.session_state.api_status}" if st.session_state.api_status == "connected" else (
            "api_error" if st.session_state.api_key else "api_default")
        _api_pop = st.popover(_api_btn_label, use_container_width=True, help="API Key 設定", key=_api_key_name)
        with _api_pop:
            st.markdown("##### 🔑 API Key 設定")
            _new_key = st.text_input(
                "api_key_input_nb", value=st.session_state.api_key,
                type="password", placeholder="輸入 Google Gemini API Key...",
                label_visibility="collapsed",
            )
            if _new_key != st.session_state.api_key:
                st.session_state.api_key = _new_key
                if _new_key:
                    st.session_state.api_status = "validating"
                    ok, model = validate_api_key(_new_key)
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
                st.caption("💡 輸入 API Key 以啟用 Gemini AI 生成功能。")
    # ── ⟲ 重置 ──
    with _c_reset:
        if st.button("⟲", key="nb_reset_btn", use_container_width=True, help="重置所有步驟"):
            reset_pipeline()
            st.rerun()
    # ── 🔐 登入 / 用戶狀態 ──
    with _c_auth:
        if _LOGGED_IN:
            _display = _USER_NAME or _USER_EMAIL or "用戶"
            _auth_pop = st.popover(f"🟢 {_display}", use_container_width=True, help="帳號選單")
            with _auth_pop:
                if _USER_PHOTO:
                    st.markdown(
                        f"<div style='text-align:center;padding:8px 0 4px;'>"
                        f"<img src='{_he(_USER_PHOTO)}' style='width:56px;height:56px;border-radius:50%;border:2px solid rgba(0,255,204,0.3);'>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    f"<div style='text-align:center;font-weight:600;color:#fff;font-size:15px;'>{_he(_display)}</div>",
                    unsafe_allow_html=True,
                )
                if _USER_EMAIL:
                    st.markdown(
                        f"<div style='text-align:center;color:rgba(255,255,255,0.5);font-size:12px;margin-bottom:12px;'>{_he(_USER_EMAIL)}</div>",
                        unsafe_allow_html=True,
                    )
                st.divider()
                if st.button("👤 個人中心", key="auth_pop_profile", use_container_width=True):
                    st.session_state.view_mode = "profile" if st.session_state.view_mode != "profile" else "wizard"
                    st.rerun()
                if st.button("🚪 登出", key="auth_pop_logout", use_container_width=True):
                    clear_session()
                    st.rerun()
        else:
            _login_url = get_login_url()
            if _login_url:
                st.link_button("🔐 登入", _login_url, use_container_width=True)
            else:
                st.markdown(
                    "<div class='auth-badge guest'>👤 訪客</div>",
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
#  PROFILE CENTER — 個人中心（單頁區塊式）
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.view_mode == "profile":

    # ── 區塊 1：帳號資訊 ──
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    if _LOGGED_IN:
        _display = _USER_NAME or _USER_EMAIL or "用戶"
        _avatar_html = (
            f"<img src='{_he(_USER_PHOTO)}' class='profile-avatar'>"
            if _USER_PHOTO else
            "<div class='profile-avatar-placeholder'>👤</div>"
        )
        st.markdown(
            f"<div class='profile-header'>"
            f"  {_avatar_html}"
            f"  <div class='profile-info'>"
            f"    <div class='profile-name'>{_he(_display)}</div>"
            f"    <div class='profile-email'>{_he(_USER_EMAIL or '')}</div>"
            f"    <div class='profile-stat'>📋 共 {_hist_count} 筆歷史記錄</div>"
            f"  </div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        _login_url = get_login_url()
        st.markdown(
            "<div class='profile-header'>"
            "  <div class='profile-avatar-placeholder'>🔒</div>"
            "  <div class='profile-info'>"
            "    <div class='profile-name'>訪客模式</div>"
            "    <div class='profile-email'>登入 Google 帳號以儲存記錄、跨裝置同步</div>"
            "  </div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if _login_url:
            _, _login_c, _ = st.columns([1, 1, 1])
            with _login_c:
                st.link_button("🔐 Sign in with Google", _login_url, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 區塊 2：偏好設定 ──
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sec-title'>⚙️ 偏好設定</div>",
        unsafe_allow_html=True,
    )
    _pref_l, _pref_r = st.columns(2, gap="medium")
    with _pref_l:
        st.markdown("**模型偏好**")
        st.selectbox(
            "model_pref", options=["Gemini 2.5 Flash (推薦)", "Gemini 2.5 Pro", "Gemini 2.0 Flash"],
            index=0, label_visibility="collapsed", key="model_select",
        )
    with _pref_r:
        st.markdown("**介面語言**")
        st.selectbox(
            "lang_pref", options=["繁體中文", "English"],
            index=0, label_visibility="collapsed", key="lang_select",
        )
    st.caption("設定會在下次生成時生效。")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 區塊 3：歷史記錄 ──
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='sec-title'>📋 歷史記錄</div>"
        f"<div class='sec-desc'>共 {_hist_count} 筆</div>",
        unsafe_allow_html=True,
    )
    if _IS_GUEST:
        st.markdown(
            "<div style='text-align:center;padding:32px 0;color:rgba(255,255,255,0.5);font-size:14px;'>"
            "🔒 請先登入以查看歷史記錄</div>",
            unsafe_allow_html=True,
        )
    else:
        _history = load_history(_USER_EMAIL)
        if not _history:
            st.markdown(
                "<div style='text-align:center;padding:32px 0;color:rgba(255,255,255,0.5);font-size:14px;'>"
                "尚無歷史記錄 · 完成一次生成後會自動保存</div>",
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
                _summary_html = _he(_preview) if _preview else '<em style="color:rgba(255,255,255,0.50);">無輸入文字</em>'
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
                        st.session_state.selected_outputs = entry.get("selected_outputs", [])
                        st.session_state.user_context = entry.get("user_context", "")
                        st.session_state.existing_materials = entry.get("existing_materials", [])
                        st.session_state.n_songs = entry.get("n_songs", 15)
                        st.session_state.step = 4
                        st.session_state.view_mode = "wizard"
                        st.rerun()
                with _hcol2:
                    _entry_id = entry.get("id", "")
                    if _entry_id and st.button("🗑️", key=f"hist_del_{hi}", use_container_width=True, help="刪除此記錄"):
                        delete_history_item(_USER_EMAIL, _entry_id)
                        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 返回 ──
    if st.button("← 返回精靈", key="profile_back", use_container_width=True):
        st.session_state.view_mode = "wizard"
        st.rerun()

    st.markdown(f"<div class='footer'>sLoth rAdio · Title Studio · v{__version__}</div>",
                unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
#  DOUBAO TOOL — 豆包無水印圖片/影片提取
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.view_mode == "doubao":
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sec-title'>🖼️ 豆包無水印提取</div>"
        "<div class='sec-desc'>從豆包對話連結中提取無水印圖片或影片資源</div>",
        unsafe_allow_html=True,
    )

    # 類型選擇
    _db_type_l, _db_type_r = st.columns(2)
    with _db_type_l:
        if st.button(
            "🖼️ 圖片提取",
            key="db_type_image",
            type="primary" if st.session_state.doubao_type == "image" else "secondary",
            use_container_width=True,
        ):
            st.session_state.doubao_type = "image"
            st.session_state.doubao_results = None
            st.rerun()
    with _db_type_r:
        if st.button(
            "🎬 影片提取",
            key="db_type_video",
            type="primary" if st.session_state.doubao_type == "video" else "secondary",
            use_container_width=True,
        ):
            st.session_state.doubao_type = "video"
            st.session_state.doubao_results = None
            st.rerun()

    # 連結輸入
    _is_image = st.session_state.doubao_type == "image"
    _placeholder = (
        "https://www.doubao.com/thread/xxxxxx"
        if _is_image
        else "https://www.doubao.com/video-sharing?share_id=xxx&video_id=xxx"
    )
    _hint = "貼上豆包對話連結（包含 /thread/）" if _is_image else "貼上豆包影片分享連結"
    st.markdown(
        f"<div style='color:rgba(255,255,255,0.55);font-size:11px;letter-spacing:2px;"
        f"text-transform:uppercase;margin:14px 0 4px;'>🔗 {_hint}</div>",
        unsafe_allow_html=True,
    )
    _db_url = st.text_input(
        "doubao_url_input",
        value=st.session_state.doubao_url,
        placeholder=_placeholder,
        label_visibility="collapsed",
    )
    st.session_state.doubao_url = _db_url

    # 解析按鈕
    _parse_btn = st.button(
        "🔍 開始解析",
        key="db_parse_btn",
        type="primary",
        use_container_width=True,
        disabled=not _db_url.strip(),
    )

    if _parse_btn and _db_url.strip():
        with st.status("⚙️ 解析中...", expanded=True) as _db_status:
            try:
                if _is_image:
                    st.write("📡 正在提取無水印圖片...")
                    _result = asyncio.run(doubao_image_parse(_db_url.strip()))
                    st.session_state.doubao_results = {"type": "image", "data": _result}
                else:
                    st.write("📡 正在提取無水印影片...")
                    if "doubao.com" in _db_url:
                        _result = asyncio.run(doubao_video_parse(_db_url.strip()))
                    else:
                        _result = asyncio.run(yunque_video_parse(_db_url.strip()))
                    st.session_state.doubao_results = {"type": "video", "data": _result}
                _db_status.update(label="✅ 解析完成！", state="complete", expanded=False)
            except (ValueError, KeyError) as e:
                st.error(f"解析失敗：{e}")
                _db_status.update(label="❌ 解析失敗", state="error", expanded=False)
            except Exception as e:
                st.error(f"發生錯誤：{e}")
                _db_status.update(label="❌ 解析失敗", state="error", expanded=False)
        if st.session_state.doubao_results:
            st.rerun()

    # 顯示結果
    _db_res = st.session_state.doubao_results
    if _db_res:
        st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:20px 0;'>", unsafe_allow_html=True)
        if _db_res["type"] == "image":
            _images = _db_res["data"]
            st.markdown(
                f"<div class='doubao-result-header'>"
                f"<span class='chip chip-teal'>🖼️ 共 {len(_images)} 張無水印圖片</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            # 圖片網格
            _cols_per_row = 3
            for _ri in range(0, len(_images), _cols_per_row):
                _row_imgs = _images[_ri : _ri + _cols_per_row]
                _cols = st.columns(_cols_per_row)
                for _ci, _img in enumerate(_row_imgs):
                    with _cols[_ci]:
                        _img_url = _img.get("url", "")
                        _w = _img.get("width", "?")
                        _h = _img.get("height", "?")
                        st.image(_img_url, use_container_width=True)
                        st.markdown(
                            f"<div style='text-align:center;font-size:11px;color:rgba(255,255,255,0.5);'>"
                            f"{_w} × {_h}</div>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f"<a href='{_he(_img_url)}' target='_blank' rel='noopener noreferrer' "
                            f"style='display:block;text-align:center;font-size:12px;color:#00ffcc;"
                            f"text-decoration:none;margin-top:4px;'>⬇️ 開啟原圖</a>",
                            unsafe_allow_html=True,
                        )

        elif _db_res["type"] == "video":
            _video = _db_res["data"]
            st.markdown(
                "<div class='doubao-result-header'>"
                "<span class='chip chip-teal'>🎬 影片解析成功</span>"
                "</div>",
                unsafe_allow_html=True,
            )
            _v_url = _video.get("url", "")
            _v_w = _video.get("width", "?")
            _v_h = _video.get("height", "?")
            _v_def = _video.get("definition", "?")
            _poster = _video.get("poster_url", "")

            if _poster:
                st.image(_poster, use_container_width=True, caption="影片封面")

            st.markdown(
                f"<div class='doubao-video-info'>"
                f"<div><span class='chip chip-purple'>📐 {_v_w} × {_v_h}</span>"
                f"<span class='chip chip-purple'>📺 {_v_def}</span></div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<a href='{_he(_v_url)}' target='_blank' rel='noopener noreferrer' "
                f"class='doubao-download-btn'>⬇️ 下載無水印影片</a>",
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # 返回
    if st.button("← 返回精靈", key="doubao_back", use_container_width=True):
        st.session_state.view_mode = "wizard"
        st.rerun()

    st.markdown(f"<div class='footer'>sLoth rAdio · Title Studio · v{__version__}</div>",
                unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
#  API GATE — 未連接 API Key 時封鎖所有步驟
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.api_status != "connected":
    st.markdown(
        "<div class='glass api-gate'>"
        "<div class='api-gate-icon'>🔑</div>"
        "<div class='api-gate-title'>請先設定 API Key</div>"
        "<div class='api-gate-desc'>"
        "點擊右上角 🔑 按鈕輸入你的 Google Gemini API Key，"
        "連接成功後即可使用所有生成功能。"
        "</div>"
        "<a class='api-gate-link' href='https://aistudio.google.com/apikey' target='_blank' rel='noopener noreferrer'>"
        "📋 前往 Google AI Studio 取得 API Key"
        "</a>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='footer'>sLoth rAdio · Title Studio · v{__version__}</div>",
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

    def _toggle_output(key):
        if key in st.session_state.selected_outputs:
            st.session_state.selected_outputs.remove(key)
        else:
            st.session_state.selected_outputs.append(key)

    @st.fragment
    def _step1_cards():
        cols = st.columns(5, gap="medium")
        for ci, (key, icon, name, desc) in enumerate(_OPTIONS):
            with cols[ci]:
                is_sel = key in st.session_state.selected_outputs
                st.button(
                    f"{icon}\n\n**{name}**",
                    key=f"out_{key}",
                    type="primary" if is_sel else "secondary",
                    use_container_width=True,
                    on_click=_toggle_output,
                    args=(key,),
                )
                st.markdown(
                    f"<div class='card-desc'>{desc}</div>", unsafe_allow_html=True)

        n_sel = len(st.session_state.selected_outputs)

        # Navigation — actions grouped right
        st.markdown("<div class='nav-spacer'></div>", unsafe_allow_html=True)
        _, nav_all, nav_count, nav_next = st.columns([2.5, 1.2, 0.8, 1], vertical_alignment="center")
        with nav_all:
            if st.button("✓ 全選直入", use_container_width=True):
                st.session_state.selected_outputs = [k for k, *_ in _OPTIONS]
                st.session_state.existing_materials = []
                st.session_state.step = 3
                st.rerun(scope="app")
        with nav_count:
            st.markdown(
                f"<div class='counter'>已選 <b class='teal'>{n_sel}</b> 項</div>", unsafe_allow_html=True)
        with nav_next:
            if st.button("下一步 →", type="primary", use_container_width=True, disabled=(n_sel == 0)):
                st.session_state.step = 2
                st.rerun(scope="app")

    _step1_cards()

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

    def _toggle_material(key):
        if key in st.session_state.existing_materials:
            st.session_state.existing_materials.remove(key)
            if key == "images":
                st.session_state.uploaded_images = []
        else:
            st.session_state.existing_materials.append(key)

    @st.fragment
    def _step2_cards():
        # Filter out items the user wants to generate + always include images
        available = [(k, ic, nm, ds) for k, ic, nm,
                     ds in _OPTIONS if k not in st.session_state.selected_outputs]
        # Append image as a material option (always available)
        available.append(("images", "🖼️", "圖片", "上傳參考圖讓 AI 理解視覺風格"))

        cols = st.columns(len(available), gap="medium")
        for ci, (key, icon, name, _) in enumerate(available):
            with cols[ci]:
                is_sel = key in st.session_state.existing_materials
                st.button(f"{icon}\n\n**已有{name}**", key=f"mat_{key}",
                          type="primary" if is_sel else "secondary", use_container_width=True,
                          on_click=_toggle_material, args=(key,))

        n_mat = len(st.session_state.existing_materials)

        # Navigation — actions grouped right
        st.markdown("<div class='nav-spacer'></div>", unsafe_allow_html=True)
        nav_back, _, nav_skip, nav_count, nav_next = st.columns([1, 1, 1.5, 0.8, 1], vertical_alignment="center")
        with nav_back:
            if st.button("← 返回", key="s2_back", use_container_width=True):
                st.session_state.existing_materials = []
                st.session_state.step = 1
                st.rerun(scope="app")
        with nav_skip:
            if st.button("跳過，從零開始", key="s2_skip", use_container_width=True):
                st.session_state.existing_materials = []
                st.session_state.step = 3
                st.rerun(scope="app")
        with nav_count:
            st.markdown(
                f"<div class='counter'>已選 <b class='purple'>{n_mat}</b> 項材料</div>", unsafe_allow_html=True)
        with nav_next:
            if st.button("下一步 →", key="s2_next", type="primary", use_container_width=True):
                st.session_state.step = 3
                st.rerun(scope="app")

    _step2_cards()

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

    # ── 已有材料：分欄輸入 ──
    _text_materials = [k for k in st.session_state.existing_materials if k != "images"]
    if _text_materials:
        st.markdown(
            "<div class='sec-desc' style='margin-bottom:12px;'>"
            f"請分別填入你已有嘅 {mat_names}，AI 會參照呢啲素材嚟生成 {gen_names}："
            "</div>",
            unsafe_allow_html=True,
        )
        _mat_placeholders = {
            "titles":      "例如：Midnight Rain… Lofi for Study 🌧️ 📚",
            "tags":        "例如：lofi, chill music, study beats, rainy night",
            "long_story":  "例如：You sit by the window on a rainy evening...",
            "short_story": "例如：Making Tea 🍵\nEvening settles outside the window...",
            "tracklist":   "例如：1. 雨夜書房 2. 窗邊咖啡 3. 晨光微醒",
        }
        _mat_heights = {
            "titles": 100, "tags": 80, "long_story": 180,
            "short_story": 120, "tracklist": 140,
        }
        # 確保 material_inputs dict 存在
        if not isinstance(st.session_state.material_inputs, dict):
            st.session_state.material_inputs = {}
        for _mk in _text_materials:
            _mlabel = _MATERIAL_LABELS.get(_mk, _mk)
            _micon = dict(_OPTIONS).get(_mk, ("📄",))[0] if any(k == _mk for k, *_ in _OPTIONS) else "📄"
            # 找到對應 icon
            for _ok, _oi, _on, _od in _OPTIONS:
                if _ok == _mk:
                    _micon = _oi
                    break
            st.markdown(
                f"<div style='color:rgba(255,255,255,0.55);font-size:11px;letter-spacing:2px;"
                f"text-transform:uppercase;margin:14px 0 4px;'>{_micon} 已有{_mlabel}</div>",
                unsafe_allow_html=True,
            )
            _mat_val = st.session_state.material_inputs.get(_mk, "")
            _new_val = st.text_area(
                f"mat_input_{_mk}",
                value=_mat_val,
                height=_mat_heights.get(_mk, 120),
                placeholder=_mat_placeholders.get(_mk, f"貼上你已有嘅{_mlabel}..."),
                label_visibility="collapsed",
            )
            st.session_state.material_inputs[_mk] = _new_val

    # ── 通用補充輸入 ──
    if _text_materials:
        _ctx_hint = f"有冇其他靈感或補充想法？（選填）"
    elif st.session_state.selected_outputs == ["tracklist"]:
        _ctx_hint = "請描述你想要嘅風格或氛圍："
    else:
        _ctx_hint = f"請將你現有嘅靈感、故事或歌單貼喺下面，我會幫你生成 {gen_names}："
    st.markdown(
        f"<div class='sec-desc' style='margin-bottom:12px;'>{_ctx_hint}</div>", unsafe_allow_html=True)

    user_input = st.text_area(
        "content_input",
        value=st.session_state.user_context,
        height=120 if _text_materials else 220,
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
        # 合併各材料欄位 + 通用輸入為完整 context
        _ctx_parts = []
        for _mk, _mv in st.session_state.material_inputs.items():
            _mv_strip = _mv.strip()
            if _mv_strip:
                _ctx_parts.append(f"[已有{_MATERIAL_LABELS.get(_mk, _mk)}]\n{_mv_strip}")
        if st.session_state.user_context.strip():
            _ctx_parts.append(st.session_state.user_context.strip())
        _combined_context = "\n\n".join(_ctx_parts)

        with st.status(f"⚙️ Gemini AI 生成中...", expanded=True) as status:
            try:
                st.write(f"🤖 使用 {st.session_state.api_model} 生成中...")
                results = ai_generate(
                    st.session_state.selected_outputs,
                    st.session_state.n_songs,
                    _combined_context,
                    user_email=_USER_EMAIL,
                )
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
                            context=_combined_context,
                            n_songs=st.session_state.n_songs,
                            mode="ai",
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
st.markdown(f"<div class='footer'>sLoth rAdio · Title Studio · v{__version__}</div>",
            unsafe_allow_html=True)
