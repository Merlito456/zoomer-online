import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Don't raise error - just log warning and continue
if not url or not key:
    logging.warning("⚠️ SUPABASE_URL and SUPABASE_KEY not set. Using mock database.")
    supabase = None
else:
    try:
        supabase: Client = create_client(url, key)
        logging.info("✅ Supabase client initialized successfully")
    except Exception as e:
        logging.error(f"❌ Failed to initialize Supabase: {e}")
        supabase = None
