from pydantic import BaseModel, ConfigDict
from typing import Optional


class CourseCreate(BaseModel):
    title: str
    code: str
    capacity: int
    is_active: Optional[bool] = True


class CourseOut(BaseModel):
    id: int
    title: str
    code: str
    capacity: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None


class CourseStatusUpdate(BaseModel):
    is_active: bool
