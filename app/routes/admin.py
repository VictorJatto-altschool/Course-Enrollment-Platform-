from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.enrollment import Enrollment
from app.auth.dependencies import require_role
from app.services.enrollment_audit_service import log_enrollment_action
from app.schemas.common import MessageOut
from app.schemas.enrollment import EnrollmentAdminOut

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_role(["admin"]))]
)

# 1️⃣ View ALL enrollments
@router.get("/enrollments", response_model=List[EnrollmentAdminOut])
def view_all_enrollments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[int] = None,
    course_id: Optional[int] = None,
    include_deleted: bool = False,
):
    limit = max(1, min(limit, 200))
    q = db.query(Enrollment)
    if include_deleted is False:
        q = q.filter(Enrollment.is_deleted == False)
    if user_id is not None:
        q = q.filter(Enrollment.user_id == user_id)
    if course_id is not None:
        q = q.filter(Enrollment.course_id == course_id)

    return q.offset(skip).limit(limit).all()

# 2️⃣ View enrollments for a specific course
@router.get("/courses/{course_id}/enrollments", response_model=List[EnrollmentAdminOut])
def view_course_enrollments(course_id: int, db: Session = Depends(get_db)):
    enrollments = (
        db.query(Enrollment)
        .filter(Enrollment.course_id == course_id, Enrollment.is_deleted == False)
        .all()
    )
    if not enrollments:
        raise HTTPException(status_code=404, detail="No enrollments found for this course")
    return enrollments

# 3️⃣ Remove a student from a course
@router.delete("/enrollments/{enrollment_id}", response_model=MessageOut)
def remove_student(enrollment_id: int, db: Session = Depends(get_db)):
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.id == enrollment_id, Enrollment.is_deleted == False)
        .first()
    )
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    enrollment.soft_delete()
    log_enrollment_action(
        db,
        action="removed_by_admin",
        actor_user_id=None,
        user_id=int(enrollment.user_id),
        course_id=int(enrollment.course_id),
        enrollment_id=int(enrollment.id),
    )
    db.commit()
    return MessageOut(message="Student removed from course")
