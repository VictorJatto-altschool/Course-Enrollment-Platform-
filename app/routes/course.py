from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseOut, CourseStatusUpdate, CourseUpdate
from app.auth.dependencies import require_role
from app.database import get_db
from app.schemas.common import MessageOut

router = APIRouter(prefix="/courses", tags=["Courses"])

# Public route
@router.get("", response_model=List[CourseOut])
def get_courses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    active: Optional[bool] = True,
    code: Optional[str] = None,
    title: Optional[str] = None,
):
    limit = max(1, min(limit, 100))

    q = db.query(Course).filter(Course.is_deleted == False)
    if active is not None:
        q = q.filter(Course.is_active == active)
    if code:
        q = q.filter(Course.code == code)
    if title:
        q = q.filter(Course.title.ilike(f"%{title}%"))

    return q.offset(skip).limit(limit).all()

# Admin-only: create course
@router.post("", dependencies=[Depends(require_role(["admin"]))], status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    existing = db.query(Course).filter(Course.code == course.code, Course.is_deleted == False).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course code must be unique")
    if course.capacity <= 0:
        raise HTTPException(status_code=400, detail="Capacity must be greater than zero")

    db_course = Course()
    db_course.title = course.title
    db_course.code = course.code
    db_course.capacity = course.capacity
    db_course.is_active = True if course.is_active is None else course.is_active
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


# Public: get a single active course by ID
@router.get("/{course_id}", response_model=CourseOut)
def get_course_by_id(course_id: int, db: Session = Depends(get_db)):
    course = (
        db.query(Course)
        .filter(
            Course.id == course_id,
            Course.is_deleted == False,
            Course.is_active.is_(True),
        )
        .first()
    )
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


# Admin-only: update course details (including activate/deactivate)
@router.patch("/{course_id}", dependencies=[Depends(require_role(["admin"]))], response_model=CourseOut)
def update_course(course_id: int, update: CourseUpdate, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id, Course.is_deleted == False).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if update.code is not None and update.code != course.code:
        existing = (
            db.query(Course)
            .filter(Course.code == update.code, Course.is_deleted == False, Course.id != course_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Course code must be unique")
        course.code = update.code

    if update.capacity is not None:
        if update.capacity <= 0:
            raise HTTPException(status_code=400, detail="Capacity must be greater than zero")
        course.capacity = update.capacity

    if update.title is not None:
        course.title = update.title

    if update.is_active is not None:
        course.is_active = update.is_active

    db.commit()
    db.refresh(course)
    return course


# Admin-only: explicit activate/deactivate endpoint
@router.patch(
    "/{course_id}/status",
    dependencies=[Depends(require_role(["admin"]))],
    response_model=CourseOut,
)
def set_course_status(course_id: int, payload: CourseStatusUpdate, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id, Course.is_deleted == False).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    course.is_active = payload.is_active
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", dependencies=[Depends(require_role(["admin"]))])
def soft_delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id, Course.is_deleted == False).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    course.soft_delete()
    db.commit()
    return MessageOut(message="Course deleted")
