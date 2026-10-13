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


async def is_conversation_member(conversation_id: int, user_id: int,) -> bool:
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


async def create_message(conversation_id: int, text: str, user_access_token: str,) -> dict | None:
    url = (
        f"{DJANGO_URL}/api/v1/internal/"
        f"conversations/{conversation_id}/messages/"
    )

    internal_token = os.getenv("INTERNAL_API_TOKEN")

    if not internal_token:
        raise RuntimeError("INTERNAL_API_TOKEN is not configured")

    headers = {
        "X-Internal-Token": internal_token,
        "Authorization": f"Bearer {user_access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=headers,
            json={"text": text},
            timeout=10.0,
        )

    if response.status_code != 201:
        print(
            "Django message creation failed:",
            response.status_code,
            response.text,
        )
        return None

    return response.json()