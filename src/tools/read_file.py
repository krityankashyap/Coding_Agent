from src.config.config import resolve_work_path
from langchain.tools import tool

@tool
def read_file(path: str) -> str:
  """
  Reads the UTF-8 text file from the working directory.

  Args:
    path: Realative path to the file within the working directory. eg: "src/tools/paths.py"
  """

  try:
    file_path= resolve_work_path(path)  # Resolve the path to ensure it's within the working directory
  except ValueError as e:
    raise ValueError(f"Invalid path '{path}': {e}") from e
  
  try:
    return file_path.read_text(encoding="utf-8")  # Read the file content as UTF-8 text
  except FileNotFoundError:
    raise FileNotFoundError(f"File '{file_path}' not found.")
  except PermissionError:
    raise PermissionError(f"Permission denied when trying to read file '{file_path}'.")
  except Exception as e:
    raise RuntimeError(f"An error occurred while reading file '{file_path}': {e}") from e
