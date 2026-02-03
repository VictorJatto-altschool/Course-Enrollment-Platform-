from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import cast
from app.database import get_db
from app.models.enrollment import Enrollment
from app.models.enrollment_audit import EnrollmentAudit
from app.models.course import Course
from app.models.user import User
from app.auth.dependencies import require_role, get_current_user
from app.services.enrollment_audit_service import log_enrollment_action
from app.schemas.common import MessageOut

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.post("/{course_id}", dependencies=[Depends(require_role(["student"]))], status_code=status.HTTP_201_CREATED)
def enroll_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
)-> MessageOut:
    course = (
        db.query(Course)
        .filter(
            Course.id == course_id,
            Course.is_active.is_(True),
            Course.is_deleted == False,
        )
        .first()
    )
    if course is None:
        raise HTTPException(404, detail="Course not found or inactive")

    current_user_id = cast(int, current_user.id)

    existing = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == current_user_id,
            Enrollment.course_id == course_id,
            Enrollment.is_deleted == False,
        )
        .first()
    )
    if existing:
        raise HTTPException(400, detail="Already enrolled")

    enrolled_count = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == course_id,
            Enrollment.is_deleted == False,
        )
        .count()
    )
    capacity = cast(int, course.capacity)
    if enrolled_count >= capacity:
        raise HTTPException(400, detail="Course is full")

    enrollment = Enrollment()
    enrollment.user_id = current_user_id
    enrollment.course_id = course_id
    db.add(enrollment)
    log_enrollment_action(
        db,
        action="enrolled",
        actor_user_id=current_user_id,
        user_id=current_user_id,
        course_id=course_id,
        enrollment_id=None,
    )
    db.commit()
    db.refresh(enrollment)
    # Update audit row to include enrollment_id if desired (optional)
    audit = db.query(EnrollmentAudit).order_by(EnrollmentAudit.id.desc()).first()
    if audit is not None and audit.enrollment_id is None:
        audit.enrollment_id = cast(int, enrollment.id)
        db.commit()
    return MessageOut(message="Enrolled successfully")





@router.delete("/{course_id}", dependencies=[Depends(require_role(["student"]))])
def deregister_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    enrollment = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.user_id == cast(int, current_user.id),
        Enrollment.is_deleted == False,
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    enrollment.soft_delete()
    log_enrollment_action(
        db,
        action="deregistered",
        actor_user_id=cast(int, current_user.id),
        user_id=cast(int, current_user.id),
        course_id=course_id,
        enrollment_id=cast(int, enrollment.id),
    )
    db.commit()
    return MessageOut(message="Successfully deregistered from course")
