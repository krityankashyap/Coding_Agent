from pathlib import Path
import os
from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT= Path(__file__).parent.parent.parent  # Get the root directory of the project
PROMPTS_DIR = PROJECT_ROOT / "prompts"  # Directory for prompts
DEFAULT_WORK_DIR = PROJECT_ROOT / "workspace"  # Default working directory where all the coding agent work will dump

AGENT_NAME= "AgCamp coding agent"

MAX_MODEL_CALLS_PER_RUN= int(os.getenv("MAX_MODEL_CALLS_PER_RUN", 10))  # Maximum number of model calls per run, default is 10
MAX_READ_BYTES= int(os.getenv("MAX_READ_BYTES", 1000000))  # Maximum number of bytes to read from a file, default is 1MB

def hitl_enabled() -> bool:
    """
    Check if Human-in-the-loop (HITL) is enabled based on the environment variable.
    Returns True if HITL is enabled, otherwise False.
    """
    return os.getenv("HITL_ENABLED", "true").lower() in {"true", "1", "yes"}  # Default is True if the environment variable is not set

def get_work_dir() -> Path:
    override_work_dir = os.getenv("WORK_DIR", "").strip()  # Get the override work directory from the environment variable
    if override_work_dir:
        return Path(override_work_dir).expanduser().resolve()  # Return the override work directory if set
    
    return DEFAULT_WORK_DIR.resolve()