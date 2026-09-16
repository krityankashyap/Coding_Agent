from dataclasses import dataclass
from schema import TurnSummary
from typing import Any
from langgraph.types import Command

@dataclass
class AgentTurnResult:
  text: str  # represents agent/assistant's response to the user
  structured: TurnSummary | None  # represents structured summary of the agent's actions in this turn
  messages: list[Any]  # represents the messages exchanged during this turn, including user input, agent responses, and tool calls
  pending_interrupt: dict[str, Any] | None

def start_turn(agent, user_txt: str, config: dict) -> AgentTurnResult:
 result= agent.invoke(
   {"messages" : [{"role": "user", "content": user_txt}]},
   config: config,
   version: "v2"
 )

def resume_turn(agent, decision: list[dict], config: dict) -> AgentTurnResult:
 result= agent.invoke(
  Command(
   resume= {
    "decision": decision
   }
  ),
  config= config,
  version= "v2"
 )
  