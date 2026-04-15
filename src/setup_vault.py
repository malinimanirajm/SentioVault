import weaviate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the client
client = weaviate.Client(
    url=os.getenv("WEAVIATE_URL")
)

def create_sentio_vault_schema():
    # Define the 'Class' (Table) for our SentioVault
    class_obj = {
        "class": "SentioTransaction",
        "description": "Financial records with integrated cognitive and decision metrics",
        "vectorizer": "text2vec-openai",  # Or 'text2vec-google'
        "moduleConfig": {
            "text2vec-openai": {
                "model": "ada",
                "modelVersion": "002",
                "type": "text"
            }
        },
        "properties": [
            {
                "name": "transaction_id",
                "dataType": ["text"],
                "description": "The unique identifier for the transaction",
            },
            {
                "name": "category",
                "dataType": ["text"],
                "description": "Expenditure category (e.g., Investment, Grocery)",
            },
            {
                "name": "amount",
                "dataType": ["number"],
                "description": "The transaction value",
            },
            {
                "name": "cognitive_load_score",
                "dataType": ["number"],
                "description": "User's mental effort during the transaction",
            },
            {
                "name": "decision_quality",
                "dataType": ["number"],
                "description": "The logic/quality rating of the financial choice",
            },
            {
                "name": "prediction_confidence",
                "dataType": ["number"],
                "description": "The AI's confidence in its recommendation",
            }
        ]
    }

    # Clear existing schema if you're re-running (be careful!)
    if client.schema.exists("SentioTransaction"):
        client.schema.delete_class("SentioTransaction")
        print("Existing class deleted.")

    client.schema.create_class(class_obj)
    print("SentioVault Schema created successfully!")

if __name__ == "__main__":
    create_sentio_vault_schema()