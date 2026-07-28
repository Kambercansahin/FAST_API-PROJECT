from fastapi import  FastAPI,Request,HTTPException,status,Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas import PostCreate,PostResponse,UserResponse,UserCreate,PostUpdate,UserUpdate
from  typing import Annotated

from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from database import Base,engine,get_db


Base.metadata.create_all(bind=engine)
app = FastAPI()

app.mount("/static",StaticFiles(directory="static"),name="static")
app.mount("/media",StaticFiles(directory="media"),name="media")

templates = Jinja2Templates(directory="templates")



@app.get("/",include_in_schema=False,name="home")
@app.get("/home/",include_in_schema=False,name="home")
def home(request:Request,db:Annotated[Session,Depends(get_db)]):#modified home page with db
    result_all_posts = db.execute(select(models.Post))#get the all posts
    all_posts = result_all_posts.scalars().all()

    all_posts_dict = {"posts":all_posts,"title":"Home"}
    return templates.TemplateResponse(request,"home.html",context=all_posts_dict)


@app.get("/posts/{post_id}",include_in_schema=False,name="post")
def get_unique_post(request:Request,post_id:int,db:Annotated[Session,Depends(get_db)]):#get the unqiue post for users
    result_unique_post = db.execute(select(models.Post).where(models.Post.id==post_id))#check the post
    unique_post = result_unique_post.scalars().first()

    if unique_post:#if unique_post is have
        title = unique_post.title[:50]

        return templates.TemplateResponse(request,"post.html",context={"post":unique_post,"title":title})

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)#if not have

#With DB
@app.post("/api/user/",response_model=UserResponse,status_code=status.HTTP_201_CREATED) #created new users
def create_user(user:UserCreate,db:Annotated[Session,Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.username == user.username))

    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Kullanıcı adı mevcut")

    result_email = db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = result_email.scalars().first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email sistemde mevcut")

    new_user = models.User(
        username=user.username,
        email =user.email
    )
    db.add(new_user)# add to db
    db.commit() # saved to db
    db.refresh(new_user)#refresh the db

    return new_user

@app.get("/api/users/{user_id}",response_model=UserResponse) #get the user with user_id
def get_user(user_id:int,db:Annotated[Session,Depends(get_db)]):
    result_user = db.execute(select(models.User).where(models.User.id == user_id))#check the user
    existing_user = result_user.scalars().first()

    if existing_user: # if it exist return
        return existing_user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Böyle bir kullanıcı yoktur") #if not throw exception

@app.get("/api/users/{user_id}/posts",response_model=list[PostResponse])#get all posts from each user
def get_user_posts(user_id:int,db:Annotated[Session,Depends(get_db)]):
    result_user = db.execute(select(models.User).where(models.User.id == user_id))#check the user
    existing_user = result_user.scalars().first()
    if not existing_user:# if it not in the db throw exception
        raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Böyle bir kullanıcı yok")

    result_post = db.execute(select(models.Post).where(models.Post.user_id == user_id))#check the post
    existing_posts = result_post.scalars().all()
    return existing_posts #return all posts

@app.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int,user_update: UserUpdate,db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id)) #get the user_id
    user = result.scalars().first()
    if not user: #if no user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı yok",
        )

    if user_update.username is not None and user_update.username != user.username: # if username not empty and username not equal to past username
        result = db.execute(
            select(models.User).where(models.User.username == user_update.username),
        )
        existing_user = result.scalars().first()
        if existing_user: # If there is a user
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="bu kullanıcı var",
            )

    if user_update.email is not None and user_update.email != user.email:# if email not empty and email not equal to past email
        result = db.execute(
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

    db.commit()
    db.refresh(user)
    return user

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))#take the user_id
    user = result.scalars().first()
    if not user:# if user not in the db
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user) # if user in the db delete user and post
    db.commit()


@app.get("/api/post/",response_model=list[PostResponse])
def get_post(db:Annotated[Session,Depends(get_db)]): #get all posts
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts

@app.get("/api/post/{post_id}",response_model=PostResponse)
def get_posts(post_id : int,db:Annotated[Session,Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id==post_id))# specific post id
    post = result.scalars().first()

    if post:#if it have
        return post

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="404 ERROR")

@app.put("/api/post/{post_id}",response_model=PostResponse)
def update_post_all(post_id :int,post_data:PostCreate,db:Annotated[Session,Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id==post_id))# specific post id
    post = result.scalars().first()

    if not post: #if post not in the db
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="404 ERROR")

    if post.user_id != post_data.user_id:# we are checking post_data.user_id is in our db
        result = db.execute(select(models.User).where(models.User.id == post_data.user_id))
        user = result.scalars().first()
        if not user:#If post_data.user_id does not exist in our database, we cannot update the user_id.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Böyle bir kullanıcı yok")

    post.title = post_data.title #post.title = post_data.title
    post.content = post_data.content#post.content = post_data.content
    post.user_id = post_data.user_id #post.user_id = post_data.user_id

    db.commit()
    db.refresh(post)
    return post

@app.patch("/api/post/{post_id}",response_model=PostResponse)
def update_post_patch(post_id :int, post_data:PostUpdate ,db:Annotated[Session,Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id==post_id))# specific post id
    post = result.scalars().first()

    if not post:# if post is not in db
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="404 ERROR")

    update_data = post_data.model_dump(exclude_unset=True) # if I want to perform an update when only a single value changes.
    for field,value in update_data.items():
        setattr(post,field,value)

    db.commit()
    db.refresh(post)
    return post

@app.delete("/api/post/{post_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id:int , db:Annotated[Session,Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))#take the post_id in db
    post = result.scalars().first()

    if not post:#if post is not in db
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Böyle bir Post yok")

    db.delete(post)
    db.commit()

@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


@app.post("/api/post/",response_model=PostResponse,status_code=status.HTTP_201_CREATED)
def created_post(post:PostCreate,db:Annotated[Session,Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Böyle bir kullanıcı yoktur")

    new_post = models.Post(
        title = post.title,
        content = post.content,
        user_id = post.user_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )