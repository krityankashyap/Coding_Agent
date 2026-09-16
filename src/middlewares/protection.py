# this middleware will make sure that we don't do tool calls that directly target any secrets or confidencial data

import json
import re
from typing import Any, Callable
from datetime import datetime
from langchain.agents.middleware import AgentMiddleware
from langchain.tools.tool_node import ToolCallRequest
from langchain.messages import ToolMessage
from langgraph.types import Command
from src.tools.paths import is_blocked_path
from src.config.config import get_work_dir
from src.tools.paths import resolve_work_path

_FILE_TOOLS= {
   "read_file",
   "write_file",
   "edit_file",
   "list_files"
}

BLOCKED_EDIT_PATTERNS = (
    r"\bos\.system\s*\(",
    r"\bsubprocess\b",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"__import__\s*\(",
)

def deny_reason(tool_name: str, arguments: dict[str, Any]) -> str | None:
    """Determine if the tool call targets any secrets or dangerous payloads."""
    
    if tool_name not in _FILE_TOOLS:
       return None
    
    if tool_name== "run_command":
       return None
    
    path= arguments.get("path", ".") # Get the path argument, defaulting to the current directory

    # Check if the path is blocked
    if is_blocked_path(str(path)):
        return f"Tool '{tool_name}' call denied: path '{path}' is blocked."
    
    if tool_name == "read_file":
        try:
            file_path= resolve_work_path(str(path))
        except ValueError as e:
            return f"Tool '{tool_name}' call denied: invalid path '{path}': {e}"
        
        if file_path.is_file() and file_path.stat().st_size > 10 * 1024 * 1024: # 10 MB size limit
            return f"Tool '{tool_name}' call denied: file '{file_path}' exceeds the 10 MB size limit."
        
    payload= ""
    if tool_name == "write_file":
        payload= str(arguments.get("content", ""))

    if tool_name == "edit_file":
        payload= str(arguments.get("new_content", ""))

    if payload:
        for pattern in BLOCKED_EDIT_PATTERNS:
            if re.search(pattern, payload):
                return f"Tool '{tool_name}' call denied: payload contains blocked pattern '{pattern}'."
            
    return None  # No issues found, allow the tool call
    
    
  
class ProtectionMiddleware(AgentMiddleware):
  """Short circuit tool calls that target any secrets or dangerous payloads"""

  def wrap_tool_call(
      self,
      request: ToolCallRequest,
      handler: Callable[[ToolCallRequest], ToolMessage | Command]
  ) -> ToolMessage | Command:
      # Check if the tool call targets any secrets or dangerous payloads
      name= request.tool_call.get("name", "")
      arguments= request.tool_call.get("args", {})

      reason= deny_reason(name, arguments)
      
      if reason is not None:
          # Deny the tool call and return an error message
          return ToolMessage(
              content=json.dumps({"error": reason}),
              metadata={"denied": True}
          )
      
      # If no issues, proceed with the tool call
      return handler(request)


   