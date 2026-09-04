# Prepare a simple function that can help us to inject HITL (Human-in-the-loop) into any agent in langchain

from langchain.agents.middleware import HumanInTheLoopMiddleware

def build_hitl_middlewares() -> HumanInTheLoopMiddleware:
  return HumanInTheLoopMiddleware(
    interrupt_on={
      "read_file": False,  # Do not interrupt on read_file tool
      "write_file":{
        "allowed_decisions" : ["approve", "reject"],  # Only allow approve or reject decisions for write_file tool
        "description": "Write or overwrite a file ondisk"

      } ,
      "edit_file": {
        "allowed_decisions" : ["approve", "reject"],  # Only allow approve or reject decisions for edit_file tool
        "description": "Edit a file on disk"
      },
      "list_files": False,  # Do not interrupt on list_files tool
    },
    description_prefix= "Coding agent your approve to move ahead"
  )

