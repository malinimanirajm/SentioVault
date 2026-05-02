import pandas as pd
import weaviate
import os
from weaviate.util import generate_uuid5
from dotenv import load_dotenv

load_dotenv()

def ingest_to_sentio_vault(csv_file_path):
    client = weaviate.connect_to_local()
    df = pd.read_csv(csv_file_path)
    
    # Fix the typo from previous version & handle NaNs
    df = df.rename(columns={'Cognitivre_Load_Score': 'cognitive_load_score'}) 
    df = df.fillna({'decision_quality': 0.0, 'cognitive_load_score': 0.0, 'Amount': 0.0})

    collection = client.collections.get("SentioTransaction")
    
    objects = []
    for _, row in df.iterrows():
        data_properties = {
            "transaction_id": str(row["Transaction_ID"]),
            "category": str(row["Category"]),
            "amount": float(row["Amount"]),
            "cognitive_load_score": float(row["cognitive_load_score"]),
            "decision_quality": float(row["Decision_Quality"]),
            "transaction_type": str(row["Transaction_Type"])
        }
        objects.append(weaviate.classes.data.DataObject(
            properties=data_properties,
            uuid=generate_uuid5(data_properties["transaction_id"])
        ))

    print(f"🚀 Ingesting {len(objects)} records...")
    result = collection.data.insert_many(objects)
    
    if result.has_errors:
        print(f"❌ Ingestion had errors: {result.errors}")
    else:
        print("✅ Ingestion Complete!")
    client.close()

if __name__ == "__main__":
    ingest_to_sentio_vault("financial_data_2024_2025.csv")