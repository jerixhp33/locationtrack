from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

_url: str = os.getenv("SUPABASE_URL", "")
_key: str = os.getenv("SUPABASE_KEY", "")

supabase: Client = create_client(_url, _key)
