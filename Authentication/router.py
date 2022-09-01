from typing import List

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import auth
from . import crud, schemas
from Shop.crud import get_cart

authRouter = APIRouter(
    prefix="/user",
    tags=["Authentication"]
)

security = HTTPBearer()
auth_handler = auth.Auth()


@authRouter.get("/list")
async def users(
    credentials: HTTPAuthorizationCredentials = Security(security),
    skip: int = 0,
    limit: int = 10
) -> List[dict]:
    """
        Get List of Users
    """
    token = credentials.credentials
    payload = auth_handler.decode_token(token)

    if payload["user_type"] != "SA":
        raise HTTPException(
            status_code=401,
            detail="Clients Are Not Allowed for This Request!"
        )

    if payload["user_type"] == "SA":
        return crud.get_users(skip, limit)

    raise HTTPException(
        status_code=400,
        detail="You Are Not Allowed for This Request!"
    )


@authRouter.post("/auth/register")
async def sign_up(user: schemas.UserAuth, cart_index: str, user_type: str = "CL"):
    db_user = crud.get_user_by_mobile(user.mobile)

    if not crud.verify_mobile(user.mobile):
        raise HTTPException(
            status_code=401,
            detail=f"Mobile ({user.mobile}) Is Not A Valid Mobile Number!"
        )

    if db_user:
        raise HTTPException(
            status_code=401,
            detail=f"Mobile ({user.mobile}) Already Exists!"
        )

    if user_type.upper() not in ["CL", "SA"]:
        user_type = "CL"

    inserted_id = crud.register_user(user, cart_index, user_type.upper())
    return str(inserted_id)


@authRouter.post("/auth/login")
async def sign_in(user: schemas.UserAuth):
    db_user = crud.get_user_by_mobile(user.mobile)

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail=f"Mobile ({user.mobile}) Is Not Registered Yet!"
        )

    user_pass = user.password + "hashing"
    if auth_handler.verify_password(
        user_pass,
        db_user["security"]
    ):
        access_token = auth_handler.encode_token(
            user.mobile,
            db_user["user_type"]
        )
        refresh_token = auth_handler.encode_refresh_token(user.mobile)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "cart": None}

    raise HTTPException(
        status_code=401,
        detail=f"Password is WRONG!"
    )


@authRouter.get("/auth/refresh_token")
def refresh_token(user_type: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    new_token = auth_handler.refresh_token(refresh_token, user_type)
    return {"access_token": new_token}
