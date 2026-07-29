from typing import Annotated
from fastapi import APIRouter,Depends,HTTPException,status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import  UserUpdate,UserResponse,UserCreate,PostResponse

router = APIRouter()

#With DB
@router.post("",response_model=UserResponse,status_code=status.HTTP_201_CREATED) #created new users
async def create_user(user:UserCreate,db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.username == user.username))

    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Kullanıcı adı mevcut")

    result_email = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = result_email.scalars().first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email sistemde mevcut")

    new_user = models.User(
        username=user.username,
        email =user.email
    )
    db.add(new_user)# add to db
    await db.commit() # saved to db
    await db.refresh(new_user)#refresh the db
    return new_user


@router.get("/{user_id}",response_model=UserResponse) #get the user with user_id
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
    )#check the post
    existing_posts = result_post.scalars().all()
    return existing_posts #return all posts

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int,user_update: UserUpdate,db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(select(models.User).where(models.User.id == user_id)) #get the user_id
    user = result.scalars().first()
    if not user: #if no user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı yok",
        )

    if user_update.username is not None and user_update.username != user.username: # if username not empty and username not equal to past username
        result = await db.execute(
            select(models.User).where(models.User.username == user_update.username),
        )
        existing_user = result.scalars().first()
        if existing_user: # If there is a user
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="bu kullanıcı var",
            )

    if user_update.email is not None and user_update.email != user.email:# if email not empty and email not equal to past email
        result = await db.execute(
            select(models.User).where(models.User.email == user_update.email),
        )
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu email zaten kullanılıyor",
            )

    if user_update.username is not None: # if username is not None
        user.username = user_update.username
    if user_update.email is not None:#if email is not None
        user.email = user_update.email
    if user_update.image_file is not None:#if image file is not None
        user.image_file = user_update.image_file

    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))#take the user_id
    user = result.scalars().first()
    if not user:# if user not in the db
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(user) # if user in the db delete user and post
    await db.commit()