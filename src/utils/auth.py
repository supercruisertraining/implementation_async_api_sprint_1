from http import HTTPStatus

import jwt
from aiohttp import ClientSession
from fastapi import Header, HTTPException

from core.config import config


class PermissionChecker:
    def __init__(self, minimal_role: str):
        self.minimal_role = minimal_role

    async def __call__(self, authorization: str = Header()):
        if config.TEST:
            return True
        if not authorization:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Token not found",
            )
        token = authorization.split(" ")[1]
        try:
            data = jwt.decode(
                token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM],
            )
            user_id = data.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail="Invalid Authentication token.",
                )
        except Exception:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )
        try:
            async with ClientSession() as session:
                url = config.CHECK_PERMISSION_URL
                async with session.get(
                    url,
                    params={
                        "resource_role_name": self.minimal_role,
                        "user_id": user_id,
                    },
                ) as response:
                    if response.ok:
                        body = await response.json()
                        if body["result"] == "success":
                            return True
                    response.raise_for_status()
        except Exception:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="Client has no permissions",
            )
