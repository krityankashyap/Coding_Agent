from langchain.tools import tool
from src.config.config import get_work_dir
from tools.paths import resolve_work_path, is_blocked_path
import json
import os
from pathlib import Path

@tool
def list_files(path: str= ".") -> str:
  """
   List files and directories under a given path in the working directory

   Args:
      path: Relative directory to list. Default to the working directory root.
  """

  work_dir=  get_work_dir()  # Get the working directory

  try:
    base_path= resolve_work_path(path)  # Resolve the path to ensure it's within the working directory
  except ValueError as e:
    raise ValueError(f"Invalid path '{path}': {e}") from e
  
  if not base_path.exists():
    return json.dumps({"error": f"Path '{base_path!r}' does not exist."})
  if not base_path.is_dir():
    return json.dumps({"error": f"Path '{base_path!r}' is not a directory."})
  
  result: list[str]= []

  for root,dirs, files in os.walk(base_path):
    root_path= Path(root)
    rel_root= root_path.relative_to(work_dir)  # Get the relative path from the working directory

    for dir_name in sorted(dirs):
      result.append(f"{(rel_root / dir_name).as_posix()}/")  # Append directory with a trailing slash

    for file_name in sorted(files):
      result.append((rel_root / file_name).as_posix())  # Append file path


    return json.dumps(result)
  