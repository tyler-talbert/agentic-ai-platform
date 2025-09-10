# Contributing to Agentic AI Platform

Thanks for your interest in contributing! This guide covers local setup, running tests, and commit conventions to keep the repo healthy and consistent.

## Local Development

- Python: 3.11 recommended
- Create a virtualenv: `python -m venv .venv && . .venv/Scripts/Activate` (Windows PowerShell)
- Install dependencies:
  - `pip install -r requirements.txt` (root if used)
  - `pip install -r requirements-dev.txt`
  - `pip install -r agent_service/requirements.txt`
  - `pip install -r agent_orchestrator/requirements.txt`
- Optional: Docker is used by CI to run services. You can use `docker compose -f docker-compose.yml up -d` to bring up services for local testing.

## Running Tests

Run the test suites locally:

```
pytest -q agent_service/tests agent_orchestrator/tests tests
```

## Commit Message Conventions

Use conventional commits to improve readability and changelog automation:

- `feat:` a new feature
- `fix:` a bug fix
- `docs:` documentation-only changes
- `style:` formatting, whitespace (no code changes)
- `refactor:` code change that neither fixes a bug nor adds a feature
- `test:` adding or fixing tests
- `chore:` tooling, config, CI changes

Examples:

- `feat(agent): add streaming responses`
- `fix(orchestrator): handle empty payload in dispatcher`
- `chore(ci): cache pip and enable concurrency`

## Pull Requests

- Keep PRs focused and small where possible.
- Include context in the description: what, why, and how it was validated.
- Ensure CI is green and tests are passing.

## Code Style

- Follow PEP8 where applicable.
- Prefer explicit names and type hints where helpful.
- Keep logging actionable and avoid noisy logs at `info` level.

## Security & Secrets

- Never commit real secrets. Use `.env.example` for placeholders.
- Add secret keys as GitHub Actions secrets for CI usage.

## Questions

Open a discussion or issue if something is unclear. Contributions—large or small—are welcome!

