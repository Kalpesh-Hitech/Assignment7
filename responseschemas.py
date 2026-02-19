from typing import Optional

from pydantic import BaseModel

from models import RoleBased


class Adminresponse(BaseModel):
    id:int
    username:str
    email:Optional[str]=None
    role:RoleBased

class Login(BaseModel):
    token:str

class StudentResponse(BaseModel):
    id:int
    name:str
    grade:str
    created_by:int