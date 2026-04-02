from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_URL=os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_KEY=os.getenv("SUPABASE_KEY")

supabase: Client=create_client(PROJECT_URL,SUPABASE_KEY)

try:
    test=supabase.table('notes').select('id'    ).execute()
    print(test)
except Exception as e:
    print(e)