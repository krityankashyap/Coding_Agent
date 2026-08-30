from typing import Any
from langchain.messages import AIMessage, ToolMessage

def user_input(text: str) -> dict[str, str]:
  """OpenAI style dict for user input"""
  return {"role": "user", "content": text}


def last_ai_text(messages: list[Any]) -> str:
  for message in reversed(messages):
    if not isinstance(message, AIMessage):
      continue
    if getattr(message, "tool_calls", None):
      continue
    content= message.content
    if isinstance(content, str):
      return content
    if isinstance(content, list):
      parts= [
        block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"
      ]
      return "\n".join(part for part in parts if part)
    
  return ""


def last_tool_call(messages: list[Any]) -> str:
  for message in reversed(messages):
    if isinstance(message, ToolMessage):
      content= message.content
      return content if isinstance(content, str) else str(content)
    
  return ""




