# Local Deployment Guide

## Recommended workflow

This repository now provides a unified cross-platform runner.

### Setup

```bash
python run.py setup
```

### Start

```bash
python run.py start
```

### Stop

```bash
python run.py stop
```

### Status

```bash
python run.py status
```

## Optional flags

```bash
python run.py start --open-browser
python run.py start --preview
python run.py start --demo
```

## Legacy helper scripts

If you still want platform-specific entry points, the repository also keeps:

- Windows: `*.cmd` and `*.ps1`
- macOS / Linux: `*.sh`

They are optional. The recommended path is `python run.py ...`.

## Demo mode

Set the following value in `backend/.env`:

```env
DEMO_MODE=true
```

Demo mode skips the real DeepSeek call and returns a built-in sample result. It is useful for open-source readers, UI walkthroughs, and conference demos.

## Default addresses

- Frontend: `http://127.0.0.1:5173`
- Backend API: `http://127.0.0.1:8000`
- Backend docs: `http://127.0.0.1:8000/docs`
