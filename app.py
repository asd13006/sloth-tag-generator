import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# ==========================================
# 1. 頁面設定與全域暗黑美學 CSS
# ==========================================
st.set_page_config(page_title="YouTube Title Studio", page_icon="🤖", layout="centered")

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
# 2. 完美無痕點擊卡片 CSS (Absolute Overlay Black Magic)
# ==========================================
def inject_dark_card_css():
    st.markdown("""
<style>
    /* 未選取狀態 */
    .song-card { 
        background-color: rgba(40, 40, 45, 0.6); 
        border: 1px solid rgba(255, 255, 255, 0.05); 
        border-radius: 12px; 
        transition: all 0.2s ease-in-out; 
        display: flex; flex-direction: column; color: #FFFFFF; overflow: hidden; height: 100%; min-height: 180px; 
    }
    
    /* 懸停與已選取狀態 (綁定於容器，確保覆蓋點擊時有效) */
    div[data-testid="stVerticalBlock"]:has(.song-card):hover .song-card { border-color: rgba(0, 255, 204, 0.4); transform: translateY(-2px); }
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

    /* =========================================================
       🔥 終極黑魔法：徹底覆蓋 Streamlit 隱形包裝，實現全卡點擊
       ========================================================= */
    /* 1. 將包含卡片的區塊設為相對定位 */
    div[data-testid="stVerticalBlock"]:has(.song-card) { 
        position: relative !important; 
    }
    
    /* 2. 鎖定 Streamlit 生成的按鈕「外層包裝」，強制絕對定位鋪滿全卡 */
    div[data-testid="stVerticalBlock"]:has(.song-card) > div:has(button) { 
        position: absolute !important; 
        top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important; 
        width: 100% !important; height: 100% !important; 
        margin: 0 !important; padding: 0 !important; 
        z-index: 999 !important; 
    }
    
    /* 3. 將按鈕本體變為全透明，消滅實體，但保留點擊功能 */
    div[data-testid="stVerticalBlock"]:has(.song-card) button { 
        position: absolute !important; 
        top: 0 !important; left: 0 !important; 
        width: 100% !important; height: 100% !important; 
        opacity: 0 !important; cursor: pointer !important; 
        margin: 0 !important; padding: 0 !important; 
        border: none !important; background: transparent !important; 
        display: block !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 初始化流水線狀態
# ==========================================
if "api_key" not in st.session_state: st.session_state.api_key = ""
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
# 頂部導航
# ==========================================
@st.dialog("⚡ AI 核心連線")
def api_dialog():
    api_input = st.text_input("Enter Gemini API Key", type="password")
    if st.button("啟動連線", use_container_width=True):
        if api_input:
            try:
                genai.configure(api_key=api_input)
                genai.get_model('models/gemini-3-flash-preview')
                st.session_state.api_key = api_input
                st.rerun()
            except: st.error("Invalid Key.")

col_nav, col_api = st.columns([8.5, 1.5])
with col_api:
    if st.button("🟢 已連線" if st.session_state.api_key else "🔑 連線", use_container_width=True) and not st.session_state.api_key: api_dialog()

st.markdown("<div class='ai-title'>YouTube Title Studio</div>", unsafe_allow_html=True)
st.markdown("<div class='ai-subtitle'>Production Ready Content Engine • v10.2</div>", unsafe_allow_html=True)

if not st.session_state.api_key:
    with st.container(border=True):
        st.markdown("#### 🔌 喚醒 Lofi 大師核心 (System Offline)")
        st.markdown("<span style='color:#8E8E93; font-size:14px;'>請貼上 Gemini API 金鑰以解鎖流水線功能。</span>", unsafe_allow_html=True)
        main_api = st.text_input("Gemini API Key", type="password", label_visibility="collapsed")
        if st.button("⚡ 快速初始化流水線", type="primary", use_container_width=True):
            if main_api:
                genai.configure(api_key=main_api)
                st.session_state.api_key = main_api
                st.rerun()
    st.stop()

genai.configure(api_key=st.session_state.api_key)
model = genai.GenerativeModel('gemini-3-flash-preview')

progress_val = (st.session_state.step - 1) / 3
step_labels = ["Ideation", "Concept", "SEO Prep", "Dashboard"]
st.progress(progress_val, text=f"Pipeline Stage {st.session_state.step}/4: {step_labels[st.session_state.step-1]}")
st.write("")

# ==========================================
# Pipeline Step 1: 音樂靈感 (完美全卡點擊版)
# ==========================================
if st.session_state.step == 1:
    inject_dark_card_css()
    
    if not st.session_state.song_data:
        st.markdown("### 🎛️ Stage 1: Music Ideation (Suno 歌曲孵化)")
        if st.button("🪄 孵化 20 首治癒系英文歌曲主題 (感官溫暖・靈魂治癒)", type="primary", use_container_width=True):
            with st.spinner("AI 正在深度創作靈魂歌單 (若需時較長請耐心等候)..."):
                prompt = """我正在使用 SUNO AI 創作英文治癒系歌曲。請為我全新創作 20 首歌曲題目及其意境 (Lyric Theme)。
                核心情感：全然放鬆、心理停頓、和平、感官溫暖。
                嚴格遵守輸出格式（格式破壞則系統崩潰）：
                [編號]. 《[英文歌名]》 [中文譯名]
                Lyric Theme: [英文意境描述] — [中文意境描述]
                一定要生成夠 20 首。不要有任何前言或結語。"""
                
                try:
                    resp = model.generate_content(prompt)
                    raw_text = resp.text.strip()
                    pattern = r"(\d+)\.\s*《(.*?)》\s*(.*?)\nLyric Theme:\s*(.*?)\s*[—-]\s*(.*)"
                    matches = re.findall(pattern, raw_text)
                    
                    if not matches:
                        st.error("⚠️ AI 輸出格式出現偏差，請重新點擊按鈕！")
                    else:
                        parsed_songs = [{"id": int(m[0]), "en_title": m[1].strip(), "zh_title": m[2].strip(), "en_theme": m[3].strip(), "zh_theme": m[4].strip()} for m in matches]
                        st.session_state.song_data = parsed_songs
                        st.rerun()
                except Exception as e:
                    st.error(f"⚠️ 伺服器繁忙 (連線超時)，請再撳一次按鈕！\n詳細錯誤: {e}")
    else:
        st.markdown("### 🎛️ Stage 1: Select Your Aesthetic Songs")
        st.markdown("<span style='color:#8E8E93; font-size:14px;'>點擊卡片任何位置即可選取。支援全選或自由組合。</span>", unsafe_allow_html=True)
        st.write("")

        cols = st.columns(3, gap="medium")
        sorted_songs = sorted(st.session_state.song_data, key=lambda x: x['id'])

        for idx, song in enumerate(sorted_songs):
            target_col = cols[idx % 3]
            is_selected = song['id'] in st.session_state.selected_song_ids
            sel_class = "selected" if is_selected else ""
            
            with target_col:
                # 每一張卡片包裝在獨立的 container 中，確保點擊覆蓋準確
                with st.container():
                    st.markdown(f"""
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
                    
                    # 生成完全隱形的按鈕，透過 CSS 強制拉伸覆蓋整張卡片
                    clicked = st.button(" ", key=f"btn_{song['id']}", use_container_width=True)
                    if clicked:
                        if song['id'] in st.session_state.selected_song_ids:
                            st.session_state.selected_song_ids.remove(song['id'])
                        else:
                            st.session_state.selected_song_ids.append(song['id'])
                        st.rerun()
                
                st.write("") # 模擬 margin-bottom

        # Sticky Action Bar
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
# Pipeline Step 2: 視覺意境 
# ==========================================
elif st.session_state.step == 2:
    st.markdown("### 🎬 Stage 2: Visual Concept (設定感官意境)")
    
    vibe = st.text_input("自定義時間與氛圍 (留空則由 AI 隨機安排)", placeholder="例如：落雨嘅深夜，一個人喺房溫書放空...")
    
    if st.button("🧠 構思 3 個極簡故事方向", use_container_width=True):
        with st.spinner("AI 正在提取視覺靈感..."):
            sel_songs = [s['en_title'] for s in st.session_state.song_data if s['id'] in st.session_state.selected_song_ids]
            songs_context = " / ".join(sel_songs)
            context = vibe if vibe else "隨機生成極度放鬆的 Blue Hour 或深夜生活日常細節 (嚴禁Dust)"
            prompt = f"""基於以下歌曲：{songs_context}
            情境設定：{context}
            請提供 3 個不同的「極簡故事意境選項」。
            要求：中英對照，非常簡短，具畫面感。
            格式必須為：[Emoji] [中文短意境] | [English short vibe]
            每行一個，不要加數字。"""
            try:
                resp = model.generate_content(prompt)
                st.session_state.concept_options = [line.strip() for line in resp.text.strip().split('\n') if "|" in line]
            except Exception as e:
                st.error(f"⚠️ 伺服器繁忙，請再撳一次！\n詳細錯誤: {e}")
    
    if st.session_state.concept_options:
        with st.container(border=True):
            st.markdown("#### 請選擇一個視覺故事方向：")
            sel_concept = st.radio("Story Direction", st.session_state.concept_options, label_visibility="collapsed")
        
        st.write("")
        col_back, col_next = st.columns(2)
        if col_back.button("⬅️ 返回重選歌曲", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
        if col_next.button("進入下一步 (Assets & SEO) ➡️", type="primary", use_container_width=True):
            st.session_state.selected_concept = sel_concept
            next_step()
            st.rerun()

# ==========================================
# Pipeline Step 3: Assets & SEO 打包
# ==========================================
elif st.session_state.step == 3:
    st.markdown("### 🖼️ Stage 3: Assets & SEO Prep (圖片與打包)")
    
    with st.container(border=True):
        st.markdown("#### 👁️ 上傳視覺特徵 (Thumbnail)")
        st.markdown("<span style='color:#8E8E93; font-size:14px;'>Upload 您生成好嘅靚圖 (可選)。</span>", unsafe_allow_html=True)
        uploaded_img = st.file_uploader("Upload Thumb", type=["jpg", "png"], label_visibility="collapsed")
        if uploaded_img: st.image(uploaded_img, use_container_width=True)
    
    st.write("")
    col_back, col_gen = st.columns(2)
    if col_back.button("⬅️ 返回重選意境", use_container_width=True):
        st.session_state.step = 2
        st.rerun()
        
    if col_gen.button("🚀 啟動全線終極生成 (Generate All)!", type="primary", use_container_width=True):
        with st.status("⚙️ 生產線全面運作中 (The Magic is happening)...", expanded=True) as status:
            st.write("1. 濃縮 300 字慵懶感官故事...")
            st.write("2. 創作精簡 Emoji 短故事...")
            st.write("3. 打包 490 字元黃金標籤...")
            
            songs_context = [s['en_title'] for s in st.session_state.song_data if s['id'] in st.session_state.selected_song_ids]
            payload = [f"Songs: {'/'.join(songs_context)}\nVibe: {st.session_state.selected_concept}"]
            if uploaded_img: payload.append(Image.open(uploaded_img))
            
            prompt = f"""你是 YouTube Lofi 音樂頻道總監。請根據以上設定，一次過輸出以下最終內容。
            
            【嚴格輸出格式，使用 === 分隔】：
            
            ===LONG_STORY===
            寫一個約 300 字的英文慵懶感官描述故事 (Detailed Story)，極度放鬆且充滿溫馨感。
            
            ===SHORT_STORY===
            精簡為「生活化、微小、帶有 Emoji 嘅 reflective」短故事。
            要好似這個例子：
            Making Tea 🍵
            Evening settles outside the window 🌙. You fill the kettle...
            
            ===TITLES===
            提供 5 個中英對照標題 (分數|||中文|||英文)。
            英文格式嚴格跟隨：[Poetic Phrase]… [曲風] for [活動1], [活動2] & [氛圍] [2個Emoji]
            
            ===TAGS===
            一連串逗號分隔 Tags，總字元控制在 450 到 490 之間。
            """
            payload.insert(0, prompt)
            
            try:
                resp = model.generate_content(payload)
                parts = resp.text.split("===")
                
                st.session_state.final_results = {
                    "story_long": next((p for p in parts if "LONG_STORY" in p), "").replace("LONG_STORY", "").strip(),
                    "story_short": next((p for p in parts if "SHORT_STORY" in p), "").replace("SHORT_STORY", "").strip(),
                    "titles": next((p for p in parts if "TITLES" in p), "").replace("TITLES", "").strip(),
                    "tags": next((p for p in parts if "TAGS" in p), "").replace("TAGS", "").strip()
                }
                status.update(label="✅ 生成完畢！", state="complete", expanded=False)
                next_step()
                st.rerun()
            except Exception as e:
                status.update(label="❌ 伺服器繁忙 (Timeout)", state="error")
                st.error(f"請再撳一次！系統異常: {e}")

# ==========================================
# Pipeline Step 4: 最終成品總結
# ==========================================
elif st.session_state.step == 4:
    st.markdown("### 🎉 Stage 4: Final Dashboard")
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
    if st.button("🔄 重置全線流程，開始新企劃", type="primary", use_container_width=True):
        reset_pipeline()
        st.rerun()

st.write("")
st.markdown(f"<div style='text-align: center; color: #8E8E93; font-size: 13px; margin-top: 50px; margin-bottom: 80px; opacity: 0.7;'>YouTube Title Studio v10.2 (Prod)<br>Developed by Leo Lai • Powered by Gemini 3 Flash Preview</div>", unsafe_allow_html=True)
