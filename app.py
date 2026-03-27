import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 1. 頁面基礎設定與 Pro 級 UI/CSS (保持 dark apple 質感)
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
        st.caption("Ready to generate aesthetic magic.")
        if st.button("Disconnect", use_container_width=True):
            st.session_state.api_key = ""
            st.rerun()

# ==========================================
# 3. 主畫面
# ==========================================
st.markdown("<div class='ios-title'>sLoth Creator Pro</div>", unsafe_allow_html=True)
st.markdown("<div class='ios-subtitle'>Aesthetic bilingual titles & SEO tags, vibe-checked for sLoth rAdio.</div>", unsafe_allow_html=True)

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
    
    generate_btn = st.button("✨ Generate Integrated Magic", type="primary", use_container_width=True)

    if generate_btn:
        if uploaded_file and video_story:
            with st.status("Thinking like an artist...", expanded=True) as status:
                st.write("Feeling the visual aesthetic...")
                st.write("Crafting integrated bilingual titles with Emojis...")
                st.write("Optimizing SEO tags length (max 490 chars)...")
                
                try:
                    # 【核心核心終極升級：真正同義，加入 Emoji】
                    prompt = f"""
                    你而家係一位深受大學生同失眠人士喜愛嘅 Lofi 電台策劃師 (類似 Lofi Girl 或 Homework Radio)。你嘅專長係寫出中英文意思準確對照，富有強烈生活感、對話感，好似老朋友關懷一樣嘅爆款標題。
                    
                    請根據圖片視覺和以下氛圍描述，為頻道 sLoth rAdio 創作標題和標籤。
                    
                    氛圍與故事：{video_story}
                    
                    【輸出格式】：
                    
                    ===TITLES===
                    提供 5 個極具點擊率 (CTR) 嘅中英對照標題 (格式: 分數|||中文標題 (含Emoji)|||英文標題 (含Emoji))。
                    
                    【標題創作法则 - 絕對指令】：
                    1. 對話與生活感：中文標題必須像是在**對觀眾說話**，帶有強烈的生活氣息和關懷感（类似：辛苦喇 / 時間到喇...）。
                    2. **真正中英同義**：英文標題必須緊密匹對中文標題的意思，確保中義同英文義完全對照。同時英文部分要保持自然的 Lofi 氛圍語調，並可以適當無縫加入 1-2 個搜尋關鍵字詞尾（如 | lo fi study session）。
                    3. **情緒 Emoji**：在中英文標題中加入**適量和適合（例如：溫書加📚，雨天加☔, 睡覺加🌙）**的 Emoji，以增加點擊慾望。
                    4. 圍繞故事：必須深度結合用戶提供的【圖片】和【故事情境】。
                    5. 格式：每個標題給出一個評分 (0-100)，並使用 `|||` 分隔。不要加序號。
                    
                    例子：
                    98|||溫書累就休息一下先啦，我喺度 ☔|||Rest if you're tired from studying, I'm here | lo fi beats to relax/study to
                    96|||2:00 am: 一個人的房間，你也還沒睡嗎? 🌙|||2:00 am: Lonely in the room, are you still up too? | calm vibes for sleep
                    
                    ===TAGS===
                    直接輸出一連串由逗號和半形空格分隔的 Tags。
                    包含 lofi hip hop radio, beats to relax/study to 等大熱字眼。
                    【字數警告】：總字元長度必須嚴格控制在 450 到 490 之間！絕對不能超過 490 字元！不可分類。
                    """
                    
                    response = model.generate_content([prompt, image])
                    result_text = response.text
                    
                    parts = result_text.split("===TAGS===")
                    titles_part = parts[0].replace("===TITLES===", "").strip()
                    tags_part = parts[1].strip() if len(parts) > 1 else ""
                    
                    status.update(label="✅ Magic Ready", state="complete", expanded=False)
                    st.toast('✨Integrated Magic generated successfully!', icon='🎉')
                    
                    # ----------------------------------------
                    # UI 顯示
                    # ----------------------------------------
                    st.write("")
                    st.markdown("#### 💬 Choose your integrated & poetic Title")
                    
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
                            st.caption("⚠️ Tags slightly over safe limit (max 490). Trim before pasting.")
                        else:
                            st.caption("✅ Perfect length. Safe to copy.")
                    
                except Exception as e:
                    status.update(label="❌ Generation interrupted", state="error")
                    st.error(f"Error details: {e}")
        else:
            st.error("Please provide both an image and a vibe description.")
            
    st.write("")
    st.markdown("<div style='text-align: center; color: #8E8E93; font-size: 12px; margin-top: 20px;'>Powered by Gemini 2.5 Flash • Built for sLoth rAdio</div>", unsafe_allow_html=True)
