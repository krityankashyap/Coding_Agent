"""
Here we gonna write couple of important functions that will be helpful for us to read and understand the path,
it's not we gonna read and understand the path, whenever a model is going to call any tool for that tool call
Let's it want to write a file so which path it's going to write the file for that we have to write functions
"""

from pathlib import Path
from fnmatch import fnmatch
from src.config.config import get_work_dir

BLOCKED_PATHS_PATTERNS= [
  ".env",
  ".env.*",
  ".pem",
  ".key",
  ".crt",
  ".secret",
  ".git",
  ".git/**",
  "*.log",
  ".p12"
]

def normalized_path(path: str) -> str:
  normalized= Path(path).as_posix()  # Return the string representation of the path with forward (/) slashes.
  if normalized.startswith("./"):
    normalized= normalized[2:]  # Remove the leading "./" if present

  return normalized

def is_blocked_path(path: str) -> bool:
  normalized= normalized_path(path)
  return any(fnmatch(normalized, pattern) for pattern in BLOCKED_PATHS_PATTERNS)  # Check if the normalized path matches any blocked patterns

def resolve_work_path(path: str) -> Path:
  work_dir= get_work_dir()  # Get the working directory
  work_dir.mkdir(parents=True, exist_ok=True)
  candidate_path= (work_dir / path).resolve()

  try:
    candidate_path.relative_to(work_dir)  # Check if the candidate path is within the working directory
  except ValueError as e:
    raise ValueError(f"Path '{candidate_path}' is outside the working directory '{work_dir}'") from e
  
  return candidate_path