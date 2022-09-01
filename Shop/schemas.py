from random import randint
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field
from decouple import config

ARVAN_BASE_URL = config("ARVAN_BASE_URL")
BUCKET_INVOICES = config("BUCKET_INVOICES")
BUCKET_PRODUCTS = config("BUCKET_PRODUCTS")


class MessageUser(BaseModel):
    """
        Message Inputs Schema
    """
    user_id: int = Field(0, ge=0)
    name: str = Field("کاربر", max_length=64)
    email: str = Field("", max_length=128)
    mobile: str = Field("09000000000", min_length=11, max_length=11)
    message: str = Field(..., max_length=1024)

    class Config:
        """
            Configuration
        """
        schema_extra = {
            "example": {
                "user_id": 0,
                "name": "کاربر",
                "email": "",
                "mobile": "09000000000",
                "message": "نظر کاربر",
            }
        }


class Message(BaseModel):
    """
        Message Schema
    """
    id: int = Field(..., gt=0)
    mesaage_index: str = Field(..., min_length=8, max_length=8)
    user_id: int = Field(0, ge=0)
    name: str = Field("کاربر", max_length=64)
    email: str = Field("", max_length=128)
    mobile: str = Field("09000000000", min_length=11, max_length=11)
    message: str = Field(..., max_length=1024)
    date: datetime = Field(datetime.now())
    response: str = Field("", max_length=1024)
    responded: bool = False

    class Config:
        """
            Configuration
        """
        schema_extra = {
            "example": {
                "id": randint(1, 100),
                "mesaage_index": 1,
                "user_id": 0,
                "name": "کاربر",
                "email": "",
                "mobile": "09000000000",
                "message": "نظر کاربر",
                "date": datetime.now(),
                "response": "",
                "responded": False,
            }
        }


class Comment(BaseModel):
    """
        Comment Schema
    """
    id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    user_id: int = Field(..., ge=0)
    name: str = Field("کاربر", max_length=64)
    email: str = Field("", max_length=128)
    mobile: str = Field("09000000000", min_length=11, max_length=11)
    comment: str = Field(..., min_length=16, max_length=1024)
    date: datetime = Field(datetime.now())
    accepted: bool = False

    class Config:
        """
            Configuration
        """
        schema_extra = {
            "example": {
                "id": randint(1, 100),
                "product_id": 1,
                "user_id": 0,
                "name": "کاربر",
                "email": "",
                "mobile": "09000000000",
                "comment": "نظر کاربر",
                "date": datetime.now(),
                "accepted": False,
            }
        }


class Category(BaseModel):
    """
        Category Schema
    """
    id: int = Field(..., gt=0)
    title: str = Field(..., max_length=128)
    products: List[int] = []

    class Config:
        """
            Configuration
        """
        schema_extra = {
            "example": {
                "id": randint(1, 100),
                "title": "عنوان دسته‌بندی",
                "products": []
            }
        }


class Product(BaseModel):
    """
        Product Schema
    """
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=8, max_length=128)
    slug: str = Field(..., min_length=8, max_length=256)
    category: int = Field(..., gt=0)
    description: str = Field("", max_length=1024)
    unit_price: int = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    score: float = Field(5, ge=0)
    released_at: datetime = datetime.now()
    cover: str = Field(..., max_length=256)
    images: List[str] = []
    comments: List[int] = []
    views: int = Field(0, ge=0)
    sales: int = Field(0, ge=0)
    offer: int = Field(0, ge=0)
    preview: bool = True

    class Config:
        """
            Configuration
        """
        schema_extra = {
            "example": {
                "id": randint(1, 100),
                "title": "عنوان محصول",
                "slug": "عنوان-محصول",
                "category": 1,
                "description": "توضیحات محصول",
                "unit_price": 40_000,
                "stock": 0,
                "score": 5,
                "released_at": datetime.now(),
                "cover": "",
                "images": [],
                "comments": [],
                "views": 0,
                "sales": 0,
                "offer": 0,
                "preview": True,
            }
        }


