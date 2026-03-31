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
    button[kind="primary"] { background: linear-gradient(90deg, #008080, #00E676) !important; animation: pulse-glow 2.5s infinite !important; border: none !important; font-weight: 700 !important; color: #1C1C1E !important;}
    
    /* Sticky Bottom Action Bar */
    .stApp > header {background-color: transparent !important;}
    div.stActionButton { position: fixed; bottom: 0; left: 0; width: 100%; background-color: rgba(20, 20, 22, 0.95); backdrop-filter: blur(15px); border-top: 1px solid rgba(255, 255, 255, 0.1); padding: 15px 0; z-index: 1000; }
    div.stActionButton > div { max-width: 1100px; margin: 0 auto; padding: 0 1rem; }

    /* 全域卡片 (Tab 4) */
    .result-card { background-color: rgba(30, 30, 35, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .section-title { font-size: 16px; font-weight: 700; color: #00ffcc; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;}
    .content-text { font-size: 15px; color: #E5E5EA; line-height: 1.6; }
    
    .score-badge-global { display: inline-block; font-size: 11px; font-weight: 700; color: #1C1C1E; background: #00ffcc; padding: 2px 8px; border-radius: 4px; margin-bottom: 8px; }
    .en-main-global { font-size: 18px; font-weight: 600; color: #FFFFFF; margin-bottom: 4px; }
    .zh-sub-global { font-size: 14px; color: #8E8E93; }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 完美無痕點擊卡片 CSS (Absolute Overlay)
# ==========================================
def inject_dark_card_css():
    st.markdown("""
<style>
    /* 未選取狀態 */
    .song-card { background-color: rgba(40, 40, 45, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; transition: all 0.2s ease-in-out; display: flex; flex-direction: column; color: #FFFFFF; overflow: hidden; height: 100%; min-height: 180px; }
    
    /* 懸停與已選取狀態 */
    div[data-testid="stVerticalBlock"]:has(.click-marker):hover .song-card { border-color: rgba(0, 255, 204, 0.4); transform: translateY(-2px); }
    .song-card.selected { background-color: rgba(20, 30, 60, 0.9); border: 2px solid #00ffcc; box-shadow: 0 0 15px rgba(0, 255, 204, 0.15); }
    .song-card.selected::after { content: '✓'; position: absolute; top: 10px; right: 15px; color: #00ffcc; font-size: 24px; font-weight: 900; text-shadow: 0 0 10px rgba(0, 255, 204, 0.6); z-index: 5; }

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

    /* 100% 覆蓋隱形按鈕 */
    div[data-testid="stVerticalBlock"]:has(.click-marker) { position: relative; }
    div[data-testid="stVerticalBlock"]:has(.click-marker) > div:last-child { position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; margin: 0 !important; padding: 0 !important; z-index: 10 !important; }
    div[data-testid="stVerticalBlock"]:has(.click-marker) div[data-testid="stButton"], div[data-testid="stVerticalBlock"]:has(.click-marker) button { width: 100% !important; height: 100% !important; opacity: 0 !important; cursor: pointer !important; margin: 0 !important; padding: 0 !important; border: none !important; background: transparent !important; }
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
    for key in ["song_data", "selected_song_ids", "concept_options", "selected_concept", "final_results"]:
        st.session_state[key] = [] if "songs" in key or "options" in key else ({} if "results" in key else None)
    st.session_state.step = 1

# ==========================================
# 頁面標題 (Demo 模式)
# ==========================================
st.markdown("<div class='ai-title'>Title Studio <span style='color:#FF9500; font-size:24px;'>(DEMO)</span></div>", unsafe_allow_html=True)
st.markdown("<div class='ai-subtitle'>Mock Data Mode • No API Cost • v11.0</div>", unsafe_allow_html=True)

progress_val = (st.session_state.step - 1) / 3
step_labels = ["Ideation", "Concept", "SEO Prep", "Dashboard"]
st.progress(progress_val, text=f"Pipeline Stage {st.session_state.step}/4: {step_labels[st.session_state.step-1]}")
st.write("")

# ==========================================
# Pipeline Step 1: 測試 3 欄卡片點擊
# ==========================================
if st.session_state.step == 1:
    inject_dark_card_css()
    
    if not st.session_state.song_data:
        st.markdown("### 🎛️ Stage 1: Music Ideation (Mock 數據)")
        if st.button("🪄 載入 20 首測試用假歌單 (不扣 API)", type="primary", use_container_width=True):
            with st.spinner("模擬 AI 生成中... (等 1 秒)"):
                time.sleep(1) # 模擬延遲
                
                # 注入 20 首假數據
                dummy_songs = []
                for i in range(1, 21):
                    dummy_songs.append({
                        "id": i,
                        "en_title": f"Soft Landing Part {i}",
                        "zh_title": f"柔軟的著陸 第 {i} 樂章",
                        "en_theme": f"Sinking into a chair, feeling your body remember how to let go. (Test {i})",
                        "zh_theme": f"沉入椅子，感受身體重新記起如何放手。 (測試 {i})"
                    })
                st.session_state.song_data = dummy_songs
                st.rerun()
    else:
        st.markdown("### 🎛️ Stage 1: Select Your Aesthetic Songs")
        st.markdown("<span style='color:#FF9500; font-size:14px;'>Demo 模式：請隨意點擊卡片測試手感，點擊整張卡片任何位置都會有反應。</span>", unsafe_allow_html=True)
        st.write("")

        cols = st.columns(3, gap="medium")
        
        def toggle_selection(song_id):
            if song_id in st.session_state.selected_song_ids:
                st.session_state.selected_song_ids.remove(song_id)
            else:
                st.session_state.selected_song_ids.append(song_id)

        for idx, song in enumerate(st.session_state.song_data):
            target_col = cols[idx % 3]
            is_selected = song['id'] in st.session_state.selected_song_ids
            sel_class = "selected" if is_selected else ""
            
            with target_col:
                with st.container():
                    st.markdown(f"""
                    <div class='click-marker'></div>
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
                    """, unsafe_allow_html=True)
                    st.button(" ", key=f"btn_{song['id']}", on_click=toggle_selection, args=(song['id'],), use_container_width=True)
                st.write("")

        st.markdown('<div class="stActionButton"><div>', unsafe_allow_html=True)
        scol1, scol2, scol3, scol4 = st.columns([3, 1.5, 1.5, 4])
        with scol1: st.markdown(f"<div style='color:#00ffcc; font-size:16px; font-weight:700; padding-top:10px;'>已選擇 {len(st.session_state.selected_song_ids)} / {len(st.session_state.song_data)}</div>", unsafe_allow_html=True)
        with scol2:
            if st.button("✅ 全選", use_container_width=True):
                st.session_state.selected_song_ids = [s['id'] for s in st.session_state.song_data]
                st.rerun()
        with scol3:
            if st.button("🗑️ 清空", use_container_width=True):
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
# Pipeline Step 2: 視覺意境 (Mock 數據)
# ==========================================
elif st.session_state.step == 2:
    st.markdown("### 🎬 Stage 2: Visual Concept (設定感官意境)")
    
    vibe = st.text_input("自定義時間與氛圍 (Demo 隨便打都得)")
    
    if st.button("🧠 載入 3 個假故事方向", use_container_width=True):
        with st.spinner("模擬提取視覺靈感..."):
            time.sleep(1)
            # 注入假概念
            st.session_state.concept_options = [
                "☔ 微雨的窗邊放空 | Spacing out by the rainy window",
                "☕ 暖光下的手沖咖啡 | Pour-over coffee in warm light",
                "🌙 深夜安靜的書檯 | Quiet study desk at midnight"
            ]
    
    if st.session_state.concept_options:
        with st.container(border=True):
            st.markdown("#### 請選擇一個視覺故事方向：")
            sel_concept = st.radio("Story Direction", st.session_state.concept_options, label_visibility="collapsed")
        
        st.write("")
        col_back, col_next = st.columns(2)
        if col_back.button("⬅️ 返回", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
        if col_next.button("進入下一步 ➡️", type="primary", use_container_width=True):
            st.session_state.selected_concept = sel_concept
            next_step()
            st.rerun()

# ==========================================
# Pipeline Step 3: Assets & SEO 打包 (Mock)
# ==========================================
elif st.session_state.step == 3:
    st.markdown("### 🖼️ Stage 3: Assets & SEO Prep")
    
    with st.container(border=True):
        st.markdown("#### 👁️ 隨便擺張圖 (Demo 模式唔上傳都得)")
        uploaded_img = st.file_uploader("Upload Thumb", type=["jpg", "png"], label_visibility="collapsed")
        if uploaded_img: st.image(uploaded_img, use_container_width=True)
    
    st.write("")
    col_back, col_gen = st.columns(2)
    if col_back.button("⬅️ 返回", use_container_width=True):
        st.session_state.step = 2
        st.rerun()
        
    if col_gen.button("🚀 載入終極假數據 (生成假 Dashboard)!", type="primary", use_container_width=True):
        with st.status("⚙️ 模擬運作中...", expanded=True) as status:
            time.sleep(1.5)
            # 注入終極假結果
            st.session_state.final_results = {
                "story_long": "This is a dummy long story. The room smells like old paper and petrichor. A low lamp casts a warm amber circle on the wooden desk. Outside, the city murmurs a gentle lullaby. You trace the rim of your mug, feeling the residual heat. The world slows down here, wrapped in a blanket of quiet thoughts and soft shadows. (這是一段長達 300 字的感官描述範例...)",
                "story_short": "Making Coffee ☕\nThe beans grind with a low hum 🫘. Hot water blooms over the grounds, filling the room with warmth ♨️.\nYou watch the slow drip, feeling the morning quiet 🌿.",
                "titles": "98|||☕ 溫暖的咖啡時光... 適合放鬆與工作的 Chill Lofi|||Warm Coffee Moments… Chill Lofi for Relaxation & Study ☕ 🌿\n95|||🌙 深夜的安靜陪伴... 適合入眠的 Ambient Beats|||Quiet Midnight Companionship… Ambient Beats for Sleep 🌙 ☁️\n92|||🌧️ 聽著雨聲放空... 適合獨處的 Cozy R&B|||Rainy Day Spacing Out… Cozy R&B for Alone Time 🌧️ 📖",
                "tags": "lofi hip hop radio, beats to relax/study to, chill vibes, warm coffee aesthetic, late night study, aesthetic lofi, sleep music, calm morning, relaxing background music, focus beats"
            }
            status.update(label="✅ 模擬完成！", state="complete", expanded=False)
            next_step()
            st.rerun()

# ==========================================
# Pipeline Step 4: 最終成品總結
# ==========================================
elif st.session_state.step == 4:
    st.markdown("### 🎉 Stage 4: Final Dashboard (Mock)")
    st.balloons()
    res = st.session_state.final_results
    
    with st.container(border=True):
        st.markdown("<div class='section-title'>1. Selected Aesthetic Concept</div>", unsafe_allow_html=True)
        sel_songs_titles = [f"《{s['en_title']}》 ({s['zh_title']})" for s in st.session_state.song_data if s['id'] in st.session_state.selected_song_ids]
        st.markdown(f"<div class='content-text'>🎵 {'<br>🎵 '.join(sel_songs_titles)}<br><br>🎬 {st.session_state.selected_concept}</div>", unsafe_allow_html=True)

    with st.markdown("<div class='result-card'>", unsafe_allow_html=True):
        st.markdown("<div class='section-title'>2. Detailed Vibe Story (300 words)</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='content-text'>{res.get('story_long', '')}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.markdown("<div class='result-card'>", unsafe_allow_html=True):
        st.markdown("<div class='section-title'>3. Short Reflective Story (with Emojis)</div>", unsafe_allow_html=True)
        st.code(res.get('story_short', ''), language="text")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### 4. YouTube SEO Titles")
    for line in res.get('titles', '').split('\n'):
        if "|||" in line:
            try:
                score, zh, en = line.split("|||")
                st.markdown(f"""
                <div style='background-color: rgba(30, 30, 35, 0.6); border: 1px solid rgba(0, 255, 204, 0.3); border-radius: 8px; padding: 15px; margin-bottom: 10px;'>
                    <div class='score-badge-global'>🔥 CTR: {score.strip()}/100</div>
                    <div class='en-main-global'>{en.replace("*","").strip()}</div>
                    <div class='zh-sub-global'>{zh.replace("*","").strip()}</div>
                </div>
                """, unsafe_allow_html=True)
            except: pass
            
    st.markdown("<div class='section-title' style='margin-top:20px;'>5. SEO Tags (490 Chars)</div>", unsafe_allow_html=True)
    st.code(res.get('tags', ''), language="text")
    
    st.write("")
    if st.button("🔄 重置全線流程", type="primary", use_container_width=True):
        reset_pipeline()
        st.rerun()

st.write("")
st.markdown(f"<div style='text-align: center; color: #8E8E93; font-size: 13px; margin-top: 50px; margin-bottom: 80px; opacity: 0.7;'>Demo Mode (No API Call) • v11.0</div>", unsafe_allow_html=True)
