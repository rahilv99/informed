# Invoked with a single new bill event. Extracts key events from bill, processes and stores in database

import google.generativeai as genai
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import s3
import sqs
import database

uri = os.environ.get("DB_URI", "mongodb+srv://admin:astrapodcast!@auxiom-backend.7edkill.mongodb.net/?retryWrites=true&w=majority&appName=auxiom-backend")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['auxiom_database']
bills_collection = db['bills']
events_collection = db['events']


def handler(payload):
    id = payload.get("id")

    print(f"Processing event for bill: {id}")

    # Get bill from database
    existing_bill = database.get_bill(bills_collection, id)