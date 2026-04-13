# Test Case Coverage Evaluation Agent

A full-stack AI agent for evaluating test case coverage against a PRD. The application reads a requirement document and an Excel test case file, extracts structured requirement points, maps them to test cases, calculates coverage scores by dimension, and generates missing test suggestions.

This repository is prepared for local deployment and open-source collaboration.

## What it does

- Supports PRD input in `txt`, `md`, and text-based `pdf`
- Supports test case input in `xlsx`
- Extracts structured requirement points:
  - functional points
  - business rules
  - boundary conditions
  - exception scenarios
  - non-functional requirements
- Maps test cases to requirement points
- Calculates a deterministic score from four fixed dimensions
- Returns structured JSON and a Markdown report
- Optionally generates missing test cases

## Tech stack

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + pandas + pypdf
- LLM: DeepSeek OpenAI-compatible API

## Repository structure

```text
backend/
  app/
    api/
    agent/
    llm/
    readers/
    services/
    utils/
  tests/
frontend/
  src/
docs/
examples/
```

## Requirements

- Python 3.11+
- Node.js 20+
- npm 10+
- Network access to DeepSeek API if you run in real LLM mode

## Quick start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. Install dependencies

Use the unified cross-platform setup command:

```bash
python run.py setup
```

This command:

- creates `backend/.venv`
- installs Python dependencies
- installs frontend dependencies
- copies `backend/.env.example` to `backend/.env` if needed

### 3. Configure environment variables

Edit `backend/.env` and fill in your own DeepSeek API key:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

If you only want to demo the UI or walkthrough the workflow without calling DeepSeek, enable demo mode:

```env
DEMO_MODE=true
```

### 4. Start the application

Use the unified cross-platform start command:

```bash
python run.py start
```

Helpful variants:

```bash
python run.py start --open-browser
python run.py start --preview
python run.py start --demo
```

### 5. Open the app

- Frontend UI: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- Backend API root: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Backend docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 6. Stop the application

```bash
python run.py stop
```

### 7. Check status

```bash
python run.py status
```

## Legacy helper scripts

The repository still includes `cmd`, `ps1`, and `sh` helper scripts for users who prefer them, but the recommended path is the unified `python run.py ...` workflow.

## Environment variables

See [backend/.env.example](backend/.env.example) for the full template.

Key variables:

```env
APP_NAME=Test Coverage Evaluation Agent
API_PREFIX=/api
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
LLM_TIMEOUT=120
LLM_MAX_RETRIES=2
LLM_REPAIR_RETRIES=1
COVERAGE_BATCH_SIZE=12
PROMPT_TEXT_PREVIEW_CHARS=240
DEMO_MODE=false
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

## Deployment modes

### Real LLM mode

- Requires a valid DeepSeek API key
- Calls the actual DeepSeek model
- Suitable for real analysis

### Demo mode

- No DeepSeek call is made
- Returns a built-in sample result
- Suitable for GitHub readers, screenshots, UI demos, and conference walkthroughs

## API overview

- `POST /api/analysis/jobs`
- `GET /api/analysis/jobs/{task_id}`
- `GET /api/analysis/jobs/{task_id}/report`
- `GET /api/analysis/health`

## Limitations

- Only text-based PDFs are supported
- OCR for scanned PDFs is not included
- Large PRDs and large test case sets can increase LLM latency
- The current task queue is in-memory and intended for local/demo usage rather than production concurrency

## Examples

- PRD sample: [sample_prd.md](examples/sample_prd.md)
- Test case sample: [sample_cases.xlsx](examples/sample_cases.xlsx)
- JSON result sample: [sample_result.json](examples/sample_result.json)
- Markdown report sample: [sample_report.md](examples/sample_report.md)
- Local deployment guide: [local_deployment.md](docs/local_deployment.md)

## Prompt files

The core internal prompts live in:

- [prompts.py](backend/app/agent/prompts.py)

The file includes:

- `REQUIREMENT_EXTRACTION_SYSTEM_PROMPT`
- `COVERAGE_ASSESSMENT_SYSTEM_PROMPT`

## Security notes

- Never commit a real `.env`
- Never commit a real API key
- If you suspect a key leak, rotate it immediately
- See [SECURITY.md](SECURITY.md) for reporting guidance

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request.

## License

This project is licensed under the [MIT License](LICENSE).
