from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.generation import PracticeGenerator
from app.llm import LLMClient, LLMProviderError
from app.main import app
from app.retrieval import ExerciseChunk, ExerciseVectorStore


class FailingLLMClient(LLMClient):
    def generate(
        self, context: ExerciseChunk, count: int
    ) -> list[tuple[str, str, str]]:
        raise LLMProviderError(
            "The configured Gemini provider could not be reached.", 503
        )


def test_health() -> None:
    response = TestClient(app).get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_practice_provider_failures_return_safe_upstream_status(
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.main.generator",
        PracticeGenerator(ExerciseVectorStore(), FailingLLMClient()),
    )
    client = TestClient(app)
    payload = {"chapter": "Linear Equations in Two Variables", "exercise": 1}

    generate_response = client.post("/api/v1/practice/generate", json=payload)
    assert generate_response.status_code == 503
    assert generate_response.json() == {
        "detail": "The configured Gemini provider could not be reached."
    }
