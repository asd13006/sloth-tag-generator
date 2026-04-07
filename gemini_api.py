"""
Gemini API 模組 — AI 生成 + Mock 資料 + 模型候選清單
"""

import json
import time

import streamlit as st
from google import genai
from google.genai import types

from history import build_dedup_prompt

# ─────────────────────────────────────────────────────────────────────────────
#  MODEL CANDIDATES — preference order
# ─────────────────────────────────────────────────────────────────────────────
MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
]

# ─────────────────────────────────────────────────────────────────────────────
#  MOCK DATA — realistic lofi-themed content for demo fallback
# ─────────────────────────────────────────────────────────────────────────────
_MOCK_TITLES_EN = [
    "Cozy Tea Moments… Chill Lofi for Relaxation, Study & Calm 🍵 🌙",
    "Find Your Calm… Soothing R&B for Work, Rest & Healing 🌸 ☕",
    "Slow Morning Chores… Chill R&B for Study, Work & Gentle Focus 🧰 🧰",
    "Peace in the Garden… Chill R&B for Study, Work & Soft Focus ⏳ 🫖",
    "Rest in the Morning Light… Chill R&B for Yoga & Peaceful Moments 🧘 🌞",
]
_MOCK_TITLES_ZH = [
    "溫馨茶時光… 放鬆、讀書＆平靜的 Chill Lofi 🍵 🌙",
    "找到你的安寧… 工作、休憩＆療癒的舒緩 R&B 🌸 ☕",
    "慢活早晨家務… 讀書、工作＆溫柔專注的 Chill R&B 🧰 🧰",
    "花園裡的寧靜… 讀書、工作＆柔和專注的 Chill R&B ⏳ 🫖",
    "晨光中的休憩… 瑜伽＆平靜時刻的 Chill R&B 🧘 🌞",
]
_MOCK_TAGS = (
    "lofi, lofi music, chill lofi, lofi hip hop, lofi beats, study music, "
    "relax music, chill music, cozy lofi, rainy day lofi, lofi cafe, "
    "late night lofi, lofi jazz, soothing music, ambient lofi, sleep lofi, "
    "focus music, lo-fi, chillhop, lofi radio, lofi mix, soft lofi, "
    "reading music, writing music, peaceful music, calm beats, "
    "midnight study lofi, rainy cafe ambience, warm lofi vibes, "
    "aesthetic lofi, lofi for work, deep focus lofi, cozy night lofi, "
    "gentle piano lofi, autumn lofi, winter lofi playlist, lofi 2024, "
    "morning coffee lofi, sunday lofi, healing lofi beats"
)
_MOCK_LONG_STORY_EN = (
    "You sit by the window, watching raindrops trace slow paths down the glass. "
    "The café is nearly empty — just you, a half-finished cup of tea, and the quiet hum of a lofi playlist "
    "drifting from somewhere behind the counter.\n\n"
    "Outside, the city feels far away. Streetlights blur into soft halos through the rain, "
    "and the occasional car passes like a whisper. You open your notebook, but there's no rush to write. "
    "Tonight, just being here is enough.\n\n"
    "The barista glances at the clock but never hurries. "
    "A stack of old paperbacks sits on the shelf by the door — they belong to no one and everyone.\n\n"
    "You pick up your pen. The first sentence comes slowly, then another, then a whole paragraph "
    "that feels like it was always waiting inside you. The rain keeps its gentle rhythm, "
    "and the lofi beats carry you forward, one soft note at a time.\n\n"
    "When you finally look up, the tea has gone cold and the rain has stopped. "
    "But the words on the page glow warm, and you smile — knowing that some of the best things "
    "are written in the quiet hours, when no one is watching."
)
_MOCK_LONG_STORY_ZH = (
    "你坐在窗邊，看著雨滴在玻璃上緩緩滑落。咖啡廳裡幾乎空無一人——"
    "只有你、一杯喝了一半的茶，和從吧台後方某處飄來的 lofi 音樂。\n\n"
    "窗外，城市彷彿很遙遠。街燈在雨中暈成柔和的光圈，"
    "偶爾有車經過，像一聲低語。你翻開筆記本，但不急著寫。"
    "今夜，就只是待在這裡，已經足夠。\n\n"
    "咖啡師熟練地擦拭義式咖啡機，看了一眼時鐘，卻從不趕時間。"
    "門邊的書架上放著一疊舊平裝書——幾個月前有人留下的，"
    "現在它們不屬於任何人，又屬於每個人。\n\n"
    "你拿起筆。第一句話來得很慢，然後又一句，接著是一整段——"
    "那些文字彷彿一直在你心裡等候。雨聲保持著溫柔的節奏，"
    "lofi 的音符帶著你前行，一個柔和的音符接著一個。\n\n"
    "當你終於抬起頭，茶已經涼了，雨也停了。"
    "但紙上的文字散發著溫暖的光，你微笑——因為最好的東西，"
    "往往是在安靜的時刻、無人注視時寫下的。"
)
_MOCK_SHORT_STORY_EN = (
    "Making Tea 🍵\n"
    "Evening settles outside the window 🌙. You fill the kettle and set it on the stove, "
    "then choose your favorite cup—the one with the crack in the glaze you never bothered to replace.\n\n"
    "The kettle hums low. When it whistles, you pour. Steam rises, fogging the window above the sink 💨. "
    "You watch the water darken, then wrap your hands around the warm cup, letting the heat seep through ☕.\n\n"
    "When you finally take a slow sip, you carry the cup to the living room and sink into the couch 🛋️. "
    "The last light has gone. Only the warmth in your hands and the slow, easy quiet of the evening 🌿."
)
_MOCK_SHORT_STORY_ZH = (
    "泡一杯茶 🍵\n"
    "夜色在窗外慢慢沉澱 🌙。你把水壺裝滿放上爐子，"
    "然後挑了你最愛的那只杯子——釉面上有道裂痕，你從沒想過要換掉它。\n\n"
    "水壺發出低沉的嗡鳴。壺嘴一響，你傾倒熱水。蒸氣升起，在水槽上方的窗玻璃上凝成一層薄霧 💨。"
    "你看著茶湯漸漸變深，然後雙手捧住溫熱的杯身，讓暖意慢慢滲透 ☕。\n\n"
    "當你終於小啜一口，便端著杯子走進客廳，陷入沙發裡 🛋️。"
    "最後的光已經散去。只剩手中的溫暖，和這個夜晚緩慢而安靜的呼吸 🌿。"
)
_MOCK_TRACKLIST = [
    {"id": 1, "en_title": "Midnight Pages", "zh_title": "午夜書頁",
     "en_theme": "Quiet pen scratches under a dim desk lamp", "zh_theme": "昏暗檯燈下筆尖沙沙的聲音"},
    {"id": 2, "en_title": "Rainy Café", "zh_title": "雨天咖啡館",
     "en_theme": "Raindrops on glass and the scent of fresh brew", "zh_theme": "玻璃上的雨滴和新煮咖啡的香氣"},
    {"id": 3, "en_title": "Paper & Ink", "zh_title": "紙與墨",
     "en_theme": "A worn journal filled with half-finished thoughts", "zh_theme": "一本寫滿未完思緒的舊日記"},
    {"id": 4, "en_title": "Warm Silence", "zh_title": "溫暖的沉默",
     "en_theme": "Two cups of tea, no words needed", "zh_theme": "兩杯茶，不需要言語"},
    {"id": 5, "en_title": "Golden Hour Drift", "zh_title": "金色時光漫遊",
     "en_theme": "Sunlight fading through linen curtains", "zh_theme": "陽光透過亞麻窗簾漸漸消逝"},
    {"id": 6, "en_title": "Autumn Letters", "zh_title": "秋日信箋",
     "en_theme": "A letter you meant to send but never did", "zh_theme": "一封你想寄出卻始終沒寄的信"},
    {"id": 7, "en_title": "Foggy Window Sill", "zh_title": "霧氣窗台",
     "en_theme": "Drawing shapes on a fogged-up window", "zh_theme": "在起霧的玻璃上隨手畫圖案"},
    {"id": 8, "en_title": "Bookshop Lullaby", "zh_title": "書店搖籃曲",
     "en_theme": "Old books and the creak of wooden floors", "zh_theme": "舊書和木地板的吱嘎聲"},
    {"id": 9, "en_title": "Slow Morning", "zh_title": "緩慢的早晨",
     "en_theme": "No alarm, just birdsong and soft light", "zh_theme": "沒有鬧鐘，只有鳥鳴和柔光"},
    {"id": 10, "en_title": "Last Train Home", "zh_title": "末班車回家",
     "en_theme": "City lights blurring past a tired smile", "zh_theme": "城市燈光在疲倦的微笑前模糊而過"},
]


