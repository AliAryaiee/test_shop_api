import time                                 # Used to Handle Expiry Time for Tokens
import datetime as dt                       # Used to Handle Expiry Time for Tokens

import jwt                                  # Used for Encoding and Decoding JWT Tokens
import bcrypt                               # Used for Hashing the Password
from decouple import config
from fastapi import HTTPException           # Used to Handle Error Handling


class Auth():
    secret = config("JWT_SECRET")
    algorithm = config("JWT_ALGORITHM")

    def encode_password(self, password: str) -> bytes:
        """
            Hashing the Password
        """
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def verify_password(self, password: str, hashed_password: str):
        """
            Decode the Password
        """
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    def encode_token(self, user_id: str, user_type: str = "CL", remember: bool = False) -> str:
        """
            Generate JWT Token
        """
        # Set Expiry Time
        expiry = dt.timedelta(hours=24)
        if remember:
            expiry = dt.timedelta(days=7)

        issued_at = int(time.time())

        payload = {
            'user_id': user_id,
            'user_type': user_type,
            'expiry': issued_at + int(expiry.total_seconds()),
            'iat': issued_at,
            'state': 'access_token',
        }

        return jwt.encode(
            payload,
            self.secret,
            algorithm=self.algorithm
        )

    def decode_token(self, token: str):
        """
            Decode JWT Token
        """
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )
            # print(payload)
            if (payload['state'] == 'access_token'):
                # return payload['user_id'], payload["user_type"]
                return payload
            raise HTTPException(
                status_code=401,
                detail='Scope for the Token is Invalid'
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token Expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid Token')

    def encode_refresh_token(self, user_id, remember: bool = False) -> str:
        """
            Refresh JWT Token
        """
        expiry = dt.timedelta(hours=24)
        if remember:
            expiry = dt.timedelta(days=7)

        issued_at = int(time.time())

        payload = {
            'user_id': user_id,
            'expiry': issued_at + int(expiry.total_seconds()),
            'iat': issued_at,
            'state': 'refresh_token',
        }

        return jwt.encode(
            payload,
            self.secret,
            algorithm=self.algorithm
        )

    def refresh_token(self, refresh_token, user_type: str):

        try:
            payload = jwt.decode(
                refresh_token,
                self.secret,
                algorithms=[self.algorithm]
            )
            if (payload['state'] == 'refresh_token'):
                user_id = payload['user_id']
                new_token = self.encode_token(user_id, user_type)
                return new_token
            raise HTTPException(
                status_code=401,
                detail='Invalid Scope for Token'
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail='Refresh Token Expired'
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401, detail='Invalid Refresh Token'
            )
