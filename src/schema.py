from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

class TurnSummary(BaseModel) :
  """ What the coding agent did in this turn? """

  summary= Field( description="Summary of the coding agent's actions in this turn" )
  file_touched: list[str]= Field(
    description="List of files that were created, modified, or deleted in this turn",
    default_factory= list
  )

  status: Literal["ok", "needs_input", "failed"]= Field(
    description="ok if the request is done, needs_input if you must ask the user, failed if the request failed",
    
  )