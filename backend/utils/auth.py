from models.user import User, UserInDB
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from typing import Annotated

from fake_db.fake_db import fake_users


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def fake_hashed_password(password: str):
    return "fakehashed" + password


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    
    return None


def fake_decode_token(token: str):
    user = get_user(fake_users, token)
    
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    print(f"Token: {token}")
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)],):
    if current_user.disabled:
        raise HTTPException(
            status_code=400,
            detail="Inactive user",
        )
    
    return current_user
