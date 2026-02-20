from typing import List

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from auth import create_access_token, get_current_user, hash_password, verify_password
from models import Student, User
from database import async_get_db, get_db
from responseschemas import Adminresponse, Login, StudentResponse
from requestschemas import LoginCrete, UpdateStudent, UserCreate
from sqlalchemy.ext.asyncio import AsyncSession

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
            username=adminseed.username, email=adminseed.email, role="student"
        )
        hashed_passedword = hash_password(adminseed.password)

        db_user.password = hashed_passedword
        db.add(db_user)
        db.flush()
        new_student = Student(
            name=adminseed.name,
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
                name=adminseed.name,
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
        "name": adminseed.name,
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


from sqlalchemy.orm import joinedload


@router.get("/all_students", response_model=List[StudentResponse]|dict)
async def student_by_id(
    teacher:str|None=None,
    teacher_id:int|None=None,
    admins:str|None=None,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(async_get_db)
):
    query=None
    if user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if teacher=="teacher" and user.role=="admin":
        query = select(User).where(User.role=="teacher")
        result = await db.execute(query)
        rows = result.scalars().all()
        if not rows:
            raise HTTPException(status_code=404, detail="No teachers found!")
        response = []
        for user_obj in rows:
            response.append(
                {
                    "id": user_obj.id,
                    "username": user_obj.username,
                    "email": user_obj.email,
                    "name":None,
                    "grade":None,
                    "created_by":None,
                    "user_id":None
                }
            )
        return response
    if teacher_id and user.role=="admin":
        query = select(Student,User).join(User,Student.student_user_id == User.id).where(Student.created_by == teacher_id)
        result = await db.execute(query)
        rows = result.all()
        if not rows:
            raise HTTPException(status_code=404, detail="No teachers found!")
        response = []
        for student_obj, user_obj in rows:
            response.append(
                {
                    "id": student_obj.id,
                    "user_id": student_obj.student_user_id,
                    "username": user_obj.username,
                    "email": user_obj.email,
                    "name": student_obj.name,
                    "grade": student_obj.grade,
                    "created_by": student_obj.created_by,
                }
            )

        return response
    if admins=="admin" and user.role=="admin":
        query = select(User).where(User.role=="admin")
        result = await db.execute(query)
        rows = result.scalars().all()
        if not rows:
            raise HTTPException(status_code=404, detail="No teachers found!")
        response = []
        for user_obj in rows:
            response.append(
                {
                    "id": user_obj.id,
                    "username": user_obj.username,
                    "email": user_obj.email,
                    "name":None,
                    "grade":None,
                    "created_by":None,
                    "user_id":None
                }
            )

        return response
    query = select(Student, User).join(User, Student.student_user_id == User.id)

    if user.role == "teacher":
        query = query.where(Student.created_by == user.id)

    result = await db.execute(query)
    rows = result.all()

    if not rows:
        raise HTTPException(status_code=404, detail="No students found!")

    response = []
    for student_obj, user_obj in rows:
        response.append(
            {
                "id": student_obj.id,
                "user_id": student_obj.student_user_id,
                "username": user_obj.username,
                "email": user_obj.email,
                "name": student_obj.name,
                "grade": student_obj.grade,
                "created_by": student_obj.created_by,
            }
        )

    return response


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
async def delete_student(
    student_user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="unauthorize access")
    query = select(User).where(User.id == student_user_id, User.role == "student")
    result_user = await db.execute(query)
    student_user = result_user.scalars().first()
    if not student_user:
        raise HTTPException(status_code=404, detail="student nhi h to kya delete kru")

    await db.delete(student_user)
    await db.commit()

    return {"message": "bhaga diya bhai"}
@router.get("/myprofile", response_model=StudentResponse)
async def get_my_profile(
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(async_get_db)
):
    if user.role == "student":
        query = select(Student, User).join(User, Student.student_user_id == User.id).where(User.id == user.id)
        result = await db.execute(query)
        row = result.first()

        if not row:
            raise HTTPException(status_code=404, detail="Student profile not found")

        student_obj, user_obj = row
        return {
            "id": student_obj.id,
            "user_id": student_obj.student_user_id,
            "username": user_obj.username,
            "email": user_obj.email,
            "name": student_obj.name,
            "grade": student_obj.grade,
            "created_by": student_obj.created_by,
        }

    return {
        "id": user.id,
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "name": "Staff Member",
        "grade": None,
        "created_by": None,
    }

@router.post("/bulk_create_students")
async def bulk_create_students(
    students_data: List[UserCreate],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db)
):
    if user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=401, detail="Sirf Admin/Teacher bulk insert kar sakte hain")
    
    try:
        for data in students_data:
            new_user = User(
                username=data.username,
                email=data.email,
                password=hash_password(data.password),
                role="student"
            )
            db.add(new_user)
            await db.flush()
            if user.role=="admin":
                new_student = Student(
                    name=data.name,
                    grade=data.grade,
                    created_by=data.teacher_id,
                    student_user_id=new_user.id
                )
            else:
                new_student = Student(
                    name=data.name,
                    grade=data.grade,
                    created_by=user.id,
                    student_user_id=new_user.id
                )
            db.add(new_student)
        
        await db.commit()
        return {"message": f"Successfully created {len(students_data)} students!"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Bulk creation fail ho gaya: {str(e)}")