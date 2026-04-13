# Contributing

Thanks for your interest in improving this project.

## Development environment

- Python 3.11+
- Node.js 20+
- npm 10+

## Local setup

Backend:

```bash
cd backend
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Then install dependencies and create local env variables:

```bash
pip install -r requirements.txt
copy .env.example .env
```

Frontend:

```bash
cd frontend
npm install
```

You can also use the repository-level setup scripts described in [README.md](README.md).

## Pull request guidelines

- Keep each pull request focused on one topic
- Avoid mixing feature work, refactors, and unrelated formatting changes in one PR
- Test the backend and frontend before opening a PR
- Update docs when the behavior, setup flow, or environment variables change
- Add screenshots when the PR changes the UI

## Commit guidelines

Clear commit messages are strongly recommended. Examples:

- `feat: add demo mode for local preview`
- `fix: handle invalid llm json response`
- `docs: update setup instructions`

## Security and secrets

- Never commit a real `.env`
- Never commit a real API key
- Never commit logs, local runtime caches, or local dependency directories
- If you suspect a secret leak, rotate it immediately and report it according to [SECURITY.md](SECURITY.md)

## Large files

- Do not commit unnecessary binary files
- Keep example files lightweight when possible
