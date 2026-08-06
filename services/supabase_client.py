from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

_url: str = os.getenv("SUPABASE_URL", "")
_key: str = os.getenv("SUPABASE_KEY", "")

# Fallback to empty string placeholder if missing to avoid crash on import during build
if not _url or not _key:
    # Use dummy values so FastAPI boots and can show clear configuration message
    _url = _url or "https://placeholder.supabase.co"
    _key = _key or "placeholder-key"

supabase: Client = create_client(_url, _key)
