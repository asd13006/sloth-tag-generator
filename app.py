"""
sLoth rAdio · Title Studio — Dynamic Wizard Mode
Google Gemini AI-powered YouTube title, tag & SEO asset generator.
Falls back to mock data when no API key is configured.

UI Language: Traditional Chinese
Design: OLED Dark + Neon Teal (#00ffcc / #b026ff)
"""

__version__ = "0.3.0"

import json
from datetime import datetime

import streamlit as st
from PIL import Image
import io

from history import load_history, save_generation, delete_history_item
from auth import init_auth, get_auth_object, inject_auth_cookies, clear_session
from styles import inject_css
from gemini_api import MODEL_CANDIDATES, validate_api_key, ai_generate, mock_generate
from dashboard import build_dashboard, _he

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
    "results": {},               # AI / mock 結果
    "uploaded_images": [],       # Step 3 上傳嘅圖片 (UploadedFile objects)
    "view_mode": "wizard",       # "wizard" | "profile"
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
#  NAVBAR ─ [brand] ··· [api | reset | profile | status]
# ═════════════════════════════════════════════════════════════════════════
with st.container(key="navbar"):
    _c_brand, _c_space, _c_key, _c_reset, _c_user, _c_status = st.columns(
        [2.5, 3.5, 0.6, 0.6, 0.8, 1.6], vertical_alignment="center"
    )
    # ── 品牌標題 ──
    with _c_brand:
        st.markdown(
            "<div class='brand-wrap'>"
            "<span class='nb-brand'>Title Studio</span>"
            "<span class='nb-sub'>sLoth rAdio</span>"
            "</div>",
            unsafe_allow_html=True,
        )
    # ── 🔑 API Key ──
    with _c_key:
        _api_pop = st.popover("🔑", use_container_width=True, help="API Key 設定")
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
                st.caption("💡 輸入 API Key 啟用 Gemini AI。未連接時使用模擬資料。")
    # ── 🔄 重置 ──
    with _c_reset:
        if st.button("🔄", key="nb_reset_btn", use_container_width=True, help="重置所有步驟"):
            reset_pipeline()
            st.rerun()
    # ── 👤 個人中心入口 ──
    with _c_user:
        _profile_icon = "👤" if _LOGGED_IN else "🔒"
        _profile_help = (_USER_NAME or _USER_EMAIL or "個人中心") if _LOGGED_IN else "登入 / 個人中心"
        if st.button(_profile_icon, key="nb_profile_btn", use_container_width=True, help=_profile_help):
            st.session_state.view_mode = "profile" if st.session_state.view_mode != "profile" else "wizard"
            st.rerun()
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
#  PROFILE CENTER — 個人中心（帳號 · API · 設定 · 歷史）
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.view_mode == "profile":
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sec-title'>👤 個人中心</div>"
        "<div class='sec-desc'>管理帳號、API 連線、偏好設定與歷史記錄</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    _tab_account, _tab_api, _tab_settings, _tab_history = st.tabs(
        ["👤 帳號", "🔑 API", "⚙️ 設定", f"📋 歷史 ({_hist_count})"])

    # ── Tab 1: 帳號 ──
    with _tab_account:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        if _LOGGED_IN:
            _display = _USER_NAME or _USER_EMAIL or "用戶"
            st.markdown(
                f"<div style='text-align:center;padding:20px 0 10px;'>"
                f"<div style='font-size:48px;margin-bottom:12px;'>👤</div>"
                f"<div style='font-family:Righteous,sans-serif;font-size:22px;color:#fff;'>{_he(_display)}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='text-align:center;color:rgba(255,255,255,0.55);font-size:13px;margin-bottom:6px;'>📧 {_he(_USER_EMAIL)}</div>"
                f"<div style='text-align:center;color:rgba(255,255,255,0.55);font-size:13px;margin-bottom:20px;'>📋 共 {_hist_count} 筆歷史記錄</div>",
                unsafe_allow_html=True,
            )
            _acc_l, _acc_c, _acc_r = st.columns([1, 1, 1])
            with _acc_c:
                if st.button("🚪 登出", key="profile_logout", use_container_width=True):
                    clear_session()
                    st.rerun()
        else:
            st.markdown(
                "<div style='text-align:center;padding:30px 0;'>"
                "<div style='font-size:48px;margin-bottom:12px;'>🔒</div>"
                "<div style='font-family:Righteous,sans-serif;font-size:20px;color:#fff;margin-bottom:8px;'>尚未登入</div>"
                "<div style='color:rgba(255,255,255,0.55);font-size:13px;margin-bottom:20px;'>使用 Google 帳號登入以儲存歷史記錄，跨裝置同步</div>"
                "</div>",
                unsafe_allow_html=True,
            )
            if _AUTH_OBJ is not None:
                _login_l, _login_c, _login_r = st.columns([1, 1, 1])
                with _login_c:
                    _AUTH_OBJ.login(color="blue", justify_content="center")
            else:
                st.caption("未設定 OAuth → 功能暫不可用。")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 2: API ──
    with _tab_api:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
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
            st.success(f"✅ 已連接 · 模型：{st.session_state.api_model}")
        elif st.session_state.api_status == "disconnected" and st.session_state.api_key:
            st.error("❌ API Key 無效或無可用模型")
        else:
            st.info("💡 輸入 API Key 啟用 Gemini AI。未連接時使用模擬資料。")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 3: 設定 ──
    with _tab_settings:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("##### ⚙️ 偏好設定")
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
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 4: 歷史記錄 ──
    with _tab_history:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)

    # ── 返回按鈕 ──
    st.markdown("<div class='nav-spacer'></div>", unsafe_allow_html=True)
    if st.button("← 返回精靈", key="profile_back", use_container_width=True):
        st.session_state.view_mode = "wizard"
        st.rerun()

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
st.markdown(f"<div class='footer'>sLoth rAdio · Title Studio · v{__version__}</div>",
            unsafe_allow_html=True)
