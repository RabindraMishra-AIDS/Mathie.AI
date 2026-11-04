# AI Learner project instructions

## Practice-question generation

- Keep textbook retrieval scoped to the requested `chapter` and `exercise_id`.
- Use textbook context to learn concepts and patterns, not to copy questions.
- Generated questions must be original variations with changed values or scenarios.
- Never include textbook Practice Set questions in the LLM context.
- Every generated question must pass all verifier layers before it is returned.
- Call the LLM only through `LLMClient`; tests must use a fake client.

## Changes and validation

- Preserve the existing FastAPI and React behavior unless the specification requires
  a change.
- Python code uses type hints, Ruff, and mypy; TypeScript uses strict mode and ESLint.
- Add a regression test for every generation or exercise-scoping bug.
- Do not commit API keys, textbook content without permission, or generated secrets.
