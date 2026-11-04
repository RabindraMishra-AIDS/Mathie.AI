import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class ExerciseChunk:
    exercise_id: int
    chapter: str
    page_start: int
    page_end: int
    topics: tuple[str, ...]
    pattern_keywords: tuple[str, ...]
    difficulty: str
    context: str


LINEAR_EQUATIONS_CHAPTER = "Linear Equations in Two Variables"

_EXERCISES = (
    (
        1,
        11,
        14,
        ("linear equations in two variables", "elimination", "substitution"),
        ("solve", "equation", "simultaneous", "elimination", "substitution"),
        "foundational algebra",
    ),
    (
        2,
        15,
        19,
        ("graphs of linear equations", "ordered pairs", "graphical method"),
        ("graph", "plot", "ordered pair", "intersection", "graphically"),
        "foundational graphical method",
    ),
    (
        3,
        20,
        26,
        ("determinants", "Cramer's rule", "simultaneous equations"),
        ("determinant", "Cramer", "D", "Dx", "Dy"),
        "intermediate determinant method",
    ),
    (
        4,
        27,
        29,
        ("equations reducible to linear form", "substitution", "factorisation"),
        ("substitution", "transform", "factor", "linear form"),
        "intermediate transformation",
    ),
    (
        5,
        30,
        36,
        (
            "applications of simultaneous equations",
            "word problems",
            "mathematical modelling",
        ),
        ("word problem", "quantity", "cost", "number", "form equations"),
        "applied modelling",
    ),
)


class ExerciseVectorStore:
    """Metadata-filtered retrieval of only the registered PDF page range."""

    def __init__(self, pdf_path: str = "../data/source/Maths_Textbook.pdf") -> None:
        path = Path(pdf_path)
        if path.is_absolute():
            self.pdf_path = path
            return

        candidates = (
            Path.cwd() / path,
            Path(__file__).resolve().parents[2] / path,
            Path(__file__).resolve().parents[2] / path.as_posix().removeprefix("../"),
        )
        self.pdf_path = next(
            (candidate for candidate in candidates if candidate.is_file()),
            candidates[0],
        )

    def search(self, chapter: str, exercise_id: int) -> ExerciseChunk:
        for item in _EXERCISES:
            identifier, start, end, topics, pattern_keywords, difficulty = item
            if chapter == LINEAR_EQUATIONS_CHAPTER and exercise_id == identifier:
                return ExerciseChunk(
                    exercise_id=identifier,
                    chapter=chapter,
                    page_start=start,
                    page_end=end,
                    topics=topics,
                    pattern_keywords=pattern_keywords,
                    difficulty=difficulty,
                    context=self._extract_pages(start, end),
                )
        raise LookupError(
            f"No textbook context found for chapter {chapter!r}, "
            f"exercise {exercise_id}."
        )

    def _extract_pages(self, start: int, end: int) -> str:
        if not self.pdf_path.is_file():
            raise LookupError(f"Textbook PDF was not found at {self.pdf_path}.")
        reader = PdfReader(self.pdf_path)
        if end > len(reader.pages):
            raise LookupError("The requested textbook pages are unavailable.")
        context = "\n".join(
            reader.pages[page_number - 1].extract_text() or ""
            for page_number in range(start, end + 1)
        ).strip()
        context = re.split(
            r"\bPractice\s+Set\b", context, maxsplit=1, flags=re.IGNORECASE
        )[0].strip()
        if not context:
            raise LookupError("The requested textbook pages contain no readable text.")
        return context
