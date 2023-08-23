from pymongo import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

'''
This script tests if the mongo db database is correctley connected
'''

MONGO_URL = os.environ["MONGO_URL"]

client = MongoClient(MONGO_URL)

# database name
db = client['urlshortener']

# collection name
links_collection = db['links']

# creating a new document for testing purposes
new_link = {
    "slug": "98f1b7",
    "original_url": "https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html",
    "created_at": datetime.utcnow()
}

# move document into 'links' collection
insert_result = links_collection.insert_one(new_link)

# check if successful
if insert_result.acknowledged:
    print("Link erfolgreich eingefügt, ID:", insert_result.inserted_id)
else:
    print("Das Einfügen des Links ist fehlgeschlagen.")

# Optional: list all collections
for link in links_collection.find():
    print(link)
