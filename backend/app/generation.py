from random import SystemRandom

from app.llm import LLMClient
from app.models import GenerateResponse, PracticeProblem
from app.retrieval import ExerciseChunk, ExerciseVectorStore

DISCLAIMER = "AI can make mistakes. Please verify answers with your professor."
DATABASE_NOTE = (
    "PostgreSQL 16 is the application database. Textbook retrieval currently reads "
    "the source PDF with an exercise_id page-range filter; pgvector can later store "
    "embeddings without changing this contract."
)


class PracticeGenerator:
    def __init__(self, store: ExerciseVectorStore, llm_client: LLMClient) -> None:
        self.store = store
        self.llm_client = llm_client
        self.random = SystemRandom()

    def generate(self, chapter: str, exercise: int, count: int) -> GenerateResponse:
        chunk = self.store.search(chapter, exercise)
        verification_error: ValueError | None = None
        for _ in range(2):
            candidates = self.llm_client.generate(chunk, count)
            self.random.shuffle(candidates)
            problems = [
                PracticeProblem(
                    question=question,
                    solution=solution,
                    explanation=explanation,
                )
                for question, solution, explanation in candidates
            ]
            try:
                self._verify(chunk, problems, count)
            except ValueError as error:
                verification_error = error
                continue
            return GenerateResponse(
                chapter=chunk.chapter,
                exercise=chunk.exercise_id,
                pages=f"{chunk.page_start}-{chunk.page_end}",
                topics=list(chunk.topics),
                problems=problems,
                disclaimer=DISCLAIMER,
                database_note=DATABASE_NOTE,
            )
        if verification_error is not None:
            raise verification_error
        raise RuntimeError("The practice generator did not produce a response.")

    @staticmethod
    def _verify(
        chunk: ExerciseChunk, problems: list[PracticeProblem], expected_count: int
    ) -> None:
        if len(problems) != expected_count:
            raise ValueError(
                f"Exercise {chunk.exercise_id} produced an incomplete practice set."
            )
        if not problems:
            raise ValueError(
                f"Exercise {chunk.exercise_id} produced no verified problems."
            )
        questions: set[str] = set()
        for problem in problems:
            if not all(
                value.strip()
                for value in (problem.question, problem.solution, problem.explanation)
            ):
                raise ValueError("A generated problem failed the content verifier.")
            normalized_question = " ".join(problem.question.lower().split())
            if normalized_question in questions:
                raise ValueError("A generated problem failed the uniqueness verifier.")
            searchable_problem = " ".join(
                value.lower()
                for value in (
                    problem.question,
                    problem.solution,
                    problem.explanation,
                )
            )
            if not any(
                keyword.lower() in searchable_problem
                for keyword in chunk.pattern_keywords
            ):
                raise ValueError(
                    "A generated problem does not match the selected exercise pattern."
                )
            questions.add(normalized_question)
