from dotenv import load_dotenv
from src.config.config import get_work_dir
from src.jobs import isoformat_now
from src.jobs import add_job, stop_pid, read_log_tail
from src.jobs import all_jobs, is_alive
from langchain.tools import tool
import time
import shlex
import sys
import re
import os
import subprocess

DEFAULT_TIMEOUT = 30  # Default timeout in seconds

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
    
 # commands executed successfully, return the output
    chunks= []
    if completed.stdout:
        chunks.append(completed.stdout.rstrip())
    if completed.stderr:
        chunks.append(completed.stderr.rstrip())
    
    body= "\n".join(chunks) if chunks else "(no output)"
    return f"exist code {completed.returncode}\n{_clip(body)}"

def run_background(command: str) -> str:
    cwd= get_work_dir()
    cwd.mkdir(parents=True, exist_ok=True)
    env= os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")  # Ensure Python output is unbuffered for real-time feedback

    log_dir= cwd/ ".agent_jobs"
    log_dir.mkdir(parents=True, exist_ok=True)

    stamp= isoformat_now().replace(":", "").replace("+", "") # we want to put this timestamp in the log file name, but colons and plus signs can be problematic in file names, so we remove them.

    tmp_log= log_dir/ f"pending-{stamp}.log"
    log_file= tmp_log.open("w", encoding="utf-8")

    try:
        proc= subprocess.Popen(
            ["/bin/bash", "lc", command],
            env= env,
            cwd= cwd,
            stdout= log_file,
            stderr= subprocess.STDOUT,
            start_new_session= True  # Start the process in a new session to isolate it from the parent process
        )
        
    finally:
        log_file.close()   # Now this is log file where we write and update so we have to ensure that we close the file after we have started the process, so that the process can write to it without any issues.

        log_path= log_dir/ f"{proc.pid}-{stamp}.log"  # We have to rename the log file to include the process ID and timestamp for easier identification
        tmp_log.rename(log_path)  # Rename the temporary log file to the final log file name
        add_job(
            pid= proc.pid,
            command= command,
            log_path= log_path,
            started_at= isoformat_now(),
            proc= proc
        )

    time.sleep(1) # Give the process a moment to start and potentially write to the log file
    tail= read_log_tail(log_path)
    if proc.poll() is not None:  # If the process has already terminated
        stop_pid(proc.pid)  # Clean up the job record
        return f"Process exited immediately with code {proc.returncode}\n{tail}"

    # if the process is still running
    urls = re.findall(r"https?://[^\s]+", tail)
    url_line = f"Open in the browser: {urls[0]}\n" if urls else (
        "No url in the log yet - try http://127.0.0.1:3000"
        "and check list_jobs if it is blank.\n"
    )

    return (
        f"{url_line}\n"
        f"Started background job (pid={proc.pid}).\n"
        f"Log: {log_path}\n"
        f"cwd={cwd}\n"
        f"Use list_jobs/stop_job to manage it.\n"
        f"------ output so far -------\n {_clip(tail) or 'No output yet.'}"
    )


@tool
def stop_job(pid: int) -> str:
    """
    Stop a background job previously started by run_command.
    Args:
        pid: The process id of the job to stop.
    """
    return stop_pid(pid)

@tool 
def run_command(command: str, background: bool = False, timeout_seconds: int = 0) -> str:
    """
    Run a bash command in the working directory (host machine, not a sandbox).

    Foreground commands wait for completion. Set background=True for servers like (flask, uvicorn, npm start) 
    so they keep running. Server-like commands are auto backgrounded even if you forget the flag.

    Args:
        command: bash command to run, e.g. 'python app.py' or 'ls -la'.
        background: If true, start the process and return pid immediately..
        timeout_seconds: Maximum time to wait for the command to complete. This is for foreground timeout. 0 uses default (30s).

    """

    blocked = deny_commands(command)
    if blocked:
        return blocked 

    timeout = timeout_seconds if timeout_seconds > 0 else DEFAULT_TIMEOUT

    background = bool(background) or looks_like_server(command)

    command = rewrite_command(command)

    if background:
        return run_background(command)
    else:
        return _run_foreground(command, timeout)

@tool 
def list_jobs() -> str:
    """
    List background processes started by run_command (servers, long jobs).
    """

    jobs = all_jobs()
    if not jobs:
        return "No background jobs running."

    lines = []
    for job in jobs:
        state = "running" if is_alive(job.pid) else "exited"
        lines.append(
            f"pid={job.pid} state={state} started={job.started_at} cmd={job.command}"
        )
        tail = read_log_tail(job.log_path, max_chars=800)

        if tail:
            lines.append(tail.rstrip())
            lines.append("--------------------------------")
        
        return "\n".join(lines)
    



  


  

         





    


