import weaviate
import os
from dotenv import load_dotenv

load_dotenv()

def setup_schema():
    # Connect using v4 Client
    client = weaviate.connect_to_local() 
    
    # Define collection (formerly 'class')
    if client.collections.exists("SentioTransaction"):
        client.collections.delete("SentioTransaction")
        
    client.collections.create(
        name="SentioTransaction",
        vectorizer_config=weaviate.classes.config.Configure.Vectorizer.text2vec_openai(),
        properties=[
            weaviate.classes.config.Property(name="transaction_id", data_type=weaviate.classes.config.DataType.TEXT),
            weaviate.classes.config.Property(name="category", data_type=weaviate.classes.config.DataType.TEXT),
            weaviate.classes.config.Property(name="amount", data_type=weaviate.classes.config.DataType.NUMBER),
            weaviate.classes.config.Property(name="cognitive_load_score", data_type=weaviate.classes.config.DataType.NUMBER),
            weaviate.classes.config.Property(name="decision_quality", data_type=weaviate.classes.config.DataType.NUMBER),
            weaviate.classes.config.Property(name="transaction_type", data_type=weaviate.classes.config.DataType.TEXT),
        ]
    )
    print("✅ Schema created: SentioTransaction")
    client.close()

if __name__ == "__main__":
    setup_schema()