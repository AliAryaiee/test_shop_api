from string import ascii_lowercase, ascii_uppercase, digits
from datetime import datetime
from typing import List
import random

import boto3
from decouple import config
from fastapi import UploadFile

from . import schemas
from db_config import (
    carts_collection,
    categories_collection,
    comments_collection,
    products_collection,
    invoices_collection,
    messages_collection,
    address_collection
)


CHARS = list(ascii_lowercase + ascii_uppercase + digits)
STORAGE_URL = config('ARVAN_BASE_URL')
BUCKET_INVOICES = config("BUCKET_INVOICES")
BUCKET_PRODUCTS = config("BUCKET_PRODUCTS")
client = boto3.resource(
    service_name="s3",
    endpoint_url=STORAGE_URL,
    aws_access_key_id=config("ARVAN_CLOUD_ACCESS_KEY"),
    aws_secret_access_key=config("ARVAN_CLOUD_SECRET_KEY")
)


# ----------- { CATEGORY Functionalities } -----------
def get_last_category_id() -> int:
    """
        Get Last Category ID
    """
    # Latest (Newest) Inserted Document
    last_category = categories_collection.find_one(sort=[("id", -1)])
    if last_category:
        return last_category["id"]
    return 0


def categories(skip: int = 0, limit: int = 12) -> List[dict]:
    """
        Get Categories
    """
    return [
        category
        for category in categories_collection.find({}, {"_id": 0}).sort([("id", 1)]).skip(skip).limit(limit)
    ]


def create_new_category(title: str):
    """
        Create A New Category
    """
    last_id = get_last_category_id()
    created_at = datetime.now()
    category = {
        "id":  last_id + 1,
        "title": title,
        "products": []
    }
    category_db = categories_collection.insert_one(category)
    print(
        f"A New Category Was Created by ID ({category_db.inserted_id}) <=> {last_id + 1} [{created_at}]"
    )
    return category_db


def get_category(category_id: int):
    """
        Find A Category by ProductID
    """
    return categories_collection.find_one({"id": category_id}, {"_id": 0})


def add_new_product_to_category(product_id: int, category_id: int):
    """
        Create A New Category
    """
    return categories_collection.find_one_and_update(
        {"id": category_id},
        {'$push': {'products': product_id}},
        {"_id": 0},
        upsert=True
    )


# ----------- { PRODUCT Functionalities } -----------
def save_product_image(image: UploadFile, image_key: str):
    """
        Upload A Product Image
    """
    image_url = ""
    bucket = client.Bucket(BUCKET_PRODUCTS)
    try:
        bucket.upload_fileobj(
            image.file,
            image_key,
            ExtraArgs={"ACL": "public-read"}
        )
        image_url = f"{STORAGE_URL}/{BUCKET_PRODUCTS}/{image_key}"
    except Exception:
        pass

    return image_url


def get_last_product_id() -> int:
    """
        Get Last Cart ID
    """
    # Latest (Newest) Inserted Document
    last_product = products_collection.find_one(sort=[("id", -1)])
    if last_product:
        return last_product["id"]
    return 0


def products(skip: int = 0, limit: int = 12) -> List[dict]:
    """
        Get Products
    """
    return [
        product
        for product in products_collection.find({}, {"_id": 0}).sort([("id", -1)]).skip(skip).limit(limit)
    ]


def create_new_product(product: schemas.ProductRequest):
    """
        Create A New Product
    """
    last_id = get_last_product_id()
    add_new_product_to_category(last_id + 1, product.category)

    created_at = datetime.now()
    product_db = {
        "id":  last_id + 1,
        "title": product.title,
        "slug": product.slug,
        "category": product.category,
        "description": product.description,
        "unit_price": product.unit_price,
        "stock": product.stock,
        "score": product.score,
        "released_at": datetime.now(),
        "cover": product.cover,
        "images": [],
        "comments": [],
        "views": 0,
        "sales": 0,
        "offer": 0,
        "preview": True,
    }
    cart_db = products_collection.insert_one(product_db)
    print(
        f"A New Product Was Created by ID ({cart_db.inserted_id}) <=> {last_id + 1} [{created_at}]"
    )

    return product_db


def get_product(product_id: str):
    """
        Find A Product by ProductID
    """
    return products_collection.find_one({"id": product_id}, {"_id": 0})


def update_product_items(cart_index: str, items: List[dict]):
    """
        Update Cart Values Like:
            Cart Items
            Amounts
            Total
    """
    amounts = 0
    total = 0
    for item in items:
        amounts += item["quantity"]
        total += item["unit_price"] * item["quantity"]

    return products_collection.find_one_and_update(
        {"cart_index": cart_index},
        {
            "$set": {
                "items": items,
                "amounts": amounts,
                "total": total,
            }
        },
        upsert=False
    )


