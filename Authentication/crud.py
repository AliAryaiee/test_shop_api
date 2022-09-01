from string import ascii_lowercase, ascii_uppercase, digits
from typing import List
import random

import bcrypt

from . import schemas
from db_config import (
    users_collection,
    carts_collection,
    comments_collection,
    address_collection,
    invoices_collection
)

CHARS = list(ascii_lowercase + ascii_uppercase + digits)


def get_last_user_id() -> int:
    """
        Get Last User ID
    """
    # Latest (Newest) Inserted Document
    last_user = users_collection.find_one(
        sort=[("id", -1)],
        projection={"security": 0}
    )
    if last_user:
        return last_user["id"]
    return 0


def get_users(skip: int = 0, limit: int = 10) -> List[dict]:
    """
        Get List of Users
    """
    return [
        item
        for item in users_collection.find({}, {"_id": 0, "security": 0}).skip(skip).limit(limit)
    ]


def get_user(id: int) -> dict:
    """
        Find A User by ID
    """
    return users_collection.find_one({"id": id}, {"_id": 0})


def get_user_by_mobile(mobile: str) -> List[dict]:
    """
        Find A User by Mobile Number
    """
    return users_collection.find_one({"mobile": mobile}, {"_id": 0})


def register_user(user: schemas.UserAuth, cart_index: str, user_type: str = "CL"):
    """
        Register A New User
    """
    user_pass = user.password + "hashing"
    hashed_password = bcrypt.hashpw(
        user_pass.encode('utf-8'),
        bcrypt.gensalt()
    )
    last_id = get_last_user_id()

    db_user = {
        "id": last_id + 1,
        "mobile": user.mobile,
        "security": hashed_password.decode("utf-8"),
        "user_type": user_type,
        "cart_index": cart_index,
    }

    return users_collection.insert_one(db_user).inserted_id


# ---------------------------------------------------------------------
def verify_mobile(mobile: str) -> bool:
    """
        Verify Mobile Number
    """
    c1 = len(mobile) != 11
    c2 = mobile[:2] != "09"
    c3 = not all([digit in digits for digit in mobile])

    conditions = [c1, c2, c3]
    if any(conditions):
        return False
    return True


# ---------------------------------------------------------------------
def find_userIDs() -> List[str]:
    """
        Find All UserIDs
    """
    return [item["user_id"] for item in users_collection.find({}, {"user_id": 1})]


def generate_user_id(email: str) -> str:
    """
        Generate UserID from Email
    """
    user_id = email.split("@")[0]
    length = len(user_id)
    addition = ""
    if length < 3:
        addition = random_key((3 - length), 12)
    new_user_id = (user_id + addition)[:12]

    user_ids = find_userIDs()
    while new_user_id in user_ids:
        if length < 3:
            addition = random_key((3 - length), 12)
        new_user_id = (user_id + addition)[:12]

    return new_user_id


def random_key(min_length: int = 8, max_length: int = 12):
    """
        Generate A Random String
    """
    length = random.randint(min_length, max_length)
    number = random.randint(max_length, max_length * 2)
    all_chars = CHARS * number
    parts_size = (len(all_chars) // length)
    parts_size += (1 if (len(all_chars) % length) else 0)

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
