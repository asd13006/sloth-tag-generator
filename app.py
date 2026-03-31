import streamlit as st
import time

# ==========================================
# 1. 頁面設定與全域暗黑美學 CSS
# ==========================================
st.set_page_config(page_title="YouTube Title Studio", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    /* 引入高級字體 */
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600;700;800&family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    
    /* 調整主容器 Padding */
    .block-container { padding-top: 2rem; max-width: 1100px !important; }

    /* AI 漸變標題 */
    @keyframes gradient-text { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .ai-title { font-weight: 800; font-size: 42px; text-align: center; background: linear-gradient(270deg, #00E676, #00ffcc, #b026ff, #00E676); background-size: 300% 300%; animation: gradient-text 4s ease infinite; -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; letter-spacing: -1px;}
    .ai-subtitle { color: #8E8E93; font-size: 15px; text-align: center; margin-bottom: 40px; letter-spacing: 1px; text-transform: uppercase; font-weight: 500; }

    @keyframes pulse-glow { 0% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); } 50% { box-shadow: 0 0 20px rgba(0, 255, 204, 0.8); } 100% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); } }
    
    /* 底部 Sticky Action Bar 美化 */
    .stApp > header {background-color: transparent !important;}
    div.stActionButton { position: fixed; bottom: 0; left: 0; width: 100%; background-color: rgba(18, 18, 20, 0.9); backdrop-filter: blur(20px); border-top: 1px solid rgba(255, 255, 255, 0.08); padding: 18px 0; z-index: 1000; box-shadow: 0 -10px 30px rgba(0,0,0,0.3); }
    div.stActionButton > div { max-width: 1100px; margin: 0 auto; padding: 0 1.5rem; }

    /* 全域卡片設定 (用於 Tab 4 結果頁) */
    .result-card { background-color: rgba(30, 30, 35, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 25px; margin-bottom: 25px; transition: all 0.3s ease; }
    .result-card:hover { border-color: rgba(255,255,255,0.15); box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
    .section-title { font-size: 17px; font-weight: 700; color: #00ffcc; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1.5px; font-family: 'Inter', sans-serif;}
    .content-text { font-size: 15px; color: #E5E5EA; line-height: 1.7; font-weight: 400;}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Aesthetic 絲滑原生卡片 CSS 重生術
# ==========================================
def inject_aesthetic_native_card_css():
    st.markdown("""
<style>
    /* =========================================================
       針對卡片區域 (Step 1) 的獨立定義
       ========================================================= */
       
    /* 基礎卡片設定 (原生 Button 改造) */
    div[data-testid="column"] button[data-testid="baseButton-secondary"], 
    div[data-testid="column"] button[data-testid="baseButton-primary"] {
        border-radius: 16px !important;
        padding: 28px 24px 24px 24px !important; /* 增加頂部 Padding 給 ID */
        width: 100% !important;
        height: 100% !important;
        min-height: 220px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
        text-align: left !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        white-space: pre-wrap !important;
        position: relative !important; /* 為了 ID 定位 */
        overflow: visible !important;
    }

    /* --- 未選取狀態 (Secondary Button) --- */
    div[data-testid="column"] button[data-testid="baseButton-secondary"] {
        background-color: rgba(35, 35, 40, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    /* 懸停效果 */
    div[data-testid="column"] button[data-testid="baseButton-secondary"]:hover {
        border-color: rgba(0, 255, 204, 0.3) !important;
        background-color: rgba(40, 40, 45, 0.8) !important;
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 24px rgba(0, 255, 204, 0.1) !important;
    }

    /* --- 已選取狀態 (Primary Button) --- */
    div[data-testid="column"] button[data-testid="baseButton-primary"] {
        background-color: rgba(20, 35, 65, 0.8) !important;
        border: 2px solid #00ffcc !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.15) !important;
    }

    /* 已選取狀態嘅右上角 Checkmark 美化 */
    div[data-testid="column"] button[data-testid="baseButton-primary"]::after {
        content: '✓';
        position: absolute;
        top: 18px;
        right: 22px;
        color: #00ffcc;
        font-size: 28px;
        font-weight: 900;
        text-shadow: 0 0 12px rgba(0, 255, 204, 0.7);
        opacity: 1;
    }

    /* =========================================================
       卡片內部文字 Aesthetic 排版 (黑魔法核心)
       ========================================================= */
       
    /* 通用文字設定 */
    div[data-testid="column"] button p {
        width: 100% !important;
        margin: 0 !important;
        text-align: left !important;
        font-family: 'SF Pro Display', sans-serif !important;
    }

    /* 1. ID 浮空小圈圈 (利用 nth-child 瞄準第一個 P 裡面的第一個文字) */
    div[data-testid="column"] button p:nth-child(1) {
        position: absolute !important;
        top: -12px !important;
        left: 20px !important;
        background: #2D2D32 !important;
        color: #8E8E93 !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        width: 24px !important;
        height: 24px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        z-index: 2 !important;
        letter-spacing: 0 !important;
    }
    
    /* 修正選中時 ID 嘅顏色 */
    div[data-testid="column"] button[data-testid="baseButton-primary"] p:nth-child(1) {
        background: #00ffcc !important;
        color: #1C1C1E !important;
        border-color: #00ffcc !important;
    }

    /* 2. 英文歌名 (瞄準第二個 P) */
    div[data-testid="column"] button p:nth-child(2) {
        color: #FFFFFF !important;
        font-size: 20px !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        letter-spacing: -0.5px !important;
        margin-bottom: 4px !important;
        margin-top: 5px !important; /* 給 ID 留位 */
    }

    /* 3. 中文譯名 (瞄準第三個 P) - 變成細灰副標題 */
    div[data-testid="column"] button p:nth-child(3) {
        color: #A1A1AA !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        margin-bottom: 18px !important;
        /* 加入虛線分割線 */
        border-bottom: 1px dashed rgba(255, 255, 255, 0.1) !important;
        padding-bottom: 18px !important;
        font-style: normal !important; /* 取消斜體 */
    }

    /* 4. 意境描述 (瞄準第四個 P 開始) */
    div[data-testid="column"] button p:nth-child(n+4) {
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        font-weight: 400 !important;
        padding-left: 15px !important;
        position: relative !important;
    }
    
    /* 意境描述前嘅螢光小圓點 (取代💡) */
    div[data-testid="column"] button p:nth-child(n+4)::before {
        content: '•';
        position: absolute;
        left: 0;
        color: #00ffcc;
        font-weight: 900;
        font-size: 18px;
        line-height: 1;
        top: -1px;
    }

    /* =========================================================
       保護底部 Action Bar 嘅按鈕樣式
       ========================================================= */
    div.stActionButton button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #008080 0%, #00E676 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        min-height: auto !important;
        height: auto !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        box-shadow: 0 4px 15px rgba(0, 230, 118, 0.3) !important;
        animation: pulse-glow 2.5s infinite !important;
        transform: none !important;
        margin: 0 !important;
    }
    div.stActionButton button[data-testid="baseButton-primary"]:hover {
        box-shadow: 0 6px 20px rgba(0, 230, 118, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    div.stActionButton button[data-testid="baseButton-primary"]::after { content: none !important; }
    div.stActionButton button[data-testid="baseButton-primary"] p { 
        color: #1C1C1E !important; 
        font-size: 16px !important; 
        font-weight: 700 !important; 
        letter-spacing: 0.5px !important;
        font-family: 'Inter', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 初始化流水線狀態 
# ==========================================
if "step" not in st.session_state: st.session_state.step = 1
if "song_data" not in st.session_state: st.session_state.song_data = []
if "selected_song_ids" not in st.session_state: st.session_state.selected_song_ids = []
if "concept_options" not in st.session_state: st.session_state.concept_options = []
if "selected_concept" not in st.session_state: st.session_state.selected_concept = None
if "final_results" not in st.session_state: st.session_state.final_results = {}

def next_step(): st.session_state.step += 1
def reset_pipeline():
    st.session_state.song_data = []
    st.session_state.selected_song_ids = []
    st.session_state.concept_options = []
    st.session_state.selected_concept = None
    st.session_state.final_results = {}
    st.session_state.step = 1

# ==========================================
# 頁面標題 (Aesthetic 模式)
# ==========================================
st.markdown("<div class='ai-title'>Title Studio</div>", unsafe_allow_html=True)
st.markdown("<div class='ai-subtitle'>Aesthetic Lofi Pipeline • v13.0</div>", unsafe_allow_html=True)

# 簡約進度條
progress_val = (st.session_state.step - 1) / 3
st.progress(progress_val)
st.write("")

# ==========================================
# Pipeline Step 1: Aesthetic 原生卡片
# ==========================================
if st.session_state.step == 1:
    # 注入終極美化 CSS
    inject_aesthetic_native_card_css()
    
    if not st.session_state.song_data:
        st.markdown("### 🎛️ Stage 1: Music Ideation (Mock)")
        col_mock1, col_mock2 = st.columns([2,1])
        with col_mock1:
            if st.button("🪄 AI 生成 20 首 Aesthetic 歌單", type="primary", use_container_width=True):
                with st.spinner("Gemini 正在構思文青標題..."):
                    time.sleep(1.5)
                    dummy_songs = []
                    for i in range(1, 21):
                        dummy_songs.append({
                            "id": i,
                            "en_title": f"Soft Landing Part {i}",
                            "zh_title": f"柔軟的著陸 第 {i} 樂章",
                            "theme": f"Sinking into a pre-loved armchair, feeling your body finally remember how to let go. — 沉入一張舊扶手椅，感受身體終於記起如何放手。"
                        })
                    st.session_state.song_data = dummy_songs
                    st.rerun()
    else:
        st.markdown("### 🎛️ Stage 1: Select Your Aesthetic Songs")
        st.write("")

        cols = st.columns(3, gap="medium")

        for idx, song in enumerate(st.session_state.song_data):
            target_col = cols[idx % 3]
            is_selected = song['id'] in st.session_state.selected_song_ids
            
            # 選中時用 primary，未選用 secondary。CSS 會自動幫佢哋換衫！
            btn_type = "primary" if is_selected else "secondary"
            
            with target_col:
                # 🔥 黑魔法排版字串：CSS 會根據行數 (nth-child) 套用不同樣式
                # Line 1: ID
                # Line 2: EN Title
                # Line 3: ZH Title
                # Line 4+: Theme
                card_content = f"""{song['id']}
{song['en_title']}
{song['zh_title']}
{song['theme']}"""
                
                # 呢個就係嗰張卡！純原生按鈕，100% 撳得中，不刷新！
                clicked = st.button(card_content, key=f"btn_{song['id']}", type=btn_type, use_container_width=True)
                if clicked:
                    if song['id'] in st.session_state.selected_song_ids:
                        st.session_state.selected_song_ids.remove(song['id'])
                    else:
                        st.session_state.selected_song_ids.append(song['id'])
                    st.rerun()

        # Sticky Action Bar
        st.markdown('<div class="stActionButton"><div>', unsafe_allow_html=True)
        scol1, scol2, scol3, scol4 = st.columns([3, 1.2, 1.2, 4])
        with scol1: 
            st.markdown(f"<div style='color:#FFFFFF; font-size:15px; font-weight:600; padding-top:12px; font-family:Inter, sans-serif;'>Selected: <span style='color:#00ffcc; font-size:20px; font-weight:800;'>{len(st.session_state.selected_song_ids)}</span> / {len(st.session_state.song_data)}</div>", unsafe_allow_html=True)
        with scol2:
            if st.button("全選", type="secondary", use_container_width=True):
                st.session_state.selected_song_ids = [s['id'] for s in st.session_state.song_data]
                st.rerun()
        with scol3:
            if st.button("清空", type="secondary", use_container_width=True):
                st.session_state.selected_song_ids = []
                st.rerun()
        with scol4:
            if st.button("確認並前往 Concept Stage ➡️", type="primary", use_container_width=True):
                if not st.session_state.selected_song_ids: st.warning("⚠️ 請至少點擊選取一首歌曲！")
                else:
                    next_step()
                    st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

# ==========================================
# Pipeline Step 2: 視覺意境 (Mock)
# ==========================================
elif st.session_state.step == 2:
    st.markdown("### 🎬 Stage 2: Visual Concept")
    with st.container(border=True):
        vibe = st.text_input("自定義時間與氛圍 (例如: 3:00 AM, 微雨, 霓虹燈)", placeholder="Midnight, raining...")
        
        if st.button("🧠 AI 構思故事方向", type="primary"):
            with st.spinner("正在提取歌曲意境..."):
                time.sleep(1)
                st.session_state.concept_options = [
                    "☔ 微雨的窗邊放空 | Spacing out by the rainy window",
                    "☕ 暖光下的手沖咖啡 | Pour-over coffee in warm light",
                    "🌙 深夜安靜的書檯 | Quiet study desk at midnight"
                ]
    
    if st.session_state.concept_options:
        st.write("")
        st.markdown("<div class='section-title'>選擇一個故事方向</div>", unsafe_allow_html=True)
        sel_concept = st.radio("Story Direction", st.session_state.concept_options, label_visibility="collapsed")
        
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
# Pipeline Step 3 & 4 (簡化版 Mock)
# ==========================================
elif st.session_state.step == 3:
    st.markdown("### 🖼️ Stage 3: Assets & SEO Prep")
    
    with st.status("⚙️ 模擬運作中...", expanded=True) as status:
        st.write("🌌 正在生成 Midjourney Prompt...")
        time.sleep(0.5)
        st.write("🔍 正在優化 SEO 標題與標籤...")
        time.sleep(0.5)
        st.session_state.final_results = {"titles": "99|||测试|||Test"}
        status.update(label="✅ 模擬完成！", state="complete", expanded=False)
    
    st.write("")
    col_back, col_gen = st.columns(2)
    if col_back.button("⬅️ 返回", type="secondary", use_container_width=True):
        st.session_state.step = 2
        st.rerun()
    if col_gen.button("查看終極 Dashboard 🏆", type="primary", use_container_width=True):
        next_step()
        st.rerun()

elif st.session_state.step == 4:
    st.markdown("### 🎉 Stage 4: Final Dashboard (Mock)")
    st.balloons()
    
    st.markdown("""
    <div class='result-card'>
        <div class='section-title'>Final titles</div>
        <div class='content-text'>99% Sleeping in Rainy Window • Relaxing Lofi • Deep Sleep Music</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 重置全線流程", type="secondary", use_container_width=True):
        reset_pipeline()
        st.rerun()

st.write("")
st.markdown(f"<div style='text-align: center; color: #555; font-size: 12px; margin-top: 50px; margin-bottom: 100px;'>Demo Mode • Aesthetic Native Cards • v13.0</div>", unsafe_allow_html=True)
