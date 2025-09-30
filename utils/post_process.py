import os
import sys
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Add the parent directory to the Python path so we can import definitions
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import common_utils.database as database
from definitions.api import CongressGovAPI
from definitions.congress import Bill
from datetime import datetime

uri = os.environ.get("DB_URI")
api_key = os.environ.get("CONGRESS_API_KEY")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['auxiom_database']
bills_collection = db['bills']

# Initialize the API client
api_client = CongressGovAPI(api_key)

bills = database.get_all_bills(bills_collection)
deleted = []

for bill in bills:
    bill_id = bill.get('bill_id')

    # if before 2022 delete
    if bill.get('published_date') < 1640995200:
        deleted.append(bill_id)
        database.delete_bill(bills_collection, bill_id)
  

print(f"Post-processing complete:")
print(f"- Deleted {len(deleted)} old bills")