def get_category_products(category_id: int, skip: int = 0, limit: int = 12) -> List[dict]:
    """
        Get List of Products Related to A Specific Category
    """
    return [
        product
        for product in products_collection.find({"category": category_id}, {"_id": 0}).sort([("id", -1)]).skip(skip).limit(limit)
    ]


# ----------- { CART Functionalities } -----------
def save_invoice_image(image: UploadFile, image_key: str):
    """
        Upload Invoice Image
    """
    image_url = ""
    bucket = client.Bucket(BUCKET_INVOICES)
    try:
        bucket.upload_fileobj(
            image.file,
            image_key,
            ExtraArgs={"ACL": "public-read"}
        )
        image_url = f"{STORAGE_URL}/{BUCKET_INVOICES}/{image_key}"
    except Exception:
        pass

    return image_url


def get_last_cart_id() -> int:
    """
        Get Last Cart ID
    """
    # Latest (Newest) Inserted Document
    last_cart = carts_collection.find_one(sort=[("id", -1)])
    if last_cart:
        return last_cart["id"]
    return 0


def carts(skip: int = 0, limit: int = 12) -> List[dict]:
    """
        Get Carts
    """
    return [
        cart
        for cart in carts_collection.find({}, {"_id": 0}).sort([("id", -1)]).skip(skip).limit(limit)
    ]


def create_new_cart(user_id: int = 0):
    """
        Create A New Cart
    """
    cart_index = random_cart_id()

    while get_cart(cart_index):
        cart_index = random_cart_id()

    last_id = get_last_cart_id()
    created_at = datetime.now()
    cart = {
        "id":  last_id + 1,
        "cart_index": cart_index,
        "user_id": user_id,
        "items": [],
        "amounts":  0,
        "total":  0,
        "created_at": created_at,
    }
    cart_db = carts_collection.insert_one(cart)
    print(
        f"A New Cart Was Created by ID ({cart_db.inserted_id}) -> {cart_index} <=> {last_id + 1} [{created_at}]"
    )
    return get_cart(cart_index)


def get_cart(cart_index: str):
    """
        Find A Cart by Cart Index
    """
    return carts_collection.find_one({"cart_index": cart_index}, {"_id": 0})


def update_cart_items(cart_index: str, items: List[dict]):
    """
        Update Cart Values Like:
            Cart Items
            Amounts
            Total
    """
    amounts = 0
    total = 0
    for item in items:
        amounts += item["quantity"]
        total += item["unit_price"] * item["quantity"]

    return carts_collection.find_one_and_update(
        {"cart_index": cart_index},
        {
            "$set": {
                "items": items,
                "amounts": amounts,
                "total": total,
            }
        },
        upsert=False
    )


# ----------- { MESSAGE Functionalities } -----------
def get_last_message_id() -> int:
    """
        Get Last Message ID
    """
    # Latest (Newest) Inserted Document
    last_category = messages_collection.find_one(sort=[("id", -1)])
    if last_category:
        return last_category["id"]
    return 0


def messages(skip: int = 0, limit: int = 12) -> List[dict]:
    """
        Get Categories
    """
    return [
        message
        for message in messages_collection.find({}, {"_id": 0}).sort([("id", -1)]).skip(skip).limit(limit)
    ]


def post_message(request: schemas.MessageUser):
    """
        Add A New Message
    """
    last_id = get_last_message_id()
    message_index = random_cart_id()
    message_object = {
        "id":  last_id + 1,
        "mesaage_index":  message_index,
        "user_id": request.user_id,
        "name": request.name,
        "email": request.email,
        "mobile": request.mobile,
        "message": request.message,
        "date": datetime.now(),
        "responsed": False,
    }
    message_object_db = messages_collection.insert_one(message_object)
    print(
        f"A New Message Has Received by ID ({message_object_db.inserted_id}) <=> {last_id + 1} [{datetime.now()}]"
    )
    return message_object_db


def get_message(mesaage_index: str):
    """
        Find A Message by Message Index
    """
    return messages_collection.find_one({"mesaage_index": mesaage_index}, {"_id": 0})


def response_message(mesaage_index: str, response: str):
    """
        Response To A Message
    """
    return messages_collection.find_one_and_update(
        {"mesaage_index": mesaage_index},
        {'$set': {'response': response, "responded": True}},
        {"_id": 0},
        upsert=True
    )


# Helper Functions
def random_cart_id(length: int = 8):
    """
        Generate Random CartID
    """
    number = random.randint(length, length * 2)
    all_chars = CHARS * number
    charz = len(all_chars)
    parts_size = (charz // length)
    parts_size += (1 if (charz % length) else 0)

    for _ in range(number):
        random.shuffle(all_chars)

    parts = [
        all_chars[index * parts_size:(index + 1) * parts_size]
        for index in range(length)
    ]

    return "".join(
        [
            random.choices(part, k=length)[random.randint(0, length - 1)]
            for part in parts
        ]
    )


if __name__ == "__main__":
    pass
