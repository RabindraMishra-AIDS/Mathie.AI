from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.generation import PracticeGenerator
from app.llm import GeminiLLMClient, LLMProviderError
from app.models import (
    GenerateRequest,
    GenerateResponse,
)
from app.retrieval import ExerciseVectorStore

settings = get_settings()
app = FastAPI(
    title="Exercise-Scoped Math Practice Generator",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
generator = PracticeGenerator(
    ExerciseVectorStore(settings.textbook_pdf_path), GeminiLLMClient(settings)
)


@app.get("/api/v1/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/api/v1/practice/generate",
    response_model=GenerateResponse,
    tags=["practice"],
)
async def generate_practice(request: GenerateRequest) -> GenerateResponse:
    try:
        return generator.generate(request.chapter, request.exercise, request.count)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except LLMProviderError as error:
        raise HTTPException(
            status_code=error.status_code, detail=error.detail
        ) from error
    except (RuntimeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

