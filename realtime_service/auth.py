import os

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()


JWT_SECRET = os.getenv("SECRET_KEY")
JWT_ALGORITHM = "HS256"


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user_id = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload",
        )

    return int(user_id)