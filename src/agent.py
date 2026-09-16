from langchain.agents.middleware import ModelCallLimitMiddleware
from config.config import MAX_MODEL_CALLS_PER_RUN, hitl_enabled
from middlewares.audit import AuditMiddleware
from middlewares.protection import ProtectionMiddleware
from middlewares.hitl import build_hitl_middlewares
from models import build_chat_model
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from schema import TurnSummary
from tools import ALL_TOOLS
from prompts import build_system_prompt
from memory import make_checkpoint_memory
from langgraph.checkpoint.memory import InMemorySaver


def build_middleware(
    *,
    enable_hitl: bool
) -> list:
  """
   1. model-call cap, i.e, how many times you want to call llm
   2. Audit log
   3. payload guardrail
   4. HITL on write/edit/run

  """

  layers: list= [
    ModelCallLimitMiddleware(
      run_limit= MAX_MODEL_CALLS_PER_RUN,
      exit_behavior="end"  # Exit the agent run when the model call limit is reached
    ),
    AuditMiddleware(),  # Middleware to log all tool calls for auditing purposes
    ProtectionMiddleware(),  # Middleware to protect against dangerous tool calls
   
  ]
  if enable_hitl:
    layers.append(build_hitl_middlewares())  # Add Human-in-the-loop middleware if enabled

  return layers

def build_agent(
    *,
    checkpointer: InMemorySaver | None = None,
    enable_hitl: bool | None = None,
    extra_guidance: str = ""
):
  model, _provider= build_chat_model()
  use_hitl= hitl_enabled() if enable_hitl is None else enable_hitl  # Use the provided enable_hitl value or default to the environment variable setting

  return create_agent(
    model= model,
    tools= ALL_TOOLS,
    system_prompt= build_system_prompt(extra_guidelines= extra_guidance),
    middleware= build_middleware(enable_hitl= use_hitl),
    response_format= ToolStrategy(TurnSummary),
    checkpointer= checkpointer or  make_checkpoint_memory(),
    name= "Coding Agent"

  )




  