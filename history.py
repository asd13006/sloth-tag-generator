"""
User history persistence — JSON file storage per user.
Each user (identified by email) gets a dedicated JSON file under user_data/.
"""

import json
import os
import hashlib
from datetime import datetime

HISTORY_DIR = os.path.join(os.path.dirname(__file__), "user_data")
MAX_HISTORY = 50


def _safe_filename(email: str) -> str:
    """Convert email to a safe, deterministic filename."""
    return hashlib.sha256(email.encode()).hexdigest()[:16]


def _user_path(email: str) -> str:
    return os.path.join(HISTORY_DIR, f"{_safe_filename(email)}.json")


def load_history(email: str) -> list:
    """Load all history entries for a user (newest first)."""
    path = _user_path(email)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_history(email: str, history: list):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    path = _user_path(email)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def save_generation(email: str, results: dict, selected_outputs: list,
                    existing_materials: list, context: str, n_songs: int,
                    mode: str) -> dict:
    """Append a generation entry to user's history. Returns the entry."""
    history = load_history(email)
    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "selected_outputs": selected_outputs,
        "existing_materials": existing_materials,
        "user_context": context[:500],
        "n_songs": n_songs,
        "results": results,
        "mode": mode,
    }
    history.insert(0, entry)
    history = history[:MAX_HISTORY]
    _save_history(email, history)
    return entry


def delete_history_item(email: str, item_id: str):
    history = load_history(email)
    history = [h for h in history if h.get("id") != item_id]
    _save_history(email, history)


def get_past_titles(email: str) -> list[str]:
    """Collect all previously generated EN titles for dedup."""
    history = load_history(email)
    titles = []
    for entry in history:
        r = entry.get("results", {})
        titles.extend(r.get("titles", []))
    return titles


def get_past_tracklist_names(email: str) -> list[str]:
    """Collect all previously generated track names for dedup."""
    history = load_history(email)
    names = []
    for entry in history:
        r = entry.get("results", {})
        for track in r.get("tracklist", []):
            en = track.get("en_title", "")
            if en:
                names.append(en)
    return names


def build_dedup_prompt(email: str | None) -> str:
    """Build a prompt fragment listing past titles/tracks to avoid duplication."""
    if not email:
        return ""
    past_titles = get_past_titles(email)
    past_tracks = get_past_tracklist_names(email)
    parts = []
    if past_titles:
        recent = past_titles[:25]
        lines = "\n".join(f"  - {t}" for t in recent)
        parts.append(
            f"IMPORTANT — Do NOT reuse or closely resemble these previously generated titles:\n{lines}"
        )
    if past_tracks:
        recent = past_tracks[:30]
        lines = "\n".join(f"  - {t}" for t in recent)
        parts.append(
            f"IMPORTANT — Do NOT reuse or closely resemble these previously used track names:\n{lines}"
        )
    return "\n\n".join(parts)
