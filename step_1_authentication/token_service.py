import os, json, time, pathlib, requests, config as config
from typing import Optional

TOKEN_URL = os.getenv("TOKEN_URL", config.API_URL)
CACHE_PATH = pathlib.Path(os.getenv("TOKEN_CACHE_FILE", "~/.cache/myapp/token.json")).expanduser()
CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

def _read_cache() -> Optional[dict]:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except Exception:
            return None
    return None

def _write_cache(token: str, expires_in: int):
    payload = {
        "accessToken": token,
        # store a few seconds early to avoid clock skew
        "expires_at": int(time.time()) + max(0, int(expires_in) - 15)
    }
    CACHE_PATH.write_text(json.dumps(payload))

def _fetch_new_token() -> str:
    payload = {
    #     "grantType": "client_credentials",
    #     "clientId": os.getenv("API_KEY"),
    #     "clientSecret": os.getenv("API_SECRET"),
    # }
    "grantType": "client_credentials",
    "clientId": "175482686405285",
    "clientSecret": "dc190e6d0e4f4fc79e4021e4b981e596"
    }
    headers = {"Content-Type": "application/json"}
    r = requests.post(TOKEN_URL, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    token = data.get("accessToken")
    config.Access_Token.append(token)
    if not token:
        raise RuntimeError(f"Token missing in response: {data}")
    _write_cache(token, data.get("expires_in", 3600))
    return token

def get_bearer_token(force_refresh: bool = False) -> str:
    """
    Returns a valid bearer token. Uses on-disk cache and refreshes if missing/expired.
    """
    if not force_refresh:
        cached = _read_cache()
        if cached and cached.get("expires_at", 0) > time.time():
            return cached["accessToken"]
    return _fetch_new_token()

#For testing purposes 
if __name__ == "__main__":
    try:
        token = get_bearer_token()
        print("✅ Successfully got token:", token[:10] + "...")  # only show part of it
    except Exception as e:
        print("❌ Failed:", e)