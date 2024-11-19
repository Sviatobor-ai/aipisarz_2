from collections.abc import AsyncGenerator, Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from httpx import AsyncClient
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.db import engine
from app.models import User

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/eee")


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient() as client:
        yield client


ClientDep = Annotated[AsyncClient, Depends(get_client)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = security.decode_jwt_access_token(token)
    except (InvalidTokenError, ValidationError) as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cound not validate credentials",
        ) from err

    user = session.get(User, payload.sub)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
