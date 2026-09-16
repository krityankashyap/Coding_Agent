from langgraph.checkpoint.memory import InMemorySaver

def make_checkpoint_memory() -> InMemorySaver:
    """Create and return an in-memory checkpoint saver."""
    return InMemorySaver()

def thred_config(thredId: str) -> dict:
    return {
        "configurable": {
            "thread_id": thredId,
        }
    }