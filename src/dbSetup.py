from pymongo import MongoClient
import os
from dotenv import load_dotenv
import hashlib
from datetime import datetime

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['cashify']

# Drop ALL existing collections for a complete reset
for collection_name in db.list_collection_names():
    db[collection_name].drop()

# Re-create necessary collections
users_col = db['users']
transactions_col = db['transactions']
categories_col = db['categories']
budgets_col = db['budgets']

# Hashing function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Insert sample users
users_data = [
    {
        "first_name": "Aidan",
        "last_name": "Quach",
        "email": "aidanquach314@gmail.com",
        "password_hash": hash_password("123"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "testuser2@example.com",
        "password_hash": hash_password("securepassword2"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
]

user_ids = users_col.insert_many(users_data).inserted_ids

# Insert sample budgets linked to users
budgets_data = [
    {
        "user_id": user_ids[0],  # Aidan
        "monthly_budget": 3000.0,
        "categories": [
            {"category_name": "Food", "allocated_amount": 500.0, "spent_amount": 300.0},
            {"category_name": "Transportation", "allocated_amount": 300.0, "spent_amount": 100.0}
        ],
        "total_utilization": 40.0
    },
    {
        "user_id": user_ids[1],  # Jane
        "monthly_budget": 2000.0,
        "categories": [
            {"category_name": "Rent", "allocated_amount": 1000.0, "spent_amount": 1000.0},
            {"category_name": "Food", "allocated_amount": 500.0, "spent_amount": 200.0}
        ],
        "total_utilization": 60.0
    }
]

budgets_col.insert_many(budgets_data)

# Insert sample transactions linked to users
transactions_data = [
    {
        "user_id": user_ids[0],  # Aidan
        "amount": -50.0,
        "category": "Food",
        "date": "2025-01-02",
        "type": "expense",
        "description": "Lunch at Subway",
    },
    {
        "user_id": user_ids[0],  # Aidan
        "amount": -20.0,
        "category": "Transportation",
        "date": "2025-01-03",
        "type": "expense",
        "description": "Gas refill",
    },
    {
        "user_id": user_ids[1],  # Jane
        "amount": 1500.0,
        "category": "Salary",
        "date": "2025-01-01",
        "type": "income",
        "description": "Monthly paycheck",
    }
]

transactions_col.insert_many(transactions_data)

# Insert default categories
categories_data = [
    {"name": "Food", "type": "expense", "created_at": datetime.now().isoformat()},
    {"name": "Transportation", "type": "expense", "created_at": datetime.now().isoformat()},
    {"name": "Rent", "type": "expense", "created_at": datetime.now().isoformat()},
    {"name": "Salary", "type": "income", "created_at": datetime.now().isoformat()},
    {"name": "Freelancing", "type": "income", "created_at": datetime.now().isoformat()},
]

categories_col.insert_many(categories_data)

print("Database setup complete.")
