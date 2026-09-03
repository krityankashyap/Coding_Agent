from tools.write_file import write_file
from tools.read_file import read_file
from tools.edit_file import edit_file
from tools.list_files import list_files


ALL_TOOLS= [
  write_file,
  read_file,
  edit_file,
  list_files,
]

def tool_catalog() -> list[dict[str, str]]:
  """ Name + Description of all tools in ALL_TOOLS """
  return [{"name": tool.name, "description": tool.description} for tool in ALL_TOOLS]