import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import common_utils.database as database
import common_utils.s3 as s3

uri = os.environ.get("DB_URI")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['auxiom_database']
bills_collection = db['bills']


bills = database.get_all_bills(bills_collection)
deleted = []
for bill in bills:
    if not bill.get('text') or bill.get('text') == '':
        database.delete_bill(bills_collection, bill.get('_id'))
        deleted.append(bill.get('bill_id'))

print(deleted)
print(f'deleted {len(deleted)} bills')
