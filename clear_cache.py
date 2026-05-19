import os
import weaviate
from weaviate.classes.query import Filter
from dotenv import load_dotenv

load_dotenv()

def flush_cache():
    port = int(os.getenv("WEAVIATE_PORT", 8081))
    print(f"🔌 Connecting to local Weaviate on port {port}...")
    
    client = weaviate.connect_to_local(port=port)
    try:
        if client.collections.exists("SentioCache"):
            cache = client.collections.get("SentioCache")
            
            # FIX: Use a catch-all filter to bypass gRPC empty-filter guardrails
            result = cache.data.delete_many(
                where=Filter.by_property("user_id").not_equal("SYSTEM_RESERVED_EMPTY_ID")
            )
            
            print("🧹 SentioCache collection cleared successfully!")
            print(f"🗑️ Successful matches removed: {result.matches}")
        else:
            print("⚠️ SentioCache collection does not exist in this vault.")
    except Exception as e:
        print(f"❌ Failed to clear cache: {e}")
    finally:
        client.close()
        print("🔌 Weaviate connection closed.")

if __name__ == "__main__":
    flush_cache()