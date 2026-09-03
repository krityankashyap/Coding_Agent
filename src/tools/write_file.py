from langchain.tools import tool
from src.config.config import resolve_work_path
from src.tools.text import prepare_file_content

@tool
def write_file(path: str, content: str) -> str:
  """
   create overwrite a UTF-8 text file in the working directory.

   Works for any text file eg .js, .ts, .py, .java etc

   the `content` is the full file body with real newline characters between lines. Do not write the two-character sequence backslash-n. Don't write as a makrdown fence

   Args:
   path-> Realtive path of the file to create/write a content
  content-> Full file body with real newline characters between lines. Do not write the two-character sequence backslash-n. Don't write as a makrdown fence

  
  """
  if not path:
    raise ValueError("Path cannot be empty.")
  
  content= prepare_file_content(path, content)  # Prepare the content based on file type

  try:
    file_path= resolve_work_path(path)  # Resolve the path to ensure it's within the working directory
    file_path.write_text(content, encoding="utf-8")  # Write the content to the file as UTF-8 text
  except ValueError as e:
    return ValueError(f"Invalid path '{path}': {e}") 
  
  return f"File '{file_path}' written successfully."
