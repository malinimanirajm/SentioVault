import pandas as pd
import weaviate
from weaviate.util import generate_uuid5
import sys

def ingest_data(csv_path):
    # Using a context manager ('with') ensures the connection closes even if there's an error
    try:
        client = weaviate.connect_to_local(port=8081)
    except Exception as e:
        print(f"❌ Could not connect to Weaviate: {e}")
        return

    try:
        df = pd.read_csv(csv_path)
        
        # 1. Normalize Column Names (Remove hidden spaces and make lowercase)
        df.columns = [c.strip().lower() for c in df.columns]
        print(f"📊 Detected columns: {df.columns.tolist()}")

        # 2. Flexible Mapping
        # This maps what's in your CSV (left) to what Weaviate expects (right)
        mapping = {
            'transaction_id': 'transaction_id',
            'category': 'category',
            'amount': 'amount',
            'cognitivre_load_score': 'cognitive_load_score', # catching the common typo
            'cognitive_load_score': 'cognitive_load_score',
            'decision_quality': 'decision_quality',
            'transaction_type': 'transaction_type'
        }
        
        # Rename based on lowercase versions
        df = df.rename(columns=mapping)
        df = df.fillna(0.0)

        collection = client.collections.get("SentioTransaction")
        
        objects = []
        for index, row in df.iterrows():
            try:
                props = {
                    "transaction_id": str(row["transaction_id"]),
                    "category": str(row["category"]),
                    "amount": float(row["amount"]),
                    "cognitive_load_score": float(row["cognitive_load_score"]),
                    "decision_quality": float(row["decision_quality"]),
                    "transaction_type": str(row["transaction_type"])
                }
                objects.append(weaviate.classes.data.DataObject(
                    properties=props,
                    uuid=generate_uuid5(props["transaction_id"])
                ))
            except KeyError as e:
                print(f"❌ Missing expected column in CSV: {e}")
                print(f"Looked for: {e} but it wasn't found after normalization.")
                return

        print(f"🚀 Ingesting {len(objects)} financial records...")
        result = collection.data.insert_many(objects)
        
        if result.has_errors:
            print(f"❌ Errors during ingestion: {result.errors}")
        else:
            print("✅ Ingestion Complete.")

    except FileNotFoundError:
        print(f"❌ File not found: {csv_path}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        client.close()
        print("🔌 Weaviate connection closed.")

if __name__ == "__main__":
    # Ensure the file name matches your actual file
    ingest_data("financial_hci_dataset.csv")