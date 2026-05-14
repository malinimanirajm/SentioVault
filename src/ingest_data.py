import os
import boto3
import pandas as pd
import weaviate
from weaviate.util import generate_uuid5
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

def upload_backup_to_s3(csv_path):
    s3 = boto3.client('s3')
    bucket = os.getenv("S3_BUCKET_NAME")
    file_name = os.path.basename(csv_path)
    try:
        s3.upload_file(csv_path, bucket, file_name)
        print(f"☁️ AWS S3: Backup successful (s3://{bucket}/{file_name})")
    except Exception as e:
        print(f"⚠️ AWS S3: Backup failed - {e}")

def ingest_data(csv_path):
    # 1. Cloud Backup (Always Free Tier)
    upload_backup_to_s3(csv_path)

    # 2. Local Ingestion
    client = weaviate.connect_to_local(port=int(os.getenv("WEAVIATE_PORT", 8081)))
    try:
        df = pd.read_csv(csv_path)
        
        # Normalize Column Names (Remove spaces and make lowercase)
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Handle typo/normalization for the specific HCI columns
        df = df.fillna(0.0)

        collection = client.collections.get("SentioTransaction")
        objects = []
        
        print(f"📊 Processing {len(df)} financial records...")

        for _, row in df.iterrows():
            # Mapping the CSV columns to our Weaviate Schema
            props = {
        "transaction_id": str(row.get("transaction_id", "0")),
        "user_id": str(row.get("user_id", "unknown_user")),
        "category": str(row.get("category", "Uncategorized")),
        "amount": float(row.get("amount", 0.0)),
        "transaction_type": str(row.get("transaction_type", "Debit")),
        # Ensure these match your actual data values
        "cognitive_load_score": float(row.get("cognitive_load_score", 0.0)),
        "decision_quality": float(row.get("decision_quality", 0.0)),
        "feedback_score": float(row.get("feedback_score", 0.0))
    }
            
            objects.append(weaviate.classes.data.DataObject(
                properties=props,
                uuid=generate_uuid5(props["transaction_id"])
            ))

        print(f"🚀 Ingesting records into local Weaviate vault...")
        result = collection.data.insert_many(objects)
        
        if result.has_errors:
            print(f"❌ Errors during ingestion: {result.errors}")
        else:
            print("✅ Ingestion Complete. Data is now searchable by User_ID and Category.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        client.close()
        print("🔌 Weaviate connection closed.")

if __name__ == "__main__":
    # Ensure this matches your actual CSV filename
    ingest_data("financial_hci_dataset.csv")