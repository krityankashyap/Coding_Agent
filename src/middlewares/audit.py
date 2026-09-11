import json
from typing import Any, Callable
from datetime import datetime
from langchain.agents.middleware import AgentMiddleware
from langchain.tools.tool_node import ToolCallRequest
from langchain.messages import ToolMessage
from langgraph.types import Command

from src.config.config import get_work_dir

class AuditMiddleware(AgentMiddleware):
  """Append JSON record after each tool call (approved or rejected) to a log file for auditing purposes."""

  def wrap_tool_call(
      self,
      request: ToolCallRequest,
      handler: Callable[[ToolCallRequest], ToolMessage | Command],
      )-> ToolMessage | Command:
       result= handler(request)  # Call the next middleware or the tool itself
       preview= ""
       if isinstance(result, ToolMessage):
         preview = str(result.content)[:200] # Get a preview of the tool's output, limited to 200 characters
         self._write({
            "timestamp": datetime.utcnow().isoformat(),
            "tool_name": request.tool.name,
            "result_privew": preview,
            "arguments": request.tool_call.get("args"),        
         })
         return result


  
  def _write(
        self,
        entry: dict[str, Any]
  ) -> None:
     log_path= get_work_dir() / ".audit_audit.log"  # Log file path in the working directory
     log_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
     with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")  # Append the JSON entry to the log file


      
    
    

