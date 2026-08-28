import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("https://jgklqdsdsblahsfshdop.supabase.co")
key = os.getenv("sb_publishable_bxJO2IRUkHiJWj5XZYl2Yw_V-TzJ3aJ")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

supabase: Client = create_client(url, key)
