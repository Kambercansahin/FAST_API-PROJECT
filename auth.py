from datetime import UTC,datetime,timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from config import settings

from typing import Annotated

from sqlalchemy import  select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends,HTTPException,status

import models
from database import get_db

password_hash = PasswordHash.recommended() # hash with argon2

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token") #Gets the Bearer Token from the header and give it to user.

def hash_password(password:str) ->str: #created hash password
    return password_hash.hash(password)

def verify_password(plain_password:str,hashed_password:str) ->bool: # verifying hash pw and user input pw
    return  password_hash.verify(plain_password,hashed_password)


"""Create a JWT access token."""
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    # I am copying the data because , I don't want to use original data
    to_encode = data.copy()
    # if I  define token time
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    #if I do not define token time
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes,
        )
    # I am adding  time info  in the data
    to_encode.update({"exp": expire})
    #I create encode
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )
    return encoded_jwt

"""Verify a JWT access token and return the subject (user id) if valid."""
def verify_access_token(token: str) -> str | None:

    try:
        decode_data = jwt.decode(
            token,
            settings.secret_key.get_secret_value(), #check the sign
            algorithms=[settings.algorithm], #check the algo
            options={"require": ["exp", "sub"]}, # check "exp" and "sub"
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return decode_data.get("sub")

async def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db:Annotated[AsyncSession,Depends(get_db)])->models.User:
    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except(TypeError,ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(models.User).where(models.User.id == user_id_int))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user

Current_User = Annotated[models.User,Depends(get_current_user)]