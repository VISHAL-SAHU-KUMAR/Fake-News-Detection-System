import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load .env from the backend root folder (absolute path)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(_env_path, override=True)

class Database:
    client: Client = None

db_config = Database()

async def init_db():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")

    print(f"SUPABASE_URL: {url}")
    print(f"SUPABASE_KEY: {'SET' if key else 'MISSING'}")

    if url and key:
        try:
            db_config.client = create_client(url, key)
            print("Connected to Supabase ✓")
        except Exception as e:
            print(f"Failed to connect to Supabase: {e}")
    else:
        print("Supabase credentials not found. Running without DB.")

async def close_db():
    pass

def get_db() -> Client:
    return db_config.client
