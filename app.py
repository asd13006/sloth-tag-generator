import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 1. 頁面基礎設定與 Pro 級 UI/CSS
# ==========================================
st.set_page_config(page_title="sLoth Creator Pro", page_icon="🍏", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    .ios-title {
        font-weight: 700;
        font-size: 38px;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #4A90E2, #50E3C2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .ios-subtitle {
        color: #8E8E93;
        font-size: 16px;
        text-align: center;
        margin-bottom: 35px;
        font-weight: 500;
    }
    
    .title-card {
        background-color: rgba(44, 44, 46, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        font-size: 16px;
        color: #E5E5EA;
        line-height: 1.5;
        transition: all 0.2s ease-in-out;
    }
    .title-card:hover {
        background-color: rgba(44, 44, 46, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
    }
    
    .block-container {
        padding-top: 2.5rem;
        max-width: 760px;
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
        api_input = st.text_input("Gemini API Key", type="password", placeholder="Enter your key...")
        if st.button("Connect via API", type="primary", use_container_width=True):
            if api_input:
                with st.spinner("Authenticating..."):
                    try:
                        genai.configure(api_key=api_input)
                        genai.get_model('models/gemini-2.5-flash')
                        st.session_state.api_key = api_input
                        st.rerun()
                    except Exception as e:
                        st.error("Invalid Key. Please try again.")
    else:
        st.success("🟢 System Online")
        st.caption("Ready to generate magic.")
        if st.button("Disconnect", use_container_width=True):
            st.session_state.api_key = ""
            st.rerun()

# ==========================================
# 3. 主畫面：Creator Dashboard
# ==========================================
st.markdown("<div class='ios-title'>sLoth Creator</div>", unsafe_allow_html=True)
st.markdown("<div class='ios-subtitle'>Transform your vibe into high-converting titles & tags.</div>", unsafe_allow_html=True)

if not st.session_state.api_key:
    st.info("👋 Welcome! Please enter your API Key in the sidebar to start.")
else:
    genai.configure(api_key=st.session_state.api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    with st.container(border=True):
        st.markdown("#### 1. Visuals & Context")
        uploaded_file = st.file_uploader("Upload Thumbnail (JPG/PNG)", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
            
        st.write("")
        video_story = st.text_area("Describe the Vibe & Audience", height=90, placeholder="E.g., 深夜溫書，窗外落緊雨，畀大學生專注用嘅陪伴感...")

    st.write("")
    
    generate_btn = st.button("✨ Generate Ideas", type="primary", use_container_width=True)

    if generate_btn:
        if uploaded_file and video_story:
            with st.status("🧠 Analyzing multimodal context...", expanded=True) as status:
                st.write("Extracting visual aesthetics...")
                st.write("Engineering psychological triggers for titles...")
                st.write("Calculating optimal SEO tags...")
                
                try:
                    # 【核心進化：植入百萬流量密碼】
                    prompt = f"""
                    你係一位 YouTube 頂級內容策劃師與 SEO 專家，專門負責為頻道打造百萬點擊的爆款影片。
                    請根據圖片視覺和以下氛圍描述，為 Lofi/純音樂頻道 (sLoth rAdio) 創作標題和標籤。
                    
                    氛圍與受眾：{video_story}
                    
                    【嚴格輸出格式】：
                    
                    ===TITLES===
                    提供 5 個【極致點擊率 (Max CTR) 與最高搜尋流量】的中英對照標題 (格式: 中文 | English)。
                    必須運用 YouTube 演算法的流量密碼，包含以下 3 大元素：
                    1. 情緒與痛點解決：賣「陪伴感」、解決「失眠/焦慮/溫書壓力/深夜emo」。
                    2. 頂流關鍵字：英文部分必須無縫融入全球最高搜尋量的 Lofi 字眼 (例如: lofi hip hop, beats to relax/study to, deep focus, chill vibes, aesthetic)。
                    3. 吸睛排版：適當使用括號 (如 【 】 或 [ ]) 標示重點，例如 【深夜陪伴】或 [Study Lofi]，並加上 1-2 個符合氛圍的 Emoji。
                    請每行輸出一個標題，不要加 1. 2. 3. 等數字序號，直接輸出。
                    
                    ===TAGS===
                    直接輸出一連串由逗號和半形空格分隔的 Tags。
                    包含 lofi hip hop radio, beats to relax/study to 等大熱字眼。
                    總長度極度逼近但不可超過 500 個字元。不可分類，不可有 hashtags。
                    """
                    
                    response = model.generate_content([prompt, image])
                    result_text = response.text
                    
                    parts = result_text.split("===TAGS===")
                    titles_part = parts[0].replace("===TITLES===", "").strip()
                    tags_part = parts[1].strip() if len(parts) > 1 else ""
                    
                    status.update(label="✅ Analysis Complete", state="complete", expanded=False)
                    st.toast('✨ Magic generated successfully!', icon='🎉')
                    
                    st.write("")
                    st.markdown("#### 📝 Select Your Favorite Title")
                    
                    for line in titles_part.split('\n'):
                        clean_title = line.replace("*", "").strip()
                        if clean_title:
                            st.markdown(f"<div class='title-card'>{clean_title}</div>", unsafe_allow_html=True)
                    
                    st.write("")
                    st.markdown("#### 🏷️ Traffic-Optimized Tags")
                    
                    char_count = len(tags_part)
                    col_tags, col_metric = st.columns([3, 1])
                    
                    with col_metric:
                        if char_count <= 500:
                            st.metric(label="Characters", value=f"{char_count}", delta=f"{500 - char_count} remaining", delta_color="normal")
                        else:
                            st.metric(label="Characters", value=f"{char_count}", delta=f"{char_count - 500} over limit", delta_color="inverse")
                            
                    with col_tags:
                        st.code(tags_part, language="text")
                        if char_count > 500:
                            st.caption("⚠️ Please trim a few tags before pasting to YouTube.")
                    
                except Exception as e:
                    status.update(label="❌ Generation Failed", state="error")
                    st.error(f"Error details: {e}")
        else:
            st.error("Please provide both an image and a vibe description.")
            
    st.write("")
    st.markdown("<div style='text-align: center; color: #8E8E93; font-size: 12px; margin-top: 20px;'>Powered by Gemini 2.5 Flash • Built for sLoth rAdio</div>", unsafe_allow_html=True)
