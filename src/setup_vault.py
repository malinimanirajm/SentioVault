import weaviate
from weaviate.classes.config import Configure, DataType, Property

def setup_sentio_vault():
    client = weaviate.connect_to_local(port=8081)

    # 1. Transaction Collection
    if client.collections.exists("SentioTransaction"):
        print("🗑️ Removing existing Transaction collection...")
        client.collections.delete("SentioTransaction")
        
    client.collections.create(
        name="SentioTransaction",
        vectorizer_config=Configure.Vectorizer.text2vec_ollama(
            api_endpoint="http://host.docker.internal:11434",
            model="nomic-embed-text",
        ),
        properties=[
            Property(name="transaction_id", data_type=DataType.TEXT),
            Property(name="user_id", data_type=DataType.TEXT),
            Property(name="category", data_type=DataType.TEXT),
            Property(name="amount", data_type=DataType.NUMBER),
            Property(name="transaction_type", data_type=DataType.TEXT),
            Property(name="cognitive_load_score", data_type=DataType.NUMBER),
            Property(name="decision_quality", data_type=DataType.NUMBER),
            Property(name="feedback_score", data_type=DataType.NUMBER),
        ]
    )
    print("✅ SentioTransaction Schema Initialized.")

    # 2. Cache Collection 
    if client.collections.exists("SentioCache"):
        print("🗑️ Removing existing Cache collection...")
        client.collections.delete("SentioCache")

    client.collections.create(
        name="SentioCache",
        vectorizer_config=Configure.Vectorizer.text2vec_ollama(
            api_endpoint="http://host.docker.internal:11434",
            model="nomic-embed-text",
        ),
        properties=[
            Property(name="user_id", data_type=DataType.TEXT),  
            Property(name="query", data_type=DataType.TEXT),
            Property(name="response", data_type=DataType.TEXT),
        ]
    )
    print("✅ SentioCache Schema Initialized.")
    client.close()

if __name__ == "__main__":
    setup_sentio_vault()