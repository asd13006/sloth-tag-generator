"""
sLoth Title Studio — Glass Morphism 2.0 Demo
Neon Frost 配色 · Sidebar + Main Content · 全面動畫系統
純視覺展示（假資料），用於確認設計方向。
"""

import streamlit as st
from demo_styles import inject_demo_css

# ═══════════════════════════════════════════
# Page Config
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="sLoth Title Studio",
    page_icon="🦥",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_demo_css()

# ═══════════════════════════════════════════
# 假資料 (Mock Data)
# ═══════════════════════════════════════════

MOCK_TITLES_EN = [
    '"Midnight Drift… Lofi Jazz for Late Night Coding Sessions 🌙 🎹"',
    '"Velvet Sunrise… Chill R&B Beats for Morning Coffee Rituals ☀️ 🎶"',
    '"Neon Rain… Synthwave Lofi for Rainy Window Gazing 🌧️ 💜"',
    '"Paper Lanterns… Acoustic Lofi for Peaceful Study Vibes 📚 🏮"',
    '"Cloud Walker… Ambient Jazz for Dreamy Sunday Afternoons ☁️ 🎷"',
]

MOCK_TITLES_ZH = [
    '"午夜漂流… 深夜寫程式的 Lofi 爵士 🌙 🎹"',
    '"天鵝絨日出… 晨間咖啡時光的 Chill R&B 節拍 ☀️ 🎶"',
    '"霓虹雨… 窗邊聽雨的 Synthwave Lofi 🌧️ 💜"',
    '"紙燈籠… 靜心讀書的 Acoustic Lofi 📚 🏮"',
    '"漫步雲端… 慵懶週日午後的 Ambient 爵士 ☁️ 🎷"',
]

MOCK_TAGS = (
    "lofi hip hop, chill beats, study music, relaxing music, lofi jazz, "
    "coding music, ambient, lo-fi, chillhop, jazz hop, late night vibes, "
    "midnight lofi, calm music, focus music, deep focus, work music, "
    "coffee shop music, rainy day, aesthetic, soft music, "
    "lofi radio, beats to relax, beats to study, chill vibes, "
    "instrumental, piano lofi, guitar lofi, smooth jazz, neo soul, "
    "bedroom pop, downtempo, trip hop, mellow beats, cozy music, "
    "sleep music, dream pop, night drive, city pop lofi"
)

MOCK_LONG_STORY = """The city breathes differently after midnight. Streetlights paint golden halos on wet pavement, and somewhere between the hum of a distant train and the gentle tap of rain against glass, you find a pocket of silence that belongs only to you.

You press play. The first notes drift in — a dusty vinyl crackle, then piano keys that feel like they've been waiting all night just for this moment. The bass arrives next, warm and round, settling into a groove so comfortable it could be a second heartbeat.

This is the hour when ideas flow without friction, when the cursor moves across the screen not because it has to, but because the music has unlocked something quiet and persistent inside you. Track after track, the playlist becomes a conversation between the night and your focus — jazz chords whispering possibilities, lofi textures softening the edges of every deadline.

Let the rain keep falling. Let the coffee grow cold. Some of the best work happens in these stolen hours, wrapped in sound that understands the beauty of staying up just a little longer."""

MOCK_SHORT_STORY = """🌙 Midnight Drift — A Lofi Jazz Experience

When the world sleeps, your best work begins. This collection weaves dusty piano loops with smooth jazz undertones, creating the perfect backdrop for late-night creators, coders, and dreamers. Press play, dim the lights, and let the music carry you through the quiet hours."""

MOCK_TRACKLIST = [
    {"en": "Midnight Drift", "zh": "午夜漂流", "theme_en": "Late Night Piano Jazz", "theme_zh": "深夜鋼琴爵士"},
    {"en": "Velvet Sunrise", "zh": "天鵝絨日出", "theme_en": "Morning Coffee Chill", "theme_zh": "晨間咖啡放鬆"},
    {"en": "Neon Rain", "zh": "霓虹雨", "theme_en": "Synthwave Rainy Mood", "theme_zh": "合成波雨天氛圍"},
    {"en": "Paper Lanterns", "zh": "紙燈籠", "theme_en": "Acoustic Study Session", "theme_zh": "聲學讀書時光"},
    {"en": "Cloud Walker", "zh": "漫步雲端", "theme_en": "Dreamy Ambient Jazz", "theme_zh": "夢幻環境爵士"},
]


