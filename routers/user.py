from typing import Annotated
from fastapi import APIRouter,Depends,HTTPException,status

from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import  UserUpdate,UserCreate,PostResponse,UserPublic,UserPrivate,Token

from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import create_access_token,verify_access_token,hash_password,password_hash,verify_password,oauth2_scheme,Current_User
from config import settings


router = APIRouter()

#With DB
@router.post("",response_model=UserPrivate,status_code=status.HTTP_201_CREATED) #created new users
async def create_user(user:UserCreate,db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.User).where(
        func.lower(models.User.username)== user.username.lower()
    ),
    )

    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Kullanıcı adı mevcut")

    result_email = await db.execute(select(models.User).where(func.lower(models.User.email) == user.email.lower()))
    existing_email = result_email.scalars().first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email sistemde mevcut")

    new_user = models.User(
        username=user.username,
        email =user.email.lower(),
        password_hash = hash_password(user.password)
    )
    db.add(new_user)# add to db
    await db.commit() # saved to db
    await db.refresh(new_user)#refresh the db
    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: Annotated[AsyncSession, Depends(get_db)],):
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
    result = await db.execute(
        select(models.User).where(func.lower(models.User.email) == form_data.username.lower(),),)

    user = result.scalars().first()

    # Verify user exists and password is correct
    # Don't reveal which one failed (security best practice)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user id as subject
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserPrivate)
async def get_current_user(current_user:Current_User):
    return current_user



@router.get("/{user_id}",response_model=UserPublic) #get the user with user_id
async def get_user(user_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    result_user = await db.execute(select(models.User).where(models.User.id == user_id))#check the user
    existing_user = result_user.scalars().first()
    if existing_user: # if it exist return
        return existing_user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Böyle bir kullanıcı yoktur") #if not throw exception

@router.get("/{user_id}/posts",response_model=list[PostResponse])#get all posts from each user
async def get_user_posts(user_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    result_user = await db.execute(select(models.User).where(models.User.id == user_id))#check the user
    existing_user = result_user.scalars().first()
    if not existing_user:# if it not in the db throw exception
        raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Böyle bir kullanıcı yok")

    result_post = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc()),
    )#check the post
    existing_posts = result_post.scalars().all()
    return existing_posts #return all posts

@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user(user_id: int,user_update: UserUpdate,current_user:Current_User,db: Annotated[AsyncSession, Depends(get_db)]):

    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Yetkiniz yok değiştirmek için")

    result = await db.execute(select(models.User).where(models.User.id == user_id)) #get the user_id
    user = result.scalars().first()
    if not user: #if no user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı yok",
        )

    if user_update.username is not None and user_update.username.lower() != user.username.lower(): # if username not empty and username not equal to past username
        result = await db.execute(
            select(models.User).where(func.lower(models.User.username) == user_update.username.lower()),
        )
        existing_user = result.scalars().first()
        if existing_user: # If there is a user
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="bu kullanıcı var",
            )

    if user_update.email is not None and user_update.email.lower() != user.email.lower():# if email not empty and email not equal to past email
        result = await db.execute(
            select(models.User).where(func.lower(models.User.email) == user_update.email.lower()),
        )
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu email zaten kullaniliyor",
            )

    if user_update.username is not None: # if username is not None
        user.username = user_update.username
    if user_update.email is not None:#if email is not None
        user.email = user_update.email.lower()
    if user_update.image_file is not None:#if image file is not None
        user.image_file = user_update.image_file

    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int,current_user:Current_User, db: Annotated[AsyncSession, Depends(get_db)]):

    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Yetkiniz yok silmek için")

    result = await db.execute(select(models.User).where(models.User.id == user_id))#take the user_id
    user = result.scalars().first()
    if not user:# if user not in the db
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(user) # if user in the db delete user and post
    await db.commit()