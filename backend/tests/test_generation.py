from email.message import Message
from typing import NoReturn

from pytest import MonkeyPatch

from app.config import Settings
from app.generation import PracticeGenerator
from app.llm import GeminiLLMClient, LLMClient, LLMProviderError
from app.retrieval import ExerciseChunk, ExerciseVectorStore


def test_default_google_model_is_available_generation_model() -> None:
    assert Settings().google_model == "gemini-flash-lite-latest"


class FakeLLMClient(LLMClient):
    def generate(
        self, context: ExerciseChunk, count: int
    ) -> list[tuple[str, str, str]]:
        assert context.exercise_id == 1
        return [
            (f"Solve equation {index}: x + y = {index + 2}", "Solution", "Explanation")
            for index in range(count)
        ]


def test_context_is_scoped_to_exercise() -> None:
    chunk = ExerciseVectorStore().search(
        "Linear Equations in Two Variables", exercise_id=2
    )

    assert chunk.exercise_id == 2
    assert chunk.page_start == 15
    assert chunk.page_end == 19
    assert "Practice Set 1.1" not in chunk.context
    assert "graph" in chunk.context.lower()


def test_generation_uses_fake_client_and_verifies_output() -> None:
    response = PracticeGenerator(ExerciseVectorStore(), FakeLLMClient()).generate(
        "Linear Equations in Two Variables", exercise=1, count=2
    )

    assert len(response.problems) == 2
    assert response.disclaimer.startswith("AI can make mistakes")
    assert not hasattr(response, "context")


def test_generation_rejects_a_problem_from_another_exercise_pattern() -> None:
    class MismatchedLLMClient(LLMClient):
        def generate(
            self, context: ExerciseChunk, count: int
        ) -> list[tuple[str, str, str]]:
            return [
                ("Evaluate the determinant | 1 2; 3 4 |", "Solution", "Explanation")
                for _ in range(count)
            ]

    try:
        PracticeGenerator(ExerciseVectorStore(), MismatchedLLMClient()).generate(
            "Linear Equations in Two Variables", exercise=1, count=1
        )
    except ValueError as error:
        assert "exercise pattern" in str(error)
    else:
        raise AssertionError("A mismatched exercise pattern should be rejected.")


def test_generation_retries_once_after_a_verification_failure() -> None:
    class RetryingLLMClient(LLMClient):
        calls = 0

        def generate(
            self, context: ExerciseChunk, count: int
        ) -> list[tuple[str, str, str]]:
            self.calls += 1
            if self.calls == 1:
                return [("Find the determinant", "Solution", "Explanation")]
            return [("Solve this simultaneous equation", "Solution", "Explanation")]

    client = RetryingLLMClient()
    response = PracticeGenerator(ExerciseVectorStore(), client).generate(
        "Linear Equations in Two Variables", exercise=1, count=1
    )

    assert client.calls == 2
    assert response.problems[0].question == "Solve this simultaneous equation"


def test_provider_requires_google_ai_studio_key() -> None:
    client = GeminiLLMClient(Settings(google_api_key=None))
    chunk = ExerciseVectorStore().search(
        "Linear Equations in Two Variables", exercise_id=1
    )

    try:
        client.generate(chunk, count=1)
    except RuntimeError as error:
        assert "GOOGLE_API_KEY" in str(error)
    else:
        raise AssertionError("An unconfigured provider should fail explicitly.")


def test_provider_http_failures_are_safe_and_actionable(
    monkeypatch: MonkeyPatch,
) -> None:
    def reject_request(*args: object, **kwargs: object) -> NoReturn:
        from urllib.error import HTTPError

        raise HTTPError(
            url="https://example.test",
            code=400,
            msg="bad request",
            hdrs=Message(),
            fp=None,
        )

    monkeypatch.setattr("app.llm.request.urlopen", reject_request)
    client = GeminiLLMClient(Settings(google_api_key="test-key"))
    chunk = ExerciseVectorStore().search(
        "Linear Equations in Two Variables", exercise_id=1
    )

    try:
        client.generate(chunk, count=1)
    except LLMProviderError as error:
        assert error.status_code == 502
        assert str(error) == "The Gemini provider rejected the request (HTTP 400)."
        assert "test-key" not in str(error)
    else:
        raise AssertionError("A provider HTTP failure should be classified.")


def test_provider_rate_limit_is_not_reported_as_a_gateway_failure(
    monkeypatch: MonkeyPatch,
) -> None:
    def reject_request(*args: object, **kwargs: object) -> NoReturn:
        from urllib.error import HTTPError

        raise HTTPError(
            url="https://example.test",
            code=429,
            msg="quota exceeded",
            hdrs=Message(),
            fp=None,
        )

    monkeypatch.setattr("app.llm.request.urlopen", reject_request)
    client = GeminiLLMClient(Settings(google_api_key="test-key"))
    chunk = ExerciseVectorStore().search(
        "Linear Equations in Two Variables", exercise_id=1
    )

    try:
        client.generate(chunk, count=1)
    except LLMProviderError as error:
        assert error.status_code == 429
        assert "quota" in str(error).lower()
    else:
        raise AssertionError("A quota failure should be classified.")


def test_provider_accepts_json_fenced_in_markdown(
    monkeypatch: MonkeyPatch,
) -> None:
    client = GeminiLLMClient(Settings(google_api_key="test-key"))
    monkeypatch.setattr(
        client,
        "_request",
        lambda prompt, mime_type="text/plain": (
            '```json\n{"problems":[{"question":"Solve x + y = 2",'
            '"solution":"x=1, y=1","explanation":"Use substitution."}]}\n```'
        ),
    )
    chunk = ExerciseVectorStore().search(
        "Linear Equations in Two Variables", exercise_id=1
    )

    assert client.generate(chunk, count=1) == [
        ("Solve x + y = 2", "x=1, y=1", "Use substitution.")
    ]
