from __future__ import annotations

import argparse
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
LOGS_DIR = ROOT / "logs"

BACKEND_PID_FILE = LOGS_DIR / "backend.pid"
FRONTEND_PID_FILE = LOGS_DIR / "frontend.pid"
BACKEND_OUT_LOG = LOGS_DIR / "backend.out.log"
BACKEND_ERR_LOG = LOGS_DIR / "backend.err.log"
FRONTEND_OUT_LOG = LOGS_DIR / "frontend.out.log"
FRONTEND_ERR_LOG = LOGS_DIR / "frontend.err.log"

BACKEND_ENV = BACKEND_DIR / ".env"
BACKEND_ENV_EXAMPLE = BACKEND_DIR / ".env.example"
BACKEND_REQUIREMENTS = BACKEND_DIR / "requirements.txt"
FRONTEND_PACKAGE_JSON = FRONTEND_DIR / "package.json"
FRONTEND_NODE_MODULES = FRONTEND_DIR / "node_modules"

IS_WINDOWS = os.name == "nt"
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_HOST = "127.0.0.1"
FRONTEND_PORT = 5173


def info(message: str) -> None:
    print(message)


def fail(message: str, exit_code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(exit_code)


def ensure_logs_dir() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def backend_python_path() -> Path:
    candidates = [
        BACKEND_DIR / (".venv/Scripts/python.exe" if IS_WINDOWS else ".venv/bin/python"),
        ROOT / ("backend_dependency/venv/Scripts/python.exe" if IS_WINDOWS else "backend_dependency/venv/bin/python"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    fail("Backend virtual environment not found. Run `python run.py setup` first.")


def npm_command() -> str:
    return "npm.cmd" if IS_WINDOWS else "npm"


def create_backend_venv() -> None:
    venv_dir = BACKEND_DIR / ".venv"
    if venv_dir.exists():
        return
    info("Creating backend virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], cwd=BACKEND_DIR, check=True)


def setup_backend() -> None:
    if not BACKEND_REQUIREMENTS.exists():
        fail("backend/requirements.txt not found.")

    create_backend_venv()
    python_exe = backend_python_path()

    info("Installing backend dependencies...")
    subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], cwd=BACKEND_DIR, check=True)
    subprocess.run([str(python_exe), "-m", "pip", "install", "-r", str(BACKEND_REQUIREMENTS)], cwd=BACKEND_DIR, check=True)

    if not BACKEND_ENV.exists() and BACKEND_ENV_EXAMPLE.exists():
        shutil.copyfile(BACKEND_ENV_EXAMPLE, BACKEND_ENV)
        info("Created backend/.env from backend/.env.example")


def setup_frontend() -> None:
    if not FRONTEND_PACKAGE_JSON.exists():
        fail("frontend/package.json not found.")

    info("Installing frontend dependencies...")
    subprocess.run([npm_command(), "install"], cwd=FRONTEND_DIR, check=True)


def setup_all() -> None:
    setup_backend()
    setup_frontend()
    info("Setup completed.")


def write_pid(pid_file: Path, pid: int) -> None:
    pid_file.write_text(str(pid), encoding="utf-8")


def remove_pid_file(pid_file: Path) -> None:
    if pid_file.exists():
        pid_file.unlink()


def read_pid(pid_file: Path) -> int | None:
    if not pid_file.exists():
        return None
    raw = pid_file.read_text(encoding="utf-8").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def is_process_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        if IS_WINDOWS:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                check=False,
            )
            return str(pid) in result.stdout
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def stop_process(pid: int) -> None:
    if not is_process_running(pid):
        return

    if IS_WINDOWS:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False, capture_output=True)
        return

    os.kill(pid, signal.SIGTERM)
    for _ in range(20):
        if not is_process_running(pid):
            return
        time.sleep(0.2)
    os.kill(pid, signal.SIGKILL)


def stop_all() -> None:
    stopped_any = False
    for pid_file, name in (
        (BACKEND_PID_FILE, "backend"),
        (FRONTEND_PID_FILE, "frontend"),
    ):
        pid = read_pid(pid_file)
        if pid is not None:
            stop_process(pid)
            remove_pid_file(pid_file)
            info(f"Stopped {name} (pid {pid})")
            stopped_any = True

    if not stopped_any:
        info("No managed processes were running.")


def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        return sock.connect_ex((host, port)) == 0


def wait_for_http(url: str, timeout_seconds: int = 45) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if 200 <= response.status < 500:
                    return True
        except Exception:
            time.sleep(1)
    return False


def open_log_handles(out_path: Path, err_path: Path):
    out_handle = out_path.open("ab")
    err_handle = err_path.open("ab")
    return out_handle, err_handle


