from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import random

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['cashify']
transactions_col = db['transactions']

# Generate sample transactions for the last 5 months
def generate_transactions(user_id, months=5, transactions_per_month=5):
    transaction_categories = ["Food", "Transportation", "Entertainment", "Groceries", "Utilities"]
    transaction_descriptions = {
        "Food": ["Lunch at McDonald's", "Dinner at Olive Garden", "Snack at Starbucks", "Burger King meal", "Chipotle bowl"],
        "Transportation": ["Uber ride", "Gas refill", "Bus pass", "Parking fee", "Car wash"],
        "Entertainment": ["Movie tickets", "Netflix subscription", "Concert ticket", "Bowling night", "Arcade games"],
        "Groceries": ["Walmart groceries", "Publix shopping", "Trader Joe's run", "Costco bulk buy", "Target food items"],
        "Utilities": ["Electric bill", "Water bill", "Internet bill", "Phone bill", "Trash service"]
    }

    transactions = []
    today = datetime.today()

    for month_offset in range(months):
        # Get the first day of the month
        first_day_of_month = (today - timedelta(days=today.day - 1)) - timedelta(days=30 * month_offset)

        for _ in range(transactions_per_month):
            category = random.choice(transaction_categories)
            description = random.choice(transaction_descriptions[category])
            amount = round(random.uniform(10, 100), 2)  # Random deduction between $10 and $100
            date = first_day_of_month + timedelta(days=random.randint(0, 27))  # Random day in the month

            transaction = {
                "user_id": user_id,
                "amount": amount,  # Deductions
                "category": category,
                "date": date.strftime("%Y-%m-%d"),  # Format as YYYY-MM-DD
                "type": "expense",
                "description": description,
                "tags": [category.lower(), "expense"]
            }
            transactions.append(transaction)

    return transactions

# Insert the generated transactions into the database
def insert_sample_transactions(user_id):
    transactions = generate_transactions(user_id=user_id)
    transactions_col.insert_many(transactions)
    print(f"Inserted {len(transactions)} transactions for user_id {user_id}.")

# Replace this with the actual user_id from your database
user_id = "677dad20eab577df50b5e616"  # Replace with ObjectId if necessary
insert_sample_transactions(user_id)
