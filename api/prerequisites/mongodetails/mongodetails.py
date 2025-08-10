from pymongo import MongoClient
import json

# --- Configuration ---
MONGO_URI = "mongodb://localhost:27017"   # Change if needed
DATABASE_NAME = "transaction_db"      # Replace with your DB name
COLLECTIONS = ["accounts", "merchants", "transactions", "users"]  # Replace with your collections
OUTPUT_FILE = "mongo_collections_details.txt"

# --- Connect to MongoDB ---
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

def fetch_collection_details(collection_name):
    collection = db[collection_name]
    
    # Get a sample document (if any exists)
    sample_doc = collection.find_one()
    if sample_doc:
        sample_doc = json.loads(json.dumps(sample_doc, default=str))  # Ensure serializable
    else:
        sample_doc = "No documents in this collection."

    # Get index info
    indexes = collection.index_information()

    return {
        "collection": collection_name,
        "sample_document": sample_doc,
        "indexes": indexes
    }

# --- Collect details ---
details = []
for col in COLLECTIONS:
    details.append(fetch_collection_details(col))

# --- Write to file ---
with open(OUTPUT_FILE, "w") as f:
    for detail in details:
        f.write(json.dumps(detail, indent=4))
        f.write("\n\n---\n\n")

print(f"Collection details saved to {OUTPUT_FILE}")
