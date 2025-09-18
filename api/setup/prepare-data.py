import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
from pymongo import MongoClient
import bson

fake = Faker()
client = MongoClient("mongodb://localhost:27017/")
db = client["finadvisor"]

users_collection = db["users"]          
transactions_collection = db["transactions"]  

numberOfRecords = 30000
num_users = max(30, numberOfRecords // 1000)  
num_merchants = 750

transaction_types = ["credit", "debit", "refund"]
transaction_modes = ["UPI", "Card", "BankTransfer", "Cash"]
statuses = ["initiated", "success", "failed", "refunded"]

merchant_categories = {
    "Food": ["Restaurant", "Cafe", "Food Delivery", "Bakery", "Fast Food"],
    "Shopping": ["Clothing Store", "Electronics Store", "Supermarket", "Online Retail", "Bookstore"],
    "Petrol": ["Gas Station", "Fuel Pump"],
    "Travel": ["Airline", "Hotel", "Travel Agency", "Car Rental"],
    "Entertainment": ["Movie Theater", "Concert Venue", "Amusement Park", "Streaming Service", "Subscription"],
    "Utilities": ["Electricity Provider", "Water Supply", "Internet Provider", "Mobile Recharge"],
    "Health": ["Hospital", "Pharmacy", "Clinic"],
    "Finance": ["Bank", "Insurance", "Brokerage", "Loan Provider"],
    "Education": ["School", "College", "Online Courses", "Stationery"],
    "Government": ["Tax Office", "Municipality", "Toll", "License Fees"],
    "Others": ["Gym", "Spa", "Charity", "Miscellaneous"]
}

merchant_types = [m for types in merchant_categories.values() for m in types]

def random_timestamp():
    return fake.date_time_between(start_date="-365d", end_date="now")

def create_users_if_empty():
    existing = users_collection.estimated_document_count()
    if existing >= num_users:
        return [doc["_id"] for doc in users_collection.find({}, {"_id": 1})]

    users = []
    for _ in range(num_users - existing):
        users.append({
            "_id": str(uuid.uuid4()),
            "name": fake.name(),
            "email": fake.email(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        })
    if users:
        users_collection.insert_many(users)

    return [doc["_id"] for doc in users_collection.find({}, {"_id": 1})]

def create_accounts(user_ids):

    accounts = []
    for uid in user_ids:
        accounts.append({
            "_id": str(uuid.uuid4()),
            "user_id": uid,
            "account_number": fake.iban(),
        })
    return accounts

def create_merchants():
    merchants = []
    for _ in range(num_merchants):
        m_type = random.choice(merchant_types)
        merchants.append({
            "_id": str(uuid.uuid4()),
            "name": f"{fake.company()} {m_type}",
            "type": m_type,
            "category": next(cat for cat, vals in merchant_categories.items() if m_type in vals),
        })
    return merchants

def create_transactions_merged(user_ids, accounts, merchants):

    account_by_user = {a["user_id"]: a for a in accounts}
    users_by_id = {u["_id"]: u for u in users_collection.find({}, {"_id": 1, "name": 1})}

    batch = []
    batch_size = 5000
    total = 0

    for _ in range(numberOfRecords):
        user_id = random.choice(user_ids)
        from_acc = account_by_user[user_id]

        is_merchant_payment = random.random() < 0.7
        merchant_obj = None
        to_account_obj = None
        description = ""
        remarks = ""

        if is_merchant_payment:
            merchant_obj = random.choice(merchants)
            description = f"Payment to {merchant_obj['name']}"
            remarks = f"{merchant_obj['type']} expense"
        else:
            to_user_id = random.choice([uid for uid in user_ids if uid != user_id])
            to_acc = account_by_user[to_user_id]
            to_account_obj = {
                "_id": to_acc["_id"],
                "user_id": to_acc["user_id"],
                "user_name": users_by_id.get(to_acc["user_id"], {}).get("name"),  # <-- added
                "account_number": to_acc["account_number"],
            }
            to_user_name = users_by_id.get(to_user_id, {}).get("name", "Recipient")
            description = f"Transfer to {to_user_name}"
            remarks = fake.sentence(nb_words=3)

        initiated_at = random_timestamp()
        status = random.choice(statuses)
        completed_at = initiated_at + timedelta(minutes=random.randint(1, 60)) if status in ("success", "refunded") else None
        failed_at = initiated_at + timedelta(minutes=random.randint(1, 60)) if status == "failed" else None

        currency = "INR" if random.random() < 0.9 else random.choice(["USD", "EUR"])
        amount = round(random.uniform(10, 10000), 2) if currency == "INR" else round(random.uniform(1, 1000), 2)

        txn_doc = {
            "_id": str(uuid.uuid4()),
            "transaction_id": str(uuid.uuid4()),
            "user_id": user_id,

            "from_account": {
                "_id": from_acc["_id"],
                "user_id": from_acc["user_id"],
                "user_name": users_by_id.get(from_acc["user_id"], {}).get("name"), 
                "account_number": from_acc["account_number"],
            },

            "to_account": to_account_obj, 
            "merchant": (
                None if not is_merchant_payment else {
                    "_id": merchant_obj["_id"],
                    "name": merchant_obj["name"],
                    "type": merchant_obj["type"],
                    "category": merchant_obj["category"],
                }
            ),

     
            "amount": amount,
            "currency": currency,
            "transaction_type": random.choice(transaction_types),
            "transaction_mode": random.choice(transaction_modes),
            "status": status,

            "initiated_at": initiated_at,
            "completed_at": completed_at,
            "failed_at": failed_at,

            # Misc
            "remarks": remarks,
            "description": description,
            "reference_number": str(bson.ObjectId()),
            "order_id": str(uuid.uuid4()) if is_merchant_payment else None,

            "created_at": initiated_at,
            "updated_at": datetime.now(),
        }

        batch.append(txn_doc)
        if len(batch) >= batch_size:
            transactions_collection.insert_many(batch)
            total += len(batch)
            batch.clear()

    if batch:
        transactions_collection.insert_many(batch)
        total += len(batch)

    return total

if __name__ == "__main__":
    users_collection.drop()
    transactions_collection.drop()

    user_ids = create_users_if_empty()
    accounts = create_accounts(user_ids)
    merchants = create_merchants()
    total = create_transactions_merged(user_ids, accounts, merchants)

    print(f"Generated {len(user_ids)} users, {len(accounts)} accounts, "
          f"{len(merchants)} merchants, and {total} transactions")
