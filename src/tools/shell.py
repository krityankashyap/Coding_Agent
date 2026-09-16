from dotenv import load_dotenv
from src.config.config import get_work_dir
import shlex
import sys
import re
import os
import subprocess

load_dotenv()

BLOCKED_COMMAND_PATTERNS = (
    r"\bsudo\b",
    r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f\b",
    r"\bmkfs\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r":\(\)\s*\{",
    r"\bdd\s+if=",
    r"curl\s+[^|]*\|\s*(ba)?sh",
    r"wget\s+[^|]*\|\s*(ba)?sh",
    r"\bchmod\s+777\b",
)

SERVER_PATTERNS = (
    r"\bflask(\s+--app)?\s+run\b",
    r"\buvicorn\b",
    r"\bgunicorn\b",
    r"\bhypercorn\b",
    r"\bpython[0-9.]*\s+\S*app\.py\b",
    r"\bnpm\s+start\b",
    r"\bnpx\s+(serve|next|vite|nuxt)\b",
    r"\bstreamlit\s+run\b",
)

## Python specific handling patterns:

_PIP_PREFIX = re.compile(
    r"^(?:pip[0-9.]*|python[0-9.]*\s+-m\s+pip)\b",
    re.IGNORECASE,
)
_PYTHON_PREFIX = re.compile(r"^python[0-9.]*\b", re.IGNORECASE)
_FLASK_PREFIX = re.compile(r"^flask\b", re.IGNORECASE)

def deny_commands(command: str) -> str | None :
  stripped= command.strip()
  if not stripped:
    return "Blocked by middleware: command not found"
  
  for pattern in BLOCKED_COMMAND_PATTERNS:
    if re.search(pattern, command, flags=re.IGNORECASE):
      return f"Blocked by middleware: command matched a dangerous pattern {pattern}"
    
  return None # the command is safe and can proceed

def looks_like_server(command: str) -> bool:
    return any(re.search(pattern, command, flags=re.IGNORECASE) for pattern in SERVER_PATTERNS)

def rewrite_command(command: str) -> str:
  exe= shlex.quote(sys.executable)  # 

  stripped= command.strip()

  if _PIP_PREFIX.match(stripped):
        return _PIP_PREFIX.sub(f"{exe} -m pip", stripped, count=1)

  if _PYTHON_PREFIX.match(stripped):
        return _PYTHON_PREFIX.sub(exe, stripped, count=1)

  if _FLASK_PREFIX.match(stripped):
        return _FLASK_PREFIX.sub(f"{exe} -m flask", stripped, count=1)

  return command

def _clip(text: str) -> str:
    if len(text) <= load_dotenv.MAX_OUTPUT_CHARS:
        return text 

    return text[:load_dotenv.MAX_OUTPUT_CHARS] + "\n... (truncated)"


def _run_foreground(command: str, timeout: int) -> str:
    cwd= get_work_dir()
    cwd.mkdir(parent=True, exist_ok= True)
    env= os.environ.copy()  # This line of code takes a snapshot of your computer's environment variables and makes a safe, independent copy of them.

    env.setdefault("PYTHONUNBUFFERED", "1")  # Ensure Python output is unbuffered for real-time feedback

    try:
        completed= subprocess.run(
            ["/bin/bash", "lc", command],
            cwd= cwd,
            env= env,
            capture_output= True,
            text= True,
            timeout= timeout
        )        
    except subprocess.TimeoutExpired as e:
        stdout= {e.stdout or ""} + {e.stderr or ""}
        return (
            f"Timed out after {timeout}s (process killed)"
            "If this is a server return with backgroung_jobs= True"
            f"{_clip(str(stdout))}"
        )

         





    


