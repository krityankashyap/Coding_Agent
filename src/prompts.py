from jinja2 import Environment, FileSystemLoader, select_autoescape
from config.config import PROMPTS_DIR, AGENT_NAME, get_work_dir
from tools import tool_catalog

_env= Environment(
    loader=FileSystemLoader(PROMPTS_DIR),
    autoescape=select_autoescape(enabled_extensions=()),
    trim_blocks= True,
    lstrip_blocks= True
)

def render_template(name: str, **context) -> str:
    """
    Render a Jinja2 template with the given context.

    Args:
        name: The name of the template file.
        **context: Key-value pairs to be passed to the template.

    Returns:
        The rendered template as a string.
    """
    template= _env.get_template(name)
    return template.render(**context)

def build_system_prompt(
        *,
        agent_name: str= AGENT_NAME,
        extra_guidelines: str= ""
) -> str:
    """
    Build the system prompt for the coding agent.

    Args:
        agent_name: The name of the agent.
        extra_guidelines: Additional guidelines to include in the prompt.

    Returns:
        The complete system prompt as a string.
    """
    return render_template(
        "system.jinja",
        agent_name= agent_name,
        extra_guidelines= extra_guidelines,
        work_dir= str(get_work_dir()),
        tools= tool_catalog()
    )

def build_greeting(
        *,
        agent_name: str= AGENT_NAME
) -> str:
    """
    Build a greeting message for the coding agent.

    Args:
        agent_name: The name of the agent.

    Returns:
        The greeting message as a string.
    """
    return render_template(
        "greeting.jinja",
        agent_name= agent_name,
        work_dir= str(get_work_dir())
    )