# test_supabase.py — run once to verify, then delete
import os
from dotenv import load_dotenv
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL loaded: {'✅' if url else '❌ MISSING'}")
print(f"KEY loaded: {'✅' if key else '❌ MISSING'}")

if not url or not key:
    print("\n⛔ Check your .env file — values are missing")
    exit()

try:
    from supabase import create_client
    client = create_client(url, key)

    # Test 1 — Insert a test row
    res = client.table("chat_history").insert({
        "session_id" : "test-session-001",
        "role"       : "user",
        "content"    : "Supabase connection test",
        "model"      : "test",
    }).execute()
    print(f"\n✅ INSERT works — row id: {res.data[0]['id']}")

    # Test 2 — Read it back
    res2 = client.table("chat_history") \
        .select("*") \
        .eq("session_id", "test-session-001") \
        .execute()
    print(f"✅ SELECT works — got {len(res2.data)} row(s)")

    # Test 3 — Delete test row (cleanup)
    client.table("chat_history") \
        .delete() \
        .eq("session_id", "test-session-001") \
        .execute()
    print("✅ DELETE works — test row cleaned up")

    print("\n🎉 Supabase is fully working!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nCommon fixes:")
    print("  - Check SUPABASE_URL and SUPABASE_KEY in .env")
    print("  - Make sure the chat_history table exists (run the SQL schema)")
    print("  - Check your Supabase project is not paused")