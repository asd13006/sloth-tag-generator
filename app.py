import streamlit as st
import time
from PIL import Image
import io

# ==========================================
# 1. 頁面設定與全域暗黑美學 CSS
# ==========================================
st.set_page_config(page_title="YouTube Title Studio",
                   page_icon="🤖", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    
    .block-container { padding-top: 2rem; max-width: 1150px !important; }

    @keyframes gradient-text { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .ai-title { font-weight: 900; font-size: 42px; text-align: center; background: linear-gradient(270deg, #00E676, #00ffcc, #b026ff, #00E676); background-size: 300% 300%; animation: gradient-text 4s ease infinite; -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; letter-spacing: -1px;}
    .ai-subtitle { color: #8E8E93; font-size: 15px; text-align: center; margin-bottom: 40px; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 600; }

    @keyframes pulse-glow { 0% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); } 50% { box-shadow: 0 0 20px rgba(0, 255, 204, 0.8); } 100% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); } }
    
    .stApp > header {background-color: transparent !important;}

    .result-card { background-color: rgba(30, 30, 35, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 25px; margin-bottom: 25px; }
    .section-title { font-size: 17px; font-weight: 700; color: #00ffcc; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1.5px;}

    /* Sticky Bottom Bar */
    div[data-testid="stBottomBlockContainer"] {
        background: rgba(18, 18, 22, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 12px 24px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 終極 Markdown 階梯式排版 CSS
# ==========================================


def inject_hierarchy_card_css():
    st.markdown("""
<style>
    /* =========================================================
       Animated Gradient Border Keyframes
       ========================================================= */
    @keyframes border-glow {
        0%   { border-color: #00ffcc; box-shadow: 0 0 18px rgba(0, 255, 204, 0.25); }
        50%  { border-color: #b026ff; box-shadow: 0 0 22px rgba(176, 38, 255, 0.2); }
        100% { border-color: #00ffcc; box-shadow: 0 0 18px rgba(0, 255, 204, 0.25); }
    }

    /* =========================================================
       基礎卡片容器 — Glassmorphism Dark
       ========================================================= */
    button[data-testid="baseButton-secondary"]:has(h3), 
    button[data-testid="baseButton-primary"]:has(h3) {
        border-radius: 20px !important;
        padding: 28px 24px 24px !important;
        width: 100% !important;
        height: 100% !important;
        min-height: 270px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
        text-align: left !important;
        transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1) !important;
        white-space: pre-wrap !important;
        position: relative !important;
        overflow: hidden !important;
        cursor: pointer !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
    }

    /* --- 未選取狀態 (Secondary) — Frosted Glass --- */
    button[data-testid="baseButton-secondary"]:has(h3) {
        background: rgba(15, 15, 35, 0.55) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
    }
    
    /* 右上角漸層光暈（視覺錨點）— 三色交替 */
    div[data-testid="column"]:nth-child(3n+1) button[data-testid="baseButton-secondary"]:has(h3) { background-image: radial-gradient(ellipse at 95% -5%, rgba(176, 38, 255, 0.12), transparent 55%) !important; }
    div[data-testid="column"]:nth-child(3n+2) button[data-testid="baseButton-secondary"]:has(h3) { background-image: radial-gradient(ellipse at 95% -5%, rgba(0, 255, 204, 0.09), transparent 55%) !important; }
    div[data-testid="column"]:nth-child(3n+3) button[data-testid="baseButton-secondary"]:has(h3) { background-image: radial-gradient(ellipse at 95% -5%, rgba(255, 165, 50, 0.09), transparent 55%) !important; }

    /* 懸停效果 — 浮起 + 邊框亮化 + 發光陰影 */
    button[data-testid="baseButton-secondary"]:has(h3):hover {
        border-color: rgba(255, 255, 255, 0.18) !important;
        transform: translateY(-6px) scale(1.015) !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35), 0 0 20px rgba(0, 255, 204, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
    }

    /* --- 已選取狀態 (Primary) — 深海藍 + 動態漸變邊框 --- */
    button[data-testid="baseButton-primary"]:has(h3) {
        background: linear-gradient(155deg, rgba(10, 26, 54, 0.92), rgba(8, 14, 35, 0.95)) !important;
        border: 2px solid #00ffcc !important;
        animation: border-glow 3s ease-in-out infinite !important;
    }
    button[data-testid="baseButton-primary"]:has(h3):hover {
        transform: translateY(-6px) scale(1.015) !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35), 0 0 30px rgba(0, 255, 204, 0.2) !important;
    }

    /* =========================================================
       階梯式文字排版 — 增強間距與可讀性
       ========================================================= */

    /* [第一層 - 標記] h5: 編號 / Checkmark */
    button h5 {
        position: absolute !important;
        top: 20px !important;
        right: 20px !important;
        left: auto !important;
        color: rgba(255, 255, 255, 0.25) !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        margin: 0 !important;
        letter-spacing: 1.5px !important;
        font-family: 'Poppins', monospace !important;
    }
    /* 選中後：右上角發光綠色勾號 */
    button[data-testid="baseButton-primary"] h5 {
        color: #00ffcc !important;
        font-size: 20px !important;
        top: 18px !important;
        text-shadow: 0 0 12px rgba(0, 255, 204, 0.6) !important;
        filter: drop-shadow(0 0 4px rgba(0, 255, 204, 0.4)) !important;
    }

    /* [第一層 - 歌名] h3: 英文歌名 */
    button h3 {
        color: #F8FAFC !important;
        font-size: 20px !important;
        font-weight: 800 !important;
        margin: 6px 0 6px 0 !important;
        line-height: 1.2 !important;
        letter-spacing: -0.3px !important;
        width: 100% !important;
        padding-right: 36px !important;
    }

    /* [第二層 - 譯名] h4: 中文譯名 */
    button h4 {
        color: #A1A1AA !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        margin: 0 0 14px 0 !important;
        padding-bottom: 14px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        width: 100% !important;
        letter-spacing: 0.5px !important;
    }
    /* 選中後虛線變亮 */
    button[data-testid="baseButton-primary"] h4 {
        border-bottom: 1px solid rgba(0, 255, 204, 0.15) !important;
        color: #C4B5FD !important;
    }

    /* [第三層 - 英文意境] strong */
    button strong {
        color: #C9CDD3 !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        display: block !important;
        line-height: 1.65 !important;
        margin-bottom: 10px !important;
        width: 100% !important;
    }

    /* [第四層 - 中文意境] em — 左側線條裝飾 */
    button em {
        color: #636370 !important;
        font-size: 12.5px !important;
        font-style: normal !important;
        display: block !important;
        line-height: 1.6 !important;
        padding-left: 12px !important;
        border-left: 2px solid rgba(255, 255, 255, 0.06) !important;
        width: 100% !important;
        margin-top: 2px !important;
    }
    /* 選中後：左側線螢光 + 文字提亮 */
    button[data-testid="baseButton-primary"] em {
        border-left: 2px solid rgba(0, 255, 204, 0.4) !important;
        color: #8E8E93 !important;
    }
    /* 選中後：英文歌名微亮 */
    button[data-testid="baseButton-primary"] h3 {
        color: #FFFFFF !important;
        text-shadow: 0 0 20px rgba(0, 255, 204, 0.12) !important;
    }
    /* 選中後：英文意境提亮 */
    button[data-testid="baseButton-primary"] strong {
        color: #D1D5DB !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 初始化流水線狀態
# ==========================================
if "step" not in st.session_state:
    st.session_state.step = 1
if "song_data" not in st.session_state:
    st.session_state.song_data = []
if "selected_song_ids" not in st.session_state:
    st.session_state.selected_song_ids = []
if "concept_options" not in st.session_state:
    st.session_state.concept_options = []
if "selected_concept" not in st.session_state:
    st.session_state.selected_concept = None
if "final_results" not in st.session_state:
    st.session_state.final_results = {}


def next_step(): st.session_state.step += 1


def reset_pipeline():
    st.session_state.song_data = []
    st.session_state.selected_song_ids = []
    st.session_state.concept_options = []
    st.session_state.selected_concept = None
    st.session_state.final_results = {}
    st.session_state.step = 1


# ==========================================
# 頁面標題
# ==========================================
st.markdown("<div class='ai-title'>Title Studio</div>", unsafe_allow_html=True)
st.markdown("<div class='ai-subtitle'>Ultimate Hierarchy Mode • v14.0</div>",
            unsafe_allow_html=True)

progress_val = (st.session_state.step - 1) / 3
st.progress(progress_val)
st.write("")

# ==========================================
# Pipeline Step 1: 階梯式排版原生卡片
# ==========================================
if st.session_state.step == 1:

    if not st.session_state.song_data:
        st.markdown("### 🎛️ Stage 1: Music Ideation")
        st.markdown(
            "<span style='color:#A1A1AA; font-size:14px;'>一鍵生成 20 首極具詩意、充滿感官溫暖嘅中英歌名同意境。</span>", unsafe_allow_html=True)
        if st.button("🪄 生成 20 首 Aesthetic 歌單", type="primary", use_container_width=True):
            with st.spinner("AI 正在孵化音樂靈感..."):
                time.sleep(1.2)
                mock_songs = [
                    {"id": 1, "en_title": "Soft Landing", "zh_title": "柔軟的著陸",
                        "en_theme": "Sinking into a chair, feeling your body remember how to let go.", "zh_theme": "沉入椅子，感受身體重新記起如何放手。"},
                    {"id": 2, "en_title": "Golden Hour Drift", "zh_title": "金色時光漫遊",
                        "en_theme": "Warm light painting the walls as the afternoon melts away.", "zh_theme": "暖光漆在牆上，整個下午正在融化。"},
                    {"id": 3, "en_title": "Paper Moon Lullaby", "zh_title": "紙月亮搖籃曲",
                        "en_theme": "A bedside lamp glowing softly, pages turning themselves.", "zh_theme": "床頭燈柔柔地亮著，書頁自己在翻動。"},
                    {"id": 4, "en_title": "Rainy Window Theatre", "zh_title": "雨窗小劇場",
                        "en_theme": "Watching raindrops race down the glass, picking your champion.", "zh_theme": "看雨滴在玻璃上賽跑，默默為牠打氣。"},
                    {"id": 5, "en_title": "Midnight Pour-Over", "zh_title": "午夜手沖",
                        "en_theme": "The quiet ritual of coffee at 2 AM, steam curling upward.", "zh_theme": "凌晨兩點沖咖啡的安靜儀式，蒸氣向上捲曲。"},
                    {"id": 6, "en_title": "Wool Socks Morning", "zh_title": "毛襪的早晨",
                        "en_theme": "Sliding across wooden floors in thick socks, no plans today.", "zh_theme": "穿著厚毛襪在木地板上滑行，今天沒有計劃。"},
                    {"id": 7, "en_title": "Fog & Honey", "zh_title": "霧與蜂蜜",
                        "en_theme": "Morning fog dissolving as you stir honey into warm milk.", "zh_theme": "晨霧散去的時候，你正把蜂蜜攪進溫牛奶裡。"},
                    {"id": 8, "en_title": "Last Train Home", "zh_title": "末班車歸途",
                        "en_theme": "Leaning against the window, city lights blurring into streaks.", "zh_theme": "靠在車窗上，城市燈火糊成一道道光痕。"},
                    {"id": 9, "en_title": "Rooftop Satellite", "zh_title": "天台衛星",
                        "en_theme": "Sitting on the rooftop, pretending the stars are listening.", "zh_theme": "坐在天台上，假裝星星們都在聽。"},
                    {"id": 10, "en_title": "Bookshop Rain", "zh_title": "書店裡的雨",
                        "en_theme": "Trapped in a bookshop by sudden rain, and not minding at all.", "zh_theme": "被突如其來的雨困在書店裡，卻一點也不介意。"},
                    {"id": 11, "en_title": "Velvet Afternoon", "zh_title": "絲絨午後",
                        "en_theme": "Sunlight pooling on unmade sheets, dust dancing slowly.", "zh_theme": "陽光灑在沒摺的床單上，灰塵在慢慢跳舞。"},
                    {"id": 12, "en_title": "Laundry Day Blues", "zh_title": "洗衣日藍調",
                        "en_theme": "The hypnotic tumble of clothes in a dryer, warmth on your face.", "zh_theme": "衣服在烘乾機裡催眠般翻滾，暖氣撲在臉上。"},
                    {"id": 13, "en_title": "Tangerine Dream", "zh_title": "橘子味的夢",
                        "en_theme": "Peeling a tangerine in silence, the scent filling the room.", "zh_theme": "安靜地剝一顆橘子，香氣漫滿整個房間。"},
                    {"id": 14, "en_title": "3 AM Skyline", "zh_title": "凌晨三點的天際線",
                        "en_theme": "The city is asleep but the lights are still on, humming softly.", "zh_theme": "城市睡著了但燈還亮著，發出輕柔的嗡嗡聲。"},
                    {"id": 15, "en_title": "Cat Nap Atlas", "zh_title": "貓咪午睡地圖",
                        "en_theme": "Following a cat's logic: sleep where the sunbeam lands.", "zh_theme": "跟著貓的邏輯：陽光照到哪裏就睡哪裏。"},
                    {"id": 16, "en_title": "Cinnamon Static", "zh_title": "肉桂色的雜訊",
                        "en_theme": "Old radio crackling in a kitchen that smells like baking.", "zh_theme": "老收音機在飄著烘焙香氣的廚房裡沙沙響。"},
                    {"id": 17, "en_title": "Slow Dissolve", "zh_title": "緩慢溶解",
                        "en_theme": "Sugar cube sinking into tea, thoughts sinking into nothing.", "zh_theme": "方糖沉入茶裡，思緒沉入虛無。"},
                    {"id": 18, "en_title": "Window Seat Poet", "zh_title": "靠窗詩人",
                        "en_theme": "Scribbling half-thoughts on a napkin, watching people pass by.", "zh_theme": "在餐巾紙上寫下半句想法，看行人路過。"},
                    {"id": 19, "en_title": "Cloud Pillow", "zh_title": "雲朵枕頭",
                        "en_theme": "That perfect moment when the pillow is cool on both sides.", "zh_theme": "枕頭兩面都是涼的，那個完美瞬間。"},
                    {"id": 20, "en_title": "Vinyl Sunset", "zh_title": "黑膠唱片的日落",
                        "en_theme": "Needle on the record, sun going down, nowhere else to be.", "zh_theme": "唱針落在唱片上，太陽正在下山，哪裡都不用去。"},
                ]
                st.session_state.song_data = mock_songs
                st.rerun()
    else:
        inject_hierarchy_card_css()
        st.markdown("### 🎛️ Stage 1: Select Your Aesthetic Songs")
        st.markdown(
            "<span style='color:#71717A; font-size:13px; letter-spacing:0.5px;'>點擊卡片選取歌曲 · 可多選 · 選中卡片會發光</span>", unsafe_allow_html=True)
        st.write("")

        cols = st.columns(3, gap="medium")

        for idx, song in enumerate(st.session_state.song_data):
            target_col = cols[idx % 3]
            is_selected = song['id'] in st.session_state.selected_song_ids

            btn_type = "primary" if is_selected else "secondary"
            # 狀態標記：選中顯示 ✅，未選中顯示 01, 02 數字
            sel_icon = "✅" if is_selected else f"{song['id']:02d}"

            with target_col:
                # 🔥 利用 Markdown 標籤精準控制排版層次
                # h5: 編號/勾號
                # h3: 英文歌名 (大字加粗)
                # h4: 中文譯名 (細灰字 + 虛線底)
                # strong: 英文意境
                # em: 中文意境 (縮進)
                card_content = f"""##### {sel_icon}
### {song['en_title']}
#### {song['zh_title']}
**{song['en_theme']}**
*{song['zh_theme']}*"""

                clicked = st.button(
                    card_content, key=f"btn_{song['id']}", type=btn_type, use_container_width=True)
                if clicked:
                    if song['id'] in st.session_state.selected_song_ids:
                        st.session_state.selected_song_ids.remove(song['id'])
                    else:
                        st.session_state.selected_song_ids.append(song['id'])
                    st.rerun()

        # Sticky Bottom Action Bar
        with st.bottom():
            scol1, scol2, scol3, scol4 = st.columns([3, 1.2, 1.2, 4])
            with scol1:
                st.markdown(
                    f"<div style='color:#FFFFFF; font-size:15px; font-weight:600; padding-top:12px;'>Selected: <span style='color:#00ffcc; font-size:22px; font-weight:900;'>{len(st.session_state.selected_song_ids)}</span> / {len(st.session_state.song_data)}</div>", unsafe_allow_html=True)
            with scol2:
                if st.button("全選", type="secondary", use_container_width=True):
                    st.session_state.selected_song_ids = [
                        s['id'] for s in st.session_state.song_data]
                    st.rerun()
            with scol3:
                if st.button("清空", type="secondary", use_container_width=True):
                    st.session_state.selected_song_ids = []
                    st.rerun()
            with scol4:
                if st.button("確認並前往下一步 ➡️", type="primary", use_container_width=True):
                    if not st.session_state.selected_song_ids:
                        st.warning("⚠️ 請至少點擊選取一首歌曲！")
                    else:
                        next_step()
                        st.rerun()

# ==========================================
# Pipeline Step 2: Visual Concept
# ==========================================
elif st.session_state.step == 2:
    st.markdown("### 🎬 Stage 2: Visual Concept")

    # 顯示已選歌曲摘要
    selected_songs = [s for s in st.session_state.song_data if s['id']
                      in st.session_state.selected_song_ids]
    song_names = "、".join([s['zh_title'] for s in selected_songs[:5]])
    if len(selected_songs) > 5:
        song_names += f"⋯等 {len(selected_songs)} 首"
    st.markdown(
        f"<div class='result-card'><div class='section-title'>已選歌曲</div><span style='color:#D1D1D6;'>{song_names}</span></div>", unsafe_allow_html=True)

    with st.container(border=True):
        vibe = st.text_input("自定義時間與氛圍（留空則 AI 隨機構思）",
                             placeholder="凌晨 3 點的微雨、暖燈下的黑膠唱片...")
        if st.button("🧠 AI 構思故事方向", type="primary", use_container_width=True):
            with st.spinner("AI 正在根據你的歌單構思視覺意境..."):
                time.sleep(1.5)
                # Mock：根據 vibe 輸入動態生成不同選項
                if vibe and "雨" in vibe:
                    st.session_state.concept_options = [
                        "☔ 微雨的窗邊放空 | Spacing out by the rainy window — 雨滴沿著玻璃蜿蜒而下，你蜷縮在毛毯裡",
                        "🌧️ 雨後街道的霓虹倒影 | Neon reflections on wet streets — 積水映照出整個城市的色彩",
                        "🌿 雨中陽台的綠意 | Balcony greens in the rain — 植物們在雨裡安靜地呼吸",
                    ]
                elif vibe and ("咖啡" in vibe or "coffee" in vibe.lower()):
                    st.session_state.concept_options = [
                        "☕ 暖光下的手沖咖啡 | Pour-over coffee in warm light — 熱水緩緩注入濾杯，香氣蔓延",
                        "🫖 深巷裡的老咖啡館 | Hidden café in the alley — 木質吧台上的咖啡漬是歲月的印記",
                        "🌅 窗台上冷掉的拿鐵 | Forgotten latte by the window — 拉花已經融化，但窗外更好看",
                    ]
                else:
                    st.session_state.concept_options = [
                        "☔ 微雨的窗邊放空 | Spacing out by the rainy window — 世界變得安靜，只剩下雨聲和你的呼吸",
                        "☕ 暖光下的手沖咖啡 | Pour-over coffee in warm light — 蒸氣緩緩上升，時間彷彿凝固了",
                        "🌙 深夜安靜的書檯 | Quiet study desk at midnight — 檯燈圈出一個只屬於你的小宇宙",
                    ]
                st.rerun()

    if st.session_state.concept_options:
        st.write("")
        st.markdown("<div class='section-title'>選擇一個故事方向</div>",
                    unsafe_allow_html=True)
        sel_concept = st.radio(
            "Story Direction", st.session_state.concept_options, label_visibility="collapsed")
        st.write("")
        col_back, col_next = st.columns(2)
        if col_back.button("⬅️ 返回", type="secondary", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
        if col_next.button("進入下一步 ➡️", type="primary", use_container_width=True):
            st.session_state.selected_concept = sel_concept
            next_step()
            st.rerun()

# ==========================================
# Pipeline Step 3: Assets & SEO Prep
# ==========================================
elif st.session_state.step == 3:
    st.markdown("### 🖼️ Stage 3: Assets & SEO Prep")
    st.markdown("<span style='color:#A1A1AA; font-size:14px;'>結合你的歌單與視覺意境，一次過生成故事、標題與 Tags。</span>",
                unsafe_allow_html=True)

    # 顯示上游資料摘要
    selected_songs = [s for s in st.session_state.song_data if s['id']
                      in st.session_state.selected_song_ids]
    concept_display = st.session_state.selected_concept or "未選擇"
    st.markdown(f"""<div class='result-card'>
        <div class='section-title'>創作素材</div>
        <p style='color:#D1D1D6; margin:4px 0;'>🎵 已選 <span style='color:#00ffcc; font-weight:700;'>{len(selected_songs)}</span> 首歌</p>
        <p style='color:#D1D1D6; margin:4px 0;'>🎬 意境：<span style='color:#00ffcc;'>{concept_display}</span></p>
    </div>""", unsafe_allow_html=True)

    # 可選上傳封面圖
    uploaded_img = st.file_uploader("📎 上傳封面圖（可選，AI 會參考圖片來寫故事）", type=[
                                    "png", "jpg", "jpeg", "webp"])
    if uploaded_img:
        img = Image.open(uploaded_img)
        st.image(img, caption="已上傳的封面圖", use_container_width=True)

    st.write("")

    # 手動觸發生成
    if not st.session_state.final_results:
        if st.button("🚀 啟動全線終極生成", type="primary", use_container_width=True):
            with st.status("⚙️ AI 正在全力運算中...", expanded=True) as status:
                st.write("📝 生成 300 字慵懶感官長故事...")
                time.sleep(0.8)
                st.write("💬 生成帶 Emoji 對話短故事...")
                time.sleep(0.6)
                st.write("🏷️ 生成 5 個高 CTR YouTube 標題...")
                time.sleep(0.6)
                st.write("🔖 生成 490 字元極限流量 Tags...")
                time.sleep(0.5)

                # Mock 四大輸出
                first_song = selected_songs[0] if selected_songs else {
                    "en_title": "Soft Landing", "zh_title": "柔軟的著陸"}

                st.session_state.final_results = {
                    "long_story": (
                        f"凌晨兩點半，窗外的雨終於慢了下來。你把毛毯拉到下巴，聽見遠處有人在彈鋼琴。"
                        f"那旋律像是從記憶深處飄來的，帶著肉桂和舊書的味道。桌上的咖啡已經涼了，"
                        f"但你不想動——因為此刻的溫度剛剛好。窗台上的多肉植物在月光下投射出小小的影子，"
                        f"像是在跳一支只有自己看得見的舞。你想起那天下午，陽光從百葉窗的縫隙灑進來，"
                        f"把整個房間染成了蜂蜜色。那時候你也在聽這首歌——{first_song['zh_title']}。"
                        f"空氣裡有洗好的床單的味道，有遠處傳來的電車聲，有貓咪踩在紙箱上的沙沙聲。"
                        f"你閉上眼睛，感覺自己正在慢慢融化成這個房間的一部分。"
                        f"沒有要去的地方，沒有要回的訊息，只有呼吸，只有此刻。"
                        f"窗簾被風輕輕吹起，像在對你說：留下來吧，這裡很安全。"
                        f"於是你留下來了。在這個屬於凌晨的小宇宙裡，讓音樂帶你去那個不需要地圖的地方。"
                    ),
                    "short_story": (
                        f"🌙 「欸，你有冇試過凌晨兩點突然好想飲嘢？」\n\n"
                        f"☕ 「有啊，我上次半夜爬起身沖咖啡，然後坐喺窗邊聽歌聽到天光。」\n\n"
                        f"🎵 「聽咩歌？」\n\n"
                        f"🎧 「{first_song['en_title']}。嗰種感覺好似⋯成個世界靜晒，淨係得你同音樂。」\n\n"
                        f"🐱 「然後隻貓就跳上你大腿？」\n\n"
                        f"😂 「你點知㗎！佢仲踩咗我杯咖啡添，不過嗰一刻真係好治癒。」\n\n"
                        f"✨ 「呢啲就係生活俾你嘅小禮物啦。」"
                    ),
                    "titles": [
                        f"🌙 凌晨兩點的溫柔 | {first_song['en_title']} — 3 Hour Lofi Mix for Late Night Healing",
                        f"☕ 把失眠變成禮物 | Midnight {first_song['en_title']} — Calm Lofi Beats to Breathe & Relax",
                        f"🐱 貓咪都睡了只剩我和音樂 | {first_song['en_title']} — Soft Lofi for Quiet Souls",
                        f"🌧️ 雨聲 × Lofi × 一杯涼掉的咖啡 | {first_song['en_title']} — Aesthetic Chill Mix",
                        f"✨ 致每一個還醒著的溫柔靈魂 | {first_song['en_title']} — 3Hr Lofi Radio for Night Owls",
                    ],
                    "tags": (
                        f"lofi,lofi hip hop,chill beats,study music,late night lofi,"
                        f"{first_song['en_title'].lower().replace(' ', '')},治癒音樂,深夜音樂,"
                        f"lofi mix,lofi radio,chill lofi,beats to relax,beats to study,"
                        f"lofi 2026,aesthetic lofi,cozy lofi,rainy lofi,midnight lofi,"
                        f"lofi playlist,soft lofi,warm lofi,lofi cafe,coffee lofi,"
                        f"sloth radio,樹懶電台,讀書音樂,放鬆音樂,助眠音樂,"
                        f"chill hop,lo-fi,lofi chill,japanese lofi,korean lofi,"
                        f"bedroom lofi,night owl music,3am music,healing music,"
                        f"comfort music,ambient lofi,piano lofi,guitar lofi,"
                        f"rain and lofi,cozy bedroom,late night vibes,alone time music,"
                        f"溫柔音樂,失眠音樂,凌晨歌單,深夜電台,慵懶音樂,貓咪音樂"
                    ),
                }
                status.update(label="✅ 全線生成完畢！",
                              state="complete", expanded=False)
            st.rerun()
    else:
        st.markdown(
            "<div style='color:#00ffcc; font-size:15px; font-weight:700; margin:12px 0;'>✅ 內容已生成完畢</div>", unsafe_allow_html=True)
        st.write("")
        col_back, col_dash = st.columns(2)
        if col_back.button("⬅️ 返回重新構思", type="secondary", use_container_width=True):
            st.session_state.final_results = {}
            st.session_state.step = 2
            st.rerun()
        if col_dash.button("查看 Dashboard 🏆", type="primary", use_container_width=True):
            next_step()
            st.rerun()

# ==========================================
# Pipeline Step 4: Final Dashboard
# ==========================================
elif st.session_state.step == 4:
    st.markdown("### 🎉 Stage 4: Final Dashboard")
    st.markdown("<span style='color:#A1A1AA; font-size:14px;'>所有成品已就緒，直接 Copy & Paste 到 YouTube Studio 發佈！</span>", unsafe_allow_html=True)
    st.write("")

    results = st.session_state.final_results

    # --- 長故事 ---
    st.markdown("<div class='section-title'>📝 300 字慵懶感官長故事</div>",
                unsafe_allow_html=True)
    st.markdown(
        f"<div class='result-card'><p style='color:#D1D1D6; line-height:1.8; font-size:15px;'>{results.get('long_story', '')}</p></div>", unsafe_allow_html=True)
    st.code(results.get("long_story", ""), language=None)

    st.write("")

    # --- 短故事 ---
    st.markdown("<div class='section-title'>💬 帶 Emoji 生活化對話短故事</div>",
                unsafe_allow_html=True)
    st.markdown(
        f"<div class='result-card' style='white-space:pre-wrap;'><p style='color:#D1D1D6; line-height:1.9; font-size:15px;'>{results.get('short_story', '')}</p></div>", unsafe_allow_html=True)
    st.code(results.get("short_story", ""), language=None)

    st.write("")

    # --- 5 個 YouTube 標題 ---
    st.markdown("<div class='section-title'>🏷️ 5 個高 CTR YouTube 標題</div>",
                unsafe_allow_html=True)
    titles = results.get("titles", [])
    for i, title in enumerate(titles, 1):
        st.markdown(f"""<div class='result-card' style='padding:16px 20px; margin-bottom:10px;'>
            <span style='color:#00ffcc; font-weight:800; margin-right:10px;'>#{i}</span>
            <span style='color:#FFFFFF; font-size:15px; font-weight:600;'>{title}</span>
        </div>""", unsafe_allow_html=True)
    titles_text = "\n".join([f"{i}. {t}" for i, t in enumerate(titles, 1)])
    st.code(titles_text, language=None)

    st.write("")

    # --- Tags ---
    tags_str = results.get("tags", "")
    tags_len = len(tags_str)
    st.markdown(
        f"<div class='section-title'>🔖 極限流量 Tags（{tags_len} / 500 字元）</div>", unsafe_allow_html=True)
    # 顯示 tag pills
    tag_list = [t.strip() for t in tags_str.split(",") if t.strip()]
    pills_html = "".join(
        [f"<span style='display:inline-block; background:rgba(0,255,204,0.1); border:1px solid rgba(0,255,204,0.3); border-radius:20px; padding:4px 12px; margin:3px 4px; color:#00ffcc; font-size:13px; font-weight:500;'>{tag}</span>" for tag in tag_list])
    st.markdown(
        f"<div class='result-card'>{pills_html}</div>", unsafe_allow_html=True)
    st.code(tags_str, language=None)

    st.write("")
    st.divider()
    st.write("")

    if st.button("🔄 重置全線流程，開始下一條片", type="secondary", use_container_width=True):
        reset_pipeline()
        st.rerun()

st.write("")
st.markdown("<div style='text-align: center; color: #555; font-size: 12px; margin-top: 50px; margin-bottom: 100px;'>sLoth rAdio • YouTube Title Studio • Demo Mode</div>", unsafe_allow_html=True)
