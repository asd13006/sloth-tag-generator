import streamlit as st
import time

# ==========================================
# 1. 頁面設定與全域暗黑美學 CSS
# ==========================================
st.set_page_config(page_title="YouTube Title Studio", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    html, body, [class*="css"] { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    
    .block-container { padding-top: 2rem; max-width: 1150px !important; }

    @keyframes gradient-text { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .ai-title { font-weight: 900; font-size: 42px; text-align: center; background: linear-gradient(270deg, #00E676, #00ffcc, #b026ff, #00E676); background-size: 300% 300%; animation: gradient-text 4s ease infinite; -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; letter-spacing: -1px;}
    .ai-subtitle { color: #8E8E93; font-size: 15px; text-align: center; margin-bottom: 40px; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 600; }

    @keyframes pulse-glow { 0% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); } 50% { box-shadow: 0 0 20px rgba(0, 255, 204, 0.8); } 100% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); } }
    
    .stApp > header {background-color: transparent !important;}

    .result-card { background-color: rgba(30, 30, 35, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 25px; margin-bottom: 25px; }
    .section-title { font-size: 17px; font-weight: 700; color: #00ffcc; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1.5px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 終極 Markdown 階梯式排版 CSS
# ==========================================
def inject_hierarchy_card_css():
    st.markdown("""
<style>
    /* =========================================================
       基礎卡片容器 (原生 Button)
       ========================================================= */
    button[data-testid="baseButton-secondary"]:has(h3), 
    button[data-testid="baseButton-primary"]:has(h3) {
        border-radius: 16px !important;
        padding: 24px !important;
        width: 100% !important;
        height: 100% !important;
        min-height: 250px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
        text-align: left !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        white-space: pre-wrap !important;
        position: relative !important;
        overflow: hidden !important;
    }

    /* --- 未選取狀態 (Secondary) --- */
    button[data-testid="baseButton-secondary"]:has(h3) {
        background-color: rgba(30, 30, 35, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* 加入微弱漸層色塊 (視覺錨點) - 解決字海疲勞 */
    div[data-testid="column"]:nth-child(3n+1) button[data-testid="baseButton-secondary"]:has(h3) { background-image: radial-gradient(circle at 100% 0%, rgba(180, 100, 255, 0.08), transparent 50%) !important; }
    div[data-testid="column"]:nth-child(3n+2) button[data-testid="baseButton-secondary"]:has(h3) { background-image: radial-gradient(circle at 100% 0%, rgba(0, 255, 204, 0.06), transparent 50%) !important; }
    div[data-testid="column"]:nth-child(3n+3) button[data-testid="baseButton-secondary"]:has(h3) { background-image: radial-gradient(circle at 100% 0%, rgba(255, 150, 50, 0.06), transparent 50%) !important; }

    /* 懸停效果 */
    button[data-testid="baseButton-secondary"]:has(h3):hover {
        border-color: rgba(255, 255, 255, 0.25) !important;
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3) !important;
    }

    /* --- 已選取狀態 (Primary) --- 強烈反差 */
    button[data-testid="baseButton-primary"]:has(h3) {
        background: linear-gradient(145deg, rgba(16, 32, 64, 0.95), rgba(12, 20, 40, 0.95)) !important; /* 深海藍色 */
        border: 2px solid #00ffcc !important;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.2) !important;
    }
    button[data-testid="baseButton-primary"]:has(h3):hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 30px rgba(0, 255, 204, 0.3) !important;
    }

    /* =========================================================
       階梯式文字排版 (利用 Markdown 標籤精準狙擊)
       ========================================================= */

    /* [第一層 - 標記] h5: 編號 或 Checkmark */
    button h5 {
        position: absolute !important;
        top: 24px !important;
        left: 24px !important;
        color: #8E8E93 !important;
        font-size: 15px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        letter-spacing: 1px !important;
    }
    /* 選中後變成亮綠色勾號 */
    button[data-testid="baseButton-primary"] h5 {
        color: #00ffcc !important;
        font-size: 22px !important;
        top: 20px !important;
        text-shadow: 0 0 10px rgba(0, 255, 204, 0.5) !important;
    }

    /* [第一層 - 歌名] h3: 英文歌名 (純白、加粗、放大) */
    button h3 {
        color: #FFFFFF !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        margin: 28px 0 4px 0 !important; /* 避開右上角 ID */
        line-height: 1.1 !important;
        letter-spacing: -0.5px !important;
        width: 100% !important;
    }

    /* [第二層 - 譯名] h4: 中文譯名 (灰色、小字、虛線底) */
    button h4 {
        color: #A1A1AA !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        margin: 0 0 16px 0 !important;
        padding-bottom: 16px !important;
        border-bottom: 1px dashed rgba(255, 255, 255, 0.15) !important; /* 分割線 */
        width: 100% !important;
    }

    /* [第三層 - 英文意境] strong: 灰色、適中 */
    button strong {
        color: #D1D1D6 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        display: block !important;
        line-height: 1.5 !important;
        margin-bottom: 8px !important;
        width: 100% !important;
    }

    /* [第四層 - 中文意境] em: 最淡灰色、縮進、左側線條 */
    button em {
        color: #71717A !important;
        font-size: 13px !important;
        font-style: normal !important;
        display: block !important;
        line-height: 1.5 !important;
        padding-left: 12px !important;
        border-left: 2px solid #3F3F46 !important; /* 左側視覺線條 */
        width: 100% !important;
    }
    /* 選中後，中文意境嘅線條變為螢光色，增加細節感 */
    button[data-testid="baseButton-primary"] em {
        border-left: 2px solid rgba(0, 255, 204, 0.5) !important;
        color: #8E8E93 !important;
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
# 頁面標題
# ==========================================
st.markdown("<div class='ai-title'>Title Studio</div>", unsafe_allow_html=True)
st.markdown("<div class='ai-subtitle'>Ultimate Hierarchy Mode • v14.0</div>", unsafe_allow_html=True)

progress_val = (st.session_state.step - 1) / 3
st.progress(progress_val)
st.write("")

# ==========================================
# Pipeline Step 1: 階梯式排版原生卡片
# ==========================================
if st.session_state.step == 1:
    
    if not st.session_state.song_data:
        st.markdown("### 🎛️ Stage 1: Music Ideation (Mock)")
        if st.button("🪄 載入 20 首排版測試歌單", type="primary", use_container_width=True):
            with st.spinner("載入中..."):
                time.sleep(0.5)
                dummy_songs = []
                for i in range(1, 21):
                    dummy_songs.append({
                        "id": i,
                        "en_title": f"Soft Landing {i}",
                        "zh_title": f"柔軟的著陸 第 {i} 樂章",
                        "en_theme": "Sinking into a chair, feeling your body remember how to let go.",
                        "zh_theme": "沉入椅子，感受身體重新記起如何放手。"
                    })
                st.session_state.song_data = dummy_songs
                st.rerun()
    else:
        inject_hierarchy_card_css()
        st.markdown("### 🎛️ Stage 1: Select Your Aesthetic Songs")
        st.markdown("<span style='color:#A1A1AA; font-size:14px;'>v14.0：解決字海疲勞，強烈選中狀態，完美階梯排版。點擊卡片任何位置選取。</span>", unsafe_allow_html=True)
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
                
                clicked = st.button(card_content, key=f"btn_{song['id']}", type=btn_type, use_container_width=True)
                if clicked:
                    if song['id'] in st.session_state.selected_song_ids:
                        st.session_state.selected_song_ids.remove(song['id'])
                    else:
                        st.session_state.selected_song_ids.append(song['id'])
                    st.rerun()

        # Action Bar
        st.divider()
        scol1, scol2, scol3, scol4 = st.columns([3, 1.2, 1.2, 4])
        with scol1: 
            st.markdown(f"<div style='color:#FFFFFF; font-size:15px; font-weight:600; padding-top:12px;'>Selected: <span style='color:#00ffcc; font-size:22px; font-weight:900;'>{len(st.session_state.selected_song_ids)}</span> / {len(st.session_state.song_data)}</div>", unsafe_allow_html=True)
        with scol2:
            if st.button("全選", type="secondary", use_container_width=True):
                st.session_state.selected_song_ids = [s['id'] for s in st.session_state.song_data]
                st.rerun()
        with scol3:
            if st.button("清空", type="secondary", use_container_width=True):
                st.session_state.selected_song_ids = []
                st.rerun()
        with scol4:
            if st.button("確認並前往下一步 ➡️", type="primary", use_container_width=True):
                if not st.session_state.selected_song_ids: st.warning("⚠️ 請至少點擊選取一首歌曲！")
                else:
                    next_step()
                    st.rerun()

# ==========================================
# Pipeline Step 2, 3, 4 (Mock 保持不變)
# ==========================================
elif st.session_state.step == 2:
    st.markdown("### 🎬 Stage 2: Visual Concept")
    with st.container(border=True):
        vibe = st.text_input("自定義時間與氛圍", placeholder="Midnight, raining...")
        if st.button("🧠 AI 構思故事方向", type="primary"):
            with st.spinner("正在提取..."):
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
            st.session_state.step = 1; st.rerun()
        if col_next.button("進入下一步 ➡️", type="primary", use_container_width=True):
            st.session_state.selected_concept = sel_concept; next_step(); st.rerun()

elif st.session_state.step == 3:
    st.markdown("### 🖼️ Stage 3: Assets & SEO Prep")
    with st.status("⚙️ 模擬運作中...", expanded=True) as status:
        time.sleep(1)
        st.session_state.final_results = {"titles": "99|||测试|||Test"}
        status.update(label="✅ 模擬完成！", state="complete", expanded=False)
    st.write("")
    col_back, col_gen = st.columns(2)
    if col_back.button("⬅️ 返回", type="secondary", use_container_width=True):
        st.session_state.step = 2; st.rerun()
    if col_gen.button("查看 Dashboard 🏆", type="primary", use_container_width=True):
        next_step(); st.rerun()

elif st.session_state.step == 4:
    st.markdown("### 🎉 Stage 4: Final Dashboard (Mock)")
    st.balloons()
    if st.button("🔄 重置全線流程", type="secondary", use_container_width=True):
        reset_pipeline(); st.rerun()

st.write("")
st.markdown(f"<div style='text-align: center; color: #555; font-size: 12px; margin-top: 50px; margin-bottom: 100px;'>Demo Mode • Ultimate Hierarchy • v14.0</div>", unsafe_allow_html=True)
