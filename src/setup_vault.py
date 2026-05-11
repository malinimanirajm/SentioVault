import weaviate
from weaviate.classes.config import Configure, DataType, Property

def setup_sentio_vault():
    # Connecting to your local Docker instance
    client = weaviate.connect_to_local(port=8081)

    # 1. Transaction Collection (Enhanced Knowledge Graph Node)
    if client.collections.exists("SentioTransaction"):
        print("🗑️ Removing existing collection to apply new schema...")
        client.collections.delete("SentioTransaction")
        
    client.collections.create(
        name="SentioTransaction",
        vectorizer_config=Configure.Vectorizer.text2vec_ollama(
            api_endpoint="http://host.docker.internal:11434",
            model="nomic-embed-text",
        ),
        properties=[
            # Core Transaction Data
            Property(name="transaction_id", data_type=DataType.TEXT),
            Property(name="user_id", data_type=DataType.TEXT),
            Property(name="category", data_type=DataType.TEXT),
            Property(name="amount", data_type=DataType.NUMBER),
            Property(name="transaction_type", data_type=DataType.TEXT),
            
            # HCI & Behavioral Metrics (from your dataset)
            Property(name="cognitive_load_score", data_type=DataType.NUMBER),
            Property(name="decision_quality", data_type=DataType.NUMBER),
            Property(name="feedback_score", data_type=DataType.NUMBER),
        ]
    )
    
    print("✅ Local Weaviate Schema Initialized with User_ID and HCI Metrics.")

    client.close()

if __name__ == "__main__":
    setup_sentio_vault()