from typing import List

from fastapi import APIRouter, HTTPException, File, UploadFile, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import crud, schemas
import auth


shopRouter = APIRouter(
    prefix="/shop",
    tags=["Shop"]
)

security = HTTPBearer()
auth_handler = auth.Auth()


# ----------- { CATEGORY Endpoints } -----------
@shopRouter.get("/category")
async def categories(skip: int = 0, limit: int = 12):
    """
        List of Latest Categories
    """
    return crud.categories(skip, limit)


@shopRouter.get("/category/{category_id}")
async def get_category(category_id: int):
    """
        Find A Category
    """
    return crud.get_category(category_id)


@shopRouter.post("/category/new")
async def new_category(
    title: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """
        Create A New Product
    """
    token = credentials.credentials
    payload = auth_handler.decode_token(token)

    if payload["user_type"] != "SA":
        raise HTTPException(
            status_code=401,
            detail="Clients Are Not Allowed for This Request!"
        )

    if payload["user_type"] == "SA":
        category_db = crud.create_new_category(title)
        try:
            del category_db["_id"]
            return category_db
        except:
            return str(category_db.inserted_id)

    raise HTTPException(
        status_code=400,
        detail="You Are Not Allowed for This Request!"
    )


# ----------- { PRODUCT Endpoints } -----------
@shopRouter.get("/products")
async def products(skip: int = 0, limit: int = 12):
    """
        List of Latest Products
    """
    return crud.products(skip, limit)


@shopRouter.get("/products/top")
async def top_products(skip: int = 0, limit: int = 12):
    """
        List of Best Products
    """
    return crud.products(skip, limit)


@shopRouter.post("/products/new")
async def new_product(
    product: schemas.ProductRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """
        Create A New Product
    """
    token = credentials.credentials
    payload = auth_handler.decode_token(token)

    if payload["user_type"] != "SA":
        raise HTTPException(
            status_code=401,
            detail="Clients Are Not Allowed for This Request!"
        )

    if payload["user_type"] == "SA":
        product_db = crud.create_new_product(product)
        del product_db["_id"]
        return product_db

    raise HTTPException(
        status_code=400,
        detail="You Are Not Allowed for This Request!"
    )


@shopRouter.post("/products/image")
async def upload_product_image(
    credentials: HTTPAuthorizationCredentials = Security(security),
    image: UploadFile = File(...),
    image_key: str = "",
    is_public: bool = True
):
    """
        Register An Invoice
    """

    token = credentials.credentials
    payload = auth_handler.decode_token(token)

    if payload["user_type"] != "SA":
        raise HTTPException(
            status_code=401,
            detail="Clients Are Not Allowed for This Request!"
        )

    if payload["user_type"] == "SA":
        if not image_key:
            image_key = str(image.filename)

        image_url = crud.save_product_image(image, image_key)
        if not image_url:
            raise HTTPException(401, "Image Wasn't Uploaded!")
        print("Image Has Uploaded Successfully!")
        return {
            "image_url": image_url
        }

    raise HTTPException(
        status_code=400,
        detail="You Are Not Allowed for This Request!"
    )


@shopRouter.get("/products/by_id")
async def get_product(product_id: int):
    """
        Find A Product
    """
    return crud.get_product(product_id) or {}


@shopRouter.get("/products/search")
async def filter_products_by_category(category_id: int):
    return crud.get_category_products(category_id)


# ----------- { CART Endpoints } -----------
@shopRouter.get("/carts")
async def carts(
    credentials: HTTPAuthorizationCredentials = Security(security),
    skip: int = 0,
    limit: int = 12
):
    """
        List of Latest Carts
    """
    token = credentials.credentials
    payload = auth_handler.decode_token(token)

    if payload["user_type"] != "SA":
        raise HTTPException(
            status_code=401,
            detail="Clients Are Not Allowed for This Request!"
        )

    if payload["user_type"] == "SA":
        return crud.carts(skip, limit)

    raise HTTPException(
        status_code=400,
        detail="You Are Not Allowed for This Request!"
    )


@shopRouter.get("/carts/new")
async def new_cart(user_id: int = 0):
    """
        Create A New Cart Index
    """
    return crud.create_new_cart(user_id)


@shopRouter.post("/carts/update")
def update_cart_items(cart_index: str, items: List[dict]):
    """
        Update A Cart
    """
    return crud.update_cart_items(cart_index, items)


@shopRouter.get("/carts/find")
async def get_cart(cart_index: str):
    """
        Find A Cart
    """
    return crud.get_cart(cart_index) or {}


@shopRouter.post("/cart/invoice")
async def upload_invoice(image: UploadFile = File(...), image_key: str = "", is_public: bool = True):
    """
        Register An Invoice
    """
    if not image_key:
        image_key = str(image.filename)
    print(f"ImageKey => {image_key}")

    image_url = crud.save_invoice_image(image, image_key)
    if not image_url:
        raise HTTPException(401, "Image Wasn't Uploaded!")
    print("Image Has Uploaded Successfully!")
    return {
        "image_url": image_url
    }


@shopRouter.post("/cart/invoice/register")
async def register(invoice: schemas.InvoiceRequest):
    """
        Register Invoice
    """
    try:
        print(invoice.dict())
        return crud.create_new_cart()
    except Exception as error:
        print(error)


# ----------- { MESSAGE Endpoints } -----------
@shopRouter.post("/messages/new")
async def send_message(message: schemas.MessageUser):
    """
        POST A Message
    """
    message_db = crud.post_message(message)
    try:
        del message_db["_id"]
        return message_db
    except:
        return str(message_db.inserted_id)