# ═══════════════════════════════════════════
# Session State
# ═══════════════════════════════════════════
if "nav" not in st.session_state:
    st.session_state.nav = "generate"
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "loading" not in st.session_state:
    st.session_state.loading = False
# Wizard step (1=Content Selection, 2=Material Lab, 3=Results)
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
# Selected archetypes in Step 1
if "selected_archetypes" not in st.session_state:
    st.session_state.selected_archetypes = []
# Target audience in Step 2
if "target_audience" not in st.session_state:
    st.session_state.target_audience = "gen_z"


def go_step(n: int):
    """切換 wizard 步驟並 rerun。"""
    st.session_state.wizard_step = n
    st.session_state.nav = "generate"
    if n < 3:
        st.session_state.show_results = False
        st.session_state.loading = False
    st.rerun()


def reset_wizard():
    """重置 wizard 到 Step 1。"""
    st.session_state.wizard_step = 1
    st.session_state.selected_archetypes = []
    st.session_state.show_results = False
    st.session_state.loading = False
    st.session_state.target_audience = "gen_z"
    st.session_state.nav = "generate"
    st.rerun()


# ═══════════════════════════════════════════
# Helper: HTML wrapper with animation class
# ═══════════════════════════════════════════
def anim(html: str, n: int = 1) -> None:
    """用 anim-N class 包裹 HTML，產生遞延進場動畫。"""
    st.markdown(f'<div class="anim-{n}">{html}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════
_WIZARD_STEPS = [
    ("💡", "Concept", 1),
    ("📝", "Draft", 2),
    ("✨", "Refine", None),   # placeholder — not clickable yet
    ("🚀", "Generate", 3),
]

with st.sidebar:
    # Brand
    st.markdown("""
        <div style="padding: 8px 0 4px;">
            <p class="sb-brand">Title Studio</p>
            <p class="sb-subtitle">創作精靈</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── Wizard Mode ──
    st.markdown('<p class="sb-section-label">Wizard Mode</p>', unsafe_allow_html=True)

    for icon, label, step_num in _WIZARD_STEPS:
        if step_num is not None:
            is_active = (st.session_state.nav == "generate" and
                         st.session_state.wizard_step == step_num)
            if st.button(
                f"{icon}  {label}",
                key=f"nav_wiz_{label.lower()}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                go_step(step_num)
        else:
            # Refine placeholder — disabled style
            st.button(
                f"{icon}  {label}",
                key=f"nav_wiz_{label.lower()}",
                type="secondary",
                use_container_width=True,
                disabled=True,
            )

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── 工具 ──
    st.markdown('<p class="sb-section-label">Tools</p>', unsafe_allow_html=True)

    if st.button("🫘  豆包工具", key="nav_doubao",
                 type="primary" if st.session_state.nav == "doubao" else "secondary",
                 use_container_width=True):
        st.session_state.nav = "doubao"
        st.rerun()

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── 設定 ──
    st.markdown('<p class="sb-section-label">Configure</p>', unsafe_allow_html=True)

    if st.button("🔑  API 連線", key="nav_api",
                 type="primary" if st.session_state.nav == "api" else "secondary",
                 use_container_width=True):
        st.session_state.nav = "api"
        st.rerun()

    if st.button("📊  歷史記錄", key="nav_history",
                 type="primary" if st.session_state.nav == "history" else "secondary",
                 use_container_width=True):
        st.session_state.nav = "history"
        st.rerun()

    if st.button("⚙️  偏好設定", key="nav_settings",
                 type="primary" if st.session_state.nav == "settings" else "secondary",
                 use_container_width=True):
        st.session_state.nav = "settings"
        st.rerun()

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── 帳戶 ──
    st.markdown('<p class="sb-section-label">Account</p>', unsafe_allow_html=True)

    # Status indicator
    st.markdown("""
        <div style="padding: 4px 14px; margin-bottom: 8px;">
            <span class="status-dot connected"></span>
            <span class="status-text">Gemini 2.5 Flash 已連線</span>
        </div>
    """, unsafe_allow_html=True)

    if st.button("👤  個人檔案", key="nav_profile",
                 type="primary" if st.session_state.nav == "profile" else "secondary",
                 use_container_width=True):
        st.session_state.nav = "profile"
        st.rerun()

    # New Project button
    if st.button("🔄  New Project", key="nav_new_project",
                 type="secondary",
                 use_container_width=True):
        reset_wizard()

    # Footer
    st.markdown('<p class="sb-version">V-4 Singularity</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════

if st.session_state.nav == "generate":

    step = st.session_state.wizard_step

    # ═══════════════════════════════════════════
    # STEP 1 — Select Creative Archetype
    # ═══════════════════════════════════════════
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
        _ARCHETYPES = [
            ("titles",   "▶️", "YouTube Titles",
             "高 CTR 導向。運用心理觸發點與病毒式 metadata 分析。", "primary"),
            ("tags",     "🔍", "SEO Tags",
             "演算法精準映射，全球搜尋排名優勢與語義關聯。", "secondary"),
            ("stories",  "🎭", "Scenario Stories",
             "多分支敘事弧線——適用短影音、遊戲與沉浸式社群內容。", "primary"),
            ("playlist", "🎵", "Suno Playlist",
             "和聲提示 AI 音樂生成。打造風格、歌詞與曲式結構。", "secondary"),
        ]

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

        # Confirm button → Step 2
        st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
        col_spacer, col_btn = st.columns([3, 1])
        with col_btn:
            can_proceed = len(st.session_state.selected_archetypes) > 0
            if st.button(
                "確認選擇 →" if can_proceed else "請至少選擇一項",
                type="primary" if can_proceed else "secondary",
                use_container_width=True,
                disabled=not can_proceed,
                key="btn_step1_next",
            ):
                go_step(2)

    # ═══════════════════════════════════════════
    # STEP 2 — Material Lab (Input + Tuning)
    # ═══════════════════════════════════════════
    elif step == 2:
        # Header + progress bar
        selected_count = len(st.session_state.selected_archetypes)
        seg_html = ""
        for i in range(3):
            active = " active" if i < 2 else ""
            seg_html += f'<div class="step-seg{active}"></div>'

        anim(f"""
            <div class="wizard-header">
                <div class="left">
                    <h1>Material Lab</h1>
                    <p class="subtitle">為你的作品注入核心素材，校準創作引擎。已選 {selected_count} 個 Archetype。</p>
                </div>
                <div class="step-bar">
                    <div class="step-segments">{seg_html}</div>
                    <span class="step-counter">Step 02 / 03</span>
                </div>
            </div>
        """, 1)

        # Split pane: 7 input + 5 tuning
        col_input, col_tune = st.columns([7, 5], gap="large")

        # ── Left: Input Zone ──
        with col_input:
            anim('<p class="context-label">Context Synthesis</p>', 2)

            with st.container(key="input_glass"):
                user_context = st.text_area(
                    "核心素材輸入",
                    placeholder="貼上你的文案、腳本片段或創意提示…",
                    height=200,
                    key="input_context",
                    label_visibility="collapsed",
                )

            # Existing materials
            anim('<p class="context-label">已有材料（可選）</p>', 3)
            existing_titles = st.text_input(
                "已有標題",
                placeholder="貼上你目前想到的標題…",
                key="mat_titles",
            )
            existing_tags = st.text_input(
                "已有標籤",
                placeholder="貼上已有的 tags（逗號分隔）…",
                key="mat_tags",
            )

            # Gemini Visual Context
            st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
            label_col, badge_col = st.columns([4, 1])
            with label_col:
                anim('<p class="context-label">Gemini Visual Context</p>', 4)
            with badge_col:
                st.markdown('<span class="vision-badge">AI Vision Enabled</span>', unsafe_allow_html=True)

            uploaded = st.file_uploader(
                "上傳參考圖片",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key="img_upload",
                help="拖曳或點擊上傳，支援 PNG/JPG/WebP（最多 5 張）",
            )

        # ── Right: Tuning Terminal ──
        with col_tune:
            with st.container(key="tuning_terminal"):
                st.markdown("""
                    <div class="tuning-header">
                        <span class="tune-icon">🎛️</span>
                        <h3>Tuning Terminal</h3>
                    </div>
                    <p class="tuning-subtitle">校準輸出共鳴與目標諧波</p>
                """, unsafe_allow_html=True)

                # Tone Matrix slider
                st.markdown('<p class="tuner-label">Tone Matrix</p>', unsafe_allow_html=True)
                tone = st.slider(
                    "Tone",
                    0, 100, 72,
                    key="tone_slider",
                    label_visibility="collapsed",
                )
                tone_name = "Catchy" if tone < 33 else ("Formal" if tone < 66 else "Dramatic")
                st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:-8px; margin-bottom:16px;">
                        <div class="slider-labels">
                            <span>Catchy</span>
                        </div>
                        <span class="slider-value">{tone_name} // {tone}%</span>
                        <div class="slider-labels">
                            <span>Dramatic</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Style Variance slider
                st.markdown('<p class="tuner-label">Style Variance</p>', unsafe_allow_html=True)
                style_var = st.slider(
                    "Style",
                    0, 100, 42,
                    key="style_slider",
                    label_visibility="collapsed",
                )
                style_name = "Minimal" if style_var < 33 else ("Dynamic" if style_var < 66 else "Complex")
                st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:-8px; margin-bottom:16px;">
                        <div class="slider-labels">
                            <span>Minimal</span>
                        </div>
                        <span class="slider-value secondary">{style_name} // {style_var}%</span>
                        <div class="slider-labels">
                            <span>Complex</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Target Audience
                st.markdown('<p class="tuner-label">Target Audience Nucleus</p>', unsafe_allow_html=True)
                _AUDIENCES = [
                    ("gen_z", "Gen Z Tech"),
                    ("corporate", "Corporate"),
                    ("academic", "Academic"),
                    ("custom", "Custom"),
                ]
                aud_cols = st.columns(2)
                for idx, (aud_key, aud_label) in enumerate(_AUDIENCES):
                    with aud_cols[idx % 2]:
                        is_aud = st.session_state.target_audience == aud_key
                        if st.button(
                            f"{'◉ ' if is_aud else '○ '}{aud_label}",
                            key=f"aud_{aud_key}",
                            type="primary" if is_aud else "secondary",
                            use_container_width=True,
                        ):
                            st.session_state.target_audience = aud_key
                            st.rerun()

        # Action row: Back + Confirm
        st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
        back_col, _, confirm_col = st.columns([1, 2, 2])
        with back_col:
            if st.button("← Back", key="btn_step2_back", use_container_width=True):
                go_step(1)
        with confirm_col:
            if st.button("✨ Confirm Tuning →", type="primary",
                         use_container_width=True, key="btn_step2_next"):
                st.session_state.loading = True
                st.session_state.show_results = False
                st.session_state.wizard_step = 3
                st.rerun()

    # ═══════════════════════════════════════════
    # STEP 3 — Results Dashboard
    # ═══════════════════════════════════════════
    elif step == 3:

        # Loading state
        if st.session_state.loading:
            st.markdown("""
                <div class="glass" style="margin-top: 16px;">
                    <div class="loading-overlay">
                        <div class="loading-spinner"></div>
                        <div class="loading-text">V-4 Singularity 正在合成你的創意資產…</div>
                    </div>
                    <div class="skeleton skeleton-block" style="height:60px;"></div>
                    <div class="skeleton skeleton-line w-90"></div>
                    <div class="skeleton skeleton-line w-75"></div>
                    <div class="skeleton skeleton-line w-50"></div>
                </div>
            """, unsafe_allow_html=True)
            import time
            time.sleep(2)
            st.session_state.loading = False
            st.session_state.show_results = True
            st.rerun()

        # Result hero
        anim("""
            <div class="result-hero">
                <p class="result-label">Generation Complete</p>
                <h1>Celestial Results</h1>
                <p class="result-desc">V-4 Singularity 已將你的概念蒸餾為高效能創意資產。精準調校，最大化 CTR。</p>
            </div>
        """, 1)

        if st.session_state.show_results:
            selected = st.session_state.selected_archetypes

            # ── Titles Section ──
            if "titles" in selected:
                titles_cards = ""
                for i, (en, zh) in enumerate(zip(MOCK_TITLES_EN, MOCK_TITLES_ZH)):
                    if i == 0:
                        titles_cards += f"""
                            <div class="title-card-primary">
                                <span class="match-badge">MATCH: 98%</span>
                                <h2>{en}</h2>
                                <div style="font-size:13px; color:var(--text-muted); margin-bottom:12px;">{zh}</div>
                                <div class="actions">
                                    <button>Copy</button>
                                    <span class="dot">•</span>
                                    <button>Variations</button>
                                </div>
                            </div>
                        """
                    else:
                        viral = ["High", "Extreme", "Mid", "High"][i - 1]
                        titles_cards += f"""
                            <div class="title-card-secondary">
                                <h2>{en}</h2>
                                <div style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">{zh}</div>
                                <div class="viral-row">
                                    <span class="viral-label">Viral Potential: {viral}</span>
                                    <button class="copy-btn">📋</button>
                                </div>
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
                                    <button title="Copy All">📋</button>
                                    <button title="Download">⬇️</button>
                                </div>
                            </div>
                            {titles_cards}
                        </div>
                    </div>
                """, 2)

            # ── Tags Section ──
            if "tags" in selected:
                tags_list = [t.strip() for t in MOCK_TAGS.split(",")]
                pills_html = "".join(f'<span class="tag-pill">{t}</span>' for t in tags_list)
                char_count = len(MOCK_TAGS)

                anim(f"""
                    <div class="glass">
                        <div class="card-header">
                            <div class="card-icon purple">🏷️</div>
                            <span class="card-title">SEO Tags</span>
                            <span class="card-badge">{len(tags_list)} tags</span>
                        </div>
                        <div class="tag-cloud">{pills_html}</div>
                        <div class="tag-counter">{char_count} / 500 chars</div>
                    </div>
                """, 3)

            # ── Stories Section ──
            if "stories" in selected:
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    anim(f"""
                        <div class="glass-elevated">
                            <div class="card-header">
                                <div class="card-icon green">📖</div>
                                <span class="card-title">Long Story</span>
                                <span class="card-badge green">EN</span>
                            </div>
                            <div class="story-prose">{MOCK_LONG_STORY}</div>
                        </div>
                    """, 4)
                with col_s2:
                    anim(f"""
                        <div class="glass-elevated">
                            <div class="card-header">
                                <div class="card-icon purple">💬</div>
                                <span class="card-title">Short Story</span>
                                <span class="card-badge">EN</span>
                            </div>
                            <div class="story-prose">{MOCK_SHORT_STORY}</div>
                        </div>
                    """, 5)

            # ── Tracklist Section ──
            if "playlist" in selected:
                tracks_html = ""
                for i, t in enumerate(MOCK_TRACKLIST, 1):
                    tracks_html += f"""
                    <div class="track-row">
                        <span class="track-num">{i:02d}</span>
                        <div class="track-info">
                            <div class="track-title">{t['en']}</div>
                            <div class="track-sub">{t['zh']}</div>
                        </div>
                        <span class="track-theme">{t['theme_en']}</span>
                    </div>"""

                anim(f"""
                    <div class="glass">
                        <div class="card-header">
                            <div class="card-icon amber">🎵</div>
                            <span class="card-title">Suno Playlist</span>
                            <span class="card-badge">{len(MOCK_TRACKLIST)} tracks</span>
                        </div>
                        {tracks_html}
                    </div>
                """, 6)

            # ── Action Bar ──
            anim("""
                <div class="action-bar">
                    <div class="action-group">
                        <button class="action-bar-btn ghost">💾 Save to Library</button>
                        <button class="action-bar-btn ghost">🔗 Collaborate</button>
                    </div>
                    <div class="action-group">
                        <button class="action-bar-btn outlined">📄 Export TXT</button>
                        <button class="action-bar-btn outlined">📦 Export JSON</button>
                    </div>
                </div>
            """, 7)

            # Back to Step 2 or New Project
            st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
            new_col, _, back_col = st.columns([1, 2, 1])
            with new_col:
                if st.button("🔄 New Project", key="btn_step3_new", use_container_width=True):
                    reset_wizard()
            with back_col:
                if st.button("← Back to Lab", key="btn_step3_back", use_container_width=True):
                    go_step(2)

    # ── Footer ──
    st.markdown('<p class="footer anim-8">sLoth Title Studio · V-4 Singularity · Celestial Engine</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# DOUBAO TOOL (placeholder)
# ═══════════════════════════════════════════
elif st.session_state.nav == "doubao":
    anim("""
        <div class="hero-title">🫘 豆包工具</div>
        <div class="hero-desc">提取豆包無水印圖片與影片</div>
    """, 1)

    with st.container(key="doubao_glass"):
        st.text_input("輸入豆包分享連結", placeholder="https://www.douyin.com/...", key="doubao_url_input", label_visibility="collapsed")

    col1, col2 = st.columns(2)
    with col1:
        st.button("🖼️ 提取圖片", use_container_width=True)
    with col2:
        st.button("🎬 提取影片", use_container_width=True)

    # Placeholder result
    anim("""
        <div class="glass-elevated" style="margin-top: 16px;">
            <div class="card-header">
                <div class="card-icon purple">🎬</div>
                <span class="card-title">影片結果</span>
                <span class="card-badge">HD</span>
            </div>
            <div style="color: var(--text-muted); font-size: 14px; padding: 20px 0; text-align: center;">
                貼上連結並點擊提取按鈕開始
            </div>
        </div>
    """, 3)

    st.markdown('<p class="footer anim-4">sLoth Title Studio · 豆包工具</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# API SETTING (placeholder)
# ═══════════════════════════════════════════
elif st.session_state.nav == "api":
    anim("""
        <div class="hero-title">🔑 API 連線設定</div>
        <div class="hero-desc">設定 Google Gemini API Key 以啟用 AI 生成功能</div>
    """, 1)

    anim("""
        <div class="glass">
            <div class="card-header">
                <div class="card-icon green">🔗</div>
                <span class="card-title">連線狀態</span>
            </div>
            <div style="padding: 8px 0;">
                <span class="status-dot connected"></span>
                <span style="font-size:14px; color: var(--accent); font-weight:600;">已連線</span>
                <span style="font-size:13px; color: var(--text-muted); margin-left: 12px;">gemini-2.5-flash</span>
            </div>
        </div>
    """, 2)

    with st.container(key="api_glass"):
        st.text_input("API Key", value="AIza••••••••••••••••••••••••", type="password", key="api_key_input")
        col1, col2 = st.columns(2)
        with col1:
            st.button("✅ 驗證 Key", type="primary", use_container_width=True)
        with col2:
            st.button("🗑️ 清除 Key", use_container_width=True)

    st.markdown('<p class="footer anim-4">sLoth Title Studio · API 設定</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# HISTORY (placeholder)
# ═══════════════════════════════════════════
elif st.session_state.nav == "history":
    anim("""
        <div class="hero-title">📊 歷史記錄</div>
        <div class="hero-desc">查看過去的生成記錄</div>
    """, 1)

    histories = [
        {"time": "2026-04-08 14:32", "title": "Midnight Drift… Lofi Jazz", "items": "5 titles · 38 tags · 2 stories · 5 tracks"},
        {"time": "2026-04-07 22:18", "title": "Velvet Sunrise… Chill R&B", "items": "5 titles · 42 tags · 2 stories"},
        {"time": "2026-04-06 09:45", "title": "Ocean Breeze… Ambient Lofi", "items": "5 titles · 35 tags · 1 story · 8 tracks"},
    ]

    for i, h in enumerate(histories, 2):
        anim(f"""
            <div class="glass" style="cursor: pointer; padding: 20px 24px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 15px; font-weight: 600; color: var(--text); margin-bottom: 4px;">{h['title']}</div>
                        <div style="font-size: 12px; color: var(--text-muted);">{h['items']}</div>
                    </div>
                    <div style="font-size: 11px; color: var(--text-muted); white-space: nowrap;">{h['time']}</div>
                </div>
            </div>
        """, i)

    st.markdown('<p class="footer anim-6">sLoth Title Studio · 歷史記錄</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# SETTINGS (placeholder)
# ═══════════════════════════════════════════
elif st.session_state.nav == "settings":
    anim("""
        <div class="hero-title">⚙️ 偏好設定</div>
        <div class="hero-desc">自訂預設生成參數與介面偏好</div>
    """, 1)

    anim("""
        <div class="glass">
            <div class="card-header">
                <div class="card-icon">🎨</div>
                <span class="card-title">預設偏好</span>
            </div>
        </div>
    """, 2)

    with st.container(key="settings_glass"):
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("預設語氣", ["Balanced", "Formal", "Casual", "Poetic"])
            st.selectbox("預設受眾", ["General", "Music Lovers", "Developers", "Students"])
        with col2:
            st.number_input("預設歌單數量", 3, 15, 5)
            st.selectbox("輸出語言", ["English + 繁體中文", "English Only", "繁體中文 Only"])

    st.markdown('<p class="footer anim-4">sLoth Title Studio · 偏好設定</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# PROFILE (placeholder)
# ═══════════════════════════════════════════
elif st.session_state.nav == "profile":
    anim("""
        <div class="hero-title">👤 個人檔案</div>
        <div class="hero-desc">帳戶資訊與使用統計</div>
    """, 1)

    anim("""
        <div class="glass">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="width:64px; height:64px; border-radius:50%; background: linear-gradient(135deg, var(--primary), var(--secondary)); display:flex; align-items:center; justify-content:center; font-size:28px; flex-shrink:0;">🦥</div>
                <div>
                    <div style="font-family: var(--font-display); font-size: 20px; color: var(--text);">Demo User</div>
                    <div style="font-size: 13px; color: var(--text-muted);">demo@sloth.studio</div>
                    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
                        <span class="chip chip-blue">12 次生成</span>
                        <span class="chip chip-purple">60 標題</span>
                        <span class="chip chip-green">已連線</span>
                    </div>
                </div>
            </div>
        </div>
    """, 2)

    anim("""
        <div class="glass-elevated">
            <div class="card-header">
                <div class="card-icon amber">📈</div>
                <span class="card-title">使用統計</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; text-align: center; padding: 8px 0;">
                <div>
                    <div style="font-family: var(--font-display); font-size: 28px; color: var(--primary);">12</div>
                    <div style="font-size: 11px; color: var(--text-muted); letter-spacing: 1px; text-transform: uppercase;">生成次數</div>
                </div>
                <div>
                    <div style="font-family: var(--font-display); font-size: 28px; color: var(--secondary);">60</div>
                    <div style="font-size: 11px; color: var(--text-muted); letter-spacing: 1px; text-transform: uppercase;">標題數量</div>
                </div>
                <div>
                    <div style="font-family: var(--font-display); font-size: 28px; color: var(--accent);">456</div>
                    <div style="font-size: 11px; color: var(--text-muted); letter-spacing: 1px; text-transform: uppercase;">Tags 產量</div>
                </div>
            </div>
        </div>
    """, 3)

    st.button("🔐 登出", use_container_width=True, key="btn_logout")

    st.markdown('<p class="footer anim-4">sLoth Title Studio · 個人檔案</p>', unsafe_allow_html=True)