# ─────────────────────────────────────────────────────────────────────────────
#  GEMINI API — real AI generation
# ─────────────────────────────────────────────────────────────────────────────
def _get_client() -> genai.Client | None:
    """Return a configured genai Client, or None if no key."""
    key = st.session_state.api_key
    if not key:
        return None
    return genai.Client(api_key=key)


def validate_api_key(key: str) -> tuple[bool, str]:
    """Validate API key and find best available model. Returns (ok, model_name)."""
    if not key:
        return False, ""
    try:
        client = genai.Client(api_key=key)
        available = set()
        for m in client.models.list():
            available.add(m.name.split("/")[-1] if "/" in m.name else m.name)
        for candidate in MODEL_CANDIDATES:
            if candidate in available:
                return True, candidate
        # If none of the candidates match, use the first available generative model
        for m_name in available:
            if "gemini" in m_name:
                return True, m_name
        return False, ""
    except Exception:
        return False, ""


def _call_json(prompt: str, image_parts: list | None = None) -> dict | list:
    """Call Gemini with JSON response mode. Returns parsed JSON."""
    client = _get_client()
    if not client:
        raise RuntimeError("API key 未設定")
    model = st.session_state.api_model
    contents = []
    if image_parts:
        for img_bytes, mime in image_parts:
            contents.append(types.Part.from_bytes(
                data=img_bytes, mime_type=mime))
    contents.append(prompt)
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.9,
        ),
    )
    return json.loads(response.text)


