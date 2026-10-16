from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class AdminDashboardResponse(BaseModel):
    message: str


class InstructorDashboardResponse(BaseModel):
    message: str
    email: str


class StudentDashboardResponse(BaseModel):
    enrolled_courses: int
    completed_courses: int
    certificates_count: int
    overall_progress: float
