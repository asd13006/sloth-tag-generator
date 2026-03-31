import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 1. 頁面設定與流水線專用 CSS
# ==========================================
st.set_page_config(page_title="YouTube Title Studio", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    
    /* 流光標題動畫 */
    @keyframes gradient-text { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .ai-title { font-weight: 800; font-size: 38px; text-align: center; background: linear-gradient(270deg, #00E676, #00ffcc, #b026ff, #00E676); background-size: 300% 300%; animation: gradient-text 4s ease infinite; -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
    .ai-subtitle { color: #8E8E93; font-size: 14px; text-align: center; margin-bottom: 30px; letter-spacing: 1px; }

    /* 絕美卡片化設計 */
    .glass-card { background-color: rgba(30, 30, 35, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .result-card { background-color: rgba(20, 20, 22, 0.8); border-left: 4px solid #00ffcc; border-radius: 8px; padding: 15px 20px; margin-bottom: 15px; }
    
    .section-title { font-size: 16px; font-weight: 700; color: #00ffcc; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;}
    .content-text { font-size: 15px; color: #E5E5EA; line-height: 1.6; }
    
    /* 隱藏 Streamlit 預設 Radio 樣式，用 CSS 美化 (盡量保持簡潔) */
    .stRadio > div { gap: 10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 初始化流水線狀態 (Pipeline State)
# ==========================================
if "api_key" not in st.session_state: st.session_state.api_key = ""
if "step" not in st.session_state: st.session_state.step = 1
# 儲存數據
if "song_options" not in st.session_state: st.session_state.song_options = []
if "selected_songs" not in st.session_state: st.session_state.selected_songs = []
if "concept_options" not in st.session_state: st.session_state.concept_options = []
if "selected_concept" not in st.session_state: st.session_state.selected_concept = None
if "final_results" not in st.session_state: st.session_state.final_results = {}

# 流程控制函數
def next_step(): st.session_state.step += 1
def reset_pipeline():
    for key in ["song_options", "selected_songs", "concept_options", "selected_concept", "final_results"]:
        st.session_state[key] = [] if "options" in key or "songs" in key else ({} if "results" in key else None)
    st.session_state.step = 1

# ==========================================
# 頂部：連線與進度條
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

col1, col2 = st.columns([8, 2])
with col2:
    if st.button("🟢 已連線" if st.session_state.api_key else "🔑 連線", use_container_width=True) and not st.session_state.api_key: api_dialog()

st.markdown("<div class='ai-title'>Title Studio Pipeline</div>", unsafe_allow_html=True)
st.markdown("<div class='ai-subtitle'>End-to-End Content Assembly Line • v5.0</div>", unsafe_allow_html=True)

if not st.session_state.api_key:
    st.info("👋 歡迎！請先輸入 API Key 以啟動流水線。")
    main_api = st.text_input("Gemini API Key", type="password", key="main_api_key")
    if st.button("⚡ 初始化流水線", type="primary", use_container_width=True):
        if main_api:
            genai.configure(api_key=main_api)
            st.session_state.api_key = main_api
            st.rerun()
    st.stop()

# 模型就緒
genai.configure(api_key=st.session_state.api_key)
model = genai.GenerativeModel('gemini-3-flash-preview')

# 顯示進度列
progress_val = (st.session_state.step - 1) / 3
st.progress(progress_val, text=f"Pipeline Stage {st.session_state.step} of 4")

# ==========================================
# Pipeline Step 1: 音樂靈感 (多選)
# ==========================================
if st.session_state.step == 1:
    st.markdown("### 🎛️ Stage 1: Music Ideation (選取歌名)")
    
    if not st.session_state.song_options:
        if st.button("🪄 孵化 20 首治癒系歌名", use_container_width=True):
            with st.spinner("AI 正在創作歌單..."):
                prompt = """生成 20 首治癒系歌曲題目及極簡意境。核心情感：放鬆、和平。
                格式必須為：《[英文歌名]》[中文譯名] - [中英短意境]
                每行一首，不要加數字序號。"""
                resp = model.generate_content(prompt)
                st.session_state.song_options = [line.strip() for line in resp.text.strip().split('\n') if "《" in line]
                st.rerun()
    else:
        st.write("請剔選你心水嘅歌曲 (可多選)：")
        with st.container(border=True):
            selected = []
            for song in st.session_state.song_options:
                if st.checkbox(song, key=song): selected.append(song)
        
        if st.button("進入下一步 ➡️", type="primary", use_container_width=True):
            if selected:
                st.session_state.selected_songs = selected
                next_step()
                st.rerun()
            else:
                st.warning("請至少剔選一首歌曲！")

# ==========================================
# Pipeline Step 2: 視覺意境 (極簡中英選擇)
# ==========================================
elif st.session_state.step == 2:
    st.markdown("### 🎬 Stage 2: Visual Concept (設定意境)")
    
    vibe = st.text_input("自定義時間與氛圍 (留空則由 AI 隨機安排)", placeholder="例如：晚上 7:30，微雨的窗邊...")
    
    if st.button("🧠 構思 3 個極簡故事大綱", use_container_width=True):
        with st.spinner("正在提取視覺靈感..."):
            songs_context = " / ".join(st.session_state.selected_songs)
            context = vibe if vibe else "隨機生成極度放鬆的 Blue Hour 或深夜情境"
            prompt = f"""
            基於以下歌曲：{songs_context}
            情境設定：{context}
            請提供 3 個不同的「極簡故事意境選項」。
            要求：中英對照，非常簡短，具畫面感。
            格式必須為：[Emoji] [中文短意境] | [English short vibe] (不超過 20 字)
            例如：☔ 微雨的窗邊放空 | Spacing out by the rainy window
            每行一個，不要加數字。
            """
            resp = model.generate_content(prompt)
            st.session_state.concept_options = [line.strip() for line in resp.text.strip().split('\n') if "|" in line]
    
    if st.session_state.concept_options:
        st.write("請選擇一個視覺故事方向：")
        with st.container(border=True):
            sel_concept = st.radio("Story Direction", st.session_state.concept_options, label_visibility="collapsed")
        
        col_back, col_next = st.columns(2)
        if col_back.button("⬅️ 返回重選歌曲", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
        if col_next.button("進入下一步 ➡️", type="primary", use_container_width=True):
            st.session_state.selected_concept = sel_concept
            next_step()
            st.rerun()

# ==========================================
# Pipeline Step 3: SEO 與圖片上傳
# ==========================================
elif st.session_state.step == 3:
    st.markdown("### 🖼️ Stage 3: Assets & SEO Setup (圖片與打包)")
    
    st.info("前置設定已完成。你可以上傳一張圖片（可選），然後啟動最終生成。")
    uploaded_img = st.file_uploader("上傳封面圖 (JPG/PNG - 可選)", type=["jpg", "png"])
    if uploaded_img: st.image(uploaded_img, use_container_width=True)
    
    st.write("")
    col_back, col_next = st.columns(2)
    if col_back.button("⬅️ 返回重選意境", use_container_width=True):
        st.session_state.step = 2
        st.rerun()
        
    if col_next.button("🚀 啟動全線生成 (Generate All)!", type="primary", use_container_width=True):
        with st.status("⚙️ 生產線全面運作中 (The Magic is happening)...", expanded=True) as status:
            st.write("1. 濃縮 300 字感官故事...")
            st.write("2. 提取 100 字 Midjourney Prompt...")
            st.write("3. 封裝 SEO 標題與 Tags...")
            
            payload = []
            songs_str = "\n".join(st.session_state.selected_songs)
            if uploaded_img: payload.append(Image.open(uploaded_img))
            
            prompt = f"""
            你是一位 Lofi 內容總監。請根據以下設定，一次過輸出所有最終內容。
            選定歌曲：{songs_str}
            選定意境：{st.session_state.selected_concept}
            
            【嚴格輸出格式，使用 === 分隔】：
            
            ===STORY===
            寫一個約 300 字的英文感官故事 (Detailed Story)，極度慵懶治癒。不要太長。
            
            ===PROMPT===
            提取一個約 100 字的精簡英文 Image Prompt，適合 AI 繪圖。
            
            ===TITLES===
            提供 5 個中英對照標題 (分數|||中文|||英文)。
            英文必須嚴格跟隨：[短句]… [曲風] for [活動] & [氛圍] [Emoji]
            
            ===TAGS===
            一連串逗號分隔的 Tags，包含 lofi hip hop radio 等大熱字眼。總長度嚴格控制在 450 到 490 字元之間。
            """
            payload.insert(0, prompt)
            
            try:
                resp = model.generate_content(payload)
                text = resp.text
                # 簡單 Parsing (解析)
                story = text.split("===STORY===")[1].split("===PROMPT===")[0].strip()
                img_prompt = text.split("===PROMPT===")[1].split("===TITLES===")[0].strip()
                titles = text.split("===TITLES===")[1].split("===TAGS===")[0].strip()
                tags = text.split("===TAGS===")[1].strip() if "===TAGS===" in text else ""
                
                st.session_state.final_results = {
                    "story": story, "prompt": img_prompt, "titles": titles, "tags": tags
                }
                status.update(label="✅ 生產完畢！", state="complete", expanded=False)
                next_step()
                st.rerun()
            except Exception as e:
                status.update(label="❌ 生成錯誤", state="error")
                st.error(f"系統異常: {e}")

# ==========================================
# Pipeline Step 4: 最終成品總結 (Dashboard)
# ==========================================
elif st.session_state.step == 4:
    st.markdown("### 🎉 Stage 4: Final Output (成品展示)")
    st.balloons()
    
    res = st.session_state.final_results
    
    # 使用卡片區塊展示所有成果
    st.markdown("<div class='section-title'>1. Selected Songs (已選歌曲)</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-card content-text'>{'<br>'.join(st.session_state.selected_songs)}</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>2. Visual Story (300 Words)</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-card content-text'>{res.get('story', '')}</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>3. Image Prompt (For Midjourney)</div>", unsafe_allow_html=True)
    st.code(res.get('prompt', ''), language="text")
    
    st.markdown("<div class='section-title'>4. YouTube Titles</div>", unsafe_allow_html=True)
    with st.container():
        for line in res.get('titles', '').split('\n'):
            line = line.replace("*", "").strip()
            if "|||" in line:
                try:
                    score, zh, en = line.split("|||")
                    st.markdown(f"""
                    <div style='background-color: rgba(30, 30, 35, 0.8); border: 1px solid rgba(0, 255, 204, 0.3); border-radius: 8px; padding: 15px; margin-bottom: 10px;'>
                        <div class='score-badge'>🔥 CTR: {score.strip()}/100</div>
                        <div class='en-main'>{en.strip()}</div>
                        <div class='zh-sub'>{zh.strip()}</div>
                    </div>
                    """, unsafe_allow_html=True)
                except: pass
                
    st.markdown("<div class='section-title'>5. SEO Tags (490 Chars)</div>", unsafe_allow_html=True)
    st.code(res.get('tags', ''), language="text")
    
    st.write("")
    if st.button("🔄 重新開啟新企劃 (Start Over)", type="primary", use_container_width=True):
        reset_pipeline()
        st.rerun()

st.write("")
st.markdown(f"<div style='text-align: center; color: #8E8E93; font-size: 13px; margin-top: 50px;'>YouTube Title Studio v5.0<br>Developed by Leo Lai • Powered by Gemini 3 Flash Preview</div>", unsafe_allow_html=True)
