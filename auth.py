"""
Google OAuth 登入模組 — 手動 HTTP 實作
完全不依賴 google_auth_oauthlib，避免 PKCE 問題。
Query-params + server cache 持久化登入狀態，cookie 作為備援。
"""

import json
import hmac
import hashlib
import base64
import logging
import uuid
import urllib.parse

import requests as _requests
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
#  常數
# ─────────────────────────────────────────────────────────────────────────────
_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
_OAUTH_SCOPES = "openid email profile"

# ─────────────────────────────────────────────────────────────────────────────
#  模組狀態
# ─────────────────────────────────────────────────────────────────────────────
_auth_obj = None   # global ref for login button rendering
_auth_secret = None  # cookie 簽名用密鑰


@st.cache_resource
def _session_store():
    """Server-side session store — 跨 rerun 持久化（server 重啟後清空）。"""
    return {}


def _persist_session(user_info: dict) -> str:
    """將 user info 存入 server 端並回傳 session ID。"""
    sid = uuid.uuid4().hex
    _session_store()[sid] = user_info
    return sid


def _restore_from_query_params() -> bool:
    """從 URL query params 中的 sid 還原登入狀態。"""
    sid = st.query_params.get("sid")
    if not sid:
        return False
    data = _session_store().get(sid)
    if not data or "email" not in data:
        # stale / invalid session — 清除
        st.query_params.pop("sid", None)
        return False
    st.session_state["connected"] = True
    st.session_state["oauth_id"] = data.get("id", "")
    st.session_state["user_info"] = data
    return True


# ─────────────────────────────────────────────────────────────────────────────
#  Cookie 持久化
# ─────────────────────────────────────────────────────────────────────────────
def _sign_cookie(data: dict, secret: str) -> str:
    """建立簽名 cookie 值: base64(json).hmac_signature"""
    payload = base64.urlsafe_b64encode(json.dumps(data, ensure_ascii=False).encode()).decode()
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def _verify_cookie(cookie_val: str, secret: str):
    """驗證並解碼簽名 cookie，失敗回傳 None。"""
    try:
        payload, sig = cookie_val.rsplit(".", 1)
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        return json.loads(base64.urlsafe_b64decode(payload).decode())
    except Exception:
        return None


def _restore_from_cookie(secret: str) -> bool:
    """從 cookie 還原登入狀態，成功回傳 True。"""
    try:
        cookie_val = st.context.cookies.get("sloth_auth")
        if not cookie_val:
            return False
        data = _verify_cookie(cookie_val, secret)
        if not data or "email" not in data:
            return False
        st.session_state["connected"] = True
        st.session_state["oauth_id"] = data.get("id", "")
        st.session_state["user_info"] = data
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  SlothAuth 核心類別
# ─────────────────────────────────────────────────────────────────────────────
class SlothAuth:
    """手動 Google OAuth，用 requests 直接呼叫 Google 端點。"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        st.session_state.setdefault("connected", False)
        st.session_state.setdefault("user_info", {})

    def _build_auth_url(self) -> str:
        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "response_type": "code",
            "scope": _OAUTH_SCOPES,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{_GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"

    def check_authentification(self):
        if st.session_state["connected"]:
            return
        # 處理 Google 回傳的錯誤
        error = st.query_params.get("error")
        if error:
            logging.warning(f"Google OAuth 錯誤: {error}")
            st.query_params.clear()
            return
        # 處理 auth code → 交換 token → 取得 user info
        auth_code = st.query_params.get("code")
        if auth_code:
            st.query_params.clear()
            try:
                # 用 auth code 交換 access token
                token_resp = _requests.post(_GOOGLE_TOKEN_URL, data={
                    "code": auth_code,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "redirect_uri": self._redirect_uri,
                    "grant_type": "authorization_code",
                }, timeout=10)
                token_data = token_resp.json()
                if "access_token" not in token_data:
                    logging.warning(f"OAuth token 交換失敗: {token_data}")
                    return
                # 用 access token 取得用戶資訊
                user_resp = _requests.get(_GOOGLE_USERINFO_URL, headers={
                    "Authorization": f"Bearer {token_data['access_token']}",
                }, timeout=10)
                user_info = user_resp.json()
                st.session_state["connected"] = True
                st.session_state["oauth_id"] = user_info.get("id")
                st.session_state["user_info"] = user_info
                # 持久化：query params (主要) + cookie (備援)
                sid = _persist_session(user_info)
                st.query_params["sid"] = sid
                st.session_state["_set_auth_cookie"] = True
                st.rerun()
            except Exception as e:
                logging.warning(f"OAuth token 交換失敗（略過）: {e}")

    def login(self, color="blue", justify_content="center"):
        if st.session_state["connected"]:
            return
        auth_url = self._build_auth_url()
        st.link_button("🔐 Sign in with Google", auth_url, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
#  公開 API
# ─────────────────────────────────────────────────────────────────────────────
def init_auth():
    """初始化 Google OAuth。回傳 (logged_in, email, name, photo_url)。
    Secrets 缺失或 auth 失敗時自動降級為訪客模式。"""
    global _auth_obj, _auth_secret
    try:
        _client_id = st.secrets["google_oauth"]["client_id"]
        _client_secret = st.secrets["google_oauth"]["client_secret"]
        _redirect_uri = st.secrets["google_oauth"].get(
            "redirect_uri", "http://localhost:8501")
        _current_uri = _redirect_uri.strip().rstrip("/")
        _auth_secret = _client_secret

        # 優先從 query params 還原，cookie 作為備援
        if not st.session_state.get("connected"):
            if not _restore_from_query_params():
                _restore_from_cookie(_auth_secret)

        auth = SlothAuth(
            client_id=_client_id,
            client_secret=_client_secret,
            redirect_uri=_current_uri,
        )
        auth.check_authentification()
        _auth_obj = auth
        return (
            st.session_state.get("connected", False),
            st.session_state.get("user_info", {}).get("email"),
            st.session_state.get("user_info", {}).get("name"),
            st.session_state.get("user_info", {}).get("picture"),
        )
    except (KeyError, FileNotFoundError):
        return False, None, None, None
    except Exception as e:
        logging.warning(f"OAuth 初始化失敗: {e}")
        return False, None, None, None


def get_auth_object():
    """取得 SlothAuth 物件（用於渲染 login 按鈕），未初始化時回傳 None。"""
    return _auth_obj


def inject_auth_cookies():
    """處理登入/登出 cookie 注入（須在頁面渲染時呼叫）。"""
    if st.session_state.get("_set_auth_cookie") and _auth_secret:
        _cookie_data = st.session_state.get("user_info", {})
        if _cookie_data:
            _cookie_val = _sign_cookie(_cookie_data, _auth_secret)
            st.components.v1.html(
                f'<script>document.cookie="sloth_auth={_cookie_val}; path=/; max-age=2592000; SameSite=Lax; Secure";</script>',
                height=1, width=1,
            )
        st.session_state["_set_auth_cookie"] = False

    if st.session_state.get("_clear_auth_cookie"):
        st.components.v1.html(
            '<script>document.cookie="sloth_auth=; path=/; max-age=0; SameSite=Lax; Secure";</script>',
            height=1, width=1,
        )
        st.session_state["_clear_auth_cookie"] = False


def clear_session():
    """登出時清除 query params session + cookie。"""
    sid = st.query_params.get("sid")
    if sid:
        _session_store().pop(sid, None)
        st.query_params.pop("sid", None)
    st.session_state["connected"] = False
    st.session_state["user_info"] = {}
    st.session_state["_clear_auth_cookie"] = True
