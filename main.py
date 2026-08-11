from fastapi import  FastAPI,Request,HTTPException,status,Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


from  typing import Annotated

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sqlalchemy import select,text
import models
from database import Base,engine,get_db

from routers import user,post

@asynccontextmanager
async def lifespan(_app:FastAPI):
    yield
    #shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.mount("/static",StaticFiles(directory="static"),name="static")
app.mount("/media",StaticFiles(directory="media"),name="media")

templates = Jinja2Templates(directory="templates")

app.include_router(router=user.router,prefix="/api/users",tags=["users"])
app.include_router(router=post.router,prefix="/api/posts",tags=["posts"])

#create middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Frame-Options"] = "SAMEORIGIN" #follow this rule regarding the use of this page within iframes on other sites.

    response.headers["X-Content-Type-Options"] = "nosniff" #don't try to guess the type of content I sent.

    #decide which referrer information to share when visiting other sites based on this rule.
    if "Referrer-Policy" not in response.headers:
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    #don't add HSTS if I am working on my local computer.
    if request.url.hostname not in ("localhost", "127.0.0.1"):
        #use HTTPS when communicating with this site
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains"
        )

    return response


@app.get("/health")
async def health_check(db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return {"status": "healthy"}



@app.get("/",include_in_schema=False,name="home")
@app.get("/home/",include_in_schema=False,name="home")
async  def home(request:Request,db:Annotated[AsyncSession,Depends(get_db)]):#modified home page with db
    result_all_posts = await db.execute(select(models.Post)
                                        .options(selectinload(models.Post.author))
                                        .order_by(models.Post.date_posted.desc()),
                                        )#get the all posts
    all_posts = result_all_posts.scalars().all()

    all_posts_dict = {"posts":all_posts,"title":"Home"}
    return templates.TemplateResponse(request,"home.html",context=all_posts_dict)


@app.get("/posts/{post_id}",include_in_schema=False,name="post")
async def get_unique_post(request:Request,post_id:int,db:Annotated[AsyncSession,Depends(get_db)]):#get the unqiue post for users
    result_unique_post = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id==post_id)
    )#check the post
    unique_post = result_unique_post.scalars().first()

    if unique_post:#if unique_post is have
        title = unique_post.title[:50]

        return templates.TemplateResponse(request,"post.html",context={"post":unique_post,"title":title})

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)#if not have

@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_posts_page(request: Request,user_id: int,db: Annotated[AsyncSession, Depends(get_db)],):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc()),
    )
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )
@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Login"},
    )


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"title": "Register"},
    )

@app.get("/account", include_in_schema=False,name="account_page")
async def account_page(request: Request):
    return templates.TemplateResponse(
        request,
        "account.html",
        {"title": "Account"},
    )


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
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
async def validation_exception_handler(request: Request, exception: RequestValidationError):
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