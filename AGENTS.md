# Project rules

- Build milestones in specification order and test each milestone before starting
  the next.
- Do not add endpoints, tables, or product features not listed in the
  specification.
- The LLM may only be called through `LLMClient`; tests must use a fake client.
- Every generated question must pass all verifier layers before it is saved or
  returned.
- Context queries must filter by `exercise_id`; add a regression test proving
  that other exercises do not enter a context pack.
- Python uses type hints, Ruff, and mypy. TypeScript uses strict mode and ESLint.
- Never commit API keys, textbook content without permission, or generated
  secrets.
