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
    
    /* 標題卡片設計 */
    .title-card {
        background-color: rgba(44, 44, 46, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 15px;
        transition: all 0.2s ease-in-out;
    }
    .title-card:hover {
        background-color: rgba(44, 44, 46, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
    }
    .score-badge {
        display: inline-block;
        font-size: 12px;
        font-weight: 700;
        color: #00E676;
        background: rgba(0, 230, 118, 0.1);
        padding: 4px 10px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .zh-title {
        font-size: 18px;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 6px;
        line-height: 1.4;
    }
    .en-title {
        font-size: 14px;
        color: #8E8E93;
        line-height: 1.4;
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
# 2. 側邊欄設定
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
                        st.error("Invalid Key.")
    else:
        st.success("🟢 System Online")
        st.caption("Ready to generate conversational magic.")
        if st.button("Disconnect", use_container_width=True):
            st.session_state.api_key = ""
            st.rerun()

# ==========================================
# 3. 主畫面
# ==========================================
st.markdown("<div class='ios-title'>sLoth Creator</div>", unsafe_allow_html=True)
st.markdown("<div class='ios-subtitle'>Transform your vibe into relatable, high-converting titles & tags.</div>", unsafe_allow_html=True)

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
        video_story = st.text_area("Describe the Vibe, Story & Time", height=100, placeholder="例如：凌晨兩點，趕功課趕到好累，窗外雨越落越大，需要人鼓勵一下...")

    st.write("")
    
    generate_btn = st.button("✨ Generate Conversational Ideas", type="primary", use_container_width=True)

    if generate_btn:
        if uploaded_file and video_story:
            with st.status("Thinking like an old friend...", expanded=True) as status:
                st.write("Feeling the visual aesthetic...")
                st.write("Searching for empathetic phrases...")
                st.write("Securing maximum search volume...")
                
                try:
                    # 【核心核心終極升級：對話式、叫人休息、生活感】
                    prompt = f"""
                    你而家係一位深受大學生同失眠人士喜愛嘅 Lofi 電台策劃師 (類似 Lofi Girl 或 Homework Radio)。你嘅專長係寫出富有強烈生活感、共鳴感，好似老朋友對話一樣嘅爆款標題。
                    
                    請根據圖片視覺和以下氛圍描述，為頻道 sLoth rAdio 創作標題和標籤。
                    
                    氛圍與故事：{video_story}
                    
                    【輸出格式】：
                    
                    ===TITLES===
                    提供 5 個極具點擊率 (CTR) 嘅中英對照標題 (格式: 分數|||中文標題|||英文標題)。
                    
                    【標題創作法则 - 絕對指令】：
                    1. 對話與生活感：標題必須像是在**對觀眾說話**，帶有強烈的生活氣息和關懷感（類似：辛苦喇，休息一下先啦 / 2:00 am: a sign... / Rest gently...）。賣的是「陪伴」和「情緒價值」，而不僅僅是音樂。
                    2. 圍繞故事：必須深度結合用戶提供的【圖片】和【故事情境】（例如：如果故事提到「雨天溫書」，中文標題可以寫「雨落得咁大，溫書累就休息一下先啦 ☔」）。
                    3. 流量組合：英文標題必須同時包含大熱流量字眼 (例如: beats to relax/study to, lofi hip hop radio, deep focus, calm vibes)。
                    4. 格式：每個標題給出一個評分 (0-100)，並使用 `|||` 分隔。不要加序號。
                    
                    參考例子格式：
                    98|||溫書累就休息一下先啦，我喺度 ☔|||rainy night study session | lo fi beats to relax/study to
                    96|||2:00 am: 一個人的房間，你也還沒睡嗎? 🌙|||late night vibes for lonely souls | chill beats to sleep to
                    
                    ===TAGS===
                    直接輸出一連串由逗號和半形空格分隔的 Tags。
                    【字數警告】：總字元長度必須嚴格控制在 450 到 490 之間！絕對不能超過 490 字元！不可分類。
                    """
                    
                    response = model.generate_content([prompt, image])
                    result_text = response.text
                    
                    parts = result_text.split("===TAGS===")
                    titles_part = parts[0].replace("===TITLES===", "").strip()
                    tags_part = parts[1].strip() if len(parts) > 1 else ""
                    
                    status.update(label="✅ Conversations Ready", state="complete", expanded=False)
                    st.toast('✨ Vibe check passed!', icon='🎉')
                    
                    # ----------------------------------------
                    # UI 顯示
                    # ----------------------------------------
                    st.write("")
                    st.markdown("#### 💬 Choose your Conversational Title")
                    
                    for line in titles_part.split('\n'):
                        line = line.replace("*", "").strip()
                        if "|||" in line:
                            try:
                                score, zh_title, en_title = line.split("|||")
                                st.markdown(f"""
                                <div class='title-card'>
                                    <div class='score-badge'>🔥 CTR Score: {score.strip()}/100</div>
                                    <div class='zh-title'>{zh_title.strip()}</div>
                                    <div class='en-title'>{en_title.strip()}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            except:
                                pass
                    
                    st.write("")
                    st.markdown("#### 🏷️ Traffic-Optimized Tags (Safe Length)")
                    
                    char_count = len(tags_part)
                    col_tags, col_metric = st.columns([3, 1])
                    
                    with col_metric:
                        st.metric(label="Characters", value=f"{char_count}", delta=f"{490 - char_count} safe chars left", delta_color="normal")
                            
                    with col_tags:
                        st.code(tags_part, language="text")
                        if char_count > 490:
                            st.caption("⚠️ Slightly over safe limit. Trim before pasting.")
                        else:
                            st.caption("✅ Perfect length. Safe to copy.")
                    
                except Exception as e:
                    status.update(label="❌ Connection interrupted", state="error")
                    st.error(f"Error details: {e}")
        else:
            st.error("Please provide both an image and a vibe description.")
            
    st.write("")
    st.markdown("<div style='text-align: center; color: #8E8E93; font-size: 12px; margin-top: 20px;'>Powered by Gemini 2.5 Flash • Vibe checked for sLoth rAdio</div>", unsafe_allow_html=True)
