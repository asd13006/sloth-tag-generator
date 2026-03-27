import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 頁面基礎設定
st.set_page_config(page_title="sLoth AI Core", page_icon="🤖", layout="wide")

# ==========================================
# 自訂 CSS (注入 AI 科技感與發光效果)
# ==========================================
st.markdown("""
<style>
    .ai-title {
        font-family: 'Courier New', Courier, monospace;
        color: #00ffcc;
        text-shadow: 0px 0px 10px rgba(0, 255, 204, 0.8);
        text-align: center;
        font-weight: bold;
        margin-bottom: 0px;
    }
    .ai-subtitle {
        font-family: 'Courier New', Courier, monospace;
        text-align: center;
        color: #8892b0;
        font-size: 14px;
        margin-bottom: 40px;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ==========================================
# 側邊欄：認證系統 (保持簡潔)
# ==========================================
with st.sidebar:
    st.header("🔑 SYSTEM.AUTH")
    if not st.session_state.api_key:
        api_input = st.text_input("輸入 API 金鑰以啟動神經網絡", type="password")
        if st.button("INITIALIZE // 啟動連線", type="primary", use_container_width=True):
            if api_input:
                with st.spinner("Authenticating..."):
                    try:
                        genai.configure(api_key=api_input)
                        genai.get_model('models/gemini-2.5-flash')
                        st.session_state.api_key = api_input
                        st.rerun()
                    except Exception as e:
                        st.error("連線被拒絕。請檢查金鑰。")
    else:
        st.success("🟢 核心系統已連線")
        if st.button("TERMINATE // 斷開連線", use_container_width=True):
            st.session_state.api_key = ""
            st.rerun()

# ==========================================
# 主畫面：AI 核心介面
# ==========================================
st.markdown("<h1 class='ai-title'>⚙️ sLoth.AI // TAG_GENERATOR_V2</h1>", unsafe_allow_html=True)
st.markdown("<div class='ai-subtitle'>[ SYSTEM ONLINE ] 多模態神經網絡準備就緒，等候指令...</div>", unsafe_allow_html=True)

if not st.session_state.api_key:
    st.info("⚠️ 系統鎖定中：請於左側控制台進行身份認證。")
else:
    genai.configure(api_key=st.session_state.api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    col_img, col_text = st.columns([4, 6], gap="large")

    with col_img:
        st.markdown("### 👁️ 視覺輸入模組 (Visual Input)")
        uploaded_file = st.file_uploader("匯入視覺數據 (JPG/PNG)", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)

    with col_text:
        st.markdown("### 🧠 語義輸入模組 (Context Input)")
        video_title = st.text_input("資料軌跡 A：影片標題", placeholder="輸入標題...")
        video_story = st.text_area("資料軌跡 B：氛圍與故事參數", height=150, placeholder="輸入情境描述...")

    st.write("")
    col_empty, col_btn, col_empty2 = st.columns([1, 2, 1])
    with col_btn:
        generate_btn = st.button("⚡ EXECUTE // 生成最佳化標籤", type="primary", use_container_width=True)

    # 執行邏輯
    if generate_btn:
        if uploaded_file and video_title and video_story:
            # 使用 AI 感嘅狀態欄 (Status) 代替普通 spinner
            with st.status("🤖 神經網絡正在解析多模態數據...", expanded=True) as status:
                st.write("掃描視覺像素特徵中...")
                st.write("正在提取標題與故事語義...")
                st.write("運算最高轉換率之標籤組合...")
                
                try:
                    # 全新 Prompt：直接要求 500 字元內嘅平鋪格式
                    prompt = f"""
                    你而家係 YouTube 演算法底層嘅分析 AI。
                    請深度分析圖片視覺元素，並結合以下標題同故事，提取出最高潛力嘅 YouTube 標籤。
                    
                    頻道屬性：Lofi, Chillhop, 放鬆, 治癒
                    影片標題：{video_title}
                    背景故事：{video_story}
                    
                    【嚴格輸出格式限制】：
                    1. 絕對唔需要分類，亦唔需要任何開場白或解釋。
                    2. 請直接輸出一連串由逗號分隔嘅 Tags (例如：lofi hip hop, chill beats, 讀書音樂, ...)。
                    3. 總長度必須盡量逼近但【不能超過】 500 個字元 (Characters)，以符合 YouTube 上限。
                    4. 標籤要混合大路搜尋詞、長尾情境詞同視覺氛圍詞。
                    """
                    
                    response = model.generate_content([prompt, image])
                    
                    status.update(label="✅ 分析完成！數據已輸出。", state="complete", expanded=False)
                    
                    st.divider()
                    st.markdown("### 📤 最終輸出數據 (Output Data)")
                    
                    # 計算字元數，提水畀用家睇下有冇超標
                    char_count = len(response.text)
                    if char_count > 500:
                        st.warning(f"⚠️ 注意：目前字元數為 {char_count}，超過 YouTube 500 字元上限，貼上時可能需要刪減尾部少許 Tag。")
                    else:
                        st.success(f"📊 完美！目前字元數為 {char_count}/500，可直接全選複製。")
                        
                    # 直接顯示純文字 Block，方便一鍵 Copy
                    st.code(response.text, language="text")
                    
                except Exception as e:
                    status.update(label="❌ 系統錯誤", state="error")
                    st.error(f"連線中斷或運算失敗：{e}")
        else:
            st.warning("⚠️ 系統提示：請確保視覺與語義模組均已輸入數據。")
