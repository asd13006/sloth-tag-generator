import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 1. 頁面基礎設定與 iOS 美學 CSS
# ==========================================
st.set_page_config(page_title="sLoth Creator", page_icon="🍏", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    .ios-title {
        font-weight: 700;
        font-size: 34px;
        letter-spacing: -0.5px;
        margin-bottom: 5px;
        text-align: center;
    }
    .ios-subtitle {
        color: #8E8E93;
        font-size: 17px;
        text-align: center;
        margin-bottom: 40px;
    }
    
    .block-container {
        padding-top: 2rem;
        max-width: 800px;
    }
</style>
""", unsafe_allow_html=True)

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ==========================================
# 2. 側邊欄：極簡設定
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    if not st.session_state.api_key:
        st.caption("Enter API Key to unlock features.")
        api_input = st.text_input("Gemini API Key", type="password", label_visibility="collapsed")
        if st.button("Connect", type="primary", use_container_width=True):
            if api_input:
                with st.spinner("Connecting..."):
                    try:
                        genai.configure(api_key=api_input)
                        genai.get_model('models/gemini-2.5-flash')
                        st.session_state.api_key = api_input
                        st.rerun()
                    except Exception as e:
                        st.error("Invalid Key.")
    else:
        st.success("Connected")
        if st.button("Disconnect", use_container_width=True):
            st.session_state.api_key = ""
            st.rerun()

# ==========================================
# 3. 主畫面：iOS 風格 Creator Dashboard
# ==========================================
st.markdown("<div class='ios-title'>sLoth Creator</div>", unsafe_allow_html=True)
st.markdown("<div class='ios-subtitle'>Auto-generate aesthetic titles and traffic-optimized tags.</div>", unsafe_allow_html=True)

if not st.session_state.api_key:
    st.info("👈 請先於左側 Settings 輸入 API Key。")
else:
    genai.configure(api_key=st.session_state.api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    with st.container(border=True):
        st.markdown("#### 1. Visuals & Vibe")
        uploaded_file = st.file_uploader("上傳封面圖 (Thumbnail)", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            # 已經修復咗之前嘅 Error，使用最新標準寫法
            st.image(image, use_container_width=True)
            
        st.write("")
        video_story = st.text_area("描述氛圍與受眾 (Vibe & Story)", height=100, placeholder="例如：落緊雨嘅夜晚，啱晒溫書或者放空聽...")

    st.write("")
    
    generate_btn = st.button("✨ Generate Magic", type="primary", use_container_width=True)

    if generate_btn:
        if uploaded_file and video_story:
            with st.status("Thinking like an artist...", expanded=True) as status:
                st.write("Analyzing visual aesthetics...")
                st.write("Crafting situational titles...")
                st.write("Optimizing SEO tags...")
                
                try:
                    # 【核心升級】：將你嘅情境感與功能性心法完全注入！
                    prompt = f"""
                    你係一位 YouTube 頂級內容策劃師與 SEO 專家。
                    請根據提供的圖片視覺和以下氛圍描述，為 Lofi/純音樂頻道 (sLoth rAdio) 創作標題和標籤。
                    
                    氛圍與受眾：{video_story}
                    
                    【輸出格式必須嚴格如下】：
                    
                    ===TITLES===
                    請提供 5 個極具點擊率嘅 YouTube 標題。標題必須具備強烈嘅「情境感」同「功能性」。
                    千萬不要只寫普通的「Relaxing Music」，必須將標題場景化！
                    參考例子：「深夜趕Deadline專用嘅高專注頻率」、「凌晨三點，一個人在房間的沉浸式歌單」。
                    核心理念：賣嘅唔單止係音樂，而係為聽眾提供一個「解決方案」同「陪伴感」。
                    可以中英混合，適當加上 emoji。要精準擊中目標受眾嘅痛點或需求，觸動人心。
                    
                    ===TAGS===
                    直接輸出一連串由逗號和半形空格分隔的 Tags。
                    必須包含 Lofi 領域最高搜尋量關鍵字 (如 lofi hip hop radio, beats to relax/study to)。
                    總長度必須極度逼近但不可超過 500 個字元。不可分類，不可有 hashtags。
                    """
                    
                    response = model.generate_content([prompt, image])
                    result_text = response.text
                    
                    parts = result_text.split("===TAGS===")
                    titles_part = parts[0].replace("===TITLES===", "").strip()
                    tags_part = parts[1].strip() if len(parts) > 1 else ""
                    
                    status.update(label="✅ Generation Complete", state="complete", expanded=False)
                    
                    st.write("")
                    st.markdown("#### 📝 Generated Titles (情境與功能性)")
                    st.info(titles_part)
                    
                    st.write("")
                    st.markdown("#### 🏷️ Optimized Tags")
                    
                    char_count = len(tags_part)
                    if char_count <= 500:
                        st.success(f"Perfect length ({char_count}/500 chars). Ready to copy.")
                    else:
                        st.warning(f"Slightly over limit ({char_count}/500 chars). Trim the last tag when pasting.")
                        
                    st.code(tags_part, language="text")
                    
                except Exception as e:
                    status.update(label="❌ Error occurred", state="error")
                    st.error(f"Something went wrong: {e}")
        else:
            st.error("Please provide both an image and a vibe description.")
            
    st.write("")
    st.caption("Designed for sLoth rAdio. Powered by Gemini Multimodal AI.")
