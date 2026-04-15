import pandas as pd
import weaviate
from weaviate.util import generate_uuid5
import os
from dotenv import load_dotenv

load_dotenv()

def ingest_to_sentio_vault(csv_file_path):
    # 1. Initialize Client
    client = weaviate.Client(url=os.getenv("WEAVIATE_URL"))
    
    # 2. Load the 2024-2025 Dataset
    df = pd.read_csv(csv_file_path)
    
    # Optional: Fill missing values to maintain FSI data integrity
    df = df.fillna({
        'Decision_Quality': 0.0,
        'Cognitivre_Load_Score': 0.0,
        'Amount': 0.0
    })

    # 3. Configure Batching (Efficient for large financial datasets)
    client.batch.configure(batch_size=100)
    
    print(f"Starting ingestion for {len(df)} records...")

    with client.batch as batch:
        for index, row in df.iterrows():
            # Create the data object mapping CSV columns to Weaviate properties
            data_object = {
                "transaction_id": str(row["Transaction_ID"]),
                "category": str(row["Category"]),
                "amount": float(row["Amount"]),
                "cognitive_load_score": float(row["Cognitivre_Load_Score"]),
                "decision_quality": float(row["Decision_Quality"]),
                "prediction_confidence": float(row["Prediction_Confidence"]),
                "transaction_type": str(row["Transaction_Type"])
            }

            # Generate a consistent UUID based on the Transaction ID
            uuid = generate_uuid5(data_object["transaction_id"])
            
            # Push to the 'SentioTransaction' class we created in Step 1
            batch.add_data_object(
                data_object=data_object,
                class_name="SentioTransaction",
                uuid=uuid
            )

    print("Ingestion Complete! SentioVault is now populated.")

if __name__ == "__main__":
    # Ensure your CSV is in the same directory
    ingest_to_sentio_vault("financial_data_2024_2025.csv")