"""Shared project paths and settings."""
from pathlib import Path
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent

DEMO_ENGINE_ROOT = PROJECT_ROOT / "demo_engine"
DEMO_ASSETS = DEMO_ENGINE_ROOT / "assets"
CONTROLLER_PATH = DEMO_ASSETS / "controller.py"

OUTPUT_ROOT = DEMO_ENGINE_ROOT / "output"
RESULTS_DIR = OUTPUT_ROOT / "results"
GRAPHS_DIR = OUTPUT_ROOT / "graphs"
USER_MOVES_DIR = OUTPUT_ROOT / "user_moves"

RESULTS_FILE = RESULTS_DIR / "rec_data.txt"
USER_MOVES_FILE = USER_MOVES_DIR / "moves.json"

DEMO_VENV_PYTHON = DEMO_ENGINE_ROOT / "venv" / "Scripts" / "python.exe"
if not DEMO_VENV_PYTHON.exists():
    DEMO_VENV_PYTHON = DEMO_ENGINE_ROOT / "venv" / "bin" / "python3"

DEMO_MAIN_SCRIPT = DEMO_ENGINE_ROOT / "main.py"

SANDBOX_MODULE = "demo_engine.sandbox"
DEMO_ENGINE_MODULE = "demo_engine"
DEMO_PREVIEW_MODULE = "demo_engine.preview"
STATUS_SHOWER_MODULE = "NexAI.dynamic.status_shower"

SHOW_GUI_PREVIEW = os.getenv("NEXAI_SHOW_GUI_PREVIEW", "true").lower() in (
    "1",
    "true",
    "yes",
)

STATUS_HOST = os.getenv("NEXAI_STATUS_HOST", "127.0.0.1")
STATUS_PORT = int(os.getenv("NEXAI_STATUS_PORT", "5050"))
PROFILER_PORT = int(os.getenv("NEXAI_PROFILER_PORT", "5000"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Supported examples: gemini-2.5-flash | gemma-4-31b-it | gemma-4-26b-a4b-it
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
# Gemini 2.5 only: 0=off, -1=dynamic, 8192+=deeper reasoning (ignored for Gemma)
GEMINI_THINKING_BUDGET = int(os.getenv("GEMINI_THINKING_BUDGET", "0"))

MAX_STEPS = 450
MOVE_TIME = 0.01


def ensure_output_dirs() -> None:
    """Create output directories if they do not exist."""
    for directory in (RESULTS_DIR, GRAPHS_DIR, USER_MOVES_DIR):
        directory.mkdir(parents=True, exist_ok=True)
