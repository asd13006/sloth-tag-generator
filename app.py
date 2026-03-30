import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 1. 頁面基礎設定與 AI 微動畫 CSS
# ==========================================
# 【改動 1】：更改瀏覽器 Tab 標題
st.set_page_config(page_title="YouTube Title Studio", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    @keyframes gradient-text {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .ai-title {
        font-weight: 800;
        font-size: 42px;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
        text-align: center;
        background: linear-gradient(270deg, #00E676, #00ffcc, #b026ff, #00E676);
        background-size: 300% 300%;
        animation: gradient-text 4s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .ai-subtitle {
        color: #8E8E93;
        font-size: 16px;
        text-align: center;
        margin-bottom: 25px;
        font-weight: 500;
        letter-spacing: 1px;
    }
    
    .title-card {
        background-color: rgba(20, 20, 22, 0.7);
        border: 1px solid rgba(0, 255, 204, 0.15);
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .title-card:hover {
        background-color: rgba(30, 30, 35, 0.9);
        border: 1px solid rgba(0, 255, 204, 0.6);
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.2);
        transform: translateY(-4px);
    }
    
    .score-badge {
        display: inline-block;
        font-size: 12px;
        font-weight: 700;
        color: #00E676;
        background: rgba(0, 230, 118, 0.1);
        border: 1px solid rgba(0, 230, 118, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    
    .en-title {
        font-size: 18px;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 6px;
        line-height: 1.4;
    }
    .zh-title {
        font-size: 14px;
        color: #8E8E93;
        line-height: 1.4;
    }
    
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); }
        50% { box-shadow: 0 0 20px rgba(0, 255, 204, 0.8); }
        100% { box-shadow: 0 0 5px rgba(0, 255, 204, 0.4); }
    }
    button[kind="primary"] {
        background: linear-gradient(90deg, #008080, #00E676) !important;
        border: none !important;
        color: #fff !important;
        font-weight: bold !important;
        animation: pulse-glow 2.5s infinite !important;
        transition: transform 0.2s !important;
    }
    button[kind="primary"]:hover {
        transform: scale(1.02) !important;
    }
    
    .block-container {
        padding-top: 1.5rem;
        max-width: 760px;
    }
</style>
""", unsafe_allow_html=True)

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ==========================================
# 2. 彈出式視窗 (Dialog)
# ==========================================
@st.dialog("⚡ AI 核心連線 (API Authentication)")
def api_connection_dialog():
    st.markdown("請輸入您的 Gemini API Key 以啟動神經網絡。")
    api_input = st.text_input("API Key", type="password", placeholder="AIzaSy...")
    
    if st.button("啟動連線", use_container_width=True):
        if api_input:
            with st.spinner("Authenticating..."):
                try:
                    genai.configure(api_key=api_input)
                    genai.get_model('models/gemini-3-flash-preview')
                    st.session_state.api_key = api_input
                    st.rerun()
                except Exception as e:
                    st.error("連線失敗：無效的金鑰。")
        else:
            st.warning("請輸入金鑰。")

@st.dialog("🟢 系統狀態")
def disconnect_dialog():
    st.success("AI 核心已成功連線，狀態良好。")
    if st.button("斷開連線 (Disconnect)", use_container_width=True):
        st.session_state.api_key = ""
        st.rerun()

# ==========================================
# 3. 頂部導航欄
# ==========================================
col_space, col_btn = st.columns([8.5, 1.5])
with col_btn:
    if not st.session_state.api_key:
        if st.button("🔑 連線", use_container_width=True):
            api_connection_dialog()
    else:
        if st.button("🟢 已連線", use_container_width=True):
            disconnect_dialog()

# ==========================================
# 4. 主畫面
# ==========================================
# 【改動 2】：更改主畫面標題
st.markdown("<div class='ai-title'>YouTube Title Studio</div>", unsafe_allow_html=True)
st.markdown("<div class='ai-subtitle'>Aesthetic Generation Core • Powered by Gemini 3</div>", unsafe_allow_html=True)

if not st.session_state.api_key:
    st.info("⚠️ 系統處於休眠狀態：請點擊右上角「🔑 連線」按鈕以喚醒 AI。")
else:
    genai.configure(api_key=st.session_state.api_key)
    model = genai.GenerativeModel('gemini-3-flash-preview')

    with st.container(border=True):
        st.markdown("#### 👁️ 視覺與情境輸入 (至少提供一項)")
        uploaded_file = st.file_uploader("匯入視覺特徵 (JPG/PNG)", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
            
        st.write("")
        video_story = st.text_area("設定情境參數 (Vibe, Story & Time)", height=100, placeholder="可選填。例如：凌晨兩點，趕功課趕到好累，窗外雨越落越大...")

    st.write("")
    
    generate_btn = st.button("✨ 啟動神經生成 (Execute Magic)", type="primary", use_container_width=True)

    if generate_btn:
        if uploaded_file or video_story:
            with st.status("🤖 神經網絡深度解析中...", expanded=True) as status:
                
                payload = []
                context_desc = ""
                
                if uploaded_file and video_story:
                    st.write("掃描圖片視覺特徵與解讀情境故事...")
                    context_desc = f"請根據提供嘅圖片視覺和以下氛圍描述：{video_story}"
                    payload.append(image)
                elif uploaded_file:
                    st.write("掃描圖片視覺特徵...")
                    context_desc = "請單純根據提供嘅圖片視覺氛圍"
                    payload.append(image)
                elif video_story:
                    st.write("解讀情境故事...")
                    context_desc = f"請單純根據以下氛圍描述：{video_story}"
                
                st.write("套用黃金三段式 Aesthetic 標題結構...")
                st.write("最佳化 490 字元流量標籤...")
                
                try:
                    prompt = f"""
                    你而家係一位深受大學生同失眠人士喜愛嘅 Lofi 電台策劃師。
                    {context_desc}，為頻道 sLoth rAdio 創作標題和標籤。
                    
                    【輸出格式】：
                    
                    ===TITLES===
                    提供 5 個極具點擊率 (CTR) 嘅中英對照標題 (格式: 分數|||中文標題|||英文標題)。
                    
                    【標題創作法則 - 絕對指令】：
                    1. 英文標題格式必須 100% 嚴格跟隨以下結構 (請留意省略號 ... 後面有一個半形空格)：
                       [極簡生活感短句]… [音樂曲風] for [活動1], [活動2] & [氛圍] [2個Emoji]
                       
                       參考例子：
                       - Cozy Tea Moments… Chill Lofi for Relaxation, Study & Calm 🍵 🌙
                       - A cozy place to study… Chill R&B for Golden Hour Focus & Slow Living 🌅 📚
                       
                    2. 音樂曲風 (Genre)：請根據圖片或氛圍靈活替換，例如 Chill Lofi, Chill R&B, Peaceful Beats, Cozy Jazz 等。
                    3. 中文標題：將英文標題轉化為語感自然、帶有陪伴感的生活化中文。
                    4. 格式：每個標題給出一個評分 (0-100)，並使用 `|||` 分隔。不要加序號。
                    
                    ===TAGS===
                    直接輸出一連串由逗號和半形空格分隔的 Tags。
                    包含 lofi hip hop radio, beats to relax/study to 等大熱字眼。
                    【字數警告】：總字元長度必須嚴格控制在 450 到 490 之間！絕對不能超過 490 字元！不可分類。
                    """
                    
                    payload.insert(0, prompt)
                    
                    response = model.generate_content(payload)
                    result_text = response.text
                    
                    parts = result_text.split("===TAGS===")
                    titles_part = parts[0].replace("===TITLES===", "").strip()
                    tags_part = parts[1].strip() if len(parts) > 1 else ""
                    
                    status.update(label="✅ 生成完畢！數據已傳輸。", state="complete", expanded=False)
                    st.toast('✨ 神經網絡生成成功！', icon='🤖')
                    
                    st.write("")
                    st.markdown("#### 💬 最佳化共鳴標題")
                    
                    for line in titles_part.split('\n'):
                        line = line.replace("*", "").strip()
                        if "|||" in line:
                            try:
                                score, zh_title, en_title = line.split("|||")
                                st.markdown(f"""
                                <div class='title-card'>
                                    <div class='score-badge'>🔥 AI 預測點擊率: {score.strip()}/100</div>
                                    <div class='en-title'>{en_title.strip()}</div>
                                    <div class='zh-title'>{zh_title.strip()}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            except:
                                pass
                    
                    st.write("")
                    st.markdown("#### 🏷️ 流量最佳化標籤")
                    
                    char_count = len(tags_part)
                    col_tags, col_metric = st.columns([3, 1])
                    
                    with col_metric:
                        st.metric(label="Characters", value=f"{char_count}", delta=f"{490 - char_count} 剩餘", delta_color="normal")
                            
                    with col_tags:
                        st.code(tags_part, language="text")
                        if char_count > 490:
                            st.caption("⚠️ 標籤稍微超過安全限制，複製前請刪減結尾。")
                        else:
                            st.caption("✅ 長度完美，已就緒。")
                    
                except Exception as e:
                    status.update(label="❌ 運算中斷", state="error")
                    st.error(f"系統錯誤：{e}")
        else:
            st.warning("⚠️ 喂喂，請至少上傳一張圖片，或者輸入少少情境故事，先可以施展魔法㗎！")
            
    st.write("")
    # 【改動 3】：底部加入版本號及署名
    st.markdown("<div style='text-align: center; color: #8E8E93; font-size: 13px; margin-top: 40px; opacity: 0.7;'>YouTube Title Studio v3.4<br>Developed by Leo Lai • Powered by Gemini 3 Flash Preview</div>", unsafe_allow_html=True)