def _build_tone_style_block() -> str:
    """Build prompt fragment from tone/style/audience/extra settings."""
    parts = []
    tone_map = {0: "溫暖柔和", 25: "寧靜治癒", 50: "平衡自然", 75: "明亮活潑", 100: "活潑有力"}
    tone = tone_map.get(st.session_state.prompt_tone, "平衡自然")
    parts.append(f"語氣風格：{tone}")
    if st.session_state.prompt_styles:
        parts.append(f"創作風格：{', '.join(st.session_state.prompt_styles)}")
    if st.session_state.prompt_audience and st.session_state.prompt_audience != "不指定":
        parts.append(f"目標受眾：{st.session_state.prompt_audience}")
    if st.session_state.prompt_extra:
        parts.append(f"額外指示：{st.session_state.prompt_extra}")
    return "\n".join(parts)


def _prepare_images() -> list | None:
    """Prepare uploaded images as (bytes, mime_type) tuples for API."""
    imgs = st.session_state.get("uploaded_images", [])
    if not imgs:
        return None
    parts = []
    for f in imgs[:5]:  # 最多 5 張
        data = f.getvalue()
        mime = f.type or "image/jpeg"
        parts.append((data, mime))
    return parts


def ai_generate_tracklist(n: int, context: str, user_email: str | None = None) -> list:
    """Generate tracklist via Gemini."""
    style_block = _build_tone_style_block()
    dedup_block = build_dedup_prompt(user_email)
    prompt = f"""You are a lofi music curator creating a tracklist for a YouTube lofi playlist.

Generate {n} lofi track concepts. Style: cozy, introspective, lofi/chillhop, quiet everyday moments.

{f"User's creative context: {context}" if context else ""}
{style_block}
{dedup_block}

Return a JSON array of exactly {n} objects. Each object must have:
- "en_title": English title, 2-5 words, poetic
- "zh_title": Traditional Chinese title, 3-6 characters
- "en_theme": English theme sentence, ≤15 words
- "zh_theme": Traditional Chinese theme sentence

Return ONLY the JSON array, no wrapping object."""

    image_parts = _prepare_images()
    data = _call_json(prompt, image_parts)
    if isinstance(data, dict) and "tracklist" in data:
        data = data["tracklist"]
    for i, item in enumerate(data, 1):
        item["id"] = i
    return data[:n]


