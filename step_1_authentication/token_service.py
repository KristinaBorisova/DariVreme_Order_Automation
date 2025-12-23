import os, json, time, pathlib, requests
from . import config
from typing import Optional

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
    # Use environment variables if available, fallback to hardcoded values
    api_key = config.API_KEY
    api_secret = config.API_SECRET

    payload = {
        "grantType": "client_credentials",
        "clientId": api_key,
        "clientSecret": api_secret
    }
    headers = {"Content-Type": "application/json"}

    print(f"🔑 Fetching token from: {config.API_URL}")
    print(f"🔑 Using API Key: {api_key[:8]}...")

    r = requests.post(config.API_URL, json=payload, headers=headers, timeout=30)

    if r.status_code != 200:
        print(f"❌ Token request failed: {r.status_code}")
        print(f"❌ Response: {r.text}")

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
        config.Access_Token = token;
        print("Access Token in config:", config.Access_Token[:10] + "...");
    except Exception as e:
        print("❌ Failed:", e)