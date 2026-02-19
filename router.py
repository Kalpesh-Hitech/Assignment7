from typing import List

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from auth import create_access_token, get_current_user, hash_password, verify_password
from models import Student, User
from database import get_db
from responseschemas import Adminresponse, Login, StudentResponse
from requestschemas import LoginCrete, UpdateStudent, UserCreate


router = APIRouter()


@router.post("/create_user", response_model=Adminresponse)
def admin(
    adminseed: UserCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_user = None
    if user.role == "admin" and adminseed.role == "admin":
        db_user = User(
            username=adminseed.username, email=adminseed.email, role=adminseed.role
        )

        hashed_passedword = hash_password(adminseed.password)

        db_user.password = hashed_passedword
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    if adminseed.role == "admin":
        raise HTTPException(
            status_code=401, detail="you are not able to create the admin role!!"
        )
    if adminseed.role == "teacher":
        if user.role != "admin":
            raise HTTPException(
                status_code=401, detail="only admin can create the teacher!!"
            )
        db_user = User(
            username=adminseed.username, email=adminseed.email, role=adminseed.role
        )

        hashed_passedword = hash_password(adminseed.password)

        db_user.password = hashed_passedword
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    if adminseed.role == "student":
        if user.role != "admin" and user.role != "teacher":
            raise HTTPException(status_code=401, detail="please enter the valid role!!")
        if user.role == "teacher":
            teacher_count = (
                db.query(Student).filter(Student.created_by == user.id).count()
            )
            if teacher_count > 30:
                raise HTTPException(
                    status_code=402,
                    detail="aapke pass 30 student ho gaye hai abhi create nai kar sakate ho!!",
                )
            db_user = User(
                username=adminseed.username, email=adminseed.email, role=adminseed.role
            )
            hashed_passedword = hash_password(adminseed.password)

            db_user.password = hashed_passedword
            db.add(db_user)
            db.flush()
            new_student = Student(
                name=adminseed.username,
                grade=adminseed.grade,
                created_by=user.id,
                student_user_id=db_user.id,
            )
            # db_user.student.append(new_student)
            db.add(new_student)
            db.commit()
            db.refresh(db_user)
        if user.role == "admin":
            db_user = User(
                username=adminseed.username, email=adminseed.email, role=adminseed.role
            )

            hashed_passedword = hash_password(adminseed.password)

            db_user.password = hashed_passedword

            if adminseed.teacher_id != None:
                db_teacher = (
                    db.query(User).filter(User.id == adminseed.teacher_id).first()
                )
                if not db_teacher:
                    raise HTTPException(
                        status_code=404, detail="teacher ki id galat hai"
                    )
                if db_teacher.role != "teacher":
                    raise HTTPException(
                        status_code=404,
                        detail="admin bhai role dekho bad me sahi id dalo",
                    )
                db.add(db_user)
                db.flush()
                new_student = Student(
                    name=adminseed.username,
                    grade=adminseed.grade,
                    created_by=adminseed.teacher_id,
                    student_user_id=db_user.id,
                )
                # db_user.student.append(new_student)

            else:
                raise HTTPException(
                    status_code=404, detail="please provide the teacher id"
                )
            db.add(new_student)
            db.commit()
            db.refresh(db_user)
    return {
        "id": db_user.id,
        "username": adminseed.username,
        "email": adminseed.email,
        "role": adminseed.role,
    }


@router.post("/login", response_model=Login)
def login(user: LoginCrete, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid Credential")
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid Credential")
    access_token = create_access_token(data={"sub": db_user.email})

    return {"token": access_token}


@router.get("/all_students", response_model=List[StudentResponse])
def student_by_id(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user.role != "admin":
        raise HTTPException(
            status_code=401, detail="admin can access the all students!"
        )
    db_students = db.query(Student).all()

    if not db_students:
        raise HTTPException(status_code=404, detail="nai hai students!!")
    return db_students


@router.get("/get_my_student", response_model=List[StudentResponse])
def get_my_students(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user.role != "teacher":
        raise HTTPException(
            status_code=401, detail="teacher can access the their students!"
        )
    db_students = db.query(Student).filter(Student.created_by == user.id)
    if not db_students:
        raise HTTPException(status_code=404, detail="nai hai students!!")
    return db_students


@router.post("/create-admin")
def create_admin(db: Session = Depends(get_db)):
    db_admin = User(
        username="kalpesh",
        email="kalpesh1@gmail.com",
        password=hash_password("1234"),
        role="admin",
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return {"message": "Admin created!!"}


@router.patch("/update_student/{student_id}", response_model=StudentResponse)
def teacher_student_id(
    student_id: int,
    new_grade: UpdateStudent,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_student = (
        db.query(Student)
        .filter(Student.created_by == user.id and Student.id == student_id)
        .first()
    )
    if not db_student:
        raise HTTPException(status_code=404, detail="not found this student")
    db_student.grade = new_grade.grade
    db.commit()
    db.refresh(db_student)
    return db_student


@router.delete("/delete_student", response_model=dict)
def delete_student(
    student_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="unauthorize access")
    student_user = (
        db.query(User)
        .filter(User.id == student_user_id, User.role == "student")
        .first()
    )
    if not student_user:
        raise HTTPException(status_code=404, detail="student nhi h to kya delete kru")

    db.delete(student_user)
    db.commit()

    return {"message": "bhaga diya bhai"}
