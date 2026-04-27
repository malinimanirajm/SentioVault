import pandas as pd
import weaviate
from weaviate.util import generate_uuid5
import os
from dotenv import load_dotenv

load_dotenv()

def ingest_to_sentio_vault(csv_file_path):
    client = weaviate.Client(url=os.getenv("WEAVIATE_URL"))
    df = pd.read_csv(csv_file_path)
    
    # Cleaning column names and filling missing values
    df = df.fillna({'Decision_Quality': 0.0, 'Cognitivre_Load_Score': 0.0, 'Amount': 0.0})

    client.batch.configure(batch_size=100)
    print(f"🚀 Ingesting {len(df)} records...")

    with client.batch as batch:
        for _, row in df.iterrows():
            data_object = {
                "transaction_id": str(row["Transaction_ID"]),
                "category": str(row["Category"]),
                "amount": float(row["Amount"]),
                "cognitive_load_score": float(row["Cognitivre_Load_Score"]),
                "decision_quality": float(row["Decision_Quality"]),
                "prediction_confidence": float(row["Prediction_Confidence"]),
                "transaction_type": str(row["Transaction_Type"])
            }
            batch.add_data_object(
                data_object=data_object,
                class_name="SentioTransaction",
                uuid=generate_uuid5(data_object["transaction_id"])
            )

    print("✅ Ingestion Complete!")

if __name__ == "__main__":
    ingest_to_sentio_vault("financial_data_2024_2025.csv")