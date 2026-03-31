import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# ==========================================
# 1. 頁面設定與大師級 Pro UI CSS (完全卡片化、國際主導)
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

    /* 全域成品卡片設計 (Tab 4 用) */
    .glass-card { background-color: rgba(30, 30, 35, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; margin-bottom: 20px;backdrop-filter: blur(10px); }
    .section-title { font-size: 16px; font-weight: 700; color: #00ffcc; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;}
    .content-text { font-size: 15px; color: #E5E5EA; line-height: 1.6; }

    /* SEO 標題層次：英大中細 (Tab 4 用) */
    .score-badge-global { display: inline-block; font-size: 11px; font-weight: 700; color: #00E676; background: rgba(0, 230, 118, 0.1); padding: 2px 8px; border-radius: 4px; margin-bottom: 8px; }
    .en-main-global { font-size: 18px; font-weight: 600; color: #FFFFFF; margin-bottom: 4px; }
    .zh-sub-global { font-size: 14px; color: #8E8E93; }

    /* 按鈕發光與 Sticky 設計 */
    @keyframes pulse-glow { 0% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); } 50% { box-shadow: 0 0 20px rgba(0, 255, 204, 0.8); } 100% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); } }
    button[kind="primary"] { background: linear-gradient(90deg, #008080, #00E676) !important; animation: pulse-glow 2.5s infinite !important; border: none !important; font-weight: 700 !important; }
    
    /* Sticky Bottom Action Bar 設計 */
    .stApp > header {background-color: transparent !important;} /* 修復 Streamlit 頂部空白 */
    
    /* Step 1 的 Sticky Bar 需要注入到 block-container 底部 */
    div.stActionButton {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: rgba(20, 20, 22, 0.95);
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px 0;
        z-index: 1000;
        text-align: center;
    }
    div.stActionButton > div {
        max-width: 760px;
        margin: 0 auto;
        padding: 0 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 大師級卡片 (Bilingual Cards with States) CSS 注入
# ==========================================
def inject_bilingual_card_css():
    st.markdown("""
<style>
    /* 卡片容器 (2欄式 Grid 輔助) */
    .card-grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px; /* Gutter: 16px */
        margin-bottom: 20px;
    }

    /* 未選取 (Default) 卡片 */
    .bilingual-card {
        background-color: #FFFFFF; /* 白色背景 */
        border: 1px solid #DDDDDD; /* 細灰色邊框 */
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        color: #1C1C1E; /* 深色文字 */
    }

    /* 懸停 (Hover) 狀態 */
    .bilingual-card:hover {
        border-color: #4A90E2; /* 藍色邊框 */
        transform: translateY(-4px); /* 卡片微浮起 */
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    /* 已選取 (Selected) 狀態 */
    .bilingual-card.selected {
        background-color: #E6F0FA; /* 淺藍色背景 */
        border: 2.5px solid #4A90E2; /* 品牌色強調邊框，加粗 */
    }

    /* 已選取 Checkmark✅ ✅ ✅ ✅ ✅ ✅ */
    .bilingual-card.selected::after {
        content: '✅';
        position: absolute;
        top: 10px;
        right: 12px;
        font-size: 18px;
        z-index: 10;
    }

    /* 頂層（標題區） */
    .card-top {
        padding: 18px 20px;
        display: flex;
        align-items: flex-start;
        gap: 15px;
        position: relative;
    }

    /* 編號（小圓圈背景） */
    .card-id-circle {
        flex-shrink: 0;
        width: 28px;
        height: 28px;
        background-color: #F2F2F7;
        border-radius: 50%;
        color: #1C1C1E;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 14px;
        margin-top: 2px;
    }

    /* 歌名層次：國際主導 */
    .title-group {
        flex-grow: 1;
        margin-right: 25px; /* 為 Checkmark 留位 */
    }
    .en-title {
        font-size: 17px;
        font-weight: 700;
        color: #1C1C1E;
        margin-bottom: 2px;
        line-height: 1.3;
    }
    .zh-title {
        font-size: 13px;
        color: #8E8E93; /* 顏色稍淺 */
        font-weight: 500;
    }

    /* 底層（意境描述區）：灰底 */
    .card-bottom {
        background-color: #F8F9FA; /* 灰底 */
        border-top: 1px solid #EEEEEE;
        padding: 15px 20px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        flex-grow: 1;
    }

    /* Lyric Theme 圖示 (燈泡) */
    .theme-icon {
        flex-shrink: 0;
        font-size: 16px;
        color: #8E8E93;
        margin-top: 2px;
    }

    /* 文字內容採換行並列，且自動 Ellipsis */
    .theme-text-group {
        flex-grow: 1;
        font-size: 13px;
        color: #3A3A3C;
        line-height: 1.5;
        
        /* 字體限制： Ellipsis 多行 hidden */
        display: -webkit-box;
        -webkit-line-clamp: 2; /* 意境描述超過兩行Ellipsis */
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
        transition: all 0.2s ease;
    }
    
    /* 懸停或選取時展開全貌 */
    .bilingual-card:hover .theme-text-group,
    .bilingual-card.selected .theme-text-group {
        -webkit-line-clamp: initial;
        overflow: visible;
    }

    .theme-en { font-weight: 500; margin-bottom: 3px; }
    .theme-zh { color: #636366; }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 初始化流水線狀態 (Pipeline State)
# ==========================================
if "api_key" not in st.session_state: st.session_state.api_key = ""
if "step" not in st.session_state: st.session_state.step = 1
# 儲存數據
if "song_data" not in st.session_state: st.session_state.song_data = [] # 結構化歌單 [{"id":1, "en_title":"...", ...}]
if "selected_song_ids" not in st.session_state: st.session_state.selected_song_ids = []
if "concept_options" not in st.session_state: st.session_state.concept_options = []
if "selected_concept" not in st.session_state: st.session_state.selected_concept = None
if "final_results" not in st.session_state: st.session_state.final_results = {}

# 流程控制函數
def next_step(): st.session_state.step += 1
def reset_pipeline():
    for key in ["song_data", "selected_song_ids", "concept_options", "selected_concept", "final_results"]:
        st.session_state[key] = [] if "songs" in key or "options" in key else ({} if "results" in key else None)
    st.session_state.step = 1

# ==========================================
# API 連線視窗
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

# 主導航按鈕 (右上角)
col_nav, col_api = st.columns([8.5, 1.5])
with col_api:
    if st.button("🟢 已連線" if st.session_state.api_key else "🔑 連線", use_container_width=True) and not st.session_state.api_key: api_dialog()

st.markdown("<div class='ai-title'>YouTube Title Studio</div>", unsafe_allow_html=True)
st.markdown("<div class='ai-subtitle'>End-to-End Content Assembly Line • v6.0</div>", unsafe_allow_html=True)

if not st.session_state.api_key:
    # 未連線提示
    with st.container(border=True):
        st.markdown("#### 🔌 喚醒 Lofi 大師核心 (System Offline)")
        st.markdown("<span style='color:#8E8E93; font-size:14px;'>請貼上 Gemini API 金鑰以解鎖流水線功能。</span>", unsafe_allow_html=True)
        main_api = st.text_input("Gemini API Key", type="password", label_visibility="collapsed", key="main_api_key")
        if st.button("⚡ 快速初始化流水線", type="primary", use_container_width=True):
            if main_api:
                genai.configure(api_key=main_api)
                st.session_state.api_key = main_api
                st.rerun()
    st.stop()

# 模型就緒
genai.configure(api_key=st.session_state.api_key)
model = genai.GenerativeModel('gemini-3-flash-preview')

# ==========================================
# 頂部全域進度條 & 選擇計數
# ==========================================
progress_val = (st.session_state.step - 1) / 3
step_labels = ["Ideation", "Concept", "SEO Prep", "Dashboard"]
col_prog, col_count = st.columns([7, 3])
with col_prog:
    st.progress(progress_val, text=f"Pipeline Stage {st.session_state.step}/4: {step_labels[st.session_state.step-1]}")
with col_count:
    if st.session_state.step == 1 and st.session_state.song_data:
        st.markdown(f"<div style='text-align:right; color:#00ffcc; font-size:14px; font-weight:600; padding-top:2px;'>已選 {len(st.session_state.selected_song_ids)} / 20</div>", unsafe_allow_html=True)

st.write("")

# ==========================================
# Pipeline Step 1: 音樂靈感 (大師級卡片、多選)
# ==========================================
if st.session_state.step == 1:
    inject_bilingual_card_css()
    
    if not st.session_state.song_data:
        # 生成按鈕放在最醒目位置
        st.markdown("### 🎛️ Stage 1: Music Ideation (Suno 歌曲孵化)")
        if st.button("🪄 孵化 20 首治癒系英文歌曲主題 (感官溫暖・靈魂治癒)", type="primary", use_container_width=True):
            with st.spinner("AI 正在深度創作靈魂歌單..."):
                prompt = """我正在使用 SUNO AI 創作英文治癒系歌曲。請為我全新創作 20 首歌曲題目及其意境 (Lyric Theme)。
                核心情感：全然放鬆、心理停頓、和平、感官溫暖。
                嚴格遵守輸出格式（格式破壞則系統崩潰）：
                [編號]. 《[英文歌名]》 [中文譯名]
                Lyric Theme: [英文意境描述] — [中文意境描述]
                一定要生成夠 20 首。不要有任何前言或結語。"""
                resp = model.generate_content(prompt)
                
                # Parsing  Parsing Parsing: 結構化 Parsing
                raw_text = resp.text.strip()
                # 使用 Regex 匹配 [編號]. 《[英文]》 [中文]\nLyric Theme: [英文] — [中文]
                pattern = r"(\d+)\.\s+《(.*?)》\s+(.*?)\nLyric Theme:\s+(.*?)\s+—\s+(.*)"
                matches = re.findall(pattern, raw_text)
                
                parsed_songs = []
                for m in matches:
                    parsed_songs.append({
                        "id": int(m[0]),
                        "en_title": m[1].strip(),
                        "zh_title": m[2].strip(),
                        "en_theme": m[3].strip(),
                        "zh_theme": m[4].strip()
                    })
                
                st.session_state.song_data = parsed_songs
                st.rerun()
    else:
        # 顯示 20 首卡片 (兩欄式排列)
        st.markdown("### 🎛️ Stage 1: Select Your Aesthetic Songs")
        st.markdown("<span style='color:#8E8E93; font-size:14px;'>請「按需選擇」，剔選多首心水歌曲 (可多選)。</span>", unsafe_allow_html=True)
        st.write("")

        # 建立 2 columns Grid
        col1, col2 = st.columns(2, gap="medium") # Gutter: 16px
        
        # 排序 ID，分為兩欄
        sorted_songs = sorted(st.session_state.song_data, key=lambda x: x['id'])
        
        # 輔助函數：生成卡片 HTML
        def generate_card_html(song, is_selected):
            selected_class = "selected" if is_selected else ""
            return f"""
            <div class='bilingual-card {selected_class}'>
                <div class='card-top'>
                    <div class='card-id-circle'>{song['id']}</div>
                    <div class='title-group'>
                        <div class='en-title'>{song['en_title']}</div>
                        <div class='zh-title'>{song['zh_title']}</div>
                    </div>
                </div>
                <div class='card-bottom'>
                    <div class='theme-icon'>💡</div>
                    <div class='theme-text-group'>
                        <div class='theme-en'>Lyric Theme: {song['en_theme']}</div>
                        <div class='theme-zh'>— {song['zh_theme']}</div>
                    </div>
                </div>
            </div>
            """

        new_selected_ids = []

        # 兩欄式渲染
        for idx, song in enumerate(sorted_songs):
            target_col = col1 if idx % 2 == 0 else col2
            with target_col:
                is_selected = song['id'] in st.session_state.selected_song_ids
                
                # 1. 顯示 HTML 卡片 (有 hover/selected 狀態)
                st.markdown(generate_card_html(song, is_selected), unsafe_allow_html=True)
                
                # 2. 卡片下方跟一個 st.checkbox 用作真正選擇邏輯 (隱藏 label)
                # 使用歌名做 Key，確保唯一
                checkbox_key = f"select_{song['id']}_{song['en_title']}"
                if st.checkbox("Select", key=checkbox_key, value=is_selected, label_visibility="collapsed"):
                    new_selected_ids.append(song['id'])
                
                # 在卡片與卡片之間留白 (模擬 Grid 效果)
                st.write("") 

        # 底部固定動作列 (Sticky Action Bar) ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅
        st.markdown('<div class="stActionButton"><div>', unsafe_allow_html=True)
        if st.button("確認選擇，進入下一步 ️(Visual Concept) ➡️", type="primary", use_container_width=True):
            if not new_selected_ids:
                st.warning("喂喂，請至少剔選一首歌曲先！")
            else:
                st.session_state.selected_song_ids = new_selected_ids
                next_step()
                st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

# ==========================================
# Pipeline Step 2: 視覺意境 (極簡中英短句)
# ==========================================
elif st.session_state.step == 2:
    st.markdown("### 🎬 Stage 2: Visual Concept (設定感官意境)")
    
    if not st.session_state.selected_song_ids:
        st.warning("⚠️ 請先返去 Stage 1 揀選一首歌曲。")
        if st.button("⬅️ 返去 Stage 1"):
            st.session_state.step = 1
            st.rerun()
    else:
        st.write("設定一個極度放鬆、慵懶嘅感官情境。可以自定義時間同氛圍。")
        vibe = st.text_input("自定義時間與氛圍 (留空則由 AI 隨機安排)", placeholder="例如：落雨嘅深夜，一個人喺房溫書放空...")
        
        if st.button("🧠 構思 3 個極簡故事方向", type="primary", use_container_width=True):
            with st.spinner("AI 正在提取視覺靈感..."):
                # 提取已選歌名
                sel_songs = [s['en_title'] for s in st.session_state.song_data if s['id'] in st.session_state.selected_song_ids]
                songs_context = " / ".join(sel_songs)
                context = vibe if vibe else "隨機生成極度放鬆的 Blue Hour 或深夜生活日常細節 (嚴禁Dust)"
                prompt = f"""基於以下歌曲：{songs_context}
                情境設定：{context}
                請提供 3 個不同的「極簡故事意境選項」。
                要求：中英對照，非常簡短，具畫面感。
                格式必須為：[Emoji] [中文短意境] | [English short vibe] (不超過 20 字)
                例如：☔ 微雨的窗邊放空 | Spacing out by the rainy window
                每行一個，不要加數字。"""
                resp = model.generate_content(prompt)
                
                # 清除舊選項，確保不寫死
                st.session_state.concept_options = [line.strip() for line in resp.text.strip().split('\n') if "|" in line]
        
        if st.session_state.concept_options:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("#### 請選擇一個視覺故事方向：")
            st.markdown("<span style='color:#8E8E93; font-size:13px;'>揀選一個作為生成長、短故事嘅核心。</span>", unsafe_allow_html=True)
            st.write("")
            
            sel_concept = st.radio("Story Direction", st.session_state.concept_options, label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
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
    st.baloons_once() if "baloons_done" not in st.session_state else None
    st.session_state.baloons_done = True

    if not st.session_state.selected_concept:
        st.warning("⚠️ 步驟錯誤：請先完成 Stage 2。")
        st.stop()

    with st.container(border=True):
        st.markdown("#### 👁️ 上傳視覺特徵 (Thumbnail)")
        st.markdown("<span style='color:#8E8E93; font-size:14px;'>Upload 您生成好嘅靚圖 (可選，有齊圖文生成更精準)。</span>", unsafe_allow_html=True)
        st.write("")
        uploaded_img = st.file_uploader("Upload Thumb (JPG/PNG)", type=["jpg", "png"], label_visibility="collapsed")
        if uploaded_img: st.image(uploaded_img, use_container_width=True)
    
    st.write("")
    
    col_back, col_gen = st.columns(2)
    if col_back.button("⬅️ 返回重選意境", use_container_width=True):
        st.session_state.step = 2
        st.rerun()
        
    if col_gen.button("🚀 啟動全線終極生成 (Generate All)!", type="primary", use_container_width=True):
        with st.status("⚙️ 生產線全面運作中 (The Magic is happening)...", expanded=True) as status:
            st.write("1. 濃縮 300 字慵懶感官故事...")
            st.write("2. 創作精簡 Emoji 生活日常短故事...")
            st.write("3. 打包 490 字元黃金流量標籤...")
            
            # 準備 Payload
            songs_context = [s['en_title'] for s in st.session_state.song_data if s['id'] in st.session_state.selected_song_ids]
            context_str = f"Songs: {'/'.join(songs_context)}\nVibe: {st.session_state.selected_concept}"
            
            payload = [context_str]
            if uploaded_img: payload.append(Image.open(uploaded_img))
            
            # 終極 Prompt (不要生成 Image Prompt)
            prompt = f"""你是 YouTube Lofi 音樂頻道總監。請根據以上歌曲設定、視覺意境及圖片（如有），一次過輸出以下最終內容。
            賣的是「共鳴」同「 companionship」，賣為聽眾提供一個「心理停頓、放鬆、心理療癒」嘅解決方案。
            
            【嚴格輸出格式，使用 === 分隔，遵守格式否則系統崩潰】：
            
            ===LONG_STORY===
            寫一個約 300 字的英文慵懶感官描述故事 (Detailed Story)，極度放鬆且充滿溫馨感。描述光影、質感、慵懶的狀態。不要太長。
            
            ===SHORT_STORY===
            精簡為約 100 字嘅「生活化、微小、帶有 Emoji 嘅 reflective/conversational」短句故事。
            要好似 Making Tea 例子一樣，中英對照格式：[English Sentence] + [Emoji]\n[English Sentence] + [Emoji]...
            不要有開場白或解釋。
            
            ===TITLES===
            提供 5 個極具點擊率 (CTR) 嘅中英對照標題 (格式: 分數|||中文|||英文)。
            英文標題要大字 (國際主導)，中文細字。
            英文格式嚴格跟隨黃金結構：[Poetic Phrase]… [曲風] for [活動1], [活動2] & [氛圍] [2個Emoji]
            
            ===TAGS===
            直接輸出一連串逗號分隔的 Tags，包含 lofi hip hop radio, beats to relax/study to 等大熱流量字。
            總字元長度必須嚴格控制在 450 到 490 之間！絕對不能超過 490 字元！
            """
            
            payload.insert(0, prompt)
            
            try:
                resp = model.generate_content(payload)
                raw_text = resp.text
                
                # 簡單 Parsing Parsing Parsing
                parts = raw_text.split("===")
                
                story_long = next((p for p in parts if "LONG_STORY" in p), "").replace("LONG_STORY", "").strip()
                story_short = next((p for p in parts if "SHORT_STORY" in p), "").replace("SHORT_STORY", "").strip()
                titles = next((p for p in parts if "TITLES" in p), "").replace("TITLES", "").strip()
                tags = next((p for p in parts if "TAGS" in p), "").replace("TAGS", "").strip()
                
                # 儲存結果
                st.session_state.final_results = {
                    "story_long": story_long,
                    "story_short": story_short,
                    "titles": titles,
                    "tags": tags
                }
                
                status.update(label="✅ 生成完畢！成品已傳輸至總結 Dashboard。", state="complete", expanded=False)
                st.toast('✨Integrated Magic generated successfully!', icon='🎉')
                next_step()
                st.rerun()
                
            except Exception as e:
                status.update(label="❌ 生成中斷", state="error")
                st.error(f"系統異常: {e}")

# ==========================================
# Pipeline Step 4: 最終成品總結 (Wizard Complete)
# ==========================================
elif st.session_state.step == 4:
    st.markdown("### 🎉 Stage 4: Wizard Complete -成品 Dashboard")
    st.balloons()
    
    if not st.session_state.final_results:
        st.warning("⚠️ 沒有生成結果，請返去完成流水線。")
        reset_pipeline()
        st.rerun()
        st.stop()
        
    res = st.session_state.final_results
    
    # 使用卡片顯示成果 ✅ ✅ ✅ ✅ ✅ ✅ ✅
    with st.container(border=True):
        col1, col2 = st.columns([7, 3])
        with col1:
            st.markdown("<div class='section-title'>1. Selected Songs & Aesthetic Concept</div>", unsafe_allow_html=True)
            # 顯示已選歌名 En/Zh
            sel_songs_titles = [f"《{s['en_title']}》 ({s['zh_title']})" for s in st.session_state.song_data if s['id'] in st.session_state.selected_song_ids]
            st.markdown(f"<div class='content-text'>🎵 {'<br>🎵 '.join(sel_songs_titles)}<br><br>🎬 {st.session_state.selected_concept}</div>", unsafe_allow_html=True)
        with col2:
             st.markdown("<div style='text-align:right;'>"+"\n".join([f"<img src='{s['image']}' style='width:60px; height:40px; border-radius:4px; margin-left:5px;'/>" for s in st.session_state.song_data if s['id'] in st.session_state.selected_song_ids and 'image' in s])+"</div>", unsafe_allow_html=True) # 如有圖顯示


    # 長故事
    with st.markdown("<div class='glass-card'>", unsafe_allow_html=True):
        st.markdown("<div class='section-title'>2. Detailed Vibe Story (300 words)</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='content-text'>{res.get('story_long', '請檢查格式')}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 短故事
    with st.markdown("<div class='glass-card'>", unsafe_allow_html=True):
        st.markdown("<div class='section-title'>3. Short Reflective Story (帶有 Emoji)</div>", unsafe_allow_html=True)
        st.code(res.get('story_short', '請檢查格式'), language="text")
    st.markdown("</div>", unsafe_allow_html=True)

    # YouTube 標題與 Tags
    st.markdown("#### 4. YouTube SEO 包裝結果 (國際主導)")
    
    # 標題卡片
    for line in res.get('titles', '').split('\n'):
        line = line.replace("*", "").strip()
        if "|||" in line:
            try:
                score, zh, en = line.split("|||")
                st.markdown(f"""
                <div style='background-color: rgba(30, 30, 35, 0.8); border: 1px solid rgba(0, 255, 204, 0.3); border-radius: 8px; padding: 15px; margin-bottom: 10px;'>
                    <div class='score-badge-global'>🔥 CTR: {score.strip()}/100</div>
                    <div class='en-main-global'>{en.strip()}</div>
                    <div class='zh-sub-global'>{zh.strip()}</div>
                </div>
                """, unsafe_allow_html=True)
            except: pass
            
    # Tags
    st.code(res.get('tags', ''), language="text")
    
    st.write("")
    if st.button("🔄 重置全線流程，開始新企劃", type="primary", use_container_width=True):
        reset_pipeline()
        st.rerun()

st.write("")
st.markdown(f"<div style='text-align: center; color: #8E8E93; font-size: 13px; margin-top: 50px; margin-bottom: 30px; opacity: 0.7;'>YouTube Title Studio v6.0<br>Developed by Leo Lai • Powered by Gemini 3 Flash Preview</div>", unsafe_allow_html=True)
