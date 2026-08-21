from pymongo import MongoClient
from pymongo.server_api import ServerApi

MONGO_URI = "YOUR_URI_HERE"
# Create a new client and connect to the server


COLLECTION_NAME = "geospatial-data"

def get_mongo_client() -> MongoClient:
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    return client

def ingest_into_mongodb():
    client = get_mongo_client()
    database = client.get_database()
    collection = database.get_collection(COLLECTION_NAME)

