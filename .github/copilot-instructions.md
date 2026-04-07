# Project Guidelines

## Overview

YouTube Title Studio (`sloth_tags`) — a Streamlit app that uses Google Gemini AI to generate optimized YouTube titles, tags, and SEO assets through a multi-step pipeline.

## Tech Stack

- **Runtime**: Python 3
- **UI Framework**: Streamlit
- **AI**: Google Generative AI (Gemini) via `google-generativeai`
- **Image Processing**: Pillow

## Architecture

Single-file Streamlit app (`app.py`) with a 4-stage pipeline managed via `st.session_state`:

1. **Music Ideation** — card-based song selection with custom CSS hierarchy
2. **Visual Concept** — AI-driven story direction generation
3. **Assets & SEO Prep** — title/tag generation
4. **Final Dashboard** — results display

State flows forward through `st.session_state.step`; each stage can navigate back.

## Code Style

- UI text and code comments in **Traditional Chinese (繁體中文)**; respond in the same language when modifying UI strings
- Custom CSS is embedded inline via `st.markdown(unsafe_allow_html=True)` — keep dark-theme aesthetic consistent (accent: `#00ffcc`, bg: `rgba(30, 30, 35, 0.7)`)
- Section separators use `# ===` comment blocks

## Build and Test

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

No test suite exists yet. Theme config lives in `.streamlit/config.toml`.

## Conventions

- Pipeline state keys: `step`, `song_data`, `selected_song_ids`, `concept_options`, `selected_concept`, `final_results`
- Helper functions (`next_step`, `go_to`, `reset_pipeline`) live at module level before the UI code
- Each pipeline stage is a top-level `if/elif` block keyed on `st.session_state.step`
- Keep the Google Generative AI API key in Streamlit secrets (`st.secrets`), never hardcode
- AI calls use `_call_json(prompt)` which returns parsed JSON via Gemini's `response_mime_type="application/json"`
- HTML escaping helpers: `_ae()` (attribute), `_he()` (content) — used in the Stage 4 iframe dashboard

## Gotchas

- **Streamlit DOM fragility**: Custom CSS targets internal selectors like `[data-testid="baseButton-primary"]` — these may break on Streamlit upgrades
- **Model candidates**: `_MODEL_CANDIDATES` is a hardcoded preference list; update it when Google adds/deprecates models
- **`requirements.txt`** does not list `streamlit` (assumed pre-installed); add it if deploying to a fresh environment
- **`check_models.py`** is a local dev utility — never commit real API keys in it

## UI/UX Work — MANDATORY Skill Usage

**BEFORE performing any UI-related task** (review, design, implement, fix, improve styling), you MUST first run the `ui-ux-pro-max` skill to obtain data-driven recommendations:

```bash
# Step 1: Always start with design system generation
python3 .github/prompts/ui-ux-pro-max/scripts/search.py "lofi music youtube seo dark dashboard" --design-system -p "sLoth Title Studio"

# Step 2: Supplement with domain-specific queries as needed
python3 .github/prompts/ui-ux-pro-max/scripts/search.py "<keywords>" --domain <ux|style|typography|color|landing>
```

This is a **blocking requirement** — do not make UI judgements from intuition alone. Use the skill output as the authoritative source for:
- Color contrast ratios (WCAG compliance)
- Typography scale and font pairing
- Animation and motion guidelines (`prefers-reduced-motion`)
- UX anti-patterns to avoid
- Accessibility checklists (focus states, keyboard nav, ARIA)

**Established design system for this project** (from skill output):
- Style: OLED Dark + Neon Teal — `#0A0A14` bg, `#00ffcc` accent, `#b026ff` secondary
- Fonts: `Righteous` (display) + `Poppins` (body) — confirmed match ✅
- Contrast minimum: 4.5:1 for body text, 3:1 for large text / UI components
- Motion: all animations must respect `@media (prefers-reduced-motion: reduce)`
- Font loading: always use `font-display=swap` on Google Fonts imports
