import streamlit as st
import google.generativeai as genai
from PIL import Image
import random

# ==========================================
# 1. 頁面設定與 AI 賽博龐克 CSS
# ==========================================
st.set_page_config(page_title="YouTube Title Studio", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    
    /* 流光標題動畫 */
    @keyframes gradient-text { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .ai-title { font-weight: 800; font-size: 42px; text-align: center; background: linear-gradient(270deg, #00E676, #00ffcc, #b026ff, #00E676); background-size: 300% 300%; animation: gradient-text 4s ease infinite; -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .ai-subtitle { color: #8E8E93; font-size: 16px; text-align: center; margin-bottom: 25px; letter-spacing: 1px; }

    /* 卡片設計 */
    .glass-card { background-color: rgba(20, 20, 22, 0.7); border: 1px solid rgba(0, 255, 204, 0.15); border-radius: 12px; padding: 20px; margin-bottom: 20px; backdrop-filter: blur(10px); }
    .title-card { background-color: rgba(30, 30, 35, 0.8); border: 1px solid rgba(0, 255, 204, 0.3); border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .score-badge { display: inline-block; font-size: 11px; font-weight: 700; color: #00E676; background: rgba(0, 230, 118, 0.1); padding: 2px 8px; border-radius: 4px; margin-bottom: 8px; }
    
    /* 標題層次：英大中細 */
    .en-main { font-size: 18px; font-weight: 600; color: #FFFFFF; margin-bottom: 4px; }
    .zh-sub { font-size: 14px; color: #8E8E93; }

    /* 按鈕發光 */
    @keyframes pulse-glow { 0% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); } 50% { box-shadow: 0 0 20px rgba(0, 255, 204, 0.8); } 100% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); } }
    button[kind="primary"] { background: linear-gradient(90deg, #008080, #00E676) !important; animation: pulse-glow 2.5s infinite !important; border: none !important; }
</style>
""", unsafe_allow_html=True)

# 初始化 Session State (記憶系統)
if "api_key" not in st.session_state: st.session_state.api_key = ""
if "step1_results" not in st.session_state: st.session_state.step1_results = []
if "selected_song" not in st.session_state: st.session_state.selected_song = None
if "step2_concepts" not in st.session_state: st.session_state.step2_concepts = []
if "selected_concept" not in st.session_state: st.session_state.selected_concept = None
if "long_story" not in st.session_state: st.session_state.long_story = None
if "image_prompt" not in st.session_state: st.session_state.image_prompt = None
if "final_titles" not in st.session_state: st.session_state.final_titles = []
if "final_tags" not in st.session_state: st.session_state.final_tags = ""

# ==========================================
# 2. API 連線視窗
# ==========================================
@st.dialog("⚡ AI 核心連線")
def api_dialog():
    api_input = st.text_input("Enter Gemini API Key", type="password", key="dialog_api")
    if st.button("啟動連線", use_container_width=True):
        if api_input:
            try:
                genai.configure(api_key=api_input)
                genai.get_model('models/gemini-3-flash-preview')
                st.session_state.api_key = api_input
                st.rerun()
            except: st.error("Invalid Key.")

# 頂部導航
col_title, col_btn = st.columns([8, 2])
with col_btn:
    label = "🟢 已連線" if st.session_state.api_key else "🔑 連線"
    if st.button(label, use_container_width=True): api_dialog()

st.markdown("<div class='ai-title'>YouTube Title Studio</div>", unsafe_allow_html=True)
st.markdown("<div class='ai-subtitle'>End-to-End Lofi Content Workflow • v4.0</div>", unsafe_allow_html=True)

if not st.session_state.api_key:
    st.info("👋 歡迎！請先輸入 API Key 以喚醒 AI 創作核心。")
    main_api = st.text_input("Gemini API Key", type="password", key="main_api_key")
    if st.button("⚡ 快速初始化", type="primary", use_container_width=True):
        if main_api:
            genai.configure(api_key=main_api)
            st.session_state.api_key = main_api
            st.rerun()
else:
    # 定義模型
    genai.configure(api_key=st.session_state.api_key)
    model = genai.GenerativeModel('gemini-3-flash-preview')

    # ==========================================
    # 3. 三大功能分頁
    # ==========================================
    tab1, tab2, tab3, tab4 = st.tabs(["🎵 音樂靈感", "🖼️ 視覺故事", "🚀 SEO 包裝", "📋 最終成品"])

    # ---- Tab 1: Suno Ideation ----
    with tab1:
        st.markdown("### 1. Suno AI 歌曲孵化")
        if st.button("🪄 生成 20 首治癒系歌曲靈感", type="primary"):
            with st.status("正在創作靈魂治癒音樂主題..."):
                prompt = """
                我正在使用 SUNO AI 創作英文治癒系歌曲。請為我全新創作 20 首歌曲題目及其意境 (Lyric Theme)。
                要求：核心情感傳遞『全然放鬆、心理停頓、和平、感官溫暖』。使用具體感官細節。
                格式：[編號]. 《[英文歌名]》 [中文譯名] |意境| [英文意境] — [中文意境]
                """
                response = model.generate_content(prompt)
                lines = response.text.strip().split('\n')
                st.session_state.step1_results = [l for l in lines if "《" in l]
        
        if st.session_state.step1_results:
            selected = st.radio("揀選一首你最鍾意嘅主題：", st.session_state.step1_results)
            if st.button("✅ 確定主題並進入下一步"):
                st.session_state.selected_song = selected
                st.success(f"已選定：{selected}")

    # ---- Tab 2: Visual Storyteller ----
    with tab2:
        st.markdown("### 2. 視覺故事與繪圖提示詞")
        if not st.session_state.selected_song:
            st.warning("請先喺 Tab 1 揀選一個音樂主題。")
        else:
            time_vibe = st.text_input("自定義時間與氛圍 (留空則由 AI 隨機)", placeholder="例如：凌晨兩點，窗外微雨...")
            if st.button("🧠 生成 3 個故事大綱", type="primary"):
                with st.status("正在構思視覺場景..."):
                    context = time_vibe if time_vibe else "晚上 7:30 (The Blue Hour), 暖燈與深藍夜色, 極度放鬆"
                    prompt = f"""
                    基於歌曲主題：{st.session_state.selected_song}
                    情境設定：{context}
                    請生成 3 個 Chill R&B 曲風的英文短故事大綱 (約 100 字)。
                    要求：微小且放鬆的動作（如聽唱片、對著熱氣放空）。
                    格式：[編號] ||| [標題] ||| [大綱內容]
                    """
                    response = model.generate_content(prompt)
                    st.session_state.step2_concepts = [l for l in response.text.strip().split('\n') if "|||" in l]
            
            if st.session_state.step2_concepts:
                sel_concept = st.radio("揀選一個故事方向：", st.session_state.step2_concepts)
                if st.button("✍️ 擴寫長篇故事與 Prompt"):
                    with st.status("正在撰寫感官長文..."):
                        prompt = f"請將此大綱擴寫：{sel_concept}。要求：1. [Detailed Story] 約 1000 字英文感官描述。2. [Short Version] 約 500 字 Image Prompt。"
                        resp = model.generate_content(prompt)
                        st.session_state.selected_concept = sel_concept
                        st.session_state.long_story = resp.text
                        st.success("故事已準備就緒！")
                        st.markdown(st.session_state.long_story)

    # ---- Tab 3: SEO Publisher ----
    with tab3:
        st.markdown("### 3. YouTube SEO 包裝")
        uploaded_img = st.file_uploader("上傳封面圖 (可選)", type=["jpg", "png"])
        if uploaded_img: st.image(uploaded_img, use_container_width=True)
        
        if st.button("🔥 生成流量標題與 Tags", type="primary"):
            with st.status("正在運算流量密碼..."):
                payload = [st.session_state.long_story if st.session_state.long_story else st.session_state.selected_song]
                if uploaded_img: payload.append(Image.open(uploaded_img))
                
                prompt = """
                請根據以上內容生成 5 個中英對照標題 (分數|||中文|||英文) 及 490 字元內的 Tags。
                標題格式：[短句]… [曲風] for [活動] & [氛圍] [Emoji]
                英文標題要大字，中文細字。Tags 嚴格控制在 450-490 字元。
                """
                payload.insert(0, prompt)
                response = model.generate_content(payload)
                parts = response.text.split("===TAGS===") if "===TAGS===" in response.text else response.text.split("Tags:")
                st.session_state.final_titles = parts[0].strip().split('\n')
                st.session_state.final_tags = parts[1].strip() if len(parts)>1 else "請檢查輸出格式"

        if st.session_state.final_titles:
            for line in st.session_state.final_titles:
                if "|||" in line:
                    score, zh, en = line.split("|||")
                    st.markdown(f"<div class='title-card'><div class='score-badge'>CTR: {score}/100</div><div class='en-main'>{en}</div><div class='zh-sub'>{zh}</div></div>", unsafe_allow_html=True)
            st.code(st.session_state.final_tags)

    # ---- Tab 4: Final Summary ----
    with tab4:
        st.markdown("### 📋 最終成品總結")
        if not st.session_state.selected_song:
            st.info("完成所有步驟後，呢度會顯示完整清單。")
        else:
            with st.container(border=True):
                st.subheader("🎵 音樂設定")
                st.write(st.session_state.selected_song)
                st.divider()
                st.subheader("📖 視覺劇本")
                st.write(st.session_state.long_story)
                st.divider()
                st.subheader("🚀 SEO 標籤")
                st.code(st.session_state.final_tags)
            if st.button("🧹 重設並開始新創作"):
                for key in list(st.session_state.keys()): 
                    if key != "api_key": del st.session_state[key]
                st.rerun()

st.markdown(f"<div style='text-align: center; color: #8E8E93; font-size: 13px; margin-top: 40px;'>YouTube Title Studio v4.0<br>Developed by Leo Lai • Powered by Gemini 3 Flash Preview</div>", unsafe_allow_html=True)
