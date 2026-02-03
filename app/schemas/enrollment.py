from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EnrollmentOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnrollmentAdminOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    is_deleted: bool
    deleted_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
