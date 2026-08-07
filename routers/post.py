from typing import Annotated

from fastapi import HTTPException,status,Depends,APIRouter

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

import models
from database import get_db
from schemas import PostResponse,PostCreate,PostUpdate

from auth import Current_User

router = APIRouter()

@router.get("",response_model=list[PostResponse])
async def get_post(db:Annotated[AsyncSession,Depends(get_db)]): #get all posts
    result = await db.execute(select(models.Post)
                              .options(selectinload(models.Post.author))
                              .order_by(models.Post.date_posted.desc()),
                              )
    posts = result.scalars().all()
    return posts

@router.get("/{post_id}",response_model=PostResponse)
async def get_posts(post_id : int,db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id==post_id)
    )# specific post id
    post = result.scalars().first()
    if post:#if it have
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="404 ERROR")

@router.put("/{post_id}",response_model=PostResponse)
async def update_post_all(post_id :int,post_data:PostCreate,
                          current_user:Current_User,db:Annotated[AsyncSession,Depends(get_db)]):

    result = await db.execute(select(models.Post).where(models.Post.id==post_id))# specific post id
    post = result.scalars().first()

    if not post: #if post not in the db
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="404 ERROR")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yetkili kişi değil")

    post.title = post_data.title #post.title = post_data.title
    post.content = post_data.content#post.content = post_data.content

    await db.commit()
    await db.refresh(post,attribute_names=["author"])
    return post

@router.patch("/{post_id}",response_model=PostResponse)
async def update_post_patch(post_id :int, post_data:PostUpdate ,current_user:Current_User,db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id==post_id))# specific post id
    post = result.scalars().first()

    if not post:# if post is not in db
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="404 ERROR")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yetkili kişi değil")

    update_data = post_data.model_dump(exclude_unset=True) # if I want to perform an update when only a single value changes.
    for field,value in update_data.items():
        setattr(post,field,value)

    await db.commit()
    await db.refresh(post,attribute_names=["author"])
    return post

@router.delete("/{post_id}",status_code=status.HTTP_204_NO_CONTENT,name="delete_post")
async def delete_post(post_id:int ,current_user:Current_User, db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))#take the post_id in db
    post = result.scalars().first()

    if not post:#if post is not in db
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Böyle bir Post yok")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yetkili kişi değil")

    await db.delete(post)
    await db.commit()



@router.post("",response_model=PostResponse,status_code=status.HTTP_201_CREATED)
async def created_post(post:PostCreate,current_user:Current_User,db:Annotated[AsyncSession,Depends(get_db)]):

    new_post = models.Post(
        title = post.title,
        content = post.content,
        user_id = current_user.id
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post,attribute_names=["author"])
    return new_post

