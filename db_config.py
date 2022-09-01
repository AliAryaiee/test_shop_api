from pymongo import MongoClient
from decouple import config

# Database Connection Information
MONGO_DB_USERNAME = config("MONGO_DB_USERNAME")
MONGO_DB_PASSWORD = config("MONGO_DB_PASSWORD")
MONGO_DB_HOSTNAME = config("MONGO_DB_HOSTNAME")
DB_NAME = ""
if config("DB_NAME"):
    DB_NAME = config("DB_NAME")

# Create Connection MongoDB URI
connection_string = f"{MONGO_DB_USERNAME}:{MONGO_DB_PASSWORD}@{MONGO_DB_HOSTNAME}/{DB_NAME}"
MONGO_DB_URI = f"mongodb+srv://{connection_string}?retryWrites=true&w=majority"

# Connect to the MongoDB Cluster
connection = MongoClient(MONGO_DB_URI)

# Select A Database
db = connection[DB_NAME]

# Collections
users_collection = db.users
products_collection = db.new_products
categories_collection = db.categories
carts_collection = db.carts
address_collection = db.address
comments_collection = db.comments
invoices_collection = db.invoices
messages_collection = db.messages


if __name__ == "__main__":
    print(db.list_collection_names())
