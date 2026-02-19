import enum
from typing import List
from sqlalchemy import Enum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped,mapped_column,relationship
from database import Base

class RoleBased(str,enum.Enum):
    ADMIN="admin"
    TEACHER="teacher"
    STUDENT="student"

class User(Base):

    __tablename__="usernew"

    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    username:Mapped[str]=mapped_column(String(20))
    email:Mapped[str]=mapped_column(String(30),unique=True)
    password:Mapped[str]=mapped_column(String(200))
    role:Mapped[RoleBased]=mapped_column(Enum(RoleBased))

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="users",
        cascade="all, delete-orphan",
        uselist=False,
        foreign_keys="Student.student_user_id",
    )

class Student(Base):
    __tablename__="student"

    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    name:Mapped[str]=mapped_column(String(20))
    grade:Mapped[str]=mapped_column(String(2))
    created_by:Mapped[int]=mapped_column(ForeignKey("usernew.id",ondelete="CASCADE"))
    student_user_id: Mapped[int] = mapped_column(
        ForeignKey("usernew.id", ondelete="CASCADE"), unique=True
    )
    users: Mapped["User"] = relationship(
        "User", back_populates="student", foreign_keys=[student_user_id]
    )
 
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])