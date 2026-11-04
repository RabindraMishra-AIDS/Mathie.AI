import json
from dataclasses import dataclass
from urllib import error, parse, request

from app.config import Settings
from app.retrieval import ExerciseChunk

_PRACTICE_RESPONSE_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "problems": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "solution": {"type": "string"},
                    "explanation": {"type": "string"},
                },
                "required": ["question", "solution", "explanation"],
            },
        }
    },
    "required": ["problems"],
}


class LLMProviderError(RuntimeError):
    """A safe, user-facing failure from the configured LLM provider."""

    def __init__(self, detail: str, status_code: int) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


class LLMClient:
    """The sole boundary through which this application calls an LLM."""

    def generate(
        self, context: ExerciseChunk, count: int
    ) -> list[tuple[str, str, str]]:
        raise NotImplementedError


@dataclass
class GeminiLLMClient(LLMClient):
    """Google AI Studio Gemini REST client constrained to retrieved text."""

    settings: Settings

    def generate(
        self, context: ExerciseChunk, count: int
    ) -> list[tuple[str, str, str]]:
        prompt = (
            "Use only the textbook context below. Generate exactly "
            f"{count} new practice problems matching its concepts, pattern, and "
            f"difficulty ({context.difficulty}). Every question must use at least "
            f"one of these exercise patterns: {', '.join(context.pattern_keywords)}. "
            "Include a correct worked solution and a short concept explanation for "
            "each. Do not use knowledge not supported by the context. Return JSON "
            'only: {"problems":[{"question":"...","solution":"...",'
            '"explanation":"..."}]}.\n\n'
            f"Chapter: {context.chapter}\nExercise: {context.exercise_id}\n"
            f"PDF pages: {context.page_start}-{context.page_end}\n"
            f"Retrieved textbook context:\n{context.context}"
        )
        parsed = self._request_json(prompt)
        problems = parsed.get("problems")
        if not isinstance(problems, list):
            raise RuntimeError("The configured LLM returned an invalid response.")
        output: list[tuple[str, str, str]] = []
        for item in problems[:count]:
            if not isinstance(item, dict):
                raise RuntimeError("The configured LLM returned an invalid response.")
            question, solution, explanation = (
                item.get("question"),
                item.get("solution"),
                item.get("explanation"),
            )
            if (
                not isinstance(question, str)
                or not isinstance(solution, str)
                or not isinstance(explanation, str)
            ):
                raise RuntimeError("The configured LLM returned an invalid response.")
            output.append((question, solution, explanation))
        return output

    def _request_json(self, prompt: str) -> dict[str, object]:
        response = self._request(prompt, "application/json")
        response = response.strip()
        if response.startswith("```") and response.endswith("```"):
            response = response.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
        try:
            parsed = json.loads(response)
        except json.JSONDecodeError as exc:
            raise LLMProviderError(
                "The configured LLM returned invalid JSON.", 502
            ) from exc
        if not isinstance(parsed, dict):
            raise LLMProviderError("The configured LLM returned invalid JSON.", 502)
        return parsed

    def _request(self, prompt: str, mime_type: str = "text/plain") -> str:
        if not self.settings.google_api_key:
            raise LLMProviderError(
                "LLM is not configured. Set GOOGLE_API_KEY in backend/.env.",
                503,
            )
        model = parse.quote(self.settings.google_model, safe="")
        api_key = parse.quote(self.settings.google_api_key, safe="")
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8192,
                "responseMimeType": mime_type,
                "responseJsonSchema": _PRACTICE_RESPONSE_SCHEMA,
            },
        }
        http_request = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=45) as http_response:
                body = json.load(http_response)
            text = body["candidates"][0]["content"]["parts"][0]["text"]
            if not isinstance(text, str):
                raise TypeError("Gemini response text is not a string.")
            return text
        except error.HTTPError as exc:
            detail = self._http_error_detail(exc)
            if exc.code == 429:
                detail = "Gemini quota is temporarily exhausted. Wait, then try again."
            raise LLMProviderError(
                detail,
                429 if exc.code == 429 else 502,
            ) from exc
        except (error.URLError, TimeoutError) as exc:
            raise LLMProviderError(
                "The configured Gemini provider could not be reached.", 503
            ) from exc
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(
                "The configured Gemini provider returned an invalid response.", 502
            ) from exc

    @staticmethod
    def _http_error_detail(exc: error.HTTPError) -> str:
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            payload = None
        if isinstance(payload, dict):
            error_body = payload.get("error")
            if isinstance(error_body, dict):
                message = error_body.get("message")
                if isinstance(message, str) and message.strip():
                    return f"Gemini request failed (HTTP {exc.code}): {message.strip()}"
        return f"The Gemini provider rejected the request (HTTP {exc.code})."
