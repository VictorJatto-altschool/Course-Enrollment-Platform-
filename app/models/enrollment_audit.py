from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EnrollmentAudit(Base):
    __tablename__ = "enrollment_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # actor_user_id is who performed the action (student/admin)
    actor_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )

    # subject user/course for the enrollment action
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    course_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("courses.id"), nullable=True, index=True)
    enrollment_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("enrollments.id"), nullable=True, index=True
    )

    action: Mapped[str] = mapped_column(String, nullable=False)  # enrolled | deregistered | removed_by_admin
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
