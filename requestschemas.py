from typing import Optional

from pydantic import BaseModel

from models import RoleBased


class UserCreate(BaseModel):
    username:str
    email:str
    password:str
    role:RoleBased
    teacher_id:Optional[int]=None
    grade:Optional[str]=None
    created_by:Optional[int]=None

class LoginCrete(BaseModel):
    email:str
    password:str

class UpdateStudent(BaseModel):
    grade:str