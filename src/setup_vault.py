import weaviate
import os
from dotenv import load_dotenv

load_dotenv()

def setup_schema():
    client = weaviate.Client(url=os.getenv("WEAVIATE_URL"))
    
    class_obj = {
        "class": "SentioTransaction",
        "description": "Financial transactions with cognitive and sentiment metrics",
        "vectorizer": "text2vec-openai", 
        "properties": [
            {"name": "transaction_id", "dataType": ["string"]},
            {"name": "category", "dataType": ["string"]},
            {"name": "amount", "dataType": ["number"]},
            {"name": "cognitive_load_score", "dataType": ["number"]},
            {"name": "decision_quality", "dataType": ["number"]},
            {"name": "prediction_confidence", "dataType": ["number"]},
            {"name": "transaction_type", "dataType": ["string"]}
        ]
    }

    if client.schema.exists("SentioTransaction"):
        client.schema.delete_class("SentioTransaction")
        
    client.schema.create_class(class_obj)
    print("✅ Schema created: SentioTransaction")

if __name__ == "__main__":
    setup_schema()