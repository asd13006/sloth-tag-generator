"""
Gemini API 模組 — AI 生成 + 模型候選清單
"""

import json

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
#  GEMINI API — AI generation
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
