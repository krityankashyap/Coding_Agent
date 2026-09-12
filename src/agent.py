from langchain.agents.middleware import ModelCallLimitMiddleware
from src.config.config import MAX_MODEL_CALLS_PER_RUN
from src.middlewares.audit import AuditMiddleware
from src.middlewares.protection import ProtectionMiddleware
from src.middlewares.hitl import HumanInTheLoopMiddleware
from src.models import build_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import ProviderStrategy
from langchain.schema import TurnSummary
from src.tools import ALL_TOOLS
from src.prompts import build_system_prompt


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
    layers.append(HumanInTheLoopMiddleware())  # Add Human-in-the-loop middleware if enabled

  return layers

def build_agent(
    *,
    enable_hitl: bool | None = None,
    extra_guidance: str= ""
):
  model, _provider= build_chat_model()
  use_hitl= enable_hitl() if enable_hitl is None else enable_hitl  # Use the provided enable_hitl value or default to the environment variable setting

  return create_agent(
    model= model,
    tools= ALL_TOOLS,
    system_prompt= build_system_prompt(extra_guidance= extra_guidance),
    middleware= build_middleware(enable_hitl= use_hitl),
    response_format= ProviderStrategy(TurnSummary),
    name= "Coding Agent"

  )




  