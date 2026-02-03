from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.enrollment_audit import EnrollmentAudit


def log_enrollment_action(
    db: Session,
    *,
    action: str,
    actor_user_id: int | None,
    user_id: int | None,
    course_id: int | None,
    enrollment_id: int | None,
) -> None:
    audit = EnrollmentAudit(
        action=action,
        actor_user_id=actor_user_id,
        user_id=user_id,
        course_id=course_id,
        enrollment_id=enrollment_id,
    )
    db.add(audit)
