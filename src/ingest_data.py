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
        df.columns = [c.strip().lower() for c in df.columns]
        df = df.fillna(0.0)

        collection = client.collections.get("SentioTransaction")
        objects = []
        for _, row in df.iterrows():
            props = {
                "transaction_id": str(row.get("transaction_id", "0")),
                "category": str(row.get("category", "Unknown")),
                "amount": float(row.get("amount", 0.0)),
                "transaction_type": str(row.get("transaction_type", "Debit"))
            }
            objects.append(weaviate.classes.data.DataObject(
                properties=props,
                uuid=generate_uuid5(props["transaction_id"])
            ))

        print(f"🚀 Ingesting {len(objects)} records...")
        collection.data.insert_many(objects)
        print("✅ Local Ingestion Complete.")
    finally:
        client.close()

if __name__ == "__main__":
    ingest_data("financial_hci_dataset.csv")