def ai_generate_assets(selected_outputs: list, context: str, tracklist: list | None, user_email: str | None = None) -> dict:
    """Generate titles, tags, stories via a single Gemini call."""
    style_block = _build_tone_style_block()
    dedup_block = build_dedup_prompt(user_email)

    tracklist_text = ""
    if tracklist:
        lines = []
        for s in tracklist:
            lines.append(
                f"  - 《{s.get('en_title', '')}》({s.get('zh_title', '')}): {s.get('en_theme', '')}")
        tracklist_text = "Tracklist for reference:\n" + "\n".join(lines)

    # 構建需要生成的項目描述
    output_specs = []
    if "titles" in selected_outputs:
        output_specs.append("""- "titles": array of 5 English YouTube titles, ranked by predicted CTR (high→low).
  Each title MUST follow this exact format: "{Catchy Name 2-5 words}… {Genre with Lofi/R&B/Jazz keyword} for {Use Case 2-3 words} {emoji} {emoji}"
  IMPORTANT: Vary the genre keyword across titles (mix Lofi, R&B, Jazz — don't repeat the same one).
  Vary the use cases (Study, Work, Relaxation, Yoga, Healing, Focus, etc.) and moods (Cozy, Peaceful, Slow, Warm, etc.).
  Use diverse, evocative emoji pairs — avoid repeating the same pair.
  Examples of good diversity:
  - "Cozy Tea Moments… Chill Lofi for Relaxation, Study & Calm 🍵 🌙"
  - "Find Peace in Small Tasks… Chill Lofi for Relaxation & Unwinding 🧼 🌿"
  - "Find Your Calm… Soothing R&B for Work, Rest & Healing 🌸 ☕"
  - "Slow Morning Chores… Chill R&B for Study, Work & Gentle Focus 🧰 🧰"
  - "Rest in the Morning Light… Chill R&B for Yoga & Peaceful Moments 🧘 🌞"
- "titles_zh": array of 5 Traditional Chinese titles, 1:1 corresponding to the English titles.""")
    if "tags" in selected_outputs:
        output_specs.append("""- "tags": a single comma-separated string of 35-45 YouTube SEO tags.
  Mix broad keywords (e.g. lofi, chill music) with niche keywords (e.g. cozy rainy night lofi).
  Total character count should be 450-500.""")
    if "long_story" in selected_outputs:
        output_specs.append("""- "long_story": English prose, 3-5 paragraphs. Second person "you". Immersive slice-of-life style.
  Total length MUST be around 1000 characters (not words). Paragraphs separated by \\n\\n.
- "long_story_zh": Traditional Chinese translation with equal poetic quality. Also ~1000 characters total.""")
    if "short_story" in selected_outputs:
        output_specs.append("""- "short_story": English short prose, 200-600 characters total. Format:
  Line 1: A short evocative title followed by one emoji (e.g. "Making Tea 🍵")
  Then 2-3 paragraphs in second person "you", present tense, with sensory details.
  Place emojis at the END of sentences (not inline). Paragraphs separated by \\n\\n.
  Example:
  "Making Tea 🍵\nEvening settles outside the window 🌙. You fill the kettle and set it on the stove...\n\nYou don't drink yet. You just stand there, holding it..."
- "short_story_zh": Traditional Chinese translation in the same format. Also 200-600 characters total.""")

    specs_text = "\n".join(output_specs)

    prompt = f"""You are a YouTube SEO copywriter specializing in lofi/chill music channels.

{f"User's creative context: {context}" if context else "No specific context provided — create a cozy lofi theme."}
{tracklist_text}
{style_block}
{dedup_block}

Generate the following as a single JSON object:
{specs_text}

Return ONLY the JSON object."""

    image_parts = _prepare_images()
    return _call_json(prompt, image_parts)


def ai_generate(selected_outputs: list, n_songs: int, context: str, user_email: str | None = None) -> dict:
    """Full AI generation pipeline."""
    result = {}

    # Step 1: 生成歌單（如果需要）
    if "tracklist" in selected_outputs:
        tracklist = ai_generate_tracklist(n_songs, context, user_email)
        result["tracklist"] = tracklist
    else:
        tracklist = None

    # Step 2: 生成其他素材（標題、標籤、故事）
    asset_outputs = [k for k in selected_outputs if k != "tracklist"]
    if asset_outputs:
        assets = ai_generate_assets(
            asset_outputs, context, tracklist or result.get("tracklist"), user_email)
        result.update(assets)

    return result


def mock_generate(selected_outputs: list, n_songs: int) -> dict:
    """Simulate AI generation with mock data. Returns only the requested keys."""
    time.sleep(1.5)  # 模擬 loading
    result = {}
    if "titles" in selected_outputs:
        result["titles"] = _MOCK_TITLES_EN
        result["titles_zh"] = _MOCK_TITLES_ZH
    if "tags" in selected_outputs:
        result["tags"] = _MOCK_TAGS
    if "long_story" in selected_outputs:
        result["long_story"] = _MOCK_LONG_STORY_EN
        result["long_story_zh"] = _MOCK_LONG_STORY_ZH
    if "short_story" in selected_outputs:
        result["short_story"] = _MOCK_SHORT_STORY_EN
        result["short_story_zh"] = _MOCK_SHORT_STORY_ZH
    if "tracklist" in selected_outputs:
        result["tracklist"] = _MOCK_TRACKLIST[:n_songs]
    return result
