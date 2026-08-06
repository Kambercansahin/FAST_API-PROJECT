from datetime import UTC,datetime,timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from config import settings


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