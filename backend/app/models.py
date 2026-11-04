from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    chapter: str = Field(min_length=1)
    exercise: int = Field(ge=1)
    count: int = Field(default=5, ge=1, le=10)


class PracticeProblem(BaseModel):
    question: str
    solution: str
    explanation: str


class GenerateResponse(BaseModel):
    chapter: str
    exercise: int
    pages: str
    topics: list[str]
    problems: list[PracticeProblem]
    disclaimer: str
    database_note: str

