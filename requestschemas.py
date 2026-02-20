from typing import Optional

from pydantic import BaseModel

from models import RoleBased


class UserCreate(BaseModel):
    username:str
    name:Optional[str]=None
    email:str
    password:str
    role:Optional[RoleBased]=RoleBased.STUDENT
    teacher_id:Optional[int]=None
    grade:Optional[str]=None
    created_by:Optional[int]=None

class LoginCrete(BaseModel):
    email:str
    password:str

class UpdateStudent(BaseModel):
    grade:str