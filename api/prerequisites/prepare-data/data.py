import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from pymongo import MongoClient
import bson

# Initialize Faker for synthetic data
fake = Faker()

# MongoDB connection setup (update with your MongoDB URI)
client = MongoClient('mongodb://localhost:27017/')
db = client['transaction_db']
users_collection = db['users']
accounts_collection = db['accounts']
merchants_collection = db['merchants']
transactions_collection = db['transactions']

# Configuration
numberOfRecords = 1000  # Number of transactions to generate
num_users = max(50, numberOfRecords // 20)  # At least 50 users, or 1 user per 20 transactions
num_merchants = 500  # Number of merchants

# Lists for transaction types, modes, statuses, and currencies
transaction_types = ['credit', 'debit', 'refund']
transaction_modes = ['UPI', 'Card', 'BankTransfer', 'Cash']
statuses = ['initiated', 'success', 'failed', 'refunded']
currencies = ['INR', 'USD', 'EUR']  # 90% INR

# Merchant categories for categorization
merchant_categories = {
    'Food': ['Restaurant', 'Cafe', 'Food Delivery', 'Bakery', 'Fast Food'],
    'Shopping': ['Clothing Store', 'Electronics Store', 'Supermarket', 'Online Retail', 'Bookstore'],
    'Petrol': ['Gas Station', 'Fuel Pump'],
    'Travel': ['Airline', 'Hotel', 'Travel Agency', 'Car Rental'],
    'Entertainment': ['Movie Theater', 'Concert Venue', 'Amusement Park', 'Streaming Service'],
    'Utilities': ['Electricity Provider', 'Water Supply', 'Internet Provider', 'Mobile Recharge'],
    'Others': ['Gym', 'Spa', 'Charity', 'Miscellaneous']
}

# Generate flat list of merchant types
merchant_types = [m_type for category in merchant_categories.values() for m_type in category]

# Helper function to generate random timestamp within last 365 days
def random_timestamp():
    return fake.date_time_between(start_date='-365d', end_date='now')

# Step 1: Create Users
def create_users():
    users = []
    for _ in range(num_users):
        user = {
            '_id': str(uuid.uuid4()),
            'name': fake.name(),
            'email': fake.email(),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        users.append(user)
    users_collection.insert_many(users)
    return [user['_id'] for user in users]

# Step 2: Create Accounts (one per user)
def create_accounts(user_ids):
    accounts = []
    for user_id in user_ids:
        account = {
            '_id': str(uuid.uuid4()),
            'user_id': user_id,
            'account_number': fake.iban(),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        accounts.append(account)
    accounts_collection.insert_many(accounts)
    return accounts

# Step 3: Create Merchants
def create_merchants():
    merchants = []
    for _ in range(num_merchants):
        merchant_type = random.choice(merchant_types)
        merchant = {
            '_id': str(uuid.uuid4()),
            'name': fake.company() + f" {merchant_type}",
            'type': merchant_type,
            'category': next(key for key, value in merchant_categories.items() if merchant_type in value),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        merchants.append(merchant)
    merchants_collection.insert_many(merchants)
    return [merchant['_id'] for merchant in merchants]

# Step 4: Create Transactions
def create_transactions(user_ids, accounts, merchant_ids):
    transactions = []
    account_map = {acc['user_id']: acc['_id'] for acc in accounts}
    
    for _ in range(numberOfRecords):
        user_id = random.choice(user_ids)
        from_account_id = account_map[user_id]
        
        # 70% chance to be a merchant transaction, 30% to another user
        if random.random() < 0.7:
            to_account_id = None
            merchant_id = random.choice(merchant_ids)
            merchant = merchants_collection.find_one({'_id': merchant_id})
            description = f"Payment to {merchant['name']}"
            remarks = f"{merchant['type']} expense"
        else:
            to_user_id = random.choice([uid for uid in user_ids if uid != user_id])
            to_account_id = account_map[to_user_id]
            merchant_id = None
            description = f"Transfer to {users_collection.find_one({'_id': to_user_id})['name']}"
            remarks = fake.sentence(nb_words=3)
        
        # Generate transaction details
        initiated_at = random_timestamp()
        status = random.choice(statuses)
        completed_at = initiated_at + timedelta(minutes=random.randint(1, 60)) if status == 'success' or status == 'refunded' else None
        failed_at = initiated_at + timedelta(minutes=random.randint(1, 60)) if status == 'failed' else None
        
        # Currency: 90% INR
        currency = 'INR' if random.random() < 0.9 else random.choice(['USD', 'EUR'])
        
        # Amount based on currency
        amount = round(random.uniform(10, 10000), 2) if currency == 'INR' else round(random.uniform(1, 1000), 2)
        
        transaction = {
            '_id': str(uuid.uuid4()),
            'transaction_id': str(uuid.uuid4()),
            'user_id': user_id,
            'from_account_id': from_account_id,
            'to_account_id': to_account_id,
            'merchant_id': merchant_id,
            'amount': amount,
            'currency': currency,
            'transaction_type': random.choice(transaction_types),
            'transaction_mode': random.choice(transaction_modes),
            'status': status,
            'initiated_at': initiated_at,
            'completed_at': completed_at,
            'failed_at': failed_at,
            'remarks': remarks,
            'description': description,
            'reference_number': str(bson.ObjectId()),
            'order_id': str(uuid.uuid4()) if merchant_id else None,
            'created_at': initiated_at,
            'updated_at': datetime.now()
        }
        transactions.append(transaction)
    
    transactions_collection.insert_many(transactions)

# Main execution
if __name__ == '__main__':
    # Clear existing collections (optional, for testing)
    users_collection.drop()
    accounts_collection.drop()
    merchants_collection.drop()
    transactions_collection.drop()
    
    # Generate data
    user_ids = create_users()
    accounts = create_accounts(user_ids)
    merchant_ids = create_merchants()
    create_transactions(user_ids, accounts, merchant_ids)
    
    print(f"Generated {num_users} users, {len(accounts)} accounts, {num_merchants} merchants, and {numberOfRecords} transactions.")