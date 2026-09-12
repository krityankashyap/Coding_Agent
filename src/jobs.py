import os
from dataclasses import dataclass, field
from typing import Any
import signal
import contextlib
import subprocess
from pathlib import Path
from datetime import datetime
from pytz import UTC
@dataclass
class BackgroundJob:
  pid: int
  command: str
  started_at: str
  log_path: str
  proc: Any= field(default=None, repr=False)  # Process handle, not included in the repr


_JOBS= dict[int , BackgroundJob]= ()  # Dictionary to hold background jobs, keyed by PID

def add_job(job: BackgroundJob) -> None:
  """Add a new background job to the job list."""
  _JOBS[job.pid]= job

def get_job(pid: int) -> BackgroundJob | None:
  """Retrieve a background job by its PID."""
  return _JOBS.get(pid)

def all_jobs() -> list[BackgroundJob]:
  """Return a list of all background jobs."""
  return list(_JOBS.values())

def remove(pid: int) -> BackgroundJob | None:
  """Remove a background job from the job list by its PID."""
  return _JOBS.pop(pid, None)

def is_alive(pid: int) -> bool:
  """Check if the background job is still running."""
  job= get_job(pid)
  if job is not None and job.proc is not None:
    return job.proc.poll() is None  # Returns None if the process is still running
  
  try:
    os.kill(pid, 0)  # Check if the process exists
    return True
  except OSError:
    return False
  

def stop_pid(pid: int) -> str:
  job= get_job(pid)

  if job is None:
    return f"No job found with PID {pid}."
  
  if not is_alive(pid):
    if job.proc is not None:
      with contextlib.suppress(ChildProcessError): # Suppress error if the process has already terminated
        job.proc.wait(timeout= 0.1)
    remove(pid)

    return f"Job with PID {pid} has already terminated."
  
  try:
    os.killpg(pid, signal.SIGTERM)  # Send SIGTERM to the process group
  except ProcessLookupError:
    remove(pid)
    return f"Job with PID {pid} has already terminated."
  except PermissionError:
    return f"Permission denied to stop job with PID {pid}."
  
  if job.proc is not None:
    try:
      job.proc.wait(timeout= 0.5) # Wait for the process to terminate gracefully
    except subprocess.TimeoutExpired:
      with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(pid, signal.SIGKILL)
      with contextlib.suppress(subprocess.TimeoutExpired):
        job.proc.wait(timeout= 1)

      remove(pid)
  return f"Job with PID {pid} was forcefully terminated."

def read_log_tail(log_path: Path, *, max_chars: int= 4000) -> str:
  """Read the last `max_chars` characters from the log file."""
  if not log_path.exists():
    return f"Log file '{log_path}' does not exist."
  
  text= log_path.read_text(encoding="utf-8", errors="replace")
  if len(text) > max_chars:
    return text[-max_chars:]  # Return only the last `max_chars` characters
  
  return text

def isoformat_now() -> str:
  """Return the current UTC time in ISO 8601 format."""
  return datetime.now(UTC).isoformat()



  
    

        
    