class ProductRequest(BaseModel):
    """
        Product Request Schema
    """
    title: str = Field(..., min_length=8, max_length=128)
    slug: str = Field(..., min_length=8, max_length=256)
    category: int = Field(..., gt=0)
    description: str = Field("", max_length=1024)
    unit_price: int = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    score: float = Field(5, ge=0)
    cover: str = Field(..., max_length=256)

    class Config:
        """
            Configuration
        """
        schema_extra = {
            "example": {
                "title": "عنوان محصول",
                "slug": "عنوان-محصول",
                "category": 1,
                "description": "توضیحات محصول",
                "unit_price": 40_000,
                "stock": 0,
                "score": 5,
                "cover": ""
            }
        }


class ProductItem(BaseModel):
    """
        Product Item Schema
    """
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=8, max_length=128)
    unit_price: int = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    cover: str = Field(..., max_length=128)
    stock: int = Field(..., ge=0)
    # score: float = Field(5, ge=0)

    class Config:
        """
            Configuration
        """
        schema_extra = {
            "example": {
                "product_id": randint(1, 100),
                "title": "عنوان محصول",
                "unit_price": 40_000,
                "quantity": 1,
                "cover": "",
                "stock": 0,
                # "score": 0
            }
        }


class Cart(BaseModel):
    """
        Cart Schema
    """
    id: int = Field(..., gt=0)
    cart_index: str = Field(..., min_length=8, max_length=8)
    user_id: int = Field(0, ge=0)
    items: List[ProductItem] = []
    amounts: int = Field(0, ge=0)
    total: int = Field(0, ge=0)
    created_at: datetime = datetime.now()
    status: str = "pending"
    # last_modified: datetime = datetime.now()

    class Config:
        """
            Configuration
        """
        schema_extra = {
            "example": {
                "id": randint(1, 100),
                "cart_index": "random_key",
                "user_id": 0,
                "items": [],
                "amounts": 0,
                "total": 0,
                "created_at": datetime.now(),
                "status": "pending"
            }
        }


class InvoiceRequest(BaseModel):
    """
        docstring
    """
    cart_index: str = Field(..., min_length=8, max_length=8)
    user_id: int = Field(0, ge=0)
    items: list = []
    amounts: int = Field(0, ge=0)
    total: int = Field(0, ge=0)
    created_at: datetime = datetime.now()

    first_name: str = Field(..., min_length=2, max_length=128)
    last_name: str = Field(..., min_length=2, max_length=128)
    mobile: str = Field(..., min_length=11, max_length=11)
    email: str = Field("", max_length=128)
    province: str = Field(..., min_length=2, max_length=128)
    city: str = Field(..., min_length=2, max_length=128)
    details: str = Field(..., max_length=512)
    zip_code: str = Field(..., min_length=10, max_length=10)
    status: str = Field("pending", min_length=4, max_length=7)
    invoice: str = Field(..., max_length=256)

    class Config:
        """
            Configuration
        """
        schema_extra = {
            "example": {
                "cart_index": "random_key",
                "user_id": 0,
                "items": [],
                "amounts": 0,
                "total": 0,
                "created_at": datetime.now(),
                "first_name": "نام",
                "last_name": "نام خانوادگی",
                "mobile": "09123456789",
                "email": "youremail@gmail.com",
                "province": "تهران",
                "city": "تهران",
                "details": "خیابان ...",
                "zip_code": "1234567890",
                "status": "pending",
                "invoice": "image_url",
            }
        }


class Invoice(Cart):
    """
        Invoice Schema
    """

    # Address Schema
    first_name: str = Field(..., min_length=2, max_length=128)
    last_name: str = Field(..., min_length=2, max_length=128)
    mobile: str = Field(..., min_length=11, max_length=11)
    email: str = Field("", max_length=128)
    province: str = Field(..., min_length=2, max_length=128)
    city: str = Field(..., min_length=2, max_length=128)
    details: str = Field(..., max_length=512)
    zip_code: str = Field(..., min_length=10, max_length=10)
    invoice: str = Field(..., max_length=128)

    class Config:
        """
            Configuration
        """
        schema_extra = {
            "example": {
                "id": randint(1, 100),
                "cart_index": "random_key",
                "user_id": 0,
                "items": [],
                "amounts": 0,
                "total": 0,
                "created_at": datetime.now(),
                "status": "paid",
                "first_name": "نام",
                "last_name": "نام خانوادگی",
                "mobile": "09123456789",
                "email": "youremail@gmail.com",
                "province": "تهران",
                "city": "تهران",
                "details": "خیابان ...",
                "zip_code": "1234567890",
                "invoice": "image_url",
            }
        }
