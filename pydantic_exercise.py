from pydantic import BaseModel,ValidationError,Field,EmailStr,SecretStr,HttpUrl
from uuid import UUID,uuid4

from datetime import datetime,UTC
from typing import Literal,Annotated



class User(BaseModel):
    u_id:UUID = Field(default_factory=uuid4)
    user_name:str
    email:EmailStr

    password:SecretStr
    website:HttpUrl | None = None

    age:Annotated[int,Field(ge=0)]
    bio:str=""
    is_active:bool =True

    full_name:str|None = None




class BlogPost(BaseModel):
    title:str
    content:str
    view_count:int=0
    is_published: bool =False


    tags: list[str]=Field(default_factory=list)

    created_datetime: datetime=Field(default_factory=lambda:datetime.now(tz=UTC))

    auth_id : str | int

    status:Literal["draft","published","archived"]="draft" #default

user = User(
    user_name="coreyms",
    email="CoreyMSchafer@gmail.com",
    age=39,
    password="secret123",
)
print(user.model_dump_json(indent=2))