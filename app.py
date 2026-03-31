import streamlit as st
import time

# ==========================================
# 0. 網址傳參 (Query Params) 點擊攔截系統
# 呢段代碼負責攔截 HTML 卡片嘅點擊，並極速更新選取狀態
# ==========================================
if "selected_song_ids" not in st.session_state: 
    st.session_state.selected_song_ids = []

try:
    if "toggle" in st.query_params:
        toggle_id = int(st.query_params["toggle"])
        if toggle_id in st.session_state.selected_song_ids:
            st.session_state.selected_song_ids.remove(toggle_id)
        else:
            st.session_state.selected_song_ids.append(toggle_id)
        # 清除網址參數，保持網址乾淨
        del st.query_params["toggle"]
except AttributeError:
    # 兼容舊版 Streamlit
    params = st.experimental_get_query_params()
    if "toggle" in params:
        toggle_id = int(params["toggle"][0])
        if toggle_id in st.session_state.selected_song_ids:
            st.session_state.selected_song_ids.remove(toggle_id)
        else:
            st.session_state.selected_song_ids.append(toggle_id)
        st.experimental_set_query_params()

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
    button[kind="primary"] { background: linear-gradient(90deg, #008080, #00E676) !important; animation: pulse-glow 2.5s infinite !important; border: none !important; font-weight: 700 !important; color: #1C1C1E !important;}
    
    /* Sticky Bottom Action Bar */
    .stApp > header {background-color: transparent !important;}
    div.stActionButton { position: fixed; bottom: 0; left: 0; width: 100%; background-color: rgba(20, 20, 22, 0.95); backdrop-filter: blur(15px); border-top: 1px solid rgba(255, 255, 255, 0.1); padding: 15px 0; z-index: 1000; }
    div.stActionButton > div { max-width: 1100px; margin: 0 auto; padding: 0 1rem; }

    /* 全域卡片 (Tab 4) */
    .result-card { background-color: rgba(30, 30, 35, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .section-title { font-size: 16px; font-weight: 700; color: #00ffcc; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;}
    .content-text { font-size: 15px; color: #E5E5EA; line-height: 1.6; }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 純 HTML 網格與卡片美學 CSS
# ==========================================
def inject_pure_html_css():
    st.markdown("""
<style>
    /* CSS Grid 完美 3 欄佈局 */
    .pure-card-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 30px;
    }
    
    /* 清除 a tag 嘅預設樣式 */
    a.card-link {
        text-decoration: none !important;
        color: inherit !important;
        display: block;
        height: 100%;
        outline: none !important;
    }
    
    /* 卡片主體 */
    .song-card { 
        background-color: rgba(40, 40, 45, 0.6); 
        border: 1px solid rgba(255, 255, 255, 0.05); 
        border-radius: 12px; 
        transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1); 
        display: flex; flex-direction: column; color: #FFFFFF; 
        height: 100%; min-height: 180px; position: relative;
    }
    
    /* 懸停特效 */
    a.card-link:hover .song-card { 
        border-color: rgba(0, 255, 204, 0.5); 
        transform: translateY(-3px); 
        box-shadow: 0 8px 20px rgba(0, 255, 204, 0.15); 
    }
    
    /* 已選取狀態 */
    .song-card.selected { 
        background-color: rgba(20, 30, 60, 0.9); 
        border: 2px solid #00ffcc; 
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.2); 
    }
    .song-card.selected::after { 
        content: '✓'; position: absolute; top: 10px; right: 15px; 
        color: #00ffcc; font-size: 24px; font-weight: 900; 
        text-shadow: 0 0 10px rgba(0, 255, 204, 0.6); z-index: 5; 
    }

    /* 標題與意境排版 */
    .card-top { padding: 16px 18px; display: flex; align-items: flex-start; gap: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
    .card-id { flex-shrink: 0; width: 24px; height: 24px; background-color: rgba(255, 255, 255, 0.1); color: #FFFFFF; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; margin-top: 4px; }
    .card-titles { flex-grow: 1; padding-right: 25px; }
    .card-en-title { font-size: 1.2rem; font-weight: 800; color: #FFFFFF; margin-bottom: 4px; line-height: 1.2; letter-spacing: -0.2px;}
    .card-zh-title { font-size: 0.95rem; color: rgba(255, 255, 255, 0.85); font-weight: 500; }
    .card-bottom { background-color: transparent; padding: 14px 18px; display: flex; align-items: flex-start; gap: 10px; flex-grow: 1; }
    .theme-icon { font-size: 16px; margin-top: 2px; flex-shrink: 0; filter: grayscale(100%) brightness(120%); opacity: 0.8;}
    .theme-text { font-size: 0.9rem; color: rgba(255, 255, 255, 0.6); line-height: 1.5; font-style: normal; font-weight: 400;}
    .theme-zh-text { margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 初始化流水線狀態 
# ==========================================
if "step" not in st.session_state: st.session_state.step = 1
if "song_data" not in st.session_state: st.session_state.song_data = []
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
st.markdown("<div class='ai-subtitle'>Pure HTML Grid • 100% Flawless Click • v11.5</div>", unsafe_allow_html=True)

progress_val = (st.session_state.step - 1) / 3
step_labels = ["Ideation", "Concept", "SEO Prep", "Dashboard"]
st.progress(progress_val, text=f"Pipeline Stage {st.session_state.step}/4: {step_labels[st.session_state.step-1]}")
st.write("")

# ==========================================
# Pipeline Step 1: 純 HTML 網格渲染 (無 Checkbox)
# ==========================================
if st.session_state.step == 1:
    inject_pure_html_css()
    
    if not st.session_state.song_data:
        st.markdown("### 🎛️ Stage 1: Music Ideation (Mock 數據)")
        if st.button("🪄 載入 20 首測試用假歌單 (不扣 API)", type="primary", use_container_width=True):
            with st.spinner("模擬 AI 生成中... (等 1 秒)"):
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
        st.markdown("<span style='color:#00ffcc; font-size:14px;'>純 HTML 網格模式：完全移除多餘按鈕。點擊卡片任何位置都會精準選取！</span>", unsafe_allow_html=True)
        st.write("")

        # 🔥 終極武器：一次過渲染整個 CSS Grid HTML
        cards_html = "<div class='pure-card-grid'>"
        for song in st.session_state.song_data:
            sel_class = "selected" if song['id'] in st.session_state.selected_song_ids else ""
            
            # 每張卡片都係一條 Link，點擊後會觸發頁首嘅 Query Params 攔截系統
            cards_html += f"""
            <a href="?toggle={song['id']}" target="_self" class="card-link">
                <div class='song-card {sel_class}'>
                    <div class='card-top'>
                        <div class='card-id'>{song['id']}</div>
                        <div class='card-titles'>
                            <div class='card-en-title'>{song['en_title']}</div>
                            <div class='card-zh-title'>{song['zh_title']}</div>
                        </div>
                    </div>
                    <div class='card-bottom'>
                        <div class='theme-icon'>💡</div>
                        <div class='theme-text'>
                            <div>{song['en_theme']}</div>
                            <div class='theme-zh-text'>— {song['zh_theme']}</div>
                        </div>
                    </div>
                </div>
            </a>
            """
        cards_html += "</div>"
        
        # 顯示完美卡片陣列
        st.markdown(cards_html, unsafe_allow_html=True)

        # Sticky Action Bar 保持不變
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
    vibe = st.text_input("自定義時間與氛圍 (Demo 隨便打都得)")
    
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

st.write("")
st.markdown(f"<div style='text-align: center; color: #8E8E93; font-size: 13px; margin-top: 50px; margin-bottom: 80px; opacity: 0.7;'>Demo Mode (Pure HTML Grid) • v11.5</div>", unsafe_allow_html=True)
