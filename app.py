"""
sLoth rAdio · Title Studio — 3-Step Wizard Mode
Google Gemini AI-powered YouTube title, tag & SEO asset generator.

UI Language: Traditional Chinese
Design: Material 3 Surface Hierarchy (#99f7ff / #d674ff)
"""

__version__ = "0.4.0"

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
    initial_sidebar_state="expanded",
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
_DEFAULTS = {
    "step": 1,                   # 1=Archetype, 2=Material Lab, 3=Results
    "selected_outputs": [],      # 想生成咩：titles / tags / long_story / short_story / tracklist
    "selected_archetypes": [],   # Archetype 卡片選擇：titles / tags / stories / tracklist
    "existing_materials": [],    # 已有嘅材料
    "user_context": "",          # Step 2 用戶輸入
    "n_songs": 15,               # 歌單數量
    "results": {},               # AI 結果
    "uploaded_images": [],       # Step 2 上傳嘅圖片
    "material_inputs": {},       # 各材料獨立輸入
    "view_mode": "wizard",       # "wizard" | "profile" | "doubao"
    "api_key": "",               # API key
    "api_status": "disconnected",
    "api_model": "",
    "prompt_tone": 50,
    "prompt_styles": [],
    "prompt_audience": "",
    "prompt_extra": "",
    "prompt_style_variance": 50,
    "doubao_url": "",
    "doubao_results": None,
    "doubao_type": "image",
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


def go_step(n: int):
    """切換 wizard 步驟並 rerun。"""
    st.session_state.step = n
    st.session_state.view_mode = "wizard"
    if n < 3:
        st.session_state.results = {}
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  OPTION DEFINITIONS
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

# Archetype 卡片定義 → 映射到 selected_outputs
_ARCHETYPES = [
    ("titles",    "▶️", "YouTube Titles",
     "高 CTR 導向。運用心理觸發點與病毒式 metadata 分析。", "primary"),
    ("tags",      "🔍", "SEO Tags",
     "演算法精準映射，全球搜尋排名優勢與語義關聯。", "secondary"),
    ("stories",   "🎭", "Scenario Stories",
     "多分支敘事弧線——適用短影音、遊戲與沉浸式社群內容。", "primary"),
    ("tracklist", "🎵", "Suno Playlist",
     "和聲提示 AI 音樂生成。打造風格、歌詞與曲式結構。", "secondary"),
]

_ARCHETYPE_TO_OUTPUTS = {
    "titles": ["titles"],
    "tags": ["tags"],
    "stories": ["long_story", "short_story"],
    "tracklist": ["tracklist"],
}

_hist_count = len(load_history(_USER_EMAIL)) if _USER_EMAIL else 0


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: HTML wrapper with animation class
# ─────────────────────────────────────────────────────────────────────────────
def anim(html: str, n: int = 1) -> None:
    """用 anim-N class 包裹 HTML，產生遞延進場動畫。"""
    st.markdown(f'<div class="anim-{n}">{html}</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
_WIZARD_STEPS = [
    ("💡", "Concept", 1),
    ("📝", "Draft", 2),
    ("🚀", "Generate", 3),
]

with st.sidebar:
    # Brand
    st.markdown("""
        <div style="padding: 8px 0 4px;">
            <p class="sb-brand">Title Studio</p>
            <p class="sb-subtitle">Sloth Radio</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── Wizard Mode ──
    st.markdown('<p class="sb-section-label">Wizard Mode</p>', unsafe_allow_html=True)

    for icon, label, step_num in _WIZARD_STEPS:
        is_active = (st.session_state.view_mode == "wizard" and
                     st.session_state.step == step_num)
        if st.button(
            f"{icon}  {label}",
            key=f"nav_wiz_{label.lower()}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            go_step(step_num)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── 工具 ──
    st.markdown('<p class="sb-section-label">Tools</p>', unsafe_allow_html=True)

    if st.button("🫘  豆包工具", key="nav_doubao",
                 type="primary" if st.session_state.view_mode == "doubao" else "secondary",
                 use_container_width=True):
        st.session_state.view_mode = "doubao" if st.session_state.view_mode != "doubao" else "wizard"
        st.rerun()

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── 設定 ──
    st.markdown('<p class="sb-section-label">Configure</p>', unsafe_allow_html=True)

    # API Key — compact status in sidebar, full input in main area
    if st.session_state.api_status == "connected":
        st.markdown(f"""
            <div class="sb-api-compact connected">
                <span class="sb-api-icon">🟢</span>
                <div class="sb-api-info">
                    <p class="sb-api-title">已連線</p>
                    <p class="sb-api-detail">{_he(st.session_state.api_model)}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif st.session_state.api_key and st.session_state.api_status == "disconnected":
        st.markdown("""
            <div class="sb-api-compact error">
                <span class="sb-api-icon">🔴</span>
                <div class="sb-api-info">
                    <p class="sb-api-title">連線失敗</p>
                    <p class="sb-api-detail">請在主畫面重新輸入</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="sb-api-compact">
                <span class="sb-api-icon">⚪</span>
                <div class="sb-api-info">
                    <p class="sb-api-title">尚未連線</p>
                    <p class="sb-api-detail">請在主畫面設定 API Key</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    if st.button("📊  歷史記錄", key="nav_history",
                 type="primary" if st.session_state.view_mode == "profile" else "secondary",
                 use_container_width=True):
        st.session_state.view_mode = "profile" if st.session_state.view_mode != "profile" else "wizard"
        st.rerun()

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── 帳戶 ──
    st.markdown('<p class="sb-section-label">Account</p>', unsafe_allow_html=True)

    if _LOGGED_IN:
        _display = _USER_NAME or _USER_EMAIL or "用戶"
        if st.button(f"👤  {_display}", key="nav_profile",
                     type="primary" if st.session_state.view_mode == "profile" else "secondary",
                     use_container_width=True):
            st.session_state.view_mode = "profile" if st.session_state.view_mode != "profile" else "wizard"
            st.rerun()
        if st.button("🚪  登出", key="nav_logout",
                     type="secondary", use_container_width=True):
            clear_session()
            st.rerun()
    else:
        _login_url = get_login_url()
        if _login_url:
            st.link_button("🔐 Sign in with Google", _login_url, use_container_width=True)
        else:
            st.markdown(
                "<div class='auth-badge guest' style='margin:0 14px;'>👤 訪客</div>",
                unsafe_allow_html=True,
            )

    # New Project button
    if st.button("🔄  New Project", key="nav_new_project",
                 type="secondary",
                 use_container_width=True):
        reset_pipeline()
        st.rerun()

    # Footer — pinned to bottom via flex
    st.markdown(f"""
        <p class="sb-version">sLoth rAdio · Title Studio · v{__version__}</p>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  PROFILE CENTER — 個人中心
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.view_mode == "profile":

    anim("""
        <div class="hero-title">📋 個人中心</div>
        <div class="hero-desc">管理帳號、偏好設定與歷史記錄</div>
    """, 1)

    # ── 區塊 1：帳號資訊 ──
    with st.container(key="input_glass"):
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

    # ── 區塊 2：偏好設定 ──
    anim('<div class="sec-title">⚙️ 偏好設定</div>', 2)
    with st.container(key="settings_glass"):
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

    # ── 區塊 3：歷史記錄 ──
    anim(f"""
        <div class="sec-title">📋 歷史記錄</div>
        <div class="sec-desc">共 {_hist_count} 筆</div>
    """, 3)

    if _IS_GUEST:
        st.markdown(
            "<div style='text-align:center;padding:32px 0;color:var(--text-muted);font-size:14px;'>"
            "🔒 請先登入以查看歷史記錄</div>",
            unsafe_allow_html=True,
        )
    else:
        _history = load_history(_USER_EMAIL)
        if not _history:
            st.markdown(
                "<div style='text-align:center;padding:32px 0;color:var(--text-muted);font-size:14px;'>"
                "尚無歷史記錄 · 完成一次生成後會自動保存</div>",
                unsafe_allow_html=True,
            )
        else:
            for hi, entry in enumerate(_history):
                _ts = entry.get("timestamp", "")
                _types = " ".join(
                    f"<span class='chip chip-blue'>{_MATERIAL_LABELS.get(k, k)}</span>"
                    for k in entry.get("selected_outputs", [])
                )
                _preview = entry.get("user_context", "")[:80]
                if len(entry.get("user_context", "")) > 80:
                    _preview += "..."
                _summary_html = _he(_preview) if _preview else '<em style="color:var(--outline);">無輸入文字</em>'
                _mode = entry.get("mode", "demo")
                _mode_badge = (
                    "<span style='font-size:10px;color:var(--primary);font-weight:600;margin-left:8px;'>AI</span>"
                    if _mode == "ai" else
                    "<span style='font-size:10px;color:var(--warning);font-weight:600;margin-left:8px;'>Demo</span>"
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
                        st.session_state.step = 3
                        st.session_state.view_mode = "wizard"
                        st.rerun()
                with _hcol2:
                    _entry_id = entry.get("id", "")
                    if _entry_id and st.button("🗑️", key=f"hist_del_{hi}", use_container_width=True, help="刪除此記錄"):
                        delete_history_item(_USER_EMAIL, _entry_id)
                        st.rerun()

    # ── 返回 ──
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    if st.button("← 返回精靈", key="profile_back", use_container_width=True):
        st.session_state.view_mode = "wizard"
        st.rerun()

    st.markdown(f'<p class="footer anim-8">sLoth rAdio · Title Studio · v{__version__}</p>',
                unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
#  DOUBAO TOOL — 豆包無水印圖片/影片提取
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.view_mode == "doubao":
    anim("""
        <div class="hero-title">🫘 豆包無水印提取</div>
        <div class="hero-desc">從豆包對話連結中提取無水印圖片或影片資源</div>
    """, 1)

    with st.container(key="doubao_glass"):
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
            f"<div style='color:var(--text-muted);font-size:11px;letter-spacing:2px;"
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
        st.markdown("<hr style='border-color:var(--border);margin:20px 0;'>", unsafe_allow_html=True)
        if _db_res["type"] == "image":
            _images = _db_res["data"]
            st.markdown(
                f"<div class='doubao-result-header'>"
                f"<span class='chip chip-blue'>🖼️ 共 {len(_images)} 張無水印圖片</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
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
                            f"<div style='text-align:center;font-size:11px;color:var(--text-muted);'>"
                            f"{_w} × {_h}</div>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f"<a href='{_he(_img_url)}' target='_blank' rel='noopener noreferrer' "
                            f"style='display:block;text-align:center;font-size:12px;color:var(--primary);"
                            f"text-decoration:none;margin-top:4px;'>⬇️ 開啟原圖</a>",
                            unsafe_allow_html=True,
                        )

        elif _db_res["type"] == "video":
            _video = _db_res["data"]
            st.markdown(
                "<div class='doubao-result-header'>"
                "<span class='chip chip-blue'>🎬 影片解析成功</span>"
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

    # 返回
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    if st.button("← 返回精靈", key="doubao_back", use_container_width=True):
        st.session_state.view_mode = "wizard"
        st.rerun()

    st.markdown(f'<p class="footer anim-4">sLoth rAdio · Title Studio · v{__version__}</p>',
                unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
#  API GATE — 未連接 API Key 時封鎖所有步驟
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.api_status != "connected":
    st.markdown(
        "<div class='api-gate-wrapper'>"
        "<div class='glass api-gate'>"
        "<div class='api-gate-icon'>🔑</div>"
        "<div class='api-gate-title'>請先設定 API Key</div>"
        "<div class='api-gate-desc'>"
        "輸入你的 Google Gemini API Key 即可使用所有生成功能。"
        "</div>",
        unsafe_allow_html=True,
    )

    # API key input in main content area
    _new_key = st.text_input(
        "api_key_input_main", value=st.session_state.api_key,
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
    if st.session_state.api_status == "disconnected" and st.session_state.api_key:
        st.caption("❌ API Key 無效，請確認後重新輸入")

    st.markdown(
        "<div style='text-align:center;margin-top:20px;'>"
        "<a class='api-gate-link' href='https://aistudio.google.com/apikey' target='_blank' rel='noopener noreferrer'>"
        "📋 前往 Google AI Studio 取得 API Key"
        "</a>"
        "</div>"
        "</div>"   # close .glass.api-gate
        "</div>",  # close .api-gate-wrapper
        unsafe_allow_html=True,
    )
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
#  STEP 1 — Select Creative Archetype
# ═════════════════════════════════════════════════════════════════════════════
step = st.session_state.step

if step == 1:
    # Phase indicator
    anim("""
        <div class="phase-indicator">
            <div class="phase-line"></div>
            <span class="phase-label">Initiating Phase 01</span>
        </div>
    """, 1)

    # Hero
    anim("""
        <div class="wizard-hero">
            <h1>Select your <span class="gradient-text">Creative Archetype</span></h1>
            <p class="hero-sub">選擇專屬的創作引擎。每條路徑使用針對不同數位格式調校的 LLM 權重。</p>
        </div>
    """, 2)

    # Archetype cards — 4 columns
    card_cols = st.columns(4, gap="medium")
    for i, (key, icon, title, desc, variant) in enumerate(_ARCHETYPES):
        with card_cols[i]:
            is_selected = key in st.session_state.selected_archetypes
            selected_cls = " selected" if is_selected else ""
            variant_cls = " variant-secondary" if variant == "secondary" else ""
            badge_html = '<span class="arch-selected-badge">Selected</span>' if is_selected else '<span class="arch-selected-badge"></span>'

            anim(f"""
                <div class="archetype-card{selected_cls}{variant_cls}">
                    {badge_html}
                    <div>
                        <div class="arch-icon">{icon}</div>
                        <div class="arch-title">{title}</div>
                        <div class="arch-desc">{desc}</div>
                    </div>
                    <div class="arch-deploy">
                        <span>Deploy Core</span>
                        <span>→</span>
                    </div>
                </div>
            """, i + 3)

            if st.button(
                f"{'✅ ' if is_selected else ''}{title}",
                key=f"arch_{key}",
                type="primary" if is_selected else "secondary",
                use_container_width=True,
            ):
                if is_selected:
                    st.session_state.selected_archetypes.remove(key)
                else:
                    st.session_state.selected_archetypes.append(key)
                st.rerun()

    # Terminal decoration
    anim("""
        <div class="terminal-block">
            <p>&gt; initializing_neural_link...</p>
            <p>&gt; sync_creative_parameters: OK</p>
            <p>&gt; awaiting_archetype_selection_</p>
        </div>
    """, 7)

    # Quick-select all + Confirm
    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
    _, col_all, col_btn = st.columns([2, 1, 1])
    with col_all:
        if st.button("✓ 全選直入", key="btn_select_all", use_container_width=True):
            st.session_state.selected_archetypes = [k for k, *_ in _ARCHETYPES]
            # Convert to outputs and jump to Step 2
            st.session_state.selected_outputs = []
            for arch in st.session_state.selected_archetypes:
                st.session_state.selected_outputs.extend(_ARCHETYPE_TO_OUTPUTS[arch])
            st.session_state.step = 2
            st.rerun()
    with col_btn:
        can_proceed = len(st.session_state.selected_archetypes) > 0
        if st.button(
            "確認選擇 →" if can_proceed else "請至少選擇一項",
            type="primary" if can_proceed else "secondary",
            use_container_width=True,
            disabled=not can_proceed,
            key="btn_step1_next",
        ):
            # Convert archetypes to output list
            st.session_state.selected_outputs = []
            for arch in st.session_state.selected_archetypes:
                st.session_state.selected_outputs.extend(_ARCHETYPE_TO_OUTPUTS[arch])
            go_step(2)


# ═════════════════════════════════════════════════════════════════════════════
#  STEP 2 — Material Lab（收集上下文 + 調校）
# ═════════════════════════════════════════════════════════════════════════════
elif step == 2:
    # Header + progress bar
    selected_count = len(st.session_state.selected_archetypes)
    gen_names = "、".join(_MATERIAL_LABELS[k] for k in st.session_state.selected_outputs)
    seg_html = ""
    for i in range(3):
        active = " active" if i < 2 else ""
        seg_html += f'<div class="step-seg{active}"></div>'

    anim(f"""
        <div class="wizard-header">
            <div class="left">
                <h1>Material Lab</h1>
                <p class="subtitle">為你的作品注入核心素材，校準創作引擎。已選 {selected_count} 個 Archetype → {gen_names}。</p>
            </div>
            <div class="step-bar">
                <div class="step-segments">{seg_html}</div>
                <span class="step-counter">Step 02 / 03</span>
            </div>
        </div>
    """, 1)

    # Split pane: 7 input + 5 tuning
    _col_left, _col_right = st.columns([7, 5], gap="large")

    # ════════════════════════════════════════
    #  LEFT COLUMN — 素材輸入 + 圖片上傳
    # ════════════════════════════════════════
    with _col_left:
        anim('<p class="context-label">Context Synthesis</p>', 2)

        with st.container(key="input_glass"):
            if st.session_state.selected_outputs == ["tracklist"]:
                _ctx_hint = "請描述你想要嘅風格或氛圍…"
            else:
                _ctx_hint = f"貼上你的靈感、故事或創意 prompt，AI 會幫你生成 {gen_names}…"
            user_input = st.text_area(
                "content_input",
                value=st.session_state.user_context,
                height=200,
                placeholder=_ctx_hint,
                label_visibility="collapsed",
            )
            st.session_state.user_context = user_input

        # Existing materials
        anim('<p class="context-label">已有材料（可選）</p>', 3)
        _mat_placeholders = {
            "titles":      "例如：Midnight Rain… Lofi for Study 🌧️ 📚",
            "tags":        "例如：lofi, chill music, study beats, rainy night",
            "long_story":  "例如：You sit by the window on a rainy evening...",
            "short_story": "例如：Making Tea 🍵\nEvening settles outside the window...",
            "tracklist":   "例如：1. 雨夜書房 2. 窗邊咖啡 3. 晨光微醒",
        }
        if not isinstance(st.session_state.material_inputs, dict):
            st.session_state.material_inputs = {}

        # Show relevant material inputs (items NOT being generated)
        _available_mats = [k for k, *_ in _OPTIONS if k not in st.session_state.selected_outputs]
        for _mk in _available_mats:
            _mlabel = _MATERIAL_LABELS.get(_mk, _mk)
            _micon = "📄"
            for _ok, _oi, _on, _od in _OPTIONS:
                if _ok == _mk:
                    _micon = _oi
                    break
            _mat_val = st.session_state.material_inputs.get(_mk, "")
            _new_val = st.text_input(
                f"已有{_mlabel}",
                value=_mat_val,
                placeholder=_mat_placeholders.get(_mk, f"貼上你已有嘅{_mlabel}..."),
                key=f"mat_input_{_mk}",
            )
            st.session_state.material_inputs[_mk] = _new_val

        # Gemini Visual Context
        st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
        label_col, badge_col = st.columns([4, 1])
        with label_col:
            anim('<p class="context-label">Gemini Visual Context</p>', 4)
        with badge_col:
            st.markdown('<span class="vision-badge">AI Vision Enabled</span>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "上傳參考圖片",
            type=["png", "jpg", "jpeg", "webp", "gif"],
            accept_multiple_files=True,
            key="img_upload",
            label_visibility="collapsed",
        )
        if uploaded:
            st.session_state.uploaded_images = uploaded
            thumb_cols = st.columns(min(len(uploaded), 5))
            for ti, f in enumerate(uploaded[:5]):
                with thumb_cols[ti]:
                    st.image(f, use_container_width=True, caption=f.name)
            if len(uploaded) > 5:
                st.caption(f"…及另外 {len(uploaded) - 5} 張圖片")

    # ════════════════════════════════════════
    #  RIGHT COLUMN — Tuning Terminal
    # ════════════════════════════════════════
    with _col_right:
        with st.container(key="tuning_terminal"):
            st.markdown("""
                <div class="tuning-header">
                    <span class="tune-icon">🎛️</span>
                    <h3>Tuning Terminal</h3>
                </div>
                <p class="tuning-subtitle">校準輸出共鳴與目標諧波</p>
            """, unsafe_allow_html=True)

            # ── Tone Matrix Slider ──
            st.markdown('<p class="tuner-label">Tone Matrix</p>', unsafe_allow_html=True)
            _tone_val = st.session_state.prompt_tone
            tone = st.slider(
                "Tone",
                0, 100, _tone_val,
                step=25,
                key="tone_slider",
                label_visibility="collapsed",
            )
            st.session_state.prompt_tone = tone
            tone_name = "Catchy" if tone < 33 else ("Formal" if tone < 66 else "Dramatic")
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:-8px; margin-bottom:16px;">
                    <div class="slider-labels"><span>Catchy</span></div>
                    <span class="slider-value">{tone_name} // {tone}%</span>
                    <div class="slider-labels"><span>Dramatic</span></div>
                </div>
            """, unsafe_allow_html=True)

            # ── Style Variance Slider ──
            st.markdown('<p class="tuner-label">Style Variance</p>', unsafe_allow_html=True)
            _style_variance = st.session_state.get("prompt_style_variance", 50)
            style_var = st.slider(
                "Style",
                0, 100, _style_variance,
                step=25,
                key="style_slider",
                label_visibility="collapsed",
            )
            st.session_state["prompt_style_variance"] = style_var
            style_name = "Minimal" if style_var < 33 else ("Dynamic" if style_var < 66 else "Complex")
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:-8px; margin-bottom:16px;">
                    <div class="slider-labels"><span>Minimal</span></div>
                    <span class="slider-value secondary">{style_name} // {style_var}%</span>
                    <div class="slider-labels"><span>Complex</span></div>
                </div>
            """, unsafe_allow_html=True)

            # ── Target Audience ──
            st.markdown('<p class="tuner-label">Target Audience Nucleus</p>', unsafe_allow_html=True)
            _aud_options = [
                ("study", "讀書/專注"),
                ("sleep", "睡眠/放鬆"),
                ("cafe", "咖啡廳/日常"),
                ("work", "工作/生產力"),
            ]
            aud_cols = st.columns(2)
            for idx, (aud_key, aud_label) in enumerate(_aud_options):
                with aud_cols[idx % 2]:
                    is_aud = st.session_state.prompt_audience == aud_label
                    if st.button(
                        f"{'◉ ' if is_aud else '○ '}{aud_label}",
                        key=f"aud_{aud_key}",
                        type="primary" if is_aud else "secondary",
                        use_container_width=True,
                    ):
                        st.session_state.prompt_audience = aud_label if not is_aud else ""
                        st.rerun()

            # ── 風格 Chips ──
            st.markdown('<p class="tuner-label" style="margin-top:16px;">Style Chips</p>', unsafe_allow_html=True)
            _style_options = ["詩意", "神秘", "治癒", "復古", "都市", "自然", "夢幻", "懷舊"]
            _sc_cols = st.columns(4, gap="small")
            for si, style in enumerate(_style_options):
                with _sc_cols[si % 4]:
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

            # ── 額外指示 ──
            st.markdown(
                "<div style='color:var(--text-muted);font-size:10px;letter-spacing:2px;"
                "text-transform:uppercase;margin:18px 0 6px;'>💡 額外指示</div>",
                unsafe_allow_html=True,
            )
            st.session_state.prompt_extra = st.text_input(
                "extra_prompt", value=st.session_state.prompt_extra,
                placeholder="例如：帶有日式和風元素、避免使用 emoji…",
                label_visibility="collapsed", key="extra_input",
            )

            # ── 歌單數量 ──
            if "tracklist" in st.session_state.selected_outputs:
                st.markdown(
                    "<div style='color:var(--text-muted);font-size:10px;letter-spacing:2px;"
                    "text-transform:uppercase;margin:14px 0 4px;'>🎚️ 歌單數量</div>",
                    unsafe_allow_html=True,
                )
                st.session_state.n_songs = st.slider(
                    "n_songs", min_value=1, max_value=20,
                    value=st.session_state.n_songs, step=1,
                    label_visibility="collapsed",
                )

    # Action row: Back + Generate
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    back_col, _, confirm_col = st.columns([1, 2, 2])
    with back_col:
        if st.button("← Back", key="btn_step2_back", use_container_width=True):
            go_step(1)
    with confirm_col:
        gen_btn = st.button("✨ 確認調校 · 開始生成", type="primary",
                            use_container_width=True, key="btn_step2_next")

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

        with st.status("⚙️ Gemini AI 生成中...", expanded=True) as status:
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
            st.session_state.step = 3
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
#  STEP 3 — Results Dashboard
# ═════════════════════════════════════════════════════════════════════════════
elif step == 3:

    # Result hero
    anim("""
        <div class="result-hero">
            <p class="result-label">Generation Complete</p>
            <h1>Celestial Results</h1>
            <p class="result-desc">Gemini AI 已將你的概念蒸餾為高效能創意資產。精準調校，最大化 CTR。</p>
        </div>
    """, 1)

    r = st.session_state.results
    selected = st.session_state.selected_outputs

    if r:
        # ── Titles Section (inline, frost-border style) ──
        if "titles" in selected and r.get("titles"):
            titles_en = r["titles"]
            titles_zh = r.get("titles_zh", [])
            titles_cards = ""
            for i, en in enumerate(titles_en):
                zh = titles_zh[i] if i < len(titles_zh) else ""
                if i == 0:
                    titles_cards += f"""
                        <div class="title-card-primary">
                            <span class="match-badge">#{i+1}</span>
                            <h2>{_he(en)}</h2>
                            <div style="font-size:13px; color:var(--text-muted); margin-bottom:12px;">{_he(zh)}</div>
                        </div>
                    """
                else:
                    titles_cards += f"""
                        <div class="title-card-secondary">
                            <h2>{_he(en)}</h2>
                            <div style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">{_he(zh)}</div>
                        </div>
                    """

            anim(f"""
                <div class="frost-border">
                    <div class="frost-border-inner">
                        <div class="result-section-header">
                            <div class="section-left">
                                <span class="pulse-dot"></span>
                                <span class="section-title">YouTube Master Titles</span>
                            </div>
                            <div class="section-actions">
                                <span style="font-size:11px;color:var(--text-muted);">{len(titles_en)} titles</span>
                            </div>
                        </div>
                        {titles_cards}
                    </div>
                </div>
            """, 2)

        # ── Tags Section ──
        if "tags" in selected and r.get("tags"):
            tags_str = r["tags"]
            tags_list = [t.strip() for t in tags_str.split(",") if t.strip()]
            pills_html = "".join(f'<span class="tag-pill">{_he(t)}</span>' for t in tags_list)
            char_count = len(tags_str)

            anim(f"""
                <div class="glass">
                    <div class="card-header">
                        <div class="card-icon purple">🏷️</div>
                        <span class="card-title">SEO Tags</span>
                        <span class="card-badge">{len(tags_list)} tags · {char_count}/500</span>
                    </div>
                    <div class="tag-cloud">{pills_html}</div>
                </div>
            """, 3)

        # ── Stories Section ──
        _has_long = "long_story" in selected and r.get("long_story")
        _has_short = "short_story" in selected and r.get("short_story")

        if _has_long and _has_short:
            col_s1, col_s2 = st.columns(2)
        elif _has_long:
            col_s1 = st.container()
            col_s2 = None
        elif _has_short:
            col_s1 = None
            col_s2 = st.container()
        else:
            col_s1 = col_s2 = None

        if _has_long and col_s1 is not None:
            with col_s1:
                anim(f"""
                    <div class="glass-elevated">
                        <div class="card-header">
                            <div class="card-icon green">📖</div>
                            <span class="card-title">Long Story</span>
                            <span class="card-badge green">EN</span>
                        </div>
                        <div class="story-prose">{_he(r['long_story'])}</div>
                    </div>
                """, 4)
                if r.get("long_story_zh"):
                    anim(f"""
                        <div class="glass-elevated">
                            <div class="card-header">
                                <div class="card-icon green">📖</div>
                                <span class="card-title">Long Story</span>
                                <span class="card-badge">中文</span>
                            </div>
                            <div class="story-prose">{_he(r['long_story_zh'])}</div>
                        </div>
                    """, 4)

        if _has_short and col_s2 is not None:
            with col_s2:
                anim(f"""
                    <div class="glass-elevated">
                        <div class="card-header">
                            <div class="card-icon purple">💬</div>
                            <span class="card-title">Short Story</span>
                            <span class="card-badge">EN</span>
                        </div>
                        <div class="story-prose">{_he(r['short_story'])}</div>
                    </div>
                """, 5)
                if r.get("short_story_zh"):
                    anim(f"""
                        <div class="glass-elevated">
                            <div class="card-header">
                                <div class="card-icon purple">💬</div>
                                <span class="card-title">Short Story</span>
                                <span class="card-badge">中文</span>
                            </div>
                            <div class="story-prose">{_he(r['short_story_zh'])}</div>
                        </div>
                    """, 5)

        # ── Tracklist Section ──
        if "tracklist" in selected and r.get("tracklist"):
            tracks_html = ""
            for i, s in enumerate(r["tracklist"], 1):
                en = s.get("en_title", "")
                zh = s.get("zh_title", "")
                theme_en = s.get("en_theme", "")
                tracks_html += f"""
                <div class="track-row">
                    <span class="track-num">{i:02d}</span>
                    <div class="track-info">
                        <div class="track-title">{_he(en)}</div>
                        <div class="track-sub">{_he(zh)}</div>
                    </div>
                    <span class="track-theme">{_he(theme_en)}</span>
                </div>"""

            anim(f"""
                <div class="glass">
                    <div class="card-header">
                        <div class="card-icon amber">🎵</div>
                        <span class="card-title">Suno Playlist</span>
                        <span class="card-badge">{len(r['tracklist'])} tracks</span>
                    </div>
                    {tracks_html}
                </div>
            """, 6)

        # ── Review card ──
        ctx = st.session_state.user_context.strip()
        if ctx:
            st.markdown(
                f"<div class='review-card'>"
                f"<div class='review-label'>根據你提供的資訊</div>"
                f"<div class='review-text'>{_he(ctx)}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # ── Uploaded image thumbnails ──
        imgs = st.session_state.get("uploaded_images", [])
        if imgs:
            st.markdown(
                "<div style='color:var(--text-muted);font-size:11px;letter-spacing:2px;"
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

        # ── Dashboard iframe (detailed view with copy/translate) ──
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

        with st.expander("📋 詳細檢視（含複製/翻譯按鈕）", expanded=False):
            st.components.v1.html(html, height=h, scrolling=True)

    # Navigation
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    new_col, _, back_col = st.columns([1, 2, 1])
    with new_col:
        if st.button("🔄 New Project", key="btn_step3_new", use_container_width=True):
            reset_pipeline()
            st.rerun()
    with back_col:
        if st.button("← 返回修改", key="btn_step3_back", use_container_width=True):
            st.session_state.results = {}
            st.session_state.step = 2
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown(f'<p class="footer anim-8">sLoth rAdio · Title Studio · v{__version__}</p>',
            unsafe_allow_html=True)
