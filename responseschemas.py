from typing import Optional

from pydantic import BaseModel

from models import RoleBased


class Adminresponse(BaseModel):
    id:int
    username:str
    name:Optional[str]
    email:Optional[str]=None
    role:RoleBased

class Login(BaseModel):
    token:str

class StudentResponse(BaseModel):
    id:int
    user_id:Optional[int]=None
    username:str
    email:str
    name:Optional[str]=None
    grade:Optional[str]=None
    created_by:Optional[int]=None