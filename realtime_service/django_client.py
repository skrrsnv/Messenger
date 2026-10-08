import os

import httpx
from dotenv import load_dotenv

load_dotenv()

DJANGO_URL = os.getenv("DJANGO_URL")


async def validate_token(token: str) -> int | None:
    url = f"{DJANGO_URL}/api/v1/internal/auth/validate/"

    headers = {
        "Authorization": f"Bearer {token}",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers,
        )

    if response.status_code != 200:
        return None

    return response.json()["user_id"]


async def is_conversation_member(
    conversation_id: int,
    user_id: int,
) -> bool:
    url = (
        f"{DJANGO_URL}/api/v1/internal/"
        f"conversations/{conversation_id}/members/{user_id}/"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return False

    data = response.json()

    return data["is_member"]