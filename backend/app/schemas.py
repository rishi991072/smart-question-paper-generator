from pydantic import BaseModel, Field
from typing import Literal

class Login(BaseModel):
    username: str
    password: str

class Section(BaseModel):
    name: str
    question_type: Literal["mcq", "descriptive", "mixed"] = "mixed"
    count: int = Field(ge=1, le=100)
    marks_each: int = Field(ge=1, le=100)

class Topic(BaseModel):
    name: str
    percentage: float = Field(ge=0, le=100)

class GenerateRequest(BaseModel):
    document_id: str
    organization: str
    exam_name: str
    course: str = ""
    branch: str = ""
    semester: str = ""
    subject: str
    exam_date: str = ""
    duration_minutes: int = Field(ge=15, le=600)
    max_marks: int = Field(ge=1, le=1000)
    difficulty: Literal["easy_medium", "medium_hard", "hard_extreme", "custom"] = "medium_hard"
    custom_easy: int = 30
    custom_medium: int = 40
    custom_hard: int = 30
    language: Literal["English", "Hindi"] = "English"
    number_of_sets: int = Field(ge=1, le=4)
    sections: list[Section]
    topics: list[Topic] = []
    include_answer_key: bool = True
    instructions: str = "All questions are compulsory. Read each question carefully."
