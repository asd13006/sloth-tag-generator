import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 1. 頁面基礎設定與全新 CSS 佈局
# ==========================================
st.set_page_config(page_title="sLoth rAdio | SEO Core", page_icon="📈", layout="wide")

st.markdown("""
<style>
    /* 專業控制台字體與發光效果 */
    .dashboard-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #00E676;
        font-weight: 800;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .dashboard-subtitle {
        color: #B0BEC5;
        font-size: 15px;
        margin-bottom: 30px;
        border-bottom: 1px solid #37474F;
        padding-bottom: 15px;
    }
    /* 隱藏預設的頂部空白 */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ==========================================
# 2. 側邊欄：API 安全閘門
# ==========================================
with st.sidebar:
    st.header("🔐 系統認證")
    if not st.session_state.api_key:
        api_input = st.text_input("輸入 Gemini API 金鑰", type="password", help="連接至 Google 演算法核心")
        if st.button("連線至伺服器", type="primary", use_container_width=True):
            if api_input:
                with st.spinner("驗證中..."):
                    try:
                        genai.configure(api_key=api_input)
                        genai.get_model('models/gemini-2.5-flash')
                        st.session_state.api_key = api_input
                        st.rerun()
                    except Exception as e:
                        st.error("連線失敗，請檢查金鑰。")
    else:
        st.success("🟢 演算法核心已連線")
        st.caption("狀態：準備生成最佳化流量標籤")
        st.divider()
        if st.button("斷開連線 / 登出", use_container_width=True):
            st.session_state.api_key = ""
            st.rerun()

# ==========================================
# 3. 主控制台佈局 (Pro Dashboard)
# ==========================================
st.markdown("<h1 class='dashboard-title'>sLoth.AI // 流量引擎控制台</h1>", unsafe_allow_html=True)
st.markdown("<div class='dashboard-subtitle'>針對 YouTube 演算法深度優化，自動提取最高曝光率之 500 字元 Tags。</div>", unsafe_allow_html=True)

if not st.session_state.api_key:
    st.warning("⚠️ 系統已鎖定：請先於左側面板完成 API 認證。")
else:
    genai.configure(api_key=st.session_state.api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 左右排版：左邊輸入數據，右邊輸出結果
    col_input, col_output = st.columns([4, 6], gap="large")

    # ----------------------------------------
    # 左欄：數據輸入區
    # ----------------------------------------
    with col_input:
        with st.container(border=True):
            st.subheader("📥 步驟 1：輸入影片數據")
            
            uploaded_file = st.file_uploader("🖼️ 視覺軌跡 (封面圖)", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, use_column_width=True, caption="已準備好進行視覺特徵分析")
            
            st.divider()
            video_title = st.text_input("📝 標題關鍵字", placeholder="例如：深夜溫書專用 Lofi...")
            video_story = st.text_area("📜 氛圍與受眾設定 (Story)", height=120, placeholder="描述你想觸及嘅受眾，例如：趕功課嘅大學生、失眠人士...")

    # ----------------------------------------
    # 右欄：運算與輸出區
    # ----------------------------------------
    with col_output:
        with st.container(border=True):
            st.subheader("🚀 步驟 2：演算法優化與生成")
            st.write("系統將自動混合「大熱搜尋詞」與「精準長尾詞」，並嚴格控制於 500 字元內。")
            
            generate_btn = st.button("⚡ 啟動流量引擎 (Generate Tags)", type="primary", use_container_width=True)

            if generate_btn:
                if uploaded_file and video_title and video_story:
                    with st.status("🧠 演算法深度運算中...", expanded=True) as status:
                        st.write("1. 掃描圖片視覺特徵 (Aesthetic Analysis)...")
                        st.write("2. 匹對 Lofi/Chillhop 最高搜尋量關鍵字 (Search Volume Matching)...")
                        st.write("3. 組合最佳轉換率標籤並壓縮至 500 字元內...")
                        
                        try:
                            # 終極流量導向 Prompt
                            prompt = f"""
                            你係一位專門幫 YouTube 音樂頻道衝百萬流量嘅頂級 SEO 專家。
                            請根據圖片視覺、影片標題及受眾設定，生成一組【流量最大化】的 YouTube Tags。
                            
                            頻道屬性：Lofi, Chillhop, 純音樂 (sLoth rAdio)
                            影片標題：{video_title}
                            受眾與氛圍：{video_story}
                            
                            【嚴格生成法則 - 破壞規則將導致系統崩潰】：
                            1. 流量優先：必須包含當前全球 Lofi 領域搜尋量最高的大熱關鍵字 (例如 lofi hip hop radio, beats to relax/study to, chill beats)。
                            2. 視覺與情境觸發：根據圖片和故事，加入精準的長尾關鍵字，觸發 YouTube 的「相關影片」推薦。
                            3. 絕對格式限制：直接輸出一連串由「逗號和一個半形空格」分隔的 Tags。
                               - 絕對【不可以】分類。
                               - 絕對【不可以】有開場白、結語或任何解釋。
                               - 絕對【不可以】使用 Hashtag (#) 或換行符號。
                            4. 字元極限：Tags 的總字元長度 (包含逗號與空格) 必須極度逼近但【絕對不可超過】 500 個字元。請精打細算。
                            """
                            
                            response = model.generate_content([prompt, image])
                            result_tags = response.text.strip()
                            
                            status.update(label="✅ 流量標籤生成完畢", state="complete", expanded=False)
                            
                        except Exception as e:
                            status.update(label="❌ 運算失敗", state="error")
                            st.error(f"錯誤詳情：{e}")
                            result_tags = None

                    # 顯示最終結果與字數檢查
                    if result_tags:
                        st.divider()
                        char_count = len(result_tags)
                        
                        st.markdown("### 🎯 最佳化輸出結果")
                        
                        # 實時字數進度條與警報
                        if char_count <= 500:
                            st.success(f"📊 完美符合演算法標準！目前字元數：**{char_count}/500**")
                            st.progress(char_count / 500)
                        else:
                            st.warning(f"⚠️ 注意：字元數超標 (**{char_count}/500**)。請於貼上 YouTube 時自行刪除最後一兩個標籤。")
                            st.progress(1.0)
                        
                        # 提供純文字 Block 方便一鍵複製
                        st.code(result_tags, language="text")
                        
                else:
                    st.error("⚠️ 啟動失敗：請於左側輸入完整的視覺軌跡 (圖片)、標題及氛圍設定。")
        
        # 介面底部留白優化
        st.write("")
        st.caption("© 2026 sLoth rAdio | Powered by Gemini Multimodal AI")
