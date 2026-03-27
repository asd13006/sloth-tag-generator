import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="sLoth rAdio Tag Gen", page_icon="🎧", layout="wide")

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ==========================================
# 側邊欄：極速認證系統
# ==========================================
with st.sidebar:
    st.header("⚙️ 系統設定")
    
    if not st.session_state.api_key:
        st.warning("請先完成認證以解鎖功能 🔒")
        api_input = st.text_input("輸入 Gemini API Key", type="password", placeholder="AIzaSy...")
        
        if st.button("連線至 AI 大腦 🚀", type="primary", use_container_width=True):
            if api_input:
                with st.spinner("極速驗證金鑰中..."):
                    try:
                        # 【優化：秒速認證】只係讀取模型資料，唔做文字生成，速度提升 10 倍！
                        genai.configure(api_key=api_input)
                        genai.get_model('models/gemini-2.5-flash')
                        
                        st.session_state.api_key = api_input
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 金鑰無效或網絡問題！\n{e}")
            else:
                st.error("請輸入金鑰！")
    else:
        st.success("✅ AI 已極速連線！")
        st.caption("你而家可以無限次生成專屬 Tags。")
        st.divider()
        if st.button("登出 / 更換 API Key", use_container_width=True):
            st.session_state.api_key = ""
            st.rerun()

# ==========================================
# 主畫面：最新 2.5-flash 引擎
# ==========================================
st.title("🎧 sLoth rAdio 專屬 Tag 生成器")
st.markdown("營造最佳 **Lofi & Chillhop** 氛圍，結合視覺與故事，一鍵生成高轉換率嘅 YouTube 標籤！")
st.divider()

if not st.session_state.api_key:
    st.info("👈 請先喺左邊【側邊欄】輸入 API Key 嚟解鎖魔法！")
else:
    genai.configure(api_key=st.session_state.api_key)
    # 【升級】使用最新一代 Flash 模型，更快更聰明
    model = genai.GenerativeModel('gemini-2.5-flash')

    col_img, col_text = st.columns([4, 6], gap="large")

    with col_img:
        st.subheader("1. 視覺氛圍")
        uploaded_file = st.file_uploader("上傳封面圖 (JPG/PNG)", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="封面預覽", use_column_width=True)
        else:
            st.info("🖼️ 尚未上傳圖片")

    with col_text:
        st.subheader("2. 內容情境")
        video_title = st.text_input("影片標題 (Title)", placeholder="例如：深夜溫書專用 Lofi...")
        video_story = st.text_area("小故事 / 氛圍描述 (Story & Vibe)", height=200, placeholder="描述一下呢條片想帶畀聽眾咩感覺...")

    st.write("")
    st.write("")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        generate_btn = st.button("✨ 立即分析圖文，一鍵生成 Tags ✨", type="primary", use_container_width=True)

    if generate_btn:
        if uploaded_file and video_title and video_story:
            with st.spinner('AI 正在感受你嘅圖片 Vibe，極速度緊精準 Tag...'):
                try:
                    prompt = f"""
                    你係一個專業嘅 YouTube SEO 專家，專門負責 Lofi、Chillhop 同純音樂頻道嘅推廣。
                    請分析以下嘅圖片氛圍，結合標題同故事情境，生成一組高轉換率嘅 YouTube Tags。
                    
                    頻道風格：放鬆、治癒、深夜陪伴 (類似 sLoth rAdio)
                    影片標題：{video_title}
                    背景故事：{video_story}
                    
                    請嚴格按照以下四個分類輸出 Tags (以逗號分隔，唔需要加 # 號，總數大約 15-20 個)：
                    1. 核心標籤 (Core Tags)
                    2. 氛圍與視覺標籤 (Vibe & Aesthetic Tags)
                    3. 情境與功能標籤 (Scenario Tags)
                    4. 長尾關鍵字 (Long-tail Keywords)
                    """
                    response = model.generate_content([prompt, image])
                    
                    st.divider()
                    st.subheader("🎉 生成結果")
                    st.success("請直接複製下方嘅 Tags 並貼上到 YouTube Studio：")
                    st.code(response.text, language="text")
                    
                except Exception as e:
                    st.error(f"哎呀，生成時出錯啦！\n錯誤詳情：{e}")
        else:
            st.warning("⚠️ 喂喂，圖片、標題、故事缺一不可，填齊先可以施展魔法㗎！")