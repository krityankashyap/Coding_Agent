from langchain.tools import tool
from src.config.config import resolve_work_path
from src.tools.text import prepare_file_content

@tool
def edit_file(path: str, old_str: str, new_str: str) -> str:
  """
   Replace 'old_str' with 'new_str' in the file at 'path'

   Language agnostic: .js, .ts, .java, .cpp and other text files all use exact substring replace.
   Pass an empty 'old_str' to create a new file sanme as('write_file').
   Both string must use new line, and not the two-character sequence backslash-n.


   Args:
   path:- Realtive file path to edit ed .README.
   old_str:- Exact text to replace, Empty string creates new file.
   new_str:- Exact text to replace with.


  """
  if not path and old_str== new_str:
    raise ValueError("Path cannot be empty when old_str and new_str are the same.")
  
  old_str= prepare_file_content(path, old_str)
  new_str= prepare_file_content(path, new_str)

  try:
    file_path= resolve_work_path(path)  # Resolve the path to ensure it's within the working directory
  except ValueError as e:
    return ValueError(f"Invalid path '{path}': {e}")
  
  if old_str== "":
    file_path.parent.mkdir(parents=True, exist_ok=True)  # Create parent directories if they don't exist
    file_path.write_text(new_str, encoding="utf-8")  # Write the new content to the file as UTF-8 text
    return f"File '{file_path}' created successfully."
  
  try:
    old_content= file_path.read_text(encoding="utf-8")  # Read the existing content of the file
  except FileNotFoundError:
    return f"File '{file_path}' not found."
  
  if old_str not in old_content:
    return f"'{old_str}' not found in file '{file_path}'. No changes made."
  
  new_content= old_content.replace(old_str, new_str)  # Replace the old string with the new string
  file_path.write_text(new_content, encoding="utf-8")  # Write the updated content back to the file
  return f"Replaced '{old_str}' with '{new_str}' in file '{file_path}'."