def start_backend() -> int:
    python_exe = backend_python_path()
    env = os.environ.copy()

    out_handle, err_handle = open_log_handles(BACKEND_OUT_LOG, BACKEND_ERR_LOG)
    try:
        process = subprocess.Popen(
            [str(python_exe), "-m", "uvicorn", "app.main:app", "--host", BACKEND_HOST, "--port", str(BACKEND_PORT)],
            cwd=BACKEND_DIR,
            stdout=out_handle,
            stderr=err_handle,
            env=env,
        )
    finally:
        out_handle.close()
        err_handle.close()

    write_pid(BACKEND_PID_FILE, process.pid)
    return process.pid


def start_frontend(preview: bool = False) -> int:
    if not FRONTEND_NODE_MODULES.exists():
        fail("frontend/node_modules is missing. Run `python run.py setup` first.")

    env = os.environ.copy()
    command = [npm_command(), "run", "preview" if preview else "dev", "--", "--host", FRONTEND_HOST, "--port", str(FRONTEND_PORT)]

    out_handle, err_handle = open_log_handles(FRONTEND_OUT_LOG, FRONTEND_ERR_LOG)
    try:
        process = subprocess.Popen(
            command,
            cwd=FRONTEND_DIR,
            stdout=out_handle,
            stderr=err_handle,
            env=env,
        )
    finally:
        out_handle.close()
        err_handle.close()

    write_pid(FRONTEND_PID_FILE, process.pid)
    return process.pid


def start_all(*, preview: bool = False, open_browser: bool = False, demo_mode: bool = False) -> None:
    ensure_logs_dir()
    stop_all()

    if is_port_open(BACKEND_HOST, BACKEND_PORT) or is_port_open(FRONTEND_HOST, FRONTEND_PORT):
        fail("Ports 8000 or 5173 are already in use. Stop other services first.")

    if not BACKEND_ENV.exists():
        info("backend/.env not found. Creating it from backend/.env.example ...")
        if not BACKEND_ENV_EXAMPLE.exists():
            fail("backend/.env.example not found.")
        shutil.copyfile(BACKEND_ENV_EXAMPLE, BACKEND_ENV)

    if demo_mode:
        os.environ["DEMO_MODE"] = "true"

    info("Starting backend...")
    backend_pid = start_backend()
    if not wait_for_http(f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/analysis/health", timeout_seconds=45):
        stop_process(backend_pid)
        fail("Backend did not become ready in time. Check logs/backend.err.log")

    info("Starting frontend...")
    frontend_pid = start_frontend(preview=preview)
    if not wait_for_http(f"http://{FRONTEND_HOST}:{FRONTEND_PORT}", timeout_seconds=45):
        stop_process(frontend_pid)
        stop_process(backend_pid)
        fail("Frontend did not become ready in time. Check logs/frontend.err.log")

    if open_browser:
        webbrowser.open(f"http://{FRONTEND_HOST}:{FRONTEND_PORT}")

    info("")
    info("Services are running:")
    info(f"  Frontend: http://{FRONTEND_HOST}:{FRONTEND_PORT}")
    info(f"  Backend : http://{BACKEND_HOST}:{BACKEND_PORT}")
    info("")
    info("Use `python run.py stop` to stop them.")


def show_status() -> None:
    backend_pid = read_pid(BACKEND_PID_FILE)
    frontend_pid = read_pid(FRONTEND_PID_FILE)

    info("Current status:")
    info(f"  Backend PID : {backend_pid or 'not managed'}")
    info(f"  Frontend PID: {frontend_pid or 'not managed'}")
    info(f"  Backend port open : {is_port_open(BACKEND_HOST, BACKEND_PORT)}")
    info(f"  Frontend port open: {is_port_open(FRONTEND_HOST, FRONTEND_PORT)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cross-platform project runner.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup_parser = subparsers.add_parser("setup", help="Install backend and frontend dependencies.")
    setup_parser.add_argument("--backend-only", action="store_true", help="Only set up the backend.")
    setup_parser.add_argument("--frontend-only", action="store_true", help="Only set up the frontend.")

    start_parser = subparsers.add_parser("start", help="Start backend and frontend.")
    start_parser.add_argument("--preview", action="store_true", help="Run frontend in preview mode instead of dev mode.")
    start_parser.add_argument("--open-browser", action="store_true", help="Open the frontend URL in a browser.")
    start_parser.add_argument("--demo", action="store_true", help="Start backend with DEMO_MODE=true.")

    subparsers.add_parser("stop", help="Stop managed backend and frontend processes.")
    subparsers.add_parser("status", help="Show current managed process status.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "setup":
        if args.backend_only and args.frontend_only:
            fail("Choose only one of --backend-only or --frontend-only.")
        if args.backend_only:
            setup_backend()
            info("Backend setup completed.")
            return
        if args.frontend_only:
            setup_frontend()
            info("Frontend setup completed.")
            return
        setup_all()
        return

    if args.command == "start":
        start_all(preview=args.preview, open_browser=args.open_browser, demo_mode=args.demo)
        return

    if args.command == "stop":
        stop_all()
        return

    if args.command == "status":
        show_status()
        return

    parser.error("Unknown command")


if __name__ == "__main__":
    main()
