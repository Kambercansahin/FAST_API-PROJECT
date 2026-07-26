from fastapi import  FastAPI,Request,HTTPException,status,Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas import PostCreate,PostResponse,UserResponse,UserCreate
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