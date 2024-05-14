import asyncio
from fastapi import (
    Depends,
    Request,
    APIRouter,
    status,
)
from exceptions import BadRequestException, NotFoundException
from database.schema import Users
from repository import AcademicSessionRepository
from repository.user import UsersRepository

from authentication.auth import auth

from beanie import PydanticObjectId

from validation import CreateStudent, UpdateStudent
from client.response import CustomResponse
from repository.student import StudentRepository
from typing import Optional

router = APIRouter(tags=["Student"], prefix="/student")


@router.get("/")
async def get_all_students(
    request: Request,
    page: int,
    per_page: int,
    level: Optional[int] = None,
    user: Users = Depends(auth.get_current_user),
):

    offset = (page - 1) * per_page

    total_students_task = (
        StudentRepository.get_total_student_count()
        if not level
        else StudentRepository.get_total_student_count_by_level(level)
    )

    tasks = [
        total_students_task,
        StudentRepository.get_all_students(offset, per_page, level),
    ]

    (
        total_students,
        all_students,
    ) = await asyncio.gather(*tasks)

    students = [student.to_dict() for student in all_students]

    context = {
        "students": students,
        "pagination": {
            "page_number": page,
            "per_pages": per_page,
            "total_pages": (total_students + per_page - 1) // per_page,
        },
    }

    return CustomResponse("get students successfully", data=context)


@router.get("/id/{student_id}")
async def get_student(
    request: Request,
    student_id: PydanticObjectId,
    user: Users = Depends(auth.get_current_user),
):
    student = await StudentRepository.get_student_by_id(student_id)

    if student is None:

        raise NotFoundException("student does not exist")

    context = {"student": student.to_dict()}

    return CustomResponse("get student successfully", data=context)


@router.get("/matric/{matric_no}")
async def get_student(
    request: Request,
    matric_no: int,
    user: Users = Depends(auth.get_current_user),
):

    student = await StudentRepository.get_student_by_matric_no(matric_no)

    if student is None:

        raise NotFoundException("student does not exist")

    context = {"student": student.to_dict()}

    return CustomResponse("get student successfully", data=context)


@router.post("/")
async def create_student(
    request: Request,
    student: CreateStudent,
    user: Users = Depends(auth.get_current_user),
):

    new_student = await StudentRepository.create_student(student)

    context = {"student": new_student.to_dict()}

    return CustomResponse("created student successfully", data=context)


@router.patch("/{student_id}")
async def update_student(
    request: Request,
    student_id: PydanticObjectId,
    update_student_param: UpdateStudent,
    user: Users = Depends(auth.get_current_user),
):
    
    print(update_student_param)

    student = await StudentRepository.get_student_by_id(student_id)

    if student is None:
        raise NotFoundException("student does not exist")
    

    if update_student_param.academic_session:
        academic_session = await AcademicSessionRepository.get_academic_session_by_id(update_student_param.academic_session)

        if not academic_session:
            raise BadRequestException("academic session does not exist")

        update_student_param.academic_session = academic_session

    student = await StudentRepository.update_student(student, update_student_param)

    context = {"student": student.to_dict()}

    return CustomResponse("updated student successfully", data=context)
