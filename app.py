import streamlit as st
import time

# ==========================================
# 1. 頁面設定與全域暗黑美學 CSS
# ==========================================
st.set_page_config(page_title="YouTube Title Studio (Demo)", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    .block-container { padding-top: 1.5rem; max-width: 1100px !important; }

    @keyframes gradient-text { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .ai-title { font-weight: 800; font-size: 38px; text-align: center; background: linear-gradient(270deg, #00E676, #00ffcc, #b026ff, #00E676); background-size: 300% 300%; animation: gradient-text 4s ease infinite; -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
    .ai-subtitle { color: #8E8E93; font-size: 14px; text-align: center; margin-bottom: 30px; letter-spacing: 1px; }

    @keyframes pulse-glow { 0% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); } 50% { box-shadow: 0 0 20px rgba(0, 255, 204, 0.8); } 100% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); } }
    
    /* 底部 Sticky Action Bar */
    .stApp > header {background-color: transparent !important;}
    div.stActionButton { position: fixed; bottom: 0; left: 0; width: 100%; background-color: rgba(20, 20, 22, 0.95); backdrop-filter: blur(15px); border-top: 1px solid rgba(255, 255, 255, 0.1); padding: 15px 0; z-index: 1000; }
    div.stActionButton > div { max-width: 1100px; margin: 0 auto; padding: 0 1rem; }
    
    .result-card { background-color: rgba(30, 30, 35, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .section-title { font-size: 16px; font-weight: 700; color: #00ffcc; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;}
    .content-text { font-size: 15px; color: #E5E5EA; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 終極魔法：將原生 Button 變成絕美卡片！
# ==========================================
def inject_native_button_card_css():
    st.markdown("""
<style>
    /* 基礎卡片設定 (取消原生 Button 樣式，變成卡片) */
    button[data-testid="baseButton-secondary"], button[data-testid="baseButton-primary"] {
        border-radius: 12px !important;
        padding: 20px 24px !important;
        width: 100% !important;
        height: 100% !important;
        min-height: 200px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
        white-space: pre-wrap !important; /* 支援多行文字 */
    }

    /* 未選取狀態 (Secondary Button) */
    button[data-testid="baseButton-secondary"] {
        background-color: rgba(40, 40, 45, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        border-color: rgba(0, 255, 204, 0.4) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(0, 255, 204, 0.15) !important;
    }

    /* 已選取狀態 (Primary Button) */
    button[data-testid="baseButton-primary"] {
        background-color: rgba(20, 30, 60, 0.9) !important;
        border: 2px solid #00ffcc !important;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.2) !important;
    }

    /* 已選取狀態嘅右上角 Checkmark */
    button[data-testid="baseButton-primary"]::after {
        content: '✓';
        position: absolute;
        top: 15px;
        right: 20px;
        color: #00ffcc;
        font-size: 26px;
        font-weight: 900;
        text-shadow: 0 0 10px rgba(0, 255, 204, 0.6);
    }

    /* 處理卡片內部文字排版 */
    button[data-testid="baseButton-secondary"] p, button[data-testid="baseButton-primary"] p {
        width: 100% !important;
        margin: 0 !important;
        color: rgba(255, 255, 255, 0.65) !important; /* 意境描述顏色 */
        font-size: 14px !important;
        line-height: 1.6 !important;
        text-align: left !important;
    }
    
    /* 英文歌名 (加粗大字) */
    button[data-testid="baseButton-secondary"] strong, button[data-testid="baseButton-primary"] strong {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        display: block !important;
        margin-bottom: 6px !important;
        letter-spacing: 0.2px !important;
    }

    /* 中文譯名 (斜體轉化為細灰字) */
    button[data-testid="baseButton-secondary"] em, button[data-testid="baseButton-primary"] em {
        color: #8E8E93 !important;
        font-style: normal !important;
        font-size: 13px !important;
        display: block !important;
        margin-bottom: 16px !important;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding-bottom: 16px !important;
    }

    /* =========================================================
       保護底部 Action Bar 嘅按鈕唔被變成卡片
       ========================================================= */
    div.stActionButton button[data-testid="baseButton-primary"] {
        background: linear-gradient(90deg, #008080, #00E676) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        min-height: auto !important;
        height: auto !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        box-shadow: none !important;
        animation: pulse-glow 2.5s infinite !important;
        transform: none !important;
    }
    div.stActionButton button[data-testid="baseButton-primary"]::after { content: none !important; }
    div.stActionButton button[data-testid="baseButton-primary"] p { color: #1C1C1E !important; font-size: 16px !important; font-weight: 700 !important; }
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
# 頁面標題 (Demo 模式)
# ==========================================
st.markdown("<div class='ai-title'>Title Studio <span style='color:#FF9500; font-size:24px;'>(DEMO)</span></div>", unsafe_allow_html=True)
st.markdown("<div class='ai-subtitle'>100% Native Button Card • Bulletproof • v12.1</div>", unsafe_allow_html=True)

progress_val = (st.session_state.step - 1) / 3
step_labels = ["Ideation", "Concept", "SEO Prep", "Dashboard"]
st.progress(progress_val, text=f"Pipeline Stage {st.session_state.step}/4: {step_labels[st.session_state.step-1]}")
st.write("")

# ==========================================
# Pipeline Step 1: 完美原生按鈕卡片
# ==========================================
if st.session_state.step == 1:
    inject_native_button_card_css()
    
    if not st.session_state.song_data:
        st.markdown("### 🎛️ Stage 1: Music Ideation (Mock 數據)")
        if st.button("🪄 載入 20 首測試用假歌單", type="primary", use_container_width=True):
            with st.spinner("模擬 AI 生成中..."):
                time.sleep(1)
                dummy_songs = []
                for i in range(1, 21):
                    dummy_songs.append({
                        "id": i,
                        "en_title": f"Soft Landing Part {i}",
                        "zh_title": f"柔軟的著陸 第 {i} 樂章",
                        "en_theme": f"Sinking into a chair, feeling your body remember how to let go.",
                        "zh_theme": f"沉入椅子，感受身體重新記起如何放手。"
                    })
                st.session_state.song_data = dummy_songs
                st.rerun()
    else:
        st.markdown("### 🎛️ Stage 1: Select Your Aesthetic Songs")
        st.markdown("<span style='color:#00ffcc; font-size:14px;'>v12.1 終極版：原生按鈕打造，絕無空位，100% 精準無痕點擊！</span>", unsafe_allow_html=True)
        st.write("")

        cols = st.columns(3, gap="medium")

        for idx, song in enumerate(st.session_state.song_data):
            target_col = cols[idx % 3]
            is_selected = song['id'] in st.session_state.selected_song_ids
            
            # 選中時用 primary，未選用 secondary。CSS 會自動幫佢哋換衫！
            btn_type = "primary" if is_selected else "secondary"
            
            with target_col:
                # 將所有資訊寫入 Markdown 字串，交畀 CSS 去排版
                card_content = f"""**{song['id']}. {song['en_title']}**
*{song['zh_title']}*
💡 {song['en_theme']}
— {song['zh_theme']}"""
                
                # 呢個就係嗰張卡！無任何多餘元素！
                clicked = st.button(card_content, key=f"btn_{song['id']}", type=btn_type, use_container_width=True)
                if clicked:
                    if song['id'] in st.session_state.selected_song_ids:
                        st.session_state.selected_song_ids.remove(song['id'])
                    else:
                        st.session_state.selected_song_ids.append(song['id'])
                    st.rerun()

        # Sticky Action Bar
        st.markdown('<div class="stActionButton"><div>', unsafe_allow_html=True)
        scol1, scol2, scol3, scol4 = st.columns([3, 1.5, 1.5, 4])
        with scol1: st.markdown(f"<div style='color:#00ffcc; font-size:16px; font-weight:700; padding-top:10px;'>已選擇 {len(st.session_state.selected_song_ids)} / {len(st.session_state.song_data)}</div>", unsafe_allow_html=True)
        with scol2:
            if st.button("✅ 全選", type="primary", use_container_width=True):
                st.session_state.selected_song_ids = [s['id'] for s in st.session_state.song_data]
                st.rerun()
        with scol3:
            if st.button("🗑️ 清空", type="primary", use_container_width=True):
                st.session_state.selected_song_ids = []
                st.rerun()
        with scol4:
            if st.button("確認並前往下一步 ➡️", type="primary", use_container_width=True):
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
    vibe = st.text_input("自定義時間與氛圍")
    
    if st.button("🧠 載入 3 個假故事方向", type="primary", use_container_width=True):
        with st.spinner("模擬提取..."):
            time.sleep(1)
            st.session_state.concept_options = [
                "☔ 微雨的窗邊放空 | Spacing out by the rainy window",
                "☕ 暖光下的手沖咖啡 | Pour-over coffee in warm light",
                "🌙 深夜安靜的書檯 | Quiet study desk at midnight"
            ]
    
    if st.session_state.concept_options:
        with st.container(border=True):
            sel_concept = st.radio("Story Direction", st.session_state.concept_options, label_visibility="collapsed")
        
        st.write("")
        col_back, col_next = st.columns(2)
        if col_back.button("⬅️ 返回", type="primary", use_container_width=True):
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
    col_back, col_gen = st.columns(2)
    if col_back.button("⬅️ 返回", type="primary", use_container_width=True):
        st.session_state.step = 2
        st.rerun()
    if col_gen.button("🚀 載入終極假數據!", type="primary", use_container_width=True):
        with st.status("⚙️ 模擬運作中...", expanded=True) as status:
            time.sleep(1)
            st.session_state.final_results = {"story_long": "Test", "story_short": "Test ☕", "titles": "99|||測試|||Test", "tags": "lofi, test"}
            status.update(label="✅ 模擬完成！", state="complete", expanded=False)
            next_step()
            st.rerun()

elif st.session_state.step == 4:
    st.markdown("### 🎉 Stage 4: Final Dashboard (Mock)")
    st.balloons()
    if st.button("🔄 重置全線流程", type="primary", use_container_width=True):
        reset_pipeline()
        st.rerun()
